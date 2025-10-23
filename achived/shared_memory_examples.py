# TFWR 无人机共享内存实用示例
# 利用 wait_for() 机制实现跨无人机数据共享

# ========================================
# 示例1：并行数据收集（列表追加）
# ========================================

def example1_parallel_collection():
    quick_print("=== Example 1: Parallel Data Collection ===")
    
    # 创建共享列表
    def create_list():
        return []
    
    shared_list = spawn_drone(create_list)
    
    # 收集者：收集一列的数据
    def collect_column():
        col_data = []
        start_x = get_pos_x()
        
        for y in range(get_world_size()):
            if can_harvest():
                col_data.append([start_x, get_pos_y(), harvest()])
            move(North)
        
        # 添加到共享列表（安全：只追加）
        data = wait_for(shared_list)
        for item in col_data:
            data.append(item)
        
        return len(col_data)
    
    # 启动多个收集者
    drones = []
    for x in range(min(4, get_world_size())):
        drone = spawn_drone(collect_column)
        if drone:
            drones.append(drone)
        move(East)
    
    # 等待完成
    for drone in drones:
        wait_for(drone)
    
    # 获取所有数据
    all_data = wait_for(shared_list)
    quick_print("Total items collected:", len(all_data))

# ========================================
# 示例2：实时统计汇总（字典更新）
# ========================================

def example2_realtime_stats():
    quick_print("=== Example 2: Realtime Statistics ===")
    
    # 创建共享统计字典
    def create_stats():
        return {
            "grass_count": 0,
            "tree_count": 0,
            "bush_count": 0,
            "empty_count": 0,
            "zones_scanned": 0
        }
    
    stats_drone = spawn_drone(create_stats)
    
    # 扫描器：扫描一个区域
    def scan_zone():
        local_stats = {
            "grass": 0,
            "tree": 0,
            "bush": 0,
            "empty": 0
        }
        
        # 扫描 5x5 区域
        for y in range(5):
            for x in range(5):
                entity = get_entity_type()
                if entity == Entities.Grass:
                    local_stats["grass"] += 1
                elif entity == Entities.Tree:
                    local_stats["tree"] += 1
                elif entity == Entities.Bush:
                    local_stats["bush"] += 1
                else:
                    local_stats["empty"] += 1
                
                if x < 4:
                    move(East)
            
            if y < 4:
                move(North)
                for _ in range(4):
                    move(West)
        
        # 更新共享统计（使用 += 操作）
        stats = wait_for(stats_drone)
        stats["grass_count"] += local_stats["grass"]
        stats["tree_count"] += local_stats["tree"]
        stats["bush_count"] += local_stats["bush"]
        stats["empty_count"] += local_stats["empty"]
        stats["zones_scanned"] += 1
        
        return 25
    
    # 启动多个扫描器
    drones = []
    zones = [[0, 0], [5, 0], [0, 5], [5, 5]]  # 四个角
    
    for zone in zones:
        # goto(zone[0], zone[1])  # 移动到区域起点
        drone = spawn_drone(scan_zone)
        if drone:
            drones.append(drone)
    
    # 等待完成
    for drone in drones:
        wait_for(drone)
    
    # 获取最终统计
    final_stats = wait_for(stats_drone)
    quick_print("Grass:", final_stats["grass_count"])
    quick_print("Trees:", final_stats["tree_count"])
    quick_print("Bushes:", final_stats["bush_count"])
    quick_print("Empty:", final_stats["empty_count"])
    quick_print("Zones scanned:", final_stats["zones_scanned"])

# ========================================
# 示例3：进度追踪（独立键模式）
# ========================================

def example3_progress_tracking():
    quick_print("=== Example 3: Progress Tracking ===")
    
    # 创建进度字典（每个无人机有独立的键）
    def create_progress():
        return {}
    
    progress_drone = spawn_drone(create_progress)
    
    # 工作者：执行任务并报告进度
    def worker_with_progress():
        drone_id = num_drones()
        
        # 初始化进度
        progress = wait_for(progress_drone)
        progress[drone_id] = {"status": "started", "completed": 0, "total": 10}
        
        # 执行 10 个任务
        for i in range(10):
            # 模拟工作
            if can_harvest():
                harvest()
            move(East)
            
            # 更新进度（安全：使用独立键）
            progress = wait_for(progress_drone)
            progress[drone_id]["completed"] = i + 1
            
            do_a_flip()
        
        # 标记完成
        progress = wait_for(progress_drone)
        progress[drone_id]["status"] = "done"
        
        return drone_id
    
    # 启动多个工作者
    drones = []
    for i in range(4):
        drone = spawn_drone(worker_with_progress)
        if drone:
            drones.append(drone)
    
    # 监控进度（可以在工作期间查看）
    do_a_flip()
    do_a_flip()
    
    current_progress = wait_for(progress_drone)
    quick_print("Current progress:", current_progress)
    
    # 等待所有完成
    for drone in drones:
        wait_for(drone)
    
    # 获取最终进度
    final_progress = wait_for(progress_drone)
    quick_print("Final progress:", final_progress)

