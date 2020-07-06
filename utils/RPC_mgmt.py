from concurrent import futures
import logging

import grpc

import json, os, re, ast, sys

from platform_api import p4_tables_api as p4_tables_api
from platform_api import p4_px_tables as p4_px_tables

from protobuffs import p4runtime_pb2 as p4runtime_pb2
from protobuffs import p4runtime_pb2_grpc as p4runtime_pb2_grpc

from protobuffs import auth_pb2 as auth_pb2
from protobuffs import code_pb2 as code_pb2

from SwitchConf import *
from Auth import *
from model.DB_mgmt import *
from Context import *

class RPC_mgmt():

    user_name_permissions = None

    @staticmethod
    def MasterArbitration(self, request, context):
        rep = p4runtime_pb2.StreamMessageResponse()
        rep.arbitration.CopyFrom(req.arbitration)
        rep.arbitration.status.code = code_pb2.OK
        yield rep

    @staticmethod
    def process_streamChannel(self, request_iterator, context):
        print "Method process_streamChannel called from client..."
        response = request_iterator
        for i in response:
            value = auth_pb2.Auth.FromString(i.other.value)
            if Auth.authenticate(value.user_name, value.passwd):
                print("User " + value.user_name + " authenticated!")
                global user_name_permissions
                user_name_permissions = value.user_name
                if i.HasField('arbitration'):
                    #arbitration update
                    return RPC_mgmt.MasterArbitration(response, context)
                elif i.HasField('packet'):
                    return RPC_mgmt.packetOut(response, context)
                else:
                    return response
            else:
                return RPC_mgmt.authStreamChannel()

    @staticmethod
    def packet_out_msg(self,pl,meta):
        return p4runtime_pb2.PacketOut(payload=pl,metadata=meta)

    @staticmethod
    def packetOut(self, request, context):
        request = p4runtime_pb2.StreamMessageRequest()
        request.packet.CopyFrom(packet)
        yield request

    @staticmethod
    def PacketIn(self, request, context):
        if request is None:
            print("packet not received")
            yield request

    @staticmethod
    def authStreamChannel():
        msg = p4runtime_pb2.StreamError()
        msg.canonical_code = code_pb2.PERMISSION_DENIED
        msg.message = "Auth error"
        yield msg

    @staticmethod
    def process_getPipe(request, context):
        return code_pb2.UNIMPLEMENTED

    @staticmethod
    def process_setPipe(request, context):
        print "Method process_setPipe called from client..."
        id_switch = request.device_id
        switch_name = SwitchConf.getSwitchName(id_switch)
        if (switch_name is False):
            print "Switch id {} does not exist".format(id_switch)
            return code_pb2.NOT_FOUND

        if Auth.hasPermission(user_name_permissions, switch_name):
            print "User {} has setPipe permission to switch {}".format(user_name_permissions,switch_name)
        else:
            print "User {} DOES NOT HAVE setPipe permission to switch {}".format(user_name_permissions,switch_name)
            return code_pb2.PERMISSION_DENIED
        response = request
        response.device_id = request.device_id
        response.role_id = request.role_id
        p4info = None
        p4_device_config = None
        config = p4runtime_pb2.ForwardingPipelineConfig()
        if p4info:
            config.p4info.CopyFrom(p4info)
        if p4_device_config:
            config.p4_device_config = p4_device_config.SerializeToString()
        response.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
        return p4runtime_pb2.SetForwardingPipelineConfigResponse()

    @staticmethod
    def process_write_request(self, request, context):
        print "Method process_write_request called from client..."
        response = request
        id_switch = request.device_id
        switch_name = SwitchConf.getSwitchName(id_switch)
        if (switch_name is False):
            print "Switch id {} does not exist".format(id_switch)
            return code_pb2.NOT_FOUND

        if Auth.hasPermission(user_name_permissions, switch_name):
            print "User {} has write_request permission to switch {}".format(user_name_permissions,switch_name)
        else:
            print "User {} DOES NOT HAVE write_request permission to switch {}".format(user_name_permissions,switch_name)
            return code_pb2.PERMISSION_DENIED

        for request_update in request.updates:
            #Get table name with ID from P4Runtime to check with ID of Switch
            try:
                table_nameswitch = SwitchConf.getTableName(id_switch, request_update.entity.table_entry.table_id)
            except TypeError:
                print "Error: Table with ID {} not found.".format(request_update.entity.table_entry.action.action.table_id)
                return response

            try:
                action_name = SwitchConf.getTableActionName(id_switch, request_update.entity.table_entry.table_id,
                                                             request_update.entity.table_entry.action.action.action_id)
            except TypeError:
                print "Error: Action with ID {} not found.".format(request_update.entity.table_entry.action.action.action_id)
                return response

            action_test = request_update.entity.table_entry.action.action.params
            action_key = action_test[0].value

            if request_update.type == p4runtime_pb2.Update.INSERT:
                print "Processing INSERT request..."
                matches = request_update.entity.table_entry.match[0]
                if matches.HasField("exact"):
                    matches_key = request_update.entity.table_entry.match[0].exact.value
                    matches_key = re.sub('matches_key', '[matches_key]', matches_key)
                    matches_key = matches_key.split()
                    matches_key = ast.literal_eval(json.dumps(matches_key))
                    action_key = action_key.split()
                    action_key = ast.literal_eval(json.dumps(action_key)) 
                    p4_tables_api.table_cam_add_entry(id_switch, table_nameswitch, matches_key, action_name, action_key)

                elif matches.HasField("ternary"):
                    keys = matches.ternary.value
                    masks = matches.ternary.mask
                    address = SwitchConf.getTableBaseAddress(id_switch, request_update.entity.table_entry.table_id)
                    p4_tables_api.table_tcam_add_entry(switch_id, table_nameswitch, address, action_name, keys, masks, action_key)
                #elif matches.HasField("lpm"):

            elif request_update.type == p4runtime_pb2.Update.MODIFY:
                print "Processing MODIFY request..."
                #First: Read the entry provided by the client to see its existance in the switch
                # TODO: hardcoded yet, need to remove dependence on switch specific p4_tables_api
                matches = request_update.entity.table_entry.match[0]
                if matches.HasField("exact"):
                    matches_key = request_update.entity.table_entry.match[0].exact.value
                    matches_key = re.sub('matches_key', '[matches_key]', matches_key)
                    matches_key = matches_key.split()
                    matches_key = ast.literal_eval(json.dumps(matches_key))
                    action_key = action_key.split()
                    action_key = ast.literal_eval(json.dumps(action_key))
                    # key = map(p4_px_tables.convert_to_int, matches_key)
                    (found, val) = p4_tables_api.table_cam_read_entry(id_switch, table_nameswitch, matches_key)
                    print "Entry found: {}".format (found)
                    if found != "False":
                        # p4_tables_api.table_cam_delete_entry(id_switch, table_nameswitch, matches_key)
                        # Second: Modify the existing entry with the values stored in the variables
                        print("Match key: {} exists in table {} of switch {}: found {}, val {}. Updating...".
                                format(matches_key,table_nameswitch,switch_name,found,val))
                        p4_tables_api.table_cam_add_entry(id_switch, table_nameswitch, matches_key, action_name, action_key)
                    else:
                        print("Error: Match key {} not found in table {} of switch {}".
                               format(matches_key,table_nameswitch,switch_name))
                        response = p4runtime_pb2.Error()
                        response.canonical_code = code_pb2.NOT_FOUND
                        return response

                # elif matches.HasField("ternary"):

                # elif matches.HasField("lpm"):

            elif request_update.type == p4runtime_pb2.Update.DELETE:
                print "Processing DELETE request..."
                #First: Use read entry which will check the existance, then delete it
                matches = request_update.entity.table_entry.match[0]
                if matches.HasField("exact"):
                    matches_key = request_update.entity.table_entry.match[0].exact.value
                    matches_key = re.sub('matches_key', '[matches_key]', matches_key)
                    matches_key = matches_key.split()
                    matches_key = ast.literal_eval(json.dumps(matches_key))
                    action_key = action_key.split()
                    action_key = ast.literal_eval(json.dumps(action_key))
                    # key = map(p4_px_tables.convert_to_int, matches_key)
                    (found, val) = p4_tables_api.table_cam_read_entry(id_switch, table_nameswitch, matches_key)
                    print "Entry found: {}".format (found)
                    if found != "False":
                        print("Match key: {} exists in table {} of switch {}: found {}, val {}. Deleting...".
                                format(matches_key,table_nameswitch,switch_name,found,val))
                        p4_tables_api.table_cam_delete_entry(id_switch, table_nameswitch, matches_key)
                    else:
                        print("Error: Match key {} not found in table {} of switch {}".
                                format(matches_key,table_nameswitch,switch_name))

                # elif matches.HasField("ternary"):

                # elif matches.HasField("lpm"):

            else:
                print("Error in update code: {}. Please inform a valid update type (INSERT, MODIFY or DELETE)".format(update[0].type))
        return response

    @staticmethod
    def process_read_request(request, context):
        print "Method process_read_request called from client..."
        # Checking every entity that came within the request.
        id_switch = request.device_id
        switch_name = SwitchConf.getSwitchName(id_switch)
        if (switch_name is False):
            print "Switch id {} does not exist".format(id_switch)
            # TODO: fix this to send correct error code to user: code_pb2.NOT_FOUND
            response = p4runtime_pb2.Error()
            response.canonical_code = code_pb2.NOT_FOUND
            yield response
            return

        if Auth.hasPermission(user_name_permissions, switch_name):
            print "User {} has read_request permission to switch {}".format(user_name_permissions,switch_name)
        else:
            print "User {} DOES NOT HAVE read_request permission to switch {}".format(user_name_permissions,switch_name)
            response = p4runtime_pb2.Error()
            response.canonical_code = code_pb2.PERMISSION_DENIED
            yield response
            return

        switch_id = request.device_id
        for requested_entity in request.entities:

            # Getting the table name stored in the database.
            requested_table_id = requested_entity.table_entry.table_id
            try:
                table_nameswitch = SwitchConf.getTableName(id_switch, requested_table_id)
            except TypeError:
                print "Table with ID {} not found.".format(requested_table_id)
                response = p4runtime_pb2.Error()
                response.canonical_code = code_pb2.NOT_FOUND
                yield response

            # Checking the table type.
            requested_match = requested_entity.table_entry.match[0]

            if requested_match.HasField("exact"):
                matches_key = requested_entity.table_entry.match[0].exact.value
                matches_key = re.sub('matches_key', '[matches_key]', matches_key)
                matches_key = matches_key.split()
                matches_key = ast.literal_eval(json.dumps(matches_key))
                (found, val) = p4_tables_api.table_cam_read_entry(switch_id, table_nameswitch, matches_key)
                print "Entry found: {}".format (found)
                if found == "False":
                    print("Error: Match key {} not found in table {} of switch {}".format(matches_key,table_nameswitch,switch_name))
                    yield p4runtime_pb2.ReadResponse()
                    return

                print("Match key: {} exists in table {} of switch {}: found {}, val {}".format(matches_key,table_nameswitch,switch_name,found,val))
                # Creating and filling the response.
                response = p4runtime_pb2.ReadResponse()

                response.entities.add()
                response.entities[0].table_entry.table_id = requested_table_id

                response.entities[0].table_entry.match.add()
                response.entities[0].table_entry.match[0].field_id = requested_match.field_id
                response.entities[0].table_entry.match[0].exact.value = requested_match.exact.value

            # TODO: ternary read.
            elif requested_match.HasField("ternary"):
                response = p4runtime_pb2.ReadResponse()

            # TODO: longest prefix match read.
            elif requested_match.HasField("lpm"):
                response = p4runtime_pb2.ReadResponse()

            else:
                print "Unsupported table type."
                yield p4runtime_pb2.ReadResponse()

            yield response
