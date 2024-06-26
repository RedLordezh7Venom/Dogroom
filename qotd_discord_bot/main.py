import os, disnake, random, re
import disnake.ext
import discord
from disnake.ext import tasks
import asyncio
from disnake.ext import commands
from dotenv import load_dotenv
from datetime import datetime,timedelta
from pathlib import Path
import aiohttp
import time
import riddle_of_theday
import links 


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


Bot = commands.Bot(
    command_prefix=disnake.ext.commands.when_mentioned,
    activity=disnake.Activity(type=disnake.ActivityType.watching, name="youthoob")
)

#ID of channel where questions are posted
target = 1236401558028292137#1116378200096907264#fill in

#ID of role that gets pinged when posting a question, leave blank string if no role should be pinged
pingrole = "1116378165284196484"

#Hour QOTD is to be posted
posttime = 20#fill in

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
import requests
from bs4 import BeautifulSoup
import random
import re

async def question_post(channel):
    # Send a GET request to the website
    r = requests.get('https://bishalsarang.github.io/Leetcode-Questions/out.html')

    # Parse the HTML content
    soup = BeautifulSoup(r.content, "html.parser")

    # Find all question titles and descriptions
    questions = soup.find_all("div", class_="content__u3I1 question-content__JfgR")

    # Select a random question
    random_question = random.choice(questions)

    # Extract question title
    title = random_question.find_previous_sibling("div", id="title").text.strip()
    title = re.sub(r'^\d+.','',title)

    # Extract question description and remove problematic Unicode characters
    description = random_question.find("div").text.strip()
    description_cleaned = description.replace('\u230a', '')  # Replace problematic Unicode character

    # Construct the problem link
    title_with_hyphens = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
    link_without_number = re.sub(r'^\d+-', '', title_with_hyphens)
    link_without_number = "https://leetcode.com/problems/"+link_without_number

    # Create an embed with the title, description, and link
    embed = disnake.Embed(
        title=title,
        description=description_cleaned,
        colour=embedcolor
    )
    embed.add_field(name="Problem Link", value=link_without_number)
    embed.set_author(name="Today's problem:", icon_url='https://images.playground.com/85f17db5dc3a4b38acc26419711b6c4d.jpeg')
    embed.set_footer(text=f"Daily Question #{datetime.now().date()}")

    # Send the embed to the channel
    if pingrole == "":
        await channel.send(embed=embed)
    else:
        await channel.send(f"<@&{pingrole}>", embed=embed)
    message = channel.last_message
    await message.create_thread(
        name=f"'{title}'",
        auto_archive_duration=60)

    print(f'{Bot.user} has posted a qotd!')


last_posted_date = None
#Scheduled to call question of the day.


@tasks.loop(hours = 1)
async def task():
    global last_posted_date
    current_date = datetime.now().date()
    if datetime.now().hour == posttime and last_posted_date!=current_date:
        channel = Bot.get_channel(target)
        await question_post(channel)
        last_posted_date = current_date

#Make sure bot is online.
@Bot.event
async def on_ready():
    print(f'{Bot.user} has connected to Discord! It is '+ str(datetime.now()))
    await task.start()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Reads for commands, which includes adding questions and testing
        
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


@Bot.slash_command(name="qotd", description="Sends QOTD for testing")
#@commands.has_permissions(send_messages=True)
async def send(inter: disnake.ApplicationCommandInteraction):
    await inter.response.defer()
   
    try:
        channel = Bot.get_channel(target)
        if channel is None :
            raise ValueError(f"Channel with ID{target} not found")
        await question_post(channel)
        
        embed = disnake.Embed(
            title = f"Success!",
            description = f"Sent a QOTD.",
            colour = embedcolor,
        )
        await inter.edit_original_message(embed=embed)
    except Exception as e:
        # Handle any errors and respond appropriately
        error_embed = disnake.Embed(
            title="Error!",
            description=f"An error occurred: {str(e)}",
            color=0xff0000,
        )
        await inter.edit_original_response(embed=error_embed)

