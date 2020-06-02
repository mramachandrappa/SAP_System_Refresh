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
        output = self.conn.call("RFC_READ_TABLE", QUERY_TABLE='TMSPCONF',
                                FIELDS=[{'FIELDNAME': 'NAME'}, {'FIELDNAME': 'SYSNAME'}, {'FIELDNAME': 'VALUE'}])
    except Exception as e:
        return "Failed while fetching TMC CTC Value: {}".format(e)

    ctc = None
    for field in output['DATA']:
        if field['WA'].split()[0] == 'CTC' and field['WA'].split()[1] == self.creds['sid']:
            ctc = field['WA'].split()[2]

    if ctc is '1':
        sid_ctc_val = self.creds['sid'] + '.' + self.creds['client']
        result["sid_ctc_val"] = sid_ctc_val
    else:
        sid_ctc_val = self.creds['sid']
        result["sid_ctc_val"] = sid_ctc_val

    result["client"] = self.creds['client']
    result["sid_val"] = self.creds['sid']

    if trans_val and ctc is not None:
        return result
    else:
        return False
