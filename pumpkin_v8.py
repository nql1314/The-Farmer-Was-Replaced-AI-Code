# 32x32南瓜挑战 - 中间4个8x8区域 + 12个6x6区域

from farm_utils import short_goto, goto

# 6x6路径定义：位置与方向的映射 {(x_offset, y_offset): direction}

PATH_6X6 = { #521.84
    (0, 0): North, (1, 0): West, (2, 0): West,
    (2, 1): South, (2, 2): West, (2, 3): South, (2, 4): West, (2, 5): South,
    (1, 5): East, (0, 5): East, (0, 4): North, (1, 4): South,
    (1, 3): East, (0, 3): North, (0, 2): North, (1, 2): South,
    (1, 1): East, (0, 1): North
}

# 8x8路径定义：位置与方向的映射 {(x_offset, y_offset): direction}
PATH_8X8 = {
    (0, 0): East, (1, 0): East, (2, 0): East, (3, 0): North,
    (3, 1): North, (3, 2): North, (3, 3): North, (3, 4): North, (3, 5): North, (3, 6): North, (3, 7): West,
    (2, 7): West, (1, 7): West, (0, 7): South,  (0, 6): East,(1,6):East,(2,6):South,
    (2, 5): West, (1, 5): West, (0, 5): South, (0, 4): East,(1,4):East,(2,4):South, (2, 3): West, (1, 3): West,
    (0,3): South, (0, 2): East, (1, 2): East, (2, 2): South, (2,1): West, (1,1): West, (0, 1): South, (0, 0): East
}

WATER_THRESHOLD = 0.85
WATER_COUNT = 10
FINAL_ROUND_THRESHOLD = 198200000  # 达到时进入最后一轮模式
TARGET = 200000000

