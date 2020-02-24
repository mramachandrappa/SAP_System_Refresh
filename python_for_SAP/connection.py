from pyrfc import Connection
import configparser


def connect():

    config = configparser.ConfigParser()
    config.read("/root/SAP_System_Refresh/config.cnf")
    creds = config['SAP']
    
    conn = Connection(user=creds['user'], passwd=creds['passwd'], ashost=creds['ashost'], sysnr=creds['sysnr'], sid=creds['sid'], client=creds['client'])
    
    attr = conn.get_connection_attributes()
    if attr['isoLanguage'] != u'EN':
        raise pyrfc.RFCError("Testing must be done with English language")

connect()
