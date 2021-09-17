from HP_Aware_base import *

import matplotlib.pyplot as plt

# vs Random
game01 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],1,["Save_for_paper/Data","HPA_4"])

game02 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],2,["Save_for_paper/Data","HPA_4"])

game03 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],3,["Save_for_paper/Data","HPA_4"])

game04 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],4,["Save_for_paper/Data","HPA_4"])

game05 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],5,["Save_for_paper/Data","HPA_4"])

game06 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],6,["Save_for_paper/Data","HPA_4"])

game07 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],7,["Save_for_paper/Data","HPA_4"])

game08 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],10,["Save_for_paper/Data","HPA_4"])

game09 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],100,["Save_for_paper/Data","HPA_4"])

game10 = Cheat_w_hpt(7,4,6,["Random player","CFR player"],100,["Save_for_paper/Data","HPA_4"])

# vs Heuristic
game1 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],1,["Save_for_paper/Data","HPA_4"])

game2 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],2,["Save_for_paper/Data","HPA_4"])

game3 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],3,["Save_for_paper/Data","HPA_4"])

game4 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],4,["Save_for_paper/Data","HPA_4"])

game5 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],5,["Save_for_paper/Data","HPA_4"])

game6 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],6,["Save_for_paper/Data","HPA_4"])

game7 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],7,["Save_for_paper/Data","HPA_4"])

game8 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],10,["Save_for_paper/Data","HPA_4"])

game9 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],100,["Save_for_paper/Data","HPA_4"])

game100 = Cheat_w_hpt(7,4,6,["Heuristic player","CFR player"],100,["Save_for_paper/Data","HPA_4"])

num_of_test_games = 10000

random_win_rates = []
heuristic_win_rates = []

random_win_rates.append(game01.play(num_of_test_games)[0][1])
random_win_rates.append(game02.play(num_of_test_games)[0][1])
random_win_rates.append(game03.play(num_of_test_games)[0][1])
random_win_rates.append(game04.play(num_of_test_games)[0][1])
random_win_rates.append(game05.play(num_of_test_games)[0][1])
random_win_rates.append(game06.play(num_of_test_games)[0][1])
random_win_rates.append(game07.play(num_of_test_games)[0][1])
random_win_rates.append(game08.play(num_of_test_games)[0][1])
random_win_rates.append(game09.play(num_of_test_games)[0][1])
random_win_rates.append(game10.play(num_of_test_games)[0][1])


heuristic_win_rates.append(game1.play(num_of_test_games)[0][1])
heuristic_win_rates.append(game2.play(num_of_test_games)[0][1])
heuristic_win_rates.append(game3.play(num_of_test_games)[0][1])
heuristic_win_rates.append(game4.play(num_of_test_games)[0][1])
heuristic_win_rates.append(game5.play(num_of_test_games)[0][1])
heuristic_win_rates.append(game6.play(num_of_test_games)[0][1])
heuristic_win_rates.append(game7.play(num_of_test_games)[0][1])
heuristic_win_rates.append(game8.play(num_of_test_games)[0][1])
heuristic_win_rates.append(game9.play(num_of_test_games)[0][1])
heuristic_win_rates.append(game100.play(num_of_test_games)[0][1])

xa = ['HP-1','HP-2','HP-3','HP-4','HP-5','HP-6','HP-7','HP-10','HP-100','         Large Game']

#bar_width = 0.3

#b1 = plt.bar([i for i in range(len(xa))],random_win_rates,width = bar_width,color = 'b',label = 'CFR vs Random')
#b2 = plt.bar([i+bar_width for i in range(len(xa))],heuristic_win_rates,width = bar_width,color = 'g',label = 'CFR vs Heuristic')

x_a = [i for i in range(len(random_win_rates))]

plt.margins(0.08)

l1 = plt.plot(x_a,random_win_rates,marker='o',color = 'b',label = 'CFR vs Random')
l2 = plt.plot(x_a,heuristic_win_rates,marker='o',color = 'g',label = 'CFR vs Heuristic')

plt.xlabel("Game Environment")
plt.xticks(x_a , xa)
plt.ylabel("Winning Rate")
plt.title("Winning rates of HP-Aware4 in different game environments")
plt.grid(axis='y')
for x,y in zip(x_a,random_win_rates):
    plt.text(x,y+0.01,'%.3f' % y,ha='center', va= 'bottom',fontsize = 12)
for x,y in zip(x_a,heuristic_win_rates):
    plt.text(x,y+0.01,'%.3f' % y,ha='center', va= 'bottom',fontsize = 12)
plt.legend(loc = 1)
plt.savefig("Save_for_paper/Figures/HPA_4_compare_bots")
plt.show()