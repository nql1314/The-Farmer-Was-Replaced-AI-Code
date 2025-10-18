# The Farmer Was Replaced - 智能资源平衡种植脚本（全面优化版）
# 利用伴生植物机制，动态调整策略
# 优化：减少计算，智能伴生处理，路径优化

world_size = get_world_size()

# 资源目标
TARGETS = {
    Items.Hay: 10000,
    Items.Wood: 5000,
    Items.Carrot: 5000
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

FARM_PATH = generate_snake_path(world_size)

# 移动到指定位置
def goto(tx, ty):
    while get_pos_x() < tx:
        move(East)
    while get_pos_x() > tx:
        move(West)
    while get_pos_y() < ty:
        move(North)
    while get_pos_y() > ty:
        move(South)

# 获取优先级（优化：减少除法）
def get_priority():
    hay = num_items(Items.Hay)
    wood = num_items(Items.Wood)
    carrot = num_items(Items.Carrot)
    
    # 使用乘法代替除法（避免浮点运算）
    # hay/10000 vs wood/5000 => hay*5000 vs wood*10000
    hay_score = hay * 5 * 5  # hay / 10000
    wood_score = wood * 10 * 5  # wood / 5000
    carrot_score = carrot * 10 * 5  # carrot / 5000
    
    if hay_score <= wood_score and hay_score <= carrot_score:
        return 'grass'
    elif wood_score <= carrot_score:
        return 'tree'
    else:
        return 'carrot'

# 决定作物
def decide_crop(x, y, priority):
    # 树的判断
    if priority == 'tree':
        if x % 2 == 0 and y % 2 == 0:
            return (Entities.Tree, False)
    else:
        if x % 3 == 0 and y % 3 == 0:
            return (Entities.Tree, False)
    
    # 胡萝卜的判断
    if priority == 'carrot':
        if (x + y) % 2 == 0:
            return (Entities.Carrot, True)
    elif priority == 'tree':
        if (x + y) % 2 == 0:
            return (Entities.Carrot, True)
    else:
        if (x + y) % 4 == 0:
            return (Entities.Carrot, True)
    
    # 默认种草
    return (Entities.Grass, False)

# 种植并记录伴生
def plant_and_record(x, y, priority, companions):
    crop, needs_soil = decide_crop(x, y, priority)
    
    # 准备土壤
    if needs_soil and get_ground_type() != Grounds.Soil:
        till()
    
    # 种植
    plant(crop)
    
    # 记录伴生需求
    comp = get_companion()
    if comp != None:
        comp_type, comp_pos = comp
        companions[(x, y)] = (comp_type, comp_pos)
    
    # 胡萝卜浇水
    if crop == Entities.Carrot:
        if get_water() < 0.5 and num_items(Items.Water) > 0:
            use_item(Items.Water)
    
    return crop

# 满足伴生需求（优化：智能检查）
def fulfill_companions(companions):
    fulfilled = 0
    
    for pos in companions:
        req = companions[pos]
        comp_type, comp_pos = req
        cx, cy = comp_pos
        
        goto(cx, cy)
        
        current = get_entity_type()
        
        # 只在不匹配时才重新种植
        if current != comp_type:
            # 收割
            if can_harvest():
                harvest()
            
            # 准备土壤
            if comp_type == Entities.Carrot:
                if get_ground_type() != Grounds.Soil:
                    till()
            
            # 种植
            plant(comp_type)
            fulfilled = fulfilled + 1
    
    return fulfilled

# 主循环
def farm_cycle():
    priority = get_priority()
    
    # 策略描述
    if priority == 'grass':
        desc = '干草'
    elif priority == 'tree':
        desc = '木头'
    else:
        desc = '胡萝卜'
    
    # 统计
    stats = {
        'harvested': 0,
        'trees': 0,
        'carrots': 0,
        'grass': 0,
        'companions': 0
    }
    
    companions = {}
    
    # 第一遍：种植并记录伴生
    for i in range(len(FARM_PATH)):
        x, y = FARM_PATH[i]
        
        # 收割
        if can_harvest():
            harvest()
            stats['harvested'] = stats['harvested'] + 1
        
        # 种植
        crop = plant_and_record(x, y, priority, companions)
        
        # 统计
        if crop == Entities.Tree:
            stats['trees'] = stats['trees'] + 1
        elif crop == Entities.Carrot:
            stats['carrots'] = stats['carrots'] + 1
        else:
            stats['grass'] = stats['grass'] + 1
        
        # 移动
        if i < len(FARM_PATH) - 1:
            nx, ny = FARM_PATH[i + 1]
            goto(nx, ny)
    
    # 第二遍：满足伴生
    if len(companions) > 0:
        stats['companions'] = fulfill_companions(companions)
    
    # 显示统计
    quick_print(desc + " 收:" + str(stats['harvested']) + 
               " 树:" + str(stats['trees']) +
               " 萝:" + str(stats['carrots']) +
               " 草:" + str(stats['grass']) +
               " 伴:" + str(stats['companions']))

# 显示状态
def show_status():
    hay = num_items(Items.Hay)
    wood = num_items(Items.Wood)
    carrot = num_items(Items.Carrot)
    
    quick_print("=== 资源 ===")
    quick_print("干:" + str(hay) + "/" + str(TARGETS[Items.Hay]))
    quick_print("木:" + str(wood) + "/" + str(TARGETS[Items.Wood]))
    quick_print("萝:" + str(carrot) + "/" + str(TARGETS[Items.Carrot]))

# 主程序
clear()
quick_print("=== 智能农场 ===")

while True:
    show_status()
    farm_cycle()
