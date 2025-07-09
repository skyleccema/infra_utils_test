#/fetch_slots_versions validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf
from .utils import project_validator

@dataclass
class FetchSlotVersionsDC:
    proj: fields.String

class FetchSlotVersionsSchema(Schema):
    proj = fields.String(required=True, validate=project_validator)
