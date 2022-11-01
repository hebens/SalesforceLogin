import configparser
import requests
import logging
import json

def authenticate():

    config = configparser.ConfigParser()
    config.read("../resources/application.properties")

    username = config['User']['User']
    password = config['User']['Password']
    client_id = config['Connected_App']['Client_Id']
    client_secret = config['Connected_App']['Client_Secret']
    
    params = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password
    }
    r = requests.post("https://login.salesforce.com/services/oauth2/token", params=params)

    access_token = r.json().get("access_token")
    instance_url = r.json().get("instance_url")
    organization_id = (r.json().get("id").split("/")[-2]) #fetches user id (-1) and org id (-2)
        
    return access_token, instance_url, organization_id

def auth(target):
    access_token, instance_url, organization_id = authenticate()

    match target:
        case "pubsub":
            return  (('accesstoken', access_token), 
                    ('instanceurl', instance_url), 
                    ('tenantid', organization_id))
        case "rest":
            return access_token, instance_url

if __name__ == '__main__':
    
    # --------------------------------------------------------------------------------------------
    # calling the auth method requires selection of the login purpose to prepare a proper response
    # valid purposes are:
    # pubsub and rest
    # --------------------------------------------------------------------------------------------
    cred = auth('rest') 
    print("Rest :: " + str(cred))
    cred = auth('pubsub')
    print("\nPubSub :: " + str(cred))