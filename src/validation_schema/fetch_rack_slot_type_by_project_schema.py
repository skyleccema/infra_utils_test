# /fetch_rack_slot_type_by_project validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf


@dataclass
class FetchRackSlotTypeByProjectDC:
    projects: fields.List


class FetchRackSlotTypeByProjectSchema(Schema):
    projects = fields.List(
        fields.String(required=True, validate=OneOf(["CERRI", "PCC"]))
    )
