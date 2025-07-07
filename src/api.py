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
from .validation_schema import FetchRackSlotTypeByProjectSchema
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
                   description="API REST Sky Automation - Infra Utils Microservice",
                   security=["Bearer"],
                   authorizations=authorizations)


# -----------------------------------------------------------------------
# -- KEYCLOAK SSO --

KEYCLOAK_CLIENT_CONFIG = os.environ.get("KEYCLOAK_CLIENT_CONFIG") or "keycloak.json"
with open(KEYCLOAK_CLIENT_CONFIG) as kc_file:
    KEYCLOAK_CONF = json.load(kc_file)

KEYCLOAK_CLIENT_ID = KEYCLOAK_CONF.get('resource')
KEYCLOAK_CLIENT_SECRET = KEYCLOAK_CONF['credentials']['secret']
KEYCLOAK_SERVER_METADATA_URL = f"%srealms/%s/.well-known/openid-configuration" % (
    KEYCLOAK_CONF.get('auth-server-url'),
    KEYCLOAK_CONF.get('realm')
)

# -----------------------------------------------------------------------
# -- AUTH INTERNAL API --

AUTH_INTERNAL_API = [
    {
        "user": "dag",
        "pass": "skyDag!@2022",
        "ip": ['*']
    }
]
AUTH_INTERNAL_API_B64 = [
    hashlib.md5(bytes("%s:%s" % (a['user'], a['pass']), "utf-8")).hexdigest() for a in AUTH_INTERNAL_API]

# -----------------------------------------------------------------------


oauth = OAuth()

oauth.init_app(app)
try:
    oauth.register(
        name='keycloak',
        client_id=KEYCLOAK_CLIENT_ID,
        client_secret=KEYCLOAK_CLIENT_SECRET,
        server_metadata_url=KEYCLOAK_SERVER_METADATA_URL,
        client_kwargs={
            'scope': 'openid email profile',
            'code_challenge_method': 'S256'  # enable PKCE
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
    @mos_authlib.mos_authlib_rest(['admin'])
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
