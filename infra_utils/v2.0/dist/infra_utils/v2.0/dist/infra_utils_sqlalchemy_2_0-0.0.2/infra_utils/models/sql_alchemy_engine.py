from sqlalchemy import create_engine
from urllib.parse import quote
from decouple import config
from sqlalchemy.orm import sessionmaker

class SqlAlchemyEngine:
    _self = None
    _engine = None
    _session_maker = None
    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    #Create sql alchemy engine or return  it if arledy exist
    def getEngine(self) :
        if self._engine is  None :
            DB_SERVER = "10.69.11.105"
            DB_PORT = "3306"
            DB_USER = config('db_user')
            DB_PASSWORD = quote(config('db_password'))
            DB_DATABASE = "infradb"
            SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s:%s/%s" % (
                DB_USER,
                DB_PASSWORD,
                DB_SERVER,
                DB_PORT,
                DB_DATABASE,
            )
            try:
                self._engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, future=True)
            except Exception as exception:
                print(f"error in create engine exception :{exception}")
        return self._engine

    # Create sql alchemy Session Maker or return it if arledy exist
    def getSessiomMaker(self):
        if self._session_maker is None:
            try:
                self._session_maker = sessionmaker(
                    bind=self.getEngine(), autocommit=False, autoflush=False
                )
            except Exception as exception:
                print(f"error in create session Maker exception :{exception}")
        return self._session_maker