from model.AuthDAO import *

class Auth():
    @staticmethod
    def authenticate(user_name, password):
        uPassword = AuthDAO.getUserPassword(user_name)
        if (uPassword is not None and uPassword == password):
            return True
        else:
            return False

    @staticmethod
    def addUser(user_name, password):
        AuthDAO.addUser(user_name, password)

    @staticmethod
    def addPermission(user_name, switch_name):
        AuthDAO.addPermission(user_name, switch_name)

    @staticmethod
    def hasPermission(user_name, switch_name):
        for permission_switch_name in AuthDAO.getUserPermissions(user_name):
            if (permission_switch_name[0] == switch_name):
                return True
        return False