def create_shared():
    return {
        # 6x6区域状态（8个)
        (0, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'6x6'},
        (26, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'6x6'},
        (26, 26):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'6x6'},
        (0, 26):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'6x6'},
        (9, 9):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'6x6'},
        (17, 9):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'6x6'},
        (9, 17):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'6x6'},
        (17, 17):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'6x6'},
                # 8x8区域状态（8个）
        (8, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        (17, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        (24, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        (0, 7):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        (0, 16):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        (24, 8):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        (0, 23):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        (24, 17):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        (7, 24):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        (16, 24):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,'type':'8x8'},
        "left_active_drones_6x6":  [(0,0),(26,0),(26,26),(0,26),(9,9),(17,9),(9,17),(17,17)],
        "right_active_drones_6x6":  [(0,0),(26,0),(26,26),(0,26),(9,9),(17,9),(9,17),(17,17)],
        "left_active_drones_8x8":  [(8,0),(17,0),(24,8),(0,7),(0,16),(24,17),(7,24),(16,24)],
        "right_active_drones_8x8":  [(8,0),(17,0),(24,8),(0,7),(0,16),(24,17),(24,17),(7,24),(16,24)]
    }

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

def get_next_region_6x6(shared):
    left_active_drones = shared["left_active_drones_6x6"]
    if len(left_active_drones) == 0:
       return
    if len(left_active_drones) > 1:
        region_pos = left_active_drones[random() * len(left_active_drones)//1]
        return region_pos
    return None

def get_next_region_8x8(shared):
    left_active_drones = shared["left_active_drones_8x8"]
    if len(left_active_drones) == 0:
       return
    if len(left_active_drones) > 1:
        region_pos = left_active_drones[random() * len(left_active_drones)//1]
        return region_pos
    return None


def final_round_helper_6x6(shared):
    left_active_drones = shared["left_active_drones_6x6"]
    right_active_drones = shared["right_active_drones_6x6"]
    while True:
        region_pos= get_next_region_6x6(shared)
        if region_pos == None:
            return
        verify_right_6x6(region_pos[0], region_pos[1])
        verify_left_6x6(region_pos[0], region_pos[1])

def final_round_helper_8x8(shared):
    left_active_drones = shared["left_active_drones_8x8"]
    right_active_drones = shared["right_active_drones_8x8"]
    while True:
        region_pos= get_next_region_8x8(shared)
        if region_pos == None:
            return
        verify_right_8x8(region_pos[0], region_pos[1])
        verify_left_8x8(region_pos[0], region_pos[1])


# 6x6区域验证函数
def verify_left_6x6(region_x, region_y):
    goto(region_x, region_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    # 验证左半区域
    left_active_drones = shared["left_active_drones_6x6"]
    for direction in PATH_6X6:
        if (region_x, region_y) not in left_active_drones:
            return
        if not can_harvest():
            plant(Entities.Pumpkin)
            loop_verify(region_data)
        move(PATH_6X6[(get_pos_x() - region_x, get_pos_y() - region_y)])

def verify_right_6x6(region_x, region_y):
    # 验证右半区域
    start_x = region_x + 3
    goto(start_x, region_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    # 验证右半区域
    right_active_drones = shared["right_active_drones_6x6"]
    for direction in PATH_6X6:
        if (region_x, region_y) not in right_active_drones:
            return
        if not can_harvest():
            plant(Entities.Pumpkin)
            loop_verify(region_data)
        move(PATH_6X6[(get_pos_x() - start_x, get_pos_y() - region_y)])

# 8x8区域验证函数
def verify_left_8x8(region_x, region_y):
    goto(region_x, region_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    # 验证左半区域
    left_active_drones = shared["left_active_drones_8x8"]
    for direction in PATH_8X8:
        if (region_x, region_y) not in left_active_drones:
            return
        if not can_harvest():
            plant(Entities.Pumpkin)
            loop_verify(region_data)
        move(PATH_8X8[(get_pos_x() - region_x, get_pos_y() - region_y)])

def verify_right_8x8(region_x, region_y):
    # 验证右半区域
    start_x = region_x + 4
    goto(start_x, region_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    # 验证右半区域
    right_active_drones = shared["right_active_drones_8x8"]
    for direction in PATH_8X8:
        if (region_x, region_y) not in right_active_drones:
            return
        if not can_harvest():
            plant(Entities.Pumpkin)
            loop_verify(region_data)
        move(PATH_8X8[(get_pos_x() - start_x, get_pos_y() - region_y)])

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
            pass
        
        # 阶段1：种植
        for direction in PATH_6X6:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(PATH_6X6[(get_pos_x() - region_x, get_pos_y() - region_y)])
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_left"]
        for direction in PATH_6X6:
            current_x = get_pos_x()
            current_y = get_pos_y()
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((current_x, current_y))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(PATH_6X6[(current_x - region_x, current_y - region_y)])
            move(PATH_6X6[(current_x - region_x, current_y - region_y)])
        
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
            help(region_data, region_data["unverified_left"])
        while region_data["help_flag"]:
            pass
        harvest()
        region_data["ready"] = False
        
        pumpkin_count = num_items(Items.Pumpkin)
        if pumpkin_count >= TARGET:
            quick_print("[worker_left_6x6]", region_x, region_y, "Target reached")
            clear()
            return
        
        # 达到临近阈值时，转为帮手模式
        if pumpkin_count >= FINAL_ROUND_THRESHOLD:
            shared["left_active_drones_6x6"].remove((region_x, region_y))
            shared["right_active_drones_6x6"].remove((region_x, region_y))
            final_round_helper_6x6(shared)
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
            pass
        
        # 阶段1：种植
        for direction in PATH_8X8:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(PATH_8X8[(get_pos_x() - region_x, get_pos_y() - region_y)])
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_left"]
        for direction in PATH_8X8:
            current_x = get_pos_x()
            current_y = get_pos_y()
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((current_x, current_y))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(PATH_8X8[(current_x - region_x, current_y - region_y)])
        
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
            help(region_data, region_data["unverified_left"])
        while region_data["help_flag"]:
            pass
        harvest()
        region_data["ready"] = False
        
        pumpkin_count = num_items(Items.Pumpkin)
        if pumpkin_count >= TARGET:
            quick_print("[worker_left_8x8]", region_x, region_y, "Target reached")
            clear()
            return
        
        # 达到临近阈值时，转为帮手模式
        if pumpkin_count >= FINAL_ROUND_THRESHOLD:
            shared["left_active_drones_8x8"].remove((region_x, region_y))
            shared["right_active_drones_8x8"].remove((region_x, region_y))
            final_round_helper_8x8(shared)
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
                
        pumpkin_count = num_items(Items.Pumpkin)
        # 阶段1：种植
        for direction in PATH_6X6:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(PATH_6X6[(get_pos_x() - region_x_R, get_pos_y() - region_y)])
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_right"]
        for direction in PATH_6X6:
            current_x = get_pos_x()
            current_y = get_pos_y()
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((current_x, current_y))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(PATH_6X6[(current_x - region_x_R, current_y - region_y)])
        
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
        pumpkin_count = num_items(Items.Pumpkin)
        if pumpkin_count >= FINAL_ROUND_THRESHOLD - 100000:
            final_round_helper_6x6(shared)
            return

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
                
        pumpkin_count = num_items(Items.Pumpkin)
        # 阶段1：种植
        for direction in PATH_8X8:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(PATH_8X8[(get_pos_x() - region_x_R, get_pos_y() - region_y)])
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_right"]
        for direction in PATH_8X8:
            current_x = get_pos_x()
            current_y = get_pos_y()
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((current_x, current_y))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(PATH_8X8[(current_x - region_x_R, current_y - region_y)])
        
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
        pumpkin_count = num_items(Items.Pumpkin)
        if pumpkin_count >= FINAL_ROUND_THRESHOLD - 100000:
            final_round_helper_8x8(shared)
            return

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