import logging
from sqlalchemy import and_
from .models.infradb_Iaas import  InfraDBRackIaas,InfraDBSlotIaas,InfraDBStbIaas ,InfraSmartCardIaas, InfraAccountIaas
from .models.infradb_Iaas import InfraDBStbTypeIaas
from .models.sql_alchemy_engine import SqlAlchemyEngine
from contextlib import contextmanager


@contextmanager
def session_scope():
    #get session from session manaer from sincleton
    session = SqlAlchemyEngine().getSessiomMaker()()
    try:
        # executes the code launched with the 'with' clause
        yield session
        session.commit()
    except Exception as e:
        #in case of exception make db rollaack and print exeprion
        session.rollback()
        print (e)
    finally:
        #I always close the session even in case of error
        session.close()

#decorator that provide to open/close session the first parameter of function must be session
def db_connect(function):
    def wrapper(*args, **kwargs):
        to_return= None
        #lanch function with 'with' clausule
        with session_scope() as session:
                #add session as first paramiter
                to_return=function(session, *args, **kwargs)
        return to_return
    return wrapper

@db_connect
def fetch_slots_versions_with_dinamic_filter(session , projects=None, platforms=None, country=None, rack_name=None,
                                             slot_version=None):
    stbs = []
    try:
        query = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
            .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
            .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id)
        conditions = []
        if projects:
            if isinstance(projects, (list, tuple, set)):
                conditions.append(InfraDBStbIaas.project.in_(projects))
        if platforms:
            if isinstance(platforms, (list, tuple, set)):
                conditions.append(InfraDBStbIaas.hardware_name.in_(platforms))
        if country:
            conditions.append(InfraDBStbIaas.country_code == country)
        if rack_name:
            conditions.append(InfraDBRackIaas.name == rack_name)
        if slot_version:
            conditions.append(InfraDBStbIaas.version_number == slot_version)
        if conditions:
            query = query.filter(and_(*conditions))
        logging.info(f"QUERY {query}")
        query = query.all()
        stbs = []
        for item in query:
            stb = {}
            stb["rack_ip"] = item[0].ip
            stb["rack_name"] = item[0].name
            stb["slot"] = item[1].slot_number
            stb["version"] = item[2].model_number
            stb["project"] = item[2].project
            stb["country"] = item[2].country_code
            stb["hardware_name"] = item[2].hardware_name

            stbs.append(stb)
    except Exception as e:
        #in case of exception make db rollaack and print exeprion
        session.rollback()
        print (e)
    finally:
        #I always close the session even in case of error
        session.close()

    return stbs

@db_connect
def query_stb_info(session,ip, slot):
    """
    Return info of DUT database
    :param session provided by decoretor
    :param ip: ip rack
    :param slot: slot stb
    :return: stb_type,pin,ip,sw_ver,territory,
    """

    logging.info(f"Passed Param :{locals().values()}")
    #make join to take data fron db
    ret = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas, InfraSmartCardIaas, InfraAccountIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .outerjoin(InfraSmartCardIaas, InfraSmartCardIaas.smart_card_id == InfraDBStbIaas.smart_card_id) \
        .outerjoin(InfraAccountIaas, InfraAccountIaas.account_id == InfraDBStbIaas.account_id) \
        .filter(InfraDBRackIaas.ip == ip) \
        .filter(InfraDBSlotIaas.slot_number == slot).first()

    #generate hardware string fron db data for back compatibility
    #ret[2] is InfraDBStbIaas from join
    hw_string = create_hw_string(ret[2].hardware_name, ret[2].country_code)
    # generate create_country_cod fron db data for back compatibility
    country_code = create_country_code(ret[2].country_code)

    # search for correct pin ret[2] is InfraDBStbIaas ret[4] is InfraAccountIaas ret[3] is InfraSmartCardIaas from join
    if ret[2].personalized_pin != "" and ret[2].personalized_pin is not None:
        pin = ret[2].personalized_pin
    elif ret[4] is not None and (ret[4].pin != "" and ret[4].pin is not None):
        pin = ret[4].pin
    elif ret[3] is not None and (ret[3].pin != "" and ret[3].pin is not None):
        pin = ret[3].pin
    else:
        pin = ""

    return hw_string, pin, ret[2].ip, ret[2].version_number, country_code, ret[0].name


