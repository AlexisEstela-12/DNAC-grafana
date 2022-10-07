import time 
import json
from requests.auth import HTTPBasicAuth
from datetime import timedelta
import requests
import datetime
import sqlite3
import re
from time import sleep


DNAC_URL = "10.96.246.70"
DNAC_USER = "admin"
DNAC_PASS = "Cisco12345"


lista = ["2a7567f6-e8d4-40d3-82b1-9a91479a4a4d",
        "9e6dcf5e-30cf-41c6-85f4-bd6457963a6c",
        "b8a9756f-1aa9-4cb9-be44-1aee13e1df89",
        "3ccf34ab-37f2-4d92-b4ba-91361c5868db",
        "c919d2ed-31a0-4570-a315-21f0ae9ec83e",
        "04ae491a-8032-4bd6-918b-ccf79e7db417",
        "75763d63-010f-4500-a32f-427ca4d81a68",
        "f8831289-b170-4815-9a94-5ef3b4b52bb8",
        "2cf0eee2-0cc2-4ed7-8b0e-dc1a5fc6f08d",
        "26c68e55-3427-4e4f-a299-c2a6ded81214",
        "69ddf9d6-349d-4188-a883-9f8dc19155d4",
        "53b2062f-a20a-4930-a888-2a43a2e1596d",
        "2abf194b-1371-4e41-9bc1-4a5c9d38e39c",
        "4a53852e-3730-4023-a80b-a580670afc42",
        "1989d66f-df32-4c9c-936b-609a9abdde7c"
         ]

def time_now ():
    timenow = datetime.datetime.now()
    return timenow

def delta_min(time):
    variacion = timedelta(minutes=60)
    time = time + variacion
    return time

def get_auth_token_first():
    global token
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
    hdr = {'content-type' : 'application/json'} 
    resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
    token = resp.json()['Token']                                                  
    return token 

def get_auth_token():   
    global hora_30
    global token
    global hora_actual
    #hora_actual = time_now()
    flag = False
    #hora_30 = delta_min(hora_actual)
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
    hdr = {'content-type' : 'application/json'}                                       
    while flag == False:
        #resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
        hora_actual = time_now()  
        flag = True
        if hora_actual > hora_30:
            resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
            hora_30 = delta_min(hora_actual)
            flag = False
            token = resp.json()['Token']
        print (token)                                                      
    return token 
    

def initiate_cmd_runner(token):
    ios_cmd = "show processes cpu | include one minute"
    for device_id in lista:
        print("executing ios command -->", ios_cmd)
        param = {
            "name": "Show Command",
            "commands": [ios_cmd],
            "deviceUuids": [device_id]
        }
        url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
        header = {'content-type': 'application/json', 'x-auth-token': token}
        response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
        print ("\n", response.json() ,"\n")
        task_id = response.json()['response']['taskId']
        print("Command runner Initiated! Task ID --> ", task_id)
        print("Retrieving Path Trace Results.... ")
        get_task_info(task_id, token)    
    
def cmd_runner_only(token,id,cuenta):
    global task
    if cuenta <= 3:   
        task = ""
        ios_cmd = "show processes cpu | include one minute"
        param = {
            "name": "Show Command",
            "commands": [ios_cmd],
            "deviceUuids": [id]
                }
        url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
        header = {'content-type': 'application/json', 'x-auth-token': token}
        time.sleep(10)
        response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
        if "errorCode" in response.json()["response"].keys() :
            cuenta = cuenta + 1
            cmd_runner_only(token,id,cuenta)
        else:
            task = response.json()['response']['taskId']
            print("error solucionado") 
    return task

def get_task_info(task_id, token):
    url = "https://{}/api/v1/task/{}".format(DNAC_URL, task_id)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    task_result = requests.get(url, headers=hdr, verify= False)
    file_id = task_result.json()['response']['progress']
    print(task_result.json())
    if "fileId" in file_id:
        unwanted_chars = '{"}'
        for char in unwanted_chars:
            file_id = file_id.replace(char, '')
        file_id = file_id.split(':')
        file_id = file_id[1]
    else:  # keep checking for task completion
        print(" \n  TODAVIA NO ACABO P MANO ESPERA :) ")
        get_task_info(task_id, token)
        sleep(10)
    get_cmd_output(token, file_id)   


def get_cmd_output(token,file_id):
    url = "https://{}/api/v1/file/{}".format(DNAC_URL, file_id)
    hdr = {'x-auth-token': token, 'content-type': 'application/json'}
    cmd_result = requests.get(url, headers=hdr, verify= False)
    print(cmd_result.json())
    result= json.dumps(cmd_result.json(), indent=4, sort_keys=True)
    device_uuid = json.loads(result)[0]['deviceUuid']
    if json.loads(result)[0]['commandResponses']["SUCCESS"]:
        sentence = json.loads(result)[0]['commandResponses']["SUCCESS"]['show processes cpu | include one minute']
        s = [ float(str(s).replace('%','')) for s in re.findall('[0-9]+[%]', sentence)]
        fecha= getTime() 
        s.append(fecha)
        almacenar_db(device_uuid,s)    


def getTime():
    timenow = datetime.datetime.now().isoformat(timespec='seconds')
    return timenow

def almacenar_db(device_uuid,s):
    lista = [tuple(s)]
    conexion = sqlite3.connect("C:/Users/aeste/OneDrive - Cisco/DNA/GRAFANNA/CPU_BASE_PRUEBA_3.db")
    cursor = conexion.cursor()
    conexion.commit()
    try:
        cursor.execute("CREATE TABLE '{}' (FiveSeconds REAL, Interrup FLOAT, OneMinute FLOAT, FiveMinutes REAL, SDate TIMESTAMP)".format(device_uuid))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(device_uuid),lista)
        conexion.commit()
    except:
        print("La tabla {} ya existe".format(device_uuid),type(s[0]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(device_uuid),lista)
        conexion.commit()
    print("TERMINAMOS DE GUARDAR EN EL DATABASE \n")
    print("\n")
        
if __name__ == "__main__":
    global hora_actual
    global hora_60
    global token   
    token = get_auth_token_first()
    hora_actual = time_now()
    hora_60 = delta_min(hora_actual)     
    while True :
        try:
            initiate_cmd_runner(token)
        except:
            print("Me equivoquè :(, duermo e intento luego")
            sleep(60)
            token = get_auth_token_first()
            initiate_cmd_runner(token)

