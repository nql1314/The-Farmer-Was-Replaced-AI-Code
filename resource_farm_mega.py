# The Farmer Was Replaced - 多无人机智能资源平衡种植脚本（肥料版）
# 策略：持久化无人机池，每个无人机独立循环工作
# 优化：无人机持续运行，无需重复创建，最大化并行效率
# 特性：伴生作物自动施肥，加速生长并获得奇异物质

from farm_utils import goto, generate_snake_path

SIZE = get_world_size()

# 资源目标
TARGETS = {
    Items.Hay: 1000000000,
    Items.Wood: 500000000,
    Items.Carrot: 500000000
}

# 创建共享数据源（用于无人机间通信）
def create_shared_data():
    return {
        "companion_map": {},     # 伴生地图
        "priority": 0,           # 当前优先级
        "should_stop": False,    # 停止信号
        "stats": {               # 统计数据
            "harvested": 0,
            "trees": 0,
            "carrots": 0,
            "grass": 0
        }
    }

# 全局共享数据（通过 wait_for 机制实现真正的共享）
shared_source = spawn_drone(create_shared_data)
shared = wait_for(shared_source)

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

# 无人机持久工作函数：持续循环处理一个区域
def drone_worker(region_id, x_start, x_end, y_start, y_end):
    # 获取共享数据
    data = wait_for(shared_source)
    
    # 缓存区域尺寸
    width = x_end - x_start
    height = y_end - y_start
    
    # 无限循环工作
    while True:
        # 检查是否需要停止
        if data["should_stop"]:
            break
        
        # 获取当前优先级
        priority = data["priority"]
        
        # 本轮统计
        local_harvested = 0
        local_trees = 0
        local_carrots = 0
        local_grass = 0
        local_fertilized = 0  # 施肥次数
        
        # 移动到区域起点
        goto(x_start, y_start)
        
        # 蛇形遍历区域
        for row in range(height):
            y = y_start + row
            going_east = row % 2 == 0
            
            for col in range(width):
                # 计算当前 x 坐标
                if going_east:
                    x = x_start + col
                else:
                    x = x_end - 1 - col
                
                # 收割
                if can_harvest():
                    harvest()
                    local_harvested = local_harvested + 1
                
                # 检查伴生需求
                pos_key = y * SIZE + x
                companion_map = data["companion_map"]
                has_companion = pos_key in companion_map
                
                if has_companion:
                    # 按照伴生需求种植
                    comp_type = companion_map[pos_key]
                    
                    if comp_type == Entities.Carrot:
                        if get_ground_type() != Grounds.Soil:
                            till()
                        plant(Entities.Carrot)
                        # 伴生作物施肥（加速生长+感染）
                        if num_items(Items.Fertilizer) > 0:
                            use_item(Items.Fertilizer)
                            local_fertilized = local_fertilized + 1
                        # 浇水
                        if get_water() < 0.5:
                            if num_items(Items.Water) > 0:
                                use_item(Items.Water)
                        local_carrots = local_carrots + 1
                    elif comp_type == Entities.Tree:
                        plant(Entities.Tree)
                        # 伴生作物施肥
                        if num_items(Items.Fertilizer) > 0:
                            use_item(Items.Fertilizer)
                            local_fertilized = local_fertilized + 1
                        local_trees = local_trees + 1
                    else:
                        plant(Entities.Grass)
                        # 伴生作物施肥
                        if num_items(Items.Fertilizer) > 0:
                            use_item(Items.Fertilizer)
                            local_fertilized = local_fertilized + 1
                        local_grass = local_grass + 1
                else:
                    # 按照策略种植（普通作物不施肥）
                    crop_id = decide_crop(x, y, priority)
                    plant_crop(crop_id)
                    
                    if crop_id == 1:
                        local_trees = local_trees + 1
                    elif crop_id == 2:
                        local_carrots = local_carrots + 1
                    else:
                        local_grass = local_grass + 1
                
                # 记录新的伴生需求
                comp = get_companion()
                if comp != None:
                    comp_type, comp_pos = comp
                    cx, cy = comp_pos
                    comp_key = cy * SIZE + cx
                    companion_map[comp_key] = comp_type
                
                # 移动到下一个位置
                if col < width - 1:
                    if going_east:
                        move(East)
                    else:
                        move(West)
            
            # 移动到下一行
            if row < height - 1:
                move(North)
        
        # 更新共享统计（使用独立键避免竞态条件）
        stats = data["stats"]
        region_key = "region_" + str(region_id)
        stats[region_key] = (local_harvested, local_trees, local_carrots, local_grass, local_fertilized)

