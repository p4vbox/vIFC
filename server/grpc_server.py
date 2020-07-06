from concurrent import futures
import logging

import grpc

import json, os, re, ast
import unicodedata

import sys

from protobuffs import p4runtime_pb2 as p4runtime_pb2
from protobuffs import p4runtime_pb2_grpc as p4runtime_pb2_grpc

from protobuffs.code_pb2 import *
from protobuffs.auth_pb2 import *

from utils.RPC_mgmt import *

class P4Runtime(p4runtime_pb2_grpc.P4RuntimeServicer):

    def __init__(self):
        self.host = 'localhost'
        self.server_port = 50051
        self.device_id = 0
        with open('utils/tls_certificates/server.crt', 'rb') as f:
            trusted_certs = f.read()

        self.credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
        self.channel = grpc.secure_channel('{}:{}'.format(self.host, self.server_port), self.credentials)
        self.stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)

    def SetForwardingPipelineConfig(self, request, context):
        return RPC_mgmt.process_setPipe(request, context)

    def GetForwardingPipelineConfig(self, request, context):
        return RPC_mgmt.process_getPipe(request, context)

    def StreamChannel(self, request_iterator, context):
        return RPC_mgmt.process_streamChannel(self, request_iterator, context)

    def Write(self, request, context):
        return RPC_mgmt.process_write_request(self, request, context)

    def Read(self, request, context):
        return RPC_mgmt.process_read_request(request, context)


if __name__ == '__main__':

    logging.basicConfig()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p4runtime_instance = P4Runtime()
    p4runtime_pb2_grpc.add_P4RuntimeServicer_to_server(p4runtime_instance,server)
    with open('utils/tls_certificates/server.key', 'rb') as f:
        private_key = f.read()
    with open('utils/tls_certificates/server.crt', 'rb') as f:
        certificate_chain = f.read()
    server_credentials = grpc.ssl_server_credentials(
      ((private_key, certificate_chain,),))
    server.add_secure_port('[::]:50051', server_credentials)
    server.start()
    print('PvS P4Runtime server running @ {}:{}'.format(p4runtime_instance.host, p4runtime_instance.server_port))
    server.wait_for_termination()
