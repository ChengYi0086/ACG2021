import argparse
import sys
import matplotlib.pyplot as plt
import time, random

parser = argparse.ArgumentParser(description='game')

parser.add_argument('num_of_ranks',type = int, help='number of ranks')
parser.add_argument('num_of_cards_each_rank',type = int, help='number of cards of each rank')
parser.add_argument('num_of_cards_each_player',type = int, help='number of cards dealt to each player')
#parser.add_argument('players_list',type = list, help='a list of players, each enter is a string')
parser.add_argument('num_of_hpts',type = int, help='number of health points')
parser.add_argument('CFR_agent_info',nargs="+", help='folder name and file name of the CFR agent')
parser.add_argument('num_of_big_iterations', type=int, help = 'large iteration numbers')
parser.add_argument('num_of_small_iterations', type=int, help='samll iterations number every big iteration')
parser.add_argument('num_of_testing_games',type=int, help='how many games we use for test')
args = parser.parse_args()

print("Please confirm:")
print("Cheat-{hpt} is played using {total_cards} cards from {num_of_ranks} ranks and each player has {num_cards_each_player} cards. The CFR player is using file{CFR_file} from folder {CFR_folder}.".format(hpt = args.num_of_hpts, total_cards = args.num_of_ranks * args.num_of_cards_each_rank,num_of_ranks = args.num_of_ranks, num_cards_each_player = args.num_of_cards_each_player, CFR_file = args.CFR_agent_info[1], CFR_folder = args.CFR_agent_info[0]))


in_content = input("Y or N:")
print(in_content)
if in_content == "Y":
    print("Game start")
else:
    print("Please restart from the beginning")
    sys.exit()

num_of_ranks = args.num_of_ranks
num_of_cards_each_rank = args.num_of_cards_each_rank
num_of_cards_each_player = args.num_of_cards_each_player
num_of_hpts = args.num_of_hpts
CFR_agent_info = args.CFR_agent_info
CFR_agent_name = args.CFR_agent_info[1]

num_of_big_iterations = args.num_of_big_iterations
num_of_small_iterations = args.num_of_small_iterations
num_of_testing_games = args.num_of_testing_games

