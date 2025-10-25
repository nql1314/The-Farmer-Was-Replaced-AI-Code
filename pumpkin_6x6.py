# 6x6南瓜挑战 - 双无人机协作系统

# ================================
# 工具函数
# ================================

from builtins import set
from farm_utils import short_goto,goto_pos

directions1 = [East,East,North,North,North,North,North,West,West,South,East,South,West,South,East,South,West]
directions2 = [South,East,East,North,North,North,North,North,West,West,South,East,South,West,South,East,South,West]
directions3 = [West,West,North,North,North,North,North,East,East,South,West,South,East,South,West,South,East]
directions4 = [South,West,West,North,North,North,North,North,East,East,South,West,South,East,South,West,South,East]


def log_move(drone_id, x, y, direction, tick):
    # 打印移动信息
    dir_name = "North"
    if direction == East:
        dir_name = "East"
    elif direction == South:
        dir_name = "South"
    elif direction == West:
        dir_name = "West"
    
    quick_print("Drone", drone_id, "at (", x, ",", y, ") moving", dir_name, "tick:", tick)

def safe_move(drone_id, direction):
    # 安全移动并记录
    x = get_pos_x()
    y = get_pos_y()
    tick = get_tick_count()
    log_move(drone_id, x, y, direction, tick)
    move(direction)

# ================================
# 共享内存初始化
# ================================

def create_shared_memory():
    # 创建共享数据结构
    return {
        "unverified_set": set(),
        "unverified_list": [],
        "id1": None,
        "id2": None
    }

# ================================
# 无人机A（左半边）
# ================================

def drone_a_worker():
    drone_id = "A"
    
    # 获取共享内存
    shared = wait_for(memory_source)
    # 初始化未验证列表
    shared["unverified_set"] = set()
    shared["unverified_list"] = []
    # 移动到左下角 (0, 0)
    short_goto(0, 0)
    
    quick_print("Drone A: Starting at (0,0)")
    
    while True:
        # ================================
        # 第一阶段：种满左半边区域
        # ================================
        quick_print("Drone A: Phase 1 - Planting left half")
        for direction in directions1:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            safe_move(drone_id, direction)
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Pumpkin)
        # ================================
        # 第二阶段：遍历区域，记录未成熟的南瓜  
        # ================================
        quick_print("Drone A: Phase 2 - Scanning left half")
        
        # 当前位置是(0, 1)，开始遍历，蛇形遍历
        for direction in directions2:
            safe_move(drone_id, direction)
            pos = (get_pos_x(), get_pos_y())
            # 检查是否成熟
            if not can_harvest():
                # 未成熟，加入未验证集合
                if pos not in shared["unverified_set"]:
                    shared["unverified_set"].add(pos)
                    shared["unverified_list"].append(pos)
        
        quick_print("Drone A: Found", len(shared["unverified_list"]), "unverified pumpkins")
        
        # ================================
        # 第三阶段：验证和补种
        # ================================
        quick_print("Drone A: Phase 3 - Verifying and replanting")
        
        while len(shared["unverified_list"]) > 0:
            # 取出一个位置
            target_x, target_y = shared["unverified_list"][0]
            shared["unverified_list"].pop(0)
            
            # 导航到目标位置
            short_goto(target_x, target_y)
            
            # 检查状态
            entity = get_entity_type()
            
            if entity == Entities.Pumpkin:
                if can_harvest():
                    # 已成熟，从集合中移除
                    pos = (get_pos_x(), get_pos_y())
                    if pos in shared["unverified_set"]:
                        shared["unverified_set"].remove(pos)
                    quick_print("Drone A: Verified at", pos)
                else:
                    # 还未成熟
                    if len(shared["unverified_list"]) == 0:
                        # 这是最后一个，浇水并等待
                        quick_print("Drone A: Last pumpkin, watering and waiting")
                        if num_items(Items.Water) > 0 and get_water() < 0.8:
                            use_item(Items.Water)
                        
                        # 等待成熟或枯萎
                        while get_entity_type() == Entities.Pumpkin and not can_harvest():
                            pass
                        
                        # 重新检查状态
                        final_entity = get_entity_type()
                        if final_entity == Entities.Pumpkin and can_harvest():
                            # 成熟了，移除
                            pos = (get_pos_x(), get_pos_y())
                            if pos in shared["unverified_set"]:
                                shared["unverified_set"].remove(pos)
                            quick_print("Drone A: Last pumpkin matured at", pos)
                        elif final_entity == Entities.Dead_Pumpkin:
                            # 变成枯萎南瓜，补种
                            quick_print("Drone A: Last pumpkin withered, replanting")
                            plant(Entities.Pumpkin)
                            pos = (get_pos_x(), get_pos_y())
                            shared["unverified_list"].append(pos)
                    else:
                        # 不是最后一个，加回列表
                        pos = (get_pos_x(), get_pos_y())
                        shared["unverified_list"].append(pos)
            
            elif entity == Entities.Dead_Pumpkin:
                # 枯萎了，补种
                quick_print("Drone A: Replanting dead pumpkin at", (get_pos_x(), get_pos_y()))
                plant(Entities.Pumpkin)
                # 加回列表
                pos = (get_pos_x(), get_pos_y())
                shared["unverified_list"].append(pos)
        
        quick_print("Drone A: Phase 3 complete, all pumpkins verified")
        
        # ================================
        # 第四阶段：去左下角等待收获信号
        # ================================
        quick_print("Drone A: Phase 4 - Waiting for harvest signal")
        
        # 移动到左下角 (0, 0)
        short_goto(0, 0)
        
        # 不断记录id1，直到id1 == id2
        while True:
            # 记录当前measure结果
            current_id = measure()
            shared["id1"] = current_id
            
            quick_print("Drone A: id1 =", current_id, ", id2 =", shared["id2"])
            
            # 检查是否一致
            if shared["id1"] == shared["id2"] and shared["id1"] != None:
                quick_print("Drone A: IDs match! Harvesting...")
                harvest()
                break
        
        quick_print("Drone A: Harvest complete, starting new cycle")

