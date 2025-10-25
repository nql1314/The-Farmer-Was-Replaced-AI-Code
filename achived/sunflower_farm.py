# The Farmer Was Replaced - 向日葵能量农场（滚动收获优化版）
# 优化策略：持续循环，从花瓣15开始依次收获成熟的向日葵，无需等待

# 导入工具函数
from farm_utils import optimize_path_circle, goto_pos

SIZE = get_world_size()

# 初始化农场：种植整个农场的向日葵
def initialize_farm():
    quick_print("初始化农场...")
    planted_count = 0
    
    # 遍历种植
    for y in range(SIZE):
        for x in range(SIZE):
            # 收割旧作物
            if can_harvest():
                harvest()
            
            # 翻土（向日葵需要土壤）
            if get_ground_type() != Grounds.Soil:
                till()
            
            # 种植向日葵
            plant(Entities.Sunflower)
            planted_count = planted_count + 1
            
            # 移动到下一格
            move(East)
        
        # 移动到下一行
        move(North)
    
    quick_print("初始化完成：" + str(planted_count) + " 株向日葵")

# 扫描所有成熟向日葵，按花瓣数分组，并顺带收获15瓣的
def scan_and_harvest_15_petals():
    # 字典：花瓣数 -> 位置列表
    petal_groups = {}
    total_mature = 0
    harvested_15 = 0
    
    # 回到原点
    goto_pos(0, 0)
    
    # 简单遍历：从下到上，从左到右
    for y in range(SIZE):
        for x in range(SIZE):
            # 检查是否是成熟的向日葵
            if get_entity_type() == Entities.Sunflower and can_harvest():
                petals = measure()
                total_mature = total_mature + 1
                
                if petals == 15:
                    # 立即收获15瓣的
                    harvest()
                    harvested_15 = harvested_15 + 1
                else:
                    # 其他花瓣数记录位置
                    if petals not in petal_groups:
                        petal_groups[petals] = []
                    petal_groups[petals].append((x, y))
            
            # 移动到下一格（环形地图，可以直接向东）
            move(East)
        
        # 移动到下一行（环形地图，可以直接向北）
        # 回到行首
        move(North)
    
    return petal_groups, total_mature, harvested_15

# 简单遍历收获指定位置字典
def harvest_simple_mode(positions_dict):
    # positions_dict: 位置字典，用于快速查找
    harvested_count = 0
    
    # 回到原点
    goto_pos(0, 0)
    
    # 简单遍历：从下到上，从左到右
    for y in range(SIZE):
        for x in range(SIZE):
            # 检查当前位置是否在待收获字典中
            pos = (x, y)
            if pos in positions_dict:
                # 收获
                if can_harvest():
                    harvest()
                    harvested_count = harvested_count + 1
            move(East)
        move(North)
    
    return harvested_count

# 路径优化收获指定位置列表
def harvest_optimized_mode(positions):
    current_x = get_pos_x()
    current_y = get_pos_y()
    optimized_positions = optimize_path_circle(positions, current_x, current_y)
    harvested_count = 0
    
    for px, py in optimized_positions:
        goto_pos(px, py)
        
        if can_harvest():
            harvest()
            harvested_count = harvested_count + 1
    
    return harvested_count

# 滚动收获循环
def rolling_harvest_cycle():
    
    power_before = num_items(Items.Power)
    total_harvested = 0
    total_bonus = 0
    
    # 第二步：扫描所有成熟的向日葵，按花瓣数分组，并顺带收获15瓣的
    petal_groups, total_mature, harvested_15 = scan_and_harvest_15_petals()
    
    if total_mature == 0:
        quick_print("没有成熟的向日葵")
        return
    
    quick_print("扫描到 " + str(total_mature) + " 株成熟向日葵")
    
    # 统计15瓣的收获
    if harvested_15 > 0:
        get_bonus_15 = total_mature >= 10
        if get_bonus_15:
            quick_print("已收获 " + str(harvested_15) + " 株 15 瓣（5倍奖励）")
            total_bonus = total_bonus + harvested_15
        else:
            quick_print("已收获 " + str(harvested_15) + " 株 15 瓣")
        total_harvested = total_harvested + harvested_15
    
    # 计算剩余未收获数量
    remaining = total_mature - harvested_15
    
    # 如果剩余不足10株，全部收获后结束
    if remaining > 0 and remaining < 10:
        quick_print("剩余 " + str(remaining) + " 株，全部收获")
        
        # 收获所有剩余的
        for petals in range(14, 6, -1):
            if petals not in petal_groups:
                continue
            
            positions = petal_groups[petals]
            count = len(positions)
            
            quick_print("收获 " + str(count) + " 株 " + str(petals) + " 瓣")
            
            quick_print("  -> 路径优化")
            harvested = harvest_optimized_mode(positions)
            
            total_harvested = total_harvested + harvested
    
    # 如果剩余>=10株，从14瓣开始依次收获
    elif remaining >= 10:
        for petals in range(14, 6, -1):
            if petals not in petal_groups:
                continue
            
            positions = petal_groups[petals]
            count = len(positions)
            
            # 检查是否满足5倍奖励条件（至少10株成熟，且花瓣数最多）
            is_max_petals = True
            for p in range(petals + 1, 16):
                if p in petal_groups:
                    is_max_petals = False
                    break
            
            # 重新计算剩余数量
            remaining = total_mature - total_harvested
            get_bonus = is_max_petals and remaining >= 10
            
            # 显示信息
            if get_bonus:
                quick_print("收获 " + str(count) + " 株 " + str(petals) + " 瓣（5倍奖励）")
            else:
                quick_print("收获 " + str(count) + " 株 " + str(petals) + " 瓣")
            
            quick_print("  -> 路径优化")
            harvested = harvest_optimized_mode(positions)
            
            total_harvested = total_harvested + harvested
            if get_bonus:
                total_bonus = total_bonus + harvested
            
            # 收获后检查剩余数量，如果<10就全部收获剩余的
            remaining = total_mature - total_harvested
            if remaining > 0 and remaining < 10:
                quick_print("剩余 " + str(remaining) + " 株，全部收获")
                # 收获所有剩余的花瓣组
                for p in range(petals - 1, 6, -1):
                    if p not in petal_groups:
                        continue
                    
                    pos_list = petal_groups[p]
                    c = len(pos_list)
                    quick_print("收获 " + str(c) + " 株 " + str(p) + " 瓣")
                    
                    quick_print("  -> 路径优化")
                    h = harvest_optimized_mode(pos_list)
                    
                    total_harvested = total_harvested + h
                break
    
    power_after = num_items(Items.Power)
    power_gained = power_after - power_before
    
    quick_print("本轮总计：收获 " + str(total_harvested) + " 株，5倍 " + str(total_bonus) + " 次，能量 +" + str(power_gained))

# 主程序
clear()
quick_print("=== 向日葵能量农场（滚动收获版）===")
quick_print("农场大小：" + str(SIZE) + "x" + str(SIZE))
quick_print("策略：从15瓣开始依次收获，持续循环")
quick_print("")
cycle_count = 0


while True:
    # 初始化：种植第一批向日葵
    goto_pos(0, 0)
    initialize_farm()
    quick_print("")
    quick_print("开始滚动收获循环...")
    quick_print("========================================")
    # 滚动收获循环
    cycle_count = cycle_count + 1
    quick_print("")
    quick_print("--- 第 " + str(cycle_count) + " 轮 ---")
    quick_print("能量：" + str(num_items(Items.Power)))
    
    rolling_harvest_cycle()
    
    quick_print("========================================")

