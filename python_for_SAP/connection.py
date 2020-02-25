from pyrfc import Connection

try:
    from ConfigParser import ConfigParser
except ModuleNotFoundError as e:
    from configparser import ConfigParser


def connect():

    config = ConfigParser()
    config.read("/root/SAP_System_Refresh/python_for_SAP/config.cnf")
    creds = config['SAP']

    conn = Connection(user=creds['user'], passwd=creds['passwd'], ashost=creds['ashost'], sysnr=creds['sysnr'], sid=creds['sid'], client=creds['client'])

    attr = conn.get_connection_attributes()
    if attr['isoLanguage'] != u'EN':
        raise pyrfc.RFCError("Testing must be done with English language")

connect()

