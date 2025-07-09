import hashlib
import json
import os
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
from .validation_schema import FetchRackSlotTypeByProjectListSchema, QueryStbInfoSchema, GetStbStatusBrokenSchema, \
    GetBrokenFromRackSchema, GetRackSlotByIpSchema, AvailableSlotsSchema, GetIpSchema, GetStbsByProjectSchema, \
    FetchRackSlotTypeByProjectSchema, FetchSlotVersionsSchema, FetchRackSlotByProjectAndTypeSchema
from .validation_schema.utils import (
    slot_range_validator,
    hw_type_validator,
    create_dynamic_dataclass,
    im_ns,
    validate_with_schema,
    im,
)
from authlib.integrations.flask_client import OAuth
import requests
from .lib import mos_authlib

# LOGGING and ENV VARS
dotenv_path = "env/.env"  # container in /app/ and locally in {HOME}/github_repo
logfile = "logs/app.log"  # container in /app/ and locally in {HOME}/github_repo

logging.basicConfig(level=logging.INFO, filename=logfile, filemode="w")  # container
load_dotenv(dotenv_path, verbose=True)

# FLASK and FLASK/RESTX
app = Flask(__name__)
# CORS
CORS(app)


# Authorization
ROLES=["admin", "test_as_you_want"]# , 'automation-infra-proxy'

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
    },

}

api = Api(app,
       title="Sky Automation - Automation Infra Utils",
       description="API REST Sky Automation - Automation Infra Utils Microservice",
       security=["Bearer"],
       authorizations=authorizations)



# -----------------------------------------------------------------------
# -- KEYCLOAK SSO --

KEYCLOAK_CLIENT_CONFIG = os.environ.get("KEYCLOAK_CLIENT_CONFIG") or "keycloak.json"
with open(KEYCLOAK_CLIENT_CONFIG) as kc_file:
    KEYCLOAK_CONF = json.load(kc_file)

KEYCLOAK_CLIENT_ID = KEYCLOAK_CONF.get("resource")
KEYCLOAK_CLIENT_SECRET = KEYCLOAK_CONF["credentials"]["secret"]
KEYCLOAK_SERVER_METADATA_URL = f"%srealms/%s/.well-known/openid-configuration" % (
    KEYCLOAK_CONF.get("auth-server-url"),
    KEYCLOAK_CONF.get("realm"),
)

# -----------------------------------------------------------------------
# -- AUTH INTERNAL API --

AUTH_INTERNAL_API = [{"user": "dag", "pass": "skyDag!@2022", "ip": ["*"]}]
AUTH_INTERNAL_API_B64 = [
    hashlib.md5(bytes("%s:%s" % (a["user"], a["pass"]), "utf-8")).hexdigest()
    for a in AUTH_INTERNAL_API
]

# -----------------------------------------------------------------------


oauth = OAuth()

oauth.init_app(app)
try:
    oauth.register(
        name="keycloak",
        client_id=KEYCLOAK_CLIENT_ID,
        client_secret=KEYCLOAK_CLIENT_SECRET,
        server_metadata_url=KEYCLOAK_SERVER_METADATA_URL,
        client_kwargs={
            "scope": "openid email profile",
            "code_challenge_method": "S256",  # enable PKCE
        },
    )
    oauth.keycloak.load_server_metadata()
    oauth.keycloak.fetch_jwk_set()
except requests.exceptions.ConnectionError as e:
    app.logger.error("Keycloak connection error: %s" % e)
    exit(-1)

# Namespace
ns = api.namespace("infra_utils", description="infra_utils library as microservice")

