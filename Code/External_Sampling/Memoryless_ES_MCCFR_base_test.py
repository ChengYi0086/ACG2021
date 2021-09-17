
# Here is the code for Outcome-Samping Monte Carlo Counterfactual Regret Minimization
# for the game Cheat for the Memoryless agent #


import  random,sys,copy,ast,os,pickle,time

from itertools import combinations
import numpy as np

# Information sets
    # infoset = [
    # 0 self.num_of_each_rank,
    # 1 len(self.pile_on_table),
    # 2 self.output_num_of_cards(self.cards_dealt),
    # 3 sorted(self.cards_dealt[self.discard/challenge_player_index]),
    # 4 Discard/Challenge Tag   <---- New!
    # 5 self.current_rank]


class Random_player_w_hpt():
    def __init__(self):
        self.name = "Random player"

    def discard(self,num_of_each_rank,cards_in_hand):
        comb = []
        for i in range(num_of_each_rank):
            for combination in combinations(cards_in_hand,i+1):
                comb.append(list(combination))
        action = random.choice(comb)
        return action

    def challenge(self):
        return random.choice([True,False])

class Heuristic_player_w_hpt():
    # Heuristic player keeps a record of certain cards which are available to all players
    def __init__(self,num_of_player,my_index):
        self.name = "Heuristic player"
        self.num_of_player = num_of_player
        self.my_index = my_index
        self.initialize_memo()

    def initialize_memo(self):
        self.cards_dealt_memo = []
        for _ in range(self.num_of_player):
            self.cards_dealt_memo.append([])
        self.pile_on_table_memo = []

    def update_memo(self,D_or_C_tag,true_cards,current_rank,player_index):
        # Here we update when: 
        # 1. Challenge happens and someone got the cards on the table
        # 2. Heuristic player itself discards cards #
        if D_or_C_tag == "D":
            if player_index == self.my_index:
                self.pile_on_table_memo += true_cards
            else:
                if current_rank in self.cards_dealt_memo[player_index]:
                    self.cards_dealt_memo[player_index].remove(current_rank)
                #self.pile_on_table_memo += [current_rank] * len(true_cards)
        if D_or_C_tag == "C":
            if player_index == self.my_index:
                self.pile_on_table_memo = []
            else:
                for card in true_cards:
                    self.cards_dealt_memo[player_index].append(card)
                    self.pile_on_table_memo = []
        return

    def discard(self,cards_in_hand,current_rank,next_rank):
        my_cards = copy.deepcopy(cards_in_hand)
        num_my_cards = len(cards_in_hand)
        num_my_correct_cards = cards_in_hand.count(current_rank)
        num_next_my_rank = cards_in_hand.count(next_rank)

        if num_my_cards == num_my_correct_cards:
            return cards_in_hand
        elif num_my_correct_cards > 0:
            return random.sample([current_rank]*num_my_correct_cards,random.randint(1,num_my_correct_cards))
        elif num_my_correct_cards == 0 and num_next_my_rank != 0:
            for card in my_cards:
                if card != next_rank:
                    my_cards.remove(card)
            return [random.choice(my_cards)]
        else:
            return [random.choice(cards_in_hand)]

    def challenge(self,cards_dealt,player_index,num_of_each_rank,current_rank,current_claim,discard_player_index):
        num_in_my_hand = cards_dealt[player_index].count(current_rank)
        num_in_pile = self.pile_on_table_memo.count(current_rank)
        num_claimed = len(current_claim)
        num_at_most = num_of_each_rank

        if self.cards_dealt_memo[discard_player_index].count(current_rank) >= num_claimed:
            #print("1st")
            return False
        elif len(cards_dealt[discard_player_index]) == 0:
            #print("2nd")
            return True
        elif num_in_my_hand + num_claimed + num_in_pile > num_at_most:
            #print("3rd")
            return True
        else:
            #print("4rd")
            return random.choice([True,False])

