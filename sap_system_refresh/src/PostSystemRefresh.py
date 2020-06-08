# -*- coding: utf-8 -*-
from pyrfc import Connection
from configparser import ConfigParser
import os
from sap_system_refresh.src.PreSystemRefresh import *


class PostSystemRefresh(PreSystemRefresh):
    # for post refresh step3 and step11.
    def check_background_jobs(self, stage):
        try:
            output = self.conn.call("TH_WPINFO")
        except Exception as e:
            return "Error while call Function Module: {}".format(e)

        wp_type = []
        for type in output['WPLIST']:
            wp_type.append(type['WP_TYP'])

        if stage == "step1":
            if 'BGD' in wp_type:
                return "Background work process is not set to 0. Please change it immediately"
            else:
                return "Background work process is set to 0. Proceeding with next step"
        elif stage == "step2":
            if 'BGD' in wp_type:
                return "Background work process is configured properly."
            else:
                return "Background work process is not set. Please change parameter value rdisp rdisp/wp_no_btc not equal to 0."

    # Change in Requirement.
    def import_sys_tables(self):
        try:
            self.conn.call("SXPG_COMMAND_EXECUTE", COMMANDNAME='ZTABIMP')
            return "Successfully Imported Quality System Tables"
        except Exception as e:
            return "Error while exporting system tables: {}".format(e)

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
                return "Failed to create variant {}: {}".format(variant_name, e)

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=report, IV_REPNAME=report, IV_VARNAME=variant_name)
                return "Old Background jobs logs are successfully deleted."
            except Exception as e:
                return "Failed to delete Old Background job logs: {}".format(e)
        else:
            return "Creation of variant {} is failed!".format(variant_name)

    # Deletes outbound queues SMQ1 & SMQ2
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
                return "Failed to create variant {}: {}".format(variant_name, e)

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=jobname, IV_REPNAME=report, IV_VARNAME=variant_name)
                return "Deleted all Outbound Queues Successfully!"
            except Exception as e:
                return "Failed to delete Outbound Queues: {}".format(e)
        else:
            return "Failed to create variant {}".format(variant_name)

    def del_trc_queues_sm58(self):
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
                return "Failed to create variant {}: {}".format(variant_name, e)

        if self.check_variant(report, variant_name) is True:
            try:
                self.conn.call("SUBST_START_REPORT_IN_BATCH", IV_JOBNAME=jobname, IV_REPNAME=report, IV_VARNAME=variant_name)
                return "Deleted all TRC Queues SM58"
            except Exception as e:
                return "Failed to delete Outbound Queues: {}".format(e)
        else:
            return "Failed to create variant {}".format(variant_name)

    # Testing - Phase
    def clean_ccms_data(self):
        try:
            self.conn.call("INST_EXECUTE_REPORT", PROGRAM='CSM_TAB_CLEAN')
            return "Successfully cleansed CCMS data"
        except Exception as e:
            return "Error while cleaning CCMS data: {}".format(e)

    # Testing - Phase
    def check_spool_consistency(self):
        try:
            output = self.conn.call("INST_EXECUTE_REPORT", PROGRAM='RSPO1043')
        except Exception as e:
            return "Failed while checking_spool_consistency: {}".format(e)

        data = []
        for res in output['OUTPUT_TAB']:
            for k, v in res.items():
                mes = dict()
                if v:
                    mes[k] = v
                    data.append(mes)

        return data

    # Implementation phase
    def se06_post_copy_transport(self):
        pass

    def user_master_import(self):
        try:
            output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='TMSPCONF')
        except Exception as e:
            return "Failed while calling FM TMS_TP_CHECK_TRANS_DIR: {}".format(e)

        print(output)



# Steps Completed in Post Refresh
# 1. Quality System User Lock               = Done
# 2. Suspend background jobs                = Done
# 3. Check background process               = Done
# 4. Import Quality System Tab              = Not Done  #FM not callable  (.ctl file to target sap server.)
# 5. Delete old background jobs             = Done
# 6. Delete outbound Queues SMQ1            = Done
# 7. Delete outbound Queues SMQ2            = Done
# 8. Delete TRC Queues SM58                 = Done
# 9. Clean CCMS data                        = Done
# 10. Check Spool Consistency               = Done
# 11. Set background process to normal      = Done
# 12. SE06 – Post copy transport process            = Not Done >            #SAP GUI
# 13. RDDNEWPP – RDDIMPDP background job execution  = Not Done >            #SAP GUI
# 14. User Master Import                            = Not Done >            #variants
# 15. Import all Printer output devices             = Not Done >            #SAP GUI
# 16. BDLS – Logical system conversion              = Not Done >            #variants
# 17. ZSCREEN_LOGIN_INFO - change                   = Not Done >            #variants
# 18. Quality System User Unlock                    = Done


