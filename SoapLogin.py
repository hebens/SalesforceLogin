#SOAP Login Module for Salesforce
#requires a properties file

import xml.etree.ElementTree as et
from datetime import datetime
import requests
import configparser

import pubsub_api_pb2 as pb2
import pubsub_api_pb2_grpc as pb2_grpc
from urllib.parse import urlparse

config = configparser.ConfigParser()
config.read("../resources/application.properties")

def authenticate():
        username = config['User']['User']
        password = config['User']['Password']
        loginUrl =  config['Server']['soapLoginUrl']
        print("Login Url :: " + str(loginUrl))
        headers = {'content-type': 'text/xml', 'SOAPAction': 'Login'}
        xml = "<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' " + \
              "xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' " + \
              "xmlns:urn='urn:partner.soap.sforce.com'><soapenv:Body>" + \
              "<urn:login><urn:username><![CDATA[" + username + \
              "]]></urn:username><urn:password><![CDATA[" + password + \
              "]]></urn:password></urn:login></soapenv:Body></soapenv:Envelope>"
        res = requests.post(loginUrl, data=xml, headers=headers)
        res_xml = et.fromstring(res.content.decode('utf-8'))[0][0][0]

        try:
            url_parts = urlparse(res_xml[3].text)
            instance_url = "{}://{}".format(url_parts.scheme, url_parts.netloc)
            session_id = res_xml[4].text
        except IndexError:
            print("An exception occurred. Check the response XML below:", 
            res.__dict__)

        # Get org ID from UserInfo
        userInfo = res_xml[6]
        # Org ID
        tenant_id = userInfo[8].text

        return session_id, instance_url, tenant_id

if __name__ == '__main__':
    session_id, instance_url, tenant_id = authenticate()
    print("SessionId    :: " + str(session_id))
    print("Instance URL :: " + str(instance_url))        