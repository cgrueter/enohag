#/usr/local/bin/python3.7
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

# Pace your shutter ID and names here
rollo_actors = {'01:75:C9:FE' : 'rollo_nord'}
# or here, if open close is reversed, as the most of mines :-)
rollo_actors_v = {'01:77:30:3A' : 'rollo_west_1',
                  '01:75:BB:76' : 'rollo_west_2',
                  '01:72:60:48' : 'rollo_south_1',
                  '01:72:64:C0' : 'rollo_south_2'}
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
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x35])) #Teached in sender ID for this shutter
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='CLOSE':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x35]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/cover/enocean/rollo_south_1/set":
    if message.payload.decode('UTF-8')=='OPEN':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x30])) #Teached in sender ID for this shutter
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='CLOSE':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x30]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/cover/enocean/rollo_south_2/set":
    if message.payload.decode('UTF-8')=='OPEN':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x34])) #Teached in sender ID for this shutter
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='CLOSE':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x34]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
  if message.topic=="homeassistant/cover/enocean/rollo_nord/set":
    if message.payload.decode('UTF-8')=='OPEN':
      communicator.send(assemble_packet_press_a_1([0xAA, 0xAA, 0xAA, 0x33])) #Teached in sender ID for this shutter
      time.sleep(0.1)
      communicator.send(assemble_packet_release())
    if message.payload.decode('UTF-8')=='CLOSE':
      communicator.send(assemble_packet_press_a_0([0xAA, 0xAA, 0xAA, 0x33]))
      time.sleep(0.1)
      communicator.send(assemble_packet_release())

def connect_messages():
  for k in rollo_actors:
    mqttclient.publish("homeassistant/cover/enocean/"+rollo_actors[k]+"/config",'{"name" : "'+rollo_actors[k]+'", "device_class" : "shutter", "command_topic" : "homeassistant/cover/enocean/'+rollo_actors[k]+'/set", "set_position_topic" : "homeassistant/cover/enocean/'+rollo_actors[k]+'/set_position", "position_topic" : "homeassistant/cover/enocean/'+rollo_actors[k]+'/position", "uniq_id" : "'+k+'", "avty_t" : "homeassistant/cover/enocean/'+rollo_actors[k]+'/availability", "exp_aft" : "600"}', retain=True)
    mqttclient.publish("homeassistant/cover/enocean/"+rollo_actors[k]+"/availability","online",retain=True)
    mqttclient.subscribe([("homeassistant/cover/enocean/"+rollo_actors[k]+"/set", 0), ("homeassistant/cover/enocean/"+rollo_actors[k]+"/set_position", 0)])
  for k in rollo_actors_v:
    mqttclient.publish("homeassistant/cover/enocean/"+rollo_actors_v[k]+"/config",'{"name" : "'+rollo_actors_v[k]+'", "device_class" : "shutter", "command_topic" : "homeassistant/cover/enocean/'+rollo_actors_v[k]+'/set", "set_position_topic" : "homeassistant/cover/enocean/'+rollo_actors_v[k]+'/set_position", "position_topic" : "homeassistant/cover/enocean/'+rollo_actors_v[k]+'/position", "uniq_id" : "'+k+'", "avty_t" : "homeassistant/cover/enocean/'+rollo_actors_v[k]+'/availability", "exp_aft" : "600"}', retain=True)
    mqttclient.publish("homeassistant/cover/enocean/"+rollo_actors_v[k]+"/availability","online",retain=True)
    mqttclient.subscribe([("homeassistant/cover/enocean/"+rollo_actors_v[k]+"/set", 0), ("homeassistant/cover/enocean/"+rollo_actors_v[k]+"/set_position", 0)])

mqtt.Client.connected_flag=False
mqtt.Client.disconnected_flag=True
mqttclient = mqtt.Client(mqttClientId)
mqttclient.on_connect=on_mqtt_connect
mqttclient.on_disconnect=on_mqtt_disconnect
mqttclient.username_pw_set(username=mqttUsername,password=mqttPassword)
mqttclient.connect(mqttBroker)
mqttclient.loop_start()
mqttclient.on_message=on_mqtt_message

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
    # Loop to empty the queue
    packet = communicator.receive.get(block=True, timeout=1)
    if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.VLD:
      packet.select_eep(0x05, 0x00)
      packet.parse_eep()
      if packet.sender_hex in rollo_actors_v:
        #print("*** Got rollo feedback --> :", rollo_actors_v[packet.sender_hex], packet.parsed['POS']['raw_value'])
        mqttclient.publish("homeassistant/cover/enocean/"+rollo_actors_v[packet.sender_hex]+"/position", 100-packet.parsed['POS']['raw_value'],retain=False)
      elif packet.sender_hex in rollo_actors:
        #print("*** Got rollo feedback --> :", rollo_actors[packet.sender_hex], packet.parsed['POS']['raw_value'])
        mqttclient.publish("homeassistant/cover/enocean/"+rollo_actors[packet.sender_hex]+"/position", packet.parsed['POS']['raw_value'],retain=False)
      else:
        print("New unknown VLD telegram: ")
        for k in packet.parsed:
          print('%s: %s' % (k, packet.parsed[k]))
    if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.BS4:
      print("New unknown BS4 telegram: ")
      for k in packet.parse_eep(0x02, 0x05):
        print('%s: %s' % (k, packet.parsed[k]))
    if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.BS1:
      packet.select_eep(0x00, 0x01)
      packet.parse_eep()
      print("New unknown BS1 telegram: ")
      for k in packet.parsed:
        print('%s: %s' % (k, packet.parsed[k]))
    if packet.packet_type == PACKET.RADIO_ERP1 and packet.rorg == RORG.RPS:
      packet.parse_eep(0x02, 0x02)
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

mqttclient.loop_stop() 
print("MQTT loop stoped")
mqttclient.disconnect()
print("MQTT client disconnected")

