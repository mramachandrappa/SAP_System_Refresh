# -*- coding: utf-8 -*-
from pyrfc import Connection
from configparser import ConfigParser
import os
import sap_system_refresh.src.PreSystemRefresh

class PostSystemRefresh:

    def __init__(self):
        self.config = ConfigParser()
        self.config.read(os.environ["HOME"] + '/.config/sap_config.cnf')
        self.creds = self.config['SAP']

        self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'], sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])

        self.preRefresh = PreSystemRefresh()

    def testing(self):
        return self.preRefresh.users_list()

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

    def check_background_jobs(self):
        try:
            output = self.conn.call("TH_WPINFO")
        except Exception as e:
            return self.prRed("\nError while call Function Module: {}".format(e))

        wp_type = []
        for type in output['WPLIST']:
            wp_type.append(type['WP_TYP'])

        if 'BGD' in wp_type:
            return self.prRed("\nBackground work process is not set to 0. Please change it immediately")
        else:
            return self.prGreen("\nBackground work process is set to 0. Proceeding with next step")

    def import_sys_tables(self):
        try:
            self.conn.call("SXPG_COMMAND_EXECUTE", COMMANDNAME='ZTABIMP')
            return self.prGreen("\nSuccessfully Imported Quality System Tables")
        except Exception as e:
            return self.prRed("\nError while exporting system tables: {}".format(e))

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

    def del_old_bg_jobs(self):
        report = "RSBTCDEL"
        variant_name = "ZDELLOG"

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

        if self.check_variant(report, variant_name) is False:
            try:
                self.create_variant(report, variant_name, desc, content, text, screen)
            except Exception as e:
                return self.prRed("Failed to create variant {}: {}".format(variant_name, e))

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=report, IV_REPNAME=report, IV_VARNAME=variant_name)
                return self.prGreen("\nOld Background jobs logs are successfully deleted.")
            except Exception as e:
                return self.prRed("\nFailed to delete Old Background job logs: {}".format(e))
        else:
            return self.prRed("\nCreation of variant {} is failed!".format(variant_name))

    def del_outbound_queues(self, jobname, report, variant_name): #For SMQ1 and SMQ2

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

        if self.check_variant(report, variant_name) is False:
            try:
                self.create_variant(report, variant_name, desc, content, text, screen)
            except Exception as e:
                return self.prRed("\nFailed to create variant {}: {}".format(variant_name, e))

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=jobname, IV_REPNAME=report, IV_VARNAME=variant_name)
                return self.prGreen("\nSDeleted all Outbound Queues Successfully!")
            except Exception as e:
                return self.prRed("Failed to delete Outbound Queues: {}".format(e))
        else:
            return self.prRed("\nFailed to create variant {}".format(variant_name))

    def del_trfc_queues_sm58(self):
        jobname = "DELTE_SM58_QUEUES"
        report = "RSARFCDL"
        variant_name= "ZDELSM58"

        desc = dict(
            MANDT=self.creds['client'],
            REPORT=report,
            VARIANT=variant_name
        )

        content = [{'SELNAME': 'TID', 'KIND': 'P', 'LOW': '*'},
                   {'SELNAME': 'SET_EXEC', 'KIND': 'P', 'LOW': 'X'}]

        text = [{'MANDT': self.creds['client'], 'LANGU': 'EN', 'REPORT': report, 'VARIANT':variant_name, 'VTEXT': 'Delete all TRFC Queues'}]

        screen = [{'DYNNR': '1000', 'KIND': 'P'}]

        if self.check_variant(report, variant_name) is False:
            try:
                self.create_variant(report, variant_name, desc, content, text, screen)
            except Exception as e:
                return self.prRed("\nFailed to create variant {}: {}".format(variant_name, e))

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=jobname, IV_REPNAME=report, IV_VARNAME=variant_name)
                return self.prGreen("\nDeleted all TRC Queues SM58")
            except Exception as e:
                return self.prRed("\nFailed to delete Outbound Queues: {}".format(e))
        else:
            return self.prRed("\nFailed to create variant {}".format(variant_name))


