import paho.mqtt.client as mqtt
import logging
import time
import os 
from brokerData import * #Informacion de la conexion

LOG_FILENAME = 'mqtt.log'

#Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '%(message)s'
    )

#Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, rc):
    logging.info("Conectado al broker")


#Callback que se ejecuta cuando llega un mensaje al topic suscrito
def on_message(client, userdata, msg):
    strmsg = str(msg.payload)                           #Convierte mensaje en string
    listOfText = strmsg.split(' ')                      #Divide el mensaje en una lista

    if '201612145' not in listOfText:                   #Comprueba si el mensaje es enviado por el mismo
        print('\n'+strmsg)                              #Imprime el mensaje si esta comprobacion da como resultado false

#Handler en caso se publique satisfactoriamente en el broker MQTT
def on_publish(client, userdata, mid): 
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)    
    
    #Y se almacena en el log 
    logCommand = 'echo "(' + str(msg.topic) + ') -> ' + str(msg.payload) + '" >> ' + LOG_FILENAME
    os.system(logCommand)
#-----------------------------------------------------------------------------------------------------------V
def fileRead(fileName = 'usuarios.txt'):                                                                         
    archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA                                              
    data = []                                                                                               #|JDBM
    for linea in archivo: #Leer cada linea del archivo                                                      
        registro = linea.split(',')                                                                         #|Recorre archivo de configuracion    
        data.append(registro)                                                                               
    archivo.close() #Cerrar el archivo al finalizar                                                         
    return data                                                                                             
#-----------------------------------------------------------------------------------------------------------A    

class ClientManagment:
    def __init__(self, user, destino,  text):
        self.user=user
        self.destino=destino
        self.text=text


    def ClientMessage(self):
        if len(self.destino)<8:
            client.publish("salas/15/"+str(self.destino), ' '+str(self.user)+' >>>: '+str(self.text) , qos = 0, retain = False)  
        else:                                                           
            client.publish("usuarios/15/"+str(self.destino), ' '+str(self.user)+' >>>: '+str(self.text) , qos = 0, retain = False)  
        time.sleep(0.1)  
        return

    #def entrada():
    #    formato = input("(Audio/Texto)?: ")                                                                                                                                  
    #    destin = input("Destino(201612145/S00)?: ")   
    #    return formato, destin


     

client = mqtt.Client(clean_session=True) #Nueva instancia de cliente
client.on_connect = on_connect #Se configura la funcion "Handler" cuando suceda la conexion
client.on_publish = on_publish #Se configura la funcion "Handler" que se activa al publicar algo
client.on_message = on_message #Se configura la funcion "Handler" que se activa al llegar un mensaje a un topic subscrito
client.username_pw_set(MQTT_USER, MQTT_PASS) #Credenciales requeridas por el broker
client.connect(host=MQTT_HOST, port = MQTT_PORT) #Conectar al servidor remoto

qos = 0

#-----------------------------------------------------------------------------------------------------------V
                                                                                                            
subs = fileRead()                                                                                           
subs = subs[0]                                                                                                       
usuario = subs[0]                                                                                           #|JCGA
del subs[0]                                                                                                     
##Subscripcion simple con tupla (topic,qos)                                                                 #|Subscricion topics de archivo de configuracion
client.subscribe(("comandos/15/"+str(usuario), qos))                                                        
client.subscribe(("usuarios/15/"+str(usuario), qos))                                                            
                                                                                                            
for i in subs:                                                                                              
    client.subscribe(("salas/15/"+str(i), qos))                                                         
                                                                                                            
#------------------------------------------------------------------------------------------------------------A

#Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
client.loop_start()
#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa

#----------------------------------------------------------------------------------------------------------------------------V    

try:    
    while True:   
        
        formato = input("(Audio/Texto)?: ")                                                                                                                                  
        destinantario = input("Destino(201612145/S00)?: ")    
        pase = True                                                                     
                                                                                                                        
        if formato == 'Texto' or 'texto':                                                                                        #Interfaz de usuario primera version   
            while pase:                                                                                                          #JCGA   
                mensaje = input("Tu: ")        
                if mensaje == 'salir':
                    pase = False     
                else:  
                    prueba1=ClientManagment(usuario,destinantario,mensaje)   
                    ClientManagment.ClientMessage(prueba1)   
                    time.sleep(0.1)                                                                                                                                                                                     
                #logging.info("Estado: conectado")                                                                                   
                #time.sleep(2)                                                                                                   
#----------------------------------------------------------------------------------------------------------------------------A

except KeyboardInterrupt:
    logging.warning("\nDesconectando del broker...")

finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")