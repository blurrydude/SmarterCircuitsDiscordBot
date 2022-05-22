# bot.py
import os
import time
import subprocess
from dotenv import load_dotenv
from discord.ext import commands, tasks
import paho.mqtt.client as mqtt
from paramiko import SSHClient
from SmarterBotBrain import BotBrain
from SmarterBotCommands import BotCommands
from SmarterDiscordUtility import DiscordUtility
from SmarterMQTTMessageHandler import MQTTMessageHandler

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GENERAL = os.getenv('GENERAL')
DEBUG = os.getenv('DEBUG')
HOUSE = os.getenv('HOUSE')
ADMINS = os.getenv('ADMIN')
CRITTERCAM_SSH_USER = os.getenv('CRITTERCAM_SSH_USER')
CRITTERCAM_SSH_PASS = os.getenv('CRITTERCAM_SSH_PASS')
CRITTERCAM_SSH_HOST = os.getenv('CRITTERCAM_SSH_HOST')

BOT = commands.Bot(command_prefix='!')

sdbot = None

class SmarterDiscordBot:
    def __init__(self, bot, cam_ssh_user, cam_ssh_pass, cam_ssh_host, general_channel, debug_channel, house_channel, admins):
        self.bot = bot
        self.cam_ssh_user = cam_ssh_user
        self.cam_ssh_pass = cam_ssh_pass
        self.cam_ssh_host = cam_ssh_host
        self.mqtt = mqtt.Client()
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.general_channel = general_channel
        self.debug_channel = debug_channel
        self.house_channel = house_channel
        self.admins = admins.split(',')
        self.utility = DiscordUtility(self)
        self.mqtt_handler = MQTTMessageHandler(self)
        self.brain = BotBrain(self)
        self.bot_commands = BotCommands(self)

        self.mqtt.on_message = self.mqtt_handler.on_message

        self.start_mqtt()

    def start_mqtt(self):
        self.mqtt.connect('192.168.2.200')
        self.mqtt.subscribe("discord/out/#")
        self.mqtt.loop_start()
    
    def stop(self):
        self.mqtt.loop_stop()
        self.mqtt.disconnect()
    
    def is_admin(self, user_id):
        return user_id in self.admins

@tasks.loop(seconds=1)
async def main_loop():
    await sdbot.brain.main_loop()

@BOT.command(name='status', help="sends the Smarter Circtuis system status to the House channel")
async def status(ctx, *args):
    sdbot.bot_commands.status()

@BOT.command(name='cam', help="takes a picture by camera number (0-2) take or video by cameranumber and duration (0-2:secs)")
async def cam(ctx, *args):
    await sdbot.bot_commands.cam(ctx)

@BOT.command(name='c', help="issues a command to the Smarter Circuits system - admin only")
async def command(ctx, *args):
    await sdbot.bot_commands.command(ctx)

@BOT.command(name='t', help="toggles a circuit by name - admin only")
async def toggle(ctx, *args):
    await sdbot.bot_commands.toggle(ctx)

@BOT.command(name='temp', help="sets the mid-range temperature of the house - admin only")
async def set_temp(ctx, *args):
    await sdbot.bot_commands.set_temp(ctx)

@BOT.command(name='restart', help='restarts a raspberry pi by last octet of IP - admin only')
async def execute(ctx, *args):
    await sdbot.bot_commands.restart(ctx)
    # if sdbot.is_admin(str(ctx.message.author.id)) is False:
    #     await ctx.send("You're not an admin.")
    #     return
    # try:
    #     host = "192.168.2"+ctx.message.content.replace("!restart ","")
    #     ssh = SSHClient()
    #     ssh.connect(host, username='pi', password=CRITTERCAM_SSH_PASS)
    #     ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('sudo reboot now')
    #     await ctx.send(ssh_stdout)
    # except Exception as err:
    #     await ctx.send("restart failed\n"+err.with_traceback)

@BOT.command(name='u', help='update bot course code and restart - admin only')
async def update(ctx):
    if sdbot.is_admin(str(ctx.message.author.id)) is False:
        await ctx.send("You're not an admin.")
        return
    await ctx.send("Getting source changes.")
    result = subprocess.check_output(["git", "pull"]).decode("utf-8")
    await ctx.send(result)
    time.sleep(10)
    await ctx.send("I am restarting for updates.")
    subprocess.call(["python3", "bot.py"])
    try:
        main_loop.stop()
    except:
        pass
    try:
        BOT.close()
    except:
        pass
    exit()

if __name__ == "__main__":
    sdbot = SmarterDiscordBot(BOT,CRITTERCAM_SSH_USER,CRITTERCAM_SSH_PASS,CRITTERCAM_SSH_HOST,GENERAL,DEBUG,HOUSE,ADMINS)
    main_loop.start()
    BOT.run(TOKEN)
    sdbot.stop()