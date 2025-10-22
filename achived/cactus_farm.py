# 仙人掌农场 - 行列分离排序版
#
# 算法：行列分离的二维冒泡排序（Row-Column Separated Sorting）
# 
# 排序规则（重要！）：
# 一个仙人掌处于"已排序状态"当且仅当：
# - 所有 North 和 East 方向的相邻仙人掌尺寸 >= 它
# - 所有 South 和 West 方向的相邻仙人掌尺寸 <= 它
#
# 核心思路（新优化策略）：
# 1. 第一步：对每一行进行独立排序
#    - 每行内部从左到右（West -> East）递增
#    - 只检查和交换 East 方向的相邻仙人掌
#    - 每一行完全排序后再处理下一行
#
# 2. 第二步：对每一列进行独立排序
#    - 每列内部从下到上（South -> North）递增
#    - 只检查和交换 North 方向的相邻仙人掌
#    - 每一列完全排序后再处理下一列
#
# 3. 为什么这样更高效：
#    - 分治策略：将二维问题分解为多个一维问题
#    - 减少遍历：每行/列只需要遍历自己，不需要全局遍历
#    - 更少的交换：行排序不会打乱列，列排序不会打乱行
#    - 更清晰的进度：可以看到每行/列的完成情况
#
# 排序顺序：
# 行排序：确保每行内 West <= ... <= East
# 列排序：确保每列内 South <= ... <= North
# 结果：满足所有仙人掌连锁收割的条件
#
# 优势：
# - 更快的收敛速度
# - 更少的移动次数
# - 更易于调试和理解
# - 保证满足二维排序条件

# 导入通用工具库
from farm_utils import goto_origin, goto_pos, check_and_swap_direction, print_cactus_grid, verify_cactus_sorted, clear_field, get_world_size_debug

# ====================
# 配置区域
# ====================
# ====================
# 工具函数（已从farm_utils导入）
# ====================

def print_grid():
    # 打印整个网格的仙人掌值（调试用）
    size = get_world_size()
    print_cactus_grid(size)


def sort_rows():
    # 第一步：对每一行进行排序（从左到右递增）
    quick_print("=== 开始行排序（West -> East 递增） ===")
    
    size = get_world_size()
    total_swaps = 0
    pass_count = 0
    
    # 对每一行进行冒泡排序
    for y in range(size):
        quick_print("排序第", y, "行...")
        row_swaps = 0
        
        # 对当前行进行冒泡排序，直到没有交换
        while True:
            swapped = False
            pass_count += 1
            
            # 从左向右遍历这一行
            for x in range(size - 1):
                goto_pos(x, y)
                
                if get_entity_type() != Entities.Cactus:
                    continue
                
                curr_val = measure()
                
                # 检查 East 方向（右边）- 应该 >= 当前值
                if check_and_swap_direction(East, curr_val, True):
                    swapped = True
                    total_swaps += 1
                    row_swaps += 1
            
            # 如果这一行没有交换，说明已排序
            if not swapped:
                break
        
        quick_print("  第", y, "行排序完成，交换", row_swaps, "次")
    
    quick_print("=== 行排序完成 ===")
    quick_print("总交换次数:", total_swaps)
    quick_print("总遍历次数:", pass_count)
    
    return total_swaps

def sort_columns():
    # 第二步：对每一列进行排序（从下到上递增）
    quick_print("")
    quick_print("=== 开始列排序（South -> North 递增） ===")
    
    size = get_world_size()
    total_swaps = 0
    pass_count = 0
    
    # 对每一列进行冒泡排序
    for x in range(size):
        quick_print("排序第", x, "列...")
        col_swaps = 0
        
        # 对当前列进行冒泡排序，直到没有交换
        while True:
            swapped = False
            pass_count += 1
            
            # 从下向上遍历这一列
            for y in range(size - 1):
                goto_pos(x, y)
                
                if get_entity_type() != Entities.Cactus:
                    continue
                
                curr_val = measure()
                
                # 检查 North 方向（上边）- 应该 >= 当前值
                if check_and_swap_direction(North, curr_val, True):
                    swapped = True
                    total_swaps += 1
                    col_swaps += 1
            
            # 如果这一列没有交换，说明已排序
            if not swapped:
                break
        
        quick_print("  第", x, "列排序完成，交换", col_swaps, "次")
    
    quick_print("=== 列排序完成 ===")
    quick_print("总交换次数:", total_swaps)
    quick_print("总遍历次数:", pass_count)
    
    return total_swaps

def bubble_sort():
    # 优化的二维冒泡排序主函数
    # 新策略：先完成每行排序，再完成每列排序
    quick_print("=== 开始优化二维冒泡排序（行列分离版） ===")
    
    tick_start = get_tick_count()
    
    size = get_world_size()
    
    quick_print("农场大小:", size, "x", size)
    quick_print("总位置数:", size * size)
    
    # 打印排序前的网格（调试用）
    quick_print("")
    quick_print("排序前：")
    print_grid()
    
    # 第一步：行排序
    quick_print("")
    tick_rows = get_tick_count()
    row_swaps = sort_rows()
    tick_rows = get_tick_count() - tick_rows
    
    # 打印行排序后的网格
    quick_print("")
    quick_print("行排序后：")
    print_grid()
    
    # 第二步：列排序
    quick_print("")
    tick_cols = get_tick_count()
    col_swaps = sort_columns()
    tick_cols = get_tick_count() - tick_cols
    
    total_ticks = get_tick_count() - tick_start
    total_swaps = row_swaps + col_swaps
    
    # 打印最终排序后的网格（调试用）
    quick_print("")
    quick_print("最终排序后：")
    print_grid()
   
    
    quick_print("")
    quick_print("=== 二维冒泡排序完成 ===")
    quick_print("行排序交换:", row_swaps, "次，耗时", tick_rows, "ticks")
    quick_print("列排序交换:", col_swaps, "次，耗时", tick_cols, "ticks")
    quick_print("总交换次数:", total_swaps)
    quick_print("总计:", total_ticks, "ticks")

def plant_cacti():
    # 种植仙人掌
    size = get_world_size()
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
    size = get_world_size()
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
quick_print("仙人掌农场 - 行列分离排序版")
quick_print("算法: 行列分离的二维冒泡排序")
quick_print("策略: 先完成所有行排序")
quick_print("      再完成所有列排序")
quick_print("优势: 分治策略，更快收敛")
quick_print("=============================")
quick_print("")

# 初始化世界大小（会自动设置调试大小）
world_size = get_world_size()
quick_print("当前农场大小:", world_size, "x", world_size)

quick_print("")
clear()

# 主循环
while True:
    run_cycle()

