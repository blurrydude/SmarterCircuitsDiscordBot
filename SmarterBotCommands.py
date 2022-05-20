import time
from scp import SCPClient

class BotCommands:
    def __init__(self, chassis):
        self.chassis = chassis
    
    def status(self):
        self.chassis.mqtt.publish("smarter_circuits/command","show status")
    
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
            time.sleep(10)
        else:
            filename = "output_"+cam+".avi"
            time.sleep(sec+30)
        print("getting file")

        self.chassis.ssh.connect(self.chassis.cam_ssh_host,username=self.chassis.cam_ssh_user,password=self.chassis.cam_ssh_pass)
        with SCPClient(self.chassis.ssh.get_transport()) as scpc:
            scpc.get('/home/'+self.chassis.cam_ssh_user+'/'+filename, filename)
        self.chassis.ssh.close()
        await self.chassis.utility.send_file(channel.id, filename)
    
    async def toggle(self, ctx):
        message = ctx.message
        user_id = str(message.author.id)
        author = message.author.display_name
        channel = message.channel
        text = message.content
        self.chassis.mqtt.publish("discord/in/"+str(channel.id)+"/"+author, text)
        if self.chassis.is_admin(str(user_id)) is False:
            await ctx.send("You're not an admin.")
            return

        self.chassis.mqtt.publish("smarter_circuits/command","toggle "+text)
    
    async def command(self, ctx):
        message = ctx.message
        user_id = str(message.author.id)
        author = message.author.display_name
        channel = message.channel
        text = message.content
        self.chassis.mqtt.publish("discord/in/"+str(channel.id)+"/"+author, text)
        if self.chassis.is_admin(str(user_id)) is False:
            await ctx.send("You're not an admin.")
            return

        self.chassis.mqtt.publish("smarter_circuits/command",str(channel.id)+" bot says "+text)