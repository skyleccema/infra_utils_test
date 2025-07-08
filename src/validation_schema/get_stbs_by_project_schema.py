#/get_stbs_by_project validation schema
from dataclasses import dataclass

from marshmallow import fields, Schema
from marshmallow.validate import OneOf
from .utils import project_validator

@dataclass
class GetStbsByProjectDC:
    proj: fields.String

class GetStbsByProjectSchema(Schema):
    proj = fields.String(required=True, validate=project_validator)
