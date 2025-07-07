#/get_stb_status_broken validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf
from .utils import ip_length_validator, slot_range_validator

@dataclass
class GetStbStatusBrokenDC:
    ip: fields.String
    slot: fields.Integer

class GetStbStatusBrokenSchema(Schema):
    ip = fields.String(required=True, validate=lambda x:ip_length_validator(x))
    slot = fields.Integer(required=True, validate=lambda x:slot_range_validator(x))