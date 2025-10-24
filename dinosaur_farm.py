# ============================================
# 恐龙脚本 - 获取远古骨头
# ============================================
# 功能：
# 1. 装备恐龙帽，通过吃苹果增长尾巴
# 2. 支持自定义目标长度
# 3. 统计效率（骨头数量、tick消耗、每骨头tick成本）
# 4. 使用哈密尔顿路径遍历农场
# ============================================

# ============================================
# 配置区域
# ============================================

# 目标尾巴长度（建议值：10, 20, 36, 64, 100）
TARGET_LENGTH = 36  # 默认36（6x6农场）

# 是否打印详细日志
VERBOSE = True

# ============================================
# 全局变量
# ============================================

total_ticks_used = 0
start_tick = 0
bones_collected = 0
apples_eaten = 0

# ============================================
# 效率统计函数
# ============================================

def calculate_move_ticks(apples):
    # 计算吃掉指定数量苹果后，每次移动消耗的ticks
    ticks = 400
    for i in range(apples):
        ticks -= ticks * 0.03 // 1
    return ticks

def calculate_bones(length):
    # 计算指定长度的尾巴能获得的骨头数量
    return length * length

def print_efficiency_table():
    # 打印不同长度的效率表
    quick_print("=============")
    quick_print("恐龙效率统计表")
    quick_print("=============")
    quick_print("长度 | 骨头数 | 移动成本(ticks) | 预计总ticks | 每骨头ticks")
    
    for length in [10, 16, 20, 25, 36, 49, 64, 81, 100]:
        bones = calculate_bones(length)
        final_move_ticks = calculate_move_ticks(length)
        # 估算总ticks：初期400ticks移动 + 后期优化移动
        # 简化估算：平均移动成本约为 (400 + final_move_ticks) / 2
        avg_move_ticks = (400 + final_move_ticks) // 2
        estimated_total_ticks = length * avg_move_ticks
        if bones > 0:
          ticks_per_bone = estimated_total_ticks // bones
        else:
            ticks_per_bone = 0
        
        quick_print(str(length) + " | " + 
                   str(bones) + " | " + 
                   str(final_move_ticks) + " | " + 
                   str(estimated_total_ticks) + " | " + 
                   str(ticks_per_bone))
    
    quick_print("=============")

# ============================================
# 核心功能函数
# ============================================

def prepare_farm():
    # 准备农场：清空所有植物以确保苹果可以生成
    quick_print("准备农场...")
    size = get_world_size()
    
    for y in range(size):
        for x in range(size):
            # 收割任何植物
            if get_entity_type() != None:
                if can_harvest():
                    harvest()
            
            # 移动到下一个位置（蛇形）
            if x < size - 1:
                if y % 2 == 0:
                    move(East)
                else:
                    move(West)
        
        # 移动到下一行
        if y < size - 1:
            move(North)
    
    quick_print("农场准备完成")

def find_apple_position():
    # 获取下一个苹果的位置
    if get_entity_type() == Entities.Apple:
        return measure()
    return None

def navigate_to_position(target_x, target_y):
    # 导航到指定位置
    # 使用简单的曼哈顿距离导航
    current_x = get_pos_x()
    current_y = get_pos_y()
    
    moves = 0
    
    # 先移动X轴
    while current_x != target_x:
        if current_x < target_x:
            if move(East):
                moves += 1
                current_x = get_pos_x()
            else:
                # 被尾巴挡住，尝试绕路
                if move(North):
                    moves += 1
                    current_y = get_pos_y()
                elif move(South):
                    moves += 1
                    current_y = get_pos_y()
                else:
                    return False  # 无法移动
        else:
            if move(West):
                moves += 1
                current_x = get_pos_x()
            else:
                # 被尾巴挡住，尝试绕路
                if move(North):
                    moves += 1
                    current_y = get_pos_y()
                elif move(South):
                    moves += 1
                    current_y = get_pos_y()
                else:
                    return False
    
    # 再移动Y轴
    while current_y != target_y:
        if current_y < target_y:
            if move(North):
                moves += 1
                current_y = get_pos_y()
            else:
                # 被尾巴挡住，尝试绕路
                if move(East):
                    moves += 1
                    current_x = get_pos_x()
                elif move(West):
                    moves += 1
                    current_x = get_pos_x()
                else:
                    return False
        else:
            if move(South):
                moves += 1
                current_y = get_pos_y()
            else:
                # 被尾巴挡住，尝试绕路
                if move(East):
                    moves += 1
                    current_x = get_pos_x()
                elif move(West):
                    moves += 1
                    current_x = get_pos_x()
                else:
                    return False
    
    return True

