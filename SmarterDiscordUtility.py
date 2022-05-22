import traceback
from discord import File

class DiscordUtility:
    def __init__(self, sdbot):
        self.sdbot = sdbot

    async def send(self, channel, message):
        try:
            channel = self.sdbot.bot.get_channel(channel)
            await channel.send(message)
        except Exception as e: 
            error = str(e)
            tb = traceback.format_exc()
            print("failed to send to "+str(channel))
            print(error)
            print(tb)
        except:
            print("failed to send to "+str(channel))
    
    async def send_file(self, channel, filename):
        try:
            channel = self.sdbot.bot.get_channel(channel)
            await channel.send(file=File(filename))
        except:
            print("failed to send file to "+str(channel))