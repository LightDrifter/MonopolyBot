from itertools import cycle
from .board import Board
from .utils import *
from .const import State
from .player import Player

class Game:
    def __init__(self):
        self.state = None
        self.num_houses = 32
        self.num_hotels = 12
        self.players = []
        self.turn_cycler = None
        self.turn = None

    def init(self):
        self.board = Board()
        self.board.init()
        self.state = State.GAME_BEGIN
        print(f"Game of Monopoly has been initialized. Please follow the instructions on screen and enter your inputs accordingly.\n")
    
    def add_player(self):
        new = Player()
        new.init(prompt(f"Enter alias for Player{len(self.players) + 1}"))
        self.players.append(new)

    def is_prop(self, card):
        colors = ["Brown", "Blue", "Pink", "Orange", "Red", "Yellow", "Green", "DBlue"]
        if card["color"] in colors:
            return True
        else:
            return False

    def check_owner(self, id):
        check = None
        for player in self.players:
            if id in player.owned_prop:
                check = player
        return check

    def advance_turn(self):
        self.turn = next(self.turn_cycler)
    
    #Bonus awarded to players for passing through GO
    def GO_Bonus(self, player):
        player.pay(-200)
        return True
    
    #Current turn player pays rent to player in argument
    def pay_rent(self, player, rent):
        player.pay(-1 * rent)
        self.turn.pay(rent)

    #All game logic in here.
    def evaluate(self):
        if self.state == State.GAME_BEGIN:
            while True:
                num_players = int(prompt(f"Please enter the number of players."))
                if num_players < 9 and num_players > 1:
                    for i in range(num_players):
                        self.add_player()
                    break
                else:
                    print(f"Only 2 to 8 players are supported as of now, please try again.\n")

            self.turn_cycler = cycle(self.players)
            self.advance_turn()

            self.state = State.TURN_BEGIN
            self.evaluate()
        
        elif self.state == State.TURN_BEGIN:
            print(f"--- {self.turn.alias}'s Turn --- \n")
            _roll = roll()
            #Need to add check for double rolls
            print(f"{self.turn.alias} rolled a {_roll}! Advancing the player through {_roll} blocks...")
            
            (new_pos, bonus) = increment(self.turn.ret_pos(), _roll)
            if bonus:
                print(f"Adding 200$ for passing through GO...")
                self.GO_Bonus(self.turn)
            
            self.turn.set_pos(new_pos)
            card = self.board.board[new_pos].card
            id = card["id"]

            #TODO: Maybe add a info() in player.py to print out details of the card...
            print(f"{self.turn.alias}, you've reached {id}!\n")

            #If not owned, prompt to buy property IF IT IS A PROPERTY
            if self.check_owner(id) is None and self.is_prop(card):
                cost = card["cost"]
                resp = prompt(f"{id} is NOT owned by anyone yet. The cost to buy this property is {cost}. Do you want to but this property? (Y/N)")
                if resp == 'y' or resp == 'Y':
                    self.turn.pay(cost)
                    self.turn.owned_prop.append(id)
                    print(f"{self.turn.alias} has bought {id} for {cost}. Remaining money is {self.turn.money}.")
                #TODO: Make auctioning possible here
                elif resp == 'n' or resp == 'N':
                    print(f"Property not bought.")
                else:
                    print(f"Unknown response... Interpreting as disinterest in buying property.")

            elif self.check_owner(id) is not None and self.is_prop(card):
                rent = card["rent"]
                print(f"This property is owned by {self.check_owner(id).alias}. Paying a rent of {rent} to the owner...")
                self.pay_rent(self.check_owner(id), rent)
                print(f"Remaining money is {self.turn.money}.")

            elif card["color"] == "CC" or card["color"] == "C":
                #TODO: Add Functionality for Chance, Community Chests
                div = True
                if card["color"] == "CC":
                    div = False
                print(f"Drawing a card from the pile...")
                print(f"{self.turn.alias} has drawn a card, and it says... {self.board.draw(div)}")
                prompt(f"Do you agree?")
            print()

            self.state = State.TURN_END
            self.evaluate()

        elif self.state == State.TURN_END:
            #TODO: Has the global prompt to buy houses anywhere or smth
            #TODO: Check for double throw, and repeat turn if that is the case
            self.advance_turn()
            self.state = State.TURN_BEGIN
            self.evaluate()
