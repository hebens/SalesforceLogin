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
config.read("../resources/application.properties")
topic    = config["Server"]["subscribe2Topic"]
grpcHost = config["Server"]["grpcHost"]
grpcPort = config["Server"]["grpcPort"]
pubsubUrl = grpcHost + ":" + grpcPort

def sf_api_call(access_token, instance_url, action, parameters = {}, method = 'get', data = {}):
    """
    Helper function to make calls to Salesforce REST API.
    Parameters: action (the URL), URL params, method (get, post or patch), data for POST/PATCH.
    """
    headers = {
        'Content-type': 'application/json',
        'Accept-Encoding': 'gzip',
        'Authorization': 'Bearer %s' % access_token
    }
    if method == 'get':
        r = requests.request(method, instance_url+action, headers=headers, params=parameters, timeout=30)
    elif method in ['post', 'patch']:
        r = requests.request(method, instance_url+action, headers=headers, json=data, params=parameters, timeout=10)
    else:
        # other methods not implemented in this example
        raise ValueError('Method should be get or post or patch.')
    print('Debug: API %s call: %s' % (method, r.url) )
    if r.status_code < 300:
        if method=='patch':
            return None
        else:
            return r.json()
    else:
        raise Exception('API error when calling %s : %s' % (r.url, r.content))

def call():
    access_token, instance_url = OauthLogin.auth('rest')
    print(json.dumps(sf_api_call(access_token, instance_url, '/services/data/v39.0/query/', {
        'q': 'SELECT Account.Name, Name, CloseDate from Opportunity where IsClosed = False order by CloseDate ASC LIMIT 10'
        }), indent=2))

if __name__ == '__main__':
    call()