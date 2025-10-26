# 32x32南瓜挑战 - 16区域32无人机协作系统（精简版）

from farm_utils import short_goto, goto

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

WATER_THRESHOLD = 0.85
WATER_COUNT = 100

def create_shared():
    return {
    (0, 7):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
    (0, 19):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
    (0, 26):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
    (7, 0):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (7, 7):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (7, 19):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (7, 26):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (19, 0):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (19, 7):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (19, 19):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (19, 26):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (26, 0):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (26, 7):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (26, 19):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (26, 26):{'ready':False,'unverified_right':[],"unverified_left":[],"help_flag":False},
    (0, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False}}

def loop_verify(region_data):
    while get_entity_type() == Entities.Pumpkin and not can_harvest():
        use_item(Items.Fertilizer)
    if get_entity_type() == Entities.Dead_Pumpkin:
        plant(Entities.Pumpkin)
        loop_verify(region_data)

def help(region_data, unverified_name):
    unverified = region_data[unverified_name]
    unverified_len = len(unverified)
    if unverified_len <= 1:
        return
    region_data["help_flag"] = True
    # 方案1：使用末尾元素（最安全，零竞争风险）
    if unverified_len >= 1:
        # 先取出最后一个元素（原子操作）
        target_x, target_y = unverified[-1]
        unverified.pop()
        short_goto(target_x, target_y)
        entity = get_entity_type()
        if entity == Entities.Pumpkin:
            if not can_harvest():
                loop_verify(region_data)
        elif entity == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
            loop_verify(region_data)
    region_data["help_flag"] = False
    return

def create_worker_left(region_x, region_y):

    def worker():
        goto(region_x, region_y)
        spawn_drone(create_worker_right(region_x, region_y))
        shared = wait_for(memory_source)
        region_data = shared[(region_x, region_y)]

        while True: #114
            current_pos_x = get_pos_x()
            if (current_pos_x >= region_x + 3):
                short_goto(region_x + 2, get_pos_y())
            # 等待右半边完成
            while region_data["ready"]:
                pass

            # 阶段1：种植
            for direction in PATH: #2000
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                move(PATH[(get_pos_x() - region_x, get_pos_y() - region_y)])
            # 阶段2：扫描未成熟南瓜
            unverified = region_data["unverified_left"]
            for direction in PATH:
                current_x = get_pos_x()
                current_y = get_pos_y()
                if not can_harvest():
                    plant(Entities.Pumpkin) #500
                    unverified.append((current_x, current_y))
                    if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD: 
                        use_item(Items.Water) #164
                move(PATH[(current_x - region_x, current_y - region_y)])
            
            # 阶段3：验证和补种
            while unverified: #600
                target_x, target_y = unverified[0]
                unverified.pop(0)
                short_goto(target_x, target_y)
                entity = get_entity_type()
                if entity == Entities.Pumpkin: #500
                    if not can_harvest(): #166
                        if get_water() < WATER_THRESHOLD: #79
                            use_item(Items.Water)
                        while get_entity_type() == Entities.Pumpkin and not can_harvest():
                            use_item(Items.Fertilizer)
                        if not can_harvest(): #36
                            plant(Entities.Pumpkin)
                            if get_water() < WATER_THRESHOLD: #14
                                use_item(Items.Water)
                            use_item(Items.Fertilizer)
                            unverified.append((get_pos_x(), get_pos_y()))
                elif entity == Entities.Dead_Pumpkin: #100
                    plant(Entities.Pumpkin)
                    if get_water() < WATER_THRESHOLD: #42
                        use_item(Items.Water)
                    use_item(Items.Fertilizer)
                    unverified.append((get_pos_x(), get_pos_y()))
            
            # 同步收获 112
            while not region_data["ready"]:
                help(region_data, "unverified_left")
            while region_data["help_flag"]:
                pass
            harvest()
            region_data["ready"] = False
            pumpkin_count = num_items(Items.Pumpkin)
            if pumpkin_count >= 200000000:
                quick_print("[worker_left]", region_x, region_y, "Target reached stopping all",get_time())
                clear()
                quick_print("[worker_left]", region_x, region_y, "Cleared",get_time())
                return
    
    return worker

