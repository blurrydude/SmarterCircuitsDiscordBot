import time
from scp import SCPClient

class BotCommands:
    def __init__(self, chassis):
        self.chassis = chassis
    
    async def cam(self, ctx):
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
        self.chassis.mqtt.publish("crittercam/command",text)
        print("sent crittercam command")
        if sec == 0:
            filename = "output_"+cam+".jpg"
            time.sleep(2)
        else:
            filename = "output_"+cam+".avi"
            time.sleep(sec+10)
        print("getting file")

        self.chassis.ssh.connect(self.cam_ssh_host,username=self.cam_ssh_user,password=self.cam_ssh_pass)
        with SCPClient(self.chassis.ssh.get_transport()) as scpc:
            scpc.get('/home/'+self.cam_ssh_user+'/'+filename, filename)
        self.chassis.ssh.close()
        await self.chassis.utility.send_file(channel.id, filename)
    
    async def command(self, ctx):
        message = ctx.message
        user_id = str(message.author.id)
        author = message.author.display_name
        channel = message.channel
        text = message.content
        self.chassis.mqtt.publish("discord/in/"+str(channel.id)+"/"+author, text)
        if author.lower() != "blurrydude":
            await message.channel.send("You are not the Dude.")
            return

        self.chassis.mqtt.publish("smarter_circuits/command",str(channel.id)+" bot says "+text)