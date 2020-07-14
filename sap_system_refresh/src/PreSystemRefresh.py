from pyrfc import Connection
from configparser import ConfigParser
import os


class PreSystemRefresh:

    def __init__(self):
        self.config = ConfigParser()
        try:
            self.config.read(os.environ["HOME"] + '/.config/sap_config.ini')
            self.creds = self.config['SAP']

            self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'],
                                   sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])
        except KeyError:
            self.config.read(os.path.expanduser('~') + '\.config\sap_config.ini')
            self.creds = self.config['SAP']

            self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'],
                                   sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])

    def users_list(self):
        try:
            tables = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='USR02', FIELDS=[{'FIELDNAME': 'BNAME'}])
        except Exception as e:
            return "Failed to fetch user's list from USR02 table: {}".format(e)

        users = []

        for data in tables['DATA']:
            for names in data.values():
                users.append(names)

        return users

    def existing_locked_users(self):
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
            return "Failed to get already locked user list: {}".format(e)

        locked_user_list = []

        for user in user_list['USERLIST']:
            locked_user_list.append(user['USERNAME'])

        return locked_user_list

    def user_lock(self, user_list, except_users_list, action):
        if action == "lock":
            func_module = 'BAPI_USER_LOCK'
        elif action == "unlock":
            func_module = 'BAPI_USER_UNLOCK'
        else:
            return "Failed! Please pass argument ['lock' | 'unlock']"

        users_locked = []
        errors = dict()
        users_exempted = []
        for user in user_list:
            if user not in except_users_list:
                try:
                    self.conn.call(func_module, USERNAME=user)
                    users_locked.append(user)
                except Exception as e:
                    errors[user] = e
                    pass
            else:
                users_exempted.append(user)

        return users_locked, errors, users_exempted

    def suspend_bg_jobs(self):
        try:
            self.conn.call("INST_EXECUTE_REPORT", PROGRAM='BTCTRNS1')
            return "Background Jobs are suspended!"
        except Exception as e:
            return "Failed to Suspend Background Jobs: {}".format(e)

    def export_sys_tables(self):
        params = dict(
            NAME='ZTABEXP',
            OPSYSTEM='Linux',
            OPCOMMAND='R3trans',
            PARAMETERS='-w /tmp/exp_ecc.log /tmp/exp.ctl'
        )

        try:
            self.conn.call("ZARCHIVFILE_CLIENT_TO_SERVER", PATH="", TARGETPATH='/tmp')
        except Exception as e:
            return "Error while copying exp.ctl file to SAP server: {}".format(e)

        try:
            self.conn.call("ZSXPG_COMMAND_INSERT", COMMAND=params)
        except Exception as e:
            return "Error while inserting Command arguments: {}".format(e)

        try:
            self.conn.call("SXPG_COMMAND_EXECUTE", COMMANDNAME='ZTABEXP')
            return "Successfully Exported Quality System Tables"
        except Exception as e:
            return "Error while exporting system tables: {}".format(e)

    def check_variant(self, report, variant_name):
        try:
            output = self.conn.call("RS_VARIANT_CONTENTS_RFC", REPORT=report, VARIANT=variant_name)
        except Exception as e:
            return "Failed to check variant {}: {}".format(variant_name, e)

        var_content = []

        for key, value in output.items():
            if key == 'VALUTAB':
                var_content = value

        for cont in var_content:            # Export Printer devices
            if cont['SELNAME'] == 'FILE' and cont['LOW'] == '/tmp/printers':
                return True

        for cont in var_content:            # User Master Export
            if cont['SELNAME'] == 'COPYCLI' and cont['LOW'] == self.creds['client']:
                return True

        for cont in var_content:            # Delete_old_bg_jobs
            if cont['SELNAME'] == 'FORCE' and cont['LOW'] == 'X':
                return True

        for cont in var_content:            # Delete_outbound_queues_SMQ1
            if cont['SELNAME'] == 'DISPLAY' and cont['LOW'] == 'X':
                return True

        for cont in var_content:            # Delete_outbound_queues_SMQ2
            if cont['SELNAME'] == 'SET_EXEC' and cont['LOW'] == 'X':
                return True

        return False

    def create_variant(self, report, variant_name, desc, content, text, screen):
        try:
            self.conn.call("RS_CREATE_VARIANT_RFC", CURR_REPORT=report, CURR_VARIANT=variant_name, VARI_DESC=desc,
                           VARI_CONTENTS=content, VARI_TEXT=text, VSCREENS=screen)
        except Exception as e:
            return "Variant {} for report {} Creation is Failed! : {}".format(variant_name, report, e)

        if self.check_variant(report, variant_name) is True:
            return "Variant {} Successfully Created for report {}".format(variant_name, report)
        else:
            return "Creation of variant {} for report {} is Failed!!".format(variant_name, report)

    def delete_variant(self, report, variant_name):
        try:
            self.conn.call("RS_VARIANT_DELETE_RFC", REPORT=report, VARIANT=variant_name)
        except Exception as e:
            return "Deletion of variant {} of report {} is Failed!: {}".format(variant_name, report, e)

        if self.check_variant(report, variant_name) is False:
            return "Variant {} for report {} is Successfully Deleted".format(variant_name, report)
        else:
            return "Failed to delete variant {} for report {}".format(variant_name, report)

    def export_printer_devices(self, report, variant_name):
        try:
            self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=report, IV_REPNAME=report, IV_VARNAME=variant_name)
            return "Exported printer devices Successfully"
        except Exception as e:
            return "Failed to export printer devices! {}".format(e)

    def sid_ctc_val(self):
        try:
            output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='E070L')  # IF Condition check needs to be implemented
        except Exception as e:
            return "Failed to get current transport sequence number from E070L Table: {}".format(e)

        result = dict()
        trans_val = None
        for data in output['DATA']:
            for val in data.values():
                trans_val = ((val.split()[1][:3] + 'C') + str(int(val.split()[1][4:]) + 1))
                result["trans_val"] = trans_val

        try:
            output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='TMSPCONF')
        except Exception as e:
            return "Failed while fetching TMC CTC Value: {}".format(e)

        ctc = None
        bin_path = None
        for field in output['DATA']:
            if field['WA'].split()[1] == 'CTC' and self.creds['sid'] in field['WA'].split()[0]:
                ctc = field['WA'].split()[2]
            if field['WA'].split()[1] == 'TRANSDIR' and self.creds['sid'] in field['WA'].split()[0]:
                bin_path = field['WA'].split()[2] + '/bin'

        if ctc is '1':
            sid_ctc_val = self.creds['sid'] + '.' + self.creds['client']
            result["sid_ctc_val"] = sid_ctc_val
        else:
            sid_ctc_val = self.creds['sid']
            result["sid_ctc_val"] = sid_ctc_val

        result["bin_path"] = bin_path
        result["client"] = self.creds['client']
        result["sid_val"] = self.creds['sid']

        if trans_val and ctc is not None:
            return result
        else:
            return False

    def user_master_export(self, report, variant_name):
        try:
            self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=report, IV_REPNAME=report, IV_VARNAME=variant_name)
            return "User Master Export is Completed!"
        except Exception as e:
            return "User Master Export is Failed!! {}".format(e)

# 1. System user lock               = Done
# 2. Suspend background Jobs        = Done
# 3. Export Quality System Tables   = Not Done # Funciton module is not callable
# 4. Export Printer Devices         = Done     # SSH to fetch /tmp/printers file from target to ansible controller node.
# 5. User Master Export             = Done     # SSH to fetch user master exported file.

