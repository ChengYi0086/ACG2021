from Memoryless_OS_MCCFR_base_test_2 import *
import matplotlib.pyplot as plt
import time

# Random player
# Heuristic player
# CFR player

num_of_train_iterations = 1000
num_of_big_iterations = 100
# total training iterations = big iterations * train iterations
num_of_test_games = 1000

# Random vs Heuristic
game1 = Cheat_w_hpt(3,2,2,["Random player","Heuristic player"],4,["Save_for_paper/Data","M_OS_MCCFR_4_2"])


heuristic_against_random = game1.play(num_of_test_games)[0][1]

train_time_list = []
num_of_infoset_list = []
winning_vs_random_list = []
winning_vs_heuristic_list = []

init_time = time.time()
print("init_time",init_time)
#train_time_list.append(init_time)

game3 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],4,["Save_for_paper/Data","M_OS_MCCFR_4_2"])
    # Heuristic vs CFR
game4 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],4,["Save_for_paper/Data","M_OS_MCCFR_4_2"])

winning_vs_random_list.append(game3.play(num_of_test_games)[0][1])
winning_vs_heuristic_list.append(game4.play(num_of_test_games)[0][1])

init_time = 0

for _ in range(num_of_big_iterations):
    print("This is {big_iter}th big iteration".format(big_iter = _ +1))
    # CFR training
    game2 = Cheat_w_hpt(3,2,2,["CFR player 1","CFR player 2"],4,["Save_for_paper/Data","M_OS_MCCFR_4_2"])

    # ----------- Training Part ----------- 
    CFR_trainer = Cheat_w_hpt_Trainer(game2,"Save_for_paper/Data","M_OS_MCCFR_4_2")
    util, time_list, infoset_list = CFR_trainer.train(num_of_train_iterations)

    for time_cost in time_list:
        train_time_list.append(time_cost + init_time)

    for num_infoset in infoset_list:
        num_of_infoset_list.append(num_infoset)

    # ----------- Testing Part -----------
    game3 = Cheat_w_hpt(3,2,2,["Random player","CFR player"],4,["Save_for_paper/Data","M_OS_MCCFR_4_2"])
    # Heuristic vs CFR
    game4 = Cheat_w_hpt(3,2,2,["Heuristic player","CFR player"],4,["Save_for_paper/Data","M_OS_MCCFR_4_2"])

    winning_vs_random_list.append(game3.play(num_of_test_games)[0][1])
    winning_vs_heuristic_list.append(game4.play(num_of_test_games)[0][1])

    init_time = train_time_list[-1]

print(train_time_list)
print(num_of_infoset_list)
print(winning_vs_random_list)
print(winning_vs_heuristic_list)

# ----------- Ploting -----------
# Training time
plt.xlabel("Iterations")
l1 = plt.plot([i for i in range(num_of_train_iterations * num_of_big_iterations)], train_time_list)
plt.title('Time Cost')
#plt.yscale('log')
plt.savefig("Save_for_paper/Figures/M_OS_MCCFR_4_2_100iter_Training_time")
plt.show()

# Number of infosets
plt.xlabel("Iterations")
l2 = plt.plot([i for i in range(num_of_train_iterations * num_of_big_iterations)], num_of_infoset_list)
plt.title('Number of Infosets')
plt.savefig("Save_for_paper/Figures/M_OS_MCCFR_4_2_100iter_Number_of_infosets")
plt.show()

# Winning rate
l3 = plt.axhline(y=heuristic_against_random,color = 'r',label = "Heuristic vs Random")
plt.xlabel("Iterations")
l4 = plt.plot([i * num_of_train_iterations for i in range(num_of_big_iterations + 1)], winning_vs_random_list,label = "CFR vs Random")
l5 = plt.plot([i * num_of_train_iterations for i in range(num_of_big_iterations + 1)], winning_vs_heuristic_list,label = "CFR vs Heuristic")
plt.title("Winning rates against Bot players")
plt.legend(loc = 0)
plt.savefig("Save_for_paper/Figures/M_OS_MCCFR_4_2_100iter_Winning_rates")
plt.show()
