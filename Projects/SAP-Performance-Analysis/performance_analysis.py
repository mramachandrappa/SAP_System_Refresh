from pyrfc import Connection
from configparser import ConfigParser
import datetime
import csv

class SAPPerfAnalysis:

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("/root/SAP_System_Refresh/python_for_SAP/config.cnf")
        self.creds = self.config['SAP']

        self.conn = Connection(user=self.creds['user'], passwd=self.creds['passwd'], ashost=self.creds['ashost'], sysnr=self.creds['sysnr'], sid=self.creds['sid'], client=self.creds['client'])

    def analytics(self):
        rows = []
        try:
            output = self.conn.call("SWNC_COLLECTOR_GET_AGGREGATES", COMPONENT='TOTAL', ASSIGNDSYS='PC3', PERIODTYPE='D', PERIODSTRT=datetime.date(2020, 3, 2))
            for key, value in output.items():
                if key == 'USERTCODE':
                    usertcode = value
                    for users in usertcode:
                        rows.append(users)

            ENTRY_ID = [i['ENTRY_ID']for i in rows]
            RESPTI = [i['RESPTI']/1000 for i in rows]
            PROCTI = [i['PROCTI']/1000 for i in rows]
            CPUTI = [i['CPUTI']/1000 for i in rows]
            ROLLWAITTI = [i['ROLLWAITTI']/1000 for i in rows]
            GUITIME = [i['GUITIME']/1000 for i in rows]

#            print(ENTRY_ID)
#            print(RESPTI)
#            print(PROCTI)
#            print(CPUTI)
#            print(ROLLWAITTI)
#            print(GUITIME)

            data = zip(ENTRY_ID, RESPTI, PROCTI, CPUTI, ROLLWAITTI, GUITIME)

            with open('data.csv', 'w', newline='') as myfile:
                writer = csv.writer(myfile)
                writer.writerow(('ENTRY_ID', 'RESPTI', 'PROCTI', 'CPUTI', 'ROLLWAITTI', 'GUITIME'))
                for row in data:
                    writer.writerow(row)
                myfile.close()
        except Exception as e:
            print(e)

    def mon_header_data(self):
        rows = []
        try:
            output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='/SDF/MON_HEADER')
            for key, value in output.items():
                if key == 'DATA':
                    usertcode = value
                    for data in usertcode:
                        rows.append(data)
            print([i for i in rows])
        except Exception as e:
            print(e)

    def get_mem_all(self):
        rows = []
        try:
            output = self.conn.call("GET_MEM_ALL")
            for key, value in output.items():
                if key == 'TF_MEM_ALL':
                    mem_all = value
                    for val in mem_all:
                        rows.append(val)

            FREE_MEM = [i['FREE_MEM']/1000 for i in rows]
            PHYS_MEM = [i['PHYS_MEM']/1000 for i in rows]

            data = zip(FREE_MEM, PHYS_MEM)
        
            with open('mem_all.csv', 'w', newline='') as myfile:
                writer = csv.writer(myfile)
                writer.writerow(('FREE_MEM', 'PHYS_MEM'))
                for row in data:
                    writer.writerow(row)
                myfile.close()
        except Exception as e:
            print(e)

    def get_cpu_all(self):
        rows = []
        try:
            output = self.conn.call("GET_CPU_ALL")
            for key, value in output.items():
                if key == 'TF_CPU_ALL':
                    cpu_all = value
                    for cpu in cpu_all:
                        rows.append(cpu)

            NBR_CPU = [i['NBR_CPU'] / 1000 for i in rows]
            USR_TOTAL = [i['USR_TOTAL'] / 1000 for i in rows]
            SYS_TOTAL = [i['SYS_TOTAL'] / 1000 for i in rows]
            IDLE_TOTAL = [i['IDLE_TOTAL'] / 1000 for i in rows]

            data = zip(NBR_CPU, USR_TOTAL, SYS_TOTAL, IDLE_TOTAL)

            with open('cpu_all.csv', 'w', newline='') as myfile:
                writer = csv.writer(myfile)
                writer.writerow(('NBR_CPU', 'USR_TOTAL', 'SYS_TOTAL', 'IDLE_TOTAL'))
                for row in data:
                    writer.writerow(row)
                myfile.close()
        except Exception as e:
            print(e)

    def server_list(self):
        rows = []
        try:
            output = self.conn.call("TH_SERVER_LIST")
            for key, value in output.items():
                if key == 'LIST':
                    hosts = value
                    for val in hosts:
                        rows.append(val)

            NAME = [i['NAME'] / 1000 for i in rows]
            HOST = [i['HOST'] / 1000 for i in rows]

            data = zip(NAME, HOST)

            with open('server_list.csv', 'w', newline='') as myfile:
                writer = csv.writer(myfile)
                writer.writerow(('NAME', 'HOST'))
                for row in data:
                    writer.writerow(row)
                myfile.close()
        except Exception as e:
            print(e)


s = SAPPerfAnalysis()

#s.analytics()
#s.mon_header_data()
s.get_mem_all()
s.get_cpu_all()
s.server_list()
