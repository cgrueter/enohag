# enohag
This script basically is a Home Assistant -> MQTT -> Enocean gateway and vice versa.
It takes the sender IDs of the configured enocean sensors and actuators and creates the Home Assistant entities and the configuration of them by the Home Assistant MQTT discovery function. After the configuration of the script and starting it, I only have to place the automatic configured entities on the Home Assistant GUI from the “unused entities” list into my GUI.

I wrote this script to integrate my enocean equipment into my Home Assistant environment.
The reason is, that I was not able to use my enocean equipment by using the official Home Assistant enocean integration. 
Home Assistant really is an amazing software, I love and use it since many years now. As soon as the official enocean integration will also work for my need, this script will be obsolete.

# Warning
Due to my lack of knowledge how to write software, I know that ths script really is chaotic python spaghetti code.
This script may help you to "write" your own script to integrate your enocean equipment in your Home Assistant environment. 

# Prerequisites
1. Up and running Home Assistant system
2. MQTT broker, I use Mosquitto on a dedicated Raspberry Pi
3. Python 3.7 (any 3.x as 3.8 may also work)
4. kipe/enocean library
5. paho MQTT client
6. Enocean USB 300 Dongle or Enocean Pi Board
7. Some Enocean equipment: Sensors as a window contact, single or double rocker and actuators as power switch for lights or shutters 

# Known working enocean equipment
- Omnio WS-CH-102 rocker sensor, receiving EEP F6-02-xx
- Omnio FK101 Window contact FK101, receiving EEP D5-00-01
- Omnio UPJ230/12 roller shutter actuator sending EEP F6-02-02, receiving feedbak EEP D2-05-00
- Omnio UPD230/10 universal dimmer
- Omnio UPS230/10 one channel switch
- Omnio UPS230/12 two channel switch
- Eltako FSG71 1-10V dimmer

# Usage
1. Configure your MQTT parameters as
- mqttBroker =
- mqttUsername =
- mqttPassword = 
- mqttClientID =
2. Configure your enocean Dongle
- enocean_port = 
3. Reduce the configured sensors and actuators for example to two
- light_acutators =
- rocker_sensor = 
- rollo_actuators =
- rollo_actuators_v =
- contact_sensors =
- For the first start, the IDs doesn't  matter, and the description should be something general.
4. Start the script on a terminal
- pi@rpi:~# python3.7 enohag.py
- and watch the output of the script whend you press a rocker or when an other sensor or actuator is sending a telegram. 
5. Take the sender IDs of the output in step 4 and reconfigure the IDs and descriptions
- light_acutators =
- rocker_sensor = 
- rollo_actuators =
- rollo_actuators_v =
- contact_sensors =
6. Stop the script and teach in your enocean dongle sender ID's to your actuators by using the teach in script. Take the base ID of your enocean dongle and add 1 for every actuator. Every enocean dongle has it's ownd base ID (first three parts of the sender ID), the last part makes the sender ID unique.
7. Configure your teached in sender IDs in the "def on_mqtt_message" function of the script.
   For every actuator you have to configure the message.topic== belong your configuration of step 5 and two times teh teached in sender IDs. One time for 'ON' and one time for 'OFF'.
   
