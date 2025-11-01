clear()
#run_time = simulate("pumpkin_8x8", Unlocks, {Items.Carrot : 10000000000, Items.Power : 1000000}, {}, 999, 1)
run_time = simulate("pumpkin_v11", Unlocks, {Items.Carrot : 10000000000, Items.Power : 0,Items.Pumpkin : 0,Items.Power:1000000,Items.Pumpkin:0}, {}, 9999, 0.2)
# print(run_time)

#run_time = simulate("test_rank", Unlocks, {Items.Carrot : 10000000000, Items.Power : 0,Items.Pumpkin : 0,Items.Power:1000000,Items.Pumpkin:0}, {}, 10, 1000)
print(run_time)