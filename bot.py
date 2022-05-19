# bot.py
import os
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
CRITTERCAM_SSH_USER = os.getenv('CRITTERCAM_SSH_USER')
CRITTERCAM_SSH_PASS = os.getenv('CRITTERCAM_SSH_PASS')
CRITTERCAM_SSH_HOST = os.getenv('CRITTERCAM_SSH_HOST')

BOT = commands.Bot(command_prefix='!')

class SmarterDiscordBot:
    def __init__(self, bot, token, cam_ssh_user, cam_ssh_pass, cam_ssh_host, general_channel, debug_channel, house_channel):
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

        self.utility = DiscordUtility(self)
        self.mqtt_handler = MQTTMessageHandler(self)
        self.brain = BotBrain(self)
        self.bot_commands = BotCommands(self)

        self.mqtt.on_message = self.mqtt_handler.on_message

        self.start_mqtt()
        self.start_bot(token)
 
    def start_mqtt(self):
        self.mqtt.connect('192.168.2.200')
        self.mqtt.subscribe("discord/out/#")
        self.mqtt.subscribe("shellies/#")
        self.mqtt.loop_start()
    
    def start_bot(self, token):
        self.main_loop.start()
        self.bot.run(token)
        # this happens when the bot stops
        self.mqtt.loop_stop()
        self.mqtt.disconnect()
    
    @tasks.loop(seconds=1)
    async def main_loop(self):
        await self.brain.main_loop()
    
    @BOT.command(name='cam')
    async def cam(self, ctx, *args):
        await self.bot_commands.cam(ctx)

    @BOT.command(name='c')
    async def command(self, ctx, *args):
        await self.bot_commands.command(ctx)

if __name__ == "__main__":
    sdbot = SmarterDiscordBot(BOT,TOKEN,CRITTERCAM_SSH_USER,CRITTERCAM_SSH_PASS,CRITTERCAM_SSH_HOST,GENERAL,DEBUG,HOUSE)
