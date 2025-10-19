# TFWR 农场通用工具库
# 包含所有脚本文件共用的辅助函数

# ====================
# 移动和导航函数
# ====================

def goto_origin():
    # 回到原点(0,0)
    while get_pos_x() > 0:
        move(West)
    while get_pos_y() > 0:
        move(South)

def goto_pos(target_x, target_y):
    # 移动到指定位置
    # 先移动x轴，再移动y轴
    while get_pos_x() < target_x:
        move(East)
    while get_pos_x() > target_x:
        move(West)
    while get_pos_y() < target_y:
        move(North)
    while get_pos_y() > target_y:
        move(South)

# ====================
# 路径生成函数
# ====================

def generate_snake_path(size):
    # 生成蛇形路径坐标列表
    # 奇数行从左到右，偶数行从右到左
    path = []
    for y in range(size):
        if y % 2 == 0:
            # 偶数行：从左到右
            for x in range(size):
                path.append((x, y))
        else:
            # 奇数行：从右到左
            for x in range(size - 1, -1, -1):
                path.append((x, y))
    return path

# ====================
# 路径优化函数
# ====================

def optimize_path(positions, start_x, start_y):
    # 使用贪心最近邻算法优化路径
    # 从起始位置开始，每次选择最近的未访问位置
    if len(positions) == 0:
        return []
    
    optimized = []
    remaining = []
    for pos in positions:
        remaining.append(pos)
    
    current_x = start_x
    current_y = start_y
    
    while len(remaining) > 0:
        # 找到距离当前位置最近的点
        min_dist = 999999
        min_idx = 0
        
        for i in range(len(remaining)):
            # 支持2元组 (x, y) 和3元组 (x, y, extra)
            x = remaining[i][0]
            y = remaining[i][1]
            dist = abs(x - current_x) + abs(y - current_y)
            if dist < min_dist:
                min_dist = dist
                min_idx = i
        
        # 移动到最近的点
        closest = remaining[min_idx]
        optimized.append(closest)
        current_x = closest[0]
        current_y = closest[1]
        
        # 从剩余列表中移除
        new_remaining = []
        for i in range(len(remaining)):
            if i != min_idx:
                new_remaining.append(remaining[i])
        remaining = new_remaining
    
    return optimized

# ====================
# 浇水相关函数
# ====================

def check_and_water(water_threshold):
    # 检查水量并浇水
    # water_threshold: 水量阈值，低于此值时浇水
    # 返回：是否浇水
    water_level = get_water()
    if water_level < water_threshold:
        if num_items(Items.Water) > 0:
            use_item(Items.Water)
            quick_print("浇水：水量从 " + str(water_level) + " 提升")
            return True
    return False

# ====================
# 胡萝卜补充函数
# ====================

def refill_carrots_generic(target_count, world_size, snake_path):
    # 通用的胡萝卜补充函数
    # target_count: 目标胡萝卜数量
    # world_size: 世界大小
    # snake_path: 蛇形路径（可选，如果为None则自动生成）
    quick_print("补充胡萝卜到" + str(target_count))
    
    if snake_path == None:
        snake_path = generate_snake_path(world_size)
    
    while num_items(Items.Carrot) < target_count:
        for i in range(len(snake_path)):
            x, y = snake_path[i]
            
            if can_harvest():
                harvest()
            
            if get_ground_type() != Grounds.Soil:
                till()
            
            plant(Entities.Carrot)
            
            if get_water() < 0.5 and num_items(Items.Water) > 0:
                use_item(Items.Water)
            
            if i < len(snake_path) - 1:
                next_x, next_y = snake_path[i + 1]
                goto_pos(next_x, next_y)
        
        do_a_flip()
    
    quick_print("胡萝卜：" + str(num_items(Items.Carrot)))

# ====================
# 南瓜相关函数
# ====================

def check_mega_pumpkin_formed(pumpkin_size):
    # 检测是否已形成巨型南瓜
    # pumpkin_size: 巨型南瓜的边长
    # 返回：是否已形成
    
    # 检查对角线两端：(0,0) 和 (size-1, size-1)
    goto_pos(0, 0)
    entity1 = get_entity_type()
    if entity1 != Entities.Pumpkin:
        return False
    
    id1 = measure()
    if id1 == None:
        return False
    
    goto_pos(pumpkin_size - 1, pumpkin_size - 1)
    entity2 = get_entity_type()
    if entity2 != Entities.Pumpkin:
        return False
    
    id2 = measure()
    if id2 == None:
        return False
    
    # ID相同说明已形成巨型南瓜
    return id1 == id2

