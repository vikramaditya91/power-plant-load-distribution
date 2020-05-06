import numpy
import logging
from app.main.model.power_plant import PowerPlantFactory, PowerPlant

logger = logging.getLogger(__name__)


def load_distributor(raw_input_data):
    load_calculations = LoadCalculations.get_load_calculator_from_raw_data(raw_input_data)
    distributed_load = load_calculations.distribute_load()
    return distributed_load


class LoadCalculations:
    def __init__(self, load_to_distribute, fuel_list, power_plants):
        self.load_to_distrib = load_to_distribute
        self.fuel_list = fuel_list
        self.power_plants = power_plants

    @classmethod
    def get_load_calculator_from_raw_data(cls, raw_input_data):
        load_to_distribute = raw_input_data.get("load", 0)
        fuels = raw_input_data.get("fuels", {})
        power_plants = raw_input_data.get("powerplants")
        power_plant_instances = [PowerPlantFactory.get_power_plant_instance(powerplant) for powerplant in power_plants]
        [PowerPlantFactory.set_fuel_on_power_plant(powerplant_instance, fuels) for powerplant_instance in
         power_plant_instances]
        return cls(load_to_distribute, fuels, power_plant_instances)

    @property
    def load_to_distrib(self):
        return self._load_to_distrib

    @load_to_distrib.setter
    def load_to_distrib(self, load_to_distrib):
        if load_to_distrib < 0:
            raise ValueError("The load to distribute cannot be less than 0")
        self._load_to_distrib = int(load_to_distrib)

    def distribute_load(self):
        self.power_plants.sort()
        power_plants_sorted = self.power_plants
        load_array = [{} for item in range(self.load_to_distrib)]
        for load_index in range(self.load_to_distrib):
            remaining_load_to_distribute = load_index
            for powerplant_index, power_plant in enumerate(power_plants_sorted):
                if remaining_load_to_distribute > 1e-2:
                    if load_index < power_plant.min_power_when_on():
                        # Can not turn on a power plant midway
                        continue
                    if (remaining_load_to_distribute >= power_plant.pmax) and \
                            (
                                    power_plant.max_power_when_on() >= remaining_load_to_distribute >= power_plant.min_power_when_on()):
                        # This power plant is not sufficient to satisfy the load
                        load_array[load_index][power_plant] = power_plant.pmax
                        remaining_load_to_distribute = remaining_load_to_distribute - power_plant.pmax
                    elif (remaining_load_to_distribute < power_plant.pmax) and \
                            (power_plant.max_power_when_on() >= remaining_load_to_distribute >= power_plant.min_power_when_on()):
                        # This power plant is just sufficient to satisfy the load. And it requires more than pmin
                        load_array[load_index][power_plant] = remaining_load_to_distribute
                        remaining_load_to_distribute = 0
                    else:
                        # Does it make sense to turn this on, but shutting down low cost power plants?
                        load_array[load_index] = self.determine_cheapest_power_plant_at_transition(load_array,
                                                                                                   load_index,
                                                                                                   powerplant_index,
                                                                                                   remaining_load_to_distribute)
                        remaining_load_to_distribute = remaining_load_to_distribute - sum(load_array[load_index].values())
            # print(
            #     f"{self.calculate_cost_of_powerplant_dict(load_array[load_index]):.2f}, owest power at load_index {load_index} is with {(load_array[load_index])}")
            if remaining_load_to_distribute > 1e-2:
                logger.warning("Powerplants were not sufficient")
            logging.debug(f"Lowest power at load_index {load_index} is with {load_array[load_index]}")


    def determine_cheapest_power_plant_at_transition(self, load_array, load_index, powerplant_index_start_from,
                                                     pending_load):
        local_dict_for_comparison = {}
        for powerplant_index_current, power_plant in enumerate(self.power_plants):
            if powerplant_index_current >= powerplant_index_start_from:
                if load_index >= power_plant.min_power_when_on():
                    if power_plant.min_power_when_on() <= load_index <= power_plant.max_power_when_on():
                        local_dict_for_comparison[power_plant] = load_array[load_index - power_plant.min_power_when_on()]
                        local_dict_for_comparison[power_plant][power_plant] = pending_load

        if len(local_dict_for_comparison) == 0:
            logger.warning(f"Demand for load of {pending_load} unable to be fulfilled.\n"
                           f"Approximating to the earlier value at {pending_load-1}")
            return load_array[load_index-1]
        most_appropriate_power_plant = self.determine_lowest_cost_in_transition_dict(local_dict_for_comparison)
        return local_dict_for_comparison[most_appropriate_power_plant]

    def determine_lowest_cost_in_transition_dict(self, local_dict_per_power_plant):
        cost_per_powerplant = {}
        for key, value in local_dict_per_power_plant.items():
            cost_per_powerplant[key] = self.calculate_cost_of_powerplant_dict(value)
        return min(cost_per_powerplant, key=cost_per_powerplant.get)

    @staticmethod
    def calculate_cost_of_powerplant_dict(load_dict):
        total_cost = 0
        for powerplant, load_value in load_dict.items():
            total_cost = total_cost + powerplant.cost_euros_per_load(load_value)
        return total_cost


if __name__ == "__main__":
    import pathlib
    import json
    import requests

    path_to_example_dir = pathlib.Path(
        "/home/vikramaditya/Applications/2020-Job-hunt/engie/powerplant-coding-challenge/" "example_payloads")
    for example in path_to_example_dir.glob('*.json'):
        with open(example, "r") as fp:
            example_content = json.load(fp)
            # output_from_call = requests.post("http://127.0.0.1:5000/powerplant/", json=example_content)
            load_distributor(example_content)
