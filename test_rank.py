# 32x32南瓜挑战 - 16区域32无人机协作系统
# 将32x32地图划分为16个6x6区域
# 每个区域由2个无人机协作处理

from builtins import set
from farm_utils import short_goto

# ================================
# 全局配置
# ================================

# 16个6x6区域的左下角坐标
REGIONS = [
    (0, 0), (0, 7), (0, 19), (0, 26),
    (7, 0), (7, 7), (7, 19), (7, 26),
    (19, 0), (19, 7), (19, 19), (19, 26),
    (26, 0), (26, 7), (26, 19), (26, 26)
]

# 左半边种植路径（从(0,0)开始）
directions1 = [East, East, North, North, North, North, North, West, West, South, East, South, West, South, East, South, West]
# 左半边扫描路径（从(0,1)开始）
directions2 = [South, East, East, North, North, North, North, North, West, West, South, East, South, West, South, East, South, West]

# 右半边种植路径（从(5,0)开始）
directions3 = [West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East]
# 右半边扫描路径（从(5,1)开始）
directions4 = [South, West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East]

# ================================
# 工具函数
# ================================

def log_move(drone_id, x, y, direction, tick):
    # 打印移动信息（简化版，减少输出）
    pass

def safe_move(drone_id, direction):
    # 安全移动
    move(direction)

# ================================
# 共享内存初始化
# ================================

def create_shared_memory():
    # 创建共享数据结构
    # 每个区域有独立的数据块，用区域坐标作为键
    return {}

# ================================
# 通用的区域工作函数
# ================================

def create_region_worker(region_x, region_y, is_left_half):
    # 创建区域工作函数的工厂函数
    # region_x, region_y: 区域左下角坐标
    # is_left_half: True表示处理左半边，False表示处理右半边
    
    def worker():
        if is_left_half:
            drone_id = "L" + str(region_x) + "," + str(region_y)
        else:
            drone_id = "R" + str(region_x) + "," + str(region_y)
        
        # 获取共享内存
        shared = wait_for(memory_source)
        
        # 创建该区域的独立数据块（使用区域坐标作为键）
        region_key = str(region_x) + "," + str(region_y)
        if region_key not in shared:
            shared[region_key] = {
                "unverified_set": set(),
                "unverified_list": [],
                "id1": None,
                "id2": None
            }
        
        # 获取该区域的数据
        region_data = shared[region_key]
        
        # 确定起始位置和路径
        if is_left_half:
            start_x = region_x
            start_y = region_y
            plant_dirs = directions1
            scan_dirs = directions2
        else:
            start_x = region_x + 5
            start_y = region_y
            plant_dirs = directions3
            scan_dirs = directions4
        
        # 移动到起始位置
        short_goto(start_x, start_y)
        
        quick_print("Drone", drone_id, "starting at", start_x, ",", start_y)
        
        while True:
            # ================================
            # 第一阶段：种植
            # ================================
            for direction in plant_dirs:
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                safe_move(drone_id, direction)
            
            # 最后一个位置也要种植
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            
            # ================================
            # 第二阶段：扫描并记录未成熟南瓜
            # ================================
            if is_left_half:
                # 左半边初始化未验证集合
                region_data["unverified_set"] = set()
                region_data["unverified_list"] = []
            
            for direction in scan_dirs:
                safe_move(drone_id, direction)
                pos = (get_pos_x(), get_pos_y())
                
                # 检查是否成熟
                if not can_harvest():
                    # 未成熟，加入未验证集合
                    if pos not in region_data["unverified_set"]:
                        region_data["unverified_set"].add(pos)
                        region_data["unverified_list"].append(pos)
            
            # ================================
            # 第三阶段：验证和补种
            # ================================
            while len(region_data["unverified_list"]) > 0:
                # 取出一个位置
                target_x, target_y = region_data["unverified_list"][0]
                region_data["unverified_list"].pop(0)
                
                # 导航到目标位置
                short_goto(target_x, target_y)
                
                # 检查状态
                entity = get_entity_type()
                
                if entity == Entities.Pumpkin:
                    if can_harvest():
                        # 已成熟，从集合中移除
                        pos = (get_pos_x(), get_pos_y())
                        if pos in region_data["unverified_set"]:
                            region_data["unverified_set"].remove(pos)
                    else:
                        # 还未成熟
                        if len(region_data["unverified_list"]) == 0:
                            # 这是最后一个，浇水并等待
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
                                if pos in region_data["unverified_set"]:
                                    region_data["unverified_set"].remove(pos)
                            elif final_entity == Entities.Dead_Pumpkin:
                                # 变成枯萎南瓜，补种
                                plant(Entities.Pumpkin)
                                pos = (get_pos_x(), get_pos_y())
                                region_data["unverified_list"].append(pos)
                        else:
                            # 不是最后一个，加回列表
                            pos = (get_pos_x(), get_pos_y())
                            region_data["unverified_list"].append(pos)
                
                elif entity == Entities.Dead_Pumpkin:
                    # 枯萎了，补种
                    plant(Entities.Pumpkin)
                    pos = (get_pos_x(), get_pos_y())
                    region_data["unverified_list"].append(pos)
            
            # ================================
            # 第四阶段：等待收获信号
            # ================================
            short_goto(start_x, start_y)
            
            if is_left_half:
                # 左半边：记录id1，直到id1 == id2
                while True:
                    current_id = measure()
                    region_data["id1"] = current_id
                    
                    # 检查是否一致
                    if region_data["id1"] == region_data["id2"] and region_data["id1"] != None:
                        harvest()
                        break
            else:
                # 右半边：记录id2，直到measure是None
                while True:
                    current_id = measure()
                    region_data["id2"] = current_id
                    
                    # 如果measure是None，说明已经收获完成
                    if current_id == None:
                        break
    
    return worker

