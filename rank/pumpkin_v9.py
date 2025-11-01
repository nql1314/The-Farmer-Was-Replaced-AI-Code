# 32x32南瓜挑战

from farm_utils import short_goto, goto

# 6x6路径定义：位置与方向的映射 {(x_offset, y_offset): direction}

PATH_6X6 = {
    (0, 0): [North, North, North, North, North, East, East, South, West, South, East, South, West, South, East, South, West, West],
    (0, 1): [North, North, North, North, East, East, South, West, South, East, South, West, South, East, South, West, West, North],
    (0, 2): [North, North, North, East, East, South, West, South, East, South, West, South, East, South, West, West, North, North],
    (0, 3): [North, North, East, East, South, West, South, East, South, West, South, East, South, West, West, North, North, North],
    (0, 4): [North, East, East, South, West, South, East, South, West, South, East, South, West, West, North, North, North, North],
    (0, 5): [East, East, South, West, South, East, South, West, South, East, South, West, West, North, North, North, North, North],
    (1, 5): [East, South, West, South, East, South, West, South, East, South, West, West, North, North, North, North, North, East],
    (2, 5): [South, West, South, East, South, West, South, East, South, West, West, North, North, North, North, North, East, East],
    (2, 4): [West, South, East, South, West, South, East, South, West, West, North, North, North, North, North, East, East, South],
    (1, 4): [South, East, South, West, South, East, South, West, West, North, North, North, North, North, East, East, South, West],
    (1, 3): [East, South, West, South, East, South, West, West, North, North, North, North, North, East, East, South, West, South],
    (2, 3): [South, West, South, East, South, West, West, North, North, North, North, North, East, East, South, West, South, East],
    (2, 2): [West, South, East, South, West, West, North, North, North, North, North, East, East, South, West, South, East, South],
    (1, 2): [South, East, South, West, West, North, North, North, North, North, East, East, South, West, South, East, South, West],
    (1, 1): [East, South, West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South],
    (2, 1): [South, West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East],
    (2, 0): [West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East, South],
    (1, 0): [West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East, South, West]
}

# 8x8路径定义：位置与方向的映射 {(x_offset, y_offset): direction}
PATH_8X8 = {
    (0, 0): [East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South],
    (1, 0): [East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East],
    (2, 0): [East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East],
    (3, 0): [North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East],
    (3, 1): [North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North],
    (3, 2): [North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North],
    (3, 3): [North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North],
    (3, 4): [North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North],
    (3, 5): [North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North],
    (3, 6): [North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North],
    (3, 7): [West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North],
    (2, 7): [West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West],
    (1, 7): [West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West],
    (0, 7): [South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West],
    (0, 6): [East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South],
    (1, 6): [East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East],
    (2, 6): [South, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East],
    (2, 5): [West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South],
    (1, 5): [West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West],
    (0, 5): [South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West],
    (0, 4): [East, East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South],
    (1, 4): [East, South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East],
    (2, 4): [South, West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East],
    (2, 3): [West, West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South],
    (1, 3): [West, South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West],
    (0, 3): [South, East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West],
    (0, 2): [East, East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South],
    (1, 2): [East, South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East],
    (2, 2): [South, West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East],
    (2, 1): [West, West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South],
    (1, 1): [West, South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West],
    (0, 1): [South, East, East, East, North, North, North, North, North, North, North, West, West, West, South, East, East, South, West, West, South, East, East, South, West, West, South, East, East, South, West, West]
}

WATER_THRESHOLD = 0.75
WATER_COUNT = 10
TARGET = 200000000

