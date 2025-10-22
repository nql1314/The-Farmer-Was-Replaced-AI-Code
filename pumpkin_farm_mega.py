# The Farmer Was Replaced - 多无人机南瓜专业种植脚本
# 策略：并行种植和管理多个6x6南瓜区域，最大化产量

from farm_utils import goto_pos, generate_snake_path, refill_carrots_generic

# 配置参数
CONFIG = {
    'pumpkin_threshold': 200000000,
    'carrot_reserve': 50,
    'carrot_target': 2000,  # 多无人机需要更多胡萝卜
    'field_size': 6
}

world_size = get_world_size()
FULL_FARM_PATH = generate_snake_path(world_size)

# 补种胡萝卜到目标数量
def refill_carrots():
    refill_carrots_generic(CONFIG['carrot_target'], world_size, FULL_FARM_PATH)

# 计算南瓜田区域（尽可能多的6x6区域）
def calculate_pumpkin_regions():
    regions = []
    field_size = CONFIG['field_size']
    
    # 计算可以放置多少个6x6区域
    regions_per_row = world_size // field_size
    
    for ry in range(regions_per_row):
        for rx in range(regions_per_row):
            x_start = rx * field_size
            y_start = ry * field_size
            regions.append((x_start, y_start))
    
    return regions

# 无人机任务：种植一个6x6南瓜田
def drone_plant_pumpkin_field(x_start, y_start):
    field_size = CONFIG['field_size']
    planted = 0
    
    for y in range(y_start, y_start + field_size):
        for x in range(x_start, x_start + field_size):
            goto_pos(x, y)
            
            # 检查胡萝卜
            if num_items(Items.Carrot) < 1:
                return (False, planted)  # 胡萝卜不足
            
            # 收割现有植物
            if can_harvest():
                harvest()
            
            # 确保土壤
            if get_ground_type() != Grounds.Soil:
                till()
            
            # 种植南瓜
            plant(Entities.Pumpkin)
            planted = planted + 1
    
    return (True, planted)

# 无人机任务：检查并补种一个区域的枯萎南瓜
def drone_replant_dead_field(x_start, y_start):
    field_size = CONFIG['field_size']
    replanted_positions = []
    dead_count = 0
    
    for y in range(y_start, y_start + field_size):
        for x in range(x_start, x_start + field_size):
            goto_pos(x, y)
            entity = get_entity_type()
            
            if entity == Entities.Dead_Pumpkin:
                dead_count = dead_count + 1
                
                # 检查胡萝卜
                if num_items(Items.Carrot) < 1:
                    return (False, replanted_positions, dead_count)
                
                # 补种
                plant(Entities.Pumpkin)
                replanted_positions.append((x, y))
    
    return (True, replanted_positions, dead_count)

# 无人机任务：等待一个区域的南瓜全部成熟
def drone_wait_field_mature(x_start, y_start):
    field_size = CONFIG['field_size']
    
    while True:
        all_mature = True
        
        for y in range(y_start, y_start + field_size):
            for x in range(x_start, x_start + field_size):
                goto_pos(x, y)
                entity = get_entity_type()
                
                if entity == Entities.Pumpkin:
                    if not can_harvest():
                        all_mature = False
                        break
                elif entity == Entities.Dead_Pumpkin:
                    # 发现枯萎，重新补种
                    if num_items(Items.Carrot) >= 1:
                        plant(Entities.Pumpkin)
                    all_mature = False
                    break
            
            if not all_mature:
                break
        
        if all_mature:
            return True
        
        # 等待
        do_a_flip()

# 无人机任务：收获一个6x6区域
def drone_harvest_field(x_start, y_start):
    goto_pos(x_start, y_start)
    
    if can_harvest():
        before = num_items(Items.Pumpkin)
        harvest()
        after = num_items(Items.Pumpkin)
        gained = after - before
        return gained
    return 0

# 并行种植所有南瓜田
def parallel_plant_all_fields(regions):
    quick_print("第1遍：并行种植所有南瓜田")
    
    drones = []
    total_planted = 0
    
    for i in range(len(regions)):
        x_start, y_start = regions[i]
        
        def create_task(xs, ys):
            def task():
                return drone_plant_pumpkin_field(xs, ys)
            return task
        
        task_func = create_task(x_start, y_start)
        
        if i < len(regions) - 1:
            drone = spawn_drone(task_func)
            if drone:
                drones.append(drone)
                quick_print("区域(" + str(x_start) + "," + str(y_start) + "): 无人机")
            else:
                success, count = task_func()
                total_planted = total_planted + count
                if not success:
                    return (False, total_planted)
                quick_print("区域(" + str(x_start) + "," + str(y_start) + "): 主机")
        else:
            success, count = task_func()
            total_planted = total_planted + count
            if not success:
                return (False, total_planted)
            quick_print("区域(" + str(x_start) + "," + str(y_start) + "): 主机")
    
    # 等待所有无人机完成
    for drone in drones:
        result = wait_for(drone)
        if result:
            success, count = result
            total_planted = total_planted + count
            if not success:
                return (False, total_planted)
    
    quick_print("已种植：" + str(total_planted) + " 个南瓜")
    return (True, total_planted)

