import os

import discord
import logging
from dotenv import load_dotenv
import urllib
import requests
import img_analysis

logging.basicConfig(level=logging.INFO)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)
client = discord.Client()

filepath = "~/Desktop/Bot_MK_I"

# Bot commands
def command(cmd):
	cmd_arr = cmd.split()

	if cmd_arr[0] == "hello":
		return 'Hello!'
	elif cmd_arr[0] == "add":
		try:
			return 'Answer is ' + str(float(cmd_arr[1]) + float(cmd_arr[2]))
		except:
			return 'Must add two numbers'
	elif cmd_arr[0] == "subtract":
		try:
			return 'Answer is ' + str(float(cmd_arr[1]) - float(cmd_arr[2]))
		except:
			return 'Must add two numbers'
	elif cmd_arr[0] == "multiply":
		try:
			return 'Answer is ' + str(float(cmd_arr[1]) * float(cmd_arr[2]))
		except:
			return 'Must add two numbers'
	elif cmd_arr[0] == "divide":
		try:
			if float(cmd_arr[2]) == 0.0:
				return 'Cannot divide by zero'
			return 'Answer is ' + str(float(cmd_arr[1]) / float(cmd_arr[2]))
		except:
			return 'Must add two numbers'

	else: 
		return 'Invalid or no command detected'
		
# End bot commands

def smoke(image_name): 
    return img_analysis.smoke(image_name)

def invert(image_name):
    return img_analysis.invert(image_name)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$invert'):
        image_name = message.content.split()[1]
        image_url = message.attachments[0].url

        r = requests.get(image_url, stream=True)
        with open(image_name, 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)

        ret_img_name = invert(image_name)
        await message.channel.send(file = discord.File(ret_img_name))
    if message.content.startswith('$analyze'):
        image_name = message.content.split()[1]
        # await message.channel.send(image_name)
        image_url = message.attachments[0].url

        r = requests.get(image_url, stream=True)
        with open(image_name, 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)

        ret_img_name = analyze(image_name)
        # await message.channel.send(ret_img_name)
        # await message.channel.send(type(ret_img_name))
        # await message.channel.send(type("bind_analyzed.png"))
        # f = discord.File(filepath = filepath, filename = "bind_analyzed.png")
        # e = discord.Embed()
        await message.channel.send(file = discord.File(ret_img_name))
        # await message.channel.send(file = discord.File("bind_analyzed.png"))

    elif message.content.startswith('$show_map'):
        map_name = message.content.split()[1]
        await message.channel.send(file = discord.File(map_name + ".jpg"))
    elif message.content.startswith('$'):
        output_msg = command(message.content[1:])
        await message.channel.send(output_msg)
        

client.run(TOKEN)