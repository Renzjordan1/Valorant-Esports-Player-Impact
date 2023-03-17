from matplotlib.axis import YAxis
import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
import numpy as np
import matplotlib.pyplot as plt
import math
import json



#Import rib.gg Data
df = pd.read_csv(r"C:\Users\Renzjordan\OneDrive\MiniProj\VALImpact\data\VCT-NA-2022-Stage-2-Challengers-ImpactEssentialPlayerData.csv")

#Set Attack Team Win target variable
df['ATKWin'] = 0
for i in range(0, len(df)):

    if(df.loc[i, 'attackingTeamNumber'] == df.loc[i, 'winningTeamNumber']):
        df.loc[i, 'ATKWin'] = 1


#Seperate Independent and Dependent Variables
indVars = df.drop(columns=['roundId_x', 'attackingTeamNumber', 'winningTeamNumber','ATKWin', 'playerId', 'assistants', 'victimId'])
depVar = df[['matchId_y', 'ATKWin']]

# finalVars = indVars.columns.values.tolist()


#Split data into testing and training sets
# X_train,X_test,y_train,y_test=train_test_split(indVars, depVar, test_size=0.25, random_state=0)

#Train on group stage
X_train = indVars[indVars['matchId_y'] < 69970].drop(columns=['matchId_y'])
Y_train = depVar[depVar['matchId_y'] < 69970].drop(columns=['matchId_y'])

X_test = indVars[indVars['matchId_y'] == 68482].drop(columns=['matchId_y'])
y_test = depVar[depVar['matchId_y'] == 68482].drop(columns=['matchId_y'])

# print(X_test.head(60))

#do Logisistic Regression
logreg = LogisticRegression()

logreg.fit(X_train, Y_train)

print(df[df['matchId_y'] == 68482])

#Transform Bomb Time from (100000 to -450000) -> (0 to 1)
def NormalizeData(data):
    # return (data - np.max(data)) / (np.min(data) - np.max(data))
    return (data - np.max(data)) / (-45000 - np.max(data))

# print(NormalizeData(df[df['matchId_y'] == 69969]['roundTime']))

#Set X-axis for graph (round + event time)
xAx = df[df['matchId_y'] == 68482]['roundId_x']-df[df['matchId_y'] == 68482]['roundId_x'][df[df['matchId_y'] == 68482].index[0]] +1 + NormalizeData(df[df['matchId_y'] == 68482]['roundTime'])

#Find index of round 13
halftime = xAx.loc[xAx==13].index[0] - xAx.loc[xAx==1].index[0]
print(xAx.head(60))

# print(halftime)
# print(df[df['matchId_y'] == 69969].iloc[:halftime])

#Get probability of [0, 1]
y_pred=logreg.predict_proba(X_test)
# y_pred=logreg.predict_proba(X_test)[::,1]
# print(y_pred)
# print(logreg.classes_)

# print(df[df['matchId_y'] == 69969].iloc[0]['attackingTeamNumber'])

#Get probabilities for home team
if(df[df['matchId_y'] == 68482].iloc[0]['attackingTeamNumber'] == 1):
    firstHalf = [item[1] for item in y_pred[:halftime+1]]
    secHalf = [item[0] for item in y_pred[halftime+1:]]
else:
    firstHalf = [item[0] for item in y_pred[:halftime+1]]
    secHalf = [item[1] for item in y_pred[halftime+1:]]

#Sey y-axis for graph
yAx = firstHalf + secHalf
print(yAx)


#Set up enough plots for each round
figure, axis = plt.subplots(5, 5)


#Get final round number
final = math.ceil(xAx.iloc[-1])

# Plot x, y for each round graph
round = 1
for i in range(5):
    for j in range(5):
        # print(xAx.loc[xAx==round].index[0])
        # print(xAx.loc[xAx.loc[xAx==round].index[0]:xAx.loc[xAx==round+1].index[0]])
        if(round!=final-1):
            # if(i==3 and j==2):
            #     print(xAx.loc[xAx.loc[xAx==round].index[0]:xAx.loc[xAx==round+1].index[0]-1])
            #     print(yAx[xAx.loc[xAx==round].index[0]-xAx.loc[xAx==1].index[0]:xAx.loc[xAx==round+1].index[0]-xAx.loc[xAx==1].index[0]])
            axis[i, j].plot(xAx.loc[xAx.loc[xAx==round].index[0]:xAx.loc[xAx==round+1].index[0]-1], yAx[xAx.loc[xAx==round].index[0]-xAx.loc[xAx==1].index[0]:xAx.loc[xAx==round+1].index[0]-xAx.loc[xAx==1].index[0]])
            axis[i, j].set_title("Round " + str(round))  
            # axis[i, j].set_xticks(xAx.loc[xAx.loc[xAx==round].index[0]:xAx.loc[xAx==round+1].index[0]-1])
        else:
            axis[i, j].plot(xAx.loc[xAx.loc[xAx==round].index[0]:], yAx[xAx.loc[xAx==round].index[0]-xAx.loc[xAx==1].index[0]:])
            axis[i, j].set_title("Round " + str(round))
            # axis[i, j].set_xticks(xAx.loc[xAx.loc[xAx==round].index[0]:])


        # axis[i, j].ylim(0, 1) 
        axis[i, j].set_yticks(np.arange(0, 1, step=0.1)) 
        

        round += 1  
        if(round == final):
            break
    if(round == final):
        break

# plt.plot(xAx, yAx)
# plt.xlabel('Round')
# plt.ylabel('Win Prob')
  
