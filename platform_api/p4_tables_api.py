#!/usr/bin/env python

#
# Copyright (c) 2017 Stephen Ibanez
# All rights reserved.
#
# This software was developed by Stanford University and the University of Cambridge Computer Laboratory
# under National Science Foundation under Grant No. CNS-0855268,
# the University of Cambridge Computer Laboratory under EPSRC INTERNET Project EP/H040536/1 and
# by the University of Cambridge Computer Laboratory under DARPA/AFRL contract FA8750-11-C-0249 ("MRC2"),
# as part of the DARPA MRC research programme.
#
# @NETFPGA_LICENSE_HEADER_START@
#
# Licensed to NetFPGA C.I.C. (NetFPGA) under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  NetFPGA licenses this
# file to you under the NetFPGA Hardware-Software License, Version 1.0 (the
# "License"); you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at:
#
#   http://www.netfpga-cic.org
#
# Unless required by applicable law or agreed to in writing, Work distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations under the License.
#
# @NETFPGA_LICENSE_HEADER_END@
#

# This code was modified for use in PvS: Programmable Virtual Switches
# Copyright (c) 2020 <authors>
# All rights reserved.

import sys, os, re, json
from fcntl import *
from ctypes import *
from utils.SwitchConf import *

from p4_px_tables import *

# These global variables hold pointers to the modules that actually handle
# virtual switches through the PICe interface
libcam_dict = {}
libtcam_dict = {}
liblpm_dict = {}

########################
### Helper Functions ###
########################

"""
Check if table_name is a valid CAM table
"""
def check_valid_cam_table_name(switch_id, table_id):
    if (SwitchConf.getTableMatchType(switch_id, table_id) != 'EM'):
        print >> sys.stderr, "ERROR: {0} is not a recognized CAM table name".format(table_name)
        return False
    return True

"""
Check if table_name is a valid TCAM table
"""
def check_valid_tcam_table_name(switch_id, table_id):
    if (SwitchConf.getTableMatchType(switch_id, table_id) != 'TCAM'):
        print >> sys.stderr, "ERROR: {0} is not a recognized TCAM table name".format(table_name)
        return False
    return True

"""
Check if table_name is a valid LPM table
"""
def check_valid_lpm_table_name(switch_id, table_id):
    if (SwitchConf.getTableMatchType(switch_id, table_id) != 'LPM'):
        print >> sys.stderr, "ERROR: {0} is not a recognized LPM table name".format(table_name)
        return False
    return True

#########################
### CAM API Functions ###
#########################

def table_cam_read_entry(switch_id, table_name, keys):
    print "Processing table_cam_read_entry: switch_id {}, table {}, keys {}".format(switch_id, table_name, keys)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_cam_table_name(switch_id, table_id):
        return "NA", "NA"

    key = PXTable.hexify_key(switch_id, table_id, keys)
    hex_key_buf = create_string_buffer("{:X}".format(key))
    value = create_string_buffer(1024) # TODO: Fix this ... Must be large enough to hold entire value
    found = create_string_buffer(10)  # Should only need to hold "True" or "False"
    print "table_cam_read_entry: table_id {}, key_hex_buf {}".format (table_id, hex_key_buf)
    rc = libcam_dict[switch_id].cam_read_entry(table_id, hex_key_buf, value, found)
    print libcam_dict[switch_id].cam_error_decode(rc)
    return found.value, value.value

def table_cam_add_entry(switch_id, table_name, keys, action_name, action_data):
    print ("Processing table_cam_add_entry: switch_id {}, table {}, keys {}, action_name {}, action_data {}".
             format(switch_id, table_name, keys,action_name, action_data))
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_cam_table_name(switch_id, table_id):
        return
    key = PXTable.hexify_key(switch_id, table_id, keys)
    value = PXTable.hexify_value(switch_id, table_id, action_name, action_data)
    print "table_cam_add_entry: table_id {}, key {:X}, value {:X}".format (table_id, key, value)
    rc = libcam_dict[switch_id].cam_add_entry(table_id, "{:X}".format(key), "{:X}".format(value))
    print libcam_dict[switch_id].cam_error_decode(rc)

def table_cam_delete_entry(switch_id, table_name, keys):
    print "Processing table_cam_delete_entry: switch_id {}, table {}, keys {}".format(switch_id, table_name, keys)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_cam_table_name(switch_id, table_id):
        return

    key = PXTable.hexify_key(switch_id, table_id, keys)
    print "table_cam_delete_entry: table_id {}, key {:X}".format (table_id, key)
    rc = libcam_dict[switch_id].cam_delete_entry(table_id, "{:X}".format(key))
    print libcam_dict[switch_id].cam_error_decode(rc)

