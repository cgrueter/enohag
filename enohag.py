#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import RadioPacket
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET, RORG
import enocean.utils
import traceback
import sys, time, queue, logging
import paho.mqtt.client as mqtt

mqttBroker = "10.0.0.99"
mqttUsername = "mqtt-user"
mqttPassword = "mqtt-secret"
mqttClientId = "enocean_gateway"
enocean_port="/dev/ttyUSB0"

light_actuators = {'01:75:CE:97' : 'light_one',
                   '01:72:6D:C5' : 'light_two',
                   '01:73:75:7B' : 'light_abc'}
rocker_sensors = ['00:7A:9F:CA','00:7A:35:C3', '00:79:10:F2', '00:7A:35:D9', '00:78:F9:09', '00:7A:9F:E3', '00:7A:3A:D4']
# Place your shutter ID and names here
rollo_actuators = {'01:75:C9:FE' : 'rollo_nord'}
# or here, if open close is reversed, as the most of mines :-)
rollo_actuators_v = {'01:77:30:3A' : 'rollo_west_1',
                     '01:75:BB:76' : 'rollo_west_2',
                     '01:72:60:48' : 'rollo_south_1',
                     '01:72:64:C0' : 'rollo_south_2'}
contact_sensors = {'01:7B:4C:42' : 'window_west_1',
                   '01:7B:6A:CF' : 'window_west_2',
                   '01:72:04:5E' : 'window_south_1',
                   '01:71:E5:FA' : 'window_south_2'}

init_logging()

destination_id=[0xFF, 0xFF, 0xFF, 0xFF]
sender_id=[0xAA, 0xAA, 0xAA, 0x00]

def assemble_packet_press_a_1(sender_id):
    return Packet.create(packet_type=PACKET.RADIO, rorg=0xF6, rorg_func=0x02, rorg_type=0x02, 
                         destination=destination_id, sender=sender_id, R1=0, EB=1, R2=0, SA=0, T21=True, NU=True)

def assemble_packet_press_a_0(sender_id):
    return Packet.create(packet_type=PACKET.RADIO, rorg=0xF6, rorg_func=0x02, rorg_type=0x02, 
                         destination=destination_id, sender=sender_id, R1=1, EB=1, R2=0, SA=0, T21=True, NU=True)

def assemble_packet_press_b_1(sender_id):
    return Packet.create(packet_type=PACKET.RADIO, rorg=0xF6, rorg_func=0x02, rorg_type=0x02, 
                         destination=destination_id, sender=sender_id, R1=2, EB=1, R2=0, SA=0, T21=True, NU=True)

def assemble_packet_press_b_0(sender_id):
    return Packet.create(packet_type=PACKET.RADIO, rorg=0xF6, rorg_func=0x02, rorg_type=0x02, 
                         destination=destination_id, sender=sender_id, R1=3, EB=1, R2=0, SA=0, T21=True, NU=True)

def assemble_packet_release(sender_id):
    return Packet.create(packet_type=PACKET.RADIO, rorg=0xF6, rorg_func=0x02, rorg_type=0x02, 
                         destination=destination_id, sender=sender_id, R1=0, EB=0, R2=0, SA=0, T21=True, NU=False)

def on_mqtt_connect(client, userdata, flags, rc):
  if rc==0:
    print("Connection to "+mqttBroker+" successful, Returned code=",rc)
    mqttclient.connected_flag=True
  else:
    print("Bad connection Returned code=",rc)

def on_mqtt_disconnect(client, userdata, rc):
  print("disconnecting reason " +str(rc))
  mqttclient.connected_flag=False
  mqttclient.disconnected_flag=True

def on_mqtt_message(client, userdata, message):
  print("Received Topic:",message.topic,"Message",message.payload)
  if message.topic=="homeassistant/light/enocean/light_one/set":
    if message.payload.decode('UTF-8')=='ON':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x12]))#Teached in sender ID for this light
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='OFF':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x12]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/light/enocean/light_two/set":
    if message.payload.decode('UTF-8')=='ON':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x16]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='OFF':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x16]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/light/enocean/light_abc/set":
    if message.payload.decode('UTF-8')=='ON':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x50]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='OFF':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x50]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/cover/enocean/rollo_west_1/set":
    if message.payload.decode('UTF-8')=='OPEN':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x32])) #Teached in sender ID for this shutter
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='CLOSE':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x32]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/cover/enocean/rollo_west_2/set":
    if message.payload.decode('UTF-8')=='OPEN':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x35]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='CLOSE':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x35]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/cover/enocean/rollo_south_1/set":
    if message.payload.decode('UTF-8')=='OPEN':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x30]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='CLOSE':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x30]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/cover/enocean/rollo_south_2/set":
    if message.payload.decode('UTF-8')=='OPEN':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x34]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='CLOSE':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x34]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/cover/enocean/rollo_nord/set":
    if message.payload.decode('UTF-8')=='OPEN':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x33]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='CLOSE':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x33]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  
