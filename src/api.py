from flask import Flask, request, make_response, jsonify
from flask_restx import Resource, Api, fields
from flask_cors import CORS
from infra_utils.QueryInfradb import (
    query_stb_info,
    get_stb_status_broken,
    get_broken_from_rack,
    query_stb_project_info,
    get_all_stb,
    get_rack_slot_by_ip,
    available_slots,
    get_auto_reboot,
    get_ip,
    get_stbs_by_project,
    fetch_slots_versions,
    fetch_slots_versions_with_dinamic_filter,
    fetch_rack_slot_type_by_project,
    fetch_rack_slot_by_project_and_type,
    fetch_rack_slot_type_by_project_grouped_by_rack,
    fetch_rack_slot_by_project_and_type_grouped_by_rack,
)
from dotenv import load_dotenv
import logging
from .validation_schema import FetchRackSlotTypeByProjectSchema
from .validation_schema.utils import (
    slot_range_validator,
    hw_type_validator,
    create_dynamic_dataclass,
    im_ns,
    validate_with_schema,
    im,
)

# LOGGING and ENV VARS
dotenv_path = "env/.env"  # container in /app/ and locally in {HOME}/github_repo
logfile = "logs/app.log"  # container in /app/ and locally in {HOME}/github_repo

logging.basicConfig(level=logging.INFO, filename=logfile, filemode="w")  # container
load_dotenv(dotenv_path, verbose=True)

# FLASK and FLASK/RESTX
app = Flask(__name__)
# CORS
CORS(app)

api = Api(app)


# Namespace
ns = api.namespace("infra_utils", description="infra_utils library as microservice")


@ns.route("/fetch_rack_slot_type_by_project")
class FetchRackSlotTypeByProject(Resource):

    @ns.expect(
        im_ns(
            ns=ns,
            name="fetch_rack_slot_type_by_project swagger expected model",
            schema_model={
                "projects": fields.List(
                    fields.String(required=True, description="Project Names")
                )
            },
        ),
        validate=False,
    )
    # @ns.expect(
    #     NewFetchDTO.swagger_model(ns=ns),
    #     validate=False
    # )
    @validate_with_schema(FetchRackSlotTypeByProjectSchema())
    def post(self):

        req_data = request.get_json()
        print(req_data)
        # return make_response(jsonify(req_data))
        pr: dict = FetchRackSlotTypeByProjectSchema().load(req_data)
        projects = pr["projects"]
        func_outs = []

        for p in projects:
            func_outs.append({p: fetch_rack_slot_type_by_project(project=p)})
        out_dict = {"projects": func_outs}
        return make_response(jsonify(out_dict))


# if __name__ == "__main__":
#     app.run(debug=True)
