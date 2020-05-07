from webargs import fields
from marshmallow import Schema, validate

class PowerPlantSchema(Schema):
    name = fields.Str(required=True)
    type = fields.Str(required=True, validate= lambda pptype: pptype in ["gasfired", "turbojet", "windturbine"])
    efficiency = fields.Float(required=True, validate=lambda eff: eff <= 1)
    pmin = fields.Float(required=True, validate=lambda pmin: pmin >= 0)
    pmax = fields.Float(required=True)


class PowerPlantLoadSchema(Schema):
    load = fields.Float(validate= lambda load: load >= 0)
    fuels = fields.Dict(
        fields.String(validate=lambda fuel_name: fuel_name in ["gas(euro/MWh)", "kerosine(euro/MWh)",
                                                               "co2(euro/ton)", "wind(%)"]),
        fields.Float(),
        required=True, validate=validate.Length(min=1))
    powerplants = fields.List(fields.Nested(PowerPlantSchema), required=True, validate=validate.Length(min=1))