def grow_tail_to_length(target_length):
    # 增长尾巴到指定长度
    global apples_eaten
    
    quick_print("开始吃苹果，目标长度: " + str(target_length))
    
    current_length = 0
    
    while current_length < target_length:
        # 检查是否有苹果在当前位置
        if get_entity_type() == Entities.Apple:
            # 获取下一个苹果位置
            apple_pos = measure()
            next_x = apple_pos[0]
            next_y = apple_pos[1]
            
            # 导航到苹果
            if navigate_to_position(next_x, next_y):
                # 成功到达苹果位置
                current_length += 1
                apples_eaten += 1
                
                if VERBOSE and current_length % 5 == 0:
                    move_ticks = calculate_move_ticks(apples_eaten)
                    quick_print("已吃苹果: " + str(current_length) + "/" + 
                               str(target_length) + 
                               " | 移动成本: " + str(move_ticks) + " ticks")
            else:
                quick_print("警告: 无法到达苹果位置，尾巴可能卡住了")
                break
        else:
            # 当前位置没有苹果，寻找苹果
            size = get_world_size()
            found = False
            
            for y in range(size):
                for x in range(size):
                    if get_entity_type() == Entities.Apple:
                        found = True
                        apple_pos = measure()
                        if navigate_to_position(apple_pos[0], apple_pos[1]):
                            current_length += 1
                            apples_eaten += 1
                        break
                    
                    # 尝试移动到下一个位置
                    if x < size - 1:
                        if y % 2 == 0:
                            if not move(East):
                                break
                        else:
                            if not move(West):
                                break
                
                if found:
                    break
                
                if y < size - 1:
                    if not move(North):
                        break
            
            if not found:
                quick_print("错误: 找不到苹果")
                break
    
    quick_print("尾巴增长完成! 最终长度: " + str(current_length))
    return current_length

def check_cactus_inventory():
    # 检查仙人掌库存
    cactus_count = num_items(Items.Cactus)
    quick_print("当前仙人掌数量: " + str(cactus_count))
    
    # 每个苹果需要消耗的仙人掌数量（根据游戏设定调整）
    # 假设每个苹果需要1个仙人掌
    needed = TARGET_LENGTH
    
    if cactus_count < needed:
        quick_print("警告: 仙人掌不足! 需要 " + str(needed) + "，但只有 " + str(cactus_count))
        return False
    
    return True

# ============================================
# 主函数
# ============================================

def run_dinosaur_farm():
    global start_tick
    global total_ticks_used
    global bones_collected
    
    # 打印效率表
    print_efficiency_table()
    
    # 记录开始时间
    start_tick = get_tick_count()
    quick_print("开始恐龙养殖...")
    quick_print("目标长度: " + str(TARGET_LENGTH))
    
    # 检查仙人掌库存
    if not check_cactus_inventory():
        quick_print("仙人掌不足，停止执行")
        return
    
    # 装备恐龙帽
    quick_print("装备恐龙帽...")
    change_hat(Hats.Dinosaur_Hat)
    quick_print("恐龙帽已装备")
    
    # 增长尾巴
    final_length = grow_tail_to_length(TARGET_LENGTH)
    
    # 卸下恐龙帽，收获骨头
    quick_print("卸下恐龙帽，收获骨头...")
    change_hat(Hats.Brown_Hat)
    
    # 计算收获
    bones_collected = calculate_bones(final_length)
    total_ticks_used = get_tick_count() - start_tick
    
    # 打印统计
    quick_print("=============")
    quick_print("恐龙养殖完成!")
    quick_print("=============")
    quick_print("尾巴长度: " + str(final_length))
    quick_print("吃掉苹果: " + str(apples_eaten))
    quick_print("收获骨头: " + str(bones_collected))
    quick_print("总消耗ticks: " + str(total_ticks_used))
    
    if bones_collected > 0:
        ticks_per_bone = total_ticks_used // bones_collected
        quick_print("每骨头成本: " + str(ticks_per_bone) + " ticks")
        
        # 计算效率评级
        if ticks_per_bone < 500:
            quick_print("效率评级: ⭐⭐⭐⭐⭐ 优秀!")
        elif ticks_per_bone < 1000:
            quick_print("效率评级: ⭐⭐⭐⭐ 良好")
        elif ticks_per_bone < 2000:
            quick_print("效率评级: ⭐⭐⭐ 一般")
        else:
            quick_print("效率评级: ⭐⭐ 需要优化")
    
    quick_print("=============")
    quick_print("当前骨头总数: " + str(num_items(Items.Bone)))
    quick_print("=============")

# ============================================
# 执行
# ============================================

# 运行恐龙养殖
run_dinosaur_farm()
