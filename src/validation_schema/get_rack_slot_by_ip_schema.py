#/get_rack_slot_by_ip validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf
from .utils import ip_length_validator, slot_range_validator

@dataclass
class GetRackSlotByIpDC:
    ip: fields.String

class GetRackSlotByIpSchema(Schema):
    ip = fields.String(required=True, validate=lambda x:ip_length_validator(x))