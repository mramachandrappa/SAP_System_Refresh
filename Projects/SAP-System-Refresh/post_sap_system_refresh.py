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

    def check_background_jobs(self):
        try:
            output = self.conn.call("TH_WPINFO")
        except Exception as e:
            return e

        wp_type = []
        for type in output['WPLIST']:
            wp_type.append(type['WP_TYP'])

        if 'BGD' in wp_type:
            return "“Background work process is not set to 0. Please change it immediately"
        else:
            return "Background work process is set to 0. Proceeding with next step"

    def import_sys_tables(self):
        try:
            self.conn.call("SXPG_COMMAND_EXECUTE", COMMANDNAME='ZTABIMP')
            return "Successfully Imported Quality System Tables"
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

    def del_old_bg_jobs(self, report, variant_name):
        desc = dict(
            MANDT=self.creds['client'],
            REPORT=report,
            VARIANT=variant_name
        )

        content = [{'SELNAME': 'JOBNAME', 'KIND': 'P', 'LOW': '*'},
                   {'SELNAME': 'USERNAME', 'KIND': 'P', 'LOW': '*'},
                   {'SELNAME': 'FRM_DATE', 'KIND': 'P', 'LOW': ''},
                   {'SELNAME': 'FRM_TIME', 'KIND': 'P', 'LOW': ''},
                   {'SELNAME': 'TO_DATE', 'KIND': 'P', 'LOW': ''},
                   {'SELNAME': 'TO_TIME', 'KIND': 'P', 'LOW': ''},
                   {'SELNAME': 'ENDDATE', 'KIND': 'P', 'LOW': ''},
                   {'SELNAME': 'ENDTIME', 'KIND': 'P', 'LOW': ''},
                   {'SELNAME': 'FIN', 'KIND': 'P', 'LOW': 'X'},
                   {'SELNAME': 'ABORT', 'KIND': 'P', 'LOW': 'X'},
                   {'SELNAME': 'FORCE', 'KIND': 'P', 'LOW': 'X'}]

        text = [{'MANDT': self.creds['client'], 'LANGU': 'EN', 'REPORT': report, 'VARIANT':variant_name, 'VTEXT': 'Delete background jobs logs'}]

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
                return "Old Background jobs logs are successfully deleted."
            except Exception as e:
                return e
        else:
            return "Please check if variant exist"

    def del_outbound_queues(self, jobname, report, variant_name):
        desc = dict(
            MANDT=self.creds['client'],
            REPORT=report,
            VARIANT=variant_name
        )

        content = [{'SELNAME': 'TID', 'KIND': 'P', 'LOW': '*'},
                   {'SELNAME': 'PACKAGE', 'KIND': 'P', 'LOW': '10.000'},
                   {'SELNAME': 'DISPLAY', 'KIND': 'P', 'LOW': 'X'}]

        text = [{'MANDT': self.creds['client'], 'LANGU': 'EN', 'REPORT': report, 'VARIANT':variant_name, 'VTEXT': 'Delete all outbound Queues'}]

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
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=jobname, IV_REPNAME=report, IV_VARNAME=variant_name)
                return "Deleted all outbound Queues"
            except Exception as e:
                return e
        else:
            return "Please check if variant exist"

    def del_trfc_queues_sm58(self, jobname, report, variant_name):
        desc = dict(
            MANDT=self.creds['client'],
            REPORT=report,
            VARIANT=variant_name
        )

        content = [{'SELNAME': 'TID', 'KIND': 'P', 'LOW': '*'},
                   {'SELNAME': 'SET_EXEC', 'KIND': 'P', 'LOW': 'X'}]

        text = [{'MANDT': self.creds['client'], 'LANGU': 'EN', 'REPORT': report, 'VARIANT':variant_name, 'VTEXT': 'Delete all trfc Queues'}]

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
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=jobname, IV_REPNAME=report, IV_VARNAME=variant_name)
                return "Deleted all TRC Queues SM58"
            except Exception as e:
                return e
        else:
            return "Please check if variant exist"



s = SAPPostRefresh()
#print(s.locked_users())
print(s.check_background_jobs())
