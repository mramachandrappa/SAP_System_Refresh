from pyrfc import Connection
from configparser import ConfigParser


class Main:

    def __init__(self):
        config = ConfigParser()
        config.read("/root/SAP_System_Refresh/python_for_SAP/config.cnf")
        self.creds = config['SAP']

        self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'],
                               sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])
    
    def users_list(self, table_name):
        tables = self.conn.call("RFC_GET_TABLE_ENTRIES", TABLE_NAME=table_name)
    
        user_names = []

        for key, value in tables.items():
            if key == 'ENTRIES':
                entries = value
                for users in entries:
                    for name in users.values():
                        user_names.append(name[3:])

        print(user_names)


s = Main()
s.users_list('USR02')