@Bot.slash_command(name="riddle", description="Sends daily riddle for testing")
async def send(inter: disnake.ApplicationCommandInteraction):
    await inter.response.defer()
    
    try:
        channel = Bot.get_channel(target)
        if channel is None:
            raise ValueError(f"Channel with ID {target} not found")

        # Assume riddle_of_theday.question_post(channel) is a function that posts the riddle
        await riddle_of_theday.question_post(channel)

        embed = disnake.Embed(
            title="Success!",
            description="Sent a riddle.",
            color=embedcolor,
        )
        
        await inter.edit_original_response(embed=embed)
    except Exception as e:
        # Handle any errors and respond appropriately
        error_embed = disnake.Embed(
            title="Error!",
            description=f"An error occurred: {str(e)}",
            color=0xff0000,
        )
        await inter.edit_original_response(embed=error_embed)

#==================================================================================================Links=======================================================================================
#reduce redundancy with global_options
global_options = links.global_options
from links import handle_insta,handle_twitter,handle_whatsapp,handle_discord,handle_nas,handle_linkedin
# Event listener for select menu interactions
@Bot.event
async def on_dropdown(inter: disnake.MessageInteraction):
    if inter.data.custom_id == "Bot-linkspanel":
        # Get the selected value from the interaction
        value = inter.values[0]
        
        # Call the appropriate handler function based on the selected value
        if value == "twitter-linkspanel":
            await handle_twitter(inter)
        elif value == "insta-linkspanel":
            await handle_insta(inter)
        elif value == "whatsapp-linkspanel":
            await handle_whatsapp(inter)
        elif value == "discord-linkspanel":
            await handle_discord(inter)
        elif value == "nasio-linkspanel":
            await handle_nas(inter)
        elif value == "linkedin-linkspanel":
            await handle_linkedin(inter)


