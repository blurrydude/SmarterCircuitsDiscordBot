# bot.py
import dotenv
import os
from dotenv import load_dotenv
import time
from discord import File
from discord.ext import commands, tasks
import paho.mqtt.client as mqtt
import asyncio
from paramiko import SSHClient
from scp import SCPClient

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GENERAL = os.getenv('GENERAL')
DEBUG = os.getenv('DEBUG')
HOUSE = os.getenv('HOUSE')
 
#client = discord.Client()
ssh = SSHClient()
ssh.load_system_host_keys()
bot = commands.Bot(command_prefix='!')
mc = mqtt.Client()
message_queue = []
 
@tasks.loop(seconds=1)
async def main_loop():
    global message_queue
    rooms = {}
    for d in message_queue:
        if d["room"] not in rooms.keys():
            rooms[d["room"]] = []
        rooms[d["room"]].append(d["data"])
    for key in rooms.keys():
        await send(key, "\n".join(rooms[key]))
    message_queue = []
 
def on_mqtt_message(mclient, userdata, message):
    global client
    global message_queue
    topic = message.topic
    data = str(message.payload.decode("utf-8"))
    if "shellies" in topic:
        if "shellyht" in topic:
            message_queue.append({"room":DEBUG, "data":topic+": "+data})
        return
    path = topic.split('/')
    if path[2] == "general":
        room = GENERAL
    elif path[2] == "debug":
        room = DEBUG
    else:
        room = int(path[2])
    if "!c" in data:
        data = data.split(" !c ")[1]
    message_queue.append({"room":room, "data":data})
 
async def send(room, message):
    channel = bot.get_channel(room)
    await channel.send(message)
 
async def send_file(room, filename):
    channel = bot.get_channel(room)
    await channel.send(file=File(filename))
 
def start_listening():
    global mc
    mc.connect('192.168.2.200')
    mc.subscribe("discord/out/#")
    mc.subscribe("shellies/#")
    mc.loop_start()
 
def publish(topic, message):
    global mc
    mc.publish(topic, message)
   
@bot.command(name='cam')
async def chart(ctx, *args):
    message = ctx.message
    user_id = str(message.author.id)
    author = message.author.display_name
    channel = message.channel
    text = message.content.replace("!cam ","")
    command = text.split(':')
    cam = command[0]
    if len(command) > 1:
        sec = int(command[1])
    else:
        sec = 0
    publish("crittercam/command",text)
    print("sent crittercam command")
    if sec == 0:
        filename = "output_"+cam+".jpg"
        time.sleep(2)
    else:
        filename = "output_"+cam+".avi"
        time.sleep(sec+10)
    print("getting file")

    ssh.connect('192.168.2.57',username='ian',password='Cannibus42')
    with SCPClient(ssh.get_transport()) as scpc:
        scpc.get('/home/ian/'+filename, filename)
    ssh.close()
    await send_file(channel.id, filename)

@bot.command(name='c')
async def chart(ctx, *args):
    message = ctx.message
    user_id = str(message.author.id)
    author = message.author.display_name
    channel = message.channel
    text = message.content
    publish("discord/in/"+str(channel.id)+"/"+author, text)
    if author.lower() != "blurrydude":
        await message.channel.send("You are not the Dude.")
        return

    publish("smarter_circuits/command",str(channel.id)+" bot says "+text)
 
mc.on_message = on_mqtt_message
start_listening()
main_loop.start()
#client.run(TOKEN)
bot.run(TOKEN)
mc.loop_stop()
mc.disconnect()
