# The Farmer Was Replaced - 多无人机向日葵能量农场
# 策略：并行种植和扫描，快速收获能量

from farm_utils import goto_pos, optimize_path

SIZE = get_world_size()

# 无人机种植函数：处理一个区域
def drone_plant_region(x_start, x_end, y_start, y_end):
    planted_count = 0
    
    for y in range(y_start, y_end):
        for x in range(x_start, x_end):
            goto_pos(x, y)
            
            # 收割旧作物
            if can_harvest():
                harvest()
            
            # 翻土（向日葵需要土壤）
            if get_ground_type() != Grounds.Soil:
                till()
            
            # 种植向日葵
            plant(Entities.Sunflower)
            planted_count = planted_count + 1
    
    return planted_count

# 并行初始化农场
def initialize_farm_mega():
    quick_print("多无人机初始化农场...")
    
    # 计算区域划分
    max_d = max_drones()
    regions = []
    
    if max_d >= 4:
        # 4个无人机：2x2划分
        half = SIZE // 2
        regions = [
            (0, half, 0, half),
            (half, SIZE, 0, half),
            (0, half, half, SIZE),
            (half, SIZE, half, SIZE)
        ]
    elif max_d >= 2:
        # 2个无人机：水平划分
        half = SIZE // 2
        regions = [
            (0, SIZE, 0, half),
            (0, SIZE, half, SIZE)
        ]
    else:
        # 单无人机：整个农场
        regions = [(0, SIZE, 0, SIZE)]
    
    # 启动无人机
    drones = []
    total_planted = 0
    
    for i in range(len(regions)):
        x_start, x_end, y_start, y_end = regions[i]
        
        def create_task(xs, xe, ys, ye):
            def task():
                return drone_plant_region(xs, xe, ys, ye)
            return task
        
        task_func = create_task(x_start, x_end, y_start, y_end)
        
        if i < len(regions) - 1:
            drone = spawn_drone(task_func)
            if drone:
                drones.append(drone)
            else:
                count = task_func()
                total_planted = total_planted + count
        else:
            count = task_func()
            total_planted = total_planted + count
    
    # 等待所有无人机完成
    for drone in drones:
        count = wait_for(drone)
        if count:
            total_planted = total_planted + count
    
    quick_print("初始化完成：" + str(total_planted) + " 株向日葵")

# 无人机扫描函数：扫描一个区域的向日葵
def drone_scan_region(x_start, x_end, y_start, y_end):
    # 返回：(花瓣数, 位置) 的列表
    sunflowers = []
    
    for y in range(y_start, y_end):
        for x in range(x_start, x_end):
            goto_pos(x, y)
            
            if get_entity_type() == Entities.Sunflower and can_harvest():
                petals = measure()
                sunflowers.append((petals, x, y))
    
    return sunflowers

# 并行扫描所有向日葵
def scan_sunflowers_mega():
    quick_print("并行扫描向日葵...")
    
    # 计算区域划分
    max_d = max_drones()
    regions = []
    
    if max_d >= 4:
        half = SIZE // 2
        regions = [
            (0, half, 0, half),
            (half, SIZE, 0, half),
            (0, half, half, SIZE),
            (half, SIZE, half, SIZE)
        ]
    elif max_d >= 2:
        half = SIZE // 2
        regions = [
            (0, SIZE, 0, half),
            (0, SIZE, half, SIZE)
        ]
    else:
        regions = [(0, SIZE, 0, SIZE)]
    
    # 启动无人机
    drones = []
    all_sunflowers = []
    
    for i in range(len(regions)):
        x_start, x_end, y_start, y_end = regions[i]
        
        def create_task(xs, xe, ys, ye):
            def task():
                return drone_scan_region(xs, xe, ys, ye)
            return task
        
        task_func = create_task(x_start, x_end, y_start, y_end)
        
        if i < len(regions) - 1:
            drone = spawn_drone(task_func)
            if drone:
                drones.append(drone)
            else:
                flowers = task_func()
                for f in flowers:
                    all_sunflowers.append(f)
        else:
            flowers = task_func()
            for f in flowers:
                all_sunflowers.append(f)
    
    # 等待所有无人机完成
    for drone in drones:
        flowers = wait_for(drone)
        if flowers:
            for f in flowers:
                all_sunflowers.append(f)
    
    return all_sunflowers

