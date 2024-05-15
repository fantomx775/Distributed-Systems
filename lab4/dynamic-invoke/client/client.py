# Copyright 2023 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter client with reflection."""

import logging
import pycurl
from google.protobuf.descriptor_pool import DescriptorPool
import grpc
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import (
    ProtoReflectionDescriptorDatabase,
)


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        reflection_db = ProtoReflectionDescriptorDatabase(channel)
        services = reflection_db.get_services()
        print(f"found services: {services}")

        desc_pool = DescriptorPool(reflection_db)
        service_desc = desc_pool.FindServiceByName("calculator.Calculator")
        print(f"found calculator service with name: {service_desc.full_name}")
        for methods in service_desc.methods:
            print(f"found method name: {methods.full_name}")
            input_type = methods.input_type
            print(f"input type for this method: {input_type.full_name}")


import json
import subprocess

grpcurl_path = r"C:\Program Files\GrpcCurl\grpcurl.exe"

def call_grpcurl(endpoint, method, input_data):
    input_json = json.dumps(input_data)

    result = subprocess.check_output([
        grpcurl_path,
        '-plaintext',
        '-d', input_json,
        endpoint,
        method
    ])

    output = json.loads(result)
    return output

def main():
    subtract_result = call_grpcurl(
        'localhost:50051',
        'calculator.Calculator/Subtract',
        {"arg1": 10, "arg2": 5}
    )
    print("Subtract Result:", subtract_result)

    add_result = call_grpcurl(
        'localhost:50051',
        'calculator.Calculator/Add',
        {"arg1": 10, "arg2": 5}
    )
    print("Add Result:", add_result)

    complex_operation_result = call_grpcurl(
        'localhost:50051',
        'calculator.Calculator/ComplexOperation',
        {"optype": 2, "args": [1.5, 2.5, -3.5]}
    )
    print("Complex Operation Result:", complex_operation_result)

    batch_operation_result = call_grpcurl(
        'localhost:50051',
        'calculator.Calculator/PerformBatchOperation',
        {"operations": [
            {"optype": 1, "args": [1, 2]},
            {"optype": 2, "args": [1.5, 2.5, -3.5]}
        ]}
    )
    print("Batch Operation Result:", batch_operation_result)



if __name__ == "__main__":
    main()
    # logging.basicConfig()
    # run()


