# The Farmer Was Replaced - 12x12南瓜农场（全场种植+ID检测优化版）
# ============================================================
# 策略：种植满12x12=144个南瓜，通过ID检测判断是否已合并成巨型南瓜
# 检测方法：对角线两端ID一致 = 同一个巨型南瓜 = 可以收获
# 
# 核心优化：
# 1. 全场种植：直接种满144格，形成12x12巨型南瓜
# 2. ID智能检测：使用measure()获取南瓜ID，快速检测对角线
# 3. 验证中检测：验证阶段持续检测，形成即跳出
# 4. 提前收获：检测到形成立即跳出验证，直接收获
# 5. 蛇形路径：全场12x12蛇形遍历，最小化移动
# 6. 批量异步验证：只监控补种位置，形成后立即结束
# 7. 原地等待：待验证<3个时原地等待，减少移动
# 8. 精准浇水：只在第一遍种植时浇水，其他阶段不浇水
# 
# ID检测逻辑：
# - 全场12x12南瓜：检查(0,0)和(11,11)的ID
# - 如果ID相同且都是Pumpkin，说明已形成12x12巨型南瓜
# - check_mega_pumpkin_formed() 只是快速检查，不等待不浇水
# - 验证阶段每次do_a_flip()后都检测ID
# - 检测到形成立即跳出，无需继续验证
# 
# 浇水策略：
# - 只在第一遍种植主循环时检查并浇水
# - 其他阶段（补种、验证、等待）不浇水，减少操作
# - 水量阈值：0.75（可在CONFIG中调整）
# 
# 性能预估（基于144个格子）：
# - 第1遍种植：~28,800 ticks (144×200) + 浇水
# - 第2遍检查补种：~144-1000 ticks (无浇水)
# - 第3遍验证：< 1,000 ticks (形成后立即结束，原地等待优化)
# - 直接收获：~200 ticks
# - 总计：约30,000-31,000 ticks/周期（极致优化）
# ============================================================

# 导入通用工具库
from farm_utils import goto_origin, goto, generate_snake_path, optimize_path_circle, check_and_water, check_mega_pumpkin_formed, harvest_mega_pumpkin

# 配置参数
CONFIG = {
    'pumpkin_threshold': 20000000,
    'carrot_reserve': 100,
    'carrot_target': 2000,
    'world_size': 12,
    'mega_pumpkin_size': 12,  # 12x12巨型南瓜
    'water_threshold': 0.75   # 水量低于此值时浇水
}

# 预计算路径
FULL_PATH = generate_snake_path(CONFIG['world_size'])

# 本地别名（为了与原代码兼容）
def goto(target_x, target_y):
    goto(target_x, target_y)

# 补充胡萝卜到目标数量
def refill_carrots():
    quick_print("补充胡萝卜到" + str(CONFIG['carrot_target']))
    
    while num_items(Items.Carrot) < CONFIG['carrot_target']:
        for i in range(len(FULL_PATH)):
            x, y = FULL_PATH[i]
            
            if can_harvest():
                harvest()
            
            if get_ground_type() != Grounds.Soil:
                till()
            
            plant(Entities.Carrot)
            
            if get_water() < 0.5 and num_items(Items.Water) > 0:
                use_item(Items.Water)
            
            if i < len(FULL_PATH) - 1:
                next_x, next_y = FULL_PATH[i + 1]
                goto(next_x, next_y)
        
        do_a_flip()
    
    quick_print("胡萝卜：" + str(num_items(Items.Carrot)))

# 检查并浇水（本地包装函数）
def check_and_water_local():
    return check_and_water(CONFIG['water_threshold'])

# 第一遍：种植全场12x12=144个南瓜
def first_pass_plant_all():
    quick_print("第1遍：种植全场12x12 (144格)")
    goto_origin()
    
    planted = 0
    watered_count = 0
    
    for i in range(len(FULL_PATH)):
        x, y = FULL_PATH[i]
        
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
        
        # 检查并浇水
        if check_and_water_local():
            watered_count = watered_count + 1
        
        if i < len(FULL_PATH) - 1:
            next_x, next_y = FULL_PATH[i + 1]
            goto(next_x, next_y)
    
    quick_print("已种植：" + str(planted) + " 个南瓜")
    if watered_count > 0:
        quick_print("浇水次数：" + str(watered_count))
    return True

# 第二遍：检查并补种枯萎南瓜，记录补种位置
def second_pass_replant_dead():
    quick_print("第2遍：检查并补种枯萎")
    goto_origin()
    
    replanted_positions = []
    dead_count = 0
    
    for i in range(len(FULL_PATH)):
        x, y = FULL_PATH[i]
        
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
        
        if i < len(FULL_PATH) - 1:
            next_x, next_y = FULL_PATH[i + 1]
            goto(next_x, next_y)
    
    if dead_count > 0:
        quick_print("发现枯萎：" + str(dead_count) + " 个，已补种")
    else:
        quick_print("无枯萎南瓜")
    
    return (True, replanted_positions)

