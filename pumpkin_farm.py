# The Farmer Was Replaced - 南瓜专业种植脚本（三遍优化版）
# 策略：种植6x6巨型南瓜以获得最大乘数 (6*6*6 = 216个南瓜)
# 优化：第一遍种植，第二遍补种枯萎，第三遍验证补种，最多3次遍历

# 配置参数
CONFIG = {
    'pumpkin_threshold': 200000,
    'carrot_reserve': 50,
    'carrot_target': 1000,
    'field_size': 6
}

world_size = get_world_size()

# 生成蛇形路径坐标列表
def generate_snake_path(size):
    path = []
    for y in range(size):
        if y % 2 == 0:
            for x in range(size):
                path.append((x, y))
        else:
            for x in range(size - 1, -1, -1):
                path.append((x, y))
    return path

# 预计算路径
PUMPKIN_PATH = generate_snake_path(CONFIG['field_size'])
FULL_FARM_PATH = generate_snake_path(world_size)

# 移动到指定位置
def goto(target_x, target_y):
    while get_pos_x() < target_x:
        move(East)
    while get_pos_x() > target_x:
        move(West)
    while get_pos_y() < target_y:
        move(North)
    while get_pos_y() > target_y:
        move(South)

# 移动到起点
def goto_origin():
    while get_pos_x() > 0:
        move(West)
    while get_pos_y() > 0:
        move(South)

# 补种胡萝卜到目标数量
def refill_carrots():
    quick_print("补充胡萝卜到" + str(CONFIG['carrot_target']))
    
    while num_items(Items.Carrot) < CONFIG['carrot_target']:
        for i in range(len(FULL_FARM_PATH)):
            x, y = FULL_FARM_PATH[i]
            
            if can_harvest():
                harvest()
            
            if get_ground_type() != Grounds.Soil:
                till()
            
            plant(Entities.Carrot)
            
            if get_water() < 0.5 and num_items(Items.Water) > 0:
                use_item(Items.Water)
            
            if i < len(FULL_FARM_PATH) - 1:
                next_x, next_y = FULL_FARM_PATH[i + 1]
                goto(next_x, next_y)
        
        do_a_flip()
    
    quick_print("胡萝卜：" + str(num_items(Items.Carrot)))

# 第一遍：初始种植所有南瓜
def first_pass_plant_all():
    quick_print("第1遍：种植所有南瓜")
    goto_origin()
    
    planted = 0
    for i in range(len(PUMPKIN_PATH)):
        x, y = PUMPKIN_PATH[i]
        
        # 检查胡萝卜
        if num_items(Items.Carrot) < CONFIG['carrot_reserve']:
            quick_print("胡萝卜不足")
            return False
        
        # 收割现有植物
        if can_harvest():
            harvest()
        
        # 确保土壤
        if get_ground_type() != Grounds.Soil:
            till()
        
        # 种植南瓜
        plant(Entities.Pumpkin)
        planted = planted + 1
        
        if i < len(PUMPKIN_PATH) - 1:
            next_x, next_y = PUMPKIN_PATH[i + 1]
            goto(next_x, next_y)
    
    quick_print("已种植：" + str(planted) + " 个")
    return True

# 第二遍：检查并补种枯萎南瓜，记录补种位置
def second_pass_replant_dead():
    quick_print("第2遍：检查并补种枯萎")
    goto_origin()
    
    replanted_positions = []  # 记录补种的位置
    dead_count = 0
    
    for i in range(len(PUMPKIN_PATH)):
        x, y = PUMPKIN_PATH[i]
        entity = get_entity_type()
        
        if entity == Entities.Dead_Pumpkin:
            dead_count = dead_count + 1
            
            # 检查胡萝卜
            if num_items(Items.Carrot) < CONFIG['carrot_reserve']:
                quick_print("胡萝卜不足")
                return (False, [])
            
            # 补种
            plant(Entities.Pumpkin)
            replanted_positions.append((x, y))
        
        if i < len(PUMPKIN_PATH) - 1:
            next_x, next_y = PUMPKIN_PATH[i + 1]
            goto(next_x, next_y)
    
    if dead_count > 0:
        quick_print("发现枯萎：" + str(dead_count) + " 个，已补种")
    else:
        quick_print("无枯萎南瓜")
    
    return (True, replanted_positions)

