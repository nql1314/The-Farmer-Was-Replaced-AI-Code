# 仙人掌农场 - 优化二维冒泡排序版
#
# 算法：优化的二维冒泡排序（Optimized 2D Bubble Sort）
# 
# 排序规则（重要！）：
# 一个仙人掌处于"已排序状态"当且仅当：
# - 所有 North 和 East 方向的相邻仙人掌尺寸 >= 它
# - 所有 South 和 West 方向的相邻仙人掌尺寸 <= 它
#
# 核心思路：
# 1. 这是二维网格排序，不是线性蛇形路径排序
# 2. 从左下角(0,0)向右(East)和向上(North)递增
# 3. 遍历每个位置，检查其四个方向的相邻仙人掌
# 4. 如果发现违反排序规则的，进行交换
# 5. 重复直到没有交换发生（所有位置都满足排序条件）
#
# 检查方向：
# - South(下): 应该 <= 当前值
# - West(左): 应该 <= 当前值  
# - North(上): 应该 >= 当前值
# - East(右): 应该 >= 当前值
#
# 优化策略：
# 1. 记录最后交换位置 - 该位置之后的区域已部分排序
# 2. 动态缩小遍历范围 - 只遍历可能未排序的区域
# 3. 提前终止 - 当没有交换发生时立即完成排序
#
# 优势：正确实现二维排序，满足仙人掌的连锁收割条件，优化后减少移动次数

# 导入通用工具库
from farm_utils import goto_origin, goto_pos, check_and_swap_direction, print_cactus_grid, verify_cactus_sorted, clear_field, get_world_size_debug

# ====================
# 配置区域
# ====================

# 调试用的自定义农场大小（设为None则使用实际大小）
DEBUG_WORLD_SIZE = None

def get_world_size_custom():
    # 获取自定义的世界大小
    # 如果DEBUG_WORLD_SIZE不为None且解锁了Debug_2，则使用自定义大小
    # 否则返回实际的世界大小
    return get_world_size_debug(DEBUG_WORLD_SIZE)

# ====================
# 工具函数（已从farm_utils导入）
# ====================

def print_grid():
    # 打印整个网格的仙人掌值（调试用）
    size = get_world_size_custom()
    print_cactus_grid(size)


def bubble_sort():
    # 优化的二维冒泡排序主函数
    # 优化策略：记录最后交换位置，缩小遍历范围
    quick_print("=== 开始优化二维冒泡排序 ===")
    
    tick_start = get_tick_count()
    
    size = get_world_size_custom()
    
    quick_print("农场大小:", size, "x", size)
    quick_print("总位置数:", size * size)
    
    # 打印排序前的网格（调试用）
    quick_print("")
    quick_print("排序前：")
    print_grid()
    
    total_swaps = 0
    pass_count = 0
    
    # 已排序的边界
    # 初始时整个区域未排序
    max_x = size - 1
    max_y = size - 1
    
    # 优化的二维冒泡排序：反复遍历直到没有交换
    while True:
        swapped = False
        pass_count += 1
        
        # 记录本次遍历中最后发生交换的位置
        last_swap_x = 0
        last_swap_y = 0
        
        quick_print("")
        quick_print("--- 第", pass_count, "次遍历 ---")
        quick_print("遍历范围: x[0,", max_x, "], y[0,", max_y, "]")
        
        # 只遍历未排序的区域
        for y in range(max_y + 1):
            for x in range(max_x + 1):
                # 移动到当前位置
                goto_pos(x, y)
                
                # 只处理仙人掌位置
                if get_entity_type() != Entities.Cactus:
                    continue
                
                curr_val = measure()
                local_swapped = False
                
                # 检查四个方向的相邻仙人掌
                # 1. South(下) - 应该 <= 当前值
                if y > 0:
                    if check_and_swap_direction(South, curr_val, False):
                        local_swapped = True
                        total_swaps += 1
                
                # 2. West(左) - 应该 <= 当前值
                if x > 0:
                    if check_and_swap_direction(West, curr_val, False):
                        local_swapped = True
                        total_swaps += 1
                
                # 3. North(上) - 应该 >= 当前值
                if y < size - 1:
                    if check_and_swap_direction(North, curr_val, True):
                        local_swapped = True
                        total_swaps += 1
                
                # 4. East(右) - 应该 >= 当前值
                if x < size - 1:
                    if check_and_swap_direction(East, curr_val, True):
                        local_swapped = True
                        total_swaps += 1
                
                # 如果这个位置发生了交换，记录位置
                if local_swapped:
                    swapped = True
                    last_swap_x = max(last_swap_x, x)
                    last_swap_y = max(last_swap_y, y)
                
                if total_swaps % 20 == 0 and total_swaps > 0:
                    quick_print("  已交换", total_swaps, "次...")
        
        quick_print("第", pass_count, "次遍历完成")
        quick_print("  总交换:", total_swaps, "次")
        
        # 如果没有交换发生，排序完成
        if not swapped:
            quick_print("没有交换发生，排序完成！")
            break
        
        # 优化：更新已排序边界
        # 最后交换位置之后的区域已经排序好了
        # 但要确保至少检查到有交换的位置附近
        max_x = min(last_swap_x + 2, size - 1)
        max_y = min(last_swap_y + 2, size - 1)
        
        quick_print("  最后交换位置: (", last_swap_x, ",", last_swap_y, ")")
        quick_print("  新遍历范围: x[0,", max_x, "], y[0,", max_y, "]")
    
    total_ticks = get_tick_count() - tick_start
    
    # 打印排序后的网格（调试用）
    quick_print("")
    quick_print("排序后：")
    print_grid()
   
    
    quick_print("")
    quick_print("=== 二维冒泡排序完成 ===")
    quick_print("总遍历次数:", pass_count)
    quick_print("总交换次数:", total_swaps)
    quick_print("总计:", total_ticks, "ticks")

