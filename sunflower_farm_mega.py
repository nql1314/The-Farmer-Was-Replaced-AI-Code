# The Farmer Was Replaced - 多无人机向日葵能量农场（优化版）
# 策略：单无人机维护共享内存，按花瓣数分类收获，最大化5倍奖励

from farm_utils import goto_pos

SIZE = get_world_size()

# ====================
# 共享内存：按花瓣数分类的向日葵集合
# ====================

def create_shared_tracker():
    # 源无人机：维护共享内存
    # 结构：{
    #   "15": [(x, y), ...],   # 15瓣
    #   "14": [(x, y), ...],   # 14瓣
    #   ...
    #   "10": [(x, y), ...],   # 10瓣
    #   "low": [(x, y), ...]   # 10以下合并
    # }
    return {
        "15": [],
        "14": [],
        "13": [],
        "12": [],
        "11": [],
        "10": [],
        "low": []
    }

def add_to_tracker(tracker, petals, x, y):
    # 添加向日葵到对应花瓣数的集合
    if petals >= 10:
        key = str(petals)
    else:
        key = "low"
    tracker[key].append((x, y))

def get_tracker_count(tracker, key):
    # 获取指定集合的数量（减去5个占位元素）
    return len(tracker[key]) - 5

def get_total_count(tracker):
    # 获取所有向日葵总数（减去占位元素）
    total = 0
    for key in tracker:
        total = total + len(tracker[key]) - 5
    return total

def clear_tracker(tracker):
    # 清空所有集合（保留5个占位元素）
    # 技巧：使用5个占位元素避免频繁的空判断
    for key in tracker:
        tracker[key] = [(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)]

def position_to_key(positions):
    # 从队列中取位置（如果只剩占位元素则返回None）
    # 优化：保持5个占位元素，避免竞态条件下的重复检查
    if len(positions) <= 5:
        return None
    return positions.pop()
# ====================
# 批次分配：蛇形条带分配
# ====================

def split_snake_batches(num_batches):
    # 将整个地图按蛇形条带分配给多个无人机
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
# 无人机工作函数
# ====================

def drone_plant_batch(batch):
    # 无人机：种植一批位置，并浇水到 >0.75
    for pos in batch:
        x, y = pos
        goto_pos(x, y)
        
        # 收割旧作物
        if can_harvest():
            harvest()
        
        # 翻土（向日葵需要土壤）
        if get_ground_type() != Grounds.Soil:
            till()
        
        # 浇水到 >0.75（5倍生长速度）
        while get_water() < 0.75:
            if num_items(Items.Water) > 0:
                use_item(Items.Water)
            else:
                break
        
        # 种植向日葵
        plant(Entities.Sunflower)

def drone_scan_and_harvest_15(batch, tracker_source):
    # 无人机：扫描批次，同时收获15瓣，其他的存入tracker
    # 返回：(扫描到的成熟数, 收获的15瓣数)
    tracker = wait_for(tracker_source)
    
    scanned = 0
    harvested_15 = 0
    
    for pos in batch:
        x, y = pos
        goto_pos(x, y)
        
        if get_entity_type() == Entities.Sunflower and can_harvest():
            petals = measure()
            scanned = scanned + 1
            
            if petals == 15:
                # 立即收获15瓣
                harvest()
                harvested_15 = harvested_15 + 1
            else:
                # 其他花瓣数存入tracker
                add_to_tracker(tracker, petals, x, y)
    
    return (scanned, harvested_15)

def drone_harvest_from_queue(tracker_source, key):
    # 无人机：从共享队列中持续取位置并收获
    # 动态任务队列机制：
    # 1. 无人机持续从共享队列中pop位置
    # 2. 移动到位置并收获
    # 3. 如果已被其他无人机收获，自动跳过
    # 4. 直到队列为空
    # 优势：负载自动平衡、容错性强、无需预分配批次
    # 返回：实际收获数量
    tracker = wait_for(tracker_source)
    harvested = 0
    
    while True:
        # 从队列中取出一个位置
        positions = tracker[key]
        
        pos = position_to_key(positions)
        if pos == None:
            break
        
        # 移动到位置
        goto_pos(pos[0], pos[1])
        
        # 检查是否还是向日葵（可能已被其他无人机收获）
        if get_entity_type() == Entities.Sunflower and can_harvest():
            harvest()
            harvested = harvested + 1
        # 如果已被收获，跳过即可（容错机制）
    
    return harvested

# ====================
# 阶段函数
# ====================

def stage_plant():
    # 阶段1：并行种植整个地图
    available = max_drones() + 1
    batches = split_snake_batches(available)
    
    drones = []
    
    for i in range(len(batches)):
        def create_task(b):
            def task():
                drone_plant_batch(b)
            return task
        
        task = create_task(batches[i])
        
        if i < len(batches) - 1:
            drone = spawn_drone(task)
            if drone:
                drones.append(drone)
            else:
                task()
        else:
            task()
    
    for drone in drones:
        wait_for(drone)
    
    # 种植完成后等待所有向日葵成熟
    # 向日葵基础生长时间：5.6-8.4秒
    # 含水量0.75时：生长速度 = 1 + 4*0.75 = 4倍
    # 最慢成熟时间：8.4 / 4 = 2.1秒
    # 为保险起见，等待3秒
    quick_print("等待向日葵成熟...")
    start_wait = get_time()
    while get_time() - start_wait < 3:
        do_a_flip()

