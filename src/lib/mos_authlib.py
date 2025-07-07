# /app/lib/mos_authlib.py
# ver 0.9.4

from functools import wraps
from typing import Union

import requests
# from flask import render_template, redirect
from authlib.jose import jwt
from authlib.jose.errors import JoseError, ExpiredTokenError, DecodeError
from flask import request, Response, session, redirect, url_for, current_app



# from authlib.integrations.flask_client import OAuth, token_update
# from authlib.integrations.flask_oauth2
# from authlib.oauth2.rfc6749 import OAuth2Token


# ---------------------------------------------------------------------------
def mos_authlib_refresh(token, req_type='refresh_token'):
    from src.api import oauth

    kc = oauth.keycloak
    client_id = kc.client_id
    client_secret = kc.client_secret

    token_endpoint = kc.server_metadata.get('token_endpoint')
    introspection_endpoint = kc.server_metadata['introspection_endpoint']
    userinfo_endpoint = kc.server_metadata['userinfo_endpoint']

    uri_endpoint = token_endpoint

    post_data = {
        "client_id": client_id,
        "client_secret": client_secret
    }

    if req_type == 'refresh_token':
        uri_endpoint = token_endpoint
        post_data["grant_type"] = "refresh_token"
        post_data["refresh_token"] = token

    if req_type == 'introspection':
        uri_endpoint = introspection_endpoint
        post_data["token"] = token

    if req_type == 'userinfo':
        uri_endpoint = userinfo_endpoint
        post_data = {
            "access_token": token
        }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    r = requests.post(uri_endpoint, data=post_data, headers=headers)
    return r


# ---------------------------------------------------------------------------
def mos_authlib_impersonation(token, impersonate_user='test'):
    from src.api import oauth

    kc = oauth.keycloak
    client_id = kc.client_id
    client_secret = kc.client_secret

    token_endpoint = kc.server_metadata.get('token_endpoint')
    uri_endpoint = token_endpoint

    post_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        # "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "grant_type": "client_credentials",
        "subject_token": token,
        # "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "audience": client_id,
        "requested_subject": impersonate_user
    }

    post_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        # "grant_type": "client_credentials",
        "subject_token": token,
        # "requested_token_type": "urn:ietf:params:oauth:token-type:id_token",
        "requested_subject": impersonate_user
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    r = requests.post(uri_endpoint, data=post_data, headers=headers)
    return r


# curl -X POST \
#     -d "client_id=starting-client" \
#     -d "client_secret=the client secret" \
#     --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
#     -d "subject_token=...." \
#     --data-urlencode "requested_token_type=urn:ietf:params:oauth:token-type:access_token" \
#     -d "audience=target-client" \
#     -d "requested_subject=wburke" \
#     http://localhost:8080/realms/myrealm/protocol/openid-connect/token


# ---------------------------------------------------------------------------
def mos_authlib_require_login():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            from src.api import oauth

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # - - SSO Authenticaton & Authorization management  - -
            user = session.get('user')
            token_data = session.get('token_data', {})
            roles = session.get('roles', [])

            if not (user and
                    # type(token_data) == dict and
                    mos_authlib_token_is_valid(token_data.get('access_token'))):
                session.clear()
                callback_uri = url_for('auth.callback', _external=True)
                return oauth.keycloak.authorize_redirect(callback_uri)

            if not roles:
                # session.clear()
                uri = url_for('auth.access_denied', _external=True)
                return redirect(uri)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            return fn(*args, **kwargs)

        return decorator

    return wrapper


