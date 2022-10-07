# import requests
# from requests.auth import HTTPBasicAuth
# import datetime
# from datetime import timedelta
# import datetime
# from datetime import datetime as dt
# import time 
# from funciones import * 


# DNAC_URL = "sandboxdnac2.cisco.com"
# DNAC_USER = "devnetuser"
# DNAC_PASS = "Cisco123!"

# def list_dispo():
#     token = get_auth_token()
#     url = "https://{}/api/v1/network-device".format(DNAC_URL)
#     hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
#     resp = requests.get(url, headers=hdr, verify= False)
#     device_list = resp.json()
#     dict ={}
#     for device in device_list['response']:
#         dict[device["id"]] = device["hostname"] 

    
# get_device_list()



variable = [{'deviceUuid': '2a7567f6-e8d4-40d3-82b1-9a91479a4a4d', 'commandResponses': {'SUCCESS': {'show processes cpu | include one minute': 'show processes cpu | include one minute\nCPU utilization for five seconds: 0%/0%; one minute: 0%; five minutes: 1%\n1000-1#'}, 'FAILURE': {}, 'BLACKLISTED': {}}}]

print(type(variable))