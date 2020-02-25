from pyrfc import Connection
from configparser import ConfigParser


def connect():

    config = ConfigParser()
    config.read("/root/SAP_System_Refresh/python_for_SAP/config.cnf")
    creds = config['SAP']

    conn = Connection(user=creds['user'], passwd=creds['passwd'], ashost=creds['ashost'], sysnr=creds['sysnr'], sid=creds['sid'], client=creds['client'])
    
   # conn.call("BAPI_USER_UNLOCK", USERNAME='SAP*')


    tables = conn.call("RFC_GET_TABLE_ENTRIES", TABLE_NAME='USR02')
    
    user_names = []

    for key, value in tables.items():
        print(key, '->', value)
        if key == 'ENTRIES':
            entries = value
            for users in entries:
                for name in users.values():
                    user_names.append(name[3:])

    #for users in user_names:
    #3    if users == 'BJOERN':
      #      pass
       # else:
        #    conn.call("BAPI_USER_LOCK", USERNAME=users)
    
    print(user_names)

connect()