def create_worker_right(region_x, region_y):

    def worker():
        shared = wait_for(memory_source)

        region_data = shared[(region_x, region_y)]

        start_x = region_x + 3
        goto(start_x, region_y)
        while True:
            # 等待左半边完成
            while region_data["ready"]:
                help(region_data, "unverified_left")
            x = get_pos_x()
            y = get_pos_y()
            if (x < start_x):
                short_goto(start_x, y)
            # 阶段1：种植
            for direction in PATH:
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                move(PATH[(get_pos_x() - start_x, get_pos_y() - region_y)])
            # 阶段2：扫描未成熟南瓜
            unverified = region_data["unverified_right"]
            for direction in PATH:
                current_x = get_pos_x()
                current_y = get_pos_y()
                if not can_harvest():
                    plant(Entities.Pumpkin)
                    unverified.append((current_x, current_y))
                    if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                        use_item(Items.Water)
                move(PATH[(current_x - start_x, current_y - region_y)])
            # 阶段3：验证和补种
            while unverified:
                target_x, target_y = unverified[0]
                unverified.remove((target_x, target_y))
                short_goto(target_x, target_y)
                
                entity = get_entity_type()
                if entity == Entities.Pumpkin:
                    if not can_harvest():
                        if get_water() < WATER_THRESHOLD:
                            use_item(Items.Water)
                        while get_entity_type() == Entities.Pumpkin and not can_harvest():
                            use_item(Items.Fertilizer)
                        if not can_harvest():
                            plant(Entities.Pumpkin)
                            if get_water() < WATER_THRESHOLD:
                                use_item(Items.Water)
                            use_item(Items.Fertilizer)
                            unverified.append((get_pos_x(), get_pos_y()))
                elif entity == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    if get_water() < WATER_THRESHOLD:
                        use_item(Items.Water)
                    use_item(Items.Fertilizer)
                    unverified.append((get_pos_x(), get_pos_y()))
            
            # 同步收获
            region_data["ready"] = True
    
    return worker

def do_work_main():
# 主无人机执行第一个区域的左半边工作
    shared = wait_for(memory_source)
    region_x = 0
    region_y = 0
    quick_print("[main]", region_x, region_y, "Initialized")

    region_data = shared[(region_x, region_y)]

    while True:
        # 检查南瓜数量
        current_pos_x = get_pos_x()
        if (current_pos_x >= region_x + 3):
            short_goto(region_x + 2, get_pos_y())
        # 等待右半边完成
        while region_data["ready"]:
            pass

        # 阶段1：种植
        for direction in PATH:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(PATH[(get_pos_x() - region_x, get_pos_y() - region_y)])
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_left"]
        for direction in PATH:
            current_x = get_pos_x()
            current_y = get_pos_y()
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((current_x, current_y))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(PATH[(current_x - region_x, current_y - region_y)])

        # 阶段3：验证和补种
        while unverified:
            target_x, target_y = unverified[0]
            unverified.pop(0)
            short_goto(target_x, target_y)
            entity = get_entity_type()
            if entity == Entities.Pumpkin:
                if not can_harvest():
                    if get_water() < WATER_THRESHOLD:
                        use_item(Items.Water)
                    while get_entity_type() == Entities.Pumpkin and not can_harvest():
                        use_item(Items.Fertilizer)
                    if not can_harvest():
                        plant(Entities.Pumpkin)
                        if get_water() < WATER_THRESHOLD:
                            use_item(Items.Water)
                        use_item(Items.Fertilizer)
                        unverified.append((get_pos_x(), get_pos_y()))
            elif entity == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                if get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
                use_item(Items.Fertilizer)
                unverified.append((get_pos_x(), get_pos_y()))
        
        # 同步收获
        while not region_data["ready"]:
            help(region_data, "unverified_right")
        while region_data["help_flag"]:
            pass
        harvest()
        region_data["ready"] = False
        pumpkin_count = num_items(Items.Pumpkin)
        if pumpkin_count >= 200000000:
            quick_print("[main]", region_x, region_y, "Target reached stopping all",get_time())
            clear()
            quick_print("[main]", region_x, region_y, "Cleared",get_time())
            return

# 主程序
memory_source = spawn_drone(create_shared)

# 生成区域工作无人机（除了第一个区域的左半边）
for region_idx in range(1, len(REGIONS)):
    region_x, region_y = REGIONS[region_idx]
    spawn_drone(create_worker_left(region_x, region_y))

# 第一个区域的右半边
region_x, region_y = REGIONS[0]
spawn_drone(create_worker_right(region_x, region_y))
do_work_main()