# ================================
# 无人机B（右半边）
# ================================

def drone_b_worker():
    drone_id = "B"
    
    # 获取共享内存
    shared = wait_for(memory_source)
    
    # 移动到 (5, 0)
    short_goto(5, 0)
    
    quick_print("Drone B: Starting at (5,0)")
    
    while True:
        # ================================
        # 第一阶段：种满右半边区域
        # ================================
        quick_print("Drone B: Phase 1 - Planting right half")
        
        for direction in directions3:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            safe_move(drone_id, direction)
        if get_ground_type() != Grounds.Soil:
                till()
        plant(Entities.Pumpkin)
        # ================================
        # 第二阶段：遍历区域，记录未成熟的南瓜
        # ================================
        quick_print("Drone B: Phase 2 - Scanning right half")
        
        # 当前位置是(6, 1)，开始遍历，蛇形遍历
        for direction in directions4:
            safe_move(drone_id, direction)
            pos = (get_pos_x(), get_pos_y())
            # 检查是否成熟
            if not can_harvest():
                # 未成熟，加入未验证集合
                if pos not in shared["unverified_set"]:
                    shared["unverified_set"].add(pos)
                    shared["unverified_list"].append(pos)
        
        quick_print("Drone B: Found", len(shared["unverified_list"]), "unverified pumpkins (total)")
        
        # ================================
        # 第三阶段：验证和补种
        # ================================
        quick_print("Drone B: Phase 3 - Verifying and replanting")
        
        while len(shared["unverified_list"]) > 0:
            # 取出一个位置
            target_x, target_y = shared["unverified_list"][0]
            shared["unverified_list"].pop(0)
            
            # 导航到目标位置
            short_goto(target_x, target_y)
            
            # 检查状态
            entity = get_entity_type()
            
            if entity == Entities.Pumpkin:
                if can_harvest():
                    # 已成熟，从集合中移除
                    pos = (get_pos_x(), get_pos_y())
                    if pos in shared["unverified_set"]:
                        shared["unverified_set"].remove(pos)
                    quick_print("Drone B: Verified at", pos)
                else:
                    # 还未成熟
                    if len(shared["unverified_list"]) == 0:
                        # 这是最后一个，浇水并等待
                        quick_print("Drone B: Last pumpkin, watering and waiting")
                        if num_items(Items.Water) > 0 and get_water() < 0.8:
                            use_item(Items.Water)
                        
                        # 等待成熟或枯萎
                        while get_entity_type() == Entities.Pumpkin and not can_harvest():
                            pass
                        
                        # 重新检查状态
                        final_entity = get_entity_type()
                        if final_entity == Entities.Pumpkin and can_harvest():
                            # 成熟了，移除
                            pos = (get_pos_x(), get_pos_y())
                            if pos in shared["unverified_set"]:
                                shared["unverified_set"].remove(pos)
                            quick_print("Drone B: Last pumpkin matured at", pos)
                        elif final_entity == Entities.Dead_Pumpkin:
                            # 变成枯萎南瓜，补种
                            quick_print("Drone B: Last pumpkin withered, replanting")
                            plant(Entities.Pumpkin)
                            pos = (get_pos_x(), get_pos_y())
                            shared["unverified_list"].append(pos)
                    else:
                        # 不是最后一个，加回列表
                        pos = (get_pos_x(), get_pos_y())
                        shared["unverified_list"].append(pos)
            
            elif entity == Entities.Dead_Pumpkin:
                # 枯萎了，补种
                quick_print("Drone B: Replanting dead pumpkin at", (get_pos_x(), get_pos_y()))
                plant(Entities.Pumpkin)
                # 加回列表
                pos = (get_pos_x(), get_pos_y())
                shared["unverified_list"].append(pos)
            
            elif entity == None:
                # 空地，重新种植
                quick_print("Drone B: Replanting empty spot at", (get_pos_x(), get_pos_y()))
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                # 加回列表
                pos = (get_pos_x(), get_pos_y())
                shared["unverified_list"].append(pos)
        
        quick_print("Drone B: Phase 3 complete, all pumpkins verified")
        
        # ================================
        # 第四阶段：去右下角等待收获信号
        # ================================
        quick_print("Drone B: Phase 4 - Monitoring right corner")
        
        # 移动到右下角 (5, 0)
        short_goto(5, 0)
        
        # 不断记录id2，如果measure是None则结束收获
        while True:
            # 记录当前measure结果
            current_id = measure()
            shared["id2"] = current_id
            
            quick_print("Drone B: id2 =", current_id)
            
            # 如果measure是None，说明已经收获完成
            if current_id == None:
                quick_print("Drone B: Harvest detected (measure is None), starting new cycle")
                break
            
# ================================
# 主程序
# ================================

quick_print("=== 6x6 Pumpkin Challenge - Dual Drone System ===")
clear()
# 初始化共享内存
memory_source = spawn_drone(create_shared_memory)
quick_print("Shared memory initialized")

# 启动无人机A（左半边）
drone_a = spawn_drone(drone_a_worker)
quick_print("Drone A spawned (left half)")

# 启动无人机B（右半边）
drone_b = spawn_drone(drone_b_worker)
quick_print("Drone B spawned (right half)")

# 等待两个无人机完成（它们会无限循环）
quick_print("Main: Both drones active, monitoring...")

# 主无人机可以在这里做其他事情或监控
while True:
    do_a_flip()
