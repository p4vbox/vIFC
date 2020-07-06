#!/usr/bin/env python

#
# Copyright (c) 2015 University of Cambridge
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

from NFTest import *
import sys, os, re, json
from fcntl import *
from ctypes import *
from collections import OrderedDict

libsume = 0
p4_externs_dict = {}

ERROR_CODE = -1

def get_address(switch_id, reg_name, index):
    if reg_name not in p4_externs_dict[switch_id].keys() and 'control_width' not in p4_externs_dict[reg_name].keys() and p4_externs_dict[reg_name]['control_width'] > 0:
        print >> sys.stderr, "ERROR: {0} is not a recognized register name".format(reg_name)
        return ERROR_CODE
    addressable_depth = 2**p4_externs_dict[reg_name]['control_width']
    if index >=  addressable_depth or index < 0:
        print >> sys.stderr, "ERROR: cannot access {0}[{1}], index out of bounds".format(reg_name, index)
        return ERROR_CODE
    return p4_externs_dict[reg_name]['base_addr'] + index

#####################
### API Functions ###
#####################

def reg_read(switch_id, reg_name, index):
    if (switch_id not in p4_externs_dict):
        print ("reg_read: switch id {} not found in p4_externs_dict")
        return ERROR_CODE

    address = get_address(switch_id, reg_name, index)
    if address == ERROR_CODE:
        return ERROR_CODE
#    print "reading address : {0}".format(hex(address))
    return libsume.regread(address)

def reg_write(reg_name, index, val):
    if (switch_id not in p4_externs_dict):
        print ("reg_write: switch id {} not found in p4_externs_dict")
        return ERROR_CODE

    address = get_address(reg_name, index)
    if address == ERROR_CODE:
        return ERROR_CODE
#    print "writing address : {0}".format(hex(address))
    return libsume.regwrite(address, val)
