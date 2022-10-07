import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import timedelta
import datetime
import time 
import sqlite3


DNAC_URL = "sandboxdnac.cisco.com"
DNAC_USER = "devnetuser"
DNAC_PASS = "Cisco123!"


def clear_counters(token,interface):
    for i in interface:	
        ios_cmd = "clear counters"
        device_id = i
        param = {
                "name": "Show Command",
                "commands": [ios_cmd],
                "deviceUuids": [device_id]
                }
        url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
        header = {'content-type': 'application/json', 'x-auth-token': token}
        response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
        print(response.json())	
        print("LOS CONTADORES SE HAN REINICIADO")	


def time_now ():
    timenow = datetime.datetime.now()
    return timenow

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
        if hora_actual > hora_30:
            resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
            hora_30 = delta_min(hora_actual)
            flag = False
            token = resp.json()['Token']                                                 
    return token  

def get_auth_token_first():
    global token
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)                 
    hdr = {'content-type' : 'application/json'} 
    resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify= False)
    token = resp.json()['Token']                                                    
    return token 

def get_device_list():
    lista = []
    token = get_auth_token_first()
    url = "https://{}/api/v1/network-device".format(DNAC_URL)
    hdr = {'x-auth-token': token, 'content-type' : 'application/json'}
    resp = requests.get(url, headers=hdr, verify= False)  # Make the Get Request
    device_list = resp.json()
    dict ={}
    for device in device_list['response']:
        dict[device["id"]] = device["hostname"]
        lista.append(device["id"])
    clear_counters(token,lista)
    time.sleep(240)
    port_list()
        
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
        print(response.json())
        if "errorCode" in response.json()["response"].keys():
            print("error salio")
            task_id = get_command_only(token,i[0],cuenta)
            print("obtuve task id con el error")
            if task_id == "":
                print("no pude obtener el taskid :( ")
                continue
            continue
        task_id = response.json()['response']['taskId']
        tupla_1 = (task_id,i)
        task_list.append(tupla_1)
    print(task_list)
    get_task_info(task_list,token)
    
    
def get_command_only(token,id,cuenta):
    global task
    if cuenta <= 3:   
        task = ""
        ios_cmd =  "show interface {} ".format(id)
        param = {
            "name": "Show Command",
            "commands": [ios_cmd],
            "deviceUuids": [id]
                }
        url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
        header = {'content-type': 'application/json', 'x-auth-token': token}
        response = requests.post(url, data=json.dumps(param), headers=header, verify= False)
        if "errorCode" in response.json()["response"].keys() :
            cuenta = cuenta + 1
            get_command_only(token,id,cuenta)
        else:
            task = response.json()['response']['taskId']
            print("termine aquí con el {}".format(id)) 
    return task

def get_task_info(task_id, token):
    file_id_list = []
    for element in task_id:
        url = "https://{}/api/v1/task/{}".format(DNAC_URL, element[0])
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
            tupla = (file_id,element[1])
        else:  
            print("entre porque aun no esta listo")
            time.sleep(10)
            file_id = get_task_info_only(element, token)
            tupla = (file_id,element[1])
        file_id_list.append(tupla)
    print(file_id_list)    
    get_cmd_output(token,file_id_list)

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
        print("obtuve el file_id por la funcion sola")
    else:  
        get_task_info_only(task_id, token)    
    return file_id


def get_cmd_output(token,file_id):
    lista = []
    for each in file_id:
        url = "https://{}/api/v1/file/{}".format(DNAC_URL, each[0])
        print(each)
        time.sleep(10)
        hdr = {'x-auth-token': token, 'content-type': 'application/json'}
        cmd_result = requests.get(url, headers=hdr, verify= False)
        result= json.dumps(cmd_result.json(), indent=4, sort_keys=True)
        print(result)
        print("aqui estoy")
        if type(cmd_result.json()) != list: 
            print("entreee a qquiii gil")
            time.sleep(10)
            continue
        print("sali de aqui")
        if json.loads(result)[0]['commandResponses']["SUCCESS"]:
            valor = json.loads(result)[0]['commandResponses']["SUCCESS"]["show interface {} ".format(each[1][1])]
            string_valor = str(valor)
            busque = string_valor.split()
            print(busque)
            bits_sec = []
            bytes = []
            packets = []
            lon = len(busque)
            print(busque)
            for j in range (0,lon) :
                if busque[j] == "bits/sec,": 
                    bits_sec.append(float(busque[j-1]))
                if (busque[j] == "packets" and busque[j-1] != "input"):
                    bytes.append(float(busque[j+2]))
                if (busque[j] == "packets" and busque[j-1] != "input"):
                    packets.append(float(busque[j-1]))
            print(bytes)
            print(bits_sec)
            print(packets)
            if bytes != [] and bits_sec != [] and packets != []:
                lista = bits_sec + bytes + packets
                fecha = getTime()
                lista.append(fecha)
                lista.insert(0,each[1][1])
                print(lista)
                almacenar_db(lista,each[1])    
                    
def almacenar_db(lista,datos): 
    print(lista)
    s = [tuple(lista)]
    conexion = sqlite3.connect("C:/Users/aeste/OneDrive - Cisco/DNA/GRAFANNA/Puertos_packets.db")
    cursor = conexion.cursor()
    conexion.commit()
    try:
        cursor.execute("CREATE TABLE '{}' (Port CHAR,Input_Rate FLOAT, Output_Rate FLOAT, Input_bytes FLOAT,Output_bytes FLOAT,Input_Packets FLOAT,Output_Packets FLOAT, SDate TIMESTAMP)".format(datos[0]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?,?,?,?)".format(),s)
        conexion.commit()
    except:
        print("La tabla {} ya existe".format(datos[0]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?,?,?,?)".format(datos[0]),s)
        conexion.commit()
    
    conexion.close()
 
# token = get_auth_token_first()
# hora_actual = time_now()
# hora_30 = delta_min(hora_actual)  
# get_device_list()

if __name__ == "__main__":  
    global hora_actual
    global hora_30
    hora_actual = time_now()
    hora_30 = delta_min(hora_actual) 
    global token 
    token = get_auth_token_first()
    while True:  
        get_device_list()
        time.sleep(40)