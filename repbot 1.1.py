import os
import json
from dotenv import load_dotenv
from discord import Intents, User, Activity, ActivityType
from discord.ext import commands
from random import random, choice
from typing import Final
from operator import itemgetter
from stocks import stocks, investMeow
from asyncio import sleep

# loading token
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# setting up the bot
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=["!", "+", "-"], intents=intents)

# code used to create original json save file
# REPUTATION = {310405592474845185: 0, 361967504777674752: 21, 213672636994027520: 10, 344939378826805248: 9, 199222232809996288: 6, 272392801151352835: 5, 425804085833498629: 5, 877653175912501311: 2, 1231140122821656617: 11, 402079431855833088: 2, 465225450025779222: 2, 1202655669140852887: 86, 211211805186457600: 1, 484095791821225986: 0, 344226645378596866: 1, 318097015760355328: 1, 701559469737246773: -2, 502938379764105221: 1, 287845050296303617: -4, 432585437195010060: 3, 384443070592319488: -1, 518112885277458462: 0, 500639282373853205: 0, 234234699072012290: 3, 484396357143101468: 0, 529447916125945856: 0, 431891878527369226: 1, 381801176645238785: -2, 255374576542810112: 3, 207270432938786817: 2, 343822001351426048: 1, 671763197845569550: 1, 399197605055168524: 1}
# ADMINS = [325638960959193110, 287845050296303617]
# BLACKLIST = []
# PREVIOUS = [10, 20]

# globals
with open("reputations.json", "r") as json_file:
    DATA = json.load(json_file)
REPUTATION = DATA[0]
ADMINS = DATA[1]
BLACKLIST = DATA[2] 
PREVIOUS = DATA[3]

'''
For some reason when you store a dictionary in json it converts all the number keys to strings 💀
so here i am converting them back so can handle the ids directly without having to change their type
'''
for key in list(REPUTATION.keys()):
    REPUTATION[int(key)] = REPUTATION[key]
    del REPUTATION[key]
for i in range(0, len(ADMINS)):
    ADMINS[i] = int(ADMINS[i])
for i in range(0, len(BLACKLIST)):
    BLACKLIST[i] = int(BLACKLIST[i])
for i in range(0, 2):
    PREVIOUS[i] = int(PREVIOUS[i])

DATA = [REPUTATION, ADMINS, BLACKLIST, PREVIOUS]

# checks if the user has negative or positive rep returns corresponding symbol
def getSymbol(user: User):
    if REPUTATION[user.id] < 0:
        symbol = "-"
    else:
        symbol = "+"

    return symbol

# checks if the bot has a rep entry
def createBotEntry():
    if bot.user.id not in REPUTATION.keys():
        REPUTATION[bot.user.id] = 0

# starting up the bot
@bot.event
async def on_ready() -> None:
    print(f"{bot.user} in now online")
    createBotEntry()

    # Activity
    activity = Activity(name="meowing", state="meow", type=ActivityType.playing)

    await bot.change_presence(activity=activity)

# Handles Errors: helpful for debugging
@bot.event
async def on_command_error(ctx, error):

    # Handles MissingRequiredArgument error
    if isinstance(error, commands.MissingRequiredArgument):
        # await ctx.send("You fucking idiot")
        # await ctx.send(f"-# Missing argument: {error.param.name}")
        return

    # Handles "false" commands
    elif isinstance(error, commands.CommandNotFound):
        # await ctx.send("idk that command you stinker")
        return
    
    # Handles BadArgument error
    elif isinstance(error, commands.BadArgument):
        # await ctx.send("You fucking idiot")
        # await ctx.send(f"-# error: BadArgument")
        return
    
    # Handle any other errors that might occur
    else:
        await ctx.send("You fucking idiot")
        await ctx.send(f"-# {error}")
        return

@bot.command(description="Invest your rep into the stock system")
async def invest(ctx, amount=1, investmentPeriod=3):
    await ctx.send("-# ⚠ This command is WIP, functionality may change! ⚠ You will not CURRENTLY recieve rep for your investments")

      # hehe heart below vvv
    # if (investmentPeriod <3) or (investmentPeriod > 20):
    #     await ctx.send("Please invest for between 3 and 20 games (inclusive)")
    #     return

    miau = "Loading"
    meow = await ctx.send(miau)

    for i in range(3):
        miau += ". "
        await meow.edit(content=miau)
        await sleep(1)
    
    # investmentMeow = investMeow(amount=amount, lifespan=investmentPeriod, age=0, discordID=ctx.author.id)
    # yeah honestly I got no clue what I'm doing I was just doing things head first but I'm gonna have to stop and think and plan this one

    investResults = stocks(amount=amount,investLength=investmentPeriod)
    await meow.delete()
    investment = amount
    
    amount += investResults[0]
    wins = investResults[1]
    await ctx.send(f"{wins} wins out of {investmentPeriod}")
    await ctx.send(f"**{investment} --> {amount:.2f} rep**")

