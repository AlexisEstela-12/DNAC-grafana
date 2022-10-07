# from operator import lshift
# from time import sleep
# import requests
# import json
# from requests.auth import HTTPBasicAuth
# import os
# import sys
# import keyword
# import re
# import datetime
from funciones import *
# import time 

# DNAC_URL = "10.96.246.70"
# DNAC_USER = "admin"
# DNAC_PASS = "Cisco12345"
# DNAC_URL = "sandboxdnac2.cisco.com"
# DNAC_USER = "devnetuser"
# DNAC_PASS = "Cisco123!"




# def get_auth_token():
#     """
#     Building out Auth request. Using requests.post to make a call to the Auth Endpoint
#     """
#     url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                      # Endpoint URL
#     hdr = {'content-type' : 'application/json'}                                           # Define request header
#     resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)      # Make the POST Request
#     token = resp.json()['Token']  
#     # print (token)                                                        # Retrieve the Token
#     return token    # Create a return statement to send the token back for later use


def get_device_list():
    
    token = get_auth_token() 
    dic = {}
    url = "https://{}/api/v1/network-device".format(DNAC_URL)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify= False)  # Make the Get Request
    device_list = resp.json()
    print("{0:25}{1:25}".format("hostname", "id"))
    for device in device_list['response']:
        print("{0:25}{1:25}".format(device['hostname'], device['id']))
        dic[device['id']] = device['hostname']

    initiate_cmd_runner(token,dic)

# # lista = ["2a7567f6-e8d4-40d3-82b1-9a91479a4a4d",
# #         "9e6dcf5e-30cf-41c6-85f4-bd6457963a6c",
# #         "b8a9756f-1aa9-4cb9-be44-1aee13e1df89",
# #         "3ccf34ab-37f2-4d92-b4ba-91361c5868db",
# #         "c919d2ed-31a0-4570-a315-21f0ae9ec83e",
# #         "04ae491a-8032-4bd6-918b-ccf79e7db417",
# #         "75763d63-010f-4500-a32f-427ca4d81a68",
# #         "f8831289-b170-4815-9a94-5ef3b4b52bb8",
# #         #"2cf0eee2-0cc2-4ed7-8b0e-dc1a5fc6f08d",
# #         "26c68e55-3427-4e4f-a299-c2a6ded81214",
# #         "69ddf9d6-349d-4188-a883-9f8dc19155d4",
# #         "53b2062f-a20a-4930-a888-2a43a2e1596d",
# #         "2abf194b-1371-4e41-9bc1-4a5c9d38e39c",
# #         "4a53852e-3730-4023-a80b-a580670afc42",
# #         "1989d66f-df32-4c9c-936b-609a9abdde7c"
# #          ]

# lista_2= ["d354c924-f8ac-425f-b167-999f157e35e8",
#         "1c5f3896-9cac-40f8-85b3-64d2ae38f171",
#         "420aab4f-ff7e-41e0-8f59-eb18c0b80759"
#         ]

# lista_1 = ["f16955ae-c349-47e9-8e8f-9b62104ab604",
#            "f0cb8464-1ce7-4afe-9c0d-a4b0cc5ee84c",
#            "aa0a5258-3e6f-422f-9c4e-9c196db115ae",
#         #    "6b741b27-f7e7-4470-b6fc-d5168cc59502",
#         ]

# def initiate_cmd_runner(token):
#     ios_cmd = "show processes cpu | include one minute"
    
#     for j in range (0,100):
#         for i in lista_2:
#         # time.sleep(30)
#     # device_id = input("Ingresa un valor de uuid")
#             device_id = i
#             print("executing ios command -->", ios_cmd)
#             param = {
#             "name": "Show Command",
#             "commands": [ios_cmd],
#             "deviceUuids": [device_id]
#             }
#             url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
#             header = {'content-type': 'application/json', 'x-auth-token': token}
#             response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
#             task_id = response.json()['response']['taskId']
#         # print("Command runner Initiated! Task ID --> ", task_id)
#         # print("Retrieving Path Trace Results.... ")
#             get_task_info(task_id, token)


# def get_task_info(task_id, token):
#     url = "https://{}/api/v1/task/{}".format(DNAC_URL, task_id)
#     hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
#     task_result = requests.get(url, headers=hdr, verify= False)
#     file_id = task_result.json()['response']['progress']
#     if "fileId" in file_id:
#         unwanted_chars = '{"}'
#         for char in unwanted_chars:
#             file_id = file_id.replace(char, '')
#         file_id = file_id.split(':')
#         file_id = file_id[1]
#         # print("File ID --> ", file_id)
#     else:  # keep checking for task completion
#         get_task_info(task_id, token)
#     get_cmd_output(token, file_id)


# def get_cmd_output(token,file_id):
#     print("INICIO DE FUNCION")
#     url = "https://{}/api/v1/file/{}".format(DNAC_URL, file_id)
#     hdr = {'x-auth-token': token, 'content-type': 'application/json'}
#     cmd_result = requests.get(url, headers=hdr, verify= False)
#     result= json.dumps(cmd_result.json(), indent=4, sort_keys=True)
#     device_uuid = json.loads(result)[0]['deviceUuid']
#     # print(result)
#     if json.loads(result)[0]['commandResponses']["SUCCESS"]:
#         # print("PRUEBA",json.loads(result)[0]['commandResponses']["SUCCESS"]['show processes cpu | include one minute'])
#         sentence = json.loads(result)[0]['commandResponses']["SUCCESS"]['show processes cpu | include one minute']
#         s = [ float(str(s).replace('%','')) for s in re.findall('[0-9]+[%]', sentence)]
#         fecha= getTime() 
#         s.append(fecha)
#         almacenar_db(device_uuid,s)

# def getTime():
#     timenow = datetime.datetime.now().isoformat(timespec='seconds')
#     return timenow

# def almacenar_db(device_uuid,s):
#     print(device_uuid)
#     lista = [tuple(s)]
#     # print(lista)
#     try:
#         # cursor.execute("CREATE TABLE '{}' (FiveSeconds REAL, Interrup FLOAT, OneMinute FLOAT, FiveMinutes REAL, SDate TIMESTAMP)".format(device_uuid))
#         cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(device_uuid),lista)
#         conexion.commit()
#     except:
#         print("La tabla {} ya existe".format(device_uuid),type(s[0]))
#         cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(device_uuid),lista)
#         conexion.commit()
def get_auth_token_first():
    global token
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
    hdr = {'content-type' : 'application/json'} 
    resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
    token = resp.json()['Token']                                                  
    return token 

                
        
if __name__ == "__main__":
    global hora_actual
    global hora_60
    global token   
    token = get_auth_token_first()
    hora_actual = time_now()
    hora_60 = delta_min(hora_actual)                                   
    while True:
        # hora_actual = time_now()
        # ios_cmd = "show processes cpu | include one minute"
        # if hora_actual > hora_60:
        #     url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
        #     hdr = {'content-type' : 'application/json'}  
        #     resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
        #     hora_30 = delta_min(hora_actual)
        #     token_new = resp.json()['Token']
        #     print(token)
        # for i in lista_2:
        #     device_id = i
        #     param = {
        #     "name": "Show Command",
        #     "commands": [ios_cmd],
        #     "deviceUuids": [device_id]
        #     }
        #     url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)  
        #     header = {'content-type': 'application/json', 'x-auth-token': token}
        #     response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
        #     task_id = response.json()['response']['taskId']
        #     get_task_info(task_id, token)
        get_device_list()             
        sleep(60)    