class InfoSet():
    # infoset = [
    # 0 self.num_of_each_rank,
    # 1 len(self.pile_on_table),
    # 2 self.output_num_of_cards(self.cards_dealt),
    # 3 sorted(self.cards_dealt[self.discard/challenge_player_index]),
    # 4 Discard/Challenge Tag   <---- New!
    # 5 self.current_rank]

    def __init__(self,infoset):
        self.infoset = infoset
        self.actions_list = self.getActions()
        self.total = len(self.actions_list)
        self.regretSum = np.zeros(self.total)
        self.strategySum = np.zeros(self.total)
        
    def getActions(self):
        action_tag = self.infoset.split(";")[4]
        #action_tag = ast.literal_eval(self.infoset.split(";")[4])
        my_cards = ast.literal_eval(self.infoset.split(";")[3])
        num_of_each_rank = ast.literal_eval(self.infoset.split(";")[0])
        if action_tag == "D":
            actions_list = []
            for i in range(num_of_each_rank):
                for combination in combinations(my_cards,i+1):
                    if list(combination) not in actions_list:
                        actions_list.append(list(combination))
        elif action_tag == "C":
            actions_list = [True,False]
        else:
            print("ERROR: Check CFR player action phase")
            sys.exit()
        return actions_list

    def getStrategy(self,reach_prob):
        regretSum = self.regretSum
        positive_regret = np.maximum(0, regretSum)
        sum_regret = sum(positive_regret)
        strategy = positive_regret/sum_regret if sum_regret > 0 else np.ones(self.total)/self.total
        self.strategySum += reach_prob * strategy
        return strategy

    def getAverageStrategy(self):
        sum_strategy = np.sum(self.strategySum)
        avg_strategy = self.strategySum/sum_strategy if sum_strategy > 0 else np.ones(self.total)/self.total
        return avg_strategy

    def getActionfromStrategy(self):
        rr = random.random()
        avg_strategy = self.getAverageStrategy()
        action_index = np.searchsorted(np.cumsum(avg_strategy),rr)
        action_list = self.getActions()
        return action_list[action_index]

class Cheat_w_hpt_Player():
    def __init__(self,folder_name,infoset_file_name):
        self.name = "CFR player"

        def load_obj(folder,file):
            path = os.path.exists(folder + '/' + file + '.pkl')
            if path == True:
                with open(folder_name + '/' + infoset_file_name + '.pkl', 'rb') as f:
                    return pickle.load(f)
            else:
                print("ERROR: No such File")
                return {}

        self.infoset_map = load_obj(folder_name,infoset_file_name)


    def get_infoset(self,information):
        # Here: information should be a string
        if information not in self.infoset_map:
            self.infoset_map[information] = InfoSet(information)
        return self.infoset_map[information]

    def join_a_string(self,seq):
        string_seq = []
        for i in seq:
            string_seq.append(str(i))
        result = ";".join(string_seq)
        return result

    def output_num_of_cards(self,cards_dealt):
        num_of_cards_list = []
        for cards in cards_dealt:
            num_of_cards_list.append(len(cards))
        return num_of_cards_list

    def discard(self,num_of_each_rank,pile_on_table,cards_dealt,player_index,current_tag,current_rank):
        info = self.join_a_string([num_of_each_rank,len(pile_on_table),self.output_num_of_cards(cards_dealt),cards_dealt[player_index],current_tag,current_rank])
        infoset = self.get_infoset(info)

        action = infoset.getActionfromStrategy()
        return action

    def challenge(self,num_of_each_rank,pile_on_table,cards_dealt,player_index,current_tag,current_rank):
        info = self.join_a_string([num_of_each_rank,len(pile_on_table),self.output_num_of_cards(cards_dealt),cards_dealt[player_index],current_tag,current_rank])
        infoset = self.get_infoset(info)

        action = infoset.getActionfromStrategy()
        return action