@db_connect
def get_stb_status_broken(session,ip, slot):
    """
    Check if device broken or not
    :param session provided by decoretor
    :param ip: ip rack
    :param slot: num STB
    :return: True/False
    """
    # make join to take data fron db
    res=session.query(InfraDBRackIaas,InfraDBSlotIaas,InfraDBStbIaas)\
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id== InfraDBRackIaas.rack_id)\
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id== InfraDBSlotIaas.slot_id)\
        .filter(InfraDBRackIaas.ip==ip)\
        .filter(InfraDBSlotIaas.slot_number==slot).first()
   #if there is a stb in the indicated slot I return the inverted state otherwise I return True (inverted False)
    if res is not None and len(res) >2 :
        ret= res[2].stb_status
    else :
        ret = False
    #the parameter must be inverted for compatibility with the old db
    return  not ret

@db_connect
def update_broken_status(session, ip, slot, broken, auto_reboot=True):
    """
    Update status BROKEN True or False
    :param session provided by decoretor
    :param ip: ip rack
    :param slot: slot stb
    :param broken: bool (True/False)
    :return: void
    """
    try:
        # make join to take data fron db
        ret = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
            .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
            .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
            .filter(InfraDBRackIaas.ip == ip) \
            .filter(InfraDBSlotIaas.slot_number == slot).first()
        # stb is the third member of the query
        stb= ret[2]
        if stb:
            #update the stb parameters. The decorator will take care of the commit
            #the parameter must be inverted for compatibility with the old db
            stb.stb_status=not broken
            stb.auto_rebot=auto_reboot
            print("stb aggiornato:", stb.stb_id)
        else:
            logging.error(f'no fond stb')
        logging.info(f'status: IP: {ip} - SLOT: {slot} - stb_id: { stb.stb_id} - BROKEN: {broken} - AUTOREBOOT: {auto_reboot}')
    except Exception as e:
        logging.error(f'Error in update broken status: {e}')

@db_connect
def get_broken_from_rack(session,ip_rack):
    """
    return list of broken devices by IP RACK
    :param session provided by decoretor
    :param ip_rack: rack_ip:
    :return: json rack_ip slots
    """
    json_broken = {'rack_ip': ip_rack, 'slots': None}
    list_slot = []
    parameters = {"ip_rack": ip_rack}
    # make join to take data fron db
    res = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .filter(InfraDBRackIaas.ip == ip_rack) \
        .filter(InfraDBStbIaas.stb_status == False).all()
    #Organize the data to be returned in a list for backwards compatibility
    if res is not None and len (res)>0:
        for single_slot in res:
            list_slot.append(single_slot[1].slot_number)
        json_broken['slots'] = list_slot
    return json_broken



@db_connect
def query_stb_project_info(session,ip, slot):
    """
    Return info of DUT database
    :param session provided by decoretor
    :param ip: ip rack
    :param slot: slot stb
    :return: stb_type, pin, ip, sw_ver, territory, server_name, project
    """
    logging.info(f"Passed Param :{locals().values()}")
    # make join to take data fron db
    ret = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas, InfraSmartCardIaas, InfraAccountIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .outerjoin(InfraSmartCardIaas, InfraSmartCardIaas.smart_card_id == InfraDBStbIaas.smart_card_id) \
        .outerjoin(InfraAccountIaas, InfraAccountIaas.account_id == InfraDBStbIaas.account_id) \
        .filter(InfraDBRackIaas.ip == ip) \
        .filter(InfraDBSlotIaas.slot_number == slot).first()

    # generate hardware string and contry_code fron db data for backwards compatibility
    hw_string= create_hw_string(ret[2].hardware_name,ret[2].country_code)
    country_code= create_country_code(ret[2].country_code)
    # The correct pin is found
    if ret[2].personalized_pin != "" and ret[2].personalized_pin is not None:
        pin = ret[2].personalized_pin
    elif ret[4] is not None and (ret[4].pin != "" and ret[4].pin is not None):
        pin = ret[4].pin
    elif ret[3] is not None and (ret[3].pin != "" and ret[3].pin is not None):
        pin = ret[3].pin
    else:
        pin = ""

    return hw_string,pin,ret[2].ip,ret[2].version_number,country_code,ret[0].name,ret[2].project

