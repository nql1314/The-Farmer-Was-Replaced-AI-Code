# TFWR 肥料高效农场
# 优化策略：使用肥料加速生长慢的作物
# 特点：
# 1. 使用肥料缩短生长时间（-2秒）
# 2. 管理植物感染状态
# 3. 利用奇异物质治愈感染植物
# 4. 支持多种作物类型

# 导入通用工具函数
from farm_utils import goto_pos, goto_origin

# ====================
# 配置参数
# ====================

# 农场模式选择
# "tree" - 树（生长7秒，肥料后5秒，产木材）
# "carrot" - 胡萝卜（生长6秒，肥料后4秒，产胡萝卜）
# "sunflower" - 向日葵（生长5秒，肥料后3秒，产能量）
# "pumpkin" - 南瓜（生长2秒，肥料后0秒，但有合并机制）
CROP_MODE = "tree"

# 是否使用肥料
USE_FERTILIZER = True

# 是否治愈感染（使用奇异物质）
CURE_INFECTION = True

# 治愈策略
# "after_harvest" - 收获后立即治愈
# "batch" - 批量治愈（收集足够奇异物质后统一治愈）
# "none" - 不治愈（接受50%产量损失）
CURE_STRATEGY = "batch"

# 批量治愈的奇异物质阈值
WEIRD_SUBSTANCE_THRESHOLD = 100

# 是否使用水
USE_WATER = True
WATER_THRESHOLD = 0.75

# ====================
# 作物配置
# ====================

def get_crop_config(mode):
    # 获取作物配置
    # mode: 作物模式
    # 返回：(实体类型, 基础生长时间, 产物名称)
    
    if mode == "tree":
        return Entities.Tree, 7, "木材"
    elif mode == "carrot":
        return Entities.Carrot, 6, "胡萝卜"
    elif mode == "sunflower":
        return Entities.Sunflower, 5, "能量"
    elif mode == "pumpkin":
        return Entities.Pumpkin, 2, "南瓜"
    else:
        # 默认使用树
        return Entities.Tree, 7, "木材"

# ====================
# 感染管理函数
# ====================

def is_infected():
    # 检测当前植物是否被感染
    # 注意：游戏中可能没有直接检测感染状态的API
    # 这里使用measure()的返回值来判断（需要测试）
    # 如果measure()对感染植物返回特殊值，可以用来判断
    # 返回：True表示可能感染，False表示可能健康
    
    # 简化策略：假设使用过肥料的植物都被感染
    # 实际游戏中可能需要其他方法判断
    return False  # 暂时返回False，后续可以改进

def cure_plant():
    # 治愈当前位置的植物（移除感染状态）
    # 使用奇异物质
    
    if num_items(Items.Weird_Substance) > 0:
        use_item(Items.Weird_Substance)
        return True
    return False

def cure_all_plants(world_size):
    # 治愈整个农场的所有植物
    # world_size: 世界大小
    
    if num_items(Items.Weird_Substance) == 0:
        quick_print("没有奇异物质，无法治愈")
        return
    
    quick_print("开始批量治愈感染植物")
    cure_count = 0
    
    for y in range(world_size):
        for x in range(world_size):
            # 如果有作物且有奇异物质
            if get_entity_type() != None and num_items(Items.Weird_Substance) > 0:
                use_item(Items.Weird_Substance)
                cure_count += 1
            
            # 移动到下一个位置
            if x < world_size - 1:
                if y % 2 == 0:
                    move(East)
                else:
                    move(West)
        
        if y < world_size - 1:
            move(North)
    
    quick_print("治愈完成，处理了 " + str(cure_count) + " 个位置")

# ====================
# 种植和收获函数
# ====================

def plant_with_fertilizer(crop_entity):
    # 种植并立即使用肥料
    # crop_entity: 作物实体类型
    
    # 确保土壤
    if get_ground_type() != Grounds.Soil:
        till()
    
    # 种植
    plant(crop_entity)
    
    # 使用肥料
    if USE_FERTILIZER and num_items(Items.Fertilizer) > 0:
        use_item(Items.Fertilizer)
        return True
    
    return False

def harvest_and_replant(crop_entity, use_cure):
    # 收获并重新种植
    # crop_entity: 作物实体类型
    # use_cure: 是否治愈
    # 返回：是否成功收获
    
    harvested = False
    
    # 收获
    if can_harvest():
        harvest()
        harvested = True
    
    # 治愈（如果需要且有奇异物质）
    if use_cure and CURE_STRATEGY == "after_harvest" and num_items(Items.Weird_Substance) > 0:
        use_item(Items.Weird_Substance)
    
    # 重新种植
    if get_ground_type() != Grounds.Soil:
        till()
    
    plant(crop_entity)
    
    # 使用肥料
    if USE_FERTILIZER and num_items(Items.Fertilizer) > 0:
        use_item(Items.Fertilizer)
    
    return harvested

