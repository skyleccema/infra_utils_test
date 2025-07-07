
from flask import current_app

import re
import json
import datetime
import pytz
from bson import objectid


# ---------------------------------------------------------------------------
#  -- MONGODB JSON CONVERT -- mongodb_to_json
# ---------------------------------------------------------------------------
def mongodb_to_json(obj):

    def mos_mongodb_handler(x):
        if isinstance(x, datetime.datetime):
            return x.isoformat()
        elif isinstance(x, objectid.ObjectId):
            return str(x)
        else:
            raise TypeError(x)

    temp = json.dumps(list(obj), default=mos_mongodb_handler)

    return json.loads(temp)


# ---------------------------------------------------------------------------
#  --  STRDATE TO DATE --
# ---------------------------------------------------------------------------
def strdate_to_date(strdate):
    origin_date = "1970-01-01"
    tz_utc = pytz.utc
    tz_ita = pytz.timezone("Europe/Rome")
    if not isinstance(strdate, str):
        current_app.logger.error("strdate_to_date - Argument is not a string: (%s) - %s" % (type(strdate), strdate))
        strdate=""
    try:
        # tz = datetime.datetime.now().astimezone().tzinfo
        if strdate[-1:] == "Z":
            strdate = strdate[:len(strdate)-1]
            tz = tz_utc     # pytz.timezone("UTC")
        else:
            tz = tz_ita
        # Format ISO (2022-08-02T00:00:00.000+00:00)
        if re.search("^\d{4,4}-\d{2,2}-\d{2,2}[T ]\d{2,2}:\d{2,2}:\d{2,2}", strdate):
            dt_no_tz = datetime.datetime.fromisoformat(strdate[0:19])
            dt = tz.localize(dt_no_tz)
        # Format  '%Y-%m-%d'
        elif re.search("^\d{4,4}-\d{2,2}-\d{2,2}$", strdate):
            dt_no_tz = datetime.datetime.strptime(strdate, '%Y-%m-%d')
            dt = tz_utc.localize(dt_no_tz)
        else:
            # dt = None
            dt_no_tz = datetime.datetime.strptime(origin_date, '%Y-%m-%d')
            dt = tz_utc.localize(dt_no_tz)
            current_app.logger.error("-- Error converting date: %s - using %s" % (strdate, origin_date))
    except ValueError as e:
        dt_no_tz = datetime.datetime.strptime(origin_date, '%Y-%m-%d')
        dt = tz_utc.localize(dt_no_tz)
        current_app.logger.error("Error converting date: %s" % strdate)
        # dt = datetime.datetime.now().astimezone(pytz.timezone("UTC"))
    return dt


# ---------------------------------------------------------------------------
#  --  JSON FILTER FIELDS -
# ---------------------------------------------------------------------------
def json_filter_fields(data=None, valid_fields=None, remove_empty=True):

    if valid_fields is None:
        valid_fields = []
    if data is None:
        data = {}

    for i in data.copy().keys():
        # -- remove if not in valid_fields
        if i not in valid_fields:
            del data[i]
            continue
        # -- remove if is an empty string
        if remove_empty:
            if data[i] == "":
                del data[i]
    return data


# ---------------------------------------------------------------------------
#  -- json_lis_fake_date_parser --
# convert string ["$gt", "$gte", "$lt", "$lte"] in datetime
def json_lis_fake_date_parser(json_obj):
    if isinstance(json_obj, dict):
        for key in json_obj.keys():
            if key in ["$gt", "$gte", "$lt", "$lte"]:
                json_obj[key] = strdate_to_date(json_obj[key])
            json_obj[key] = json_lis_fake_date_parser(json_obj[key])
    elif isinstance(json_obj, list):
        for key in json_obj:
            key = json_lis_fake_date_parser(key)
    return json_obj
