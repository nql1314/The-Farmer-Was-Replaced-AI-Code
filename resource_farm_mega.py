# The Farmer Was Replaced - 多无人机智能资源平衡种植脚本
# 策略：将农场分区，每个无人机负责独立区域，并行收集资源
# 优化：最大化无人机利用率，减少总时间

from farm_utils import goto_pos, generate_snake_path

SIZE = get_world_size()

# 资源目标
TARGETS = {
    Items.Hay: 1000000000,
    Items.Wood: 500000000,
    Items.Carrot: 500000000
}

# 伴生地图（全局共享，但每个无人机只处理自己区域）
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

# 无人机工作函数：处理一个区域
def drone_farm_region(x_start, x_end, y_start, y_end, priority):
    # 无人机负责一个矩形区域的种植和收割
    harvested = 0
    trees = 0
    carrots = 0
    grass = 0
    
    # 蛇形遍历区域
    for y in range(y_start, y_end):
        # 确定行方向
        if (y - y_start) % 2 == 0:
            x_range = range(x_start, x_end)
        else:
            x_range = range(x_end - 1, x_start - 1, -1)
        
        for x in x_range:
            # 移动到位置
            goto_pos(x, y)
            
            # 收割
            if can_harvest():
                harvest()
                harvested = harvested + 1
            
            # 检查是否有伴生需求（使用全局字典）
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
            
            # 记录伴生需求到全局地图
            comp = get_companion()
            if comp != None:
                comp_type, comp_pos = comp
                cx, cy = comp_pos
                comp_key = cy * SIZE + cx
                companion_map[comp_key] = comp_type
    
    # 返回统计
    return (harvested, trees, carrots, grass)

# 主循环（多无人机版本）
def farm_cycle_mega():
    priority = get_priority()
    
    # 计算区域划分
    drone_count = num_drones()
    max_drones1 = max_drones()
    
    # 根据可用无人机数量划分区域
    # 策略：将农场水平分割为若干条带
    regions = []
    
    if max_drones1 >= 4:
        # 4个或更多无人机：分成4个区域（2x2网格）
        half_size = SIZE // 2
        regions = [
            (0, half_size, 0, half_size),           # 左下
            (half_size, SIZE, 0, half_size),        # 右下
            (0, half_size, half_size, SIZE),        # 左上
            (half_size, SIZE, half_size, SIZE)      # 右上
        ]
    elif max_drones1 >= 2:
        # 2-3个无人机：水平分割
        half_size = SIZE // 2
        regions = [
            (0, SIZE, 0, half_size),                # 下半部分
            (0, SIZE, half_size, SIZE)              # 上半部分
        ]
    else:
        # 只有主无人机：整个农场
        regions = [(0, SIZE, 0, SIZE)]
    
    # 启动无人机处理各个区域
    drones = []
    total_stats = [0, 0, 0, 0]  # harvested, trees, carrots, grass
    
    quick_print("启动" + str(len(regions)) + "个区域任务")
    
    for i in range(len(regions)):
        x_start, x_end, y_start, y_end = regions[i]
        
        # 定义无人机任务函数
        def create_task(xs, xe, ys, ye, p):
            def task():
                return drone_farm_region(xs, xe, ys, ye, p)
            return task
        
        task_func = create_task(x_start, x_end, y_start, y_end, priority)
        
        if i < len(regions) - 1:
            # 尝试生成无人机
            drone = spawn_drone(task_func)
            if drone:
                drones.append(drone)
                quick_print("区域" + str(i+1) + ": 无人机")
            else:
                # 无法生成更多无人机，主无人机执行
                stats = task_func()
                for j in range(4):
                    total_stats[j] = total_stats[j] + stats[j]
                quick_print("区域" + str(i+1) + ": 主机")
        else:
            # 最后一个区域由主无人机执行
            stats = task_func()
            for j in range(4):
                total_stats[j] = total_stats[j] + stats[j]
            quick_print("区域" + str(i+1) + ": 主机")
    
    # 等待所有无人机完成并收集结果
    for i in range(len(drones)):
        stats = wait_for(drones[i])
        if stats:
            for j in range(4):
                total_stats[j] = total_stats[j] + stats[j]
    
    # 显示统计
    if priority == 0:
        desc = "草"
    elif priority == 1:
        desc = "树"
    else:
        desc = "萝"
    
    harvested, trees, carrots, grass = total_stats
    quick_print(desc + " 收:" + str(harvested) + 
               " 树:" + str(trees) +
               " 萝:" + str(carrots) +
               " 草:" + str(grass))

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
quick_print("=== 多无人机智能农场 ===")
quick_print("农场大小：" + str(SIZE) + "x" + str(SIZE))
quick_print("最大无人机：" + str(max_drones()))

while True:
    show_status()
    farm_cycle_mega()