@Bot.slash_command(name="links", description="Get links to the Geek Room community")
async def links(inter: disnake.ApplicationCommandInteraction):
    # Create the select menu options
    options = [
        disnake.SelectOption(
            label="Twitter",
            description="Geek Room's Official Twitter Page",
            emoji="✖️",
            value="twitter-linkspanel"
        ),
        disnake.SelectOption(
            label="Whatsapp Group",
            description="Join Geek Room's Whatsapp",
            emoji="💬",
            value="whatsapp-linkspanel"
        ),
        disnake.SelectOption(
            label="Discord Server",
            description="Join the Official server",
            emoji="🎮",
            value="discord-linkspanel"
        ),
        disnake.SelectOption(
            label="Nas.io Community",
            description="Geek Room's Nas.io community page",
            emoji="🎯",
            value="nasio-linkspanel"
        ),
        disnake.SelectOption(
            label="LinkedIn",
            description="Geek room's Official Linkedin ",
            emoji="ℹ️",
            value="linkedin-linkspanel"
        ),
        disnake.SelectOption(
            label="Instagram",
            description="Geek Room's Official Instagram",
            emoji="📸",
            value="insta-linkspanel"
        )
    ]

    # Create the select menu
    select_menu = disnake.ui.Select(
        placeholder="❌┆Links",
        options=options,
        custom_id="Bot-linkspanel"
    )

    # Create an action row with the select menu
    action_row = disnake.ui.ActionRow(select_menu)

    # Create the embed
    embed = disnake.Embed(
        title="🔗・Links",
        description="Get access to all Geek Room rescources from the menu!",
        color=0x3498db
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/843487478881976381/874694194474668052/Bot_banner_invite.jpg")

    # Send the response with the embed and action row
    await inter.response.send_message(embed=embed, components=[action_row])

    row = disnake.ui.ActionRow(
        disnake.ui.Button(
            label="Bot Invite",
            url="https://google.com",
            style=disnake.ButtonStyle.link
        )
    )

    # Create the embed
    embed = disnake.Embed(
        title="📨・Bot Invite",
        description="Make your server even better with Bot!",
        color=0x3498db
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/843487478881976381/874694194474668052/Bot_banner_invite.jpg")

# @Bot.slash_command(name="link", description="Sends the Geek Room links")
# async def link(inter: disnake.ApplicationCommandInteraction):
#     await inter.response.defer()

#     try:
#         # Create an embed with the link
#         embed = disnake.Embed(
#             title="Links",
#             description="Here are the links to Geek Room's resources",
#             color=0x3498db
#         )
#         embed.add_field(
#             name="Linktree",
#             value="[Geek Room Linktree](https://linktr.ee/geekroom)",
#             inline=False
#         )
#         embed.add_field(
#             name="LinkedIn",
#             value="[Official LinkedIn Page](https://www.linkedin.com/company/geekr00m/)",
#             inline=False
#         )
#         embed.add_field(
#             name="Instagram",
#             value="[Official Instagram Page](https://www.instagram.com/geekr00m/)",
#             inline=False
#         )
#         embed.add_field(
#             name="Twitter",
#             value="[Geek Room Twitter](https://twitter.com/geek__room_)",
#             inline=False
#         )
#         embed.add_field(
#             name="Whatsapp Group",
#             value="[Geek Room Whatsapp](https://chat.whatsapp.com/EPDLVRHU1AM1HQ76NFWIDW)",
#             inline=False
#         )
#         embed.add_field(
#             name="Discord",
#             value="[Official Discord](https://discord.com/invite/7TEVm4pmMv)",
#             inline=False
#         )
#         embed.set_author(name=f"@geekroom",icon_url="https://ugc.production.linktr.ee/2a6c8d7a-a38a-45c4-9e9f-4a14b6c88714_GR-Logo.png?io=true&size=avatar-v3_0")
#         # embed.set_image(url="https://ugc.production.linktr.ee/2a6c8d7a-a38a-45c4-9e9f-4a14b6c88714_GR-Logo.png?io=true&size=avatar-v3_0")
#         embed.set_footer(text="Visit Geek Room for more awesome content!")

#         # Send the embed
#         await inter.edit_original_response(embed=embed)
#     except Exception as e:
#         # Handle any errors and respond appropriately
#         error_embed = disnake.Embed(
#             title="Error!",
#             description=f"An error occurred: {str(e)}",
#             color=0xff0000,
#         )
#         await inter.edit_original_response(embed=error_embed)






#=================================================================================================================================================================================================
@Bot.slash_command(name="say", description="Send a message containing the value")
@commands.has_permissions(kick_members=True)
async def say(inter, channel_id, message):
    channel = Bot.get_channel(int(channel_id))
    await channel.send(message)
    embed = disnake.Embed(
        title = f"Success!",
        description = f"Sent the message.",
        colour = embedcolor,
    )
    await inter.send(embed=embed)

@Bot.slash_command(name="summarise", description="Summarise chat upto a week")
# @commands.has_permissions(kick_members=True)
async def summarise(inter):
    await inter.response.defer()  # Defer the interaction first
    
    channel = inter.channel
    
    # Calculate the start and end dates for the week
    end_date = datetime.now()  # Current local date and time
    start_date = end_date - timedelta(days=7)  # 7 days ago
    
    # Fetch messages within the week
    messages = await channel.history(limit=None, after=start_date, before=end_date).flatten()
    
    summary = ""
    for message in messages:
        if not message.author.bot:
            summary += f"{message.clean_content}\n"
    
    await riddle_of_theday.summarise(channel,summary)
    embed = disnake.Embed(
        title = f"Success!",
        description = f"Summarised text for the time period {start_date} to {end_date}",
        colour = embedcolor,
    )
    await inter.send(embed = embed)
Bot.run(TOKEN)
