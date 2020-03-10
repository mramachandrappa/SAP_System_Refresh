from pyrfc import Connection
from configparser import ConfigParser


class SAPRefresh:

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("/root/Python-For-SAP/Projects/SAP-System-Refresh/config.cnf")
        self.creds = self.config['SAP']
        self.client = self.creds['client']

        self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'], sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])
    
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
        params = dict(
                    PARAMETER='ISLOCKED',
                    FIELD='LOCAL_LOCK',
                    SIGN='I',
                    OPTION='EQ',
                    LOW='L'
                    )
        tables = self.conn.call("BAPI_USER_GETLIST", SELECTION_RANGE=[params])
        locked_user_list = []

        for key, value in tables.items():
            if key == 'USERLIST':
                user_list = value
                for users in user_list:
                    locked_user_list.append(users['USERNAME'])

        f = open("locked_user_list.txt", "w")
        f.write(str(locked_user_list))
        f.close()

        return locked_user_list

    def user_lock(self, user_list):
        f = open("except_user_list.txt", "r")
        except_users_list = f.read()

        print("Except_users_list =>", except_users_list)

        users_locked = []

        for user in user_list:
            if user not in except_users_list:
                self.conn.call('BAPI_USER_LOCK', USERNAME=user)
                users_locked.append(user)

        return users_locked

    def suspend_jobs(self, program_value):

        print(self.conn.call("INST_EXECUTE_REPORT", PROGRAM=program_value))

    def export_sys_tables(self, cmd):

        print(self.conn.call("SXPG_COMMAND_EXECUTE", COMMANDNAME=cmd))

    def check_variant(self, report, variant_name):

        output = self.conn.call("RS_VARIANT_CONTENTS_RFC", REPORT=report, VARIANT=variant_name)

        var_content = None

        for key, value in output.items():
            if key == 'VALUTAB':
                var_content = value

        for cont in var_content:
            if cont['SELNAME'] == 'FILE' and cont['LOW'] == '/tmp/printers':
                return True

        return False

    def create_variant(self, report, variant_name):

        desc = dict(
            MANDT=self.client,
            REPORT=report,
            VARIANT=variant_name
        )

        content = [{'SELNAME': 'DO_SRV', 'KIND': 'P', 'LOW': 'X'},
                   {'SELNAME': '_EXP', 'KIND': 'P', 'LOW': 'X'},
                   {'SELNAME': 'DO_EXP', 'KIND': 'P', 'LOW': 'X'},
                   {'SELNAME': 'DO_LOG', 'KIND': 'P', 'LOW': 'X'},
                   {'SELNAME': 'WITH_CNF', 'KIND': 'P', 'LOW': 'X'},
                   {'SELNAME': 'DEVICE', 'KIND': 'S', 'SIGN': 'I', 'OPTION': 'CP', 'LOW': '*'},
                   {'SELNAME': 'FILE', 'KIND': 'P', 'LOW': '/tmp/printers'}]

        text = [{'MANDT': self.client, 'LANGU': 'EU', 'REPORT': report, 'VARIANT':variant_name, 'VTEXT': 'Printers Export'}]

        screen = [{'DYNNR': '1000', 'KIND': 'P'}]
        
        try:
            variant = self.conn.call("RS_CREATE_VARIANT_RFC", CURR_REPORT=report, CURR_VARIANT=variant_name, VARI_DESC=desc, VARI_CONTENTS=content, VARI_TEXT=text, VSCREENS=screen)
        except Exception as e:
            return e

        return variant

    def delete_variant(self, report, variant_name):



    def import_printer_devices(self):

        print(self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME='RSPOXDEV', IV_REPNAME='RSPOXDEV', IV_VARNAME='PRINT_IMP'))
        
        self.conn.close()

s = SAPRefresh()
#user_list = s.users_list('USR02')
#locked_users = s.locked_users()
#users_locked = s.user_lock(user_list)
s.create_variant('RSPOXDEV', 'ZPRINT_EXP')

#print("User_list =>", user_list)
#print("Already_Locked_users =>", locked_users)
#print("Final_users_locked =>", users_locked)

#s.suspend_jobs('BTCTRNS1')
#s.export_sys_tables('ZTABEXP')
#s.export_printer_devices()
#s.import_printer_devices()
