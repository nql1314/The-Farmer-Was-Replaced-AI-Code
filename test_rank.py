# 32x32南瓜挑战 - 16区域32无人机协作系统（精简版）

from farm_utils import short_goto, goto_pos

# 16个6x6区域的左下角坐标
REGIONS = [
    (0, 0), (0, 7), (0, 19), (0, 26),
    (7, 0), (7, 7), (7, 19), (7, 26),
    (19, 0), (19, 7), (19, 19), (19, 26),
    (26, 0), (26, 7), (26, 19), (26, 26)
]

# 路径定义：位置与方向的映射 {(x_offset, y_offset): direction}
# 左半边路径
LEFT_PATH = {
    (0, 0): East, (1, 0): East, (2, 0): North,
    (2, 1): North, (2, 2): North, (2, 3): North, (2, 4): North, (2, 5): West,
    (1, 5): West, (0, 5): South, (0, 4): East, (1, 4): South,
    (1, 3): West, (0, 3): South, (0, 2): East, (1, 2): South,
    (1, 1): West, (0, 1): South
}

# 右半边路径
RIGHT_PATH = {
    (5, 0): West, (4, 0): West, (3, 0): North,
    (3, 1): North, (3, 2): North, (3, 3): North, (3, 4): North, (3, 5): East,
    (4, 5): East, (5, 5): South, (5, 4): West, (4, 4): South,
    (4, 3): East, (5, 3): South, (5, 2): West, (4, 2): South,
    (4, 1): East, (5, 1): South
}

# 计算最优路径（贪心最近邻算法）
def find_optimal_path(current_x, current_y, positions):
    if len(positions) == 0:
        return []
    
    # 使用贪心算法：每次选择最近的未访问位置
    result = []
    visited = []
    cx = current_x
    cy = current_y
    remaining = []
    for pos in positions:
        remaining.append(pos)
    
    while remaining:
        min_dist = 999999
        nearest_idx = 0
        
        for i in range(len(remaining)):
            tx, ty = remaining[i]
            dist = abs(tx - cx) + abs(ty - cy)
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i
        
        target = remaining[nearest_idx]
        remaining.pop(nearest_idx)
        result.append(target)
        cx, cy = target
    
    return result

def create_shared():
    return {"stop": False}

def create_worker(region_x, region_y, is_left):
    def worker():
        shared = wait_for(memory_source)
        region_key = str(region_x) + "," + str(region_y)
        
        if region_key not in shared:
            shared[region_key] = {"ready": False}
        
        region_data = shared[region_key]
        
        # 确定路径
        if is_left:
            path_map = LEFT_PATH
            start_offset_x = 0
        else:
            path_map = RIGHT_PATH
            start_offset_x = 5
        
        while True:
            # 检查停止信号
            if shared["stop"]:
                break
            
            # 等待右半边完成
            if is_left:
                while region_data["ready"]:
                    if shared["stop"]:
                        break
                    pass
                if shared["stop"]:
                    break
            
            # 阶段1：种植（不需要回到起始位置，从当前位置开始）
            for i in range(18):
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                move(path_map[(get_pos_x() - region_x, get_pos_y() - region_y)])
            # 阶段2：扫描未成熟南瓜
            unverified = []
            for i in range(18):
                if not can_harvest():
                    plant(Entities.Pumpkin)
                    current_x = get_pos_x()
                    current_y = get_pos_y()
                    unverified.append((current_x, current_y))
                    if num_items(Items.Water) > 10 and get_water() < 0.8:
                        use_item(Items.Water)
                move(path_map[(current_x - region_x, current_y - region_y)])
            
            unverified = find_optimal_path(get_pos_x(), get_pos_y(), unverified)

            # 阶段3：验证和补种
            while unverified:
                if shared["stop"]:
                    break
                target_x, target_y = unverified[0]
                unverified.pop(0)
                short_goto(target_x, target_y)
                
                entity = get_entity_type()
                if entity == Entities.Pumpkin:
                    if can_harvest():
                        pass
                    else:
                        if len(unverified) == 0:
                            if num_items(Items.Water) > 0 and get_water() < 0.8:
                                use_item(Items.Water)
                            while get_entity_type() == Entities.Pumpkin and not can_harvest():
                                if shared["stop"]:
                                    break
                                pass
                            if get_entity_type() == Entities.Dead_Pumpkin:
                                plant(Entities.Pumpkin)
                                unverified.append((get_pos_x(), get_pos_y()))
                        else:
                            unverified.append((get_pos_x(), get_pos_y()))
                elif entity == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    unverified.append((get_pos_x(), get_pos_y()))
            
            # 同步收获
            if not shared["stop"]:
                if is_left:
                    while region_data["ready"]:
                        if shared["stop"]:
                            break
                        pass
                    if not shared["stop"]:
                        for i in range(98):
                            pass
                        harvest()
                        if num_items(Items.Pumpkin) >= 200000000:
                            shared["stop"] = True
                            break
                else:
                    region_data["ready"] = False