# rep commands
@bot.command(description="+/- rep from people")
async def rep(ctx, user:User=None):
    if user == None:
        user = ctx.author

    # check argument is valid
    if user.id not in REPUTATION.keys():
        REPUTATION[user.id] = 0

    # find prefix used
    if ctx.prefix == "!":
        symbol = getSymbol(user)
        await ctx.send(f"{user.name} is on **{symbol}rep {abs(REPUTATION[user.id])}**")
        return

    if ctx.author.id in BLACKLIST:
        await ctx.message.delete()
        monkey = await ctx.send(f"shut up {ctx.author.name}")
        await monkey.delete(delay=2)
        return

    # check the user is valid
    if user == ctx.author:
        await ctx.send("nice try 🤡")
        return 

    # checking the user has not used rep more than twice in a row
    if (ctx.author.id == PREVIOUS[0] and ctx.author.id == PREVIOUS[1]) and (ctx.author.id not in ADMINS):
        await ctx.send("Stop spamming this command you silly goose")
        return

    # changing value for user
    if ctx.prefix == "+":
        REPUTATION[user.id] += 1
    else:
        REPUTATION[user.id] -= 1

    PREVIOUS[1] = PREVIOUS[0]
    PREVIOUS[0] = ctx.author.id

    symbol = getSymbol(user)
    await ctx.send(f"{user.name} is now on **{symbol}rep {abs(REPUTATION[user.id])}**")

    # Saving the object to a JSON file
    with open("reputations.json", "w") as json_file:
        json.dump(DATA, json_file)

# setRep
@bot.command(name="setrep",hidden=True)
async def setRep(ctx, user: User, amount: int):
    # checking if user has perms
    if ctx.author.id not in ADMINS:
        await ctx.send("SHUT UP BOZO")
        return

    REPUTATION[user.id] = amount

    symbol = getSymbol(user)
    await ctx.send(f"{user.name} is now on **{symbol}rep {abs(REPUTATION[user.id])}**")

    # Saving the object to a JSON file
    with open("reputations.json", "w") as json_file:
        json.dump(DATA, json_file)


# gambles user rep with a 49% win chance
@bot.command(name="gamble",description="Gamble your rep... gl ;)")
async def gambleRep(ctx, amount=None):

    # checking if user gambled all
    if amount.lower() == "all":
        amount = REPUTATION[ctx.author.id]
    
    try:
        amount = int(amount)
    except Exception:
        await ctx.send("you're not funny or smart")
        return
    
    # checking is user entered value
    if (amount == None) or (int(amount) <=0):
        await ctx.send("You cannot gamble nothing fool")
        return

    # checking if user in rep
    if ctx.author.id not in REPUTATION.keys():
        REPUTATION[ctx.author.id] = 0

    # checking if viable gamble
    if (REPUTATION[ctx.author.id] < 1  or REPUTATION[ctx.author.id] < amount):
        await ctx.send("You don't got that much rep punk!")
        return
    
    # win
    if random() <= 0.49:
        REPUTATION[ctx.author.id] += amount
        REPUTATION[bot.user.id] -= amount
        await ctx.send("You win :D")
    # lose
    else:
        REPUTATION[ctx.author.id] -= amount
        REPUTATION[bot.user.id] += amount
        await ctx.send("you lose")
    await ctx.send(f"-# You now have {REPUTATION[ctx.author.id]} rep")

    # Saving the object to a JSON file
    with open("reputations.json", "w") as json_file:
        json.dump(DATA, json_file)


# # gambleSlots
# @bot.command(name="slots")
# async def gambleSlots(ctx):
#     await ctx.send("-# note: the random function is TERRIBLE")

#     # checking if the user has enough rep
#     if REPUTATION[ctx.author.id] < 1:
#         await ctx.send("brokies can't gamble")

#     emojis = ["😼","🎁","🤓","🤑","😎"]
#     slots = ""
#     for i in range(3):
#         slots += choice(emojis)
#     await ctx.send(slots)

#     # cost of playing
#     REPUTATION[ctx.author.id] -= 1

#     # jackpot
#     if slots[0] == slots[1] == slots[2]: # NOTE: 1 in 4^3 = 1/64
#         REPUTATION[ctx.author.id] += 5
#         await ctx.send("JACKPOT")
#     # small win
#     elif (slots[0] == slots[1]) or (slots[1] == slots[2]): # NOTE: 1 in 2*(4^2)*(3/4) = 1/24
#         REPUTATION[ctx.author.id] += 2
#         await ctx.send("SMALL WIN")
#     await ctx.send(f"You now have {REPUTATION[ctx.author.id]} rep")
    
#     # 1/64 + 1/24 = 11/192 = 5.73/100 chance of winning

#     # Saving the object to a JSON file
#     with open("reputations.json", "w") as json_file:
#         json.dump(DATA, json_file)


