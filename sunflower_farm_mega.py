# The Farmer Was Replaced - 多无人机向日葵能量农场（共享内存版）
# 策略：使用共享内存协调多无人机，实时跟踪成熟向日葵，最大化5倍奖励

from farm_utils import goto_pos

SIZE = get_world_size()

# ====================
# 共享内存工具函数
# ====================

def create_shared_sunflower_tracker():
    # 源无人机：返回共享的向日葵跟踪器
    # 结构：{位置键: (花瓣数, x, y), ...}
    return {}

def create_shared_stats():
    # 源无人机：返回共享统计数据
    return {
        "total_sunflowers": 0,    # 总向日葵数
        "mature_count": 0,         # 成熟数量
        "max_petals": 0,           # 最大花瓣数
        "harvested": 0,            # 已收获数量
        "bonus_count": 0,          # 5倍奖励次数
        "power_gained": 0          # 获得能量
    }

def add_sunflower_to_tracker(tracker, x, y, petals):
    # 添加或更新向日葵到跟踪器
    key = str(x) + "," + str(y)
    tracker[key] = (petals, x, y)

def remove_sunflower_from_tracker(tracker, x, y):
    # 从跟踪器中移除向日葵
    key = str(x) + "," + str(y)
    if key in tracker:
        tracker.pop(key)

def get_tracker_size(tracker):
    # 获取跟踪器中的向日葵数量
    count = 0
    for key in tracker:
        count = count + 1
    return count

def get_max_petals_from_tracker(tracker):
    # 获取跟踪器中的最大花瓣数
    max_p = 0
    for key in tracker:
        petals, x, y = tracker[key]
        if petals > max_p:
            max_p = petals
    return max_p

def get_sunflowers_by_petals(tracker, target_petals):
    # 获取指定花瓣数的所有向日葵位置
    positions = []
    for key in tracker:
        petals, x, y = tracker[key]
        if petals == target_petals:
            positions.append((x, y))
    return positions

# ====================
# 批次分配函数
# ====================

def split_batches_by_strips(num_batches):
    # 按照条带分配批次（每个无人机负责连续的几行）
    if num_batches <= 0:
        return []
    
    batches = []
    rows_per_batch = SIZE // num_batches
    remainder = SIZE % num_batches
    
    start_y = 0
    for i in range(num_batches):
        # 前 remainder 个批次多分配一行
        if i < remainder:
            end_y = start_y + rows_per_batch + 1
        else:
            end_y = start_y + rows_per_batch
        
        # 生成这个批次的所有位置（蛇形遍历）
        batch_positions = []
        for y in range(start_y, end_y):
            if y % 2 == 0:
                # 偶数行：从左到右
                for x in range(SIZE):
                    batch_positions.append((x, y))
            else:
                # 奇数行：从右到左
                for x in range(SIZE - 1, -1, -1):
                    batch_positions.append((x, y))
        
        if len(batch_positions) > 0:
            batches.append(batch_positions)
        
        start_y = end_y
    
    return batches

# ====================
# 无人机工作函数（使用共享内存）
# ====================

def drone_plant_batch(batch):
    # 无人机：种植一批位置
    planted_count = 0
    
    for pos in batch:
        x, y = pos
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

def drone_scan_and_track_batch(batch, tracker_source):
    # 无人机：扫描一批位置并更新共享跟踪器
    # 返回：扫描到的成熟向日葵数量
    tracker = wait_for(tracker_source)
    
    scanned_count = 0
    
    for pos in batch:
        x, y = pos
        goto_pos(x, y)
        
        entity = get_entity_type()
        
        if entity == Entities.Sunflower:
            if can_harvest():
                # 成熟的向日葵，测量花瓣数并添加到跟踪器
                petals = measure()
                add_sunflower_to_tracker(tracker, x, y, petals)
                scanned_count = scanned_count + 1
            # 未成熟的向日葵不做处理
    
    return scanned_count

