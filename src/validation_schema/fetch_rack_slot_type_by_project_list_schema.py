# /fetch_rack_slot_type_by_project validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf

from .utils import project_validator


@dataclass
class FetchRackSlotTypeByProjectListDC:
    projects: fields.List


class FetchRackSlotTypeByProjectListSchema(Schema):
    projects = fields.List(
        fields.String(required=True, validate=project_validator)
    )