mqtt.Client.connected_flag=False
mqtt.Client.disconnected_flag=True
mqttclient = mqtt.Client(mqttClientId)
mqttclient.on_connect=on_mqtt_connect
mqttclient.on_disconnect=on_mqtt_disconnect
mqttclient.username_pw_set(username=mqttUsername,password=mqttPassword)
mqttclient.connect(mqttBroker)
mqttclient.loop_start()
mqttclient.on_message=on_mqtt_message

def connect_messages():
  for k in light_actuators:
    mqttclient.publish("homeassistant/light/enocean/"+light_actuators[k]+"/config",'{"name" : "'+light_actuators[k]+'", "state_topic":"homeassistant/light/enocean/'+light_actuators[k]+'/state","command_topic" : "homeassistant/light/enocean/'+light_actuators[k]+'/set", "uniq_id" : "'+k+'", "avty_t" : "homeassistant/light/enocean/'+light_actuators[k]+'/availability"}', qos=1, retain=False)
    mqttclient.publish("homeassistant/light/enocean/"+light_actuators[k]+"/availability","online",retain=False)
    mqttclient.subscribe([("homeassistant/light/enocean/"+light_actuators[k]+"/set", 0)])
  for k in rollo_actuators:
    mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators[k]+"/config",'{"name" : "'+rollo_actuators[k]+'", "device_class" : "shutter", "command_topic" : "homeassistant/cover/enocean/'+rollo_actuators[k]+'/set", "set_position_topic" : "homeassistant/cover/enocean/'+rollo_actuators[k]+'/set_position", "position_topic" : "homeassistant/cover/enocean/'+rollo_actuators[k]+'/position", "uniq_id" : "'+k+'", "avty_t" : "homeassistant/cover/enocean/'+rollo_actuators[k]+'/availability"}', qos=1, retain=False)
    mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators[k]+"/availability","online",retain=False)
    mqttclient.subscribe([("homeassistant/cover/enocean/"+rollo_actuators[k]+"/set", 0), ("homeassistant/cover/enocean/"+rollo_actuators[k]+"/set_position", 0)])
  for k in rollo_actuators_v:
    mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators_v[k]+"/config",'{"name" : "'+rollo_actuators_v[k]+'", "device_class" : "shutter", "command_topic" : "homeassistant/cover/enocean/'+rollo_actuators_v[k]+'/set", "set_position_topic" : "homeassistant/cover/enocean/'+rollo_actuators_v[k]+'/set_position", "position_topic" : "homeassistant/cover/enocean/'+rollo_actuators_v[k]+'/position", "uniq_id" : "'+k+'", "avty_t" : "homeassistant/cover/enocean/'+rollo_actuators_v[k]+'/availability"}', qos=1, retain=False)
    mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators_v[k]+"/availability","online",retain=False)
    mqttclient.subscribe([("homeassistant/cover/enocean/"+rollo_actuators_v[k]+"/set", 0), ("homeassistant/cover/enocean/"+rollo_actuators_v[k]+"/set_position", 0)])
  for k in contact_sensors:
    mqttclient.publish("homeassistant/binary_sensor/enocean/"+contact_sensors[k]+"/config",'{"name" : "'+contact_sensors[k]+'", "device_class" : "window", "state_topic" : "homeassistant/binary_sensor/enocean/'+contact_sensors[k]+'/state", "payload_on" : "open", "payload_off" : "closed" , "uniq_id" : "'+k+'", "avty_t" : "homeassistant/binary_sensor/enocean/'+contact_sensors[k]+'/availability", "exp_aft" : "1800"}', qos=1, retain=False)
    mqttclient.publish("homeassistant/binary_sensor/enocean/"+contact_sensors[k]+"/availability","online",retain=False)

communicator = SerialCommunicator(enocean_port)
communicator.start()

