# TFWR 肥料高级农场
# 高级策略：智能管理肥料使用和感染状态
# 特点：
# 1. 分区种植不同作物
# 2. 优先给生长慢的作物使用肥料
# 3. 智能管理感染状态和奇异物质
# 4. 追踪每个位置的状态

# 导入通用工具函数
from farm_utils import goto_pos, goto_origin, wrap_distance

# ====================
# 高级配置参数
# ====================

# 分区配置（将农场分成多个区域种植不同作物）
# 每个区域：(起始x, 起始y, 宽度, 高度, 作物类型, 是否使用肥料)
ZONES = [
    
    # 区域2：右下角种胡萝卜（中等价值，使用肥料）
    # (5, 0, 5, 5, Entities.Carrot, True),
    
    # 区域3：左上角种向日葵（获取能量，使用肥料）
    # (0, 5, 5, 5, Entities.Sunflower, True),
    
    # 区域4：右上角种南瓜（快速生长，不使用肥料）
    # (5, 5, 5, 5, Entities.Pumpkin, False),
]

# 肥料管理策略
FERTILIZER_PRIORITY = [
    # 按优先级排序：先给哪些作物使用肥料
    Entities.Carrot,    # 胡萝卜：6秒 -> 4秒，节省2秒（33.3%）
    Entities.Sunflower, # 向日葵：5秒 -> 3秒，节省2秒（40%）
    Entities.Pumpkin,   # 南瓜：2秒 -> 0秒，节省2秒（100%，但产量低）
]

# 感染管理配置
INFECTION_MANAGEMENT = {
    "enabled": True,              # 是否管理感染
    "cure_threshold": 50,         # 奇异物质数量阈值（达到后开始治愈）
    "cure_strategy": "selective", # 治愈策略："all"全部治愈, "selective"选择性治愈, "none"不治愈
    "cure_priority": [            # 优先治愈哪些作物
        Entities.Sunflower,       # 向日葵提供能量，优先治愈
        Entities.Carrot,
        Entities.Pumpkin,
    ],
}

# 浇水配置
WATERING_CONFIG = {
    "enabled": True,
    "threshold": 0.75,  # 水位低于此值时浇水
}

# ====================
# 状态追踪
# ====================

# 全局状态变量
farm_state = {}  # 存储每个位置的状态
statistics = {
    "total_fertilizer_used": 0,
    "total_weird_substance_used": 0,
    "total_harvested": 0,
    "cycles_completed": 0,
    "fertilizer_saved": 0,  # 节省的肥料数量（智能管理）
}

def init_farm_state(world_size):
    # 初始化农场状态追踪
    # world_size: 世界大小
    
    farm_state["size"] = world_size
    farm_state["cells"] = {}  # 格式：(x,y) -> {"crop": entity, "fertilized": bool, "infected": bool}
    
    for y in range(world_size):
        for x in range(world_size):
            farm_state["cells"][(x, y)] = {
                "crop": None,
                "fertilized": False,
                "infected": False,
                "last_harvest_time": 0,
            }

def get_cell_state(x, y):
    # 获取指定位置的状态
    if (x, y) in farm_state["cells"]:
        return farm_state["cells"][(x, y)]
    return None

def update_cell_crop(x, y, crop):
    # 更新指定位置的作物类型
    if (x, y) not in farm_state["cells"]:
        farm_state["cells"][(x, y)] = {}
    farm_state["cells"][(x, y)]["crop"] = crop

def update_cell_fertilized(x, y, fertilized):
    # 更新指定位置的肥料状态
    if (x, y) not in farm_state["cells"]:
        farm_state["cells"][(x, y)] = {}
    farm_state["cells"][(x, y)]["fertilized"] = fertilized

def update_cell_infected(x, y, infected):
    # 更新指定位置的感染状态
    if (x, y) not in farm_state["cells"]:
        farm_state["cells"][(x, y)] = {}
    farm_state["cells"][(x, y)]["infected"] = infected

# ====================
# 智能肥料管理
# ====================

