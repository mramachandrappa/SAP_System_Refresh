from pyrfc import Connection
from configparser import ConfigParser


def connect():

    config = ConfigParser()
    config.read("/root/SAP_System_Refresh/python_for_SAP/config.cnf")
    creds = config['SAP']

    conn = Connection(user=creds['user'], passwd=creds['passwd'], ashost=creds['ashost'], sysnr=creds['sysnr'], sid=creds['sid'], client=creds['client'])

    tables = conn.call("RFC_GET_TABLE_ENTRIES", QUERY_TABLE='USR02')

    print(tables)

    fields= []
    fields_name = []

    data_fields = tables["DATA"]
    data_names = tables["FIELDS"]



connect()