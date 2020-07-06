from DB_mgmt import *

class SwitchConfDAO():
    @staticmethod
    def addSwitch(switch_id, switch_name, dir_path):
        try:
            queryCursor.execute("INSERT INTO switches (device_id, switch_name, dir_path) VALUES (?, ?, ?)", (switch_id, switch_name, dir_path))
            dbVar.commit()
            return True
        except:
            return False

    @staticmethod
    def addTable(switch_id, table_id, table_name, match_type, table_base_address):
        if switch_id == -1:
            return False

        #Check if the switch already has a table named "table_name"
        queryCursor.execute('SELECT * FROM switch_tables WHERE table_id=? AND device_id=?', (table_id, switch_id))
        if(queryCursor.fetchone() is not None):
            return False

        try:
            queryCursor.execute("INSERT INTO switch_tables (device_id, table_id, table_name, match_type, base_address) VALUES (?,?,?,?,?)", (switch_id, table_id, table_name, match_type, table_base_address))
            dbVar.commit()
            return True
        except:
            return False

    @staticmethod
    def addTableMatchField(switch_id, table_id, field_id, field_name, field_type, field_size):
        if switch_id == -1:
            return False

        #Gets the table ID
        queryCursor.execute('SELECT * FROM switch_tables WHERE table_id=? AND device_id=?', (table_id,switch_id))
        row = queryCursor.fetchone()
        if(row is None):
            return False
        table_id = row[1]

        #Check if the table already has a field named "field_name"
        queryCursor.execute('SELECT * FROM table_match_fields WHERE field_name=? AND device_id=? AND table_id=?', (field_name, switch_id, table_id))
        if(queryCursor.fetchone() is not None):
            return False

        try:
            queryCursor.execute("INSERT INTO table_match_fields (device_id, table_id, field_id, field_name, field_type, field_size) VALUES (?,?,?,?,?,?)", (switch_id, table_id, field_id, field_name, field_type, field_size))
            dbVar.commit()
            return True
        except:
            return False

    @staticmethod
    def addTableAction(switch_id, table_id, action_id, action_name):
        if switch_id == -1:
            return False

        #Gets the table ID
        queryCursor.execute('SELECT * FROM switch_tables WHERE table_id=? AND device_id=?', (table_id,switch_id))
        row = queryCursor.fetchone()
        if(row is None):
            return False
        table_id = row[1]

        #Check if the table already has a action named "action_name"
        queryCursor.execute('SELECT * FROM table_actions WHERE action_id=? AND device_id=? AND table_id=?', (action_id, switch_id, action_id))
        if(queryCursor.fetchone() is not None):
            return False

        try:
            queryCursor.execute("INSERT INTO table_actions (device_id, table_id, action_id, action_name) VALUES (?,?,?,?)", (switch_id, table_id, action_id, action_name))
            dbVar.commit()
            return True
        except:
            return False

    @staticmethod
    def addTableActionField(switch_id, table_id, action_id, field_id, field_name, field_type, field_size):
        if switch_id == -1:
            return False
        # Get table ID
        queryCursor.execute('SELECT * FROM switch_tables WHERE table_id=? AND device_id=?', (table_id, switch_id))
        row = queryCursor.fetchone()
        if(row is None):
            return False
        table_id = row[1]
        #Check if the table already has a action named "action_name"
        queryCursor.execute('SELECT * FROM table_action_fields WHERE device_id=? AND table_id=? AND action_id=?', (switch_id, table_id, action_id))
        if(queryCursor.fetchone() is not None):
            return False

        try:
            queryCursor.execute("INSERT INTO table_action_fields (device_id, table_id, action_id, field_id, field_name, field_type, field_size) VALUES (?,?,?,?,?,?,?)", (switch_id, table_id, action_id, field_id, field_name, field_type, field_size))
            dbVar.commit()
            return True
        except:
            return False

    @staticmethod
    def getSwitchID(switch_name):
        queryCursor.execute('SELECT device_id FROM switches WHERE switch_name=?', (switch_name,))
        row = queryCursor.fetchone()
        if(row is None):
            return -1
        else:
            return row[0]

    @staticmethod
    def getSwitchName(switch_id):
        queryCursor.execute('SELECT switch_name FROM switches WHERE device_id=?', (switch_id,))
        row = queryCursor.fetchone()
        if (row is None):
            return False
        else:
            return row[0]

    @staticmethod
    def getSwitchPath(switch_id):
        queryCursor.execute('SELECT dir_path FROM switches WHERE device_id=?', (switch_id,))
        row = queryCursor.fetchone()
        return row[0]

    @staticmethod
    def getTableName(switch_id, table_id):
        queryCursor.execute('SELECT table_name FROM switch_tables WHERE table_id=? AND device_id=?', (table_id,switch_id))
        row = queryCursor.fetchone()
        return row[0]

    @staticmethod
    def getTableId(switch_id, table_name):
        queryCursor.execute('SELECT table_id FROM switch_tables WHERE table_name=? AND device_id=?', (table_name,switch_id))
        row = queryCursor.fetchone()
        return row[0]

    @staticmethod
    def getTableBaseAddress(switch_id, table_id):
        queryCursor.execute('SELECT base_address FROM switch_tables WHERE table_id=? AND device_id=?', (table_id,switch_id))
        row = queryCursor.fetchone()
        return row[0]

    @staticmethod
    def getTableMatchType(switch_id, table_id):
        queryCursor.execute('SELECT match_type FROM switch_tables WHERE device_id=? AND table_id=?', (switch_id,table_id))
        row = queryCursor.fetchone()
        return row[0]

    @staticmethod
    def getTableMatchFieldName(switch_id, table_id, field_id):
        queryCursor.execute('SELECT field_name FROM table_match_fields WHERE table_id=? AND device_id=? AND field_id=?', (table_id,switch_id,field_id))
        row = queryCursor.fetchone()
        return row[0]

    @staticmethod
    def getTableMatchFields(switch_id, table_id):
        queryCursor.execute('SELECT field_name, field_type, field_size FROM table_match_fields WHERE table_id=? AND device_id=?', (table_id,switch_id))
        row = queryCursor.fetchall()
        return row

    @staticmethod
    def getTableActionName(switch_id, table_id, action_id):
        queryCursor.execute('SELECT action_name FROM table_actions WHERE table_id=? AND device_id=? AND action_id=?', (table_id,switch_id,action_id))
        row = queryCursor.fetchone()
        return row[0]

    @staticmethod
    def getTableActionId(switch_id, table_id, action_name):
        queryCursor.execute('SELECT action_id FROM table_actions WHERE device_id=? AND table_id=? AND action_name=?', (switch_id,table_id,action_name))
        row = queryCursor.fetchone()
        return row[0]

    @staticmethod
    def getTableActionFields(switch_id, table_id, action_id):
        queryCursor.execute('SELECT field_name, field_type, field_size FROM table_action_fields WHERE table_id=? AND device_id=? AND action_id=?', (table_id,switch_id,action_id))
        row = queryCursor.fetchall()
        return row

    @staticmethod
    def hasTableActionName(switch_id, table_id, action_name):
        queryCursor.execute('SELECT * FROM table_actions WHERE device_id=? AND table_id=? AND action_name=?', (switch_id,table_id,action_name))
        row = queryCursor.fetchall()
        if(len(row) == 0):
            return False
        else:
            return True

    @staticmethod
    def hasTableMatchType(switch_id, table_match_type):
        queryCursor.execute('SELECT table_id FROM switch_tables WHERE device_id=? AND match_type=?', (switch_id,table_match_type))
        row = queryCursor.fetchall()
        if(len(row) == 0):
            return False
        else:
            return True

    @staticmethod
    def getAllSwitchTables():
        return queryCursor.execute('SELECT * FROM switch_tables').fetchall()