def should_use_fertilizer(x, y, crop_entity):
    # 判断是否应该在此位置使用肥料
    # x, y: 位置
    # crop_entity: 作物类型
    # 返回：是否应该使用肥料
    
    # 检查肥料数量
    fertilizer_count = num_items(Items.Fertilizer)
    if fertilizer_count == 0:
        return False
    
    # 获取作物在优先级列表中的位置
    priority = -1
    for i in range(len(FERTILIZER_PRIORITY)):
        if FERTILIZER_PRIORITY[i] == crop_entity:
            priority = i
            break
    
    if priority == -1:
        return False  # 不在优先级列表中，不使用肥料
    
    # 智能决策：根据肥料数量和优先级决定
    world_size = get_world_size()
    total_cells = world_size * world_size
    
    # 如果肥料充足（>= 总格子数），全部使用
    if fertilizer_count >= total_cells:
        return True
    
    # 如果肥料有限，只给高优先级作物使用
    if priority <= 1:  # 树和胡萝卜
        return True
    elif priority == 2 and fertilizer_count >= total_cells / 2:  # 向日葵（肥料>50%）
        return True
    
    return False

def apply_fertilizer_smart(x, y, crop_entity):
    # 智能使用肥料
    # x, y: 位置
    # crop_entity: 作物类型
    # 返回：是否使用了肥料
    
    if should_use_fertilizer(x, y, crop_entity):
        if num_items(Items.Fertilizer) > 0:
            use_item(Items.Fertilizer)
            update_cell_fertilized(x, y, True)
            statistics["total_fertilizer_used"] += 1
            return True
    else:
        statistics["fertilizer_saved"] += 1
        update_cell_fertilized(x, y, False)
    
    return False

# ====================
# 智能感染管理
# ====================

def should_cure_plant(x, y, crop_entity):
    # 判断是否应该治愈此位置的植物
    # x, y: 位置
    # crop_entity: 作物类型
    # 返回：是否应该治愈
    
    if not INFECTION_MANAGEMENT["enabled"]:
        return False
    
    strategy = INFECTION_MANAGEMENT["cure_strategy"]
    
    if strategy == "none":
        return False
    elif strategy == "all":
        return True
    elif strategy == "selective":
        # 检查奇异物质数量
        weird_count = num_items(Items.Weird_Substance)
        if weird_count < INFECTION_MANAGEMENT["cure_threshold"]:
            return False
        
        # 检查作物优先级
        priority = -1
        for i in range(len(INFECTION_MANAGEMENT["cure_priority"])):
            if INFECTION_MANAGEMENT["cure_priority"][i] == crop_entity:
                priority = i
                break
        
        # 只治愈高优先级作物
        return priority <= 1
    
    return False

def cure_plant_smart(x, y, crop_entity):
    # 智能治愈植物
    # x, y: 位置
    # crop_entity: 作物类型
    # 返回：是否治愈了
    
    cell_state = get_cell_state(x, y)
    if cell_state == None or not cell_state["infected"]:
        return False  # 未感染，不需要治愈
    
    if should_cure_plant(x, y, crop_entity) and num_items(Items.Weird_Substance) > 0:
        use_item(Items.Weird_Substance)
        update_cell_infected(x, y, False)
        statistics["total_weird_substance_used"] += 1
        return True
    
    return False

# ====================
# 分区种植函数
# ====================

def get_zone_for_position(x, y):
    # 获取指定位置所属的区域
    # x, y: 位置
    # 返回：区域配置元组，如果不在任何区域则返回None
    
    for zone in ZONES:
        zone_x, zone_y, zone_w, zone_h, crop, use_fert = zone
        if x >= zone_x and x < zone_x + zone_w and y >= zone_y and y < zone_y + zone_h:
            return zone
    
    return None

def get_crop_for_position(x, y, default_crop):
    # 获取指定位置应该种植的作物
    # x, y: 位置
    # default_crop: 默认作物（如果不在任何区域）
    # 返回：作物实体类型
    
    if len(ZONES) == 0:
        return default_crop
    
    zone = get_zone_for_position(x, y)
    if zone != None:
        return zone[4]  # 返回作物类型
    
    return default_crop

# ====================
# 高级种植和收获
# ====================

def plant_advanced(x, y, default_crop):
    # 高级种植：根据位置和策略决定作物类型和是否使用肥料
    # x, y: 位置
    # default_crop: 默认作物类型
    
    # 确保土壤
    if get_ground_type() != Grounds.Soil:
        till()
    
    # 浇水（如果需要）
    if WATERING_CONFIG["enabled"] and get_water() < WATERING_CONFIG["threshold"]:
        if num_items(Items.Water) > 0:
            use_item(Items.Water)
    
    # 确定种植的作物
    crop_entity = get_crop_for_position(x, y, default_crop)
    
    # 种植
    plant(crop_entity)
    
    # 更新状态
    update_cell_crop(x, y, crop_entity)
    
    # 智能使用肥料
    apply_fertilizer_smart(x, y, crop_entity)