@ns.route("/fetch_rack_slot_type_by_project")
class FetchRackSlotTypeByProject(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(ns=ns, name='fetch_rack_slot_type_by_project swagger expected model',
              schema_model={"project": fields.String(required=True, description="Project Name")}
              ),
        validate=False
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
        project = pr["project"]

        func_outs: list[dict] = fetch_rack_slot_type_by_project(project=project)
        out_dict = {'stbs': func_outs}
        return make_response(jsonify(out_dict))

@ns.route("/fetch_rack_slot_type_by_project_list")
class FetchRackSlotTypeByProjectList(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="fetch_rack_slot_type_by_project from project list swagger expected model",
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
    @validate_with_schema(FetchRackSlotTypeByProjectListSchema())
    def post(self):

        req_data = request.get_json()
        print(req_data)
        # return make_response(jsonify(req_data))
        pr: dict = FetchRackSlotTypeByProjectListSchema().load(req_data)
        projects = pr["projects"]
        func_outs = []

        for p in projects:
            func_outs.append({p: fetch_rack_slot_type_by_project(project=p)})
        dict_out = {"projects": func_outs}
        return make_response(jsonify(dict_out))

@ns.route("/query_stb_info")
class QueryStbInfo(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="query_stb_info swagger expected model",
            schema_model={'ip': fields.String(required=True, description="Rack IP address"),
                            'slot': fields.Integer(required=True, description="Slot SetTopBox")}
        ),
        validate=False,
    )
    @validate_with_schema(QueryStbInfoSchema())
    def post(self):

        req_data = request.get_json()
        print(req_data)
        # return make_response(jsonify(req_data))
        data_in: dict = QueryStbInfoSchema().load(req_data)
        func_outs: tuple = query_stb_info(data_in['ip'],data_in['slot'])
        dict_out: dict = {'info': func_outs}
        return make_response(jsonify(dict_out))

@ns.route("/get_stb_status_broken")
class GetStbStatusBroken(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="get_stb_status_broken swagger expected model",
            schema_model={'ip': fields.String(required=True, description="Rack IP address"),
                            'slot': fields.Integer(required=True, description="Slot SetTopBox")}
        ),
        validate=False,
    )
    @validate_with_schema(GetStbStatusBrokenSchema())
    def post(self):

        req_data = request.get_json()
        print(req_data)
        # return make_response(jsonify(req_data))
        data_in: dict = GetStbStatusBrokenSchema().load(req_data)
        func_outs: bool = get_stb_status_broken(data_in['ip'],data_in['slot'])
        dict_out = {'broken': func_outs}
        return make_response(jsonify(dict_out))


@ns.route("/get_broken_from_rack")
class GetBrokenFromRack(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="get_broken_from_rack swagger expected model",
            schema_model={'ip_rack': fields.String(required=True, description="Rack IP address")}
        ),
        validate=False,
    )
    @validate_with_schema(GetBrokenFromRackSchema())
    def post(self):

        req_data = request.get_json()
        print(req_data)
        # return make_response(jsonify(req_data))
        data_in: dict = GetBrokenFromRackSchema().load(req_data)
        dict_out: dict = get_broken_from_rack(data_in['ip_rack'])
        return make_response(jsonify(dict_out))

@ns.route("/query_stb_project_info")
class QueryStbProjectInfo(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="query_stb_project_info swagger expected model",
            schema_model={'ip': fields.String(required=True, description="Rack IP address"),
                            'slot': fields.Integer(required=True, description="Slot SetTopBox")}
        ),
        validate=False,
    )
    @validate_with_schema(QueryStbInfoSchema())
    def post(self):

        req_data = request.get_json()
        print(req_data)
        # return make_response(jsonify(req_data))
        data_in: dict = QueryStbInfoSchema().load(req_data)
        func_outs: tuple = query_stb_project_info(data_in['ip'],data_in['slot'])
        dict_out: dict = {'info': func_outs}
        return make_response(jsonify(dict_out))
# TBD
# @ns.route("/get_all_stb")
# class FetchRackSlotTypeByProject(Resource):
#     @mos_authlib.mos_authlib_rest(ROLES)
#     def post(self):
#         func_outs: list = get_all_stb()
#         out_json_list = []
#         for out in func_outs:
#              out_json_list.append(out.__dict__)
#             #return make_response(jsonify(str(out)))
#         dict_out: dict = {'stbs': func_outs}
#         return make_response(jsonify(dict_out))

@ns.route("/get_rack_slot_by_ip")
class GetRackSlotByIp(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="get_rack_slot_by_ip swagger expected model",
            schema_model={'ip': fields.String(required=True, description="STB IP address")}
        ),
        validate=False,
    )
    @validate_with_schema(GetRackSlotByIpSchema())
    def post(self):

        req_data = request.get_json()
        print(req_data)
        # return make_response(jsonify(req_data))
        data_in: dict = GetRackSlotByIpSchema().load(req_data)
        func_outs: tuple = get_rack_slot_by_ip(data_in['ip'])
        dict_out: dict = dict()
        dict_out['rack_ip'] = func_outs[0]
        dict_out['slot_number'] = func_outs[1]
        return make_response(jsonify(dict_out))