# 动态计算区域划分（最大化无人机利用）
def calculate_regions():
    max_d = max_drones()
    
    # 根据最大无人机数量动态划分
    if max_d >= 16:
        # 16+ 无人机：4x4 网格
        step = SIZE // 4
        regions = []
        for row in range(4):
            for col in range(4):
                x_start = col * step
                if col < 3:
                    x_end = (col + 1) * step
                else:
                    x_end = SIZE
                y_start = row * step
                if row < 3:
                    y_end = (row + 1) * step
                else:
                    y_end = SIZE
                regions.append((x_start, x_end, y_start, y_end))
        return regions
    elif max_d >= 9:
        # 9-15 无人机：3x3 网格
        step = SIZE // 3
        regions = []
        for row in range(3):
            for col in range(3):
                x_start = col * step
                if col < 2:
                    x_end = (col + 1) * step
                else:
                    x_end = SIZE
                y_start = row * step
                if row < 2:
                    y_end = (row + 1) * step
                else:
                    y_end = SIZE
                regions.append((x_start, x_end, y_start, y_end))
        return regions
    elif max_d >= 4:
        # 4-8 无人机：2x2 网格
        half = SIZE // 2
        return [
            (0, half, 0, half),
            (half, SIZE, 0, half),
            (0, half, half, SIZE),
            (half, SIZE, half, SIZE)
        ]
    elif max_d >= 2:
        # 2-3 无人机：上下分割
        half = SIZE // 2
        return [
            (0, SIZE, 0, half),
            (0, SIZE, half, SIZE)
        ]
    else:
        # 单无人机：整个农场
        return [(0, SIZE, 0, SIZE)]

# 启动持久化无人机池
def start_drone_pool():
    regions = calculate_regions()
    drones = []
    
    quick_print("=== 启动无人机池 ===")
    quick_print("区域数：" + str(len(regions)))
    quick_print("最大无人机：" + str(max_drones()))
    
    # 为每个区域启动持久化无人机
    for i in range(len(regions)):
        x_start, x_end, y_start, y_end = regions[i]
        
        # 创建无人机工作函数（闭包捕获参数）
        def create_worker(rid, xs, xe, ys, ye):
            def worker():
                drone_worker(rid, xs, xe, ys, ye)
            return worker
        
        worker_func = create_worker(i, x_start, x_end, y_start, y_end)
        
        # 生成无人机
        drone = spawn_drone(worker_func)
        if drone:
            drones.append(drone)
            quick_print("区域" + str(i) + ": 无人机已启动")
        else:
            quick_print("区域" + str(i) + ": 无法生成（达到上限）")
            break
    
    quick_print("成功启动 " + str(len(drones)) + " 个持久无人机")
    return drones

# 收集统计数据
def collect_stats():
    stats = shared["stats"]
    total_harvested = 0
    total_trees = 0
    total_carrots = 0
    total_grass = 0
    total_fertilized = 0
    
    # 遍历所有区域统计
    for key in stats:
        if key != "harvested" and key != "trees" and key != "carrots" and key != "grass":
            region_stats = stats[key]
            if region_stats:
                # 兼容旧版本（4个值）和新版本（5个值）
                if len(region_stats) == 5:
                    h, t, c, g, f = region_stats
                    total_fertilized = total_fertilized + f
                else:
                    h, t, c, g = region_stats
                total_harvested = total_harvested + h
                total_trees = total_trees + t
                total_carrots = total_carrots + c
                total_grass = total_grass + g
    
    return (total_harvested, total_trees, total_carrots, total_grass, total_fertilized)

# 主循环：监控和更新优先级
def main_loop():
    # 获取当前优先级
    priority = get_priority()
    shared["priority"] = priority
    
    # 显示优先级
    if priority == 0:
        desc = "草"
    elif priority == 1:
        desc = "树"
    else:
        desc = "萝"
    
    quick_print("优先级: " + desc)

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
quick_print("=== 持久化多无人机农场 V2 ===")
quick_print("农场大小：" + str(SIZE) + "x" + str(SIZE))
quick_print("最大无人机：" + str(max_drones()))

# 启动持久化无人机池（只启动一次）
drones = start_drone_pool()

# 主循环：只负责监控和更新优先级
cycle_count = 0
while True:
    cycle_count = cycle_count + 1
    
    # 显示状态
    show_status()
    
    # 更新优先级
    main_loop()
    
    # 每隔一段时间显示统计（可选）
    if cycle_count % 5 == 0:
        harvested, trees, carrots, grass, fertilized = collect_stats()
        quick_print("统计 - 收:" + str(harvested) + 
                   " 树:" + str(trees) + 
                   " 萝:" + str(carrots) + 
                   " 草:" + str(grass) +
                   " 肥:" + str(fertilized))
    
    # 等待一段时间再检查（让无人机工作）
    for i in range(10):
        do_a_flip()
