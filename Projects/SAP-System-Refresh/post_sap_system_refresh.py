from pyrfc import Connection
from configparser import ConfigParser


class SAPPostRefresh:

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("/root/Python-For-SAP/Projects/SAP-System-Refresh/config.cnf")
        self.creds = self.config['SAP']

        self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'], sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])

    def users_list(self):
        tables = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='USR02', FIELDS=[{'FIELDNAME': 'BNAME'}])

        users = []
        try:
            for data in tables['DATA']:
                for names in data.values():
                    users.append(names)
        except Exception:
            return "Error while fetching user's list"

        return users

    def locked_users(self):
        params = dict(
                    PARAMETER='ISLOCKED',
                    FIELD='LOCAL_LOCK',
                    SIGN='I',
                    OPTION='EQ',
                    LOW='L'
                    )
        tables = self.conn.call("BAPI_USER_GETLIST", SELECTION_RANGE=[params])
        locked_user_list = []

        try:
            for data in tables['USERLIST']:
                locked_user_list.append(data['USERNAME'])
        except Exception:
            return "Error while fetching locked user's list"

        f = open("post_locked_user_list.txt", "w")
        f.write(str(locked_user_list))
        f.close()

        return locked_user_list

    def user_lock(self, user_list):
        f = open("except_user_list.txt", "r")
        except_users_list = f.read()

        print("Except_users_list =>", except_users_list)

        users_locked = []
        exceptions = []

        for user in user_list:
            if user not in except_users_list:
                try:
                    self.conn.call('BAPI_USER_LOCK', USERNAME=user)
                    users_locked.append(user)
                except Exception as e:
                    exceptions.append(e)
                    pass

        return users_locked

    def suspend_jobs(self):
        try:
            self.conn.call("INST_EXECUTE_REPORT", PROGRAM='BTCTRNS1')
            return "Suspended Background Jobs"
        except Exception:
            return "Error while suspending the Jobs"

    def check_backgroud_jobs(self):
        try:
            output = self.conn.call("TH_WPINFO")
        except Exception as e:
            return e
 #           return "“Background work process is not set to 0. Please change it immediately"
        wp_type = []
        for i in output['WPLIST']:
            wp_type.append(i['WP_TYP'])

        if 'BGD' in wp_type:
            return "“Background work process is not set to 0. Please change it immediately"
        else:
            return "Background work process is set to 0. Proceeding with next step"


s = SAPPostRefresh()
#print(s.locked_users())
print(s.check_background_jobs())