def create_hw_string(hardware_name,country_code) :
    # generate hardware string fron db data for backwards compatibility
    if hardware_name is None or country_code is None :
        return None
    if hardware_name.upper()=='FALCON' :
        if country_code.upper()=='ITA' :
            return 'eu-q-falconv2-it'
        elif country_code.upper()=='DEU' :
            return 'eu-q-falconv2-de'
        elif country_code.upper()=='IRL' or country_code.upper()=='GBR' :
            return 'eu-q-falconv2-uk'
    elif hardware_name.upper() == 'AMIDALA':
        if country_code.upper() == 'ITA':
            return 'eu-q-amidala-it'
        elif country_code.upper() == 'DEU':
            return 'eu-q-amidala-de'
        elif country_code.upper() == 'IRL' or country_code.upper() == 'GBR':
            return 'eu-q-amidala-uk'
    elif hardware_name.upper() == 'TITAN':
        if country_code.upper() == 'ITA':
            return 'eu-q-titan-it'
        elif country_code.upper() == 'DEU':
            return 'eu-q-titan-de'
        elif country_code.upper() == 'IRL' or country_code.upper() == 'GBR':
            return 'eu-q-titan-uk'
    elif hardware_name.upper() == 'LLAMA':
        if country_code.upper() == 'ITA':
            return 'eu-q-llama-x3-it'
        elif country_code.upper() == 'DEU':
            return 'eu-q-llama-x3-de'
        elif country_code.upper() == 'IRL' or country_code.upper() == 'GBR':
            return 'eu-q-llama-x3-uk'
    elif hardware_name.upper()=='X-WING' :
        if country_code.upper()=='IRL' or country_code.upper()=='GBR' :
            return 'eu-q-falconv2-uk'
    elif hardware_name.upper() == 'MRBOX':
        if country_code.upper() == 'ITA':
            return 'eu-q-mr412-it'
        elif country_code.upper() == 'DEU':
            return 'eu-q-mr412-de'
        elif country_code.upper() == 'IRL' or country_code.upper() == 'GBR':
            return 'eu-q-mr412-uk'
    elif hardware_name.upper() == 'AMIDALA_HIP':
            return 'eu-q-amidala-it-hip'
    elif hardware_name.upper() == 'STREAM':
        if country_code.upper() == 'ITA':
            return 'sky-stream-it'
        elif country_code.upper() == 'DEU':
            return 'sky-stream-de'
        elif country_code.upper() == 'IRL' or country_code.upper() == 'GBR':
            return 'sky-stream-uk'
    elif hardware_name.upper() == 'XI1':
        return 'XiOne'
    elif hardware_name.upper() == 'SKY+':
        return 'skyplushd'
    elif hardware_name.upper() == "MYSKYHD" :
        return "Fusion"
    else:
        return hardware_name

def create_country_code(country_code) :
    # generate hardware  contry_code fron db data for backwards compatibility
    if country_code.upper() == "ITA" :
        return "it"
    if country_code.upper() == "DEU" :
        return "de"
    if country_code.upper() == "GBR" or country_code.upper() == "IRL" :
        return "uk"

@db_connect
def get_all_stb (session):
    #I retrieve all stbs from db
    ret = session.query(InfraDBStbIaas).all()
    session.expunge_all()
    return ret
@db_connect
def put_stb(session,stb):
    #add a stb to db
    session.add(stb)


