from matplotlib.axis import YAxis
import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
import numpy as np
import matplotlib.pyplot as plt
import math



#Import ri.gg Data
df = pd.read_csv(r"C:\Users\Renzjordan\OneDrive\MiniProj\VALImpact\data\VCT-NA-2022-Stage-2-Challengers-ImpactEssentialData.csv")

#Set Attack Team Win target variable
df['ATKWin'] = 0
for i in range(0, len(df)):

    if(df.loc[i, 'attackingTeamNumber'] == df.loc[i, 'winningTeamNumber']):
        df.loc[i, 'ATKWin'] = 1


#Seperate Independent and Dependent Variables
indVars = df.drop(columns=['roundId_x', 'attackingTeamNumber', 'winningTeamNumber','ATKWin'])
depVar = df[['matchId_y', 'ATKWin']]

# finalVars = indVars.columns.values.tolist()


#Split data into testing and training sets
# X_train,X_test,y_train,y_test=train_test_split(indVars, depVar, test_size=0.25, random_state=0)

#Train on group stage
X_train = indVars[indVars['matchId_y'] < 69970].drop(columns=['matchId_y'])
Y_train = depVar[depVar['matchId_y'] < 69970].drop(columns=['matchId_y'])

X_test = indVars[indVars['matchId_y'] == 69970].drop(columns=['matchId_y'])
y_test = depVar[depVar['matchId_y'] == 69970].drop(columns=['matchId_y'])

# print(X_test.head(60))

#do Logisistic Regression
logreg = LogisticRegression()

logreg.fit(X_train, Y_train)

print(df[df['matchId_y'] == 69970])

#Transform Bomb Time from (100000 to -450000) -> (0 to 1)
def NormalizeData(data):
    # return (data - np.max(data)) / (np.min(data) - np.max(data))
    return (data - np.max(data)) / (-45000 - np.max(data))

# print(NormalizeData(df[df['matchId_y'] == 69969]['roundTime']))

#Set X-axis for graph (round + event time)
xAx = df[df['matchId_y'] == 69970]['roundId_x']-1092196 + NormalizeData(df[df['matchId_y'] == 69970]['roundTime'])

#Find index of round 13
halftime = xAx.loc[xAx==13].index[0] - xAx.loc[xAx==1].index[0]
# print(xAx.head(60))

# print(halftime)
# print(df[df['matchId_y'] == 69969].iloc[:halftime])

#Get probability of [0, 1]
y_pred=logreg.predict_proba(X_test)
# y_pred=logreg.predict_proba(X_test)[::,1]
# print(y_pred)
# print(logreg.classes_)

# print(df[df['matchId_y'] == 69969].iloc[0]['attackingTeamNumber'])

#Get probabilities for home team
if(df[df['matchId_y'] == 69970].iloc[0]['attackingTeamNumber'] == 1):
    firstHalf = [item[1] for item in y_pred[:halftime+1]]
    secHalf = [item[0] for item in y_pred[halftime+1:]]
else:
    firstHalf = [item[0] for item in y_pred[:halftime+1]]
    secHalf = [item[1] for item in y_pred[halftime+1:]]

#Sey y-axis for graph
yAx = firstHalf + secHalf
# print(yAx)


#Set up enough plots for each round
figure, axis = plt.subplots(5, 5)


#Get final round number
final = math.ceil(xAx.iloc[-1])

#Plot x, y for each round graph
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







