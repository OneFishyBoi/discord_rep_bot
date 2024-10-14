import requests
from dotenv import load_dotenv
from typing import Final
import os
import json
print("---------------------------------------------------------------")
print("\n")

# loading token
load_dotenv()
API_KEY: Final[str] = os.getenv("RIOT_TOKEN")

'''
Code has to string together urls to request data from the api through https://
riotHost should stay the same (unless you need to change region)
endPoint may change depending on what you are requesting
'''
# try:
#     requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/RGAPI-fa97e696-178c-4667-a4b6-d046cc43a2f8?api_key={API_KEY}").json()
# except:
#     print("GET A NEW API KEY YOU MONKEY")

def getWins(matchCount=3):
    # Defining strings for url conglomeration
    apiText = f"api_key={API_KEY}"
    platform = "euw1"
    region = "europe"
    riotHost = ".api.riotgames.com"
    username = "Ducktape"
    tagLine = "meow"

    # Getting my PUUID:
    endPoint = f"/riot/account/v1/accounts/by-riot-id/{username}/{tagLine}"
    puuidURL = f"https://{region}{riotHost}{endPoint}?{apiText}"
    summoner_data = requests.get(puuidURL).json()
    puuid = summoner_data["puuid"]

    # Getting my last n matches:
    endPoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
    matchesURL = f"https://{region}{riotHost}{endPoint}?count={matchCount}&{apiText}&type=ranked"
    matches = requests.get(matchesURL).json()

    # Getting my summonerID from PUUID
    endPoint = f"/lol/summoner/v4/summoners/by-puuid/{puuid}"
    summonerURL = f"https://{platform}{riotHost}{endPoint}?{apiText}"
    summoner_data = requests.get(summonerURL).json()
    summonerID = summoner_data['id']

    wins = 0
    # Getting win/loss for each match 
    for matchID in matches:
        # Getting match data
        endPoint = f"/lol/match/v5/matches/{matchID}"
        matchURL = f"https://{region}{riotHost}{endPoint}?{apiText}"
        matchData = requests.get(matchURL).json()

        # Getting my teamId from my summonerID
        participants = matchData["info"]["participants"]
        for participant in participants:
            if participant["summonerId"] == summonerID:
                teamID = participant["teamId"]
                break
        
        # Riot games is awesome!!
        teamIndex = 0 if teamID == 100 else 1

        # Getting match result
        matchResult = matchData["info"]["teams"][teamIndex]["win"]
        if matchResult:
            wins += 1
    return wins

import json


class investMeow:
    def __init__(self, amount=1, lifespan=3, age=0, discordID=None) -> None:
        self.amount = amount
        self.lifespan = lifespan
        self.age = age
        self.discordID = discordID

    def checkAge(self):
        return self.lifespan == self.age

    def to_dict(self):
        return {
            "amount": self.amount,
            "lifespan": self.lifespan,
            "age": self.age,
            "discordID": self.discordID
        }


# rep = 20

# def roundTowardsZero(n):
#     if n > 0:
#         # For positive numbers
#         if n != int(n):
#             return floor(n + 0.5)
#         else:
#             return n
#     else:
#         # For negative numbers
#         if n != int(n):
#             return ceil(n - 0.5)
#         else:
#             return n

def trunc(n): # round to 2dp
    return float(f"{n:.2f}")

def stocks(amount=1,investLength=3):
    winNumber = getWins(investLength) # example amount of wins for concept
    winRate = winNumber/investLength 
    # roi = (winRate - 0.5)*amount
    roi = (winRate - 0.5)*amount*2
    # print(trunc(roi))
    return [roi,winNumber]

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# rep += stocks(amount=rep,investLength=20)[0]
# print(rep)

# a = True
# print(f"({rep})")
# while rep >= 0:
#     rep += stocks(amount=rep,investLength=3)[0]
#     print(f"{rep}")
#     sleep(3)
#     # a = bool(input())

print("Stocks loaded!")