# 并行补种枯萎南瓜
def parallel_replant_dead_fields(regions):
    quick_print("第2遍：并行检查并补种枯萎")
    
    drones = []
    total_dead = 0
    all_replanted = []
    
    for i in range(len(regions)):
        x_start, y_start = regions[i]
        
        def create_task(xs, ys):
            def task():
                return drone_replant_dead_field(xs, ys)
            return task
        
        task_func = create_task(x_start, y_start)
        
        if i < len(regions) - 1:
            drone = spawn_drone(task_func)
            if drone:
                drones.append(drone)
            else:
                success, positions, dead = task_func()
                total_dead = total_dead + dead
                for pos in positions:
                    all_replanted.append(pos)
                if not success:
                    return (False, all_replanted, total_dead)
        else:
            success, positions, dead = task_func()
            total_dead = total_dead + dead
            for pos in positions:
                all_replanted.append(pos)
            if not success:
                return (False, all_replanted, total_dead)
    
    # 等待所有无人机完成
    for drone in drones:
        result = wait_for(drone)
        if result:
            success, positions, dead = result
            total_dead = total_dead + dead
            for pos in positions:
                all_replanted.append(pos)
            if not success:
                return (False, all_replanted, total_dead)
    
    if total_dead > 0:
        quick_print("发现枯萎：" + str(total_dead) + " 个，已补种")
    else:
        quick_print("无枯萎南瓜")
    
    return (True, all_replanted, total_dead)

# 并行等待所有区域成熟
def parallel_wait_all_mature(regions):
    quick_print("并行等待所有区域成熟...")
    
    drones = []
    
    for i in range(len(regions)):
        x_start, y_start = regions[i]
        
        def create_task(xs, ys):
            def task():
                return drone_wait_field_mature(xs, ys)
            return task
        
        task_func = create_task(x_start, y_start)
        
        if i < len(regions) - 1:
            drone = spawn_drone(task_func)
            if drone:
                drones.append(drone)
            else:
                task_func()
        else:
            task_func()
    
    # 等待所有无人机完成
    for drone in drones:
        wait_for(drone)
    
    quick_print("所有区域已成熟")

# 并行收获所有南瓜田
def parallel_harvest_all_fields(regions):
    quick_print("并行收获所有南瓜田")
    
    drones = []
    total_gained = 0
    
    for i in range(len(regions)):
        x_start, y_start = regions[i]
        
        def create_task(xs, ys):
            def task():
                return drone_harvest_field(xs, ys)
            return task
        
        task_func = create_task(x_start, y_start)
        
        if i < len(regions) - 1:
            drone = spawn_drone(task_func)
            if drone:
                drones.append(drone)
            else:
                gained = task_func()
                total_gained = total_gained + gained
        else:
            gained = task_func()
            total_gained = total_gained + gained
    
    # 等待所有无人机完成
    for drone in drones:
        gained = wait_for(drone)
        if gained:
            total_gained = total_gained + gained
    
    quick_print("收获 +" + str(total_gained) + " 总计:" + str(num_items(Items.Pumpkin)))

# 南瓜种植主循环
def pumpkin_farming_cycle():
    pumpkin_count = num_items(Items.Pumpkin)
    
    quick_print("南瓜:" + str(pumpkin_count) + " 胡萝卜:" + str(num_items(Items.Carrot)))
    
    # 检查是否需要种植
    if pumpkin_count >= CONFIG['pumpkin_threshold']:
        quick_print("南瓜充足")
        do_a_flip()
        return
    
    quick_print("=== 开始多无人机种植南瓜 ===")
    start_time = get_time()
    
    # 计算所有南瓜区域
    regions = calculate_pumpkin_regions()
    quick_print("将种植 " + str(len(regions)) + " 个 6x6 南瓜田")
    
    # 第一遍：并行种植所有
    success, planted = parallel_plant_all_fields(regions)
    if not success:
        quick_print("胡萝卜不足，补充中...")
        refill_carrots()
        return
    
    # 等待生长
    quick_print("等待生长...")
    do_a_flip()
    
    # 第二遍：并行补种枯萎
    success, replanted, dead_count = parallel_replant_dead_fields(regions)
    if not success:
        quick_print("胡萝卜不足，补充中...")
        refill_carrots()
        return
    
    # 并行等待所有区域成熟
    parallel_wait_all_mature(regions)
    
    # 并行收获所有南瓜田
    elapsed = get_time() - start_time
    quick_print("全部成熟！用时:" + str(elapsed) + "s")
    parallel_harvest_all_fields(regions)

# 主程序
clear()
quick_print("=== 多无人机南瓜农场 ===")
quick_print("农场大小：" + str(world_size) + "x" + str(world_size))
quick_print("最大无人机：" + str(max_drones()))
quick_print("目标:" + str(CONFIG['pumpkin_threshold']))

while True:
    pumpkin_farming_cycle()
