#/fetch_rack_slot_by_project_and_type_grouped_by_rack validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from .utils import hw_type_validator, project_validator

@dataclass
class FetchRackSlotByProjectAndTypeGroupedByRackDC:
    proj: fields.String
    typ: fields.String

class FetchRackSlotByProjectAndTypeGroupedByRackSchema(Schema):
    proj = fields.String(required=True, validate=project_validator)
    typ = fields.String(required=True, validate=hw_type_validator)

