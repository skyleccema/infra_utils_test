#/fetch_rack_slot_type_by_project_grouped_by_rack validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from .utils import project_validator

@dataclass
class FetchRackSlotTypeByProjectGroupedByRackDC:
    proj: fields.String

class FetchRackSlotTypeByProjectGroupedByRackSchema(Schema):
    proj = fields.String(required=True, validate=project_validator)
