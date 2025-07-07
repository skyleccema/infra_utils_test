# app/models/ssr_services.py

from typing import Optional
from sqlalchemy.dialects import mysql
from sqlalchemy import Column, Table, Integer, String,Date
from sqlalchemy.orm import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# mapper_registry = db.registry()

# declarative base class
Base = declarative_base()

# @mapper_registry.mapped
#@dataclass
class InfraDBRackIaas(Base):
    __bind_key__ = 'infradb'
    # __tablename__ = 'rack_iaas'
    __table__ = Table(
        "rack_iaas",
        Base.metadata,
        Column("rack_id", Integer, primary_key=True),
        Column("name", String(250)),
        Column("ip", String(15)),
        Column("subnet", String(20)),
        Column("rack_model", String(250)),
        Column("slot_number", Integer),
        Column("moxa_ip", String(15))
    )

    rack_id: int # = field(init=False)
    name: Optional[str] = None
    ip: Optional[str] = None
    subnet: Optional[int] = None
    rack_model: Optional[str] = None
    slot_number: Optional[int] = None
    moxa_ip: Optional[str] = None
    # slots: List[InfraDBSlot] = field(default_factory=list)

    slots = relationship("InfraDBSlotIaas", back_populates='rack')

    # __mapper_args__ = {   # type: ignore
    #     "properties": {
    #         "slots": relationship("InfraDBSlot")
    #     }
    # }


#@dataclass
class InfraDBSlotIaas(Base):
    __bind_key__ = 'infradb'
    # __tablename__ = 'slot'
    __table__ = Table(
        'slot_iaas',
        Base.metadata,
        Column("slot_id", Integer, primary_key=True),
        Column("rack_id", Integer, ForeignKey('rack_iaas.rack_id')),
        Column("ethernet_cable", mysql.BOOLEAN),
        Column("serial_cable", mysql.BOOLEAN),
        Column("hdmi_cable", mysql.BOOLEAN),
        Column("sat1", String(250)),
        Column("sat2", String(250)),
        Column("dtt", mysql.BOOLEAN),
        Column("splitter_audio_video", mysql.BOOLEAN),
        Column("splitter_video", mysql.BOOLEAN),
        Column("down_scaler", mysql.BOOLEAN),
        Column("status_slot", mysql.BOOLEAN),
        Column("moxa_port", Integer),
        Column("slot_number", Integer),
        Column("note", mysql.TEXT)

    )

    slot_id: int
    rack_id: int
    ethernet_cable: Optional[bool] = None
    serial_cable: Optional[bool] = None
    hdmi_cable: Optional[bool] = None
    sat1: Optional[str] = None
    sat2: Optional[str] = None
    dtt: Optional[bool] = None
    splitter_audio_video: Optional[bool] = None
    splitter_video: Optional[bool] = None
    down_scaler: Optional[bool] = None
    status_slot: Optional[bool] = None
    moxa_port: Optional[int] = None
    slot_number: Optional[int] = None
    note: Optional[str] = None

    # status: InfraDBSlotStatus = field(default_factory=list)
   # status = db.relationship("InfraDBSlotStatus", uselist=False, backref="slot")

    # __mapper_args__ = {   # type: ignore
    #     "properties": {
    #         "status": db.relationship("InfraDBSlotStatus")
    #     }
    # }
    rack = relationship("InfraDBRackIaas", back_populates="slots")
    stbs_iaas = relationship("InfraDBStbIaas", back_populates="slot")


