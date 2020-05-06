from abc import ABC, abstractmethod
from app.main.utils.general_utils import PowerPlantTypeEnum

class PowerPlantFactory:
    @staticmethod
    def get_power_plant_type(pptype):
        if pptype == "gasfired":
            return GasFired
        elif pptype == "turbojet":
            return TurboJet
        elif pptype == "windturbine":
            return WindTurbine
        else:
            raise ValueError(f"unexpected power plant type {pptype}. Check for typos")

    @staticmethod
    def get_power_plant_instance(powerplant_raw):
        pptype = PowerPlantFactory.get_power_plant_type(powerplant_raw.get("type"))
        return pptype(powerplant_raw.get("name"), powerplant_raw.get("efficiency"),
                      powerplant_raw.get("pmin"), powerplant_raw.get("pmax"))

    @staticmethod
    def set_fuel_on_power_plant(powerplant_instance, fuels):
        if powerplant_instance == GasFired:
            powerplant_instance.fuel_rate = fuels.get("gas(euro/MWh)")
            powerplant_instance.co2_emission = fuels.get("co2(euro/ton)")
        elif powerplant_instance == TurboJet:
            powerplant_instance.fuel_rate = fuels.get("kerosine(euro/MWh)")
            # Problem statement says only the gas-fired emits CO2...
            # powerplant_instance.co2_emission = fuels.get("co2(euro/ton)")
        elif powerplant_instance == WindTurbine:
            powerplant_instance.wind_percentage = fuels.get("wind(%)")


class PowerPlant(ABC):
    def __init__(self, name, efficiency, pmin, pmax):
        self.name = name
        self.efficiency = efficiency
        self.pmin = pmin
        self.pmax = pmax
        self.fuel_rate = 0
        self.co2_emission = 0

    @abstractmethod
    def cost_euros_per_load(self, load_on_powerplant):
        pass

    @abstractmethod
    def min_power_when_on(self):
        pass

    @abstractmethod
    def max_power_when_on(self):
        pass

    def cost_per_mwh(self):
        fuel_cost = self.fuel_rate/self.efficiency
        co2_cost = 0.3 * self.co2_emission
        return fuel_cost + co2_cost

    @staticmethod
    def sort_power_plants_by_cost_per_mwh(power_plants):
        return sorted(power_plants, key=lambda p: p.cost_per_mwh)

class GasFired(PowerPlant):
    def max_power_when_on(self):
        return self.pmax

    def min_power_when_on(self):
        return self.pmin

    def cost_euros_per_load(self, load_on_powerplant):
        if 0 < load_on_powerplant < self.pmin:
            ValueError("Impossible to operate at this point")
        return load_on_powerplant * self.cost_per_mwh()


class TurboJet(PowerPlant):
    def max_power_when_on(self):
        return self.pmax

    def min_power_when_on(self):
        return self.pmin

    def cost_euros_per_load(self, load_on_powerplant):
        if 0 < load_on_powerplant < self.pmin:
            ValueError("Impossible to operate at this point")
        cost_in_euros = load_on_powerplant * self.fuel_rate / self.efficiency
        return cost_in_euros


class WindTurbine(PowerPlant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wind_percentage = 0

    @property
    def wind_percentage(self):
        return self._wind_percentage

    @wind_percentage.setter
    def wind_percentage(self, wind_percentage):
        if wind_percentage<0:
            raise ValueError("Wind percentage cannot be less than 0")
        self._wind_percentage = wind_percentage

    def max_power_when_on(self):
        return self.pmax * self.wind_percentage/100

    def min_power_when_on(self):
        return self.pmax * self.wind_percentage/100

    def cost_euros_per_load(self, load_on_powerplant):
        return 0
