# 32x32南瓜挑战 - 16区域32无人机协作系统（精简版）

from farm_utils import short_goto, goto_pos

# 16个6x6区域的左下角坐标
REGIONS = [
    (0, 0), (0, 7), (0, 19), (0, 26),
    (7, 0), (7, 7), (7, 19), (7, 26),
    (19, 0), (19, 7), (19, 19), (19, 26),
    (26, 0), (26, 7), (26, 19), (26, 26)
]

# 路径定义
LEFT_PLANT = [East, East, North, North, North, North, North, West, West, South, East, South, West, South, East, South, West]
LEFT_SCAN = [South, East, East, North, North, North, North, North, West, West, South, East, South, West, South, East, South, West]
RIGHT_PLANT = [West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East]
RIGHT_SCAN = [South, West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East]

def create_shared():
    return {"stop": False}

def create_worker(region_x, region_y, is_left):
    def worker():
        shared = wait_for(memory_source)
        region_key = str(region_x) + "," + str(region_y)
        
        if region_key not in shared:
            shared[region_key] = {"ready": False}
        
        region_data = shared[region_key]
        
        # 确定起始位置和路径
        if is_left:
            start_x = region_x
            plant_dirs = LEFT_PLANT
            scan_dirs = LEFT_SCAN
        else:
            start_x = region_x + 5
            plant_dirs = RIGHT_PLANT
            scan_dirs = RIGHT_SCAN
        
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
            
            # 移动到起始位置
            goto_pos(start_x, region_y)
            
            # 阶段1：种植
            for direction in plant_dirs:
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                move(direction)
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            
            # 阶段2：扫描未成熟南瓜
            unverified = []
            for direction in scan_dirs:
                move(direction)
                if not can_harvest():
                    plant(Entities.Pumpkin)
                    unverified.append((get_pos_x(), get_pos_y()))
                    if num_items(Items.Water) > 10 and get_water() < 0.8:
                        use_item(Items.Water)
            
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
                short_goto(start_x, region_y)
                if is_left:
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
                else:
                    region_data["ready"] = False
    
    return worker

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
    shared[region_key] = {"ready": False}

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
    
    # 移动到起始位置
    short_goto(region_x, region_y)
    
    # 阶段1：种植
    for direction in LEFT_PLANT:
        if shared["stop"]:
            break
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Pumpkin)
        move(direction)
    if not shared["stop"]:
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Pumpkin)
    
    if shared["stop"]:
        break
    
    # 阶段2：扫描未成熟南瓜
    unverified = []
    for direction in LEFT_SCAN:
        if shared["stop"]:
            break
        move(direction)
        if not can_harvest():
            plant(Entities.Pumpkin)
            unverified.append((get_pos_x(), get_pos_y()))
            if num_items(Items.Water) > 10 and get_water() < 0.8:
                use_item(Items.Water)
    
    if shared["stop"]:
        break
    
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
    
    if shared["stop"]:
        break
    
    # 同步收获
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