# 第三遍：验证补种位置，如果还是枯萎继续补种（异步批量优化）
def third_pass_verify_replanted(replanted_positions):
    if len(replanted_positions) == 0:
        return True
    
    quick_print("第3遍：验证补种的" + str(len(replanted_positions)) + "个位置")
    
    # 需要持续监控的位置列表
    unconfirmed = []
    for pos in replanted_positions:
        unconfirmed.append((pos[0], pos[1], 0))  # (x, y, good_count)
    
    max_rounds = 20
    round_count = 0
    
    while len(unconfirmed) > 0 and round_count < max_rounds:
        round_count = round_count + 1
        quick_print("验证轮次" + str(round_count) + "，剩余" + str(len(unconfirmed)) + "个位置")
        
        # 等待生长
        do_a_flip()
        
        # 批量检查所有未确认的位置
        next_unconfirmed = []
        replant_list = []
        
        for item in unconfirmed:
            x, y, good_count = item
            goto(x, y)
            entity = get_entity_type()
            
            if entity == Entities.Dead_Pumpkin:
                # 发现枯萎，标记需要补种，good_count重置
                replant_list.append((x, y))
                quick_print("(" + str(x) + "," + str(y) + ")枯萎")
            elif entity == Entities.Pumpkin:
                # 正常南瓜，增加good_count
                new_good_count = good_count + 1
                if new_good_count >= 4:
                    # 连续4次都是好的，确认成功
                    quick_print("(" + str(x) + "," + str(y) + ")确认成功")
                else:
                    # 继续监控
                    next_unconfirmed.append((x, y, new_good_count))
            else:
                # 异常状态（可能还在生长），继续监控
                next_unconfirmed.append((x, y, good_count))
        
        # 批量补种枯萎的南瓜
        if len(replant_list) > 0:
            quick_print("补种" + str(len(replant_list)) + "个枯萎南瓜")
            for pos in replant_list:
                x, y = pos
                goto(x, y)
                
                if num_items(Items.Carrot) < CONFIG['carrot_reserve']:
                    quick_print("胡萝卜不足")
                    return False
                
                plant(Entities.Pumpkin)
                # 补种后重置good_count，加入监控列表
                next_unconfirmed.append((x, y, 0))
        
        unconfirmed = next_unconfirmed
    
    # 最终检查
    if len(unconfirmed) > 0:
        quick_print("警告：" + str(len(unconfirmed)) + "个位置未确认")
        return False
    
    quick_print("验证完成")
    return True

# 收获南瓜田
def harvest_pumpkin_field():
    goto_origin()
    
    if can_harvest():
        before = num_items(Items.Pumpkin)
        harvest()
        after = num_items(Items.Pumpkin)
        gained = after - before
        quick_print("收获 +" + str(gained) + " 总计:" + str(after))
        return True
    return False

# 南瓜种植主循环
def pumpkin_farming_cycle():
    pumpkin_count = num_items(Items.Pumpkin)
    
    quick_print("南瓜:" + str(pumpkin_count) + " 胡萝卜:" + str(num_items(Items.Carrot)))
    
    # 检查是否需要种植
    if pumpkin_count >= CONFIG['pumpkin_threshold']:
        quick_print("南瓜充足")
        do_a_flip()
        return
    
    quick_print("=== 开始种植南瓜 ===")
    start_time = get_time()
    
    # 第一遍：种植所有
    if not first_pass_plant_all():
        refill_carrots()
        return
    
    # 等待生长
    quick_print("等待生长...")
    do_a_flip()
    
    # 第二遍：补种枯萎
    has_carrots, replanted_pos = second_pass_replant_dead()
    if not has_carrots:
        refill_carrots()
        return
    
    # 如果有补种，等待并验证
    if len(replanted_pos) > 0:
        # 第三遍：验证补种
        if not third_pass_verify_replanted(replanted_pos):
            refill_carrots()
            return
    
    # 持续等待直到全部成熟
    quick_print("等待全部成熟...")
    cycles = 0
    while True:
        cycles = cycles + 1
        elapsed = get_time() - start_time
        quick_print("全部成熟！用时:" + str(elapsed) + "s")
        harvest_pumpkin_field()
        break

# 主程序
clear()
quick_print("=== 南瓜农场 ===")
quick_print("目标:" + str(CONFIG['pumpkin_threshold']))

while True:
    pumpkin_farming_cycle()
