# The Farmer Was Replaced - 南瓜专业种植脚本（优化版）
# 策略：种植6x6巨型南瓜以获得最大乘数 (6*6*6 = 216个南瓜)
# 优化：减少重复遍历，使用蛇形路径，合并检查和补种

# 配置参数
PUMPKIN_THRESHOLD = 2000  # 南瓜数量低于此值时优先种植南瓜
CARROT_RESERVE = 50      # 保留的胡萝卜数量（种植南瓜需要消耗胡萝卜）
PUMPKIN_FIELD_SIZE = 6   # 南瓜田大小（6x6获得最大乘数）

world_size = get_world_size()

# 优化的蛇形遍历种植函数（一次遍历完成所有操作）
def plant_and_maintain_field():
    # 一次遍历完成：种植、检查、补种
    # 返回：(需要补种, 全部成熟)
    needs_replant = False
    all_ready = True
    
    for y in range(PUMPKIN_FIELD_SIZE):
        for x in range(PUMPKIN_FIELD_SIZE):
            # 检查当前状态
            entity = get_entity_type()
            
            # 处理枯萎南瓜或空地
            if entity != Entities.Pumpkin:
                needs_replant = True
                all_ready = False
                
                # 确保是土壤
                if get_ground_type() != Grounds.Soil:
                    till()
                
                # 检查胡萝卜库存并种植
                if num_items(Items.Carrot) > CARROT_RESERVE:
                    plant(Entities.Pumpkin)
                    # 使用肥料加速（如果有）
                    if num_items(Items.Fertilizer) > 0:
                        use_item(Items.Fertilizer)
                else:
                    return (False, False)  # 胡萝卜不足
            
            # 检查未成熟的南瓜
            elif entity == Entities.Pumpkin:
                if not can_harvest():
                    all_ready = False
            
            # 蛇形移动（最后一个位置不移动）
            if not (y == PUMPKIN_FIELD_SIZE - 1 and x == PUMPKIN_FIELD_SIZE - 1):
                if x < PUMPKIN_FIELD_SIZE - 1:
                    # 向右或向左移动
                    if y % 2 == 0:
                        move(East)
                    else:
                        move(West)
                else:
                    # 移动到下一行
                    move(North)
    
    return (needs_replant, all_ready)

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
        # 一次遍历完成种植、检查、补种
        needs_replant, all_ready = plant_and_maintain_field()
        
        # 检查胡萝卜是否不足
        if needs_replant == False and all_ready == False:
            quick_print("胡萝卜不足")
            return False
        
        # 如果全部成熟，收获
        if all_ready:
            quick_print("南瓜田成熟")
            harvest_field()
            break
        
        # 等待生长
        do_a_flip()
    
    return True

# 主程序
while True:
    clear()
    success = pumpkin_farming_cycle()
    
    # 如果胡萝卜不足，等待或切换到其他脚本
    if not success:
        quick_print("需要胡萝卜，等待中...")
        do_a_flip()
