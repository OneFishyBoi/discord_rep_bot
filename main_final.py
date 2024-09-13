from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, User
from discord.ext import commands
from random import random, choice
import json
from operator import itemgetter

'''
TODO:
- make it work

'''

# loading token
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# setting up the bot
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=["!", "+", "-"], intents=intents)

# code used to create original json save file
# REPUTATION = {310405592474845185: 0, 361967504777674752: 19, 213672636994027520: 9, 344939378826805248: 9, 199222232809996288: 6, 272392801151352835: 5, 425804085833498629: 5, 877653175912501311: 2, 1231140122821656617: 11, 402079431855833088: 2, 465225450025779222: 2, 1202655669140852887: 85, 211211805186457600: 1, 484095791821225986: 0, 344226645378596866: 1, 318097015760355328: 1, 701559469737246773: -4, 502938379764105221: 0, 287845050296303617: -5, 432585437195010060: 3, 384443070592319488: -1, 518112885277458462: 0, 500639282373853205: 0, 234234699072012290: 3, 484396357143101468: 1, 529447916125945856: 0, 431891878527369226: 1, 381801176645238785: -2, 255374576542810112: 3, 207270432938786817: 1, 343822001351426048: 1, 671763197845569550: 1}
# ADMINS = [325638960959193110]
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
    print(f"{bot.user} in now running")
    createBotEntry()

# rep commands
@bot.command()
async def rep(ctx, user:User=None):
    if user == None:
        user = ctx.author

    # check argument is valid
    if user.id not in REPUTATION.keys():
        REPUTATION[user.id] = 0

    # find prefix used
    if ctx.prefix == "!":
        symbol = getSymbol(user)
        await ctx.send(f"{user.name} is on {symbol}REP {abs(REPUTATION[user.id])}")
        return

    if ctx.author.id in BLACKLIST:
        await ctx.send("YOU HAVE BEEN BANNED")
        return
    
    # check the user is valid
    if user == ctx.author:
        await ctx.send("You can't give yourself (please specify who you would like to give rep)")
        return 
    
    # checking the user has not used rep more than twice in a row
    if ctx.author.id == PREVIOUS[0] and ctx.author.id == PREVIOUS[1]:
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
    await ctx.send(f"{user.name} is now on {symbol}REP {abs(REPUTATION[user.id])}")

    # Saving the object to a JSON file
    with open("reputations.json", "w") as json_file:
        json.dump(DATA, json_file)

# setRep
@bot.command(name="setrep")
async def setRep(ctx, user: User, amount: int):
    # checking if user has perms
    if ctx.author.id not in ADMINS:
        await ctx.send("SHUT UP BOZO")
        return

    REPUTATION[user.id] = amount

    symbol = getSymbol(user)
    await ctx.send(f"{user.name} is now on {symbol}REP {abs(REPUTATION[user.id])}")

    # Saving the object to a JSON file
    with open("reputations.json", "w") as json_file:
        json.dump(DATA, json_file)


# gambles user rep with a 49% win chance
@bot.command(name="gamble")
async def gambleRep(ctx, amount=None):
    # checking is user entered value
    if amount == None:
        await ctx.send("You cannot gamble nothing")
        return

    # checking if user gambled all
    if amount.lower() == "all":
        amount = REPUTATION[ctx.author.id]
    
    try:
        amount = int(amount)
    except Exception:
        await ctx.send("not a valid amount")
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
        await ctx.send("you win")
    # lose
    else:
        REPUTATION[ctx.author.id] -= amount
        REPUTATION[bot.user.id] += amount
        await ctx.send("you lose")
    await ctx.send(f"You now have {REPUTATION[ctx.author.id]} rep")

    # Saving the object to a JSON file
    with open("reputations.json", "w") as json_file:
        json.dump(DATA, json_file)


# gambleSlots
@bot.command(name="slots")
async def gambleSlots(ctx):
    # checking if the user has enough rep
    if REPUTATION[ctx.author.id] < 1:
        await ctx.send("brokies can't gamble")

    emojis = ["😼","🎁","🤓","🤑"]
    slots = choice(emojis) + choice(emojis) + choice(emojis)
    await ctx.send(slots)

    # cost of playing
    REPUTATION[ctx.author.id] -= 1

    # jackpot
    if slots[0] == slots[1] == slots[2]:
        REPUTATION[ctx.author.id] += 30
        await ctx.send("JACKPOT")
    # small win
    elif (slots[0] == slots[1]) or (slots[1] == slots[2]):
        REPUTATION[ctx.author.id] += 5
        await ctx.send("SMALL WIN")
    await ctx.send(f"You now have {REPUTATION[ctx.author.id]} rep")

    # Saving the object to a JSON file
    with open("reputations.json", "w") as json_file:
        json.dump(DATA, json_file)

@bot.command()
async def admin(ctx, user: User=None):
    # check user who sent message has perms
    if ctx.author.id not in ADMINS:
        await ctx.send("You do not have access to this command")
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

@bot.command()
async def blacklist(ctx, user: User=None):
    # check if user has perms
    if ctx.author.id not in ADMINS:
        await ctx.send("you do not have the perms")
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
    await ctx.send(output)

# entry point
def main() -> None:
    bot.run(token=TOKEN)

if __name__ == "__main__":
    main()  
