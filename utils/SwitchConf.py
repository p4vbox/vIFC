from model.SwitchConfDAO import *

class SwitchConf():
    @staticmethod
    def addSwitch(switch_id, switch_name, dir_path):
        return SwitchConfDAO.addSwitch(switch_id, switch_name, dir_path)

    @staticmethod
    def addTable(switch_id, table_id, table_name, match_type, table_base_address):
        return SwitchConfDAO.addTable(switch_id, table_id, table_name, match_type, table_base_address)

    @staticmethod
    def addTableMatchField(switch_id, table_id, field_id, field_name, field_type, field_size):
        return SwitchConfDAO.addTableMatchField(switch_id, table_id, field_id, field_name, field_type, field_size)

    @staticmethod
    def addTableAction(switch_id, table_id, action_id, action_name):
        return SwitchConfDAO.addTableAction(switch_id, table_id, action_id, action_name)

    @staticmethod
    def addTableActionField(switch_id, table_id, action_id, field_id, field_name, field_type, field_size):
        return SwitchConfDAO.addTableActionField(switch_id, table_id, action_id, field_id, field_name, field_type, field_size)

    @staticmethod
    def getSwitchName(switch_id):
        return SwitchConfDAO.getSwitchName(switch_id)

    @staticmethod
    def getSwitchPath(switch_id):
        return SwitchConfDAO.getSwitchPath(switch_id)

    @staticmethod
    def getTableId(switch_id, table_name):
        return SwitchConfDAO.getTableId(switch_id, table_name)

    @staticmethod
    def getTableName(switch_id, table_id):
        return SwitchConfDAO.getTableName(switch_id, table_id)

    @staticmethod
    def getTableBaseAddress(switch_id, table_id):
        return SwitchConfDAO.getTableBaseAddress(switch_id, table_id)

    @staticmethod
    def getTableMatchType(switch_id, table_id):
        return SwitchConfDAO.getTableMatchType(switch_id, table_id)

    @staticmethod
    def getTableMatchFields(switch_id, table_id):
        return SwitchConfDAO.getTableMatchFields(switch_id, table_id)

    @staticmethod
    def getTableMatchFieldName(switch_id, table_id, field_id):
        return SwitchConfDAO.getTableMatchFieldName(switch_id, table_id, field_id)

    @staticmethod
    def getTableActionName(switch_id, table_id, action_id):
        return SwitchConfDAO.getTableActionName(switch_id, table_id, action_id)

    @staticmethod
    def getTableActionId(switch_id, table_id, action_name):
        return SwitchConfDAO.getTableActionId(switch_id, table_id, action_name)

    @staticmethod
    def getTableActionFields(switch_id, table_id, action_id):
        return SwitchConfDAO.getTableActionFields(switch_id, table_id, action_id)

    @staticmethod
    def hasTableActionName(switch_id, table_id, action_name):
        return SwitchConfDAO.hasTableActionName(switch_id, table_id, action_name)

    @staticmethod
    def hasTableMatchType(switch_id, table_match_type):
        return SwitchConfDAO.hasTableMatchType(switch_id, table_match_type)

    @staticmethod
    def getAllSwitchTables():
        return SwitchConfDAO.getAllSwitchTables()

