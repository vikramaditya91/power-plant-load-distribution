import logging
from app.main.model.power_plant import PowerPlantFactory, PowerPlant, PowerPlantConfigurationError
logger = logging.getLogger("service")


def load_distributor(raw_input_data):
    """
    Obtains the raw_input_data, transfers it and gets the output in desired form
    :param raw_input_data: dictionary of load, fuels and powerplants
    :return:list of powerplants with the name and load on each of them
    """
    load_calculations_interface = LoadCalculationInterface.get_load_calculator_from_raw_data(raw_input_data)
    distributed_load = load_calculations_interface.distribute_load()
    sanitized_response = load_calculations_interface.convert_distributed_data_as_response(
        distributed_load, load_calculations_interface.power_plants)
    return sanitized_response


class LoadCalculationInterface:
    """Interface to the Flask App for consolidating information from the POST and sending valid data back"""
    @classmethod
    def get_load_calculator_from_raw_data(cls, raw_input_data):
        load_to_distribute = raw_input_data.get("load", 0)
        fuels = raw_input_data.get("fuels", {})
        power_plants = raw_input_data.get("powerplants")
        power_plant_instances = [PowerPlantFactory.get_power_plant_instance(powerplant) for powerplant in power_plants]
        [PowerPlantFactory.set_fuel_on_power_plant(powerplant_instance, fuels) for powerplant_instance in
         power_plant_instances]
        return cls(load_to_distribute, fuels, power_plant_instances)

    def __init__(self, load_to_distribute, fuel_list, power_plants):
        logger.info("Setting up load calculation interface")
        self.load_to_distrib = load_to_distribute
        self.fuel_list = fuel_list
        self.power_plants = power_plants

    @property
    def load_to_distrib(self):
        return self._load_to_distrib

    @load_to_distrib.setter
    def load_to_distrib(self, load_to_distrib):
        if load_to_distrib < 0:
            raise ValueError("The load to distribute cannot be less than 0")
        self._load_to_distrib = int(load_to_distrib)

    def distribute_load(self):
        """
        Sends the load and power plants to the PowerPlantCore to get the most inexpensive configuration of PowerPlants
        :return:
        """
        power_plants_sorted = PowerPlant.get_sorted_power_plants(self.power_plants)
        load_calculator = LoadCalculatorCore()
        return load_calculator.get_optimal_power_plants_for_load(self.load_to_distrib, power_plants_sorted)

    @staticmethod
    def convert_distributed_data_as_response(distributed_load_dict, power_plants):
        """Converts the available information of optimal powerplants to the response expected i.e list of dicts"""
        response = []
        for power_plant in power_plants:
            load_on_power_plant = distributed_load_dict.get(power_plant, 0)
            response.append({"name": power_plant.name,
                             "p": load_on_power_plant})
        return response


