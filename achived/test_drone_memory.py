# 测试无人机内存共享机制
# 目标：验证引用类型（列表、字典）在无人机间的行为

# 测试1：全局变量（预期：不共享）
test1_result = "Test 1 - Global Variable:"
global_counter = 0

def increment_global():
    global global_counter
    global_counter += 1
    return global_counter

if num_unlocked(Unlocks.Megafarm) > 0:
    drone1 = spawn_drone(increment_global)
    result1 = wait_for(drone1)
    quick_print(test1_result)
    quick_print("  Drone returned:", result1)
    quick_print("  Global counter:", global_counter)
    quick_print("  Expected: returned=1, global=0 (not shared)")
else:
    quick_print("Megafarm not unlocked, skipping tests")

# 测试2：列表引用（关键测试）
test2_result = "Test 2 - List Reference:"
shared_list = [0, 0, 0]

def modify_list():
    # 尝试修改传入的列表
    shared_list[0] = 100
    shared_list[1] = 200
    shared_list.append(300)
    return shared_list

if num_unlocked(Unlocks.Megafarm) > 0:
    quick_print(test2_result)
    quick_print("  Before spawn:", shared_list)
    
    drone2 = spawn_drone(modify_list)
    result2 = wait_for(drone2)
    
    quick_print("  Drone returned:", result2)
    quick_print("  Original list:", shared_list)
    quick_print("  Expected: If shared, list=[100,200,0,300]")
    quick_print("  Expected: If copied, list=[0,0,0]")

# 测试3：字典引用
test3_result = "Test 3 - Dictionary Reference:"
shared_dict = {"count": 0, "value": 10}

def modify_dict():
    shared_dict["count"] = 999
    shared_dict["new_key"] = 888
    return shared_dict

if num_unlocked(Unlocks.Megafarm) > 0:
    quick_print(test3_result)
    quick_print("  Before spawn:", shared_dict)
    
    drone3 = spawn_drone(modify_dict)
    result3 = wait_for(drone3)
    
    quick_print("  Drone returned:", result3)
    quick_print("  Original dict:", shared_dict)

# 测试4：通过参数传递引用（使用闭包）
test4_result = "Test 4 - Closure with List:"
closure_list = [1, 2, 3]

def create_modifier():
    def modifier():
        closure_list[0] = 999
        closure_list.append(888)
        return closure_list
    return modifier

if num_unlocked(Unlocks.Megafarm) > 0:
    quick_print(test4_result)
    quick_print("  Before spawn:", closure_list)
    
    modifier_func = create_modifier()
    drone4 = spawn_drone(modifier_func)
    result4 = wait_for(drone4)
    
    quick_print("  Drone returned:", result4)
    quick_print("  Original list:", closure_list)
    quick_print("  Expected: If closure works, list=[999,2,3,888]")

# 测试5：多个无人机同时修改同一列表
test5_result = "Test 5 - Multiple Drones:"
multi_list = [0, 0, 0, 0, 0]

def modify_at_index():
    # 每个无人机修改不同的索引
    index = len(multi_list) % 5  # 简单的分配策略
    multi_list[index] = 777
    return index

if num_unlocked(Unlocks.Megafarm) > 0:
    quick_print(test5_result)
    quick_print("  Before spawn:", multi_list)
    
    drones = []
    for i in range(min(3, max_drones())):
        drone = spawn_drone(modify_at_index)
        if drone:
            drones.append(drone)
    
    results = []
    for drone in drones:
        result = wait_for(drone)
        results.append(result)
    
    quick_print("  Drones modified indices:", results)
    quick_print("  Final list:", multi_list)
    quick_print("  Expected: If shared, some values=777")

# 测试6：返回值测试
test6_result = "Test 6 - Return Value Communication:"

def create_data():
    new_list = [100, 200, 300]
    new_dict = {"x": 10, "y": 20}
    return [new_list, new_dict]

if num_unlocked(Unlocks.Megafarm) > 0:
    quick_print(test6_result)
    
    drone6 = spawn_drone(create_data)
    result6 = wait_for(drone6)
    
    quick_print("  Received from drone:", result6)
    quick_print("  This should work: drones can return data")

# 最终总结
quick_print("")
quick_print("=== Test Summary ===")
quick_print("Testing complete. Review the results above.")
quick_print("Key observations:")
quick_print("1. Global variables: Each drone has its own copy")
quick_print("2. Reference types: Check if they are shared or copied")
quick_print("3. Return values: Always work for data passing")