# ====================
# 农场循环函数
# ====================

def initialize_farm(world_size, crop_entity):
    # 初始化农场：清空并种植所有位置
    # world_size: 世界大小
    # crop_entity: 作物实体类型
    
    quick_print("初始化农场，种植 " + str(world_size * world_size) + " 个作物")
    
    goto_pos(0, 0)
    
    for y in range(world_size):
        for x in range(world_size):
            # 清理现有植物
            if can_harvest():
                harvest()
            
            # 浇水（如果需要）
            if USE_WATER and get_water() < WATER_THRESHOLD and num_items(Items.Water) > 0:
                use_item(Items.Water)
            
            # 种植并施肥
            plant_with_fertilizer(crop_entity)
            
            # 移动到下一个位置
            if x < world_size - 1:
                if y % 2 == 0:
                    move(East)
                else:
                    move(West)
        
        if y < world_size - 1:
            move(North)
    
    quick_print("初始化完成")

def harvest_cycle(world_size, crop_entity):
    # 收获循环：遍历农场收获成熟的作物
    # world_size: 世界大小
    # crop_entity: 作物实体类型
    # 返回：收获数量
    
    harvest_count = 0
    
    goto_pos(0, 0)
    
    for y in range(world_size):
        for x in range(world_size):
            # 浇水（如果需要）
            if USE_WATER and get_water() < WATER_THRESHOLD and num_items(Items.Water) > 0:
                use_item(Items.Water)
            
            # 收获并重新种植
            if harvest_and_replant(crop_entity, CURE_INFECTION):
                harvest_count += 1
            
            # 移动到下一个位置
            if x < world_size - 1:
                if y % 2 == 0:
                    move(East)
                else:
                    move(West)
        
        if y < world_size - 1:
            move(North)
    
    return harvest_count

def run_fertilizer_farm(cycles):
    # 运行肥料农场主循环
    # cycles: 循环次数（如果为-1则无限循环）
    
    world_size = get_world_size()
    crop_entity, base_grow_time, product_name = get_crop_config(CROP_MODE)
    
    quick_print("====================")
    quick_print("肥料农场启动")
    quick_print("作物类型：" + CROP_MODE + " (" + product_name + ")")
    quick_print("基础生长时间：" + str(base_grow_time) + "秒")
    quick_print("使用肥料：" + str(USE_FERTILIZER))
    quick_print("治愈策略：" + CURE_STRATEGY)
    quick_print("农场大小：" + str(world_size) + "x" + str(world_size))
    quick_print("====================")
    
    # 初始化农场
    initialize_farm(world_size, crop_entity)
    
    # 主循环
    cycle_count = 0
    total_harvested = 0
    
    while cycles == -1 or cycle_count < cycles:
        cycle_count += 1
        
        # 等待作物生长
        quick_print("等待作物成熟...")
        do_a_flip()
        
        # 收获循环
        harvested = harvest_cycle(world_size, crop_entity)
        total_harvested += harvested
        
        # 显示统计
        quick_print("循环 " + str(cycle_count) + " 完成")
        quick_print("本次收获：" + str(harvested))
        quick_print("累计收获：" + str(total_harvested))
        
        # 显示库存
        quick_print("库存状态：")
        if CROP_MODE == "tree":
            quick_print("  木材：" + str(num_items(Items.Wood)))
        elif CROP_MODE == "carrot":
            quick_print("  胡萝卜：" + str(num_items(Items.Carrot)))
        elif CROP_MODE == "sunflower":
            quick_print("  能量：" + str(num_items(Items.Power)))
        elif CROP_MODE == "pumpkin":
            quick_print("  南瓜：" + str(num_items(Items.Pumpkin)))
        
        quick_print("  肥料：" + str(num_items(Items.Fertilizer)))
        quick_print("  奇异物质：" + str(num_items(Items.Weird_Substance)))
        
        # 批量治愈（如果需要）
        if CURE_STRATEGY == "batch" and num_items(Items.Weird_Substance) >= WEIRD_SUBSTANCE_THRESHOLD:
            cure_all_plants(world_size)
        
        quick_print("---")
    
    quick_print("农场循环完成")
    quick_print("总计收获：" + str(total_harvested))

# ====================
# 快速测试函数
# ====================

def quick_test():
    # 快速测试：运行3个循环
    run_fertilizer_farm(3)

def infinite_farm():
    # 无限循环农场
    run_fertilizer_farm(-1)

# ====================
# 主程序入口
# ====================

# 运行示例：快速测试
quick_test()

# 如果需要无限循环，取消注释下面这行：
# infinite_farm()