@db_connect
def get_rack_slot_by_ip (session,ip):

    """
    :param session provided by decoretor
    :param ip ip of a stb
    :return: rack ip , slot number
    """
    # return slot numer and rack ip from ip of a stb
    ret = session.query(InfraDBRackIaas,InfraDBSlotIaas,InfraDBStbIaas) \
                .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
                .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
                .filter(InfraDBStbIaas.ip == ip).first()
    return ret[0].ip , ret[1].slot_number
	

@db_connect
def available_slots(session,project, hw_type):
    """
    :param session provided by decoretor
    :param project: es. SAAS, APPS, TEST
    :param hw_type : platform:
    :return: num_slots available for test
    """
    logging.info(f"Passed Param :{locals().values()}")
    # make join to take data fron db, count number of slot for given project and hw_type
    ret= session.query(InfraDBRackIaas,InfraDBSlotIaas,InfraDBStbIaas,InfraDBStbTypeIaas) \
                .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
                .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
                .outerjoin(InfraDBStbTypeIaas, InfraDBStbIaas.hardware_name == InfraDBStbTypeIaas.hardware_name) \
                .filter(InfraDBStbIaas.project == project).filter(InfraDBStbTypeIaas.family == hw_type)\
                .filter(InfraDBStbIaas.stb_status == True).count()
    return ret
@db_connect
def get_auto_reboot(session):
    """
        Fetches slot num and rack ip information for slots that require auto-reboot from infrastructure database.
        :param session provided by decoretor
        :returns: A list of dictionaries, where each dictionary contains slot num and rack ip.
                List is empty if something went wrong in fetching data or no slots with auto-reboot
        :rtype: list
        """
    try:
        # make join to take data fron db
        res = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
            .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
            .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
            .filter(InfraDBStbIaas.auto_rebot == True).all()
        dict_list=[]
        # Organize the data to be returned in a list for backwards compatibility
        for item in res :
            dict = {}
            dict['slot'] = item[1].slot_number
            dict['magiq'] = item[0].ip
            dict_list.append(dict)
        return dict_list
    except Exception as e:
        print(f"Error fetching data from MySQL database: {str(e)}")
        return []

@db_connect
def get_ip(session,slot_num ,server_name ,server_ip) :
    """
        Return ip of given stb.
        :param session provided by decoretor
        :slot_num numer of slot
        :server_name name of rack (can be null if specify server_ip)
        :server_ip name of rack (can be null if specify server_name)
        :returns: ip of given stb
        :rtype: list
        """
    stb_ip = None
    query = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .filter(InfraDBSlotIaas.slot_number == slot_num)


    if server_name:
        res = query.filter(InfraDBRackIaas.name == server_name).first()
    elif server_ip:
        res = query.filter(InfraDBRackIaas.ip == server_ip).first()
    else:
        res = None
    if res :
        stb_ip = res[2].ip

    return stb_ip
@db_connect
def get_stbs_by_project(session,project) :
    """
        Fetches all slot  of a projrcct.
        :param session provided by decoretor
        :praram project the project whose stb you want to know.
        :returns: A list of stb
        :rtype: list
        """
    # make join to take data fron db
    query = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .filter(InfraDBStbIaas.project == project).all()
    # Organize the data to be returned in a list for backwards compatibility
    stbs=[]
    for item in query :
        stb={}
        stb["rack_ip"]= item[0].ip
        stb["slot"] = item[1].slot_number
        stbs.append(stb)

    return stbs
@db_connect
def fetch_slots_versions(session,project) :
    # make join to take data fron db
    """
        Fetches all slot  of a projrcct.
        :param session provided by decoretor
        :praram project the project whose slots you want to know.
        :returns: A list of slots
        :rtype: list
    """
    query = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .filter(InfraDBStbIaas.project == project).all()
    # Organize the data to be returned in a list for backwards compatibility
    stbs=[]
    for item in query :
        stb={}
        stb["rack_ip"]= item[0].ip
        stb["slot"] = item[1].slot_number
        stb["version"] = item[2].model_number
        stbs.append(stb)
    return stbs

