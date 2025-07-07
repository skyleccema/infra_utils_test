#/available_slots validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf
from .utils import hw_type_validator

@dataclass
class AvailableSlotsDC:
    proj: fields.String
    typ: fields.String

class AvailableSlotsSchema(Schema):
    proj = fields.String(required=True, validate=OneOf(["CERRI","PCC"]))
    typ = fields.String(required=True, validate=lambda x:hw_type_validator(x))

# AvailableSlotsSchema
