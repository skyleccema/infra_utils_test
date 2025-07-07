# # -----------------------------------------------------------------------
# # -- KEYCLOAK SSO --
# import hashlib
# import json
# import os
#
# import requests
#
# KEYCLOAK_CLIENT_CONFIG = os.environ.get("KEYCLOAK_CLIENT_CONFIG") or "keycloak.json"
# with open(KEYCLOAK_CLIENT_CONFIG) as kc_file:
#     KEYCLOAK_CONF = json.load(kc_file)
#
# KEYCLOAK_CLIENT_ID = KEYCLOAK_CONF.get('resource')
# KEYCLOAK_CLIENT_SECRET = KEYCLOAK_CONF['credentials']['secret']
# KEYCLOAK_SERVER_METADATA_URL = f"%srealms/%s/.well-known/openid-configuration" % (
#     KEYCLOAK_CONF.get('auth-server-url'),
#     KEYCLOAK_CONF.get('realm')
# )
#
# # -----------------------------------------------------------------------
# # -- AUTH INTERNAL API --
#
# AUTH_INTERNAL_API = [
#     {
#         "user": "dag",
#         "pass": "skyDag!@2022",
#         "ip": ['*']
#     }
# ]
# AUTH_INTERNAL_API_B64 = [
#     hashlib.md5(bytes("%s:%s" % (a['user'], a['pass']), "utf-8")).hexdigest() for a in AUTH_INTERNAL_API]
#
# # -----------------------------------------------------------------------
#
#
# oauth = OAuth()
#
# oauth.init_app(app)
# try:
#     oauth.register(
#         name='keycloak',
#         client_id=KEYCLOAK_CLIENT_ID,
#         client_secret=KEYCLOAK_CLIENT_SECRET,
#         server_metadata_url=KEYCLOAK_SERVER_METADATA_URL,
#         client_kwargs={
#             'scope': 'openid email profile',
#             'code_challenge_method': 'S256'  # enable PKCE
#         },
#     )
#     oauth.keycloak.load_server_metadata()
#     oauth.keycloak.fetch_jwk_set()
# except requests.exceptions.ConnectionError as e:
#     exit(-1)