class Cheat_w_hpt_Trainer():
    def __init__(self,game,folder_name,infoset_file_name):
        self.name = "CFR player"
        self.folder_name = folder_name
        self.infoset_file_name = infoset_file_name
        self.game = game

        def load_obj(folder_name,file_name):
            path = os.path.exists(folder_name + '/' + file_name + '.pkl')
            if path == True:
                with open(folder_name + '/' + file_name + '.pkl', 'rb') as f:
                    return pickle.load(f)
            else:
                print("No such file exist")
                return {}

        self.infoset_map = load_obj(self.folder_name,self.infoset_file_name)
        #self.whole_infoset_list = self.infoset_map.keys()

    def get_infoset(self,information):
        # Here: information should be a string
        if information not in self.infoset_map:
            self.infoset_map[information] = InfoSet(information)
        return self.infoset_map[information]

    def join_a_string(self,seq):
        string_seq = []
        for i in seq:
            string_seq.append(str(i))
        result = ";".join(string_seq)
        return result

    def output_num_of_cards(self,cards_dealt):
        num_of_cards_list = []
        for cards in cards_dealt:
            num_of_cards_list.append(len(cards))
        return num_of_cards_list

    def CFR(self,reach_probs,player_index):
        # Here we only sample one path of history
        # we iterate the player interchangably #

        # infoset = [
            # 0 self.num_of_each_rank,
            # 1 len(self.pile_on_table),
            # 2 self.output_num_of_cards(self.cards_dealt),
            # 3 sorted(self.cards_dealt[self.discard/challenge_player_index]),
            # 4 Discard/Challenge Tag   <---- New!
            # 5 self.current_rank]

        if self.game.if_game_ends() == True:
            return self.game.get_payoff(player_index)
        else:
            #print(self.game.check_state())
            if self.game.check_state() == "The Game Begins" or self.game.check_state() == "Discard phase":
                # Clarify the infoset #######################
                self.game.check_state()
                info = self.join_a_string([self.game.num_of_each_rank,len(self.game.pile_on_table),self.output_num_of_cards(self.game.cards_dealt),self.game.cards_dealt[self.game.discard_player_index],self.game.current_tag,self.game.one_deck[self.game.current_rank_index]])

                #print("info, ",info)
                infoset = self.get_infoset(info)
                #############################################
                infoset_value = 0

                if self.game.discard_player_index != player_index:
                    #print("Here we do NOT update")

                    # Sample an action
                    chosen_action = infoset.getActionfromStrategy()
                    #chosen_index = infoset.getActions().index(chosen_action)

                    # Update the game
                    self.game.update_discarded_cards(self.game.discard_player_index,chosen_action)
                    self.game.update_history(chosen_action)
                    self.discard_cards = chosen_action

                    infoset_value = self.CFR(reach_probs,player_index)

                    for index,action in enumerate(infoset.getActions()):
                        strategy = infoset.getStrategy(reach_probs[player_index])

                    return infoset_value

                elif self.game.discard_player_index == player_index:
                    #print("Here we UPDATE")

                    # Save the temp game state
                    temp_history = copy.deepcopy(self.game.history_claim)
                    temp_true_history = copy.deepcopy(self.game.true_history)
                    temp_cards_dealt = copy.deepcopy(self.game.cards_dealt)
                    temp_pile_on_table = copy.deepcopy(self.game.pile_on_table)
                    temp_hit_point = copy.deepcopy(self.game.current_hpt)

                    strategy = infoset.getStrategy(reach_probs[player_index])
                    counterfactual_values = np.zeros(len(infoset.getActions()))

                    for index,action in enumerate(infoset.getActions()):

                        # Update the game
                        self.game.update_discarded_cards(player_index,action)
                        self.game.update_history(action)
                        self.discard_cards = action

                        temp_temp_history = copy.deepcopy(temp_history)
                        temp_temp_true_history = copy.deepcopy(temp_true_history)
                        temp_temp_cards_dealt = copy.deepcopy(temp_cards_dealt)
                        temp_temp_pile_on_table = copy.deepcopy(temp_pile_on_table)
                        temp_temp_hit_point = copy.deepcopy(temp_hit_point)

                        counterfactual_values[index] = self.CFR(reach_probs,player_index)
                        infoset_value += strategy[index] * counterfactual_values[index]

                        self.game.back_to_last_state(temp_temp_history,temp_temp_true_history,temp_temp_cards_dealt,temp_temp_pile_on_table,temp_temp_hit_point)

                    #infoset_value = counterfactual_values.dot(strategy)

                    for index,action in enumerate(infoset.getActions()):
                        infoset.regretSum[index] += counterfactual_values[index] - infoset_value

                    return infoset_value

                else:
                    print("ERROR: Check training - discard phase")
                    sys.exit()

            elif self.game.check_state() == "Challenge phase":
                # Clarify the infoset #######################
                self.game.check_state()
                info = self.join_a_string([self.game.num_of_each_rank,len(self.game.pile_on_table),self.output_num_of_cards(self.game.cards_dealt),self.game.cards_dealt[self.game.challenge_player_index],self.game.current_tag,self.game.one_deck[self.game.current_rank_index]])

                #print("info, ",info)
                infoset = self.get_infoset(info)
                #############################################
                infoset_value = 0

                if self.game.challenge_player_index != player_index:
                    #print("Here we do NOT update")

                    # Sample an action
                    chosen_action = infoset.getActionfromStrategy()
                    #chosen_index = infoset.getActions().index(chosen_action)

                    # Update the game
                    self.game.update_history(chosen_action)

                    if chosen_action == True:
                        if self.game.check_result(len(self.discard_cards) * [self.game.one_deck[self.game.current_rank_index]],self.discard_cards):
                            #print("Challenges Fails. It's True!")
                            self.game.current_hpt[self.game.challenge_player_index] += 1
                            self.game.update_challenge_cards(self.game.challenge_player_index)
                        else:
                            #print("Challenge Successes! It's a lie.")
                            self.game.current_hpt[(self.game.challenge_player_index +1)%2] += 1
                            self.game.update_challenge_cards(self.game.discard_player_index)

                    infoset_value = self.CFR(reach_probs,player_index)

                    for index,action in enumerate(infoset.getActions()):
                        strategy = infoset.getStrategy(reach_probs[player_index])

                    return infoset_value

                elif self.game.challenge_player_index == player_index:
                    #print("Here we UPDATE")

                    temp_history = copy.deepcopy(self.game.history_claim)
                    temp_true_history = copy.deepcopy(self.game.true_history)
                    temp_cards_dealt = copy.deepcopy(self.game.cards_dealt)
                    temp_pile_on_table = copy.deepcopy(self.game.pile_on_table)
                    temp_hit_point = copy.deepcopy(self.game.current_hpt)

                    strategy = infoset.getStrategy(reach_probs[player_index])
                    counterfactual_values = np.zeros(len(infoset.getActions()))

                    for index,action in enumerate(infoset.getActions()):
                        # Update the game
                        self.game.update_history(action)

                        if action == True:
                            if self.game.check_result(len(self.discard_cards) * [self.game.one_deck[self.game.current_rank_index]],self.discard_cards):
                            #print("Challenges Fails. It's True!")
                                self.game.current_hpt[player_index] += 1
                                self.game.update_challenge_cards(self.game.challenge_player_index)
                            else:
                                #print("Challenge Successes! It's a lie.")
                                self.game.current_hpt[(player_index +1)%2] += 1
                                self.game.update_challenge_cards(self.game.discard_player_index)

                        temp_temp_history = copy.deepcopy(temp_history)
                        temp_temp_true_history = copy.deepcopy(temp_true_history)
                        temp_temp_cards_dealt = copy.deepcopy(temp_cards_dealt)
                        temp_temp_pile_on_table = copy.deepcopy(temp_pile_on_table)
                        temp_temp_hit_point = copy.deepcopy(temp_hit_point)

                        counterfactual_values[index] = self.CFR(reach_probs,player_index)
                        infoset_value += strategy[index] * counterfactual_values[index]

                        self.game.back_to_last_state(temp_temp_history,temp_temp_true_history,temp_temp_cards_dealt,temp_temp_pile_on_table,temp_temp_hit_point)

                    #infoset_value = counterfactual_values.dot(strategy)

                    for index,action in enumerate(infoset.getActions()):
                        infoset.regretSum[index] += counterfactual_values[index] - infoset_value

                    return infoset_value

                else:
                    print("ERROR: Check training - challenge phase")
                    sys.exit()                    

            else:
                print("ERROR: CFR not aware the state")
                sys.exit()

    def save_obj(self,obj,folder_name,file_name):
        with open(folder_name + '/' + file_name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def train(self,iterations):
        util = 0
        time_list = []
        whole_infoset_list = []
        train_begin_time = time.time()
        self.train_begin_time = copy.deepcopy(train_begin_time)
        for iter in range(iterations):
            print("Here is {num}th iterations".format(num = iter+1))
            len_of_infoset_list = len(self.infoset_map.keys())
            self.game.begin_new_game()
            reach_probs = np.ones(2)
            for player_index in range(2):
                util += self.CFR(reach_probs,player_index)
            one_iteration_end_time = time.time()
            #print("one iteration end time",one_iteration_end_time)
            #print(self.train_begin_time)
            one_iteration_time = one_iteration_end_time - self.train_begin_time
            #print("one iteration time",one_iteration_time)
            time_list.append(one_iteration_time)
            whole_infoset_list.append(len_of_infoset_list)

        self.save_obj(self.infoset_map,self.folder_name,self.infoset_file_name)
        
        return util,time_list,whole_infoset_list

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
        #print("New Game Starts!")
        self.cards_dealt = self.deal_cards()
        #for i in range(self.num_of_players):
            #print('Cards for player {player_num} {player_name} is {cards_dealt}'.format(player_num = i+1, player_name = self.players_list[i], cards_dealt = self.cards_dealt[i]))
        #print("------------------------------")
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

        #print("After update")
        #print("Cards dealt: {cards_dealt}".format(cards_dealt = self.cards_dealt))
        #print("Pile on table: {pile_on_table}".format(pile_on_table = self.pile_on_table))

    def update_challenge_cards(self,losing_player_num):
        for card in self.pile_on_table:
            self.cards_dealt[losing_player_num].append(card)
        self.pile_on_table = []
        #print("After update")
        #print("Cards dealt: {cards_dealt}".format(cards_dealt = self.cards_dealt))
        #print("Pile on table: {pile_on_table}".format(pile_on_table = self.pile_on_table))

    def update_history(self,action):
        if action == True or action == False:
            self.history_claim.append(action)
        else:
            self.true_history.append(action)
            self.history_claim.append(len(action) * [self.one_deck[self.current_rank_index]])

        #print("After update")
        #print("History claim: {history_claim}".format(history_claim = self.history_claim))
        #print("True history: {true_history}".format(true_history = self.true_history))

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
                        #print("Player {player_num} {player_name} discards all cards, so wins!".format(player_num = i +1, player_name = self.players_list[i]))
                        self.winning_number[i] += 1
                        return True
            return False
        self.winning_tag = "Hit point reached"
        print(self.winning_tag)
        #print("Player {player_num} {player_name} hits {hpt} points, so loses!".format(player_num = self.hpt_player_index + 1, player_name = self.players_list[self.hpt_player_index],hpt = self.num_of_hpt))
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
                    #print(rank_state + "\n" + player_state)

                    if self.players_list[self.discard_player_index] == "Random player 1" or self.players_list[self.discard_player_index] == "Random player 2" or self.players_list[self.discard_player_index] == "Random player":
                        discard_cards = self.Random_player.discard(self.num_of_each_rank,self.cards_dealt[self.discard_player_index])
                    if self.players_list[self.discard_player_index] == "Heuristic player":
                        discard_cards = self.Heuristic_player.discard(self.cards_dealt[self.discard_player_index],self.one_deck[self.current_rank_index],self.one_deck[(self.current_rank_index + self.num_of_players) % self.num_of_ranks])
                    if self.players_list[self.discard_player_index] == "CFR player" or self.players_list[self.discard_player_index] == "CFR player 1" or self.players_list[self.discard_player_index] == "CFR player 2":
                        discard_cards = self.CFR_player.discard(self.num_of_each_rank,self.pile_on_table,self.cards_dealt,self.discard_player_index,self.current_tag,self.one_deck[self.current_rank_index])

                    #print("Player {player_num} {player_name} discards {player_action}".format(player_num = self.discard_player_index + 1, player_name = self.players_list[self.discard_player_index],player_action = discard_cards))
                    
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

                    #print("Player {player_num} {player_name}'s choice is {player_action}".format(player_num = self.challenge_player_index + 1, player_name = self.players_list[self.challenge_player_index],player_action = action))
   
                    self.update_history(action)

                    if action == True:
                        if self.check_result(len(discard_cards) * [self.one_deck[self.current_rank_index]],discard_cards):
                            #print("Challenges Fails. It's True!")
                            self.current_hpt[self.challenge_player_index] += 1
                            self.update_challenge_cards(self.challenge_player_index)
                            # Here is for Heuristic player memo update
                            if self.Heuristic_switch == True:
                                self.Heuristic_player.update_memo("C",discard_cards,self.one_deck[self.current_rank_index],self.challenge_player_index)
                        else:
                            #print("Challenge Successes! It's a lie.")
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

                    #print("Now Hit Points are {hit_points}".format(hit_points = self.current_hpt))

                
            #print(self.current_hpt)

        for keys in self.winning_rate.keys():
            self.winning_rate[keys] = float(self.winning_number[keys]) / (game+1)

        #print(self.winning_rate)
        #print(self.winning_number)
        #print(self.current_hpt)
        return self.winning_rate,self.current_hpt

    