#/get_broken_from_rack validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf
from .utils import ip_length_validator, slot_range_validator

@dataclass
class GetBrokenFromRackDC:
    ip_rack: fields.String

class GetBrokenFromRackSchema(Schema):
    ip_rack = fields.String(required=True, validate=lambda x:ip_length_validator(x))

#GetBrokenFromRackSchema