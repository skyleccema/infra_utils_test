from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'utility per il db infrastruttura'
LONG_DESCRIPTION = 'utility per il db infrastruttura'

# Impostazioni
setup(
    name="infra_utils_sqlalchemy_1.4",
    version=VERSION,
    author="Francesco Amirante",
    author_email="<francesco.amirante.mediamotive@skytv.it>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "python-decouple",
        "SQLAlchemy>=1.4,<1.5",
        "mysql-connector-python",
        "mysqlclient"
    ]
)