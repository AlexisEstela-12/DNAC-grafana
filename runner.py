from operator import lshift
from time import sleep
import requests
import json
from requests.auth import HTTPBasicAuth
import os
import sys
import keyword
import re
import datetime
import sqlite3
import mysql.connector



DNAC_URL = "10.96.246.70"
DNAC_USER = "admin"
DNAC_PASS = "Cisco12345"

lista_prueba = [(1.0, 0.0, 2.0, 2.0, '12/05/2022', '18:19:48')]
def create_database(lista):
    mydb = mysql.connector.connect(
    host = "localhost",
    user = "admin",
    password = "cisco12345",
    database = "Programa"
    )
    mycursor = mydb.cursor(prepared = True)
    
    # mycursor.execute("CREATE TABLE Datos (FiveSeconds REAL, Interrump FLOAT,OneMinute FLOAT, FiveMinutes REAL, SDate TIMESTAMP,sTime TIMESTAMP )")
    # sql  = "INSERT INTO Datos(FiveSeconds,Interrump,OneMinute,FiveMinutes,SDate,sTime) VALUES (?,?,?,?,?,?)"
    sql  = "INSERT INTO Datos(FiveSeconds,Interrump,OneMinute,FiveMinutes,SDate,sTime) VALUES ('%s','%s','%s','%s','%s','%s')" % (str,str,str,str,str,str)
    mycursor.executemany(sql,lista)
    mydb.commit()
    
    
def get_auth_token():
    """
    Building out Auth request. Using requests.post to make a call to the Auth Endpoint
    """
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                      # Endpoint URL
    hdr = {'content-type' : 'application/json'}                                           # Define request header
    resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)      # Make the POST Request
    token = resp.json()['Token']                                                          # Retrieve the Token
    return token    # Create a return statement to send the token back for later use


def get_device_list():
    """
    Building out function to retrieve list of devices. Using requests.get to make a call to the network device Endpoint
    """
    token = get_auth_token()
    url = "https://{}/api/v1/network-device".format(DNAC_URL)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify= False)  # Make the Get Request
    device_list = resp.json()
    print("{0:25}{1:25}".format("hostname", "id"))
    for device in device_list['response']:
        print("{0:25}{1:25}".format(device['hostname'], device['id']))
        #initiate_cmd_runner(token,device['id']) # initiate command runner
    initiate_cmd_runner(token) # initiate command runner

def initiate_cmd_runner(token):
    ios_cmd = "show processes cpu | include one minute"
    device_id = str(input("Copy/Past a device ID here:"))
    print("executing ios command -->", ios_cmd)
    param = {
        "name": "Show Command",
        "commands": [ios_cmd],
        "deviceUuids": [device_id]
    }
    url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
    header = {'content-type': 'application/json', 'x-auth-token': token}
    response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
    #print (response.json())
    task_id = response.json()['response']['taskId']
    print("Command runner Initiated! Task ID --> ", task_id)
    print("Retrieving Path Trace Results.... ")
    get_task_info(task_id, token)


def get_task_info(task_id, token):
    url = "https://{}/api/v1/task/{}".format(DNAC_URL, task_id)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    task_result = requests.get(url, headers=hdr, verify= False)
    file_id = task_result.json()['response']['progress']
    if "fileId" in file_id:
        unwanted_chars = '{"}'
        for char in unwanted_chars:
            file_id = file_id.replace(char, '')
        file_id = file_id.split(':')
        file_id = file_id[1]
        print("File ID --> ", file_id)
    else:  # keep checking for task completion
        get_task_info(task_id, token)
    get_cmd_output(token, file_id)


def get_cmd_output(token,file_id):
    print("INICIO DE FUNCION")
    url = "https://{}/api/v1/file/{}".format(DNAC_URL, file_id)
    hdr = {'x-auth-token': token, 'content-type': 'application/json'}
    cmd_result = requests.get(url, headers=hdr, verify= False)
    result= json.dumps(cmd_result.json(), indent=4, sort_keys=True)
    device_uuid = json.loads(result)[0]['deviceUuid']
    print(result)
    print("se imprimio")
    if json.loads(result)[0]['commandResponses']["SUCCESS"]:
        print("PRUEBA",json.loads(result)[0]['commandResponses']["SUCCESS"]['show processes cpu | include one minute'])
        sentence = json.loads(result)[0]['commandResponses']["SUCCESS"]['show processes cpu | include one minute']
        s = [ float(str(s).replace('%','')) for s in re.findall('[0-9]+[%]', sentence)]
        fecha, hora = getTime() 
        s.append(fecha)
        s.append(hora)
        print (s)
        salida = almacenar_db(s)
        create_database(salida)
         
        
def getTime():
    timenow = datetime.datetime.now()
    fecha = timenow.strftime("%d/%m/%Y")
    hora = timenow.strftime("%H:%M:%S")
    print(fecha)
    print(hora)
    return fecha, hora

def almacenar_db(s):
    lista = [tuple(s)]
    print(lista)
    return lista


get_device_list()