def drone_harvest_positions(positions, tracker_source, stats_source):
    # 无人机：收获指定位置的向日葵
    # 返回：收获数量
    tracker = wait_for(tracker_source)
    stats = wait_for(stats_source)
    
    harvested = 0
    power_before = num_items(Items.Power)
    
    for pos in positions:
        x, y = pos
        goto_pos(x, y)
        
        if get_entity_type() == Entities.Sunflower and can_harvest():
            harvest()
            remove_sunflower_from_tracker(tracker, x, y)
            harvested = harvested + 1
    
    power_after = num_items(Items.Power)
    power_gained = power_after - power_before
    
    # 更新统计
    stats["harvested"] = stats["harvested"] + harvested
    stats["power_gained"] = stats["power_gained"] + power_gained
    
    return harvested

# ====================
# 阶段函数（使用共享内存机制）
# ====================

def stage_plant():
    # 阶段1：并行种植整个地图
    quick_print("=== 阶段1：种植 ===")
    
    # 并行种植（使用条带分配）
    available = max_drones() + 1
    batches = split_batches_by_strips(available)
    quick_print("分批: " + str(len(batches)) + " 条带")
    
    drones = []
    results = []
    
    for i in range(len(batches)):
        def create_task(b):
            def task():
                return drone_plant_batch(b)
            return task
        
        task = create_task(batches[i])
        
        if i < len(batches) - 1:
            drone = spawn_drone(task)
            if drone:
                drones.append(drone)
            else:
                results.append(task())
        else:
            results.append(task())
    
    for drone in drones:
        results.append(wait_for(drone))
    
    # 统计结果
    total = 0
    for result in results:
        total = total + result
    
    quick_print("已种植: " + str(total) + " 株")
    return True

def stage_scan_and_track(tracker_source):
    # 阶段2：并行扫描并更新跟踪器
    quick_print("=== 阶段2：扫描成熟向日葵 ===")
    
    # 清空跟踪器
    tracker = wait_for(tracker_source)
    for key in tracker:
        tracker.pop(key)
    
    # 并行扫描（使用条带分配）
    available = max_drones() + 1
    batches = split_batches_by_strips(available)
    
    drones = []
    results = []
    
    for i in range(len(batches)):
        def create_task(b, src):
            def task():
                return drone_scan_and_track_batch(b, src)
            return task
        
        task = create_task(batches[i], tracker_source)
        
        if i < len(batches) - 1:
            drone = spawn_drone(task)
            if drone:
                drones.append(drone)
            else:
                results.append(task())
        else:
            results.append(task())
    
    for drone in drones:
        results.append(wait_for(drone))
    
    # 统计结果
    total_scanned = 0
    for result in results:
        total_scanned = total_scanned + result
    
    quick_print("扫描到: " + str(total_scanned) + " 株成熟向日葵")
    return total_scanned

def stage_harvest_by_petals(tracker_source, stats_source):
    # 阶段3：按花瓣数收获（优先最大花瓣，最大化5倍奖励）
    quick_print("=== 阶段3：按花瓣收获 ===")
    
    tracker = wait_for(tracker_source)
    stats = wait_for(stats_source)
    
    # 重置统计
    stats["harvested"] = 0
    stats["bonus_count"] = 0
    stats["power_gained"] = 0
    
    total_count = get_tracker_size(tracker)
    if total_count == 0:
        quick_print("没有成熟的向日葵")
        return
    
    # 从15瓣开始收获
    for petals in range(15, 6, -1):
        positions = get_sunflowers_by_petals(tracker, petals)
        
        if len(positions) == 0:
            continue
        
        # 计算剩余数量
        remaining = get_tracker_size(tracker)
        
        # 检查是否满足5倍奖励条件
        max_petals = get_max_petals_from_tracker(tracker)
        get_bonus = petals == max_petals and remaining >= 10
        
        # 显示信息
        if get_bonus:
            quick_print("收获 " + str(len(positions)) + " 株 " + str(petals) + " 瓣（5倍奖励）")
            stats["bonus_count"] = stats["bonus_count"] + len(positions)
        else:
            quick_print("收获 " + str(len(positions)) + " 株 " + str(petals) + " 瓣")
        
        # 并行收获
        available = max_drones() + 1
        
        # 分批：确保每个批次大小合理
        batch_size = len(positions) // available
        if batch_size == 0:
            batch_size = 1
        
        batches = []
        for i in range(0, len(positions), batch_size):
            batches.append(positions[i:i + batch_size])
        
        if len(batches) > available:
            # 合并多余的批次
            extra = batches[available:]
            for batch in extra:
                for pos in batch:
                    batches[available - 1].append(pos)
            batches = batches[:available]
        
        drones = []
        results = []
        
        for i in range(len(batches)):
            def create_task(b, tsrc, ssrc):
                def task():
                    return drone_harvest_positions(b, tsrc, ssrc)
                return task
            
            task = create_task(batches[i], tracker_source, stats_source)
            
            if i < len(batches) - 1:
                drone = spawn_drone(task)
                if drone:
                    drones.append(drone)
                else:
                    results.append(task())
            else:
                results.append(task())
        
        for drone in drones:
            results.append(wait_for(drone))
        
        # 如果剩余<10，停止（避免浪费5倍奖励机会）
        remaining = get_tracker_size(tracker)
        if remaining > 0 and remaining < 10:
            quick_print("剩余 " + str(remaining) + " 株（<10），停止收获")
            break
    
    # 显示统计
    quick_print("本轮总计：收获 " + str(stats["harvested"]) + " 株，5倍 " + str(stats["bonus_count"]) + " 次，能量 +" + str(stats["power_gained"]))

