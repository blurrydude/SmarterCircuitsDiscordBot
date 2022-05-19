from discord import File

class DiscordUtility:
    def __init__(self, sdbot):
        self.sdbot = sdbot

    async def send(self, channel, message):
        channel = self.sdbot.bot.get_channel(channel)
        await channel.send(message)
    
    async def send_file(self, channel, filename):
        channel = self.sdbot.bot.get_channel(channel)
        await channel.send(file=File(filename))