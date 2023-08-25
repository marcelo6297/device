#Dispositivo IoT Simulado
#Para ejecutar este archivo se debe instalar counterfit y luego ejecutarlo
#instalar las librerias de counterfit
#Este dispositivo lee los datos de counterfit y los envia a la nube de Azure utilizando certificados X.509
#Se deben instanciar 9 sensores en counterfit 3 ADC para los sensores de tensión, 3 ADC para los sensores de Corriente
#2 sensores para Humedad y Temperatura y Un GPS, en el GPS setear una coordenada.
#Utilizando el CLI de Azure crear los certificados para el dispositivo en la misma ubicación de estos archivos.
#La nube de azure puede enviar comandos que encienden los LED del dispositivo.

import time

import random


from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_led import GroveLed

from counterfit_shims_seeed_python_dht import DHT

import counterfit_shims_serial
import pynmea2
from counterfit_connection import CounterFitConnection
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse, X509

import json

CounterFitConnection.init('127.0.0.1', 5000)

host_name = "trabajo-final-hub.azure-devices.net"
device_id = "reemplazar por el ID de su dispositivo"

x509 = X509("./utilizar su cert.pem", "./utilizar su clave-key.pem")
device_client = IoTHubDeviceClient.create_from_x509_certificate(x509, host_name, device_id)


print('Conectado con certificado X509')
device_client.connect()
print('Connected')

#Sensor Multiple de 8 Canales
sensorMultiple = ADC()

escalaVolt = 250
escalaCorr = 150
resolucion = 1023 #o 4096 depende del medidor
dormirPor = 20
 
dht = DHT("11", 6)

vacled  = GroveLed(10)
ampled  = GroveLed(11)
templed  = GroveLed(12)
#GPS
serial = counterfit_shims_serial.Serial('/dev/ttyAMA0')


#Manejar las solicitudes de la nube
def handle_method_request(request):

    if request.payload['vac_on'] == True:
        vacled.on()
    elif request.payload['vac_on'] == False:
        vacled.off()
    if request.payload['amp_on'] == True:
        ampled.on()
    elif request.payload['amp_on'] == False:
        ampled.off()    
    if request.payload['temp_on'] == True:
        templed.on()
    elif request.payload['temp_on'] == False:
        templed.off()

    method_response = MethodResponse.create_from_method_request(request, 200)
    device_client.send_method_response(method_response)
    device_client.on_method_request_received = handle_method_request




while True:
    #Leer voltaje
    print('Leyendo sensores')
   
    voltajeFRData = sensorMultiple.read(0) * escalaVolt / resolucion
    voltajeFSData = sensorMultiple.read(1) * escalaVolt / resolucion
    voltajeFTData = sensorMultiple.read(2) * escalaVolt / resolucion

    #Leer corriente
    corrienteFRData = sensorMultiple.read(3) * escalaCorr / resolucion
    corrienteFSData = sensorMultiple.read(4) * escalaCorr / resolucion
    corrienteFTData = sensorMultiple.read(5) * escalaCorr / resolucion
       
    #Leer temperatura
    _, temperaturaData = dht.read()
     
    #Leer GPS
    line = serial.readline().decode('utf-8')
    msg = pynmea2.parse(line)
    
    if msg.sentence_type == 'GGA':
       lat = pynmea2.dm_to_sd(msg.lat)
       lon = pynmea2.dm_to_sd(msg.lon)

       if msg.lat_dir == 'S':
           lat = lat * -1

       if msg.lon_dir == 'W':
           lon = lon * -1

    message = Message(json.dumps({ 'voltajeData': {'FR': voltajeFRData, 'FS': voltajeFSData, 'FT': voltajeFTData} ,
                                    'corrienteData': {'FR': corrienteFRData, 'FS': corrienteFSData, 'FT': corrienteFTData},
                                    'temperaturaData': temperaturaData,
                                     "gpsData" : { "lat":lat, "lon":lon } 
                                  }))
    print('Enviando a azure')
    device_client.send_message(message)

    print('Durmiendo')    
    time.sleep(dormirPor)
