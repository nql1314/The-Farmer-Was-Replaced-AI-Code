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

WATER_THRESHOLD = 0.9
WATER_COUNT = 10
CIRCLE_COUNT = 1000
SLOW_THRESHOLD = 25000.0
# 0.9 50 500 38338
# 0.9 30 500 39144
# 0.9 20 500 38425
# 0.9 15 500 38964
# 0.9 5 500 39037
# 0.9 0 500 39116
# 0.98 10 5000 38830
# 0.95 10 5000 39065
# 0.9 10 5000 39164
# 0.85 10 5000 38819
# 0.8 10 5000 38484
# 0.75 10 500 38400
# 0.5 10 500 34700


def create_shared():
    return {'stop':False,'0,7':{'ready':False},'0,19':{'ready':False},'0,26':{'ready':False},
    '7,0':{'ready':False},'7,7':{'ready':False},'7,19':{'ready':False},'7,26':{'ready':False},
    '19,0':{'ready':False},'19,7':{'ready':False},'19,19':{'ready':False},'19,26':{'ready':False},
    '26,0':{'ready':False},'26,7':{'ready':False},'26,19':{'ready':False},'26,26':{'ready':False},
    '0,0':{'ready':False}}



def create_worker_right(region_x, region_y):
    def worker():
        shared = wait_for(memory_source)
        region_key = str(region_x) + "," + str(region_y)
        

        region_data = shared[region_key]

        start_x = region_x + 3
        goto_pos(start_x, region_y)

        while True:
            # 检查停止信号
            if shared["stop"]:
                return
            # 等待左半边完成
            while region_data["ready"]:
             if shared["stop"]:
                return
             pass
            # 阶段1：种植
            for direction in PATH:
                if shared["stop"]:
                    return
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                move(PATH[(get_pos_x() - start_x, get_pos_y() - region_y)])
            # 阶段2：扫描未成熟南瓜
            unverified = []
            for direction in PATH:
                if shared["stop"]:
                    return
                current_x = get_pos_x()
                current_y = get_pos_y()
                if not can_harvest():
                    plant(Entities.Pumpkin)
                    unverified.append((current_x, current_y))
                    if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                        use_item(Items.Water)
                move(PATH[(current_x - start_x, current_y - region_y)])
            # 阶段3：验证和补种
            quick_print("unverified count: " + str(len(unverified)))
            while unverified:
                if shared["stop"]:
                    return
                target_x, target_y = unverified[0]
                unverified.remove((target_x, target_y))
                short_goto(target_x, target_y)
                
                entity = get_entity_type()
                if entity == Entities.Pumpkin:
                    if can_harvest():
                        pass
                    else:
                        if get_water() < WATER_THRESHOLD:
                            use_item(Items.Water)
                        while get_entity_type() == Entities.Pumpkin and not can_harvest():
                            if shared["stop"]:
                                return
                            use_item(Items.Fertilizer)
                        if get_entity_type() == Entities.Dead_Pumpkin:
                            plant(Entities.Pumpkin)
                            if get_water() < WATER_THRESHOLD:
                                use_item(Items.Water)
                            unverified.append((get_pos_x(), get_pos_y()))
                elif entity == Entities.Dead_Pumpkin:
                    plant(Entities.Pumpkin)
                    if get_water() < WATER_THRESHOLD:
                        use_item(Items.Water)
                    unverified.append((get_pos_x(), get_pos_y()))
            
            # 同步收获
            if shared["stop"]:
                return
            region_data["ready"] = True
    
    return worker

def do_work_main():
    beginTime = get_time()
# 主无人机执行第一个区域的左半边工作
    shared = wait_for(memory_source)
    region_key = "0,0"

    region_data = shared[region_key]
    circle = 0
    slow_count = 0

    while True:
        start_time = get_time()
        # 检查南瓜数量并设置停止信号
        if shared["stop"]:
            return
        
        # 等待右半边完成
        while region_data["ready"]:
            if shared["stop"]:
                return
            pass

        # 阶段1：种植
        for direction in PATH:
            if shared["stop"]:
                return
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(PATH[(get_pos_x() - region_x, get_pos_y() - region_y)])
        
        # 阶段2：扫描未成熟南瓜
        unverified = []
        for direction in PATH:
            if shared["stop"]:
                return
            current_x = get_pos_x()
            current_y = get_pos_y()
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((current_x, current_y))
                if num_items(Items.Water) > WATER_COUNT and get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(PATH[(current_x - region_x, current_y - region_y)])
        quick_print("unverified count: " + str(len(unverified)))
        # 阶段3：验证和补种
        while unverified:
            if shared["stop"]:
                return
            target_x, target_y = unverified[0]
            unverified.pop(0)
            short_goto(target_x, target_y)
            
            entity = get_entity_type()
            if entity == Entities.Pumpkin:
                if can_harvest():
                    pass
                else:
                    if get_water() < WATER_THRESHOLD:
                        use_item(Items.Water)
                    while get_entity_type() == Entities.Pumpkin and not can_harvest():
                        if shared["stop"]:
                            return
                        use_item(Items.Fertilizer)
                    if get_entity_type() == Entities.Dead_Pumpkin:
                        plant(Entities.Pumpkin)
                        if get_water() < WATER_THRESHOLD:
                            use_item(Items.Water)
                        unverified.append((get_pos_x(), get_pos_y()))
            elif entity == Entities.Dead_Pumpkin:
                plant(Entities.Pumpkin)
                if get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
                unverified.append((get_pos_x(), get_pos_y()))
        
        # 同步收获
        while not region_data["ready"]:
            if shared["stop"]:
                return
        if not shared["stop"]:
            items = num_items(Items.Pumpkin)
            harvest()
            increment = num_items(Items.Pumpkin) - items
            circle += 1
            if increment/(get_time() - start_time) < SLOW_THRESHOLD:
                slow_count += 1
            quick_print("circle: " + str(circle) + " time: " + str(get_time() - start_time) + " increment: " + str(increment/(get_time() - start_time)))
    
            region_data["ready"] = False
            if circle > CIRCLE_COUNT:
                quick_print("all time: " + str(get_time() - beginTime) + " average speed: " + str(num_items(Items.Pumpkin)/(get_time() - beginTime)) + " slow count: " + str(slow_count))
                shared["stop"] = True 
                return

# 主程序
memory_source = spawn_drone(create_shared)

# 第一个区域的右半边
region_x, region_y = REGIONS[0]
spawn_drone(create_worker_right(region_x, region_y))
do_work_main()