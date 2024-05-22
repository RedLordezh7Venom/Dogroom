import os, disnake, random, re
import disnake.ext
import discord
from discord.ext import commands
import google.generativeai as genai
from disnake.ext import tasks
import asyncio
from disnake.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import aiohttp
import time

#using gemini



load_dotenv()
TOKEN = os.environ.get('TOKEN')
GOOGLE_AI_KEY = os.envirion.get('GOOGLE_AI_KEY')
MAX_HISTORY  = 10
message_history = {}

# Configure the generative AI model-----------------------------------------------------------------------------------------------------------------------------------------------------------
genai.configure(api_key=GOOGLE_AI_KEY)
text_generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 512,
}
image_generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 512,
}
safety_settings = [{
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
}, {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
}, {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
}, {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
}]
text_model = genai.GenerativeModel(model_name="gemini-pro",
                                   generation_config=text_generation_config,
                                   safety_settings=safety_settings)
image_model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                    generation_config=image_generation_config,
                                    safety_settings=safety_settings)
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Bot = commands.Bot(
    command_prefix=disnake.ext.commands.when_mentioned,
    activity=disnake.Activity(type=disnake.ActivityType.watching, name="dogroom fetcher")
)


#ID of channel where questions are posted
target = 1116378200096907264#fill in
target2 = 1116378196678545430

#ID of role that gets pinged when posting a question, leave blank string if no role should be pinged
pingrole = "1116378165284196484"

#Hour QOTD is to be posted
posttime = 16#fill in

embedcolor = disnake.Colour.green()

errorembedcolor = disnake.Colour.red()

questionsfile = Path(__file__).with_name('questions.txt')
linksfile = Path(__file__).with_name('questionlins.txt')
tempfile = Path(__file__).with_name('temp.txt')

#Adds a question to the text file when called.
def question_add(question):
    with open(questionsfile, 'a') as questions:
        questions.write(question+'\n')

def remove_question(qotd):
    with open (questionsfile, "r") as input:
        with open (tempfile, "w") as output:
            for line in input:
                if line.strip("\n") != qotd:
                    output.write(line)
    os.replace(tempfile, questionsfile)
progress = 0
#Posts question of the day when called.
async def question_post(channel):
      # Ignore messages sent by the bot
    cleaned_text = "send a daily riddle on either of the following topics  : DSA, AI , Machine learning, web development, coding , cyber security, programming history, robotics do not give answer only question the title should be \"Daily riddle\":"


    response_text = await generate_response_with_text(cleaned_text)
    #add AI response to history
    await split_and_send_messages(channel, response_text, 1700)
    return


async def generate_response_with_text(message_text):
  prompt_parts = [message_text]
  print("Got textPrompt: " + message_text)
  response = text_model.generate_content(prompt_parts)
  if (response._error):
    return "❌" + str(response._error)
  return response.text

async def split_and_send_messages(channel, text, max_length):

  # Split the string into parts
  messages = []
  for i in range(0, len(text), max_length):
    sub_message = text[i:i + max_length]
    messages.append(sub_message)

  # Send each part as a separate message
  for string in messages:
    await channel.send(string)


last_posted_date = None
#Scheduled to call question of the day.

 

@tasks.loop(hours = 1)
async def task():
    global last_posted_date
    current_date = datetime.now().date()
    if datetime.now().hour == posttime and last_posted_date!=current_date:
        channel = Bot.get_channel(target2)
        await question_post(channel)
        last_posted_date = current_date


#Make sure bot is online.
@Bot.event
async def on_ready():
    print(f'{Bot.user} has connected to Discord! It is '+ str(datetime.now()))
    await task.start()

#Reads for commands, which includes adding questions and testing
     
@Bot.slash_command(name="riddle", description="Sends riddle for testing")
# @commands.has_permissions(send_messages=True)
async def send(inter):
    channel = Bot.get_channel(target)
    await question_post(channel)
    embed = disnake.Embed(
        title = f"Success!",
        description = f"Sent a daily riddle.",
        colour = embedcolor,
    )
    await inter.send(embed=embed)


@Bot.slash_command(name="add", description="Add a QOTD to the list")
async def add(inter, question):
    embed = disnake.Embed(
        title = f"Added QOTD! Thank you for submitting.",
        description = f"'{question}'",
        colour = embedcolor,
    )
    await inter.send(embed=embed)
    question_add(question)
    print(f'{inter.author} has added "{question}"!')

if __name__ == '__main__':
   Bot.run(TOKEN)

















































    # with open(linksfile,'r') as links:
    #     llines = links.read().splitlines()
    # with open(questionsfile, 'r') as questions:
    #     qlines = questions.read().splitlines()
    #     try:
    #         random_index = random.randint(0, len(qlines) - 1)
    #         qotd = qlines[random_index]
    #         qlink = llines[random_index]

    #         embed = disnake.Embed(
    #             title=f"{qotd}\nProblem Link: {qlink}",
    #             description=f"Post your answers in the Thread down below!",
    #             colour=embedcolor,
    #         )
    #         global progress
    #         embed.set_author(name="Today's problem:", icon_url='https://images.playground.com/85f17db5dc3a4b38acc26419711b6c4d.jpeg')
    #         embed.set_footer(text=f"Daily Question #{datetime.now().date()}")
    #         progress += 1
            
    #         if pingrole == "":
    #             await channel.send(embed=embed)
    #         else:
    #             await channel.send(f"<@&{pingrole}>", embed=embed)
            
    #         message = channel.last_message
    #         await message.create_thread(
    #             name=f"'{qotd}'",
    #             auto_archive_duration=1440,
    #         )
        
            
    #     except Exception as e:
    #         print(f"Error posting question: {e}")
    #         embed = disnake.Embed(
    #             title="QOTD: No questions left.",
    #             description="Everyone submit one, using **/add**!\nInstead, here's a cat.",
    #             colour=errorembedcolor,
    #         )
    #         async with aiohttp.ClientSession() as session:
    #             request = await session.get('https://some-random-api.ml/animal/cat')
    #             cat = await request.json()
    #         embed.set_image(url=cat["image"])
    #         await channel.send(embed=embed)
    # print(f'{Bot.user} has posted a qotd!')