@bot.command(hidden=True)
async def admin(ctx, user: User=None):
    # check user who sent message has perms
    if ctx.author.id not in ADMINS:
        await ctx.send("shut up filth")
        return
    
    # checks current admins
    if ctx.prefix == "!":
        await ctx.send(f"here are the current admins: {ADMINS}")
        return

    # checking they have specified a user for + and - commands
    if user == None:
        await ctx.send("You must specify a user")
        return
    
    # adds or removed admin based on prefix used
    if ctx.prefix == "+":
        # checks if user is already in ADMIN
        if user.id in ADMINS:
            await ctx.send(f"{user.name} is already in the admin list")
            return

        ADMINS.append(user.id)
        await ctx.send(f"{user.name} has been added to the admin list")
    else:
        # checks if the user is in the list to remove
        if user.id not in ADMINS:
            await ctx.send(f"{user.name} is not an admin")
            return
        
        ADMINS.remove(user.id)
        await ctx.send(f"{user.name} has been removed from the admin list")

    # Saving the object to a JSON file
    with open("reputations.json", "w") as json_file:
        json.dump(DATA, json_file)

@bot.command(hidden = True) 
async def servers(ctx):
    if ctx.author.id in ADMINS:
        servers = list(bot.guilds)
        meow = f"Connected on {str(len(servers))} servers:\n"
        for i in range(len(servers)):
            meow += f"{servers[i].name}\n"
        await ctx.channel.send(meow)
    else:
        await ctx.send("shut up filth")

@bot.command(hidden=True)
async def blacklist(ctx, user: User=None):
    # check if user has perms
    if ctx.author.id not in ADMINS:
        await ctx.send("shut up filth")
        return
    
    # checks current blacklist
    if ctx.prefix == "!":
        await ctx.send(f"Here is the currnet blacklist: {BLACKLIST}")
        return

    # checks user has specified a user for + or - command   
    if user == None:
        await ctx.send("You must specify a user")
        return

    # adds or removed user based on prefix used
    if ctx.prefix == "+":
        # checks if user is already in BLACKLIST
        if user.id in BLACKLIST:
            await ctx.send(f"{user.name} is already in the blacklist")
            return

        BLACKLIST.append(user.id)
        await ctx.send(f"{user.name} has been added to the blacklist")
    else:
        # checks if the user is in the list to remove
        if user.id not in BLACKLIST:
            await ctx.send(f"{user.name} is not in the blacklist")
            return
        
        BLACKLIST.remove(user.id)
        await ctx.send(f"{user.name} has been removed from the blacklist")
    
    # Saving the object to a JSON file
    with open("reputations.json", "w") as json_file:
        json.dump(DATA, json_file)

@bot.command()
async def leaderboard(ctx):
    # getting the current dictionary
    data = []
    for key, value in REPUTATION.items():
        if key != 1202655669140852887:
            data.append([key, value])
    
    # sorting the users based on rep
    sorted_data = sorted(data, key=itemgetter(1), reverse=True)

    # getting the top three users
    output = ""
    for i in range(0, 3):
        user = await bot.fetch_user(sorted_data[i][0])
        output += f"{i}. {user.name}    {sorted_data[i][1]} \n"
    output += "... \n"
    
    # edge case where user is not in rep
    if ctx.author.id not in REPUTATION.keys():
        sender_index = 1

    # find where the user that sent the message is
    for i in range(0, len(sorted_data)):
        if ctx.author.id == sorted_data[i][0]:
            sender_index = i
    
    # edge case where user is in the top three or bottom
    if sender_index < 3 or sender_index == len(sorted_data)-1:
        user = await bot.fetch_user(sorted_data[-1][0])
        output += f"{len(sorted_data)}. {user.name}    {sorted_data[-1][1]}"
        await ctx.send(output)
        return

    # add the user to the output
    user = await bot.fetch_user(sorted_data[sender_index][0])
    output += f"{sender_index+1}. {user.name}    {sorted_data[sender_index][1]}\n"
    output += "... \n"

    # adding last ranked user
    user = await bot.fetch_user(sorted_data[-1][0])
    output += f"{len(sorted_data)}. {user.name}    {sorted_data[-1][1]}"
    # print(output)
    await ctx.send(output)


'''
LEGACY COMMANDS
'''

# hello
@bot.command(name='hello')
async def hello(ctx):
    global lastHello
    try:
        lastHello
    except NameError:
        lastHello = 502938379764105221

    user_id = ctx.author.id
    strUser = str(user_id)
    if user_id == lastHello:
        await ctx.send("https://tenor.com/view/mewing-gif-11339234860235694668")
    else: 
        await ctx.send('Hello <@' + strUser + ">")
    lastHello = user_id

'''
Old command names
'''

@bot.command(hidden=True)
async def gamblerep(ctx):
    await ctx.send("Try `!gamble` instead")

@bot.command(hidden=True)
async def minusrep(ctx):
    await ctx.send("Try `-rep` instead")

@bot.command(hidden=True)
async def plusrep(ctx):
    await ctx.send("Try `+rep` instead")

@bot.command(hidden=True)
async def queryrep(ctx):
    await ctx.send("Try `!rep` instead")



# entry point
def main() -> None:
    bot.run(token=TOKEN)

if __name__ == "__main__":
    main()  
