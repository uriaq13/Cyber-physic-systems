#!/usr/bin/env python
from math import sin, cos
import rospy
from geometry_msgs.msg import Pose2D, TransformStamped, Quaternion
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64, Float32
import tf2_ros
import tf.transformations

class Odometria:
    def __init__(self):
        rospy.init_node('odometria_node')

        self.r = 0.05
        self.l = 0.18
        self.ts = 0.1

        self.wl = 0.0
        self.wr = 0.0

        self.v = 0.0
        self.w = 0.0

        self.dis = Float64()
        self.dis.data = 0.0

        self.pose = Pose2D()
        self.pose.x = 0.0
        self.pose.y = 0.0
        self.pose.theta = 0.0
        
        self.br = tf2_ros.TransformBroadcaster()

        # Initialize the Odometry message
        self.odom = Odometry()
        self.odom.header.frame_id = "odom"
        self.odom.child_frame_id = "base_link"

        self.odometria_publisher = rospy.Publisher('odom', Odometry, queue_size=10)
        self.dist_publisher = rospy.Publisher('dist', Float64, queue_size=10)
        
        rospy.Subscriber('/wl', Float32, self.wl_callback)
        rospy.Subscriber('/wr', Float32, self.wr_callback)
        rospy.Timer(rospy.Duration(0.1), self.timer_callback)

    def wl_callback(self, msg):
        self.wl = msg.data

    def wr_callback(self, msg):
        self.wr = msg.data
        
    def omega(self):
        self.w = ((self.r)/self.l) * (self.wr - self.wl)

    def vel(self):
        self.v = ((self.r)/2) * (self.wr + self.wl)

    def distance(self):
        self.dis.data += self.v * self.ts

    def position(self):
        self.pose.theta += self.w * self.ts
        self.pose.x += cos(self.pose.theta) * self.v * self.ts
        self.pose.y += sin(self.pose.theta) * self.v * self.ts

    def timer_callback(self, timer):
        self.omega()
        self.vel()
        self.distance()
        self.position()
        
        # Create and populate the TransformStamped message for TF
        t = TransformStamped()
        t.header.stamp = rospy.Time.now()
        t.header.frame_id = "odom"
        t.child_frame_id = "base_link"
        t.transform.translation.x = self.pose.x
        t.transform.translation.y = self.pose.y
        t.transform.translation.z = 0.0  # Assuming a 2D robot
        q = tf.transformations.quaternion_from_euler(0, 0, self.pose.theta)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        # Broadcast the transform
        self.br.sendTransform(t)

        # Populate the Odometry message
        self.odom.header.stamp = rospy.Time.now()
        self.odom.pose.pose.position.x = self.pose.x
        self.odom.pose.pose.position.y = self.pose.y
        self.odom.pose.pose.position.z = 0.0
        q = tf.transformations.quaternion_from_euler(0, 0, self.pose.theta)
        self.odom.pose.pose.orientation = Quaternion(*q)
        
        # Assuming you also want to include velocity in your odometry (optional)
        self.odom.twist.twist.linear.x = self.v
        self.odom.twist.twist.angular.z = self.w

        # Publish the Odometry message
        self.odometria_publisher.publish(self.odom)
        self.dist_publisher.publish(self.dis)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    o = Odometria()
    o.run()