# ====================
# 主循环
# ====================

def farming_cycle(tracker_source, stats_source):
    # 主农场循环
    # 使用共享内存机制协调多个无人机
    # 策略：种植→持续扫描和收获循环
    
    quick_print("=== 新一轮 ===")
    quick_print("能量: " + str(num_items(Items.Power)))
    
    start = get_time()
    
    # 阶段1：种植
    stage_plant()
    
    # 持续循环：扫描和收获
    round_num = 0
    total_harvested_this_cycle = 0
    
    while True:
        round_num = round_num + 1
        quick_print("")
        quick_print("--- 循环 " + str(round_num) + " ---")
        
        # 扫描成熟的向日葵
        scanned = stage_scan_and_track(tracker_source)
        
        if scanned == 0:
            # 没有成熟的向日葵
            if round_num == 1:
                # 第一次扫描就没有，说明刚种植完，等待一会儿
                quick_print("等待向日葵成熟...")
                do_a_flip()
                continue
            else:
                # 之前有成熟的，现在没有了，结束这一轮
                quick_print("所有向日葵已收获，结束本轮")
                break
        
        # 收获向日葵
        stage_harvest_by_petals(tracker_source, stats_source)
        
        # 获取统计
        stats = wait_for(stats_source)
        total_harvested_this_cycle = total_harvested_this_cycle + stats["harvested"]
        
        # 检查是否还有剩余的向日葵未收获（<10株时会停止）
        remaining = get_tracker_size(wait_for(tracker_source))
        if remaining > 0:
            quick_print("剩余 " + str(remaining) + " 株未收获（保留等待更多成熟）")
        
        # 安全检查：避免无限循环
        if round_num > 50:
            quick_print("警告：超过50轮循环，结束本轮")
            break
    
    # 最终统计
    elapsed = get_time() - start
    quick_print("")
    quick_print("=== 本轮完成 ===")
    quick_print("用时: " + str(elapsed) + "s")
    quick_print("总收获: " + str(total_harvested_this_cycle) + " 株")
    quick_print("能量: " + str(num_items(Items.Power)))
    
    return True

# ====================
# 主程序
# ====================

clear()
quick_print("=== 多无人机向日葵能量农场（共享内存版）===")
quick_print("地图: " + str(SIZE) + "x" + str(SIZE))
quick_print("无人机: " + str(max_drones()))
quick_print("策略: 共享内存跟踪，实时扫描，最大化5倍奖励")
quick_print("")

# 创建共享内存源
tracker_source = spawn_drone(create_shared_sunflower_tracker)
stats_source = spawn_drone(create_shared_stats)

cycle = 0
while True:
    cycle = cycle + 1
    quick_print("")
    quick_print("========================================")
    quick_print(">>> 轮次 " + str(cycle) + " <<<")
    quick_print("========================================")
    
    farming_cycle(tracker_source, stats_source)
    
    quick_print("")
