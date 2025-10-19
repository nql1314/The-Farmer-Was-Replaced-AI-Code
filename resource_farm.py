# The Farmer Was Replaced - 智能资源平衡种植脚本（12x12优化版）
# 单次循环，地图记录伴生，顺路种植，零回头

SIZE = get_world_size()

# 资源目标
TARGETS = {
    Items.Hay: 1000000,
    Items.Wood: 500000,
    Items.Carrot: 500000
}

# 伴生地图（存储每个位置需要的作物类型）
companion_map = {}

# 获取优先级（使用乘法避免除法）
def get_priority():
    hay = num_items(Items.Hay)
    wood = num_items(Items.Wood)
    carrot = num_items(Items.Carrot)
    
    # 比较相对进度：hay/1000000 vs wood/500000 vs carrot/500000
    # 使用乘法：hay*1 vs wood*2 vs carrot*2
    if hay <= wood * 2 and hay <= carrot * 2:
        return 0  # grass
    elif wood <= carrot:
        return 1  # tree
    else:
        return 2  # carrot

# 决定种植作物（内联优化，返回整数）
def decide_crop(x, y, priority):
    # 树的判断
    if priority == 1:  # tree priority
        if x % 2 == 0 and y % 2 == 0:
            return 1  # Tree
    else:
        if x % 3 == 0 and y % 3 == 0:
            return 1  # Tree
    
    # 胡萝卜的判断
    if priority == 2:  # carrot priority
        if (x + y) % 2 == 0:
            return 2  # Carrot
    elif priority == 1:
        if (x + y) % 2 == 0:
            return 2  # Carrot
    else:
        if (x + y) % 4 == 0:
            return 2  # Carrot
    
    # 默认种草
    return 0  # Grass

# 种植作物（根据编号）
def plant_crop(crop_id):
    if crop_id == 1:
        plant(Entities.Tree)
    elif crop_id == 2:
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Carrot)
        # 胡萝卜浇水
        if get_water() < 0.5:
            if num_items(Items.Water) > 0:
                use_item(Items.Water)
    else:
        plant(Entities.Grass)

# 主循环（单次蛇形遍历）
def farm_cycle():
    priority = get_priority()
    
    # 统计
    harvested = 0
    trees = 0
    carrots = 0
    grass = 0
    companions_recorded = 0
    companions_planted = 0
    
    # 蛇形遍历
    for y in range(SIZE):
        # 确定行方向
        if y % 2 == 0:
            x_range = range(SIZE)
            x_step = 1
        else:
            x_range = range(SIZE - 1, -1, -1)
            x_step = -1
        
        for x in x_range:
            # 收割
            if can_harvest():
                harvest()
                harvested = harvested + 1
            
            # 检查是否有伴生需求
            pos_key = y * SIZE + x
            if pos_key in companion_map:
                # 按照伴生需求种植
                comp_type = companion_map[pos_key]
                
                if comp_type == Entities.Carrot:
                    if get_ground_type() != Grounds.Soil:
                        till()
                    plant(Entities.Carrot)
                    if get_water() < 0.5:
                        if num_items(Items.Water) > 0:
                            use_item(Items.Water)
                    carrots = carrots + 1
                elif comp_type == Entities.Tree:
                    plant(Entities.Tree)
                    trees = trees + 1
                else:
                    plant(Entities.Grass)
                    grass = grass + 1
                
                companions_planted = companions_planted + 1
                # 清除已处理的伴生需求
                companion_map.pop(pos_key)
            else:
                # 按照策略种植
                crop_id = decide_crop(x, y, priority)
                plant_crop(crop_id)
                
                # 统计
                if crop_id == 1:
                    trees = trees + 1
                elif crop_id == 2:
                    carrots = carrots + 1
                else:
                    grass = grass + 1
            
            # 记录伴生需求到地图
            comp = get_companion()
            if comp != None:
                comp_type, comp_pos = comp
                cx, cy = comp_pos
                comp_key = cy * SIZE + cx
                # 只记录，不立即处理
                companion_map[comp_key] = comp_type
                companions_recorded = companions_recorded + 1
            
            # 移动到下一格（蛇形）
            if x != x_range[-1]:
                if x_step > 0:
                    move(East)
                else:
                    move(West)
        
        # 移动到下一行
        if y < SIZE - 1:
            move(North)
    
    # 显示统计
    if priority == 0:
        desc = "草"
    elif priority == 1:
        desc = "树"
    else:
        desc = "萝"
    
    quick_print(desc + " 收:" + str(harvested) + 
               " 树:" + str(trees) +
               " 萝:" + str(carrots) +
               " 草:" + str(grass) +
               " 伴记:" + str(companions_recorded) +
               " 伴种:" + str(companions_planted))

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
quick_print("=== 12x12智能农场 ===")

while True:
    show_status()
    farm_cycle()
