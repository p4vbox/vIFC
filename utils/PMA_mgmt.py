import json, os, re, ast, sys
import unicodedata
from fcntl import *
from ctypes import *

from platform_api import p4_tables_api as p4_tables_api

from SwitchConf import *
from Auth import *
from model.DB_mgmt import *

class PMA_mgmt():
    @staticmethod
    def init_database():
        return DB_mgmt.initDB()

    @staticmethod
    def load_switch_data(switch_name, dir_path, switch_id, switch_dat_file, table_defines_file):
        print "Running load_switch_data for switch {}".format(switch_name)

        if (not SwitchConf.addSwitch(switch_id, switch_name, dir_path)):
            print "Error adding switch {}. Fail".format(switch_name)
            return False

        with open(switch_dat_file) as dat_file:
            switch_info = json.load(dat_file)

        with open(table_defines_file) as json_file:
            table_defines_info = json.load(json_file)

        for block, block_dict in switch_info.items():
            # For SimpleSumeSwitch, block name is TopPipe
            if 'px_lookups' in block_dict.keys():
                for table_dict in block_dict['px_lookups']:
                    table_name = table_dict['p4_name']
                    table_type = table_dict['match_type']
                    table_base_address = int(table_defines_info[table_type][table_name]['base_address'], 16)
                    table_id = int(table_defines_info[table_type][table_name]['tableID'])
                    print "Adding table for switch {}: {}({}), type: {}".format(switch_name,table_name,table_id,table_type)
                    SwitchConf.addTable(switch_id, table_id, table_name, table_type, table_base_address)

                    field_id = 1 #TODO: Auto-generated field ID?
                    for field in table_dict['request_fields']:
                        if ('padding' in field['px_name'] or 'hit' in field['px_name']):
                            # We are skipping these just like the P4-NetFPGA CLI does
                            continue
                        print "Processing from dat_file field {}".format(field)
                        # lookup_request_padding might generate a problem here, check it further!
                        if ('p4_name' in field):
                            field_name = field['px_name']
                            field_type = field['type']
                            field_size = field['size']
                            print "Adding match field for {}({}), name: {}, type: {}, size: {}".format(table_name,table_id,field_name,field_type,field_size)
                            SwitchConf.addTableMatchField(switch_id, table_id, field_id, field_name, field_type, field_size)
                            field_id = field_id + 1

                    for action_name in table_dict['action_ids']:
                        action_id =  table_dict['action_ids'][action_name]
                        print "Adding action for {}({}), name: {}, id {}".format(table_name,table_id,action_name,action_id)
                        SwitchConf.addTableAction(switch_id, table_id, action_id, action_name)

                    field_id = 1 #TODO: Auto-generated field ID?
                    for field in table_dict['response_fields']:
                        if ('padding' in field['px_name'] or 'hit' in field['px_name']):
                            continue
                        print "Processing from dat_file field {}".format(field)
                        # TODO: during _hexify we hardcode action_run, see p4_px_tables
                        if (field['type'] == 'struct'):
                            action_name = field['p4_action']
                            field_type = field['type']
                            action_id = SwitchConf.getTableActionId(switch_id, table_id, action_name)
                            for f in field['fields']:
                                field_name = f['px_name']
                                field_type = f['type']
                                field_size = f['size']
                                print "Adding action field for {}({}), name: {}, type: {}, size: {}".format(action_name, action_id, field_name, field_type, field_size)
                                SwitchConf.addTableActionField(switch_id, table_id, action_id, field_id, field_name, field_type, field_size)
                                field_id = field_id + 1

    @staticmethod
    def load_switch_modules(switch_name, dir_path, switch_id):
        print "Running load_switch_modules for switch {}".format(switch_name)
        if (SwitchConf.hasTableMatchType(switch_id, "EM")):
            print "Loading libcam for switch {} ({})".format(switch_name, dir_path + '/libcam.so')
            p4_tables_api.libcam_dict[switch_id]=cdll.LoadLibrary(dir_path + '/libcam.so')
            # argtypes for the functions called from  C
            p4_tables_api.libcam_dict[switch_id].cam_read_entry.argtypes = [c_uint, c_char_p, c_char_p, c_char_p]
            p4_tables_api.libcam_dict[switch_id].cam_add_entry.argtypes = [c_uint, c_char_p, c_char_p]
            p4_tables_api.libcam_dict[switch_id].cam_delete_entry.argtypes = [c_uint, c_char_p]
            p4_tables_api.libcam_dict[switch_id].cam_error_decode.argtypes = [c_int]
            p4_tables_api.libcam_dict[switch_id].cam_error_decode.restype = c_char_p
            p4_tables_api.libcam_dict[switch_id].cam_get_size.argtypes = [c_uint]
            p4_tables_api.libcam_dict[switch_id].cam_get_size.restype = c_uint

        if (SwitchConf.hasTableMatchType(switch_id, "TCAM")):
            print "Loading libtcam for switch {} ({})".format(switch_name, dir_path + '/libtcam.so')
            p4_tables_api.libtcam_dict[switch_id] = cdll.LoadLibrary(dir_path + '/libtcam.so')
            # argtypes for the functions called from  C
            p4_tables_api.libtcam_dict[switch_id].tcam_clean.argtypes = [c_uint]
            p4_tables_api.libtcam_dict[switch_id].tcam_get_addr_size.argtypes = []
            p4_tables_api.libtcam_dict[switch_id].tcam_set_log_level.argtypes = [c_uint, c_uint]
            p4_tables_api.libtcam_dict[switch_id].tcam_write_entry.argtypes = [c_uint, c_uint, c_char_p, c_char_p, c_char_p]
            p4_tables_api.libtcam_dict[switch_id].tcam_erase_entry.argtypes = [c_uint, c_uint]
            p4_tables_api.libtcam_dict[switch_id].tcam_verify_entry.argtypes = [c_uint, c_uint, c_char_p, c_char_p, c_char_p]
            p4_tables_api.libtcam_dict[switch_id].tcam_verify_entry.restype = c_uint
            p4_tables_api.libtcam_dict[switch_id].tcam_error_decode.argtypes = [c_int]
            p4_tables_api.libtcam_dict[switch_id].tcam_error_decode.restype = c_char_p

        if (SwitchConf.hasTableMatchType(switch_id, "LPM")):
            print "Loading liblpm for switch {} ({})".format(switch_name, dir_path + '/liblpm.so')
            p4_tables_api.liblpm_dict[switch_id] = cdll.LoadLibrary(dir_path + '/liblpm.so')
            # argtypes for the functions called from  C
            p4_tables_api.liblpm_dict[switch_id].lpm_get_addr_size.argtypes = []
            p4_tables_api.liblpm_dict[switch_id].lpm_set_log_level.argtypes = [c_uint, c_uint]
            p4_tables_api.liblpm_dict[switch_id].lpm_load_dataset.argtypes = [c_uint, c_char_p]
            p4_tables_api.liblpm_dict[switch_id].lpm_verify_dataset.argtypes = [c_uint, c_char_p]
            p4_tables_api.liblpm_dict[switch_id].lpm_set_active_lookup_bank.argtypes = [c_uint, c_uint]
            p4_tables_api.liblpm_dict[switch_id].lpm_error_decode.argtypes = [c_int]
            p4_tables_api.liblpm_dict[switch_id].lpm_error_decode.restype = c_char_p

        return True

    """
    Read the SimpleSumeSwitch_reg_defines.txt file
    """
    @staticmethod
    def load_reg_data(switch_id, extern_defines_file):
        print "Running load_switch_data for switch id {}".format(switch_id)

        switch_name = SwitchConf.getSwitchName(switch_id)
        if (switch_name is False):
            print "Error loading registers for switch id {}: not found".format(switch_id)
            return False

        with open(extern_defines_file) as f:
            p4_externs[switch_id] = json.load(f)

    @staticmethod
    def load_libsume_module(lib_path):
        print "Running load_libsume_module ({})...".format(lib_path)
        p4_regs_api.libsume=cdll.LoadLibrary(lib_path)

        # argtypes for the functions called from  C
        p4_regs_api.libsume.regread.argtypes = [c_uint]
        p4_regs_api.libsume.regwrite.argtypes= [c_uint, c_uint]
