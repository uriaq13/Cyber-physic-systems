import json
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import paho.mqtt.client as mqtt

broker = "10.42.0.238"
m_topic = "mqtt_topic"
client = mqtt.Client()
client.connect(broker)

def hex_array_str(arr):
    my_str = ""
    for i in range(len(arr)):
        val = arr[i]
        if val < 16:
            my_str = my_str + "0"
        my_str = my_str + str('{0:x}'.format(arr[i])) + " "
    return my_str

escritura = False
while not escritura:
    continue_reading = True

    # This is the default key for authentication
    key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

    # Data read        
    backdata = []

    # Create an object of the class MFRC522
    MIFAREReader = MFRC522()

    #block_num = 8

    # Input block number
    block_num = 1

    print("Acerque el tag al lector")

    # This loop keeps checking for chips. If one is near it will get the UID and authenticate
    while continue_reading:
        client.publish(m_topic, payload = int(0))
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print("Tag detectado!")
        
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:
            
            # Print UID
            print("UID del tag: %s %s %s %s" % ('{0:x}'.format(uid[0]), '{0:x}'.format(uid[1]), '{0:x}'.format(uid[2]), '{0:x}'.format(uid[3])))
            
            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, block_num, key, uid)

            # Check if authenticated
            if status == MIFAREReader.MI_OK:

                # Read block_num
                backdata = MIFAREReader.MFRC522_Read(block_num)

                topic="lectura"
                text_data = ''.join([chr(int_value) for int_value in backdata])
                client.publish(topic, payload = text_data)
                                
                if backdata == [0x45, 0x71, 0x2e, 0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]:
                    escritura = True
                # if backdata != None:
                #     print("El bloque " + str(block_num) + " tiene el dato: " + hex_array_str(backdata))
                #     print(backdata)
                # else:
                #     print("No se pudo leer el bloque!")

                # # Make sure to stop reading for cards
                continue_reading = False
                GPIO.cleanup()
            else:
                print("Error de autentificacin!")


#if backdata == [69, 113, 46, 53, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
if backdata == [0x45, 0x71, 0x2e, 0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]:
    for i in range (20,23):
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        backdata = []
        block_num=i
        continue_reading = True
        # Create an object of the class MFRC522
        MIFAREReader = MFRC522()

        # This loop keeps checking for chips. If one is near it will get the UID and authenticate
        while continue_reading:

            # Scan for cards    
            (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

            # If a card is found
            if status == MIFAREReader.MI_OK:
                print("Tag detectado")

            # Get the UID of the card
            (status,uid) = MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:

                # Variable for the data to write
                data = [[0x53, 0x61, 0x6C, 0x61, 0x64, 0x6F, 0x73, 0x6D, 0x61, 0x72, 0x6D, 0x75, 0x65, 0x72, 0x74, 0x6F],
                        [0x6D, 0x65, 0x73, 0x61, 0x2C, 0x73, 0x69, 0x6C, 0x6C, 0x61, 0x2C, 0x62, 0x61, 0x6E, 0x63, 0x6F],
                        [0x33, 0x20, 0x36, 0x36, 0x20, 0x33, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]

                
                # Print UID
                print("UID de tag: %s%s%s%s" % ('{0:x}'.format(uid[0]), '{0:x}'.format(uid[1]), '{0:x}'.format(uid[2]), '{0:x}'.format(uid[3])))
                
                # Select the scanned tag
                MIFAREReader.MFRC522_SelectTag(uid)

                # Authenticate
                status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, block_num, key, uid)

                # Check if authenticated
                if status == MIFAREReader.MI_OK:
                    
                    print(block_num)
                    print("El bloque ",block_num," tena esta informacin:")
                    # Read block 8
                    backdata = MIFAREReader.MFRC522_Read(block_num)
                    print(hex_array_str(backdata))
                    
                    print("El bloque ", block_num ," se llenar con informacin nueva.")
                    # Write the data
                    index=i-20
                    MIFAREReader.MFRC522_Write(block_num, data[index])

                    print("Ahora el bloque ", block_num," tiene el nuevo dato:")
                    # Check to see if it was written
                    backdata = MIFAREReader.MFRC522_Read(block_num)
                    print(hex_array_str(backdata))

                    json_data = json.dumps(backdata)
                    topic="lectura"
                    #text_data = ''.join([chr(int_value) for int_value in backdata])
                    client.publish(topic, payload = json_data)

                    client.publish(m_topic, payload = int(1))
                    # Stop
                    MIFAREReader.MFRC522_StopCrypto1()
                    # Make sure to stop reading for cards
                    continue_reading = False
                    GPIO.cleanup()
                else:
                    print("Error de autentificacin")
client.loop_forever()