class Cheat_w_hpt():
    def __init__(self,num_of_ranks,num_of_each_rank,num_of_cards_for_each_player,players_list,num_of_hpt,CFR_player_info = None):
        self.full_deck = [1,2,3,4,5,6,7,8,9,10,11,12,13]
        self.num_of_ranks = num_of_ranks
        self.one_deck = self.full_deck[:self.num_of_ranks]
        self.num_of_each_rank = num_of_each_rank
        self.num_of_cards_for_each_player = num_of_cards_for_each_player
        self.players_list = players_list
        self.num_of_players = len(self.players_list)
        self.num_of_hpt = num_of_hpt
        self.Heuristic_switch = False
        self.current_tag = None

        if "Random player 1" in self.players_list or "Random player 2" in self.players_list or "Random player" in self.players_list:
            self.Random_player = Random_player_w_hpt()
        if "Heuristic player" in self.players_list:
            self.Heuristic_switch = True
            self.Heuristic_player = Heuristic_player_w_hpt(self.num_of_players,self.players_list.index("Heuristic player"))
        if "CFR player" in self.players_list or "CFR player 1" in self.players_list or "CFR player 2" in self.players_list:
            self.CFR_player = Cheat_w_hpt_Player(CFR_player_info[0],CFR_player_info[1])

        self.winning_number = {}
        self.winning_rate = {}
        for i in range(self.num_of_players):
            self.winning_number[i] = 0
            self.winning_rate[i] = 0.0

    def deal_cards(self):
        all_cards = self.one_deck * self.num_of_each_rank
        random.shuffle(all_cards)

        cards_dealt = []
        for _ in range(self.num_of_players):
            card_in_hand = random.sample(all_cards,self.num_of_cards_for_each_player)
            for card in card_in_hand:
                all_cards.remove(card)
            cards_dealt += [sorted(card_in_hand)]

        return cards_dealt

    def init_game(self):
        print("New Game Starts!")
        self.cards_dealt = self.deal_cards()
        for i in range(self.num_of_players):
            print('Cards for player {player_num} {player_name} is {cards_dealt}'.format(player_num = i+1, player_name = self.players_list[i], cards_dealt = self.cards_dealt[i]))
        print("------------------------------")
        self.history_claim = []
        self.true_history = []
        self.current_rank_index = 0
        first_player_index = random.randint(0,self.num_of_players-1)
        self.first_player_index = first_player_index
        self.discard_player_index = first_player_index
        self.pile_on_table = []
        self.current_stage = ""
        self.current_hpt = [0] * self.num_of_players

    def begin_new_game(self):
        return self.init_game()

    def check_result(self,claim,truth):
        if claim == truth:
            return True
        else:
            return False

    def update_discarded_cards(self,player_num,discarded_cards):
        for card in discarded_cards:
            if card in self.cards_dealt[player_num]:
                self.cards_dealt[player_num].remove(card)
                self.pile_on_table.append(card)
            else:
                print("ERROR: Discard Wrong Cards")
                sys.exit()

        print("After update")
        print("Cards dealt: {cards_dealt}".format(cards_dealt = self.cards_dealt))
        print("Pile on table: {pile_on_table}".format(pile_on_table = self.pile_on_table))

    def update_challenge_cards(self,losing_player_num):
        for card in self.pile_on_table:
            self.cards_dealt[losing_player_num].append(card)
        self.pile_on_table = []
        print("After update")
        print("Cards dealt: {cards_dealt}".format(cards_dealt = self.cards_dealt))
        print("Pile on table: {pile_on_table}".format(pile_on_table = self.pile_on_table))

    def update_history(self,action):
        if action == True or action == False:
            self.history_claim.append(action)
        else:
            self.true_history.append(action)
            self.history_claim.append(len(action) * [self.one_deck[self.current_rank_index]])

        print("After update")
        print("History claim: {history_claim}".format(history_claim = self.history_claim))
        print("True history: {true_history}".format(true_history = self.true_history))

    def check_state(self):
        if len(self.history_claim) == 0:
            self.discard_player_index = (self.first_player_index + len(self.true_history)) % self.num_of_players
            self.current_rank_index = len(self.true_history)  % self.num_of_ranks
            self.current_tag = "D"
            return "The Game Begins"
        elif len(self.history_claim) % self.num_of_players == 0:
            self.discard_player_index = (self.first_player_index + len(self.true_history)) % self.num_of_players
            self.current_rank_index = len(self.true_history)  % self.num_of_ranks
            self.current_tag = "D"
            return "Discard phase"
        elif len(self.history_claim) % self.num_of_players >= 1:
                self.challenge_player_index = (self.discard_player_index + (len(self.history_claim) % self.num_of_players)) % self.num_of_players
                self.current_tag = "C"
                return "Challenge phase"
        else:
            print("ERROR: Check current state")
            sys.exit()

    def if_game_ends(self):
        self.hpt_player_index = 0
        game_should_end = None
        self.winning_tag = None
        for player in range(self.num_of_players):
            if self.current_hpt[player] == self.num_of_hpt:
                game_should_end = True
                self.hpt_player_index = player
        if game_should_end != True:
            if len(self.history_claim) != 0 and (len(self.history_claim) % self.num_of_players == 0):
                for i in range(self.num_of_players):
                    if len(self.cards_dealt[i]) == 0:
                        self.winning_tag = "Discarded all cards"
                        self.winning_player_index  = i
                        print(self.winning_tag)
                        print("Player {player_num} {player_name} discards all cards, so wins!".format(player_num = i +1, player_name = self.players_list[i]))
                        self.winning_number[i] += 1
                        return True
            return False
        self.winning_tag = "Hit point reached"
        print(self.winning_tag)
        print("Player {player_num} {player_name} hits {hpt} points, so loses!".format(player_num = self.hpt_player_index + 1, player_name = self.players_list[self.hpt_player_index],hpt = self.num_of_hpt))
        self.winning_number[(self.hpt_player_index+1) % 2] += 1
        return True

    def get_payoff(self,player_index):
        if self.winning_tag == "Discarded all cards":
            if player_index == self.winning_player_index:
                return 1.0
            else:
                return -1.0
        elif self.winning_tag == "Hit point reached":
            if player_index == self.hpt_player_index:
                return -1.0
            else:
                return 1.0
        else:
            print("ERROR: Game not ends!")
            sys.exit()

    def back_to_last_state(self,last_history,last_true_history,last_cards_dealt,last_pile_on_table,last_hpt_num):
        self.history_claim = last_history
        self.true_history = last_true_history
        self.cards_dealt = last_cards_dealt
        self.pile_on_table = last_pile_on_table
        self.current_hpt = last_hpt_num
        return

    def output_num_of_cards(self,cards_dealt):
        num_of_cards_list = []
        for cards in cards_dealt:
            num_of_cards_list.append(len(cards))
        return num_of_cards_list
    
    def play(self,num_of_total_games):
        for game in range(num_of_total_games):
            print("+++++++++++++++ Game {game_number} +++++++++++++++".format(game_number = game + 1))
            if self.Heuristic_switch == True:
                self.Heuristic_player.initialize_memo()

            self.begin_new_game()
            while self.if_game_ends() != True:
                if self.check_state() == "The Game Begins" or self.check_state() == "Discard phase":
                    # Discard
                    rank_state = "Current Rank: {current_rank}".format(current_rank = self.one_deck[self.current_rank_index])
                    player_state = "Current Discard Player: {current_player}".format(current_player = self.players_list[self.discard_player_index])
                    #print("-----------------------------------")
                    print(rank_state + "\n" + player_state)

                    if self.players_list[self.discard_player_index] == "Random player 1" or self.players_list[self.discard_player_index] == "Random player 2" or self.players_list[self.discard_player_index] == "Random player":
                        discard_cards = self.Random_player.discard(self.num_of_each_rank,self.cards_dealt[self.discard_player_index])
                    if self.players_list[self.discard_player_index] == "Heuristic player":
                        discard_cards = self.Heuristic_player.discard(self.cards_dealt[self.discard_player_index],self.one_deck[self.current_rank_index],self.one_deck[(self.current_rank_index + self.num_of_players) % self.num_of_ranks])
                    if self.players_list[self.discard_player_index] == "CFR player" or self.players_list[self.discard_player_index] == "CFR player 1" or self.players_list[self.discard_player_index] == "CFR player 2":
                        discard_cards = self.CFR_player.discard(self.num_of_each_rank,self.pile_on_table,self.cards_dealt,self.discard_player_index,self.current_tag,self.one_deck[self.current_rank_index])

                    print("Player {player_num} {player_name} discards {player_action}".format(player_num = self.discard_player_index + 1, player_name = self.players_list[self.discard_player_index],player_action = discard_cards))
                    
                    self.update_discarded_cards(self.discard_player_index,discard_cards)
                    self.update_history(discard_cards)

                    if self.Heuristic_switch == True:
                        self.Heuristic_player.update_memo("D",discard_cards,self.one_deck[self.current_rank_index],self.discard_player_index)


                elif self.check_state() == "Challenge phase":
                    
                    if self.players_list[self.challenge_player_index] == "Random player 1" or self.players_list[self.challenge_player_index] == "Random player 2" or self.players_list[self.challenge_player_index] == "Random player":
                        action = self.Random_player.challenge()
                    if self.players_list[self.challenge_player_index] == "Heuristic player":
                        #print(self.cards_dealt[self.discard_player_index])
                        action = self.Heuristic_player.challenge(self.cards_dealt,self.challenge_player_index,self.num_of_each_rank,self.one_deck[self.current_rank_index],discard_cards,self.discard_player_index)
                    if self.players_list[self.challenge_player_index] == "CFR player" or self.players_list[self.challenge_player_index] == "CFR player 1" or self.players_list[self.challenge_player_index] == "CFR player 2":
                        action = self.CFR_player.challenge(self.num_of_each_rank,self.pile_on_table,self.cards_dealt,self.challenge_player_index,self.current_tag,self.one_deck[self.current_rank_index])
                    
                    player_state = "Current Challenge Player: {current_player}".format(current_player = self.players_list[self.challenge_player_index])

                    print("Player {player_num} {player_name}'s choice is {player_action}".format(player_num = self.challenge_player_index + 1, player_name = self.players_list[self.challenge_player_index],player_action = action))
   
                    self.update_history(action)

                    if action == True:
                        if self.check_result(len(discard_cards) * [self.one_deck[self.current_rank_index]],discard_cards):
                            print("Challenges Fails. It's True!")
                            self.current_hpt[self.challenge_player_index] += 1
                            self.update_challenge_cards(self.challenge_player_index)
                            # Here is for Heuristic player memo update
                            if self.Heuristic_switch == True:
                                self.Heuristic_player.update_memo("C",discard_cards,self.one_deck[self.current_rank_index],self.challenge_player_index)
                        else:
                            print("Challenge Successes! It's a lie.")
                            self.current_hpt[self.discard_player_index] += 1
                            self.update_challenge_cards(self.discard_player_index)
                            # Here is for Heuristic player memo update
                            if self.Heuristic_switch == True:
                                self.Heuristic_player.update_memo("C",discard_cards,self.one_deck[self.current_rank_index],self.discard_player_index)
                    elif action == False:
                        pass
                    else:
                        print("ERROR: Check player's choice")
                        sys.exit()

                    print("Now Hit Points are {hit_points}".format(hit_points = self.current_hpt))

                
            print(self.current_hpt)

        for keys in self.winning_rate.keys():
            self.winning_rate[keys] = float(self.winning_number[keys]) / (game+1)

        print(self.winning_rate)
        print(self.winning_number)
        print(self.current_hpt)
        return self.winning_rate,self.current_hpt

# Setting base line - Random vs Heuristic
game1 = Cheat_w_hpt(num_of_ranks, num_of_cards_each_rank, num_of_cards_each_player, ["Random player"])