# 检测是否已形成巨型南瓜（本地包装函数）
def check_mega_pumpkin_formed_local():
    return check_mega_pumpkin_formed(CONFIG['mega_pumpkin_size'])

# 第三遍：验证补种位置（批量异步验证+路径优化+ID提前检测）
def third_pass_verify_replanted(replanted_positions):
    if len(replanted_positions) == 0:
        # 即使没有补种位置，也检查是否已形成巨型南瓜
        quick_print("无补种位置，检查是否已形成巨型南瓜...")
        if check_mega_pumpkin_formed_local():
            quick_print("检测到12x12巨型南瓜已形成！")
            return True
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
        
        # ⭐优化：待验证位置<3个时，补种完后原地等待直到成长完成
        if len(unconfirmed) < 3:
            quick_print("剩余位置少(" + str(len(unconfirmed)) + "个)，原地处理...")
            
            # 先检查并补种枯萎的
            replant_needed = []
            for item in unconfirmed:
                x, y, good_count = item
                goto(x, y)
                entity = get_entity_type()
                
                if entity == Entities.Dead_Pumpkin:
                    quick_print("(" + str(x) + "," + str(y) + ")枯萎，补种")
                    if num_items(Items.Carrot) < CONFIG['carrot_reserve']:
                        quick_print("胡萝卜不足")
                        return False
                    plant(Entities.Pumpkin)
                    replant_needed.append((x, y))
            
            # 如果有补种，原地等待多次直到成长完成
            if len(replant_needed) > 0:
                quick_print("补种完成，原地等待成长...")
                wait_count = 0
                max_local_wait = 3
                
                while wait_count < max_local_wait:
                    do_a_flip()
                    wait_count = wait_count + 1
                    
                    # 检查补种的位置是否都成长了
                    all_grown = True
                    for pos in replant_needed:
                        x, y = pos
                        goto(x, y)
                        entity = get_entity_type()
                        if entity != Entities.Pumpkin:
                            all_grown = False
                            break
                    
                    if all_grown:
                        quick_print("补种位置已成长，等待轮次:" + str(wait_count))
                        break
                
                # 重置unconfirmed，将补种的位置加入
                new_unconfirmed = []
                for pos in replant_needed:
                    new_unconfirmed.append((pos[0], pos[1], 0))
                unconfirmed = new_unconfirmed
                continue
            
            # 没有补种，检查现有位置
            still_unconfirmed = []
            for item in unconfirmed:
                x, y, good_count = item
                goto(x, y)
                entity = get_entity_type()
                
                if entity == Entities.Pumpkin:
                    new_good_count = good_count + 1
                    if new_good_count >= 3:
                        quick_print("(" + str(x) + "," + str(y) + ")确认成功")
                    else:
                        still_unconfirmed.append((x, y, new_good_count))
                else:
                    still_unconfirmed.append((x, y, good_count))
            
            unconfirmed = still_unconfirmed
            
            # 如果没有待确认的了，等待一轮后检测巨型南瓜
            if len(unconfirmed) == 0:
                quick_print("所有位置确认完成，等待一轮后检测巨型南瓜...")
                do_a_flip()
                if check_mega_pumpkin_formed_local():
                    quick_print("检测到12x12巨型南瓜已形成！")
                    return True
            
            continue
        
        # 正常处理：待验证位置>=3个
        # 优化检查顺序：按照最近邻排序
        current_x = get_pos_x()
        current_y = get_pos_y()
        optimized_unconfirmed = optimize_path_circle(unconfirmed, current_x, current_y)
        
        # 批量检查所有未确认的位置
        next_unconfirmed = []
        replant_list = []
        confirmed_count = 0
        
        for item in optimized_unconfirmed:
            x, y, good_count = item
            goto(x, y)
            entity = get_entity_type()
            
            if entity == Entities.Dead_Pumpkin:
                # 发现枯萎，标记需要补种
                replant_list.append((x, y))
                quick_print("(" + str(x) + "," + str(y) + ")枯萎")
            elif entity == Entities.Pumpkin:
                # 正常南瓜，增加good_count
                new_good_count = good_count + 1
                
                if new_good_count >= 3:
                    # 连续3次都是好的，确认成功，从未确认列表移除
                    confirmed_count = confirmed_count + 1
                    quick_print("(" + str(x) + "," + str(y) + ")确认成功")
                    # 注意：不加入next_unconfirmed，自动从监控中移除
                else:
                    # 继续监控
                    next_unconfirmed.append((x, y, new_good_count))
            else:
                # 异常状态（可能还在生长），继续监控
                next_unconfirmed.append((x, y, good_count))
        
        # 批量补种枯萎的南瓜（使用路径优化，不浇水）
        if len(replant_list) > 0:
            quick_print("补种" + str(len(replant_list)) + "个枯萎南瓜")
            current_x = get_pos_x()
            current_y = get_pos_y()
            optimized_replant = optimize_path_circle(replant_list, current_x, current_y)
            
            for pos in optimized_replant:
                x, y = pos
                goto(x, y)
                
                if num_items(Items.Carrot) < CONFIG['carrot_reserve']:
                    quick_print("胡萝卜不足")
                    return False
                
                plant(Entities.Pumpkin)
                # 补种后重置good_count为0，重新加入监控列表
                next_unconfirmed.append((x, y, 0))
            
            # 补种完成后，等待一轮
            quick_print("补种完成，等待一轮...")
            do_a_flip()
            
            # 然后检测是否形成巨型南瓜
            if check_mega_pumpkin_formed_local():
                quick_print("检测到12x12巨型南瓜已形成！提前结束验证")
                return True
        else:
            # 没有补种，正常等待生长
            do_a_flip()
            
            # 快速检查是否已形成巨型南瓜（不等待不浇水）
            if check_mega_pumpkin_formed_local():
                quick_print("检测到12x12巨型南瓜已形成！提前结束验证")
                return True
        
        # 显示本轮统计
        if confirmed_count > 0:
            quick_print("本轮确认" + str(confirmed_count) + "个位置")
        
        unconfirmed = next_unconfirmed
    
    # 最终检查
    if len(unconfirmed) > 0:
        quick_print("警告：" + str(len(unconfirmed)) + "个位置未确认")
        # 但如果已经形成巨型南瓜，也返回True
        if check_mega_pumpkin_formed_local():
            quick_print("但检测到巨型南瓜已形成，继续收获")
            return True
        return False
    
    quick_print("验证完成，所有位置已确认")
    return True

