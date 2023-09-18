#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import rospy
from std_msgs.msg import String, Int32  

"""
Topic for mqtt = mqtt_topic
"""
class MQTTT_Bridge:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect("10.42.0.238", 1883, 60)  

        rospy.init_node("mqtt")
        self.pub = rospy.Publisher("mqtt_pub", String, queue_size=10)
        self.dato = rospy.Publisher("dato", Int32, queue_size=10)

    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")  # Assuming the message payload is a string
        rospy.loginfo("Received MQTT message: %s", payload)

        # Publish the MQTT message as a ROS message
        ros_msg = String()
        ros_msg.data = payload
        self.pub.publish(ros_msg)

        if ros_msg.data == "1":
            self.dato.publish(1)
            rospy.loginfo("publico uno")
        else: 
            self.dato.publish(0)
            rospy.loginfo("publico cero")


    def run(self):
        # Subscribe to the MQTT topic where you expect messages
        self.mqtt_client.subscribe("mqtt_topic")
        self.mqtt_client.loop_start()
        rospy.spin()


if __name__ == '__main__':
    try:
        s = MQTTT_Bridge()
        s.run()
   
    except rospy.ROSInterruptException:
        rospy.loginfo("Error in Mqtt Bridge")