def harvest_advanced(x, y, default_crop):
    # 高级收获：收获并根据策略治愈和重新种植
    # x, y: 位置
    # default_crop: 默认作物类型（用于重新种植）
    # 返回：是否成功收获
    
    if not can_harvest():
        return False
    
    # 获取当前状态
    cell_state = get_cell_state(x, y)
    crop_entity = default_crop
    if cell_state != None and cell_state["crop"] != None:
        crop_entity = cell_state["crop"]
    
    # 收获
    harvest()
    statistics["total_harvested"] += 1
    
    # 治愈（如果需要）
    if cell_state != None and cell_state["infected"]:
        cure_plant_smart(x, y, crop_entity)
    
    # 重新种植
    plant_advanced(x, y, crop_entity)
    
    return True

# ====================
# 主循环
# ====================

def initialize_advanced_farm(world_size, default_crop):
    # 初始化高级农场
    # world_size: 世界大小
    # default_crop: 默认作物类型
    
    quick_print("初始化高级肥料农场")
    quick_print("农场大小：" + str(world_size) + "x" + str(world_size))
    
    # 初始化状态追踪
    init_farm_state(world_size)
    
    # 回到原点
    goto_pos(0, 0)
    
    # 遍历种植
    for y in range(world_size):
        for x in range(world_size):
            # 清理现有植物
            if can_harvest():
                harvest()
            # 种植
            plant_advanced(x, y, default_crop)
            move(East)
        move(North)
    
    quick_print("初始化完成")
    print_statistics()

def harvest_cycle_advanced(world_size, default_crop):
    # 高级收获循环
    # world_size: 世界大小
    # default_crop: 默认作物类型
    # 返回：本次收获数量
    
    harvest_count = 0
    
    goto_pos(0, 0)
    
    for y in range(world_size):
        for x in range(world_size):
            if harvest_advanced(x, y, default_crop):
                harvest_count += 1
            move(East)
        move(North)
    return harvest_count

def print_statistics():
    # 打印统计信息
    quick_print("=== 统计信息 ===")
    quick_print("循环次数：" + str(statistics["cycles_completed"]))
    quick_print("总收获：" + str(statistics["total_harvested"]))
    quick_print("使用肥料：" + str(statistics["total_fertilizer_used"]))
    quick_print("节省肥料：" + str(statistics["fertilizer_saved"]))
    quick_print("使用奇异物质：" + str(statistics["total_weird_substance_used"]))
    quick_print("库存：")
    quick_print("  木材：" + str(num_items(Items.Wood)))
    quick_print("  胡萝卜：" + str(num_items(Items.Carrot)))
    quick_print("  能量：" + str(num_items(Items.Power)))
    quick_print("  南瓜：" + str(num_items(Items.Pumpkin)))
    quick_print("  肥料：" + str(num_items(Items.Fertilizer)))
    quick_print("  奇异物质：" + str(num_items(Items.Weird_Substance)))

def run_advanced_farm(default_crop, cycles):
    # 运行高级农场
    # default_crop: 默认作物类型
    # cycles: 循环次数（-1为无限）
    
    world_size = get_world_size()
    
    quick_print("=====================")
    quick_print("高级肥料农场启动")
    quick_print("=====================")
    
    # 初始化
    initialize_advanced_farm(world_size, default_crop)
    
    # 主循环
    while cycles == -1 or statistics["cycles_completed"] < cycles:
        # 等待成熟
        quick_print("等待作物成熟...")
        do_a_flip()
        
        # 收获
        harvest_count = harvest_cycle_advanced(world_size, default_crop)
        statistics["cycles_completed"] += 1
        
        quick_print("循环 " + str(statistics["cycles_completed"]) + " 完成，收获 " + str(harvest_count))
        
        # 每5个循环显示一次详细统计
        if statistics["cycles_completed"] % 5 == 0:
            print_statistics()
    
    quick_print("=====================")
    quick_print("农场循环完成")
    print_statistics()

# ====================
# 主程序入口
# ====================

def quick_test_advanced():
    # 快速测试高级农场
    run_advanced_farm(Entities.Carrot, 3)

def infinite_farm_advanced():
    # 无限循环高级农场
    run_advanced_farm(Entities.Carrot, -1)

# 运行示例
set_world_size(5)
quick_test_advanced()

# 无限循环（取消注释）：
# infinite_farm_advanced()

