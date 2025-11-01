from farm_utils import goto

WATER_THRESHOLD = 0.9
WATER_COUNT = 10
TARGET = 10000000

clear()
while True:
    # 阶段1：种植
    for i in range(8):
        for j in range(8):
            move(East)
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
        move(North)
    
    # 阶段2：扫描未成熟南瓜
    unverified = []
    for i in range(8):
        for j in range(8):
            if not can_harvest():
                plant(Entities.Pumpkin)
                unverified.append((i, j))
                if get_water() < WATER_THRESHOLD:
                    use_item(Items.Water)
            move(East)
        move(North)

    while len(unverified) > 0:
        target_x, target_y = unverified.pop(0)
        goto(target_x, target_y)
        if not can_harvest():
            plant(Entities.Pumpkin)
            unverified.append((target_x, target_y))
            if get_water() < WATER_THRESHOLD:
                use_item(Items.Water)
    harvest()
    if num_items(Items.Pumpkin) >= TARGET:
        quick_print("Target reached")
        break