def create_shared():
    return {
        # 6x6区域状态（8个)
        (0, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (26, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (26, 26):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (0, 26):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (9, 9):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (17, 9):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (9, 17):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (17, 17):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
                # 8x8区域状态（8个）
        (8, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (17, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (24, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (0, 7):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (0, 16):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (24, 8):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (0, 23):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (24, 17):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (7, 24):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        (16, 24):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
    }

def plant_and_verify(region_data,unverified_key,start_x,start_y):
    while True:
        copy_unverified = []
        for target_x, target_y in region_data[unverified_key]:
                short_goto(target_x, target_y)
                if not can_harvest():
                    plant(Entities.Pumpkin)
                    if get_water() < WATER_THRESHOLD:
                        use_item(Items.Water)
                    use_item(Items.Fertilizer)
                    copy_unverified.append((get_pos_x(), get_pos_y()))
        region_data[unverified_key] = copy_unverified
        if len(copy_unverified) == 0:
            break

def loop_verify(region_data):
    while get_entity_type() == Entities.Pumpkin and not can_harvest():
        use_item(Items.Fertilizer)
    if get_entity_type() == Entities.Dead_Pumpkin:
        plant(Entities.Pumpkin)
        loop_verify(region_data)

def help(region_data, unverified):
    unverified_len = len(unverified)
    if unverified_len <= 1:
        return
    if unverified_len >= 1:
        target_x, target_y = unverified[-1]
        unverified.pop()
        region_data["help_flag"] = True
        short_goto(target_x, target_y)
        entity = get_entity_type()
        if entity == Entities.Pumpkin:
            if not can_harvest():
                loop_verify(region_data)
        elif entity == Entities.Dead_Pumpkin:
            plant(Entities.Pumpkin)
            loop_verify(region_data)
        region_data["help_flag"] = False

# 6x6区域的worker_left函数
def create_worker_left_6x6(region_x, region_y, start_x_L, start_x_R,start_y):
    def worker():
        create_worker_right_6x6(region_x, region_y, start_x_R,start_y)
    spawn_drone(worker)
    goto(start_x_L, start_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    region_x_R = region_x + 3
    region_x_L_R = region_x + 2
    
    while True:
        current_pos_x = get_pos_x()
        if current_pos_x >= region_x_R:
            short_goto(region_x_L_R, get_pos_y())
        
        # 等待右半边完成
        while region_data["ready"]:
            quick_print("[worker_left_6x6]", region_x, region_y, "Waiting for right half to finish")
            pass
        
        # 阶段1：种植
        path = PATH_6X6[(get_pos_x() - region_x, get_pos_y() - region_y)]
        for direction in path:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(direction)
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_left"]
        for direction in path:
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((get_pos_x(), get_pos_y()))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(direction)
        
        # 阶段3：验证和补种
        plant_and_verify(region_data, "unverified_left", region_x, region_y)
        
        # 同步收获
        while not region_data["ready"]:
            help(region_data, region_data["unverified_right"])
        while region_data["help_flag"]:
            pass
        harvest()
        region_data["ready"] = False
        
        pumpkin_count = num_items(Items.Pumpkin)
        if pumpkin_count >= TARGET:
            quick_print("[worker_left_6x6]", region_x, region_y, "Target reached")
            clear()
            return
        
# 8x8区域的worker_left函数
def create_worker_left_8x8(region_x, region_y, start_x_L, start_x_R,start_y):
    def worker():
        create_worker_right_8x8(region_x, region_y, start_x_R,start_y)
    spawn_drone(worker)
    goto(start_x_L, start_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    region_x_R = region_x + 4
    region_x_L_R = region_x + 3
    
    while True:
        current_pos_x = get_pos_x()
        if current_pos_x >= region_x_R:
            short_goto(region_x_L_R, get_pos_y())
        
        # 等待右半边完成
        while region_data["ready"]:
            quick_print("[worker_left_8x8]", region_x, region_y, "Waiting for right half to finish")
            pass
        
        # 阶段1：种植
        path = PATH_8X8[(get_pos_x() - region_x, get_pos_y() - region_y)]
        for direction in path:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(direction)
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_left"]
        for direction in path:
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((get_pos_x(), get_pos_y()))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(direction)
        
        # 阶段3：验证和补种
        plant_and_verify(region_data, "unverified_left", region_x, region_y)
        
        # 同步收获
        while not region_data["ready"]:
            help(region_data, region_data["unverified_right"])
        while region_data["help_flag"]:
            pass
        harvest()
        region_data["ready"] = False
        
        pumpkin_count = num_items(Items.Pumpkin)
        if pumpkin_count >= TARGET:
            quick_print("[worker_left_8x8]", region_x, region_y, "Target reached")
            clear()
            return
# 6x6区域的worker_right函数
def create_worker_right_6x6(region_x, region_y, start_x,start_y):
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    region_x_R = region_x + 3
    goto(start_x, start_y)
    
    while True:
        # 等待左半边完成
        while region_data["ready"]:
            help(region_data, region_data["unverified_left"])
        x = get_pos_x()
        y = get_pos_y()
        if x < region_x_R:
            short_goto(region_x_R, y)
                
        # 阶段1：种植
        path = PATH_6X6[(get_pos_x() - region_x_R, get_pos_y() - region_y)]
        for direction in path:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(direction)
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_right"]
        for direction in path:
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((get_pos_x(), get_pos_y()))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(direction)
        
        # 阶段3：验证和补种
        plant_and_verify(region_data, "unverified_right", region_x, region_y)
        
        # 同步收获
        region_data["ready"] = True

# 8x8区域的worker_right函数
def create_worker_right_8x8(region_x, region_y, start_x,start_y):
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    region_x_R = region_x + 4
    goto(start_x, start_y)
    
    while True:
        # 等待左半边完成
        while region_data["ready"]:
            help(region_data, region_data["unverified_left"])
        x = get_pos_x()
        y = get_pos_y()
        if x < region_x_R:
            short_goto(region_x_R, y)
                
        # 阶段1：种植
        path = PATH_8X8[(get_pos_x() - region_x_R, get_pos_y() - region_y)]
        for direction in path:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(direction)
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_right"]
        for direction in path:
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((get_pos_x(), get_pos_y()))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(direction)
        
        # 阶段3：验证和补种
        plant_and_verify(region_data, "unverified_right", region_x, region_y)
        
        # 同步收获
        region_data["ready"] = True

# 主程序
memory_source = spawn_drone(create_shared)

# 6x6区域工人（8个边缘区域）

def worker2():
    create_worker_left_6x6(26, 0,28, 31,0)
spawn_drone(worker2)
def worker3():
    create_worker_left_6x6(26, 26,28, 31,31)
spawn_drone(worker3)
def worker4():
    create_worker_left_6x6(0, 26, 0, 3,31)
spawn_drone(worker4)
def worker5():
    create_worker_left_6x6(9, 9, 9, 12,9)
spawn_drone(worker5)
def worker6():
    create_worker_left_6x6(17, 9, 19, 22,9)
spawn_drone(worker6)
def worker7():
    create_worker_left_6x6(9, 17, 11, 14,22)
spawn_drone(worker7)
def worker1():
    create_worker_left_6x6(17, 17, 19, 22,22)
spawn_drone(worker1)

# 8x8区域工人（8个区域）
def worker8():
    create_worker_left_8x8(8, 0, 8, 12,0)
spawn_drone(worker8)
def worker9():
    create_worker_left_8x8(17, 0, 20, 24,0)
spawn_drone(worker9)
def worker10():
    create_worker_left_8x8(0, 7, 0, 4,7)
spawn_drone(worker10)
def worker11():
    create_worker_left_8x8(24, 8, 28, 31,8)
spawn_drone(worker11)

def worker12():
    create_worker_left_8x8(0, 16, 0, 4,23)
spawn_drone(worker12)
def worker13():
    create_worker_left_8x8(24, 17, 27, 31,24)
spawn_drone(worker13)
def worker14():
    create_worker_left_8x8(7, 24, 10, 14,31)
spawn_drone(worker14)
def worker15():
    create_worker_left_8x8(16, 24, 19, 23,31)
spawn_drone(worker15)

create_worker_left_6x6(0, 0, 0, 3,0)
while True:
    if num_items(Items.Pumpkin) >= TARGET:
        break