import configparser
import requests
import logging
import json

def auth():

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
        
    authmeta = (('accesstoken', access_token), 
                ('instanceurl', instance_url), 
                ('tenantid', organization_id))
    return authmeta

if __name__ == '__main__':
    auth = auth()
    print(auth)