# ========================================
# 示例4：任务分配（生产者-消费者）
# ========================================

def example4_task_queue():
    quick_print("=== Example 4: Task Queue ===")
    
    # 创建任务队列
    def create_queue():
        tasks = []
        for i in range(20):
            tasks.append(i)
        return {
            "tasks": tasks,
            "results": {},
            "completed": 0
        }
    
    queue_drone = spawn_drone(create_queue)
    
    # 工作者：从队列取任务并处理
    def worker():
        drone_id = num_drones()
        my_results = []
        
        while True:
            # 获取任务
            queue = wait_for(queue_drone)
            
            if len(queue["tasks"]) == 0:
                break  # 没有任务了
            
            # 取出第一个任务
            task = queue["tasks"][0]
            queue["tasks"] = queue["tasks"][1:]  # 移除任务
            
            # 处理任务（这里只是简单示例）
            result = task * 2
            my_results.append(result)
            
            # 等待一下，给其他无人机机会
            do_a_flip()
        
        # 存储结果（使用独立键）
        queue = wait_for(queue_drone)
        queue["results"][drone_id] = my_results
        queue["completed"] += len(my_results)
        
        return len(my_results)
    
    # 启动多个工作者
    worker_count = min(4, max_drones())
    drones = []
    
    for i in range(worker_count):
        drone = spawn_drone(worker)
        if drone:
            drones.append(drone)
    
    # 等待完成
    results = []
    for drone in drones:
        count = wait_for(drone)
        results.append(count)
    
    # 获取最终结果
    final_queue = wait_for(queue_drone)
    quick_print("Tasks completed:", final_queue["completed"])
    quick_print("Results by drone:", final_queue["results"])

# ========================================
# 示例5：协作式农场处理（安全模式）
# ========================================

def example5_collaborative_farming():
    quick_print("=== Example 5: Collaborative Farming ===")
    
    # 创建共享状态
    def create_farm_state():
        return {
            "harvested": 0,
            "planted": 0,
            "tilled": 0,
            "positions": []  # 记录处理过的位置
        }
    
    state_drone = spawn_drone(create_farm_state)
    
    # 农场工作者
    def farm_worker():
        drone_id = num_drones()
        local_harvested = 0
        local_planted = 0
        local_tilled = 0
        my_positions = []
        
        # 处理一行
        for x in range(get_world_size()):
            pos = [get_pos_x(), get_pos_y()]
            my_positions.append(pos)
            
            # 收割
            if can_harvest():
                harvest()
                local_harvested += 1
            
            # 翻土
            if get_ground_type() != Grounds.Soil:
                till()
                local_tilled += 1
            
            # 种植
            plant(Entities.Carrot)
            local_planted += 1
            
            if x < get_world_size() - 1:
                move(East)
        
        # 更新共享状态（使用 += 操作，相对安全）
        state = wait_for(state_drone)
        state["harvested"] += local_harvested
        state["planted"] += local_planted
        state["tilled"] += local_tilled
        
        # 追加位置（安全操作）
        for pos in my_positions:
            state["positions"].append(pos)
        
        return local_planted
    
    # 启动多个工作者
    drones = []
    for y in range(min(4, get_world_size())):
        # 移动到每一行的起点
        # goto(0, y)
        
        drone = spawn_drone(farm_worker)
        if drone:
            drones.append(drone)
    
    # 等待完成
    for drone in drones:
        wait_for(drone)
    
    # 获取最终状态
    final_state = wait_for(state_drone)
    quick_print("Total harvested:", final_state["harvested"])
    quick_print("Total planted:", final_state["planted"])
    quick_print("Total tilled:", final_state["tilled"])
    quick_print("Positions processed:", len(final_state["positions"]))

# ========================================
# 主程序：运行示例
# ========================================

if num_unlocked(Unlocks.Megafarm) > 0:
    # 选择要运行的示例
    # example1_parallel_collection()
    # example2_realtime_stats()
    # example3_progress_tracking()
    # example4_task_queue()
    # example5_collaborative_farming()
    
    quick_print("Shared memory examples ready!")
    quick_print("Uncomment one example to run")
else:
    quick_print("Megafarm not unlocked!")

# ========================================
# 关键要点总结
# ========================================
# 1. 创建源无人机返回共享对象
# 2. 多个工作者通过 wait_for(源) 获取同一对象
# 3. 优先使用追加操作（append）
# 4. 或使用独立键（每个无人机一个键）
# 5. 避免读-修改-写序列
# 6. 谨慎处理竞态条件
# ========================================

