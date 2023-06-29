import urllib.request as urllib
from bs4 import BeautifulSoup
import pandas as pd
import json
import ssl
from urllib.parse import quote 


##SCRAPES RIB.GG FOR DATA USEFUL TO TRAIN A MODEL ON HOW MUCH IMPACT AN EVENT HAD ON A ROUND AND ASSOCIATES IT TO A PLAYER



#All data stored here
aggregateData = pd.DataFrame()
playerData = pd.DataFrame()

#list of all matches (from rib.gg Discord bot commands)
matches = pd.read_csv("./Amer-VCT-Spring2023/data/AllMatches.csv")

#Scrap rib.gg for all matches in csv
for i in range(0, len(matches)):
    link = ("https://rib.gg/series/" + quote(matches.loc[i, "Team 1 Name"]) + "-vs-" + quote(matches.loc[i, "Team 2 Name"]) + "-" + quote(matches.loc[i, "Event Name"]) + "/" + str(matches.loc[i, "Series Id"]) + "?match=" + str(matches.loc[i, "Match Id"])).replace(" -", "").split(" ")
    link = '-'.join(link)

    print(link)

    #Links to rib.gg Round and Replay pages
    urlReplay = link + "&round=1" + '&tab=replay'
    urlRound = link + "&round=1" + '&tab=rounds'

    #Bypass SSL Verification (expired SSL causing issues)
    context = ssl._create_unverified_context()

    #Make request and get content from Replay page
    requestReplay = urllib.Request(urlReplay, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'})
    pageReplay = urllib.urlopen(requestReplay, context=context, timeout=60)

    #Make request and get content from Round page
    requestRound = urllib.Request(urlRound, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'})
    pageRound = urllib.urlopen(requestRound, context=context, timeout=60)

    #Parse with BeautifulSoup
    soupReplay = BeautifulSoup(pageReplay,'html.parser')
    soupRound = BeautifulSoup(pageRound, 'html.parser')


    #Get Kills Data
    killsData = soupReplay.find_all("script")[-1].contents[0].split("],\"kills\":")[1].split(",\"xvys\":[")[0]
    killsData = json.loads(killsData)

    #Get Events Data
    eventsData = soupReplay.find_all("script")[-1].contents[0].split(",\"events\":")[1].split(",\"locations\":[")[0]
    eventsData = json.loads(eventsData)

    #Get Economy Data
    economyData = soupReplay.find_all("script")[-1].contents[0].split("\"economies\":")[1].split("},\"content\":")[0]
    economyData = json.loads(economyData)

    #Get Rounds Data
    roundsData = soupReplay.find_all("script")[-1].contents[0].split("],\"kills\":")[0].split("\"rounds\":")[-1] + "]"
    roundsData = json.loads(roundsData)

    #Get Players Data
    playersData = soupReplay.find_all("script")[-1].contents[0].split("\"players\":[{\"matchId\":" + str(matches.loc[i, "Match Id"]))[1].split("}]")[0]
    playersData =  "[{\"matchId\":" + str(matches.loc[i, "Match Id"]) + playersData + "}]"
    playersData = json.loads(playersData)


    #Store parsed data into Dataframes, drop un-necessary columns
    kD = pd.DataFrame(killsData).drop(columns=['gameTimeMillis', 'victimLocationX', 'victimLocationY', 'damageType', 'abilityType', 'weaponId', 'secondaryFireMode', 'weapon', 'weaponCategory', 'first'])
    evD = pd.DataFrame(eventsData).drop(columns=['roundNumber','impact', 'attackingWinProbabilityBefore', 'attackingWinProbabilityAfter', 'ability', 'damageType', 'weaponId'])
    ecD = pd.DataFrame(economyData).drop(columns=['roundNumber', 'agentId', 'score', 'weaponId','armorId', 'remainingCreds', 'spentCreds'])
    rD = pd.DataFrame(roundsData).drop(columns=['ceremony', 'deletedOn', 'team1LoadoutTier', 'team2LoadoutTier', 'attackingTeamNumber'])
    plD = pd.DataFrame(playersData).drop(columns=['player'])


    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None) 


    #Match econ data with player data
    ecPDStart = pd.merge(ecD, plD, how='left', on = 'playerId')

    #Get total round econ value for each team 
    ecPD = ecPDStart.groupby(['teamNumber', 'roundId'])['loadoutValue'].sum()
    ecPD = ecPD.reset_index()


    #Get econ data for each team
    ecPD1 = ecPD.loc[ecPD['teamNumber'] == 1]
    ecPD2 = ecPD.loc[ecPD['teamNumber'] == 2]

    #Combine both team's econ data for each single round
    ecPDEnd = pd.merge(ecPD1, ecPD2, how='inner', left_on = 'roundId', right_on = 'roundId')
    ecPDEnd = ecPDEnd.drop(columns=['teamNumber_x', 'teamNumber_y'])

   #Get context to each event (kills data, round data, econ data)
    evKD = pd.merge(evD, kD, how='left', left_on = 'killId', right_on = 'id')
    evKD = pd.merge(evKD, rD, how='inner', left_on = 'roundId_x', right_on = 'id')
    evKD = pd.merge(evKD, ecPDEnd, how='inner', left_on = 'roundId_x', right_on = 'roundId')



    ##SET TIME + BOMB TIME
    evKD['roundTime'] = 100000
    evKD.loc[evKD['eventType'] == 'plant', 'roundTime'] = 0


    #Adjust round time to match time remaining in each round at each event
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

            #Adjust loadout value when kill occurs (lost weapon/gained weapon)
            if(evKD.loc[i, 'victimTeamNumber'] == 2):
                evKD.loc[i, 'loadoutValue_y'] -= ecPDStart[((ecPDStart['playerId'] == evKD.loc[i, 'victimId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]
                evKD.loc[i, 'loadoutValue_x'] += (ecPDStart[((ecPDStart['playerId'] == evKD.loc[i, 'victimId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]) / 3

            elif(evKD.loc[i, 'victimTeamNumber'] == 1):
                evKD.loc[i, 'loadoutValue_x'] -= ecPDStart[((ecPDStart['playerId'] == evKD.loc[i, 'victimId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]
                evKD.loc[i, 'loadoutValue_y'] += (ecPDStart[((ecPDStart['playerId'] == evKD.loc[i, 'victimId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]) / 3

            #Adjust loadout value when res occurs
            elif(not(pd.isna(evKD.loc[i, 'resId']))):
                if(ecPDStart[(ecPDStart['playerId'] == evKD.loc[i, 'referencePlayerId'])]['teamNumber'].values[0] == 1):
                    evKD.loc[i, 'loadoutValue_x'] += ecPDStart[((ecPDStart['playerId'] ==  evKD.loc[i, 'referencePlayerId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]

                elif(ecPDStart[(ecPDStart['playerId'] == evKD.loc[i, 'referencePlayerId'])]['teamNumber'].values[0] == 2):
                    evKD.loc[i, 'loadoutValue_y'] += ecPDStart[((ecPDStart['playerId'] ==  evKD.loc[i, 'referencePlayerId']) & (ecPDStart['roundId'] == evKD.loc[i, 'roundId_x']))]['loadoutValue'].values[0]

                else:
                    pass

            else:
                pass
        
        else:
            pass

    
    #Label loadout values for ATK and DEF sides
    evKD.loc[evKD['attackingTeamNumber'] == 1, 'ATKLoadoutValue'] = evKD['loadoutValue_x']
    evKD.loc[evKD['attackingTeamNumber'] == 1, 'DEFLoadoutValue'] = evKD['loadoutValue_y']

    evKD.loc[evKD['attackingTeamNumber'] == 2, 'ATKLoadoutValue'] = evKD['loadoutValue_y']
    evKD.loc[evKD['attackingTeamNumber'] == 2, 'DEFLoadoutValue'] = evKD['loadoutValue_x']
            
    
    ##SET PLAYERS ALIVE
    evKD['ATKAlive'] = 5
    evKD['DEFAlive'] = 5

    for i in range(1, len(evKD)):

        if(evKD.loc[i, 'roundId_x'] == evKD.loc[i-1, 'roundId_x']):

            #Adjust Players Alive on each side (evKD.side = value of the side of killing player)
            if(evKD.loc[i, 'side']=='def'):
                evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive'] -1
                evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive']

            elif(evKD.loc[i, 'side']=='atk'):
                evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive'] -1
                evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive']

            #Adjust Players Alive when res occurs
            elif(not(pd.isna(evKD.loc[i, 'resId']))):
                if(evKD.loc[i, 'attackingTeamNumber'] == ecPDStart[(ecPDStart['playerId'] == evKD.loc[i, 'referencePlayerId'])]['teamNumber'].values[0]):
                    evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive'] + 1
                    evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive']
                else:
                    evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive'] + 1
                    evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive']
                    
            #No kill/res
            else:
                evKD.loc[i, 'ATKAlive'] = evKD.loc[i-1, 'ATKAlive']
                evKD.loc[i, 'DEFAlive'] = evKD.loc[i-1, 'DEFAlive']
        
        else:
            pass


    #Get rid of none in ASSISTANTs
    for i in range(0, len(evKD)):

        if(type(evKD.loc[i, 'assistants']) == list):
            if(evKD.loc[i, 'assistants'][0] is None):
                evKD.loc[i, 'assistants'] = ['1']
                evKD.loc[i, 'assistants'].pop(0)
        else:
            evKD.loc[i, 'assistants'] = ['1']
            evKD.loc[i, 'assistants'].pop(0)


    ##Add baited players as assistant
    for i in range(1, len(evKD)):

        if(not(pd.isna(evKD.loc[i, 'tradedForKillId_x']))):
            if(type(evKD.loc[i, 'assistants']) == list):
                evKD.loc[i, 'assistants'].append(int(evKD[(evKD['killId'] == evKD.loc[i, 'tradedForKillId_x'])]['victimId'].values[0]))
            else:
                evKD.loc[i, 'assistants'] = [0]
                evKD.loc[i, 'assistants'][0] = int(evKD[(evKD['killId'] == evKD.loc[i, 'tradedForKillId_x'])]['victimId'].values[0])


    #Get essential data for win prob model + player impact
    evKDEssentials = evKD[['matchId_y', 'roundId_x', 'attackingTeamNumber', 'roundTime', 'ATKAlive', 'DEFAlive', 'ATKLoadoutValue', 'DEFLoadoutValue', 'winningTeamNumber', 'playerId', 'assistants', 'victimId']]
    # print(evKDEssentials.head(1)['matchId_y'])
    #Aggregate all matches' data
    aggregateData = pd.concat([aggregateData, evKDEssentials])


# print(aggregateData)
aggregateData.to_csv("./Amer-VCT-Spring2023/data/EventEssentials+Players.csv", index=False)
