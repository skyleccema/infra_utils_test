import flask_restx
from typing import Dict, Type, Any
from dataclasses import dataclass
from marshmallow import fields as ma_fields, ValidationError, Schema
from flask import request
from functools import wraps


__projects = [
    "PCC",
    "Automation",
    "Prodotto",
    "CERRI",
    "Trionfetti",
    "SAAS",
    "MDP",
    "TEST",
    "Team_CA",
    "APP_DE",
    "SAAS_TEST",
    "CUG_TRIAL",
    "MDP_TEST"
]

__infra_device_types = [
    "Xi1",
    "Llama",
    "Stream",
    "Falcon",
    "Amidala",
    "Amidala_Hip",
    "Titan",
    "MRBOX",
    "MySkyHD",
    "OpenTV",
    "Roku",
    "Sky+",
    "X-Wing",
]


def slot_range_validator(slot_id: int):
    """
    Custom validator for slot id value range
    """
    if slot_id > 16 or slot_id < 0:
        raise ValidationError("Slot id must be between 0 and 16")


def ip_length_validator(ip: str):
    """
    Custom validator for range of number of character of an ip address
    """
    n_chars = len(ip)
    if n_chars > 15 or n_chars < 7:
        raise ValidationError(
            "Ip address number of characters must be between 7 and 15"
        )
        # raise flask_restx.ValidationError('Ip address number of characters must be between 7 and 15')


def project_validator(proj: str):
    for p in __projects:
        if proj == p:
            return
    raise ValidationError("Inserted project is not valid.")


def hw_type_validator(hw_type: str):
    for dev in __infra_device_types:
        if hw_type == dev:
            return
    raise ValidationError("Inserted infrastructure device type is not valid.")


def create_dynamic_dataclass(fields_dict: Dict[str, Type]) -> Type:
    # Create dataclass using type() and __annotations__
    DynamicClass = type(
        "DynamicDataclass",
        (object,),
        {"__annotations__": fields_dict, "__module__": __name__},
    )
    # Apply dataclass decorator
    return dataclass(DynamicClass)


## TO-DO refactoring
def validate_with_schema(schema):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            custom_message = {
                "schedule_result": "KO",
                "request_system_id": 1,
                "error_code": 4000,
                "error_message": "Json Parsing error: ",
            }

            if request.method != "GET" and request.url.startswith(
                request.host_url + "api/v1/job-service"
            ):
                data = request.get_data()
                if data:
                    try:
                        request.json_module.loads(data)
                    except ValueError as e:
                        custom_message["error_message"] += str(e)
                        return custom_message, 400
                else:
                    custom_message["error_message"] += "No payload"
                    return custom_message, 400

            req_data = request.get_json()
            if not req_data:
                custom_message["error_message"] += "Empty json"
                return custom_message, 400
            try:
                # Validate data with Marshmallow schema
                schema.load(req_data)
            except ValidationError as e:
                custom_message = {
                    "schedule_result": "KO",
                    "request_master_id": req_data.get("request_master_id"),
                    "request_system_id": 1,
                    "request_job_id": req_data.get("request_job_id"),
                    "error_code": 4001,
                    "error_message": f"Validation error: {e.messages}",
                }
                return custom_message, 400
            return fn(*args, **kwargs)

        return wrapper

    return decorator


# OLD im
def im(api: flask_restx.Api, name: str, schema_model: Any) -> flask_restx.Model:
    return api.model(name, schema_model)


# new fetch im
def im_ns(ns: flask_restx.Namespace, name: str, schema_model: Any) -> Any:
    if isinstance(ns, flask_restx.Namespace):
        return ns.model(
            name=name,
            model=schema_model,
        )
    else:
        raise flask_restx.ValidationError("Namespace object not defined.")