def table_cam_get_size(switch_id, table_name):
    print "Processing table_cam_get_size for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_cam_table_name(switch_id, table_id):
        return 0

    return libcam_dict[switch_id].cam_get_size(table_id)


##########################
### TCAM API Functions ###
##########################

def table_tcam_clean(switch_id, table_name):
    print "Processing table_tcam_clean for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_tcam_table_name(switch_id, table_id):
        return

    rc = libtcam_dict[switch_id].tcam_clean(table_id)
    print libtcam_dict[switch_id].tcam_error_decode(rc)

def table_tcam_get_addr_size(switch_id):
    print "Processing table_tcam_get_addr_size for switch id {}".format(switch_id)

    return libtcam_dict[switch_id].tcam_get_addr_size()

def table_tcam_set_log_level(switch_id, table_name, msg_level):
    print "Processing table_tcam_set_log_level for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.gettable_id(switch_id, table_name)

    if not check_valid_tcam_table_name(switch_id, table_id):
        return

    rc = libtcam_dict[switch_id].tcam_set_log_level(table_id, msg_level)
    print libtcam_dict[switch_id].tcam_error_decode(rc)

def table_tcam_write_entry(switch_id, table_name, addr, keys, masks, action_name, action_data):
    print "Processing table_tcam_write_entry for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_tcam_table_name(switch_id, table_id):
        return

    mask = PXTable.hexify_mask(switch_id, table_id, masks)
    key = PXTable.hexify_key(switch_id, table_id, keys)
    value = PXTable.hexify_value(switch_id, table_id, action_name, action_data)
    rc = libtcam_dict[switch_id].tcam_write_entry(table_id, addr, "{:X}".format(key), "{:X}".format(mask), "{:X}".format(value))
    print libtcam_dict[switch_id].tcam_error_decode(rc)

def table_tcam_erase_entry(switch_id, table_name, addr):
    print "Processing table_tcam_erase_entry for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_tcam_table_name(switch_id, table_id):
        return

    rc = libtcam_dict[switch_id].tcam_erase_entry(table_id, addr)
    print libtcam_dict[switch_id].tcam_error_decode(rc)


def table_tcam_verify_entry(switch_id, table_name, addr, keys, masks, action_name, action_data):
    print "Processing table_tcam_verify_entry for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_tcam_table_name(switch_id, table_id):
        return

    mask = PXTable.hexify_mask(switch_id, table_id, masks)
    key = PXTable.hexify_key(switch_id, table_id, keys)
    value = PXTable.hexify_value(switch_id, table_id, action_name, action_data)
    return libtcam_dict[switch_id].tcam_verify_entry(table_id, addr, "{:X}".format(key), "{:X}".format(mask), "{:X}".format(value))

def table_tcam_error_decode(error):

    return libtcam_dict[switch_id].tcam_error_decode(error)


#########################
### LPM API Functions ###
#########################

def table_lpm_get_addr_size(switch_id):
    print "Processing table_lpm_get_addr_size for switch id {}".format(switch_id)

    return liblpm_dict[switch_id].lpm_get_addr_size()

def table_lpm_set_log_level(switch_id, table_name):
    print "Processing table_lpm_set_log_level for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_lpm_table_name(switch_id, table_id):
        return

    rc = liblpm_dict[switch_id].lpm_set_log_level(table_id, msg_level)
    print liblpm_dict[switch_id].lpm_error_decode(rc)

def table_lpm_load_dataset(switch_id, table_name, filename):
    print "Processing table_lpm_load_dataset for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_lpm_table_name(switch_id, table_id):
        return

    rc = liblpm_dict[switch_id].lpm_load_dataset(table_id, filename)
    print liblpm_dict[switch_id].lpm_error_decode(rc)

def table_lpm_verify_dataset(switch_id, table_name, filename):
    print "Processing table_lpm_verify_dataset for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_lpm_table_name(switch_id, table_id):
        return

    return liblpm_dict[switch_id].lpm_verify_dataset(table_id, filename)

def table_lpm_set_active_lookup_bank(switch_id, table_name, bank):
    print "Processing table_lpm_set_active_lookup_bank for switch id {} and table name {}".format(switch_id, table_name)
    table_id = SwitchConf.getTableId(switch_id, table_name)

    if not check_valid_lpm_table_name(switch_id, table_id):
        return

    rc = liblpm_dict[switch_id].lpm_set_active_lookup_bank(table_id, bank)
    print liblpm_dict[switch_id].lpm_error_decode(rc)

def table_lpm_error_decode(error):

    return liblpm_dict[switch_id].lpm_error_decode(error)
