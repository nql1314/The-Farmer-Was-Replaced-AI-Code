# The Farmer Was Replaced - 智能资源平衡种植脚本（优化版）
# 根据资源需求动态调整种植策略
# 优化：使用字典管理配置，列表缓存决策

world_size = get_world_size()

# 资源目标配置
RESOURCE_TARGETS = {
    Items.Hay: 5000,
    Items.Wood: 2000,
    Items.Carrot: 2000
}

# 生成蛇形路径
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
FARM_PATH = generate_snake_path(world_size)

# 获取资源比例字典
def get_resource_ratios():
    ratios = {}
    for item in [Items.Hay, Items.Wood, Items.Carrot]:
        target = RESOURCE_TARGETS[item]
        current = num_items(item)
        if target > 0:
            ratios[item] = current / target
        else:
            ratios[item] = 1.0
    return ratios

# 获取当前最缺的资源
def get_priority_crop():
    ratios = get_resource_ratios()
    
    hay_ratio = ratios[Items.Hay]
    wood_ratio = ratios[Items.Wood]
    carrot_ratio = ratios[Items.Carrot]
    
    if hay_ratio <= wood_ratio and hay_ratio <= carrot_ratio:
        return 'grass'
    elif wood_ratio <= carrot_ratio:
        return 'tree'
    else:
        return 'carrot'

# 检查是否应该种树
def should_plant_tree(x, y, priority):
    if priority == 'tree':
        return x % 2 == 0 and y % 2 == 0
    elif priority == 'carrot':
        return x % 3 == 0 and y % 3 == 0
    else:
        return x % 3 == 0 and y % 3 == 0

# 检查是否应该种胡萝卜
def should_plant_carrot(x, y, priority):
    if priority == 'tree':
        return (x + y) % 2 == 0
    elif priority == 'carrot':
        return (x + y) % 2 == 0
    else:
        return (x + y) % 4 == 0

# 根据策略和位置决定作物
def decide_crop_by_strategy(x, y, priority):
    # 返回：(作物类型, 需要土壤)
    if should_plant_tree(x, y, priority):
        return (Entities.Tree, False)
    elif should_plant_carrot(x, y, priority):
        return (Entities.Carrot, True)
    else:
        return (Entities.Grass, False)

# 移动一步
def move_one_step(current_x, current_y, target_x, target_y):
    if current_x < target_x:
        move(East)
    elif current_x > target_x:
        move(West)
    elif current_y < target_y:
        move(North)
    elif current_y > target_y:
        move(South)

# 智能农场循环
def smart_farm_cycle():
    # 确定当前策略
    priority = get_priority_crop()
    
    # 策略描述
    if priority == 'grass':
        strategy_desc = '干草优先'
    elif priority == 'tree':
        strategy_desc = '木头优先'
    else:
        strategy_desc = '胡萝卜优先'
    
    # 统计字典
    stats = {
        'strategy': strategy_desc,
        'harvested': 0,
        'trees': 0,
        'carrots': 0,
        'grass': 0,
        'watered': 0
    }
    
    # 当前位置
    current_pos = [get_pos_x(), get_pos_y()]
    
    # 遍历路径
    for i in range(len(FARM_PATH)):
        x, y = FARM_PATH[i]
        
        # 收割
        if can_harvest():
            harvest()
            stats['harvested'] = stats['harvested'] + 1
        
        # 根据策略决定作物
        crop, needs_soil = decide_crop_by_strategy(x, y, priority)
        
        # 准备土壤
        if needs_soil and get_ground_type() != Grounds.Soil:
            till()
        
        # 种植
        plant(crop)
        
        # 统计
        if crop == Entities.Tree:
            stats['trees'] = stats['trees'] + 1
        elif crop == Entities.Carrot:
            stats['carrots'] = stats['carrots'] + 1
            # 胡萝卜特殊处理
            if get_water() < 0.5 and num_items(Items.Water) > 0:
                use_item(Items.Water)
                stats['watered'] = stats['watered'] + 1
        else:
            stats['grass'] = stats['grass'] + 1
        
        # 移动到下一个位置
        if i < len(FARM_PATH) - 1:
            next_x, next_y = FARM_PATH[i + 1]
            move_one_step(current_pos[0], current_pos[1], next_x, next_y)
            current_pos = [next_x, next_y]
    
    return stats

# 显示状态
def show_status():
    quick_print("=== 资源状态 ===")
    
    # 干草
    hay = num_items(Items.Hay)
    hay_target = RESOURCE_TARGETS[Items.Hay]
    hay_percent = hay * 100 / hay_target
    quick_print("干草: " + str(hay) + "/" + str(hay_target))
    
    # 木头
    wood = num_items(Items.Wood)
    wood_target = RESOURCE_TARGETS[Items.Wood]
    wood_percent = wood * 100 / wood_target
    quick_print("木头: " + str(wood) + "/" + str(wood_target))
    
    # 胡萝卜
    carrot = num_items(Items.Carrot)
    carrot_target = RESOURCE_TARGETS[Items.Carrot]
    carrot_percent = carrot * 100 / carrot_target
    quick_print("胡萝卜: " + str(carrot) + "/" + str(carrot_target))
    
    # 显示当前优先级
    priority = get_priority_crop()
    if priority == 'grass':
        quick_print("策略: 干草优先")
    elif priority == 'tree':
        quick_print("策略: 木头优先")
    else:
        quick_print("策略: 胡萝卜优先")

# 显示统计信息
def show_stats(stats):
    quick_print("收获:" + str(stats['harvested']) + 
               " 树:" + str(stats['trees']) +
               " 萝:" + str(stats['carrots']) +
               " 草:" + str(stats['grass']))

# 主循环
clear()
quick_print("=== 智能资源农场启动 ===")

while True:
    show_status()
    stats = smart_farm_cycle()
    show_stats(stats)
