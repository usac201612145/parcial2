"""
-----------
Parcial 2 - Grupo 15
-----------
"""

import paho.mqtt.client as mqtt
import logging
from time import time 
import binascii
import threading #JDBM Concurrencia con hilos
import os 
from brokerData import * 

# JDBM funcion de manejo de audio 
def audioManage(state,hora):
    message = 'aplay '+hora+'.wav'
    logging.debug("AUDIO REPRODUCIDO")
    os.system(message)

# Configuracion inicial de logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )

# Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, rc):
    logging.info("Conectado al broker")

# Handler en caso se publique satisfactoriamente en el broker MQTT
def on_publish(client, userdata, mid): 
    publishText = "✓✓"
    logging.debug(publishText)

# PMJO - JCAG - JDBM - funcion de recepcion con condicionantes
# para el manejo corrrecto dependiendo del topico al que llegue el mensaje
def on_message(client, userdata, msg):

    strtopic = str(msg.topic)
    listOfTopic = strtopic.split('/')

    if 'audio' in listOfTopic:
        buff = msg.payload
        hora = time()
        logging.debug("SE RECIBIO UN AUDIO")
        archivo = open(str(hora)+'.wav', 'wb')
        archivo.write(buff)
        archivo.close()

    # JDBM funcion del hilo que ejecuta la funcion del manejo del audio
    # el unico argumento que se manda es hora que es el timestamp del momento en 
    # que se recibe el archivo
        t1 = threading.Thread(name = 'Audio Manage',
                        target = audioManage,
                        args = (0,str(hora)),
                        daemon = False
                        )
        t1.start()          # se inicia el hilo

    strmsg = msg.payload                    # JCAG
    strmsg = strmsg.decode()                #Convierte mensaje en string     
    listOfText = strmsg.split(' ')          #Divide el mensaje en una lista

    if str(usuario) not in listOfText:      #Comprueba si el mensaje es enviado por el mismo
        print('\n'+strmsg)                  #Imprime el mensaje si esta comprobacion da como resultado false
    

#-----------------------------------------------------------------------------------------------------------V
def fileRead(fileName):                                                                         
    archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA                                              
    data = []                                                                                               #|JDBM
    for linea in archivo: #Leer cada linea del archivo                                                      
        registro = linea.split(',')                                                                         #|Recorre archivo de configuracion    
        data.append(registro)                                                                               
    archivo.close() #Cerrar el archivo al finalizar                                                         
    return data      

#-----------------------------------------------------------------------------------------------------------A    
#-------------------------------------------------------------------------------------------------------------------------------------V 
# JCAG
class ClientManagment:
    def __init__(self, user, destino,  text, fsize):
        self.user=user
        self.destino=destino                         #Clase para el manejo del cliente
        self.text=text
        self.fsize=fsize

    def ClientMessage(self):
        if len(self.destino)<8:
            client.publish("salas/15/"+str(self.destino), ' '+str(self.user)+' ('+str(self.destino)+')'+' >>>: '+str(self.text) , qos = 0, retain = False)  
        else:                                                           
            client.publish("usuarios/15/"+str(self.destino), ' '+str(self.user)+' >>>: '+str(self.text) , qos = 0, retain = False)  
        return

    def ClientSubsMsg(self):
        client.subscribe(("usuarios/15/"+str(self.user), qos)) 
        client.subscribe(("audio/15/"+str(self.user), qos)) 
        return

    def ClientSubsSalas(self):
        client.subscribe(("salas/15/"+str(self.text), qos)) 
        client.subscribe(("audio/15/"+str(self.text), qos)) 
        return

    # PMJO envio de audio convirtiendo la informacion del archivo a bytearray 
    # para asegurar el envio correcto
    def ClientAudio(self, duracion):
        mensajeAudio = 'arecord -d ' + duracion + ' -f U8 -r 8000 ola.wav'
        os.system(mensajeAudio)
        f = open("ola.wav", "rb")
        imagestring = f.read()
        f.close()
        data= bytearray(imagestring)
        client.publish("audio/15/"+str(self.destino),data, qos = 0, retain = False)
        return

#-------------------------------------------------------------------------------------------------------------------------------------A 
# INICIO DE CLIENTE MQTT
client = mqtt.Client(clean_session=True) 
client.on_connect = on_connect 
client.on_message = on_message 
client.username_pw_set(MQTT_USER, MQTT_PASS) 
client.connect(host=MQTT_HOST, port = MQTT_PORT) 

qos = 0

#-----------------------------------------------------------------------------------------------------------
                                                                                                            
subs = fileRead('usuarios')                                                                                           
subs = subs[0]                                                                                                       
usuario = subs[0]          
usuario = usuario.strip()                                                                                #|JCGA
del subs[0]                                                                                                     
##Subscripcion simple con tupla (topic,qos)                                                                 #|Subscricion topics de archivo de configuracion
send = ClientManagment(usuario,0,0,0)
ClientManagment.ClientSubsMsg(send)     

subs = fileRead('salas')                                                                                           
subs = subs[0]  
newsubs = []

for i in subs:
    subs = i.split("15")
    element = subs[1]
    newsubs.append(element.strip()) 
                                                                                                                                                                                                                       
for i in newsubs:    
    send = ClientManagment(0,0,i,0)                                                                                          
    ClientManagment.ClientSubsSalas(send)                                                       
                                                                                                            
#------------------------------------------------------------------------------------------------------------A

#Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
client.loop_start()
#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa

#----------------------------------------------------------------------------------------------------------------------------V    

try:    
    while True:   
        
        formato = input("(Audio/Texto)?: ")                                                                                                                                  
        destinatario = input("Destino(201612145/S00)?: ")    
        pase = True                                                                     
                                                                                                                        
        if formato == 'Texto' or formato =='texto':                                                                                        #Interfaz de usuario primera version   
            while pase:                                                                                                          #JCGA   
                mensaje = input("Tu: ")        
                if mensaje == 'salir':
                    pase = False     
                else:  
                    send=ClientManagment(usuario,destinatario,mensaje,0)   
                    ClientManagment.ClientMessage(send)    
        elif formato == 'Audio' or formato == 'audio': 
            duracionIn = input("Ingrese la duracion del mensaje: ")
            send=ClientManagment(usuario,destinatario,0,0)
            ClientManagment.ClientAudio(send, duracionIn)
            logging.info('Enviando audio')
                                                                                                 
#----------------------------------------------------------------------------------------------------------------------------A

except KeyboardInterrupt:
    logging.warning("\nDesconectando del broker...")

finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")