# plt.title('FAZE vs 100T')
plt.show()

#Import player data for each match
playerData = pd.read_csv(r"C:\Users\Renzjordan\OneDrive\MiniProj\VALImpact\data\VCT-NA-2022-Stage-2-Challengers-PlayerData.csv")
playerImpact = df[['matchId_y', 'roundId_x', 'attackingTeamNumber', 'playerId', 'assistants', 'victimId']]
playerImpact = playerImpact[playerImpact['matchId_y'] == 68482]
playerImpact['impact'] = 0


# print(playerImpact.head())

#Calculate impact for each player
for i in range(0, len(playerImpact)):
    
    matchId = playerImpact.loc[playerImpact.index[0]+i, 'matchId_y']
    playerId = playerImpact.loc[playerImpact.index[0]+i, 'playerId'] 

    if(not math.isnan(playerId)):
        # print(matchId, playerId)
        # print(playerData[((playerData['matchId'] == matchId) & (playerData['playerId'] == playerId))]['teamNumber'].values)
    
        playerImpact.loc[playerImpact.index[0]+i, 'impact'] = abs(yAx[i]-yAx[i-1])
    
    else:
        pass



# print(playerImpact.head(20))



playerNames = pd.read_csv(r"C:\Users\Renzjordan\OneDrive\MiniProj\VALImpact\data\VCTPlayers.csv")



# for i in range(0, 5):
#     print(type(playerImpact.loc[playerImpact.index[0] + i, 'assistants']))
#     print((playerImpact.loc[playerImpact.index[0] + i, 'assistants']))
#     if(type(playerImpact.loc[playerImpact.index[0] + i, 'assistants'])) is str:
#         playerImpact.loc[playerImpact.index[0] + i, 'assistants'] = json.loads(playerImpact.loc[playerImpact.index[0] + i, 'assistants'])
#         # print(playerImpact.loc[playerImpact.index[0] + i, 'assistants'].split(','))
#         if(playerImpact.loc[playerImpact.index[0] + i, 'assistants'][0] is None):
#             playerImpact.loc[playerImpact.index[0] + i, 'assistants'] = np.nan

gVR = playerImpact.groupby(['roundId_x', 'victimId'])['impact'].sum().reset_index()
gVM = playerImpact.groupby(['victimId'])['impact'].sum().reset_index()

print(gVM.head(10))

            
#Getting impact for assistants + split individual impact
playerImpact['impact_assist'] = 0
for i in range(0, len(playerImpact)):
    if(len(json.loads(playerImpact.loc[playerImpact.index[0] + i, 'assistants'])) > 0):
        playerImpact.loc[playerImpact.index[0]+i,'impact_assist'] = playerImpact.loc[playerImpact.index[0] + i, 'impact'] * (0.30 / len(json.loads(playerImpact.loc[playerImpact.index[0] + i, 'assistants'])))
        playerImpact.loc[playerImpact.index[0]+i,'impact'] -= playerImpact.loc[playerImpact.index[0] + i, 'impact'] * (0.30)



#Create assistant impact dataframe
ass = pd.DataFrame(pd.np.empty((0, 8)))
ass.columns = playerImpact.columns.tolist()


for i in range(0, len(playerImpact)):
    for p in (json.loads(playerImpact.loc[playerImpact.index[0] + i, 'assistants'])):
        # print(p)
        row =  pd.DataFrame([{'matchId_y': playerImpact.loc[playerImpact.index[0]+i,'matchId_y'],
         'roundId_x': playerImpact.loc[playerImpact.index[0]+i,'roundId_x'], 
         'attackingTeamNumber': playerImpact.loc[playerImpact.index[0]+i,'attackingTeamNumber'],
         'playerId': p,
         'assistants': [],
         'victimId': playerImpact.loc[playerImpact.index[0]+i,'victimId'],
         'impact': playerImpact.loc[playerImpact.index[0]+i,'impact_assist']}])
        ass = pd.concat([ass, row])
        print(row)

ass['impact_assist'] = 0

#Impact by round
# gP = playerImpact.groupby(['roundId_x', 'playerId'])['impact'].sum().reset_index()
# gP['impact'] = gP['impact'] - gVR['impact']

# print(gP)

gA = ass.groupby(['playerId'])['impact'].sum().reset_index()

#Impact by match
gP = playerImpact.groupby(['playerId'])['impact'].sum().reset_index()

# print(gP.head(20))
print(gVM.head(20))
print(gP.head(20))
print(gA.head(20))

gP['impact'] = gP['impact'] - gVM['impact']

gP = pd.merge(gP, playerNames, how='left', left_on = 'playerId', right_on = 'Player Id')



gP['impact'] = gP['impact'] + gA['impact']




print(gP)


# print(X_test, y_pred)

#Get accuracy/loss metrics
# cnf_matrix = metrics.confusion_matrix(y_test, y_pred)

# print(cnf_matrix)
# print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
# print("Precision:",metrics.precision_score(y_test, y_pred))
# print("Recall:",metrics.recall_score(y_test, y_pred))
# fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred)
# auc = metrics.roc_auc_score(y_test, y_pred)
# plt.plot(fpr,tpr,label="data 1, auc="+str(auc))
# plt.legend(loc=4)
# plt.show()

# print(len(y_pred))
# print(len(y_test['ATKWin'].values))
# losses = np.subtract(y_test['ATKWin'].values, y_pred)**2
# brier_score = losses.sum()/len(y_pred)
# print(brier_score, losses)







