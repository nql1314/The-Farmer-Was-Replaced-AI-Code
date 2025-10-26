# 32x32南瓜挑战 - 16区域32无人机协作系统（最后一轮优化版）

from farm_utils import short_goto, goto

# 路径定义：位置与方向的映射 {(x_offset, y_offset): direction}
PATH = {
    (0, 0): East, (1, 0): East, (2, 0): North,
    (2, 1): North, (2, 2): North, (2, 3): North, (2, 4): North, (2, 5): West,
    (1, 5): West, (0, 5): South, (0, 4): East, (1, 4): South,
    (1, 3): West, (0, 3): South, (0, 2): East, (1, 2): South,
    (1, 1): West, (0, 1): South
}

WATER_THRESHOLD = 0.85
WATER_COUNT = 10
FINAL_ROUND_THRESHOLD = 198400000  # 达到时进入最后一轮模式
TARGET = 200000000

def create_shared():
    return {
        # 区域状态
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
        (0, 0):{'ready':False,'unverified_left':[],"unverified_right":[],"help_flag":False},
        "left_active_drones":  [(0,0),(0,7),(0,19),(0,26),(7,0),(7,7),(7,19),(7,26),(19,0),(19,7),(19,19),(19,26),(26,0),(26,7),(26,19),(26,26)],
        "right_active_drones":  [(0,0),(0,7),(0,19),(0,26),(7,0),(7,7),(7,19),(7,26),(19,0),(19,7),(19,19),(19,26),(26,0),(26,7),(26,19),(26,26)]
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

def get_next_region(shared):
    left_active_drones = shared["left_active_drones"]
    if len(left_active_drones) == 0:
       return
    if len(left_active_drones) > 1:
        region_pos = left_active_drones[random() * len(left_active_drones)//1]
        return region_pos
    return None


def final_round_helper(shared):
    left_active_drones = shared["left_active_drones"]
    right_active_drones = shared["right_active_drones"]
    while True:
        region_pos= get_next_region(shared)
        if region_pos == None:
            return
        verify_right(region_pos[0], region_pos[1])
        verify_left(region_pos[0], region_pos[1])


def verify_left(region_x, region_y):
    goto(region_x, region_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    # 验证左半区域
    left_active_drones = shared["left_active_drones"]
    for direction in PATH:
        if (region_x, region_y) not in left_active_drones:
            return
        if not can_harvest():
            plant(Entities.Pumpkin)
            loop_verify(region_data)
        move(PATH[(get_pos_x() - region_x, get_pos_y() - region_y)])

def verify_right(region_x, region_y):
    # 验证右半区域
    start_x = region_x + 3
    goto(start_x, region_y)
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    # 验证右半区域
    right_active_drones = shared["right_active_drones"]
    for direction in PATH:
        if (region_x, region_y) not in right_active_drones:
            return
        if not can_harvest():
            plant(Entities.Pumpkin)
            loop_verify(region_data)
        move(PATH[(get_pos_x() - start_x, get_pos_y() - region_y)])

def create_worker_left(region_x, region_y, start_x_L, start_x_R):
    goto(start_x_L, region_y)
    def worker():
        create_worker_right(region_x, region_y, start_x_R)
    spawn_drone(worker)
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
        
        # 阶段3：验证和补种（正常流程，不受最后一轮影响）
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
            quick_print("[worker_left]", region_x, region_y, "Target reached after harvest")
            clear()
            return
        
        # 达到临近阈值时，转为帮手模式
        if pumpkin_count >= FINAL_ROUND_THRESHOLD:
            shared["left_active_drones"].remove((region_x, region_y))
            shared["right_active_drones"].remove((region_x, region_y))
            final_round_helper(shared)
            return

def create_worker_right(region_x, region_y, start_x):
    shared = wait_for(memory_source)
    region_data = shared[(region_x, region_y)]
    region_x_R = region_x + 3
    goto(start_x, region_y)
    
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
        for direction in PATH:
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(PATH[(get_pos_x() - region_x_R, get_pos_y() - region_y)])
        
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
            move(PATH[(current_x - region_x_R, current_y - region_y)])
        
        # 阶段3：验证和补种（正常流程，不受最后一轮影响）
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
        
        # 同步收获（先设置ready标志，让左边开始收获）
        region_data["ready"] = True
        pumpkin_count = num_items(Items.Pumpkin)
        # 达到临近阈值时，帮助另一个区域
        if pumpkin_count >= FINAL_ROUND_THRESHOLD - 100000:
            final_round_helper(shared)
            return

# 主程序
memory_source = spawn_drone(create_shared)
def worker1():
    create_worker_left(0, 7, 0, 3)
spawn_drone(worker1)
def worker2():
    create_worker_left(0, 19, 0, 3)
spawn_drone(worker2)
def worker3():
    create_worker_left(0, 26, 0, 3)
spawn_drone(worker3)
def worker4():
    create_worker_left(7, 0, 7, 10)
spawn_drone(worker4)
def worker5():
    create_worker_left(7, 7, 7, 10)
spawn_drone(worker5)
def worker6():
    create_worker_left(7, 19, 7, 10)
spawn_drone(worker6)
def worker7():
    create_worker_left(7, 26, 7, 10)
spawn_drone(worker7)
def worker8():
    create_worker_left(19, 0, 21, 24)
spawn_drone(worker8)
def worker9():
    create_worker_left(19, 7, 21, 24)
spawn_drone(worker9)
def worker10():
    create_worker_left(19, 19, 21, 24)
spawn_drone(worker10)
def worker11():
    create_worker_left(19, 26, 21, 24)
spawn_drone(worker11)
def worker12():
    create_worker_left(26, 0, 28, 31)
spawn_drone(worker12)
def worker13():
    create_worker_left(26, 7, 28, 31)
spawn_drone(worker13)
def worker14():
    create_worker_left(26, 19, 28, 31)
spawn_drone(worker14)
def worker15():
    create_worker_left(26, 26, 28, 31)
spawn_drone(worker15)
create_worker_left(0, 0, 0, 3)
while True:
    if num_items(Items.Pumpkin) >= TARGET:
        break
clear()
