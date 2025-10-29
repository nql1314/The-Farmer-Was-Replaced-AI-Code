# 32x32南瓜挑战 - 12个7x7区域(4列x7行 + 3列x7行) + 4个8x8区域

from farm_utils import short_goto, goto

# 4列x7行左半区路径定义
PATH_4X7 = {
    (0,0):North,(0,1):North,(0,2):North,(0,3):North,(0,4):North,(0,5):North,(0,6):East,
    (1,6):East,(2,6):East,(3,6):South,(3,5):South,(3,4):South,(3,3):South,(3,2):South,
    (3,1):South,(3,0):West,(2,0):North,(1,0):North,(1,1):South,(2,1):North,(2,2):North,
    (1,2):South,(1,3):South,(1,4):South,(1,5):South,(2,5):West,(2,4):North,(1,0):West,
    (2,3):North
}

# 3列x7行右半区路径定义
PATH_3X7 = {
    (0,0):East,(1,0):East,(2,0):North,(2,1):North,(2,2):North,(2,3):North,(2,4):North,(2,5):North,
    (2,6):West,(1,6):West,(0,6):South,(0,5):East,(1,5):South,(1,4):West,(0,4):South,(0,3):East,
    (1,3):South,(1,2):West,(0,2):South,(0,1):East,(1,1):South
}

def move_3_7_R(region_xx, region_yy):
    if ((region_xx,region_yy) == (1,1)):
        move(South)
        move(West)
    else:
        move(PATH_3X7[(region_xx, region_yy)])

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
FINAL_ROUND_THRESHOLD = 198500000  # 达到时进入最后一轮模式
TARGET = 20000000

def create_shared():
    return {
        # 7x7区域状态（12个）- 左下角坐标
        (0, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (8, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (16, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (0, 8):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (0, 16):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (25, 9):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (17, 25):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (25, 25):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (17, 17):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (25, 17):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (9, 25):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (8, 8):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        # 8x8区域状态（4个）
        (8, 16):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (16, 8):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (24, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        (0,24):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False,},
        "left_active_drones_7x7":  [(0,0),(8,0),(16,0),(0,8),(0,16),(25,9),(17,25),(25,25),(17,17),(25,17),(9,25),(8,8)],
        "right_active_drones_7x7":  [(0,0),(8,0),(16,0),(0,8),(0,16),(25,9),(17,25),(25,25),(17,17),(25,17),(9,25),(8,8)],
        "left_active_drones_8x8":  [(8,16),(16,8),(24,0),(0,24)],
        "right_active_drones_8x8":  [(8,16),(16,8),(24,0),(0,24)]
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

def get_next_region_7x7(shared):
    left_active_drones = shared["left_active_drones_7x7"]
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


def final_round_helper_7x7(shared):
    left_active_drones = shared["left_active_drones_7x7"]
    right_active_drones = shared["right_active_drones_7x7"]
    while True:
        region_pos= get_next_region_7x7(shared)
        if region_pos == None:
            return
        verify_right_7x7(region_pos[0], region_pos[1])
        verify_left_7x7(region_pos[0], region_pos[1])

def final_round_helper_8x8(shared):
    left_active_drones = shared["left_active_drones_8x8"]
    right_active_drones = shared["right_active_drones_8x8"]
    while True:
        region_pos= get_next_region_8x8(shared)
        if region_pos == None:
            return
        verify_right_8x8(region_pos[0], region_pos[1])
        verify_left_8x8(region_pos[0], region_pos[1])


# 7x7区域验证函数（左半区4列x7行）
def verify_left_7x7(region_x, region_y):
    goto(region_x, region_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    # 验证左半区域4列x7行
    left_active_drones = shared["left_active_drones_7x7"]
    for direction in PATH_4X7:
        if (region_x, region_y) not in left_active_drones:
            return
        if not can_harvest():
            plant(Entities.Pumpkin)
            loop_verify(region_data)
        move(PATH_4X7[(get_pos_x() - region_x, get_pos_y() - region_y)])

def verify_right_7x7(region_x, region_y):
    # 验证右半区域3列x7行
    start_x = region_x + 4
    goto(start_x, region_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    # 验证右半区域
    right_active_drones = shared["right_active_drones_7x7"]
    for direction in PATH_3X7:
        if (region_x, region_y) not in right_active_drones:
            return
        if not can_harvest():
            plant(Entities.Pumpkin)
            loop_verify(region_data)
        region_xx = get_pos_x()-start_x
        region_yy = get_pos_y() - region_y
        move_3_7_R(region_xx, region_yy)

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

# 7x7区域的worker_left函数（左半区4列x7行）
def create_worker_left_7x7(region_x, region_y, start_x_L, start_x_R,start_y):
    goto(start_x_L, region_y)
    def worker():
        create_worker_right_7x7(region_x, region_y, start_x_R,start_y)
    spawn_drone(worker)
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
        
        # 阶段1：种植（左半区4列x7行）
        for direction in PATH_4X7:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(PATH_4X7[(get_pos_x() - region_x, get_pos_y() - region_y)])
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_left"]
        for direction in PATH_4X7:
            current_x = get_pos_x()
            current_y = get_pos_y()
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((current_x, current_y))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(PATH_4X7[(current_x - region_x, current_y - region_y)])
        
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
            quick_print("[worker_left_7x7]", region_x, region_y, "Target reached")
            clear()
            return
        
        # 达到临近阈值时，转为帮手模式
        if pumpkin_count >= FINAL_ROUND_THRESHOLD:
            shared["left_active_drones_7x7"].remove((region_x, region_y))
            shared["right_active_drones_7x7"].remove((region_x, region_y))
            final_round_helper_7x7(shared)
            return

# 8x8区域的worker_left函数
def create_worker_left_8x8(region_x, region_y, start_x_L, start_x_R, start_y):
    goto(start_x_L, start_y)
    def worker():
        create_worker_right_8x8(region_x, region_y, start_x_R, start_y)
    spawn_drone(worker)
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



# 7x7区域的worker_right函数（右半区3列x7行）
def create_worker_right_7x7(region_x, region_y, start_x,start_y):
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
        # 阶段1：种植（右半区3列x7行）
        for direction in PATH_3X7:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move_3_7_R(get_pos_x() - region_x_R, get_pos_y() - region_y)
        
        # 阶段2：扫描未成熟南瓜
        unverified = region_data["unverified_right"]
        for direction in PATH_3X7:
            current_x = get_pos_x()
            current_y = get_pos_y()
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((current_x, current_y))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move_3_7_R(current_x - region_x_R, current_y - region_y)
        
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
            final_round_helper_7x7(shared)
            return

# 8x8区域的worker_right函数
def create_worker_right_8x8(region_x, region_y, start_x, start_y):
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

# 第一个7x7农场由主无人机处理
create_worker_left_7x7(0, 0, 0, 4, 0)
while True:
    if num_items(Items.Pumpkin) >= TARGET:
        break