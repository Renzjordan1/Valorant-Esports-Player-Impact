
import urllib.request as urllib
from bs4 import BeautifulSoup
import pandas as pd
# from classes import *
import re
import json


# list of all matches VCT NA Chal 2 
# matches = pd.read_csv (r'C:\Users\Renzjordan\OneDrive\MiniProj\VALImpact\data\NA-VCTChal2-matches.csv')


aggregateData = pd.DataFrame()

matches = pd.read_csv(r"C:\Users\Renzjordan\OneDrive\MiniProj\VALImpact\data\NA-VCTChal2-matches.csv")
# print(matches.head())

for i in range(0, len(matches)):
    link = ("https://rib.gg/series/" + matches.loc[i, "Team 1 Name"] + "-vs-" + matches.loc[i, "Team 2 Name"] + "-" + matches.loc[i, "Event Name"] + "/" + str(matches.loc[i, "Series Id"]) + "?match=" + str(matches.loc[i, "Match Id"])).replace(" -", "").split(" ")
    link = '-'.join(link)

    print(link)
    urlReplay = link + "&round=1" + '&tab=replay'
    urlRound = link + "&round=1" + '&tab=rounds'
    # urlReplay = 'https://rib.gg/series/cloud9-vs-version1-vct-north-america-2022-stage-1-challengers-main-event/26475?match=58847&round=' + str(round) + '&tab=replay'
    # urlRound = 'https://rib.gg/series/cloud9-vs-version1-vct-north-america-2022-stage-1-challengers-main-event/26475?match=58847&round=' + str(round) + '&tab=rounds'

    requestReplay = urllib.Request(urlReplay, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'})
    pageReplay = urllib.urlopen(requestReplay)

    requestRound = urllib.Request(urlRound, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'})
    pageRound = urllib.urlopen(requestRound)

    soupReplay = BeautifulSoup(pageReplay,'html.parser')
    soupRound = BeautifulSoup(pageRound, 'html.parser')


    # roundBody = soupRound.find('tbody')
    # roundRow = roundBody.find_all('tr')

    # print(soupReplay.find_all("script")[5].contents[0].split("63828")[1])
    # print(soupReplay.find_all("script")[5])
    # print(re.split("\[(.*?)\]", str(soupReplay.find_all("script")[6].contents[0])))

    killsData = soupReplay.find_all("script")[5].contents[0].split("],\"kills\":")[1].split(",\"xvys\":[")[0]
    killsData = json.loads(killsData)

    eventsData = soupReplay.find_all("script")[5].contents[0].split(str(matches.loc[i, "Match Id"])+",\"events\":")[1].split(",\"locations\":[")[0]
    eventsData = json.loads(eventsData)

    economyData = soupReplay.find_all("script")[5].contents[0].split("\"economies\":")[1].split("}},\"trending\":")[0]
    economyData = json.loads(economyData)

    roundsData = soupReplay.find_all("script")[5].contents[0].split("],\"kills\":")[0].split("\"rounds\":")[-1] + "]"
    roundsData = json.loads(roundsData)


    playersData = soupReplay.find_all("script")[5].contents[0].split("},\"players\":[{\"matchId\":" + str(matches.loc[i, "Match Id"]))[2].split(",\"stats\":")[0]
    playersData =  "[{\"matchId\":" + str(matches.loc[i, "Match Id"]) + playersData
    playersData = json.loads(playersData)
    # print(roundsData)


    kD = pd.DataFrame(killsData).drop(columns=['gameTimeMillis', 'victimLocationX', 'victimLocationY', 'damageType', 'abilityType', 'weaponId', 'secondaryFireMode', 'weapon', 'weaponCategory', 'first'])
    evD = pd.DataFrame(eventsData).drop(columns=['roundNumber','impact', 'attackingWinProbabilityBefore', 'attackingWinProbabilityAfter', 'ability', 'damageType', 'weaponId'])
    ecD = pd.DataFrame(economyData).drop(columns=['roundNumber', 'agentId', 'score', 'weaponId','armorId', 'remainingCreds', 'spentCreds'])
    rD = pd.DataFrame(roundsData).drop(columns=['ceremony', 'deletedOn', 'team1LoadoutTier', 'team2LoadoutTier', 'attackingTeamNumber'])
    plD = pd.DataFrame(playersData).drop(columns=['player'])


    # print(evD['eventType'].unique())
    # print(kD)
    # print(evD)
    # print(ecD)
    # print(rD)
    # print(plD)


    ecPDStart = pd.merge(ecD, plD, how='left', on = 'playerId')
    # print(ecPDStart)

    ecPD = ecPDStart.groupby(['teamNumber', 'roundId'])['loadoutValue'].sum()
    # ecPD = ecPD.combine(ecPD.loc[0],ecPD.loc[1],on='roundId')
    ecPD = ecPD.reset_index()

    ecPD1 = ecPD.loc[ecPD['teamNumber'] == 1]
    ecPD2 = ecPD.loc[ecPD['teamNumber'] == 2]
    ecPDEnd = pd.merge(ecPD1, ecPD2, how='inner', left_on = 'roundId', right_on = 'roundId')
    ecPDEnd = ecPDEnd.drop(columns=['teamNumber_x', 'teamNumber_y'])

    # print(ecPDEnd)

    evKD = pd.merge(evD, kD, how='left', left_on = 'killId', right_on = 'id')
    evKD = pd.merge(evKD, rD, how='inner', left_on = 'roundId_x', right_on = 'id')
    evKD = pd.merge(evKD, ecPDEnd, how='inner', left_on = 'roundId_x', right_on = 'roundId')


    ##SET TIME + BOMB TIME
    evKD['roundTime'] = 100000
    evKD.loc[evKD['eventType'] == 'plant', 'roundTime'] = 0

    for i in range(1, len(evKD)):

        if(evKD.loc[i, 'roundId_x'] == evKD.loc[i-1, 'roundId_x']):

            if(evKD.loc[i-1, 'eventType'] == 'plant'):
                evKD.loc[i, 'roundTime'] = -1 * (evKD.loc[i, 'roundTimeMillis_x'] - evKD.loc[i-1, 'roundTimeMillis_x'])

            elif(evKD.loc[i-1, 'roundTime']<0):
                evKD.loc[i, 'roundTime'] = evKD.loc[i-1, 'roundTime'] + (-1 * (evKD.loc[i, 'roundTimeMillis_x'] - evKD.loc[i-1, 'roundTimeMillis_x'])) 

            elif(evKD.loc[i, 'roundTime']!=0):
                evKD.loc[i, 'roundTime'] = evKD.loc[i-1, 'roundTime']  + (-1 * (evKD.loc[i, 'roundTimeMillis_x'] - evKD.loc[i-1, 'roundTimeMillis_x']))
            
            else:
                pass
        
        else:
            pass
        

    ##SET LOADOUT VALUES
    for i in range(1, len(evKD)):

        if(evKD.loc[i, 'roundId_x'] == evKD.loc[i-1, 'roundId_x']):
            evKD.loc[i, 'loadoutValue_x'] = evKD.loc[i-1, 'loadoutValue_x']
            evKD.loc[i, 'loadoutValue_y'] = evKD.loc[i-1, 'loadoutValue_y']

            if(evKD.loc[i, 'victimTeamNumber'] == 2):
                evKD.loc[i, 'loadoutValue_y'] -= ecPDStart[((ecPDStart['playerId'] == evKD.loc[i, 'victimId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]
                evKD.loc[i, 'loadoutValue_x'] += (ecPDStart[((ecPDStart['playerId'] == evKD.loc[i, 'victimId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]) / 3


            elif(evKD.loc[i, 'victimTeamNumber'] == 1):
                evKD.loc[i, 'loadoutValue_x'] -= ecPDStart[((ecPDStart['playerId'] == evKD.loc[i, 'victimId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]
                evKD.loc[i, 'loadoutValue_y'] += (ecPDStart[((ecPDStart['playerId'] == evKD.loc[i, 'victimId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]) / 3

            elif(not(pd.isna(evKD.loc[i, 'resId']))):
                if(ecPDStart[(ecPDStart['playerId'] == evKD.loc[i, 'referencePlayerId'])]['teamNumber'].values[0] == 1):
                    evKD.loc[i, 'loadoutValue_x'] += ecPDStart[((ecPDStart['playerId'] ==  evKD.loc[i, 'referencePlayerId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]

                elif(ecPDStart[(ecPDStart['playerId'] == evKD.loc[i, 'referencePlayerId'])]['teamNumber'].values[0] == 2):
                    evKD.loc[i, 'loadoutValue_y'] += ecPDStart[((ecPDStart['playerId'] ==  evKD.loc[i, 'referencePlayerId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]

                else:
                    evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive'] + 1
                    evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive']


            else:
                pass
        
        else:
            pass
    

    evKD.loc[evKD['attackingTeamNumber'] == 1, 'ATKLoadoutValue'] = evKD['loadoutValue_x']
    evKD.loc[evKD['attackingTeamNumber'] == 1, 'DEFLoadoutValue'] = evKD['loadoutValue_y']

    evKD.loc[evKD['attackingTeamNumber'] == 2, 'ATKLoadoutValue'] = evKD['loadoutValue_y']
    evKD.loc[evKD['attackingTeamNumber'] == 2, 'DEFLoadoutValue'] = evKD['loadoutValue_x']
            
    
    ##SET PLAYERS ALIVE
    evKD['ATKAlive'] = 5
    evKD['DEFAlive'] = 5

    for i in range(1, len(evKD)):
        if(evKD.loc[i, 'roundId_x'] == evKD.loc[i-1, 'roundId_x']):
            if(evKD.loc[i, 'side']=='def'):
                evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive'] -1
                evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive']
            elif(evKD.loc[i, 'side']=='atk'):
                evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive'] -1
                evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive']

            elif(not(pd.isna(evKD.loc[i, 'resId']))):
                if(evKD.loc[i, 'attackingTeamNumber'] == ecPDStart[(ecPDStart['playerId'] == evKD.loc[i, 'referencePlayerId'])]['teamNumber'].values[0]):
                    evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive'] + 1
                    evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive']
                else:
                    evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive'] + 1
                    evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive']
                
                

            else:
                evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive']
                evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive']




    evKDEssentials = evKD[['matchId_y', 'roundId_x', 'attackingTeamNumber', 'roundTime', 'ATKAlive', 'DEFAlive', 'ATKLoadoutValue', 'DEFLoadoutValue', 'winningTeamNumber']]

    aggregateData = pd.concat([aggregateData, evKDEssentials])

    # print(evKD[['killId', 'id_x', 'roundId_x', 'id_y']])

# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
    # print(evKDEssentials)

print(aggregateData)
aggregateData.to_csv(r"C:\Users\Renzjordan\OneDrive\MiniProj\VALImpact\data\VCT-NA-2022-Stage-2-Challengers-ImpactEssentialData.csv", index=False)


# print(evKD.iloc[[42, 43, 44]])
# print(evKD['eventType'].unique())

# for col in evKD.columns:
#     print(col)

# for key, value in evKD[0].items():
#     print(key)

# print(replayDiv)


# print(invCol[3].find_all('div')[1].getText())
# p1Econ = 0
# p2Econ = 0
# p = {}
# gg = GameState({}, [], 1)


# #Initialize Players
# def createPlayers(roundRow, p):
#     for i in range(len(roundRow)):

#         if (i == 5): #SKIP Team Header
#             continue

#         roundCol = roundRow[i].find_all('td')

#         name = (roundCol[0].find('a').getText())
#         p["player{0}".format(i)] = Player(name, 0)


# def fillTeams(game, players):
#     game.setPlayers(players)


# #Set Inventory Value
# def setInventories(roundRow, p):
    
#     for i in range(len(roundRow)):

#         if (i == 5): #SKIP Team Header
#             continue

#         roundCol = roundRow[i].find_all('td')

#         value = roundCol[3].find_all('div')[1].getText()

#         p["player{0}".format(i)].setValue(value)

# # def findPlay(replayRow, game):





# createPlayers(roundRow, p)
# setInventories(roundRow, p)
# fillTeams(gg, p)

# for key in gg.players2:
#     print(p[key].name, p[key].value)



    
    

    

# print(invRow.prettify())