from textwrap import indent
import requests
import json
from requests.auth import HTTPBasicAuth
from funciones import DNAC_PASS,DNAC_URL,DNAC_USER
from funciones import *

# DNAC_URL = "10.96.246.70"
# DNAC_USER = "admin"
# DNAC_PASS = "Cisco12345"

def get_command_only(token,id,cuenta):
    global task
    if cuenta <= 3:   
        task = ""
        ios_cmd =  "show interface {} ".format(id[1])
        param = {
            "name": "Show Command",
            "commands": [ios_cmd],
            "deviceUuids": [id[0]]
                }
        url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
        header = {'content-type': 'application/json', 'x-auth-token': token}
        time.sleep(10)
        response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
        if "errorCode" in response.json()["response"].keys() :
            cuenta = cuenta + 1
            get_command_only(token,id,cuenta)
        else:
            task = response.json()['response']['taskId']
            print("termine aquí con el {}".format(id[1])) 
    return task


def get_device_list():
    token = get_auth_token_first()
    url = "https://{}/api/v1/network-device".format(DNAC_URL)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify= False)  # Make the Get Request
    device_list = resp.json()
    dict ={}
    for device in device_list['response']:
        dict[device["id"]] = device["hostname"] 

    
def almacenar_db(device_uuid,s):
    hostnames = list_dispo()  
    print(device_uuid[0])
    lista = [tuple(s)]
    conexion = sqlite3.connect("C:/Users/aeste/OneDrive - Cisco/DNA/GRAFANNA/cpu_database_5.db")
    cursor = conexion.cursor()
    conexion.commit()
    try:
        cursor.execute("CREATE TABLE '{}' (Port CHAR,Input_Rate FLOAT, Output_Rate FLOAT, Input_bytes FLOAT,Output_bytes FLOAT, SDate TIMESTAMP)".format(hostnames[device_uuid[0]]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?,?)".format(hostnames[device_uuid[0]]),lista)
        conexion.commit()
    except:
        print("La tabla {} ya existe".format(device_uuid[0]),type(s[0]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?,?)".format(hostnames[device_uuid[0]]),lista)
        conexion.commit()
    
    conexion.close()
    
def delta_min(time):
    variacion = timedelta(minutes=60)
    time = time + variacion
    return time

def getTime():
    timenow = datetime.datetime.now().isoformat(timespec='seconds')
    return timenow
    
def get_auth_token():
    global hora_30
    global token
    global hora_actual
    flag = False
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
    hdr = {'content-type' : 'application/json'}                                       
    while flag == False:
        hora_actual = time_now()  
        flag = True
        if hora_actual > hora_60:
            resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
            hora_30 = delta_min(hora_actual)
            flag = False
            token = resp.json()['Token']                                                 
    return token  

def port_list():
    token = get_auth_token()
    list_ports = []
    url = "https://{}/dna/intent/api/v1/interface".format(DNAC_URL)
    header = {'content-type': 'application/json', 'x-auth-token': token}
    response = requests.get(url, headers=header, verify= False)
    json_response = response.json()
    result= json.dumps(json_response, indent=4, sort_keys=True)
    longitud = len(json.loads(result)["response"])
    for i in range (0,longitud):
        port = (json.loads(result)["response"][i]["portName"])
        uuid = (json.loads(result)["response"][i]["deviceId"])
        dupla = (uuid,port)
        list_ports.append(dupla)
    print(list_ports)
    get_command(token,list_ports)

def get_command(token,puertos):
    global task_id
    task_id = ""
    global cuenta 
    cuenta = 0
    task_list = [] 
    for i in puertos:
        ios_cmd = "show interface {} ".format(i[1])
        device_id = i[0]
        param = {
            "name": "Show Command",
            "commands": [ios_cmd],
            "deviceUuids": [device_id]
            }
        url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
        header = {'content-type': 'application/json', 'x-auth-token': token}
        response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
        if "errorCode" in response.json()["response"].keys():
            print("error salio")
            task_id = get_command_only(token,i,cuenta)
            if task_id == "":
                continue
            continue
        task_id = response.json()['response']['taskId']
        task_list.append(task_id)
        print("termine aquí con el {}".format(i[1]))
        lista_file_id =   get_task_info(task_list,token)  
            # get_task_info(task_id, token,i)
            
            
def get_task_info_only(task_id, token):
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
    else:  
        get_task_info_only(task_id, token)    
    
    return file_id
            
def get_task_info(task_id, token):
    file_id_list = []
    global file_id
    for element in task_id:
        url = "https://{}/api/v1/task/{}".format(DNAC_URL, element)
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
            file_id_list.append(file_id)
        else:  
            file_id = get_task_info_only(element, token)
        print(file_id_list)    
        get_cmd_output(token,file_id_list)

def get_cmd_output(token,file_id):
    for each in file_id:
        url = "https://{}/api/v1/file/{}".format(DNAC_URL, each)
        hdr = {'x-auth-token': token, 'content-type': 'application/json'}
        cmd_result = requests.get(url, headers=hdr, verify= False)
        result= json.dumps(cmd_result.json(), indent=4, sort_keys=True)
        print(result)
        print("aqui estoy")
        if type(cmd_result.json()) != list: 
            print("entreee a qquiii gil")
            continue
        print("sali de aqui")
        # if json.loads(result)[0]['commandResponses']["SUCCESS"]:
        #     valor = json.loads(result)[0]['commandResponses']["SUCCESS"]["show interface {} ".format(i[1])]
        #     string_valor = str(valor)
        #     busque = string_valor.split()
        #     bits_sec = []
        #     bytes = []
        #     lon = len(busque)
        #     print(busque)
        #     for each in range (0,lon) :
        #         if busque[each] == "bits/sec,": 
        #             bits_sec.append(float(busque[each-1]))
        #         if (busque[each] == "packets" and busque[each-1] != "input"):
        #             bytes.append(float(busque[each+2]))
                    
        #     lista = bits_sec + bytes 
        #     fecha = getTime()
        #     lista.append(fecha)
        #     lista.insert(0,i[1])
        #     print(lista)
        #     almacenar_db(lista)
        
def list_dispo():
    token = get_auth_token()
    url = "https://{}/api/v1/network-device".format(DNAC_URL)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify= False)
    device_list = resp.json()
    dict ={}
    for device in device_list['response']:
        dict[device["id"]] = device["hostname"]
    return dict

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
    hora_actual = time_now()
    hora_60 = delta_min(hora_actual) 
    global token 
    token = get_auth_token_first()  
    port_list()
    # global token 
    # token = get_auth_token_first()
#     hora_actual = time_now()
    # hora_60 = delta_min(hora_actual)                                

#     while True:
#         port_list()
#         sleep(300)
                                                        









    # while True:
    #     hora_actual = time_now()
    #     ios_cmd = "show processes cpu | include one minute"
    #     if hora_actual > hora_60:
    #         url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
    #         hdr = {'content-type' : 'application/json'}  
    #         resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
    #         hora_30 = delta_min(hora_actual)
    #         token_new = resp.json()['Token']
    #         print(token)
    #     port_list(token)
    #     sleep(360)