#@dataclass
class InfraDBStbIaas(Base):
    __bind_key__ = 'infradb'
    # __tablename__ = 'slot_status'
    __table__ = Table(
        'stb_iaas',
        Base.metadata,
        Column("stb_id", Integer, primary_key=True),
        Column("slot_id", Integer, ForeignKey('slot_iaas.slot_id')),
        Column("smart_card_id", Integer, ForeignKey('smart_card_iaas.smart_card_id')),
        Column("account_id", Integer, ForeignKey('account_iaas.account_id')),
        Column("country_code", String(10)),
        Column("hardware_name", String(250)),
        Column("chipId", String(250)),
        Column("deviceid", String(250)),
        Column("mac_address", String(17)),
        Column("mac_address_br", String(17)),
        Column("model_number", String(250)),
        Column("receiverId", String(250)),
        Column("project", String(250)),
        Column("version_number", String(250)),
        Column("serial_number", String(250)),
        Column("ip", String(15)),
        Column("personalized_pin", String(4)),
        Column("stb_status", mysql.BOOLEAN),
        Column("auto_rebot", mysql.BOOLEAN),
        Column("used_for", String(250)),
        Column("note", mysql.TEXT),
        Column("last_as_status", mysql.BOOLEAN),
        Column('last_as_date', Date),
        Column('last_modified', Date),
        Column("stb_status_info", mysql.TEXT),
        Column('last_as_call', Date)
    )


    stb_id: int
    slot_id: int
    smart_card_id: Optional[int] = None
    account_id: Optional[int] = None
    country_code: Optional[str] = None
    hardware_name: Optional[str] = None
    chipId: Optional[str] = None
    deviceid: Optional[str] = None
    mac_address_br: Optional[str] = None
    mac_address: Optional[str] = None
    model_number: Optional[str] = None
    receiverId: Optional[str] = None
    project: Optional[str] = None
    version_number: Optional[str] = None
    serial_number: Optional[str] = None
    ip: Optional[str] = None
    personalized_pin: Optional[str] = None
    stb_status: Optional[bool] = None
    auto_rebot: Optional[bool] = None
    used_for: Optional[str] = None
    note: Optional[str] = None
    last_as_status: Optional[bool] = None
    last_as_date: Optional[Date] = None
    last_modified: Optional[Date] = None
    stb_status_info: Optional[str] = None
    last_as_call: Optional[str] = None

    slot = relationship("InfraDBSlotIaas", back_populates="stbs_iaas")
    smart = relationship("InfraSmartCardIaas", back_populates="stbs_iaas")
    account = relationship("InfraAccountIaas", back_populates="stbs_iaas")

    # last_check: datetime.datetime.isoformat()
    # slot = relationship('InfraDBRack', foreign_keys='InfraDBSlotStatus.slot_id')

#@dataclass
class InfraSmartCardIaas(Base):
    __bind_key__ = 'infradb'
    # __tablename__ = 'slot_status'
    __table__ = Table(
        'smart_card_iaas',
        Base.metadata,
        Column("smart_card_id", Integer, primary_key=True),
        Column("serial_number", String(250)),
        Column('start_date', Date),
        Column('end_date', Date),
        Column("owner", String(250)),
        Column("pin", String(4)),
        Column("bouquet", String(250)),
        Column("sub_bouquet", String(250)),
        Column("name", String(250)),
        Column("password", String(250)),
        Column("note", mysql.TEXT)
    )

    smart_card_id: int
    serial_number: Optional[str] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    owner: Optional[str] = None
    pin: Optional[str] = None
    bouquet: Optional[str] = None
    sub_bouquet: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None
    note: Optional[str] = None

    stbs_iaas = relationship("InfraDBStbIaas", back_populates="smart")

#@dataclass
class InfraAccountIaas(Base):
    __bind_key__ = 'infradb'
    # __tablename__ = 'slot_status'
    __table__ = Table(
        'account_iaas',
        Base.metadata,
        Column("account_id", Integer, primary_key=True),
        Column("account", String(250)),
        Column('customerID', String(250)),
        Column('macontractID', String(250)),
        Column("name", String(250)),
        Column("surname", String(250)),
        Column("x1accountID", String(250)),
        Column("bouquet", String(250)),
        Column("sub_bouquet", String(250)),
        Column("pin", String(4)),
        Column("email", String(250)),
        Column("password", String(250)),
        Column('start_date', Date),
        Column('end_date', Date),
        Column("note", mysql.TEXT)
    )

    account_id: int
    account: Optional[str] = None
    customerID: Optional[str] = None
    macontractID: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    x1accountID: Optional[str] = None
    bouquet: Optional[str] = None
    sub_bouquet: Optional[str] = None
    pin: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None
    note: Optional[str] = None

    stbs_iaas = relationship("InfraDBStbIaas", back_populates="account")

#@dataclass
class InfraDBStbTypeIaas(Base):
    __bind_key__ = 'infradb'
    # __tablename__ = 'slot_status'
    __table__ = Table(
        'stb_type_iaas',
        Base.metadata,
        Column("hardware_name", String(250), primary_key=True),
        Column("family", String(250))
    )
    hardware_name: Optional[str] = None
    family: Optional[str] = None