# endless loop receiving radio packets
while communicator.is_alive():
  if mqttclient.disconnected_flag:
    connect_messages()
    print("Connect Messages sent")
    mqttclient.disconnected_flag=False
  while not mqttclient.connected_flag:
    print("Waiting for reconnect")
    time.sleep(1)
  try:
    # Loop to empty the queue...
    packet = communicator.receive.get(block=True, timeout=1)
    if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.VLD:
      packet.select_eep(0x05, 0x00)
      packet.parse_eep()
      if packet.sender_hex in rollo_actuators:
        print("*** Got rollo feedback --> :", rollo_actuators[packet.sender_hex], packet.parsed['POS']['raw_value'])
        mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators[packet.sender_hex]+"/position", packet.parsed['POS']['raw_value'],retain=False)
      elif packet.sender_hex in rollo_actuators_v:
        print("*** Got rollo feedback --> :", rollo_actuators_v[packet.sender_hex], packet.parsed['POS']['raw_value'])
        mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators_v[packet.sender_hex]+"/position", 100-packet.parsed['POS']['raw_value'],retain=False)
      else:
        print("New unknown VLD telegram: ")
        for k in packet.parsed:
          print('%s: %s' % (k, packet.parsed[k]))
    if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.BS4:
      # parse packet with given FUNC and TYPE
      print("New unknown BS4 telegram: ")
      for k in packet.parse_eep(0x02, 0x05):
        print('%s: %s' % (k, packet.parsed[k]))
    if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.BS1:
      # alternatively you can select FUNC and TYPE explicitely
      packet.select_eep(0x00, 0x01)
      # parse it
      packet.parse_eep()
      if packet.sender_hex in contact_sensors:
        print("*** Got contact message --> :" , contact_sensors[packet.sender_hex], packet.parsed['CO']['value'])
        mqttclient.publish("homeassistant/binary_sensor/enocean/"+contact_sensors[packet.sender_hex]+"/state",packet.parsed['CO']['value'],retain=False)
      else:
        print("New unknown BS1 telegram: ")
        for k in packet.parsed:
          print('%s: %s' % (k, packet.parsed[k]))
    if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.RPS:
      packet.parse_eep(0x02, 0x02)
      if packet.sender_hex in light_actuators:
        if packet.parsed['R1']['value'] == 'Button AI' and packet.parsed['EB']['value'] == 'pressed':
          print("*** Got light feedback: ", light_actuators[packet.sender_hex], "A ON")
          mqttclient.publish("homeassistant/light/enocean/"+light_actuators[packet.sender_hex]+"/state","ON",retain=False)
        if packet.parsed['R1']['value'] == 'Button AO' and packet.parsed['EB']['value'] == 'pressed':
          print("*** Got light feedback: ", light_actuators[packet.sender_hex] , "A OFF")
          mqttclient.publish("homeassistant/light/enocean/"+light_actuators[packet.sender_hex]+"/state","OFF",retain=False)
        if packet.parsed['R1']['value'] == 'Button BI' and packet.parsed['EB']['value'] == 'pressed':
          print("*** Got light feedback: ", light_actuators[packet.sender_hex], "B ON")
        if packet.parsed['R1']['value'] == 'Button BO' and packet.parsed['EB']['value'] == 'pressed':
          print("*** Got light feedback: ", light_actuators[packet.sender_hex] , "B OFF")
      elif packet.sender_hex in rocker_sensors:
        if packet.parsed['R1']['value'] == 'Button AI' and packet.parsed['EB']['value'] == 'pressed':
          print("*** Got rocker message: ", packet.sender_hex, "A ON")
        if packet.parsed['R1']['value'] == 'Button AO' and packet.parsed['EB']['value'] == 'pressed':
          print("*** Got rocker message: ", packet.sender_hex , "A OFF")
        if packet.parsed['R1']['value'] == 'Button BI' and packet.parsed['EB']['value'] == 'pressed':
          print("*** Got rocker message: ", packet.sender_hex, "B ON")
        if packet.parsed['R1']['value'] == 'Button BO' and packet.parsed['EB']['value'] == 'pressed':
          print("*** Got rocker message: ", packet.sender_hex , "B OFF")
      else:
        print("New unknown RPS telegram: ")
        for k in packet.parsed:
          print('%s: %s' % (k, packet.parsed[k]))
  except queue.Empty:
    continue
  except KeyboardInterrupt:
    break
  except Exception:
    traceback.print_exc(file=sys.stdout)
    break

if communicator.is_alive():
  communicator.stop()
  print("Communicator stoped.")

for k in light_actuators:
  mqttclient.publish("homeassistant/light/enocean/"+light_actuators[k]+"/availability","offline",qos=1,retain=False)
  #mqttclient.publish("homeassistant/light/enocean/"+light_actuators[k]+"/config",'') # uncomment to delete the configuration
for k in rollo_actuators:
  mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators[k]+"/availability","offline",qos=1,retain=False)
  #mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators[k]+"/config",'')
for k in rollo_actuators_v:
  mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators_v[k]+"/availability","offline",qos=1,retain=False)
  #mqttclient.publish("homeassistant/cover/enocean/"+rollo_actuators_v[k]+"/config",'')
for k in contact_sensors:
  mqttclient.publish("homeassistant/binary_sensor/enocean/"+contact_sensors[k]+"/availability","offline",qos=1,retain=False)
  #mqttclient.publish("homeassistant/binary_sensor/enocean/"+contact_sensors[k]+"/config",'')
    
mqttclient.loop_stop() 
print("MQTT loop stoped")
mqttclient.disconnect()
print("MQTT client disconnected")
