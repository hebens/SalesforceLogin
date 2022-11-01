#SOAP Login Module for Salesforce
#requires a properties file

from cgi import test
from genericpath import samefile
import xml.etree.ElementTree as et
from datetime import datetime
import requests
import configparser

import pubsub_api_pb2 as pb2
import pubsub_api_pb2_grpc as pb2_grpc
from urllib.parse import urlparse

config = configparser.ConfigParser()
config.read("../resources/application.properties")

def auth():
        """
        Sends a login request to the Salesforce SOAP API to retrieve a session
        token. The session token is bundled with other identifying information
        to create a tuple of metadata headers, which are needed for every RPC
        call.
        """
        username = config['User']['User']
        password = config['User']['Password']
        url =  config['Server']['soapLoginUrl']
        print("Login Url :: " + str(url))
        headers = {'content-type': 'text/xml', 'SOAPAction': 'Login'}
        xml = "<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' " + \
              "xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' " + \
              "xmlns:urn='urn:partner.soap.sforce.com'><soapenv:Body>" + \
              "<urn:login><urn:username><![CDATA[" + username + \
              "]]></urn:username><urn:password><![CDATA[" + password + \
              "]]></urn:password></urn:login></soapenv:Body></soapenv:Envelope>"
        res = requests.post(url, data=xml, headers=headers)
        res_xml = et.fromstring(res.content.decode('utf-8'))[0][0][0]

        try:
            url_parts = urlparse(res_xml[3].text)
            url = "{}://{}".format(url_parts.scheme, url_parts.netloc)
            session_id = res_xml[4].text
        except IndexError:
            print("An exception occurred. Check the response XML below:", 
            res.__dict__)

        # Get org ID from UserInfo
        uinfo = res_xml[6]
        # Org ID
        tenant_id = uinfo[8].text

        # Set metadata headers
        metadata = (('accesstoken', session_id),
                         ('instanceurl', url),
                         ('tenantid', tenant_id))
        return metadata

if __name__ == '__main__':
    auth = auth()
    print(auth)        