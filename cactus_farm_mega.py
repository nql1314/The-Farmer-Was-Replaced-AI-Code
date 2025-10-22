# 多无人机仙人掌农场 - 并行排序优化版
#
# 策略：
# 1. 并行种植仙人掌
# 2. 行列分离排序（先所有行，再所有列）
# 3. 并行排序多行/列以提高效率
# 4. 单点触发连锁收割

from farm_utils import goto_pos, check_and_swap_direction, print_cactus_grid

world_size = get_world_size()

# 无人机任务：种植一个区域的仙人掌
def drone_plant_region(x_start, x_end, y_start, y_end):
    planted = 0
    
    for y in range(y_start, y_end):
        for x in range(x_start, x_end):
            goto_pos(x, y)
            
            if get_ground_type() != Grounds.Soil:
                till()
            
            entity = get_entity_type()
            if entity != Entities.Cactus:
                if entity != None:
                    harvest()
                plant(Entities.Cactus)
                planted = planted + 1
    
    return planted

# 并行种植仙人掌
def plant_cacti_mega():
    quick_print("并行种植仙人掌...")
    
    max_d = max_drones()
    total_planted = 0
    
    # 按行划分任务，每个无人机负责若干行
    # 这样可以充分利用所有可用的无人机
    rows_per_drone = max(1, world_size // max_d)
    
    # 如果无人机数量很多，确保每个无人机至少处理1行
    if rows_per_drone == 0:
        rows_per_drone = 1
    
    drone_groups = []
    for i in range(0, world_size, rows_per_drone):
        end_row = min(i + rows_per_drone, world_size)
        drone_groups.append((0, world_size, i, end_row))
    
    quick_print("分配 " + str(len(drone_groups)) + " 个种植任务（最大无人机: " + str(max_d) + "）")
    
    # 启动无人机
    drones = []
    
    for group_idx in range(len(drone_groups)):
        x_start, x_end, y_start, y_end = drone_groups[group_idx]
        
        def create_task(xs, xe, ys, ye):
            def task():
                quick_print("  无人机种植行 " + str(ys) + "-" + str(ye-1))
                return drone_plant_region(xs, xe, ys, ye)
            return task
        
        task_func = create_task(x_start, x_end, y_start, y_end)
        
        # 最后一个任务由主无人机执行
        if group_idx < len(drone_groups) - 1:
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
    
    quick_print("种植完成:", total_planted, "个仙人掌")

# 无人机任务：排序一行
def drone_sort_row(y):
    row_swaps = 0
    
    # 对当前行进行冒泡排序
    while True:
        swapped = False
        
        # 从左向右遍历这一行
        for x in range(world_size - 1):
            goto_pos(x, y)
            
            if get_entity_type() != Entities.Cactus:
                continue
            
            curr_val = measure()
            
            # 检查 East 方向
            if check_and_swap_direction(East, curr_val, True):
                swapped = True
                row_swaps = row_swaps + 1
        
        if not swapped:
            break
    
    return row_swaps

# 无人机任务：排序一列
def drone_sort_column(x):
    col_swaps = 0
    
    # 对当前列进行冒泡排序
    while True:
        swapped = False
        
        # 从下向上遍历这一列
        for y in range(world_size - 1):
            goto_pos(x, y)
            
            if get_entity_type() != Entities.Cactus:
                continue
            
            curr_val = measure()
            
            # 检查 North 方向
            if check_and_swap_direction(North, curr_val, True):
                swapped = True
                col_swaps = col_swaps + 1
        
        if not swapped:
            break
    
    return col_swaps

# 并行排序所有行
def sort_rows_mega():
    quick_print("=== 并行行排序（West -> East 递增） ===")
    
    max_d = max_drones()
    total_swaps = 0
    
    # 将行分配给无人机
    # 每个无人机负责若干行
    rows_per_drone = (world_size + max_d - 1) // max_d  # 向上取整
    
    drone_groups = []
    for i in range(0, world_size, rows_per_drone):
        end_row = min(i + rows_per_drone, world_size)
        drone_groups.append(range(i, end_row))
    
    quick_print("分配 " + str(len(drone_groups)) + " 个无人机组")
    
    # 为每个组启动任务
    drones = []
    
    for group_idx in range(len(drone_groups)):
        rows = drone_groups[group_idx]
        
        def create_task(row_range):
            def task():
                swaps = 0
                for y in row_range:
                    quick_print("  排序行" + str(y))
                    s = drone_sort_row(y)
                    swaps = swaps + s
                return swaps
            return task
        
        task_func = create_task(rows)
        
        if group_idx < len(drone_groups) - 1:
            drone = spawn_drone(task_func)
            if drone:
                drones.append(drone)
            else:
                swaps = task_func()
                total_swaps = total_swaps + swaps
        else:
            swaps = task_func()
            total_swaps = total_swaps + swaps
    
    # 等待所有无人机完成
    for drone in drones:
        swaps = wait_for(drone)
        if swaps:
            total_swaps = total_swaps + swaps
    
    quick_print("=== 行排序完成 ===")
    quick_print("总交换次数:", total_swaps)
    
    return total_swaps

# 并行排序所有列
def sort_columns_mega():
    quick_print("")
    quick_print("=== 并行列排序（South -> North 递增） ===")
    
    max_d = max_drones()
    total_swaps = 0
    
    # 将列分配给无人机
    cols_per_drone = (world_size + max_d - 1) // max_d
    
    drone_groups = []
    for i in range(0, world_size, cols_per_drone):
        end_col = min(i + cols_per_drone, world_size)
        drone_groups.append(range(i, end_col))
    
    quick_print("分配 " + str(len(drone_groups)) + " 个无人机组")
    
    # 为每个组启动任务
    drones = []
    
    for group_idx in range(len(drone_groups)):
        cols = drone_groups[group_idx]
        
        def create_task(col_range):
            def task():
                swaps = 0
                for x in col_range:
                    quick_print("  排序列" + str(x))
                    s = drone_sort_column(x)
                    swaps = swaps + s
                return swaps
            return task
        
        task_func = create_task(cols)
        
        if group_idx < len(drone_groups) - 1:
            drone = spawn_drone(task_func)
            if drone:
                drones.append(drone)
            else:
                swaps = task_func()
                total_swaps = total_swaps + swaps
        else:
            swaps = task_func()
            total_swaps = total_swaps + swaps
    
    # 等待所有无人机完成
    for drone in drones:
        swaps = wait_for(drone)
        if swaps:
            total_swaps = total_swaps + swaps
    
    quick_print("=== 列排序完成 ===")
    quick_print("总交换次数:", total_swaps)
    
    return total_swaps

# 多无人机冒泡排序
def bubble_sort_mega():
    quick_print("=== 多无人机二维冒泡排序 ===")
    
    tick_start = get_tick_count()
    
    quick_print("农场大小:", world_size, "x", world_size)
    quick_print("最大无人机:", max_drones())
    
    # 打印排序前的网格
    quick_print("")
    quick_print("排序前：")
    print_cactus_grid(world_size)
    
    # 第一步：并行行排序
    quick_print("")
    tick_rows = get_tick_count()
    row_swaps = sort_rows_mega()
    tick_rows = get_tick_count() - tick_rows
    
    # 打印行排序后的网格
    quick_print("")
    quick_print("行排序后：")
    print_cactus_grid(world_size)
    
    # 第二步：并行列排序
    quick_print("")
    tick_cols = get_tick_count()
    col_swaps = sort_columns_mega()
    tick_cols = get_tick_count() - tick_cols
    
    total_ticks = get_tick_count() - tick_start
    total_swaps = row_swaps + col_swaps
    
    # 打印最终排序后的网格
    quick_print("")
    quick_print("最终排序后：")
    print_cactus_grid(world_size)
    
    quick_print("")
    quick_print("=== 二维冒泡排序完成 ===")
    quick_print("行排序交换:", row_swaps, "次，耗时", tick_rows, "ticks")
    quick_print("列排序交换:", col_swaps, "次，耗时", tick_cols, "ticks")
    quick_print("总交换次数:", total_swaps)
    quick_print("总计:", total_ticks, "ticks")

# 收割仙人掌
def harvest_all():
    goto_pos(0, 0)
    
    count_before = num_items(Items.Cactus)
    
    # 从左下角开始收割
    if can_harvest():
        harvest()
    
    count_after = num_items(Items.Cactus)
    gained = count_after - count_before
    
    expected_max = world_size * world_size
    expected_chain = expected_max * expected_max
    
    quick_print("首次收割获得:", gained, "个仙人掌")
    
    if gained >= expected_chain:
        quick_print("完美！触发完整连锁反应")
    else:
        quick_print("连锁效果:", gained, "/", expected_chain, "（", gained * 100 // expected_chain, "%）")
        
        # 收割剩余的
        quick_print("收割剩余仙人掌...")
        for y in range(world_size):
            for x in range(world_size):
                goto_pos(x, y)
                if can_harvest():
                    harvest()
    
    final_count = num_items(Items.Cactus)
    total_gained = final_count - count_before
    quick_print("总收获:", total_gained, "个仙人掌")

# 运行完整周期
def run_cycle():
    tick_start = get_tick_count()
    cactus_start = num_items(Items.Cactus)
    
    quick_print("")
    quick_print("==========================")
    quick_print("多无人机仙人掌周期开始")
    quick_print("==========================")
    
    # 种植
    quick_print("")
    quick_print(">>> 阶段1: 并行种植")
    tick_phase = get_tick_count()
    plant_cacti_mega()
    tick_plant = get_tick_count() - tick_phase
    quick_print("种植耗时:", tick_plant, "ticks")
    
    # 排序
    quick_print("")
    quick_print(">>> 阶段2: 多无人机排序")
    tick_phase = get_tick_count()
    bubble_sort_mega()
    tick_sort = get_tick_count() - tick_phase
    quick_print("排序耗时:", tick_sort, "ticks")
    
    # 收割
    quick_print("")
    quick_print(">>> 阶段3: 收割")
    quick_print("从左下角触发连锁反应...")
    tick_phase = get_tick_count()
    harvest_all()
    tick_harvest = get_tick_count() - tick_phase
    quick_print("收割耗时:", tick_harvest, "ticks")
    
    # 统计
    total_ticks = get_tick_count() - tick_start
    cactus_gained = num_items(Items.Cactus) - cactus_start
    
    quick_print("")
    quick_print("==========================")
    quick_print("周期完成")
    quick_print("==========================")
    quick_print("阶段1 种植:", tick_plant, "ticks")
    quick_print("阶段2 排序:", tick_sort, "ticks")
    quick_print("阶段3 收割:", tick_harvest, "ticks")
    quick_print("--------------------------")
    quick_print("总计:", total_ticks, "ticks")
    quick_print("获得:", cactus_gained, "个仙人掌")
    quick_print("总数:", num_items(Items.Cactus))
    quick_print("==========================")
    quick_print("")

# 初始化
quick_print("=============================")
quick_print("多无人机仙人掌农场")
quick_print("算法: 并行行列分离排序")
quick_print("策略: 多无人机同时排序不同行/列")
quick_print("优势: 大幅减少排序时间")
quick_print("=============================")
quick_print("")

quick_print("当前农场大小:", world_size, "x", world_size)
quick_print("最大无人机:", max_drones())

quick_print("")
clear()

# 主循环
while True:
    run_cycle()
