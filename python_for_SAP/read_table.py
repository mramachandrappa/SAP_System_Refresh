from pyrfc import Connection
from configparser import ConfigParser


class SAPRefresh:

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("/root/SAP_System_Refresh/python_for_SAP/config.cnf")
        self.creds = self.config['SAP']

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

        return user_names

    def locked_users(self):
        tables = self.conn.call("BAPI_USER_GETLIST", SELECTION_RANGE=[{'PARAMETER': 'ISLOCKED', 'FIELD': 'LOCAL_LOCK',
                                                                       'SIGN': 'I', 'OPTION': 'EQ', 'LOW': 'L'}])
        locked_user_list = []

        for key, value in tables.items():
            if key == 'USERLIST':
                user_list = value
                for users in user_list:
                    locked_user_list.append(users['USERNAME'])

        return locked_user_list

    def user_lock(self, user_list):
        self.config.read("/root/SAP_System_Refresh/python_for_SAP/exception_list.txt")
        self.users = self.config['exception_user_list']
        exception_list = self.users['users']

        for user in user_list:
            print(user)




s = SAPRefresh()
user_list = s.users_list('USR02')
locked_users = s.locked_users()
s.user_lock(user_list)



