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
        list_of_power_plants_instances = [PowerPlantFactory.set_fuel_on_power_plant(powerplant_instance, fuels)
                                          for powerplant_instance in power_plant_instances]
        return cls(load_to_distribute, fuels, list_of_power_plants_instances)

    @property
    def load_to_distrib(self):
        return self._load_to_distrib

    @load_to_distrib.setter
    def load_to_distrib(self, load_to_distrib):
        if load_to_distrib<0:
            raise ValueError("The load to distribute cannot be less than 0")
        self._load_to_distrib = int(load_to_distrib)

    def distribute_load(self):
        power_plants_sorted = PowerPlant.sort_power_plants_by_cost_per_mwh(self.power_plants)
        load_array = []
        current_load_power_plant = numpy.zeros((len(self.power_plants), self.load_to_distrib))
        for load_index, load_operating_point in enumerate(load_array):
            remaining_load_to_distribute = load_operating_point
            for powerplant_index, power_plant in enumerate(self.power_plants):
                if remaining_load_to_distribute >= 0:
                    if load_operating_point - power_plant.min_power_when_on <= 0:
                        # Can not turn on a power plant midway
                        continue
                    if remaining_load_to_distribute - power_plant.pmax > 0:
                        # This power plant is not sufficient to satisfy the load
                        current_load_power_plant[powerplant_index, load_index] = power_plant.pmax
                        remaining_load_to_distribute = remaining_load_to_distribute - power_plant.pmax
                    elif (remaining_load_to_distribute - power_plant.pmax) < 0 and (remaining_load_to_distribute > power_plant.pmin):
                        # This power plant is just sufficient to satisfy the load. And it requires more than pmin
                        current_load_power_plant[powerplant_index, load_index] = remaining_load_to_distribute
                    elif (remaining_load_to_distribute - power_plant.pmax) < 0 and (remaining_load_to_distribute < power_plant.pmin):
                        # Does it make sense to turn this on, but shutting down low cost power plants?
                        power_plant.pmin
                        cost_compare



                print(index)

        return []

if __name__ == "__main__":
    import pathlib
    import json
    import requests
    path_to_example_dir = pathlib.Path("/home/vikramaditya/Applications/2020-Job-hunt/engie/powerplant-coding-challenge/" "example_payloads")
    for example in path_to_example_dir.glob('*.json'):
        with open(example, "r") as fp:
            example_content = json.load(fp)
            # output_from_call = requests.post("http://127.0.0.1:5000/powerplant/", json=example_content)
            load_distributor(example_content)