# 分组并收获向日葵
def harvest_sunflowers_by_petals(all_sunflowers):
    if len(all_sunflowers) == 0:
        quick_print("没有成熟的向日葵")
        return
    
    quick_print("扫描到 " + str(len(all_sunflowers)) + " 株成熟向日葵")
    
    # 按花瓣数分组
    petal_groups = {}
    for item in all_sunflowers:
        petals, x, y = item
        if petals not in petal_groups:
            petal_groups[petals] = []
        petal_groups[petals].append((x, y))
    
    total_harvested = 0
    total_bonus = 0
    power_before = num_items(Items.Power)
    
    # 从15瓣开始收获
    for petals in range(15, 6, -1):
        if petals not in petal_groups:
            continue
        
        positions = petal_groups[petals]
        count = len(positions)
        
        # 计算剩余数量
        remaining = len(all_sunflowers) - total_harvested
        
        # 检查是否满足5倍奖励条件
        is_max_petals = True
        for p in range(petals + 1, 16):
            if p in petal_groups:
                is_max_petals = False
                break
        
        get_bonus = is_max_petals and remaining >= 10
        
        # 显示信息
        if get_bonus:
            quick_print("收获 " + str(count) + " 株 " + str(petals) + " 瓣（5倍奖励）")
            total_bonus = total_bonus + count
        else:
            quick_print("收获 " + str(count) + " 株 " + str(petals) + " 瓣")
        
        # 优化路径并收获
        current_x = get_pos_x()
        current_y = get_pos_y()
        optimized_positions = optimize_path(positions, current_x, current_y)
        
        for px, py in optimized_positions:
            goto_pos(px, py)
            if can_harvest():
                harvest()
                total_harvested = total_harvested + 1
        
        # 如果剩余<10，停止5倍奖励并全部收获
        remaining = len(all_sunflowers) - total_harvested
        if remaining > 0 and remaining < 10:
            quick_print("剩余 " + str(remaining) + " 株，全部收获")
            for p in range(petals - 1, 6, -1):
                if p not in petal_groups:
                    continue
                pos_list = petal_groups[p]
                for px, py in pos_list:
                    goto_pos(px, py)
                    if can_harvest():
                        harvest()
                        total_harvested = total_harvested + 1
            break
    
    power_after = num_items(Items.Power)
    power_gained = power_after - power_before
    
    quick_print("本轮总计：收获 " + str(total_harvested) + " 株，5倍 " + str(total_bonus) + " 次，能量 +" + str(power_gained))

# 滚动收获循环
def rolling_harvest_cycle():
    # 扫描向日葵
    all_sunflowers = scan_sunflowers_mega()
    
    # 收获向日葵
    harvest_sunflowers_by_petals(all_sunflowers)

# 主程序
clear()
quick_print("=== 多无人机向日葵能量农场 ===")
quick_print("农场大小：" + str(SIZE) + "x" + str(SIZE))
quick_print("最大无人机：" + str(max_drones()))
quick_print("策略：并行种植和扫描，快速收获")
quick_print("")

cycle_count = 0

while True:
    # 初始化：并行种植
    goto_pos(0, 0)
    initialize_farm_mega()
    quick_print("")
    quick_print("开始滚动收获循环...")
    quick_print("========================================")
    
    # 滚动收获循环
    cycle_count = cycle_count + 1
    quick_print("")
    quick_print("--- 第 " + str(cycle_count) + " 轮 ---")
    quick_print("能量：" + str(num_items(Items.Power)))
    
    rolling_harvest_cycle()
    
    quick_print("========================================")
