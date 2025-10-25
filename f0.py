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
PATH = {
    (0, 0): East, (1, 0): East, (2, 0): North,
    (2, 1): North, (2, 2): North, (2, 3): North, (2, 4): North, (2, 5): West,
    (1, 5): West, (0, 5): South, (0, 4): East, (1, 4): South,
    (1, 3): West, (0, 3): South, (0, 2): East, (1, 2): South,
    (1, 1): West, (0, 1): South
}

def create_shared():
    return {"stop": False}


def create_worker(region_x, region_y, is_left):
    def worker():
        shared = wait_for(memory_source)
        region_key = str(region_x) + "," + str(region_y)
        
        if region_key not in shared:
            shared[region_key] = {"ready": False}
        
        region_data = shared[region_key]
        
        if is_left:
            start_x = region_x
        else:
            start_x = region_x + 3

        goto_pos(start_x, region_y)
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
            
            # 阶段1：种植
            for direction in PATH:
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                move(PATH[(get_pos_x() - start_x, get_pos_y() - region_y)])
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            
            # 阶段2：扫描未成熟南瓜
            unverified = []
            for direction in PATH:
                current_x = get_pos_x()
                current_y = get_pos_y()
                if not can_harvest():
                    plant(Entities.Pumpkin)
                    unverified.append((current_x, current_y))
                    if num_items(Items.Water) > 10 and get_water() < 0.8:
                        use_item(Items.Water)
                move(PATH[(current_x - start_x, current_y - region_y)])
            
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
                        if get_water() < 0.8:
                            use_item(Items.Water)
                        while get_entity_type() == Entities.Pumpkin and not can_harvest():
                            if shared["stop"]:
                                break
                            if num_items(Items.Fertilizer) > 0:
                                use_item(Items.Fertilizer)
                        if get_entity_type() == Entities.Dead_Pumpkin:
                            plant(Entities.Pumpkin)
                            unverified.append((get_pos_x(), get_pos_y()))
                elif entity == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    unverified.append((get_pos_x(), get_pos_y()))
            
            # 同步收获
            if not shared["stop"]:
                if is_left:
                    while not region_data["ready"]:
                        if shared["stop"]:
                            break
                    if not shared["stop"]:
                        for i in range(98):
                            pass
                        harvest()
                        if num_items(Items.Pumpkin) >= 200000000:
                            shared["stop"] = True
                            break
                        region_data["ready"] = False
                else:
                    region_data["ready"] = True
    
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

goto_pos(region_x, region_y)
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
    
    # 阶段1：种植
    for direction in PATH:
        if shared["stop"]:
            break
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Pumpkin)
        move(PATH[(get_pos_x() - region_x, get_pos_y() - region_y)])

    if shared["stop"]:
        break
    
    # 阶段2：扫描未成熟南瓜
    unverified = []
    for direction in PATH:
        if shared["stop"]:
            break
        current_x = get_pos_x()
        current_y = get_pos_y()
        if not can_harvest():
            plant(Entities.Pumpkin)
            unverified.append((current_x, current_y))
            if num_items(Items.Water) > 10 and get_water() < 0.8:
                use_item(Items.Water)
        move(PATH[(current_x - region_x, current_y - region_y)])

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
                if get_water() < 0.8:
                    use_item(Items.Water)
                while get_entity_type() == Entities.Pumpkin and not can_harvest():
                    if shared["stop"]:
                        break
                    if num_items(Items.Fertilizer) > 0:
                        use_item(Items.Fertilizer)
                if get_entity_type() == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    unverified.append((get_pos_x(), get_pos_y()))
        elif entity == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
            unverified.append((get_pos_x(), get_pos_y()))
    
    if shared["stop"]:
        break
    
    # 同步收获
    while not region_data["ready"]:
        if shared["stop"]:
            break
    if not shared["stop"]:
        for i in range(98):
            pass
        harvest()
        region_data["ready"] = False
        if num_items(Items.Pumpkin) >= 200000000:
            shared["stop"] = True
            break