class LoadCalculatorCore:
    """All functions related to calculating the load. No unit conversion handled here"""
    def get_optimal_power_plants_for_load(self, load, sorted_power_plants):
        """
        NOTE: Unit conversion is not handled here
        Obtains a dict (key=powerplant, value=load on it) based on the load provided and a list of sorted power plants
        which is going to cost the least in euros
        It uses a sorted list of power plants by cost/mwh and fills up the load in that order
        The algorithm is:
        a) Is the total-load less than pmin of the powerplant? skip it
        b) Is the remaining-load more than the pmax, fill the powerplants's load with pmax
        c) Is the remaining-load less than pmax, but more than pmin, fill the powerplant's load by remaining-load
        d) Is the remaining-load less than pmax and also less than pmin, take the special algorithm in determine_cheapest_config_at_transition
        :param load: int, load required to be distributed among power plants available on the grid
        :param sorted_power_plants: list of sorted power plant instances
        :return: dict of powerplants which are the most optimal (least cost in euros)
        """
        remaining_load_to_distrib = load
        power_plants_to_use = {}
        sorted_power_plants_copy = sorted_power_plants
        for powerplant_current_index, current_power_plant in enumerate(sorted_power_plants_copy):
            if remaining_load_to_distrib > 0:
                if (load < current_power_plant.min_power_when_on()) or (current_power_plant in power_plants_to_use.keys()):
                    # Power plant can not be turned on as load is greater than min power
                    continue
                if (remaining_load_to_distrib >= current_power_plant.min_power_when_on()) and (remaining_load_to_distrib>=current_power_plant.max_power_when_on()):
                    # This power plant is going to be used normally sufficient to satisfy the load
                    power_plants_to_use[current_power_plant] = current_power_plant.max_power_when_on()
                    remaining_load_to_distrib = remaining_load_to_distrib - current_power_plant.max_power_when_on()
                elif (remaining_load_to_distrib >= current_power_plant.min_power_when_on()) and (remaining_load_to_distrib<current_power_plant.max_power_when_on()):
                    # This power plant is just sufficient to satisfy the load. And it requires more than pmin
                    power_plants_to_use[current_power_plant] = remaining_load_to_distrib
                    remaining_load_to_distrib = 0
                elif remaining_load_to_distrib <= current_power_plant.min_power_when_on():
                    # Does it make sense to turn this on, but shutting down low cost power plants?
                    power_plants_to_use = self.determine_cheapest_config_at_transition(power_plants_to_use,
                                                                                       powerplant_current_index,
                                                                                       sorted_power_plants_copy,
                                                                                       remaining_load_to_distrib,
                                                                                       load)

                    remaining_load_to_distrib = load - sum(power_plants_to_use.values())
        if remaining_load_to_distrib>1e-2:
            logging.debug(f"Impossible to have a configuration with load {load}")
            raise PowerPlantConfigurationError(f"Impossible to have a configuration with a load of {load}")
        return power_plants_to_use

    def determine_cheapest_config_at_transition(self, power_plants_already_calc, powerplant_index_check_from,
                                                sorted_power_plants, remaining_load_to_distrib, max_load):
        """
        Handles situations when the reminaing load to distribute is less than the pmin of a power-plant.
        A combination of functional-programming approach/fractional knapsack-without-repetition is followed here.
        Against each power-plant, it is checked what the value would be the total cost if the load were
        total-cost = cost(total load - pmin of current power plant) + cost(pmin of current power plant)
        The minimum of this value is found and that configuration is returned
        :param power_plants_already_calc: Already prepared list of power plants from the calling function
        :param powerplant_index_check_from: Already parsed through these power plants. So no need to check them again
        :param sorted_power_plants: list of sorted power plants
        :param remaining_load_to_distrib: remaining load to distribute
        :param max_load: total-load requested
        :return: dict of power plants which are going to be the most inexpensive in terms of euros
        """
        cost_dict_for_transition = {}
        list_to_check = sorted_power_plants.copy()
        for powerplant_index, power_plant in enumerate(list_to_check):
            if powerplant_index_check_from <= powerplant_index:
                if max_load > power_plant.min_power_when_on():
                    if power_plant.min_power_when_on()>0:
                        try:
                            min_config_when_previous_plants_shutdown = self.get_optimal_power_plants_for_load( max_load - power_plant.min_power_when_on(), sorted_power_plants.copy())
                            min_config_when_previous_plants_shutdown[power_plant] = power_plant.min_power_when_on()
                            cost_dict_for_transition[power_plant] = min_config_when_previous_plants_shutdown
                        except PowerPlantConfigurationError:
                            continue
                    else:
                        power_plants_already_calc[power_plant] = remaining_load_to_distrib
                        cost_dict_for_transition[power_plant] = power_plants_already_calc

        lowest_cost_power_plant = self.determine_lowest_cost_in_transition_dict(cost_dict_for_transition)
        return cost_dict_for_transition[lowest_cost_power_plant]

    def determine_lowest_cost_in_transition_dict(self, local_dict_per_power_plant):
        """
        Determines the dictionary key with lowest value
        :param local_dict_per_power_plant: dictionary where key is power plant,
        but value is the dict of powerplants with load as their key
        :return: power plant with minimum cost of the dict
        """
        cost_per_powerplant = {}
        for key, value in local_dict_per_power_plant.items():
            cost_per_powerplant[key] = self.calculate_cost_of_powerplant_dict(value)
        return min(cost_per_powerplant, key=cost_per_powerplant.get)

    @staticmethod
    def calculate_cost_of_powerplant_dict(load_dict):
        """Calculates the total cost of the running of the dictionary of the power plants"""
        total_cost = 0
        for powerplant, load_value in load_dict.items():
            total_cost = total_cost + powerplant.cost_euros_per_load(load_value)
        return total_cost
