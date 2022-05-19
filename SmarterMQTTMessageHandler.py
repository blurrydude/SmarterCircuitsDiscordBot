class MQTTMessageHandler:
    def __init__(self, sdbot):
        self.sdbot = sdbot

    def on_message(self, client, userdata, message):
        topic = message.topic
        data = str(message.payload.decode("utf-8"))
        if "shellies" in topic:
            if "shellyht" in topic:
                self.sdbot.brain.message_queue.append({"channel":self.sdbot.debug_channel, "data":topic+": "+data})
            return
        path = topic.split('/')
        if path[2] == "general":
            channel = self.sdbot.general_channel
        elif path[2] == "debug":
            channel = self.sdbot.debug_channel
        elif path[2] == "house":
            channel = self.sdbot.house_channel
        else:
            channel = int(path[2])
        if "!c" in data:
            data = data.split(" !c ")[1]
        self.sdbot.brain.message_queue.append({"channel":channel, "data":data})