# ================================
# 主程序
# ================================

quick_print("=== 32x32 Pumpkin Challenge - 32 Drones System ===")
clear()

# 初始化共享内存（1个无人机）
memory_source = spawn_drone(create_shared_memory)
quick_print("Shared memory initialized")

# 生成区域工作无人机
drones = []
drone_count = 0

# 先为2-16号区域（索引1-15）生成无人机
quick_print("Spawning drones for regions 2-16...")
for region_idx in range(1, len(REGIONS)):
    region_x, region_y = REGIONS[region_idx]
    
    # 左半边无人机
    left_worker = create_region_worker(region_x, region_y, True)
    drone_left = spawn_drone(left_worker)
    if drone_left:
        drones.append(drone_left)
        drone_count += 1
        quick_print("Spawned left drone for region", region_idx + 1, "(", region_x, ",", region_y, ")")
    
    # 右半边无人机
    right_worker = create_region_worker(region_x, region_y, False)
    drone_right = spawn_drone(right_worker)
    if drone_right:
        drones.append(drone_right)
        drone_count += 1
        quick_print("Spawned right drone for region", region_idx + 1, "(", region_x, ",", region_y, ")")

quick_print("Drones spawned for regions 2-16:", drone_count)

region_x, region_y = REGIONS[0]
right_worker = create_region_worker(region_x, region_y, False)
drone_right = spawn_drone(right_worker)
if drone_right:
    drones.append(drone_right)
    drone_count += 1
    quick_print("Spawned right drone for region 1 (", region_x, ",", region_y, ")")

quick_print("Total drones spawned:", drone_count)
quick_print("Max drones available:", num_unlocked(Unlocks.Megafarm))

# 主无人机加入第一个区域的左半边工作
quick_print("Main drone joining region 1 (left half)")

# 获取共享内存
shared = wait_for(memory_source)

# 主无人机执行第一个区域的左半边工作
start_x = region_x
start_y = region_y
drone_id = "MAIN"

# 创建第一个区域的独立数据块
region_key = str(region_x) + "," + str(region_y)
if region_key not in shared:
    shared[region_key] = {
        "unverified_set": set(),
        "unverified_list": [],
        "id1": None,
        "id2": None
    }

# 获取第一个区域的数据
region_data = shared[region_key]

short_goto(start_x, start_y)
quick_print("Main drone at region 1 (0, 0)")

while True:
    # ================================
    # 第一阶段：种植
    # ================================
    for direction in directions1:
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Pumpkin)
        safe_move(drone_id, direction)
    
    if get_ground_type() != Grounds.Soil:
        till()
    plant(Entities.Pumpkin)
    
    # ================================
    # 第二阶段：扫描
    # ================================
    region_data["unverified_set"] = set()
    region_data["unverified_list"] = []
    
    for direction in directions2:
        safe_move(drone_id, direction)
        pos = (get_pos_x(), get_pos_y())
        
        if not can_harvest():
            if pos not in region_data["unverified_set"]:
                region_data["unverified_set"].add(pos)
                region_data["unverified_list"].append(pos)
    
    # ================================
    # 第三阶段：验证和补种
    # ================================
    while len(region_data["unverified_list"]) > 0:
        target_x, target_y = region_data["unverified_list"][0]
        region_data["unverified_list"].pop(0)
        
        short_goto(target_x, target_y)
        entity = get_entity_type()
        
        if entity == Entities.Pumpkin:
            if can_harvest():
                pos = (get_pos_x(), get_pos_y())
                if pos in region_data["unverified_set"]:
                    region_data["unverified_set"].remove(pos)
            else:
                if len(region_data["unverified_list"]) == 0:
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
                        if pos in region_data["unverified_set"]:
                            region_data["unverified_set"].remove(pos)
                    elif final_entity == Entities.Dead_Pumpkin:
                        # 变成枯萎南瓜，补种
                        plant(Entities.Pumpkin)
                        pos = (get_pos_x(), get_pos_y())
                        region_data["unverified_list"].append(pos)
                else:
                    pos = (get_pos_x(), get_pos_y())
                    region_data["unverified_list"].append(pos)
        
        elif entity == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
            pos = (get_pos_x(), get_pos_y())
            region_data["unverified_list"].append(pos)
    
    # ================================
    # 第四阶段：等待收获
    # ================================
    short_goto(start_x, start_y)
    
    while True:
        current_id = measure()
        region_data["id1"] = current_id
        
        if region_data["id1"] == region_data["id2"] and region_data["id1"] != None:
            harvest()
            quick_print("Main: Harvest complete, cycle", get_tick_count())
            break

            