# ---------------------------------------------------------------------------
def mos_authlib_rest(roles=[], get_token=False, internal_api=False):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            from src.api import oauth

            check_roles = False if roles else True
            client_roles = []

            kc = oauth.keycloak
            client_id = kc.client_id
            jwks = kc.server_metadata.get('jwks')

            auth_header = request.headers.get("Authorization")


            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # - INTERNAL API - BASIC AUTH
            if auth_header and auth_header.lower().startswith("basic ") and internal_api:
                digest_str = auth_header[6:].strip()
                user, authorized = internal_api_basic_auth(digest_str)
                if not authorized:
                    current_app.logger.info("Basic auth: ip address not authorized: %s" % request.remote_addr)
                if user and authorized:
                    current_app.logger.debug("Basic auth: autenticated user %s" % user)
                    # kwargs['token'] = fake_token("user")
                    return fn(*args, **kwargs)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # - SSO -
            if auth_header and auth_header.lower().startswith("bearer "):
                token_str = auth_header[7:].strip()
                try:
                    token = jwt.decode(token_str, jwks)
                    token.validate()
                    user = token.get('preferred_username')
                    resource_access = token.get('resource_access')
                    if resource_access:
                        resource_access_roles = resource_access.get(client_id)
                        current_app.logger.info("Basic auth: resources access client_id %s" % str(client_id))
                        if resource_access_roles:
                            client_roles = resource_access_roles.get('roles')
                            for role in client_roles:
                                current_app.logger.info("Basic auth: resources access role %s" % str(role))
                        else:
                            client_roles = []

                        user_roles = []  # Only for log
                        for role in roles:
                            if role in client_roles:
                                check_roles = True
                                user_roles.append(role)
                        if user_roles:
                            current_app.logger.info(
                                "decorator mos_authlib_rest: User: %s - Access OK with role: %s" % (user, user_roles))
                    if check_roles:
                        if get_token:
                            kwargs['token'] = token
                        return fn(*args, **kwargs)
                    else:
                        return {
                            "error": "unauthorized",
                            "error_description": "Access denied - Requested roles: %s - User roles: %s" %
                                                 (roles, client_roles)}, 403
                except ValueError as e:
                    current_app.logger.info(str(e))
                    return Response(str(e), status=401)
                except ExpiredTokenError as e:
                    current_app.logger.info(str(e))
                    return Response(str(e), status=401)
                except JoseError as e:
                    current_app.logger.info(str(e))
                    print(type(e), str(e))
                    return Response(status=403)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            return Response("Bearer required", status=401)

        return decorator

    return wrapper


# ---------------------------------------------------------------------------
def token_roles(token={}):
    from src.api import oauth

    client_id = oauth.keycloak.client_id
    try:
        roles = token['resource_access'][client_id]['roles']
    except KeyError as e:
        current_app.logger.error(str(e))
        roles = []
        pass
    return roles


# ---------------------------------------------------------------------------
def internal_api_basic_auth(digest=None):
    if digest in current_app.config['AUTH_INTERNAL_API_B64']:
        idx = current_app.config['AUTH_INTERNAL_API_B64'].index(digest)
        user = current_app.config['AUTH_INTERNAL_API'][idx]['user']

        # - IP address Check
        req_addr = request.remote_addr
        authorized_ip = current_app.config['AUTH_INTERNAL_API'][idx].get('ip')
        if not authorized_ip:
            authorized = True
        elif "*" in authorized_ip or req_addr in authorized_ip:
            authorized = True
        else:
            authorized = False

        return user, authorized

    return None


# ---------------------------------------------------------------------------
def mos_authlib_token_is_valid(token=""):
    from src.api import oauth

    kc = oauth.keycloak
    try:
        token = jwt.decode(token, kc.server_metadata.get('jwks'))
    except DecodeError as e:
        current_app.logger.debug(str(e))
        return False

    try:
        token.validate()
    except ExpiredTokenError as e:
        current_app.logger.debug(str(e))
        return False
    return True


def get_token_user_name(token={}):
    # client_id = oauth.keycloak.client_id
    try:
        _user_name = token["preferred_username"]
    except KeyError as e:
        current_app.logger.error(str(e))
        _user_name = "USER_UNKNOWN"
        pass
    return _user_name


def get_user_projects(token: dict = {}) -> Union[list, None]:
    from src.api import oauth

    # client_id = oauth.keycloak.client_id
    try:

        _client_id = oauth.keycloak.client_id
        _projects_access = token["projects_access"]
        _client = _projects_access.get(_client_id, None)
        _projects = _client.get("projects", None)

    except KeyError as e:
        current_app.logger.error(str(e))
        _projects = None

    return _projects


def get_user_info_from_token(token: dict) -> dict:
    from src.api import oauth

    if isinstance(token, dict) and token != {}:
        try:
            # TODO implement gathering info to pass to infra-utils

            _client_id = oauth.keycloak.client_id
            _projects_access = token["projects_access"]
            _client = _projects_access.get(_client_id, None)
            _projects = _client.get("projects", None)

        except KeyError as e:
            current_app.logger.error(str(e))
            _projects = {}
        return _projects
    else:
        return {}
