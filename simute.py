#run_time = simulate("pumpkin_6x6", Unlocks, {Items.Carrot : 10000000000, Items.Power : 1000000}, {}, -1, 10000)
run_time = simulate("test_rank", Unlocks, {Items.Carrot : 10000000000, Items.Power : 0,Items.Pumpkin : 0,Items.Power:1000000}, {}, -1, 1)
print(run_time)