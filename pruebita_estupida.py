
import time
import requests
import json
from requests.auth import HTTPBasicAuth
DNAC_URL = "sandboxdnac2.cisco.com"
DNAC_USER = "devnetuser"
DNAC_PASS = "Cisco123!"

def get_auth_token():
    

    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
    hdr = {'content-type' : 'application/json'}                                       
    resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False) 
    token = resp.json()['Token']
    print (token)                                                      
    return token    
x_1 = get_auth_token()
print (x_1)
time.sleep(30)
x_2 = get_auth_token()
print (x_2)

if x_1 == x_2:
    print ("ALEXIS COJUDO")
else: 
    print("TE GANE")