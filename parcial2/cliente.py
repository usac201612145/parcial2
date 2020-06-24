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

# JDBM funcion de manejo de audio por medio de hilo
def audioManage(state,hora):
    logging.info("Reproduciendo Mensaje de Voz")
    message = 'aplay '+hora+'.wav'
    os.system(message)
    logging.info("Mensaje de Voz reproducido")

# Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )

# Callback que se ejecuta cuando nos conectamos al broker
def on_connect(client, userdata, rc):
    logging.info("Conectado al broker")

# Handler en caso se publique satisfactoriamente en el broker MQTT
def on_publish(client, userdata, mid): 
    publishText = "✓✓"
    logging.info(publishText)

# PMJO - JCAG - JDBM - funcion de recepcion con condicionantes
# para el manejo corrrecto dependiendo del topico al que llegue el mensaje
def on_message(client, userdata, msg):

    strtopic = str(msg.topic)
    listOfTopic = strtopic.split('/')

    if 'audio' in listOfTopic:
        buff = msg.payload
        hora = time()
        logging.info("Se recibio un Mensaje de Voz")
        archivo = open(str(hora)+'.wav', 'wb')
        archivo.write(buff)
        archivo.close()

    # JDBM funcion del hilo que ejecuta la funcion del manejo del audio
    # el unico argumento que se manda es hora que es el timestamp del momento en 
    # que se recibe el archivo
        t1 = threading.Thread(name = 'Manejo de Audio',
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
    

#-----------------------------------------------------------------------------------------------------------
def fileRead(fileName):                                                                         
    archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA                                              
    data = []                                                                                               #|JDBM
    for linea in archivo: #Leer cada linea del archivo                                                      
        registro = linea.split(',')                                                                         #|Recorre archivo de configuracion    
        data.append(registro)                                                                               
    archivo.close() #Cerrar el archivo al finalizar                                                         
    return data      

#-----------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
# JCAG
#Clase para el manejo del cliente
class ClientManagment:
    def __init__(self, user, destino,  text, fsize):
        self.user = user
        self.destino = destino                         
        self.text = text
        self.fsize = fsize

    #Funcion para publicar en el topic de salas o a un usuario, se le envia el destino(sala o carnet) 
    # y el mensaje que se va enviar
    def ClientMessage(self):
        if len(self.destino)<8:
            client.publish("salas/15/"+str(self.destino), ' '+str(self.user)+' ('+str(self.destino)+')'+' >>>: '+str(self.text) , qos = 0, retain = False)  
        else:                                                           
            client.publish("usuarios/15/"+str(self.destino), ' '+str(self.user)+' >>>: '+str(self.text) , qos = 0, retain = False)  
        return

    #Funcion para suscribirse a un topic, se suscribe con el usuario al que se envia, esta funcion se usa cuando 
    # se selcciona la opcion de texto
    def ClientSubsMsg(self):
        client.subscribe(("usuarios/15/"+str(self.user), qos)) 
        client.subscribe(("audio/15/"+str(self.user), qos)) 
        return
    
    #Funcion para suscribirse a las salas y al topic de audio. Esta funcion se usa cuando se selecciona en el menu
    #la opcion de enviar audio
    def ClientSubsSalas(self):
        client.subscribe(("salas/15/"+str(self.text), qos)) 
        client.subscribe(("audio/15/"+str(self.text), qos)) 
        return

    # PMJO envio de audio convirtiendo la informacion del archivo a bytearray 
    # para asegurar el envio correcto
    def ClientAudio(self, duracion):
        if int(duracion)>30:
            duracion = '30'
            logging.warning('No se puede mandar archivos de mas de 30s, se enviara de 30s')
        logging.debug(duracion)
        mensajeAudio = 'arecord -d ' + duracion + ' -f U8 -r 8000 ola.wav'
        os.system(mensajeAudio)
        archivo = open("ola.wav", "rb")
        audiodata = archivo.read()
        archivo.close()
        data= bytearray(audiodata)
        client.publish("audio/15/"+str(self.destino),data, qos = 0, retain = False)
        return

#-------------------------------------------------------------------------------------------------------------------------------------A 
# PMJO
# INICIO DE CLIENTE MQTT
client = mqtt.Client(clean_session=True) 
client.on_connect = on_connect
client.on_publish = on_publish 
client.on_message = on_message 
client.username_pw_set(MQTT_USER, MQTT_PASS) 
client.connect(host=MQTT_HOST, port = MQTT_PORT) 

qos = 0

#-----------------------------------------------------------------------------------------------------------

#Se lee el archivo de usuarios, para usar el carne que esta en el archivo                      
subs = fileRead('usuarios')                                                                   
subs = subs[0]                                                                               
usuario = subs[0]          
usuario = usuario.strip()                                                                      #|PMJO
del subs[0]                                                                                                     
#Subscripcion simple con tupla (topic,qos)                                                     #|Subscricion topics de archivo de configuracion
#Se crea el objeto send de la clase ClienteManagment
send = ClientManagment(usuario,0,0,0)
ClientManagment.ClientSubsMsg(send)     


#Se lee el archivo de usuarios, para usar las salas que estan en el archivo y suscribirse al topic  
subs = fileRead('salas')
subs = subs[0]  
newsubs = []

#Se toma solo el dato de la sala, por ejemplo S01 del archivo de salas
for i in subs:
    subs = i.split("15")
    element = subs[1]
    newsubs.append(element.strip()) 

#Se realiza la suscripcion a los topics de las salas usan la clase ClienteManagment
for i in newsubs:    
    send = ClientManagment(0,0,i,0)                                                                                          
    ClientManagment.ClientSubsSalas(send)                                                       
                                                                                                            
#------------------------------------------------------------------------------------------------------------
client.loop_start()
#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa
#------------------------------------------------------------------------------------------------------------  

try:    
    while True:     #Este codigo lo ejecutamos siempre para mantener el menu constante y seleccionar entre texto, audio
                    # ingresar la duracion del audio, salirse del chat, etc.
        
        formato = input("(Audio/Texto): ")                                                                                             
        destinatario = input("Destino(2016xxxxx/S00): ")    
        pase = True                                                                     
                                                                                                                        
        if formato == 'Texto' or formato =='texto':                                                 #Interfaz de usuario primera version
            while pase:                                                                                             #JCGA   
                mensaje = input("Tu: ")        
                if mensaje == 'salir':
                    pase = False     
                else:
                    #Al haber guardado los datos ingresados por el usuario, se usan los datos de usuario, destinatario y mensaje
                    #para enviarlos a los topics ingresados y publicarlos por MQTT
                    send=ClientManagment(usuario,destinatario,mensaje,0)   
                    ClientManagment.ClientMessage(send)

                    #JCAGA | JDBM
                    #Si el usuario selecciono que desea enviar audio, se ejecuta este elif para que ingrese la duracion del audio
        elif formato == 'Audio' or formato == 'audio': 
            duracionIn = input("Ingrese la duracion del mensaje: ")
            send=ClientManagment(usuario,destinatario,0,0)
            ClientManagment.ClientAudio(send, duracionIn)
            logging.info('Enviando audio')
                                                                                                 
#----------------------------------------------------------------------------------------------------------------------------

except KeyboardInterrupt:
    logging.warning("\nDesconectando del broker...")

finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")