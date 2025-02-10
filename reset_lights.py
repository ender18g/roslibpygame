import time # import time library
import roslibpy # import roslibpy library

# establish roslibpy connection to ROS
#ros_node = roslibpy.Ros(host='127.0.0.1', port=9012)
ros_node = roslibpy.Ros(host='192.168.8.104', port=9012)





# start ROSLIBPY node
ros_node.run()



# define robot name we will connect to
robot_names = ['juliet', 'echo', 'bravo', 'india', 'foxtrot', 'omega']


# create publisher on the cmd_lightring topic, use https://iroboteducation.github.io/create3_docs/api/ros2/ for message type specification
led_pubs = [roslibpy.Topic(ros_node, f'/{names}/cmd_lightring', 'irobot_create_msgs/LightringLeds') for names in robot_names]
note_pubs = [roslibpy.Topic(ros_node, f'/{names}/cmd_audio', 'irobot_create_msgs/AudioNoteVector') for names in robot_names]

#batt_topic = [roslibpy.Topic(ros_node, f'/{names}}/battery_state', 'sensor_msgs/BatteryState') for names in robot_names]  



#def callback_battery(msg):
#      print(msg)


# compose an LightringLeds message
led_colors = [{'red': 255, 'green': 0, 'blue': 255}, 
              {'red': 255, 'green': 0, 'blue': 255},
              {'red': 255, 'green': 0, 'blue': 255},
              {'red': 255, 'green': 255, 'blue': 255},
              {'red': 255, 'green': 255, 'blue': 255},
              {'red': 255, 'green': 255, 'blue': 255}]


lightring_led_message = {'leds': led_colors,
                         'override_system': False}

lightring_ros_msg = roslibpy.Message(lightring_led_message)

def generateAudioMessage(frequency, duration):
        dur_msg = {'sec': 0, 'nanosec': int(duration * 10**9)}
        audio_notes = [
            {'frequency': frequency, 'max_runtime': dur_msg}
        ]
        #audio_notes = [{'frequency': 392, 'max_runtime': {'sec': 0,'nanosec': 177500000}}, {'frequency': 523, 'max_runtime': {'sec': 0,'nanosec': 355000000}}, {'frequency': 587, 'max_runtime': {'sec': 0,'nanosec': 177500000}}, {'frequency': 784, 'max_runtime': {'sec': 0,'nanosec': 533000000}}]
        message_audio = roslibpy.Message({
            'notes': audio_notes,
            'append': False
        })
        return message_audio


count = 0
audio_msg = generateAudioMessage(900, 1)
for t in range(0,len(robot_names)):
    led_pubs[t].publish(lightring_ros_msg)
    note_pubs[t].publish(audio_msg)
    print(robot_names[count])
    count +=1
    time.sleep(4)




[t.unadvertise() for t in led_pubs]

ros_node.terminate()