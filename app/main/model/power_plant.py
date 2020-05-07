from abc import ABC, abstractmethod


class PowerPlantFactory:
    """Responsible for instantiating the power plants and feeding them information about fuels"""
    @staticmethod
    def get_power_plant_type(pptype):
        """determines type of PowerPlant instance based on string"""
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
        """Factory for generating the power plant instances"""
        pptype = PowerPlantFactory.get_power_plant_type(powerplant_raw.get("type"))
        return pptype(powerplant_raw.get("name"), powerplant_raw.get("efficiency"),
                      powerplant_raw.get("pmin"), powerplant_raw.get("pmax"))

    @staticmethod
    def set_fuel_on_power_plant(powerplant_instance, fuels):
        """Sets the fuel on the power plant instances"""
        if type(powerplant_instance) == GasFired:
            powerplant_instance.fuel_rate = fuels.get("gas(euro/MWh)")
            powerplant_instance.co2_emission = fuels.get("co2(euro/ton)")
        elif type(powerplant_instance) == TurboJet:
            powerplant_instance.fuel_rate = fuels.get("kerosine(euro/MWh)")
            # Problem statement says only the gas-fired emits CO2...
            # powerplant_instance.co2_emission = fuels.get("co2(euro/ton)")
        elif type(powerplant_instance) == WindTurbine:
            powerplant_instance.wind_percentage = fuels.get("wind(%)")
        else:
            ValueError("Unknown powerplant to set fuel on")


class PowerPlant(ABC):
    """PowerPlant Base Class"""
    def __init__(self, name, efficiency, pmin, pmax):
        self.name = name
        self.efficiency = efficiency
        self.pmin = pmin
        self.pmax = pmax
        self.fuel_rate = 0
        self.co2_emission = 0

    def __lt__(self, other):
        """Compare powerplants by the running cost per mwh"""
        return self.cost_per_mwh() < other.cost_per_mwh()

    @abstractmethod
    def cost_euros_per_load(self, load_on_powerplant):
        """Cost in euros per load of power plant"""
        pass

    @abstractmethod
    def min_power_when_on(self):
        """Minimum power that has to be delivered by the power plant when on"""
        pass

    @abstractmethod
    def max_power_when_on(self):
        """Max power that can be delivered by the powerplant when on"""
        pass

    def cost_per_mwh(self):
        """Cost per mwh of electricity"""
        fuel_cost = self.fuel_rate/self.efficiency
        co2_cost = 0.3 * self.co2_emission
        return fuel_cost + co2_cost

    @staticmethod
    def get_sorted_power_plants(power_plants):
        """Sort the power plants. It sorts them based on the cost_per_mwh"""
        power_plants.sort()
        return power_plants


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
