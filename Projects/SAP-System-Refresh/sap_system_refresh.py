from pyrfc import Connection
from configparser import ConfigParser


class SAPRefresh:

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

    def suspend_jobs(self):

        try:
            self.conn.call("INST_EXECUTE_REPORT", PROGRAM='BTCTRNS1')
            return "Suspended Background Jobs"
        except Exception:
            return "Error while suspending the Jobs"

    def export_sys_tables(self):

        try:
            self.conn.call("SXPG_COMMAND_EXECUTE", COMMANDNAME='ZTABEXP')
            return "Successfully Exported Quality System Tables"
        except Exception:
            return "Error while exporting system tables"

    def check_variant(self, report, variant_name):

        try:
            output = self.conn.call("RS_VARIANT_CONTENTS_RFC", REPORT=report, VARIANT=variant_name)
        except Exception as e:
            return e

        var_content = []

        for key, value in output.items():
            if key == 'VALUTAB':
                var_content = value

        for cont in var_content:
            if cont['SELNAME'] == 'FILE' and cont['LOW'] == '/tmp/printers':
                return True

        for cont in var_content:
            if cont['SELNAME'] == 'COMFILE' and cont['LOW'] == 'PC3C900006':
                return True

        return False

    def create_variant(self, report, variant_name, desc, content, text, screen):

        try:
            self.conn.call("RS_CREATE_VARIANT_RFC", CURR_REPORT=report, CURR_VARIANT=variant_name, VARI_DESC=desc, VARI_CONTENTS=content, VARI_TEXT=text, VSCREENS=screen)
        except Exception:
            raise Exception("Variant Creation is Unsuccessful!!")

        if self.check_variant(report, variant_name) is True:
            return "Variant Successfully Created"
        else:
            raise Exception("Creation of variant is failed!!")

    def delete_variant(self, report, variant_name):

        try:
            self.conn.call("RS_VARIANT_DELETE_RFC", REPORT=report, VARIANT=variant_name)
        except Exception:
            return "Variant doesn't exist"

        if self.check_variant(report, variant_name) is False:
            return "Variant Successfully Deleted"

    def export_printer_devices(self, report, variant_name):

        desc = dict(
            MANDT=self.creds['client'],
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

        text = [{'MANDT': self.creds['client'], 'LANGU': 'EN', 'REPORT': report, 'VARIANT':variant_name, 'VTEXT': 'Printers Export'}]

        screen = [{'DYNNR': '1000', 'KIND': 'P'}]

        variant = None

        if self.check_variant(report, variant_name) is False:
            try:
                self.create_variant(report, variant_name, desc, content, text, screen)
                variant = True
            except Exception as e:
                return e

        if variant is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=report, IV_REPNAME=report, IV_VARNAME=variant_name)
                return "Exported printer devices Successfully"
            except Exception as e:
                return e
        else:
            return "Please check if variant exist"

    def user_master_export(self, report, variant_name):

        try:
            output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='E070L') #IF Condition check needs to be implemented
        except Exception as e:
            return e

        pc3_val = None
        for data in output['DATA']:
            for val in data.values():
                pc3_val = ((val.split()[1][:3] + 'C') + str(int(val.split()[1][4:]) + 1))
        
        desc = dict(
            MANDT='asdf',
            REPORT=report,
            VARIANT=variant_name
        )

        content = [{'SELNAME': 'COPYCLI', 'KIND': 'P', 'LOW': self.creds['client']},
                   {'SELNAME': 'SUSR', 'KIND': 'P', 'LOW': 'X'},
                   {'SELNAME': 'MODUS', 'KIND': 'P', 'LOW': 'E'},
                   {'SELNAME': 'ALTINP', 'KIND': 'P', 'LOW': 'A'},
                   {'SELNAME': 'COMFILE', 'KIND': 'P', 'LOW': pc3_val},
                   {'SELNAME': 'PROF', 'KIND': 'P', 'LOW': 'X'},
                   {'SELNAME': 'PROFIL', 'KIND': 'P', 'LOW': 'SAP_USER'},
                   {'SELNAME': 'TARGET', 'KIND': 'P', 'LOW': self.creds['sid']}]

        text = [{'MANDT': self.creds['client'], 'LANGU': 'EN', 'REPORT': report, 'VARIANT': variant_name,
                 'VTEXT': 'User Master Export'}]

        screen = [{'DYNNR': '1000', 'KIND': 'P'}]

        variant = None

        if pc3_val is not None and self.check_variant(report, variant_name) is False:
            try:
                self.create_variant(report, variant_name, desc, content, text, screen)
                variant = True
            except Exception as e:
                return e
        else:
            return "User-Master Export : pc3_val and variant check failed!!"

        if variant is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=report, IV_REPNAME=report, IV_VARNAME=variant_name)
                return "User Master Export is Done"
            except Exception as e:
                return e
        else:
            return "Please check if variant exist"


s = SAPRefresh()

print(s.locked_users())
#user_list = s.users_list('USR02')
#locked_users = s.locked_users()
#users_locked = s.user_lock(user_list)
#print(s.create_variant('RSPOXDEV', 'ZPRINT_EXP'))
#print(s.check_variant('RSPOXDEV', 'ZPRINT_EXP'))
#print(s.delete_variant('RSPOXDEV', 'ZPRINT_EXP'))
#print(s.export_printer_devices('RSPOXDEV', 'ZPRINT_EXP'))

#print(s.user_master_export('ZRSCLXCOP', 'ZUSR_EXP'))

#print("User_list =>", user_list)
#print("Already_Locked_users =>", locked_users)
#print("Final_users_locked =>", users_locked)

#s.suspend_jobs()
#s.export_sys_tables()
#s.export_printer_devices()
#s.import_printer_devices()
