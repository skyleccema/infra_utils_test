# This is the settings.py file
from os import getenv

ENV = getenv("ENV")
GROUP = getenv("GROUP")
PROJECT_NAME = getenv("PROJECT_NAME")
PROJECT_ANGULAR = getenv("PROJECT_ANGULAR")
SERVICE_NAME = getenv("SERVICE_NAME")
PORTAL_NAME = getenv("PORTAL_NAME")
KEYCLOAK_CLIENT_CONFIG = getenv("KEYCLOAK_CLIENT_CONFIG")
MONGODBUSERNAME = getenv("MONGODBUSERNAME")
MONGODBPASSWORD = getenv("MONGODBPASSWORD")
MONGODBHOST = getenv("MONGODBHOST")
MONGODBPORT = getenv("MONGODBPORT")
MONGODBCLIENT = getenv("MONGODBCLIENT")
db_user = getenv("db_user")
db_password = getenv("db_password")
