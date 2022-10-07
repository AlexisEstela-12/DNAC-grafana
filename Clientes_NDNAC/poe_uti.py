import csv
from netmiko import ConnectHandler
import datetime
import time 
import sqlite3

def almacenar_db(device_uuid,s):
    lista = [tuple(s)]
    print(lista)
    conexion = sqlite3.connect("C:/Users/aeste/OneDrive - Cisco/DNA/GRAFANNA/Clientes_NDNAC/PoE_NDNAC_general.db")
    cursor = conexion.cursor()
    conexion.commit()
    try:
        cursor.execute("CREATE TABLE '{}' (DeviceName TEXT,powerAllocated REAL, powerConsumed REAL, powerRemaining REAL, powerUsed'%' REAL ,SDate TIMESTAMP)".format(device_uuid))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?,?)".format(device_uuid),lista)
        conexion.commit()
    except:
        print("La tabla {} ya existe".format(device_uuid),type(s[4]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?,?)".format(device_uuid),lista)
        conexion.commit()

def almacenar_db_perdevice(name, s):
    lista = [tuple(s)]
    conexion = sqlite3.connect("C:/Users/aeste/OneDrive - Cisco/DNA/GRAFANNA/Clientes_NDNAC/PoE_NDNAC.db")
    cursor = conexion.cursor()
    conexion.commit()
    print(lista)
    try:
        cursor.execute("CREATE TABLE '{}' (powerAllocated REAL, powerConsumed REAL, powerRemaining REAL, powerUsed'%' REAL ,SDate TIMESTAMP)".format(name))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(name),lista)
        conexion.commit()
    except:
        print("La tabla {} ya existe".format(name),type(s[4]))
        cursor.executemany("INSERT INTO '{}' VALUES(?,?,?,?,?)".format(name),lista)
        conexion.commit()

def getTime():
    timenow = datetime.datetime.now().isoformat(timespec='seconds')
    return timenow  

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
            net_connect.enable()
            print("se logro en el equipo {}".format(i[1]))
            output_CPU = net_connect.send_command("show power inline police")
            spl = output_CPU.split()
            if spl[0] != "Module":
                print("El dispositivo {} no es un equipo PoE ".format(i[1]))
            else: 
                pwr_allocated = float(spl[12])
                pwr_consumed = float(spl[13])
                pwr_Remainig = float(spl [14])
                pwr_consumed_perc = float(round(pwr_consumed*100/pwr_allocated,2))
                fecha= getTime() 
                lista_para = [i[1], pwr_allocated,pwr_consumed,pwr_Remainig,pwr_consumed_perc,fecha]
                lista_espe = [pwr_allocated,pwr_consumed,pwr_Remainig,pwr_consumed_perc,fecha]
                almacenar_db('General',lista_para)
                almacenar_db_perdevice(i[1],lista_espe)


if __name__ == "__main__":
    while True:
        lista = excel_credential()
        connect_netmiko(lista)  
        time.sleep(400)
            