# 主程序
clear()
memory_source = spawn_drone(create_shared)

# 生成区域工作无人机（除了第一个区域的左半边）
for region_idx in range(1, len(REGIONS)):
    region_x, region_y = REGIONS[region_idx]
    spawn_drone(create_worker(region_x, region_y, True))
    spawn_drone(create_worker(region_x, region_y, False))

# 第一个区域的右半边
region_x, region_y = REGIONS[0]
spawn_drone(create_worker(region_x, region_y, False))

# 主无人机执行第一个区域的左半边工作
shared = wait_for(memory_source)
region_key = str(region_x) + "," + str(region_y)

if region_key not in shared:
    shared[region_key] = {"ready": False, "round": 0}

region_data = shared[region_key]

while True:
    # 检查南瓜数量并设置停止信号
    if num_items(Items.Pumpkin) >= 200000000:
        shared["stop"] = True
        break
    
    # 等待右半边完成
    while region_data["ready"]:
        if num_items(Items.Pumpkin) >= 200000000:
            shared["stop"] = True
            break
        pass
    
    if shared["stop"]:
        break
    
    # 增加轮次
    region_data["round"] += 1
    current_round = region_data["round"]
    
    # 阶段1：种植（不需要回到起始位置，从当前位置开始）
    
    for i in range(18):
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Pumpkin)
        move(LEFT_PATH[(get_pos_x() - region_x, get_pos_y() - region_y)])
    
    if shared["stop"]:
        break
    
    # 阶段2：扫描未成熟南瓜
    unverified = []
    for i in range(18):
        if shared["stop"]:
            break
        if not can_harvest():
            plant(Entities.Pumpkin)
            current_x = get_pos_x()
            current_y = get_pos_y()
            unverified.append((current_x, current_y))
            if num_items(Items.Water) > 10 and get_water() < 0.8:
                use_item(Items.Water)
        move(LEFT_PATH[(current_x - region_x, current_y - region_y)])
    
    # 阶段3：验证和补种（使用最优路径）
    unverified = find_optimal_path(get_pos_x(), get_pos_y(), unverified)
    while unverified:
        if shared["stop"]:
            break
        target_x, target_y = unverified[0]
        unverified.pop(0)
        short_goto(target_x, target_y)
        
        entity = get_entity_type()
        if entity == Entities.Pumpkin:
            if can_harvest():
                pass
            else:
                if len(unverified) == 0:
                    if num_items(Items.Water) > 0 and get_water() < 0.8:
                        use_item(Items.Water)
                    while get_entity_type() == Entities.Pumpkin and not can_harvest():
                        if shared["stop"]:
                            break
                        pass
                    if get_entity_type() == Entities.Dead_Pumpkin:
                        plant(Entities.Pumpkin)
                        unverified.append((get_pos_x(), get_pos_y()))
                else:
                    unverified.append((get_pos_x(), get_pos_y()))
        elif entity == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
            unverified.append((get_pos_x(), get_pos_y()))
                    
    if shared["stop"]:
        break
    
    # 同步收获（移动到收获位置）
    short_goto(region_x, region_y)
    region_data["ready"] = True
    while region_data["ready"]:
        if shared["stop"]:
            break
        pass
    if not shared["stop"]:
        for i in range(98):
            pass
        harvest()
        if num_items(Items.Pumpkin) >= 200000000:
            shared["stop"] = True
            break