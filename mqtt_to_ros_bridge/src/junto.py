#Read a RFID and publish it to MQTT

import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import paho.mqtt.client as mqtt
import time


def hex_array_str(arr):
    my_str = ""
    for i in range(len(arr)):
        val = arr[i]
        if val < 16:
            my_str = my_str + "0"
        my_str = my_str + str('{0:x}'.format(arr[i])) + " "
    return my_str

mqtt_broker = "10.48.0.238"
mqtt_topic = "house/sensor1"
client = mqtt.Client()
client.connect(mqtt_broker, 1883, 60)

continue_reading = True
MIFAREReader = MFRC522()
key= [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
backData = []
block_num=int(0)

while continue_reading:
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    if status == MIFAREReader.MI_OK:
        print("¡Tag detectado!")
    (status,uid) = MIFAREReader.MFRC522_Anticoll()
    if status == MIFAREReader.MI_OK:
        print("UID del tag: %s %s %s %s" % ('{0:x}'.format(uid[0]), '{0:x}'.format(uid[1]), '{0:x}'.format(uid[2]), '{0:x}'.format(uid[3])))
        MIFAREReader.MFRC522_SelectTag(uid)
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, block_num, key, uid)
        if status == MIFAREReader.MI_OK:
            backdata = MIFAREReader.MFRC522_Read(block_num)
            if backdata != None:
                print("El bloque " + str(block_num) + " tiene el dato: " + hex_array_str(backdata))
                client.publish(mqtt_topic, payload=hex_array_str(backdata))
            else:
                print("¡No se pudo leer el bloque!")

            # Make sure to stop reading for cards
            continue_reading = False
            GPIO.cleanup()
        else:
            print("¡Error de autentificación!")

client.loop_forever()
               