#/get_ip validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf
from .utils import slot_range_validator, ip_length_validator

@dataclass
class GetIpDC:
    slot: fields.Integer
    server_name: fields.String
    server_ip: fields.String

class GetIpSchema(Schema):
    slot = fields.Integer(required=True, validate=lambda x: slot_range_validator(x))
    server_name = fields.String(required=True)
    server_ip = fields.String(required=True, validate=lambda x:ip_length_validator(x))

# AvailableSlotsSchema