@ns.route("/available_slots")
class AvailableSlots(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="available_slots swagger expected model",
            schema_model={'proj': fields.String(required=True, description="Project name"),
               'typ': fields.String(required=True, description="Hw device type")}
        ),
        validate=False,
    )
    @validate_with_schema(AvailableSlotsSchema())
    def post(self):

        req_data = request.get_json()
        print(req_data)
        # return make_response(jsonify(req_data))
        data_in: dict = AvailableSlotsSchema().load(req_data)
        func_outs: int = available_slots(data_in['proj'],data_in['typ'])
        dict_out = {'available_slots': func_outs}
        return make_response(jsonify(dict_out))


@ns.route("/get_auto_reboot")
class GetAutoReboot(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    def post(self):
        func_outs: list = get_auto_reboot()
        dict_out: dict = {'autoreboots': func_outs}
        return make_response(jsonify(dict_out))


@ns.route("/get_ip")
class GetIp(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="get_ip swagger expected model",
            schema_model={'slot': fields.Integer(required=True, description="Slot SetTopBox"),
               'server_name': fields.String(required=True, description="Rack IP address"),
               'server_ip': fields.String(required=True, description="Rack IP address"),
               }
        ),
        validate=False,
    )
    @validate_with_schema(GetIpSchema())
    def post(self):

        req_data = request.get_json()
        print(req_data)
        # return make_response(jsonify(req_data))
        data_in: dict = GetIpSchema().load(req_data)
        func_outs: str = str(get_ip(data_in['slot'],data_in['server_name'],data_in['server_ip']))
        dict_out = {'ip': func_outs}
        return make_response(jsonify(dict_out))


@ns.route("/get_stbs_by_project")
class GetStbsByProject(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="get_stbs_by_project swagger expected model",
            schema_model={
                "proj": fields.String(required=True, description="Project Names")
            },
        ),
        validate=False,
    )
    @validate_with_schema(GetStbsByProjectSchema())
    def post(self):
        req_data = request.get_json()
        print(req_data)
        pr: dict = GetStbsByProjectSchema().load(req_data)
        project = pr["proj"]
        func_outs: list = get_stbs_by_project(project=project)
        dict_out: dict = {'stbs': func_outs}
        return make_response(jsonify(dict_out))


@ns.route("/fetch_slots_versions")
class FetchSlotVersions(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="fetch_slots_versions swagger expected model",
            schema_model={
                "proj": fields.String(required=True, description="Project Names")
            },
        ),
        validate=False,
    )
    @validate_with_schema(FetchSlotVersionsSchema())
    def post(self):
        req_data = request.get_json()
        print(req_data)
        pr: dict = FetchSlotVersionsSchema().load(req_data)
        project = pr["proj"]
        func_outs: list = fetch_slots_versions(project=project)
        dict_out: dict = {'stbs': func_outs}
        return make_response(jsonify(dict_out))

@ns.route("/fetch_rack_slot_by_project_and_type")
class FetchRackSlotByProjectAndType(Resource):
    @mos_authlib.mos_authlib_rest(ROLES)
    @ns.expect(
        im_ns(
            ns=ns,
            name="fetch_rack_slot_by_project_and_type swagger expected model",
            schema_model={
                "proj": fields.String(required=True, description="Project Names"),
                'typ': fields.String(required=True, description="Hw device type")
            },
        ),
        validate=False,
    )
    @validate_with_schema(FetchRackSlotByProjectAndTypeSchema())
    def post(self):
        req_data = request.get_json()
        print(req_data)
        pr: dict = FetchRackSlotByProjectAndTypeSchema().load(req_data)
        project = pr["proj"]
        hw_type = pr["typ"]
        func_outs: list = fetch_rack_slot_by_project_and_type(project=project, device_type=hw_type)
        dict_out: dict = {'stbs': func_outs}
        return make_response(jsonify(dict_out))

