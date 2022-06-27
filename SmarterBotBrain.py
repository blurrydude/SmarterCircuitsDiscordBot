class BotBrain:
    def __init__(self, chassis):
        self.chassis = chassis
        self.message_queue = [{"channel":chassis.house_channel, "data":"initialized"}]
    
    async def main_loop(self):
        channels = {}
        for d in self.message_queue:
            if d["channel"] not in channels.keys():
                channels[d["channel"]] = []
            channels[d["channel"]].append(d["data"])
        for key in channels.keys():
            await self.chassis.utility.send(key, "\n".join(channels[key]))
        self.message_queue = []