# 直接收获12x12巨型南瓜（本地包装函数）
def harvest_mega_pumpkin_local():
    return harvest_mega_pumpkin(CONFIG['mega_pumpkin_size'])

# 南瓜种植主循环
def pumpkin_farming_cycle():
    pumpkin_count = num_items(Items.Pumpkin)
    carrot_count = num_items(Items.Carrot)
    water_level = get_water()
    water_tank_count = num_items(Items.Water)
    
    quick_print("========================================")
    quick_print("南瓜:" + str(pumpkin_count) + " / " + str(CONFIG['pumpkin_threshold']))
    quick_print("胡萝卜:" + str(carrot_count))
    quick_print("水量:" + str(water_level) + " 水桶:" + str(water_tank_count))
    
    # 检查是否需要种植
    if pumpkin_count >= CONFIG['pumpkin_threshold']:
        quick_print("南瓜充足，等待中...")
        do_a_flip()
        return
    
    quick_print("=== 开始种植12x12南瓜农场 ===")
    start_time = get_time()
    start_ticks = get_tick_count()
    
    # 第一遍：种植全场
    pass1_start = get_tick_count()
    if not first_pass_plant_all():
        refill_carrots()
        return
    pass1_ticks = get_tick_count() - pass1_start
    quick_print("第1遍耗时: " + str(pass1_ticks) + " ticks")
    
    # 等待生长
    quick_print("等待生长...")
    do_a_flip()
    
    # 第二遍：补种枯萎
    pass2_start = get_tick_count()
    has_carrots, replanted_pos = second_pass_replant_dead()
    if not has_carrots:
        refill_carrots()
        return
    pass2_ticks = get_tick_count() - pass2_start
    quick_print("第2遍耗时: " + str(pass2_ticks) + " ticks")
    
    # 第三遍：验证补种（会在验证过程中检测是否形成巨型南瓜）
    pass3_start = get_tick_count()
    if not third_pass_verify_replanted(replanted_pos):
        refill_carrots()
        return
    pass3_ticks = get_tick_count() - pass3_start
    quick_print("第3遍耗时: " + str(pass3_ticks) + " ticks")
    
    # 如果验证阶段已检测到巨型南瓜形成，直接收获
    # 否则继续等待
    if not check_mega_pumpkin_formed_local():
        quick_print("等待巨型南瓜形成...")
        wait_cycles = 0
        max_wait = 20
        
        while wait_cycles < max_wait:
            do_a_flip()
            wait_cycles = wait_cycles + 1
            quick_print("等待周期 " + str(wait_cycles))
            
            # 快速检查是否已形成（不等待不浇水）
            if check_mega_pumpkin_formed_local():
                quick_print("检测到12x12巨型南瓜已形成！")
                break
        
        if wait_cycles >= max_wait:
            quick_print("警告：等待超时，可能有问题")
    
    # 收获12x12巨型南瓜
    harvest_start = get_tick_count()
    harvest_mega_pumpkin_local()
    harvest_ticks = get_tick_count() - harvest_start
    
    elapsed_time = get_time() - start_time
    elapsed_ticks = get_tick_count() - start_ticks
    
    quick_print("========================================")
    quick_print("本轮完成！")
    quick_print("总用时: " + str(elapsed_time) + "s")
    quick_print("总Ticks: " + str(elapsed_ticks))
    quick_print("收获阶段Ticks: " + str(harvest_ticks))
    quick_print("========================================")

# 主程序
clear()
quick_print("=== 12x12南瓜农场（ID检测优化版）===")
quick_print("目标:" + str(CONFIG['pumpkin_threshold']))
quick_print("策略: 全场种植12x12 + ID检测 + 提前收获")
quick_print("预期单次收获: 12^3 = 1,728 个南瓜")

while True:
    pumpkin_farming_cycle()
