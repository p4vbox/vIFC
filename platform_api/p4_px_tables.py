#!/usr/bin/env python2

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

import sys, os, argparse, re, json, ast
import struct, socket

from utils.SwitchConf import *

class PXTable():

    """
    Combine P4 field values into single hex number where the bit width of each
    P4 field value is indicated in fields list
    """
    @staticmethod
    def _hexify(field_vals, fields):
        field_sizes = [size for name, size in fields if ('padding' not in name and 'hit' not in name)]
	if (len(field_vals) != len(field_sizes)):
            print >> sys.stderr, "ERROR: not enough fields provided to complete _hexify()"
            sys.exit(1)
        # convert field_vals to int
        field_vals = map(convert_to_int, field_vals)

        # combine field_vals using field sizes
        ret = 0
        for val, bits in zip(field_vals, field_sizes):
            mask = 2**bits -1
            ret = (ret << bits) + (val & mask)
        return ret


    """
    Return list of fields, each entry of form: (field_name, size_bits, lsb)
    Sorted in decending order by lsb
    """
    @staticmethod
    def extract_fields(switch_id, table_id):
        result = []
        field_list = SwitchConf.getTableMatchFields(switch_id, table_id)
        for field in field_list:
            result.append((field[0], field[2]))
        return result

    """
    Return list of fields, each entry of form: (field_name, size_bits, lsb)
    Sorted in decending order by lsb
    """
    @staticmethod
    def extract_action_fields(switch_id, table_id, action_id):
        result = []
        field_list = SwitchConf.getTableActionFields(switch_id, table_id, action_id)
        # TODO: we hardcode action_run with 2 bits. It does not seem belong to a specific action
        result.append (("action_run", 2))
        for field in field_list:
            result.append((field[0], field[2]))
        return result

    """
    Convert the action_name and action_data into a single hex value represented
    as a string
    """
    @staticmethod
    def hexify_value(switch_id, table_id, action_name, action_data):
        print "Calling hexify_value for switch_id {} tbl_id {} action {} data {}".format(switch_id, table_id, action_name, action_data)
        # action_name = '{}.{}'.format(self.block_name, action_name) if action_name != 'NoAction' else '.NoAction'
        if (not SwitchConf.hasTableActionName(switch_id, table_id, action_name)):
            print >> sys.stderr, "ERROR: {} is not a recognized action for table {}".format(action_name, table_id)
            sys.exit(1)
        action_id = SwitchConf.getTableActionId(switch_id, table_id, action_name)
        fields = PXTable.extract_action_fields(switch_id, table_id, action_id)
        field_vals = [action_id] + action_data
        print "Table action fields: {}, supplied values: {}".format(fields, field_vals)
        return PXTable._hexify(field_vals, fields)

    """
    Convert list of ints representing the keys to match on into a single hex value
    represented as a string
    """
    @staticmethod
    def hexify_key(switch_id, table_id, key_list):
        print "Calling hexify_key for switch_id {} tbl_id {} key_list {}".format(switch_id, table_id, key_list)
        fields = PXTable.extract_fields(switch_id, table_id)
        field_vals = key_list
        print "Table match fields: {}, supplied values: {}".format(fields, field_vals)
        return PXTable._hexify(field_vals, fields)

    """
    Convert mask_list into single hex value represented as a string
    """
    @staticmethod
    def hexify_mask(switch_id, table_id, mask_list):
        fields = PXTable.extract_fields(switch_id, table_id)
        field_vals = mask_list
        return PXTable._hexify(field_vals, fields)


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def mac2int(addr):
    return int(addr.translate(None, ":"), 16)

def convert_to_int(val):
    if type(val) == str:
        mac_fmat = r'([\dA-Fa-f]{2}:){5}[\dA-Fa-f]{2}'
        ip_fmat = r'([0-9]{1,3}\.){3}[0-9]{1,3}'
        if re.match(mac_fmat, val):
            return mac2int(val)
        elif re.match(ip_fmat, val):
            return ip2int(val)
        else:
            try:
                return int(val, 0)
            except ValueError as e:
                print >> sys.stderr, "ERROR: failed to convert {} of type {} to an integer".format(val, type(val))
                sys.exit(1)
    elif type(val) == int:
        return val
    else:
        print >> sys.stderr, "ERROR: failed to convert {} of type {} to an integer".format(val, type(val))
        sys.exit(1)
