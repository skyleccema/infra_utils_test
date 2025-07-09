#/fetch_rack_slot_by_project_and_type validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf
from .utils import hw_type_validator, project_validator

@dataclass
class FetchRackSlotByProjectAndTypeDC:
    proj: fields.String
    typ: fields.String

class FetchRackSlotByProjectAndTypeSchema(Schema):
    proj = fields.String(required=True, validate=project_validator)
    typ = fields.String(required=True, validate=hw_type_validator)