@db_connect
def fetch_slots_versions_with_dinamic_filter(session,projects=None, platforms=None, country=None, rack_name=None,
                                             slot_version=None):
    stbs = []
    query = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id)
    conditions = []
    if projects:
        if isinstance(projects, (list, tuple, set)):
            conditions.append(InfraDBStbIaas.project.in_(projects))
    if platforms:
        if isinstance(platforms, (list, tuple, set)):
            conditions.append(InfraDBStbIaas.hardware_name.in_(platforms))
    if country:
        conditions.append(InfraDBStbIaas.country_code == country)
    if rack_name:
        conditions.append(InfraDBRackIaas.name == rack_name)
    if slot_version:
        conditions.append(InfraDBStbIaas.version_number == slot_version)
    if conditions:
        query = query.filter(and_(*conditions))
    logging.info(f"QUERY {query}")
    query = query.all()
    stbs = []
    for item in query:
        stb = {}
        stb["rack_ip"] = item[0].ip
        stb["rack_name"] = item[0].name
        stb["slot"] = item[1].slot_number
        stb["version"] = item[2].model_number
        stbs.append(stb)
    return stbs

@db_connect
def fetch_rack_slot_type_by_project(session,project) :
    # make join to take data fron db
    """
        Fetches all slot  of a projrcct.
        :param session provided by decoretor
        :praram project the project whose slots you want to know.
        :returns: A list of slots
        :rtype: list
    """
    query = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .filter(InfraDBStbIaas.project == project)\
        .filter(InfraDBSlotIaas.status_slot==True)\
        .filter(InfraDBStbIaas.stb_status==True).all()
    # Organize the data to be returned in a list for backwards compatibility
    stbs=[]
    for item in query :
        stb={}
        stb["rack_name"]= item[0].name
        stb["slot"] = item[1].slot_number
        stb["device_type"] = item[2].hardware_name
        stbs.append(stb)
    return stbs
@db_connect
def fetch_rack_slot_by_project_and_type(session,project,device_type) :
    # make join to take data fron db
    """
        Fetches all slot  of a projrcct.
        :param session provided by decoretor
        :praram project the project whose slots you want to know.
        :returns: A list of slots
        :rtype: list
    """
    query = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .filter(InfraDBStbIaas.project == project) \
        .filter(InfraDBStbIaas.hardware_name == device_type) \
        .filter(InfraDBSlotIaas.status_slot==True)\
        .filter(InfraDBStbIaas.stb_status==True).all()
    # Organize the data to be returned in a list for backwards compatibility
    stbs=[]
    for item in query :
        stb={}
        stb["rack_name"]= item[0].name
        stb["slot"] = item[1].slot_number
        stbs.append(stb)
    return stbs

@db_connect
def fetch_rack_slot_type_by_project_grouped_by_rack(session,project) :
    # make join to take data fron db
    """
        Fetches all slot  of a projrcct.
        :param session provided by decoretor
        :praram project the project whose slots you want to know.
        :returns: A list of slots gruped by rack
        :rtype: list
    """
    query = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .filter(InfraDBStbIaas.project == project)\
        .filter(InfraDBSlotIaas.status_slot==True)\
        .filter(InfraDBStbIaas.stb_status==True).all()
    # Organize the data to be returned as required
    stbs= {}
    for item in query :
        stb={}
        stb["slot"] = item[1].slot_number
        stb["device_type"] = item[2].hardware_name
        if item[0].name not in stbs :
            stbs[item[0].name]={}
            stbs[item[0].name]["devices"]=[]
        stbs[item[0].name]["devices"].append(stb)
    racks=[]
    for key in stbs :
        rack={}
        rack["rack_name"]=key
        rack["devices"]=stbs[key]["devices"]
        racks.append(rack)
    to_return={}
    to_return["records"]=racks
    return to_return

