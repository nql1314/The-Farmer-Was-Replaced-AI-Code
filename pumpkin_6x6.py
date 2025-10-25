# 6x6南瓜挑战 - 双无人机协作系统（精简版）

from farm_utils import short_goto

# 左半边(0,0)种植路径
LEFT_PLANT = [East,East,North,North,North,North,North,West,West,South,East,South,West,South,East,South,West]
# 左半边(0,1)扫描路径
LEFT_SCAN = [South,East,East,North,North,North,North,North,West,West,South,East,South,West,South,East,South,West]
# 右半边(5,0)种植路径
RIGHT_PLANT = [West,West,North,North,North,North,North,East,East,South,West,South,East,South,West,South,East]
# 右半边(5,1)扫描路径
RIGHT_SCAN = [South,West,West,North,North,North,North,North,East,East,South,West,South,East,South,West,South,East]

def create_shared():
    return {}

def process_half(start_x, plant_dirs, scan_dirs, is_left):
    shared = wait_for(memory_source)
    
    while True:
        # 等待右半边完成
        while shared["ready"]:
            pass
        
        # 移动到起始位置
        short_goto(start_x, 0)
        
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
            target_x, target_y = unverified[0]
            unverified.pop(0)
            short_goto(target_x, target_y)
            
            while not can_harvest():
                plant(Entities.Pumpkin)
                if get_water() < 0.8:
                    use_item(Items.Water)
                if len(unverified) == 1:
                    use_item(Items.Fertilizer)
        
        # 同步收获
        if is_left:
            while not shared["ready"]:
                pass
            do_a_flip()
            harvest()
            shared["ready"] = False
            if num_items(Items.Pumpkin) >= 200000000:
                shared["stop"] = True
                break
        else:
            shared["ready"] = True
            if num_items(Items.Pumpkin) >= 200000000:
                shared["stop"] = True
                break

def left_worker():
    process_half(0, LEFT_PLANT, LEFT_SCAN, True)

def right_worker():
    process_half(5, RIGHT_PLANT, RIGHT_SCAN, False)

# 主程序
clear()
memory_source = spawn_drone(create_shared)
memory = wait_for(memory_source)
memory["ready"] = False

spawn_drone(left_worker)
spawn_drone(right_worker)

while True:
    do_a_flip()
