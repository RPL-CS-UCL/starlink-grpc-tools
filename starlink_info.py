#!/usr/bin/env python3
import rospy
import subprocess
import json
from std_msgs.msg import String
from sensor_msgs.msg import Image
import base64
import os
from PIL import Image as PILImage
import io
 
PROJ_DICT = '/home/jjiao/robohike_ws/src/RPL-RoboHike/src/tools/starlink-grpc-tools'

def run_dish_command(*args):
    cmd = ['python3', f'{PROJ_DICT}/dish_grpc_text.py'] + list(args)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return result.stdout.decode()
 
def publish_obstruction_map(pub):
    filename = "/tmp/obstructions.png"
    subprocess.run(['python3', f'{PROJ_DICT}/dish_obstruction_map.py', filename])
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            img = PILImage.open(f)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            encoded = base64.b64encode(img_bytes).decode()
            pub.publish(encoded)
 
def starlink_status_publisher():
    rospy.init_node('starlink_status_node')
    status_pub = rospy.Publisher('/starlink/status', String, queue_size=10)
    ping_pub = rospy.Publisher('/starlink/ping_latency', String, queue_size=10)
    ob_map_pub = rospy.Publisher('/starlink/obstruction_map', String, queue_size=1)
 
    rate = rospy.Rate(1.0)  # 1 Hz
    while not rospy.is_shutdown():
        try:
            status = run_dish_command('status')
            latency = run_dish_command('ping_latency')
            status_pub.publish(status)
            ping_pub.publish(latency)
            publish_obstruction_map(ob_map_pub)
        except Exception as e:
            rospy.logerr(f"Starlink query error: {e}")
        rate.sleep()
 
if __name__ == '__main__':
    starlink_status_publisher()