# The Farmer Was Replaced - 基础资源种植脚本（优化版）
# 专门种植：干草（Hay）、木头（Wood）、胡萝卜（Carrot）
# 优化：使用字典配置，列表缓存路径

world_size = get_world_size()

# 作物配置字典
CROP_CONFIG = {
    'tree_interval': 3,
    'carrot_ratio': 3,
    'water_threshold': 0.5,
    'fertilizer_reserve': 10
}

# 资源目标字典
RESOURCE_TARGETS = {
    Items.Hay: 5000,
    Items.Wood: 2000,
    Items.Carrot: 2000
}

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
FARM_PATH = generate_snake_path(world_size)

# 检查是否应该种树
def should_plant_tree(x, y):
    interval = CROP_CONFIG['tree_interval']
    return x % interval == 0 and y % interval == 0

# 决定种植什么作物
def decide_crop(x, y):
    # 返回：(作物类型, 需要土壤)
    if should_plant_tree(x, y):
        return (Entities.Tree, False)
    elif (x + y) % CROP_CONFIG['carrot_ratio'] == 1:
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

# 主遍历和种植函数
def farm_cycle():
    # 统计字典
    stats = {
        'harvested': 0,
        'trees': 0,
        'carrots': 0,
        'grass': 0,
        'watered': 0,
        'fertilized': 0
    }
    
    # 当前位置
    current_pos = [get_pos_x(), get_pos_y()]
    
    # 遍历路径
    for i in range(len(FARM_PATH)):
        x, y = FARM_PATH[i]
        
        # 收割成熟的植物
        if can_harvest():
            harvest()
            stats['harvested'] = stats['harvested'] + 1
        
        # 决定种植什么
        crop, needs_soil = decide_crop(x, y)
        
        # 准备土壤（如果需要）
        if needs_soil and get_ground_type() != Grounds.Soil:
            till()
        
        # 种植
        plant(crop)
        
        # 统计
        if crop == Entities.Tree:
            stats['trees'] = stats['trees'] + 1
        elif crop == Entities.Carrot:
            stats['carrots'] = stats['carrots'] + 1
            # 特殊处理：胡萝卜
            # 智能浇水
            if get_water() < CROP_CONFIG['water_threshold']:
                if num_items(Items.Water) > 0:
                    use_item(Items.Water)
                    stats['watered'] = stats['watered'] + 1
            
            # 使用肥料（如果有富余）
            if num_items(Items.Fertilizer) > CROP_CONFIG['fertilizer_reserve']:
                use_item(Items.Fertilizer)
                stats['fertilized'] = stats['fertilized'] + 1
        else:
            stats['grass'] = stats['grass'] + 1
        
        # 移动到下一个位置
        if i < len(FARM_PATH) - 1:
            next_x, next_y = FARM_PATH[i + 1]
            move_one_step(current_pos[0], current_pos[1], next_x, next_y)
            current_pos = [next_x, next_y]
    
    return stats

# 显示库存状态
def show_inventory():
    # 创建库存字典
    inventory = {
        'hay': num_items(Items.Hay),
        'wood': num_items(Items.Wood),
        'carrot': num_items(Items.Carrot),
        'water': num_items(Items.Water),
        'fertilizer': num_items(Items.Fertilizer),
        'power': num_items(Items.Power)
    }
    
    quick_print("=== 资源库存 ===")
    quick_print("干草: " + str(inventory['hay']) + "/" + str(RESOURCE_TARGETS[Items.Hay]))
    quick_print("木头: " + str(inventory['wood']) + "/" + str(RESOURCE_TARGETS[Items.Wood]))
    quick_print("胡萝卜: " + str(inventory['carrot']) + "/" + str(RESOURCE_TARGETS[Items.Carrot]))
    quick_print("水: " + str(inventory['water']) + " 肥料: " + str(inventory['fertilizer']))
    
    return inventory

# 显示统计信息
def show_stats(stats):
    quick_print("收获:" + str(stats['harvested']) + 
               " 树:" + str(stats['trees']) +
               " 萝:" + str(stats['carrots']) +
               " 草:" + str(stats['grass']))

# 主循环
clear()
quick_print("=== 基础农场启动 ===")

while True:
    inventory = show_inventory()
    stats = farm_cycle()
    show_stats(stats)