def plant_cacti():
    # 种植仙人掌
    size = get_world_size_custom()
    goto_origin()
    
    planted = 0
    for y in range(size):
        for x in range(size):
            if get_ground_type() != Grounds.Soil:
                till()
            
            entity = get_entity_type()
            if entity != Entities.Cactus:
                if entity != None:
                    harvest()
                plant(Entities.Cactus)
                planted += 1
            
            if x < size - 1:
                if y % 2 == 0:
                    move(East)
                else:
                    move(West)
        
        if y < size - 1:
            move(North)
    
    quick_print("种植完成:", planted, "个仙人掌")

def harvest_all():
    # 收割仙人掌
    size = get_world_size_custom()
    goto_origin()
    
    count_before = num_items(Items.Cactus)
    
    # 从左下角开始收割（位置0,0）
    if can_harvest():
        harvest()
    
    count_after = num_items(Items.Cactus)
    gained = count_after - count_before
    
    expected_max = size * size
    expected_chain = expected_max * expected_max
    
    quick_print("首次收割获得:", gained, "个仙人掌")
    
    if gained >= expected_chain:
        quick_print("完美！触发完整连锁反应")
    else:
        quick_print("连锁效果:", gained, "/", expected_chain, "（", gained * 100 // expected_chain, "%）")
        
        # 收割剩余的
        quick_print("收割剩余仙人掌...")
        for y in range(size):
            for x in range(size):
                goto_pos(x, y)
                if can_harvest():
                    harvest()
    
    final_count = num_items(Items.Cactus)
    total_gained = final_count - count_before
    quick_print("总收获:", total_gained, "个仙人掌")

def run_cycle():
    # 运行完整周期
    tick_start = get_tick_count()
    cactus_start = num_items(Items.Cactus)
    
    quick_print("")
    quick_print("==========================")
    quick_print("仙人掌周期开始（冒泡版）")
    quick_print("==========================")
    
    # 种植
    quick_print("")
    quick_print(">>> 阶段1: 种植")
    tick_phase = get_tick_count()
    plant_cacti()
    tick_plant = get_tick_count() - tick_phase
    quick_print("种植耗时:", tick_plant, "ticks")
    
    # 排序（会自动等待成熟）
    quick_print("")
    quick_print(">>> 阶段2: 优化二维冒泡排序")
    quick_print("排序直到没有交换发生...")
    tick_phase = get_tick_count()
    bubble_sort()
    tick_sort = get_tick_count() - tick_phase
    quick_print("排序耗时:", tick_sort, "ticks")
    
    # 收割（排序完成后立即收割）
    quick_print("")
    quick_print(">>> 阶段3: 收割")
    quick_print("从左下角触发连锁反应...")
    tick_phase = get_tick_count()
    harvest_all()
    tick_harvest = get_tick_count() - tick_phase
    quick_print("收割耗时:", tick_harvest, "ticks")
    
    # 统计
    total_ticks = get_tick_count() - tick_start
    cactus_gained = num_items(Items.Cactus) - cactus_start
    
    quick_print("")
    quick_print("==========================")
    quick_print("周期完成")
    quick_print("==========================")
    quick_print("阶段1 种植:", tick_plant, "ticks")
    quick_print("阶段2 排序:", tick_sort, "ticks")
    quick_print("阶段3 收割:", tick_harvest, "ticks")
    quick_print("--------------------------")
    quick_print("总计:", total_ticks, "ticks")
    quick_print("获得:", cactus_gained, "个仙人掌")
    quick_print("总数:", num_items(Items.Cactus))
    quick_print("==========================")
    quick_print("")

# 初始化
quick_print("=============================")
quick_print("仙人掌农场 - 优化二维冒泡排序版")
quick_print("算法: 优化的二维网格冒泡排序")
quick_print("特点: 记录端点边界，减少遍历范围")
quick_print("      没有交换时完成排序并收割")
quick_print("=============================")
quick_print("")

# 初始化世界大小（会自动设置调试大小）
world_size = get_world_size_custom()
quick_print("当前农场大小:", world_size, "x", world_size)

quick_print("")
quick_print("初始化：清空农场")
clear_field(world_size)

# 主循环
while True:
    run_cycle()