def stage_scan_and_harvest_15(tracker_source):
    # 阶段2：并行扫描，同时收获15瓣
    # 返回：(总扫描数, 收获的15瓣数)
    
    # 清空tracker
    tracker = wait_for(tracker_source)
    clear_tracker(tracker)
    
    available = max_drones() + 1
    batches = split_snake_batches(available)
    
    drones = []
    results = []
    
    for i in range(len(batches)):
        def create_task(b, src):
            def task():
                return drone_scan_and_harvest_15(b, src)
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
    
    # 统计
    total_scanned = 0
    total_harvested_15 = 0
    for result in results:
        scanned, harvested_15 = result
        total_scanned = total_scanned + scanned
        total_harvested_15 = total_harvested_15 + harvested_15
    
    return (total_scanned, total_harvested_15)

def stage_harvest_by_petals(tracker_source, petals_list):
    # 阶段3：按花瓣数依次收获（使用动态队列）
    # petals_list: 要收获的花瓣数列表，如 [14, 13, 12, ...]
    # 返回：总收获数
    
    tracker = wait_for(tracker_source)
    total_harvested = 0
    
    for petals in petals_list:
        # 确定key
        if petals >= 10:
            key = str(petals)
        else:
            key = "low"
        power_before = num_items(Items.Power)
        positions = tracker[key]
        count = len(positions)
        
        if count == 0:
            continue
        
        # 启动所有可用无人机，让它们从共享队列中取任务
        available = max_drones() + 1
        
        drones = []
        results = []
        
        for i in range(available):
            def create_task(src, k):
                def task():
                    return drone_harvest_from_queue(src, k)
                return task
            
            task = create_task(tracker_source, key)
            
            if i < available - 1:
                drone = spawn_drone(task)
                if drone:
                    drones.append(drone)
                else:
                    # 如果无法生成无人机，主无人机自己执行
                    results.append(task())
            else:
                # 最后一个任务主无人机自己执行
                results.append(task())
                
        
        # 等待所有无人机完成
        for drone in drones:
            results.append(wait_for(drone))
        
        # 统计本轮收获
        harvested = 0
        for result in results:
            harvested = harvested + result
        
        total_harvested = total_harvested + harvested
        power_after = num_items(Items.Power)
        power_gained = power_after - power_before
        quick_print("本轮收获 " + str(petals) + " 瓣 " + str(harvested) + " 株，能量 +" + str(power_gained))
    return total_harvested

# ====================
# 主循环
# ====================

def farming_cycle(tracker_source):
    # 主循环：种植→扫描收获15瓣→依次收获14-10瓣→收获10以下
    
    start_time = get_time()
    power_before = num_items(Items.Power)
    
    # 阶段1：种植
    stage_plant()
    
    # 持续扫描和收获循环
    round_num = 0
    total_harvested = 0
    
    while True:
        round_num = round_num + 1
        
        # 阶段2：扫描并收获15瓣
        scanned, harvested_15 = stage_scan_and_harvest_15(tracker_source)
        
        if scanned == 0:
            if round_num == 1:
                # 第一次扫描没有成熟的，等待
                do_a_flip()
                continue
            else:
                # 之后扫描没有，说明收获完毕
                break
        
        total_harvested = total_harvested + harvested_15
        
        # 阶段3：依次收获14-10瓣和10以下
        # 收获顺序：14, 13, 12, 11, 10, low
        petals_order = [14, 13, 12, 11, 10, 9]  # 9代表low
        harvested_rest = stage_harvest_by_petals(tracker_source, petals_order)
        total_harvested = total_harvested + harvested_rest
        
        # 安全检查
        if round_num > 50:
            break
    
    # 统计
    elapsed = get_time() - start_time
    power_after = num_items(Items.Power)
    power_gained = power_after - power_before
    
    # 计算效率
    if elapsed > 0:
        harvest_rate = total_harvested / elapsed
    else:
        harvest_rate = 0
    
    quick_print("本轮完成: 收获 " + str(total_harvested) + " 株, 能量 +" + str(power_gained) + ", 用时 " + str(elapsed) + "s, 效率 " + str(harvest_rate) + " 株/s")

# ====================
# 主程序
# ====================

clear()
quick_print("=== 多无人机向日葵农场（优化版）===")
quick_print("地图: " + str(SIZE) + "x" + str(SIZE))
quick_print("无人机: " + str(max_drones()))
quick_print("策略: 单无人机维护共享内存，按花瓣分类收获")
quick_print("")

# 创建共享内存源（只用一台无人机）
tracker_source = spawn_drone(create_shared_tracker)

cycle = 0
while True:
    cycle = cycle + 1
    quick_print("")
    quick_print("===== 轮次 " + str(cycle) + " =====")
    
    farming_cycle(tracker_source)
    
    quick_print("")
    