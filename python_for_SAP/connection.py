from pyrfc import Connection



def connect():
    conn = Connection(user='MRAM', passwd='Sap@123', ashost='52.207.1.100', sysnr='01', client='100')

    attr = conn.get_connection_attributes()
    if attr['isoLanguage'] != u'EN':
        raise pyrfc.RFCError("Testing must be done with English language")

connect()
