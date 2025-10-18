# The Farmer Was Replaced - 南瓜专业种植脚本（优化版）
# 策略：种植6x6巨型南瓜以获得最大乘数 (6*6*6 = 216个南瓜)
# 优化：蛇形路径，立即处理枯萎南瓜，自动补充胡萝卜

# 配置参数
PUMPKIN_THRESHOLD = 20000  # 南瓜数量低于此值时优先种植南瓜
CARROT_RESERVE = 50     # 保留的胡萝卜数量（种植南瓜需要消耗胡萝卜）
CARROT_TARGET = 1000    # 胡萝卜不足时补种到此数量
PUMPKIN_FIELD_SIZE = 6   # 南瓜田大小（6x6获得最大乘数）

world_size = get_world_size()

# 补种胡萝卜到目标数量
def refill_carrots():
    quick_print("胡萝卜不足，补种到" + str(CARROT_TARGET))
    
    # 使用蛇形遍历补种胡萝卜
    while num_items(Items.Carrot) < CARROT_TARGET:
        for y in range(world_size):
            for x in range(world_size):
                # 收割成熟的
                if can_harvest():
                    harvest()
                
                # 确保是土壤
                if get_ground_type() != Grounds.Soil:
                    till()
                
                # 种植胡萝卜
                plant(Entities.Carrot)
                
                # 浇水加速
                if get_water() < 0.5:
                    if num_items(Items.Water) > 0:
                        use_item(Items.Water)
                
                # 蛇形移动
                if not (y == world_size - 1 and x == world_size - 1):
                    if x < world_size - 1:
                        if y % 2 == 0:
                            move(East)
                        else:
                            move(West)
                    else:
                        move(North)
        
        # 等待生长
        quick_print("等待胡萝卜成熟...")
        do_a_flip()
    
    quick_print("胡萝卜补充完成：" + str(num_items(Items.Carrot)))

# 优化的蛇形遍历种植函数（立即处理枯萎南瓜）
def plant_and_maintain_field():
    # 一次遍历完成：种植、立即检查枯萎并补种
    # 返回：是否全部成熟
    all_ready = True
    
    for y in range(PUMPKIN_FIELD_SIZE):
        for x in range(PUMPKIN_FIELD_SIZE):
            entity = get_entity_type()
            
            # 如果不是南瓜（空地或枯萎南瓜），立即种植
            if entity != Entities.Pumpkin:
                all_ready = False
                
                # 检查胡萝卜是否充足
                if num_items(Items.Carrot) < CARROT_RESERVE:
                    return False  # 需要补充胡萝卜
                
                # 确保是土壤
                if get_ground_type() != Grounds.Soil:
                    till()
                
                # 种植南瓜
                plant(Entities.Pumpkin)
                
                # 立即检查是否种出了枯萎南瓜
                # 如果是枯萎南瓜，立即重新种植
                while get_entity_type() == Entities.Dead_Pumpkin:
                    quick_print("发现枯萎南瓜(" + str(x) + "," + str(y) + ")，重新种植")
                    
                    # 检查胡萝卜
                    if num_items(Items.Carrot) < CARROT_RESERVE:
                        return False
                    
                    plant(Entities.Pumpkin)
            
            # 检查南瓜是否成熟
            elif not can_harvest():
                all_ready = False
            
            # 蛇形移动（最后一个位置不移动）
            if not (y == PUMPKIN_FIELD_SIZE - 1 and x == PUMPKIN_FIELD_SIZE - 1):
                if x < PUMPKIN_FIELD_SIZE - 1:
                    if y % 2 == 0:
                        move(East)
                    else:
                        move(West)
                else:
                    move(North)
    
    return all_ready

# 收获南瓜田
def harvest_field():
    # 快速移动到任意成熟南瓜位置并收获
    # 移动到(0,0)
    while get_pos_x() > 0:
        move(West)
    while get_pos_y() > 0:
        move(South)
    
    # 收获（任意一个成熟南瓜即可触发整片收获）
    if can_harvest():
        harvest()
        quick_print("收获南瓜！数量：" + str(num_items(Items.Pumpkin)))
        return True
    return False

# 南瓜种植主循环
def pumpkin_farming_cycle():
    pumpkin_count = num_items(Items.Pumpkin)
    quick_print("南瓜：" + str(pumpkin_count))
    
    # 如果南瓜数量充足，跳过
    if pumpkin_count >= PUMPKIN_THRESHOLD:
        quick_print("南瓜充足")
        return True
    
    quick_print("开始种植南瓜")
    
    # 移动到南瓜田起点(0,0)
    while get_pos_x() > 0:
        move(West)
    while get_pos_y() > 0:
        move(South)
    
    # 持续维护南瓜田直到收获
    while True:
        # 一次遍历完成种植、立即处理枯萎、检查成熟
        result = plant_and_maintain_field()
        
        # 如果返回False，说明胡萝卜不足
        if result == False:
            quick_print("胡萝卜不足")
            # 补充胡萝卜到目标数量
            refill_carrots()
            # 回到南瓜田起点
            while get_pos_x() > 0:
                move(West)
            while get_pos_y() > 0:
                move(South)
            continue
        
        # 如果返回True，说明全部成熟
        if result == True:
            quick_print("南瓜田成熟")
            harvest_field()
            break
        
        # 等待生长
        do_a_flip()
    
    return True

# 主程序
clear()
while True:
    pumpkin_farming_cycle()
