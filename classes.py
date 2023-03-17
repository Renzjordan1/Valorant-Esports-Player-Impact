class GameState:
    def __init__(self, players1, players2, round):
        self.players1 = players1 #List of Players on Team 1
        self.players2 = players2 #List of Players on Team 2
        self.round = round #Round number

    def setPlayers(self, players):
        self.players1 = dict(list(players.items())[:len(players)//2])
        self.players2 = dict(list(players.items())[len(players)//2:])



class Player:
    def __init__(self, name, value):    
        self.name = name #Player Name
        self.value = value #Inventory Value

    def setValue(self, value):
        self.value = value
    
    def resetValue(self):
        self.value = 0
        







