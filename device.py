#Lectura de valores que simulan 3 sensores de voltaje
#3 sensores de corriente
#1 sensor de Humedad y temperatura y 1 GPS
#Luego estos datos son convertidos a formato JSon y enviados a la nube de Azure
#En la nube se procesa con Azure Function para tomar desciciones en base a ciertos umbrales definidos

import time

import random


from azure.iot.device import IoTHubDeviceClient, Message

import json

connection_string = "ingrese su connection_string aqui"
device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)

dormirPor = 20

print('Connecting')
device_client.connect()
print('Connected')


while True:
    #Leer voltaje
    print('Leyendo sensores')
    voltajeFRData = random.randint(900,1023) 
    voltajeFSData = random.randint(900,1023) 
    voltajeFTData = random.randint(900,1023) 
    # voltajeData = voltaje.read(0)
    voltajeFRData = (voltajeFRData * 25) / 1023
    voltajeFSData = (voltajeFSData * 25) / 1023
    voltajeFTData = (voltajeFTData * 25) / 1023


    #Leer corriente
    #corrienteData = corriente.read(1)
    corrienteFRData = random.randint(500,610) 
    corrienteFSData = random.randint(500,610) 
    corrienteFTData = random.randint(500,610)

    corrienteFRData = (corrienteFRData * 100 ) / 1023
    corrienteFSData = (corrienteFSData * 100 ) / 1023
    corrienteFTData = (corrienteFTData * 100 ) / 1023
    #Leer temperatura    
    temperaturaData = random.randint(10,90); 


    message = Message(json.dumps({ 'voltajeData': {'FR': voltajeFRData, 'FS': voltajeFSData, 'FT': voltajeFTData} ,
                                    'corrienteData': {'FR': corrienteFRData, 'FS': corrienteFSData, 'FT': corrienteFTData},
                                    'temperaturaData': temperaturaData,
                                     "gpsData" : { "lat":-25.2858500, "lon":-57.6167300 } 
                                  }))
    print('Enviando a azure')
    device_client.send_message(message)

    print('Durmiendo')    
    time.sleep(dormirPor)


    
    
    
