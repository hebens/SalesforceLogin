from __future__ import print_function
import configparser
import grpc
import requests
import threading
import io
import pubsub_api_pb2 as pb2
import pubsub_api_pb2_grpc as pb2_grpc
import avro.schema
import avro.io
import time
import certifi
import json

import OauthLogin

semaphore = threading.Semaphore(1)
latest_replay_id = None

config = configparser.ConfigParser()
config.read("./resources/application.properties")
topic    = config["Server"]["subscribe2Topic"]
grpcHost = config["Server"]["grpcHost"]
grpcPort = config["Server"]["grpcPort"]
pubsubUrl = grpcHost + ":" + grpcPort

def fetchReqStream(topic):
    while True:
        semaphore.acquire()
        print("Semaphore acquired!")
        yield pb2.FetchRequest(
            topic_name = topic,
            replay_preset = pb2.ReplayPreset.LATEST,
            num_requested = 1)

def decode(schema, payload):
  schema = avro.schema.parse(schema)
  buf = io.BytesIO(payload)
  decoder = avro.io.BinaryDecoder(buf)
  reader = avro.io.DatumReader(schema)
  ret = reader.read(decoder)
  return ret

with open(certifi.where(), 'rb') as f:
    creds = grpc.ssl_channel_credentials(f.read())
with grpc.secure_channel(pubsubUrl, creds) as channel:
    authmetadata = OauthLogin.oAuthLogin()
    stub = pb2_grpc.PubSubStub(channel)
    substream = stub.Subscribe(fetchReqStream(topic), metadata=authmetadata)
    for event in substream:
        if event.events:
            semaphore.release()
            print("Number of events received: ", len(event.events))
            payloadbytes = event.events[0].event.payload
            schemaid = event.events[0].event.schema_id
            schema = stub.GetSchema(
                    pb2.SchemaRequest(schema_id=schemaid),
                    metadata=authmetadata).schema_json
            decoded = decode(schema, payloadbytes)
            print("Got an event!", json.dumps(decoded))
        else:
            print("[", time.strftime('%b %d, %Y %l:%M%p %Z'),"] The subscription is active.")
        latest_replay_id = event.latest_replay_id
