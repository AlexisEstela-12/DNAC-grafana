import csv
from netmiko import ConnectHandler
import re
import datetime
import time 
import sqlite3

def almacenar_db(device_uuid,s):
    lista = [tuple(s)]
    conexion = sqlite3.connect("C:/Users/aeste/OneDrive - Cisco/DNA/GRAFANNA/Clientes_NDNAC/CPU_NDNAC.db")
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

def getTime():
    timenow = datetime.datetime.now().isoformat(timespec='seconds')
    return timenow   

def connect_netmiko(lista):
        for i in lista:
            net_connect = ConnectHandler(
                device_type = "cisco_xe",
                ip = i[0],
                username = i[2],
                password = i[3]
                                        )
            if net_connect.check_enable_mode():
                    print("Success: in enable mode")
            else:
                print("Fail... con el equipo {}".format(i[1]))
                continue
            print(net_connect.find_prompt())
            net_connect.enable()
            print("se logro en el equipo {}".format(i[1]))
            output_CPU = net_connect.send_command("show processes cpu | include one minute")
            s = [ float(str(s).replace('%','')) for s in re.findall('[0-9]+[%]', output_CPU)]
            fecha= getTime() 
            s.append(fecha)
            almacenar_db(i[1],s)
            
 
def excel_credential():
    lista_general = []
    with open("C:/Users/aeste/OneDrive - Cisco/Escritorio/credenciales.csv",newline="\n") as csvfile:
        spamreader = csv.reader(csvfile,delimiter=",") 
        for row in spamreader:
            if row == ["","","",""] or row == ['IP Address', 'Hostname', 'Username', 'Password']:
                continue
            else:
                lista_general.append(row)
    return lista_general

if __name__ == "__main__":
    while True:
        lista = excel_credential()
        connect_netmiko(lista)  
