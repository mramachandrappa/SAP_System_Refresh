from pyrfc import Connection
from configparser import ConfigParser
import os


class PreSystemRefresh:

    def __init__(self):
        self.config = ConfigParser()
        self.config.read(os.environ["HOME"] + '/.config/sap_config.cnf')
        self.creds = self.config['SAP']

        self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'], sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])

    def prRed(self, text):
        return "\033[91m {}\033[00m".format(text)

    def prGreen(self, text):
        return "\033[92m {}\033[00m".format(text)

    def prYellow(self, text):
        print("\033[93m {}\033[00m".format(text))

    def users_list(self):
        try:
            tables = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='USR02', FIELDS=[{'FIELDNAME': 'BNAME'}])
        except Exception as e:
            return self.prRed("\nError while fetching user's list from USR02 table: {}".format(e))

        users = []

        for data in tables['DATA']:
            for names in data.values():
                users.append(names)

        return users

    def locked_users(self):
        params = dict(
                    PARAMETER='ISLOCKED',
                    FIELD='LOCAL_LOCK',
                    SIGN='I',
                    OPTION='EQ',
                    LOW='L'
                    )
        try:
            user_list = self.conn.call("BAPI_USER_GETLIST", SELECTION_RANGE=[params])
        except Exception as e:
            return self.prRed("\nFailed to get already locked user list: {}".format(e))

        locked_user_list = []

        for user in user_list['USERLIST']:
                locked_user_list.append(user['USERNAME'])

        return locked_user_list

    def user_lock(self, user_list, except_users_list):
        users_locked = []

        for user in user_list:
            if user not in except_users_list:
                try:
                    self.conn.call('BAPI_USER_LOCK', USERNAME=user)
                    self.prGreen("\nUser: " + user + " is locked!")
                    users_locked.append(user)
                except Exception as e:
                    self.prRed("\nNot able to Lock user: " + user + "Please check! {}".format(e))
                    pass
            else:
                self.prYellow("\nUser: " + user + " is excepted from setting to Administer Lock.")

        return users_locked

    def suspend_jobs(self):
        try:
            self.conn.call("INST_EXECUTE_REPORT", PROGRAM='BTCTRNS1')
            return self.prGreen("\nBackground Jobs are suspended!")
        except Exception as e:
            return self.prRed("\nFailed to Suspend Background Jobs: {}".format(e))

    def export_sys_tables(self):
        try:
            self.conn.call("SXPG_COMMAND_EXECUTE", COMMANDNAME='ZTABEXP')
            return self.prGreen("\nSuccessfully Exported Quality System Tables")
        except Exception as e:
            return self.prRed("\nError while exporting system tables: {}".format(e))

    def check_variant(self, report, variant_name):
        try:
            output = self.conn.call("RS_VARIANT_CONTENTS_RFC", REPORT=report, VARIANT=variant_name)
        except Exception as e:
            return self.prRed("\nFailed to check variant {}: {}".format(variant_name, e))

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

        for cont in var_content:
            if cont['SELNAME'] == 'FORCE' and cont['LOW'] == 'X':
                return True

        for cont in var_content:
            if cont['SELNAME'] == 'DISPLAY' and cont['LOW'] == 'X':
                return True

        for cont in var_content:
            if cont['SELNAME'] == 'SET_EXEC' and cont['LOW'] == 'X':
                return True

        return False

    def create_variant(self, report, variant_name, desc, content, text, screen):
        try:
            self.conn.call("RS_CREATE_VARIANT_RFC", CURR_REPORT=report, CURR_VARIANT=variant_name, VARI_DESC=desc, VARI_CONTENTS=content, VARI_TEXT=text, VSCREENS=screen)
        except Exception as e:
            return self.prRed("\nVariant {} Creation is Unsuccessful!!".format(variant_name, e))

        if self.check_variant(report, variant_name) is True:
            return self.prGreen("\nVariant {} Successfully Created".format(variant_name))
        else:
            return self.prRed("\nCreation of variant {} is failed!!".format(variant_name))

    def delete_variant(self, report, variant_name):
        try:
            self.conn.call("RS_VARIANT_DELETE_RFC", REPORT=report, VARIANT=variant_name)
        except Exception as e:
            return self.prRed("\nDeletion of variant {} is failed!!: {}".format(variant_name, e))

        if self.check_variant(report, variant_name) is False:
            return self.prGreen("\nVariant {} Successfully Deleted".format(variant_name))

    def export_printer_devices(self):
        report = "RSPOXDEV"
        variant_name = "ZPRINT_EXP"

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

        if self.check_variant(report, variant_name) is False:
            try:
                self.create_variant(report, variant_name, desc, content, text, screen)
            except Exception as e:
                return e

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=report, IV_REPNAME=report, IV_VARNAME=variant_name)
                return self.prGreen("\nExported printer devices Successfully")
            except Exception as e:
                return self.prRed("\nFailed to export printer devices! {}".format(e))
        else:
            return self.prRed("\nCreation of variant {} failed!".format(variant_name))

    def user_master_export(self):
        report = "ZRSCLXCOP"
        variant_name = "ZUSR_EXP"

        try:
            output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='E070L') #IF Condition check needs to be implemented
        except Exception as e:
            return self.prRed("\nFailed to get current transport sequence number from E070L Table: {}".format(e))

        pc3_val = None
        for data in output['DATA']:
            for val in data.values():
                pc3_val = ((val.split()[1][:3] + 'C') + str(int(val.split()[1][4:]) + 1))

        try:
            result = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='TMSPCONF', FIELDS=[{'FIELDNAME': 'NAME'}, {'FIELDNAME': 'SYSNAME'}, {'FIELDNAME': 'VALUE'}])
        except Exception as e:
            return self.prRed("\nFailed while fetching TMC CTC Value: {}".format(e))

        ctc = None
        for field in result['DATA']:
            if field['WA'].split()[0] == 'CTC' and field['WA'].split()[1] == self.creds['sid']:
                ctc = field['WA'].split()[2]

        if ctc is '1':
            ctc_val = self.creds['sid'] + '.' + self.creds['client']
        else:
            ctc_val = self.creds['sid']

        desc = dict(
            MANDT=self.creds['client'],
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
                   {'SELNAME': 'TARGET', 'KIND': 'P', 'LOW': ctc_val}]

        text = [{'MANDT': self.creds['client'], 'LANGU': 'EN', 'REPORT': report, 'VARIANT': variant_name,
                 'VTEXT': 'User Master Export'}]

        screen = [{'DYNNR': '1000', 'KIND': 'P'}]

        if pc3_val is not None and self.check_variant(report, variant_name) is False:
            try:
                self.create_variant(report, variant_name, desc, content, text, screen)
            except Exception as e:
                return self.prRed("\nException occured while creating variant {}".format(e))
        else:
            return self.prRed("\nUser-Master Export : pc3_val and variant {} check failed!!".format(variant_name))

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=report, IV_REPNAME=report, IV_VARNAME=variant_name)
                return self.prGreen("\nUser Master Export is Completed!")
            except Exception as e:
                return self.prRed("\nUser Master Export is Failed!! {}".format(e))
        else:
            return self.prRed("\nVariant {} creation has unknown issues, please check!".format(variant_name))
