from discord import File

class DiscordUtility:
    def __init__(self, sdbot):
        self.sdbot = sdbot

    async def send(self, channel, message):
        try:
            channel = self.sdbot.bot.get_channel(channel)
            await channel.send(message)
        except:
            print("failed to send")
    
    async def send_file(self, channel, filename):
        try:
            channel = self.sdbot.bot.get_channel(channel)
            await channel.send(file=File(filename))
        except:
            print("failed to send file")