def harvest_mega_pumpkin(pumpkin_size):
    # 收获巨型南瓜
    # pumpkin_size: 巨型南瓜的边长
    # 返回：是否成功收获
    quick_print("收获" + str(pumpkin_size) + "x" + str(pumpkin_size) + "巨型南瓜")
    
    before_count = num_items(Items.Pumpkin)
    
    # 移动到(0,0)收获
    goto_pos(0, 0)
    
    if can_harvest():
        # 获取ID用于显示
        pumpkin_id = measure()
        
        harvest()
        
        after_count = num_items(Items.Pumpkin)
        gained = after_count - before_count
        
        quick_print("收获巨型南瓜 ID:" + str(pumpkin_id))
        quick_print("+" + str(gained) + " 个南瓜，总计:" + str(after_count))
        return True
    else:
        quick_print("警告：无法收获，可能还未完全成熟")
        return False

# ====================
# 仙人掌相关函数
# ====================

def check_and_swap_direction(direction, curr_val, should_be_greater):
    # 检查某个方向的仙人掌，如果不符合排序条件则交换
    # direction: 要检查的方向
    # curr_val: 当前仙人掌的值
    # should_be_greater: True表示该方向应该>=当前值，False表示应该<=当前值
    # 返回：是否进行了交换
    
    neighbor_val = measure(direction)
    
    # 检查是否违反排序规则
    if should_be_greater:
        # North/East方向应该 >= 当前值
        if neighbor_val < curr_val:
            swap(direction)
            return True
    else:
        # South/West方向应该 <= 当前值
        if neighbor_val > curr_val:
            swap(direction)
            return True
    
    return False

def print_cactus_grid(world_size):
    # 打印整个网格的仙人掌值（调试用）
    # world_size: 世界大小
    
    # 只在小农场时打印
    if world_size > 10:
        quick_print("农场太大，跳过网格打印")
        return
    
    quick_print("仙人掌网格状态：")
    
    # 从上到下打印（y从大到小），这样显示更直观
    for y in range(world_size - 1, -1, -1):
        row = []
        for x in range(world_size):
            goto_pos(x, y)
            if get_entity_type() == Entities.Cactus:
                val = measure()
                row.append(str(val))
            else:
                row.append(".")
        
        # 打印行号和内容
        line = "y=" + str(y) + ": " + " "+ str(row)
        quick_print(line)
    
    # 打印x轴标签
    x_labels = "    "
    for x in range(world_size):
        x_labels += str(x) + " "
    quick_print(x_labels)

def verify_cactus_sorted(world_size):
    # 验证整个网格是否已正确排序
    # world_size: 世界大小
    # 返回：(是否已排序, 不满足条件的位置数量)
    
    unsorted_count = 0
    
    for y in range(world_size):
        for x in range(world_size):
            goto_pos(x, y)
            
            if get_entity_type() != Entities.Cactus:
                continue
            
            curr_val = measure()
            
            # 检查四个方向
            if y > 0:
                south_val = measure(South)
                if south_val > curr_val:
                    unsorted_count += 1
            
            if x > 0:
                west_val = measure(West)
                if west_val > curr_val:
                    unsorted_count += 1
            
            if y < world_size - 1:
                north_val = measure(North)
                if north_val < curr_val:
                    unsorted_count += 1
            
            if x < world_size - 1:
                east_val = measure(East)
                if east_val < curr_val:
                    unsorted_count += 1
    
    return unsorted_count == 0, unsorted_count

# ====================
# 田地清理函数
# ====================

def clear_field(world_size):
    # 清空农场
    # world_size: 世界大小
    goto_origin()
    
    count = 0
    for y in range(world_size):
        for x in range(world_size):
            entity = get_entity_type()
            if entity != None:
                harvest()
                count += 1
            
            if x < world_size - 1:
                if y % 2 == 0:
                    move(East)
                else:
                    move(West)
        
        if y < world_size - 1:
            move(North)
    
    if count > 0:
        quick_print("清空完成，清除" + str(count) + "个作物")
    else:
        quick_print("农场已是空的")

# ====================
# 调试工具函数
# ====================

def get_world_size_debug(debug_size):
    # 获取自定义的世界大小（调试用）
    # debug_size: 自定义大小，如果为None则使用实际大小
    # 返回：世界大小
    if debug_size != None:
        if get_world_size() != debug_size:
            quick_print("调试模式：农场大小设置为", debug_size, "x", debug_size)
        return debug_size
    else:
        return get_world_size()