@db_connect
def fetch_rack_slot_by_project_and_type_grouped_by_rack(session,project,device_type) :
    # make join to take data fron db
    """
        Fetches all slot  of a projrcct.
        :param session provided by decoretor
        :praram project the project whose slots you want to know.
        :praram type of device es "Amidala"
        :returns: A list of slots
        :rtype: list
    """
    query = session.query(InfraDBRackIaas, InfraDBSlotIaas, InfraDBStbIaas) \
        .outerjoin(InfraDBSlotIaas, InfraDBSlotIaas.rack_id == InfraDBRackIaas.rack_id) \
        .outerjoin(InfraDBStbIaas, InfraDBStbIaas.slot_id == InfraDBSlotIaas.slot_id) \
        .filter(InfraDBStbIaas.project == project) \
        .filter(InfraDBStbIaas.hardware_name == device_type) \
        .filter(InfraDBSlotIaas.status_slot==True)\
        .filter(InfraDBStbIaas.stb_status==True).all()
    # Organize the data to be returned as required
    stbs= {}
    for item in query :
        stb={}
        stb["slot"] = item[1].slot_number
        #stb["device_type"] = item[2].hardware_name
        if item[0].name not in stbs :
            stbs[item[0].name]={}
            stbs[item[0].name]["devices"]=[]
        stbs[item[0].name]["devices"].append(stb)
    racks=[]
    for key in stbs :
        rack={}
        rack["rack_name"]=key
        rack["devices"]=stbs[key]["devices"]
        racks.append(rack)
    to_return={}
    to_return["records"]=racks
    return to_return

def deprecated_sql_alchemy_connector_message(function):
    def wrapper(*args, **kwargs):
        logging.error(f'metod sql_alchemy_connector() is depecrated , uses decorator db_connect instead')
        return function(*args, **kwargs)
    return wrapper

@deprecated_sql_alchemy_connector_message
@DeprecationWarning
def sql_alchemy_connector() :
    #metod sql_alchemy_connector() is depecrated , uses decorator db_connect instead
    return None

if __name__ == "__main__" :
    """"
    print(query_stb_info("10.170.0.7", 1))
    print(query_stb_info("10.170.0.7", 16))
    print(query_stb_info("10.170.0.7", 2))
    print(get_stb_status_broken("10.170.0.7", 1))
    print(get_stb_status_broken("10.170.0.7", 16))
    print(get_stb_status_broken("10.170.0.7", 2))
    update_broken_status("10.170.3.71", 1, False, auto_reboot=True)
    update_broken_status("10.170.3.71", 8, False, auto_reboot=True)
    print(get_broken_from_rack("10.170.1.39"))
    print(get_broken_from_rack("10.170.1.139"))
    print(get_broken_from_rack("10.158.8.199"))
    print(query_stb_project_info("10.170.0.7", 1))
    print(query_stb_project_info("10.170.0.7", 16))
    print(query_stb_project_info("10.170.0.7", 2))
    print(get_all_stb())
    print(get_rack_slot_by_ip("10.170.0.118"))
    print(available_slots("PCC", "Llama"))
    print(get_auto_reboot())
    print(get_ip("8" ,"STHD 04" ,None))
    print(get_ip("8", None, "10.170.0.103"))
    print(get_stbs_by_project("PCC"))
    print(get_stbs_by_project("ACI"))
    print(fetch_slots_versions("PCC"))
    print(fetch_slots_versions("ACI"))
    print(query_stb_project_info("10.170.0.7", 1))
    print(query_stb_project_info("10.170.0.7", 16))
    sql_alchemy_connector()    
    ret=get_all_stb()
    for stb in ret :
        if stb.ip == "10.170.0.16" :
            stb.note="prova"
            print ("ip trovato")
            put_stb(stb)
    print (fetch_server_name_slot_number_type_by_project("Team_CA"))
    print (fetch_server_name_slot_number_by_project_and_type("Team_CA","Amidala"))
    """
#res= fetch_slots_versions("TEST")
