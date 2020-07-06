from DB_mgmt import *
from protobuffs.code_pb2 import *

class AuthDAO():
    @staticmethod
    def addUser(user_name, password):
        try:
            queryCursor.execute("INSERT INTO users (name, password) VALUES (?,?)", (user_name, password))
            dbVar.commit()
            return True
        except:
            return False

    @staticmethod
    def addPermission(user_name, switch_name):
        queryCursor.execute('SELECT * FROM switches WHERE switch_name=?', (switch_name,))
        row = queryCursor.fetchone()
        if(row is None):
            return False

        switch_id = row[0]

        queryCursor.execute('SELECT * FROM users WHERE name=?', (user_name,))
        row = queryCursor.fetchone()
        if(row is None):
            return False

        user_id = row[0]

        try:
            queryCursor.execute("INSERT INTO permissions (user_id, device_id, name) VALUES (?,?,?)", (user_id, switch_id, switch_name))
            dbVar.commit()
            return True
        except:
            return False

    @staticmethod
    def getUserPassword(user_name):
        queryCursor.execute('SELECT * FROM users WHERE name=?', (user_name,))
        row = queryCursor.fetchone()
        if(row is None):
            return None
        else:
            return row[2]

    @staticmethod
    def getUserPermissions(user_name):
        user_id = AuthDAO.getUserID(user_name)
        if(user_id == -1):
            return code_pb2.PERMISSION_DENIED

        queryCursor.execute('SELECT name FROM permissions WHERE user_id=?', (user_id,))
        row = queryCursor.fetchall()
        return row

    @staticmethod
    def getUserID(user_name):
        queryCursor.execute('SELECT * FROM users WHERE name=?', (user_name,))
        row = queryCursor.fetchone()
        if(row is None):
            return -1
        else:
            return row[0]
