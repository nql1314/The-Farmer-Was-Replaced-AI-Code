# ============================================
# 恐龙脚本 - A* 搜索算法版本（共享内存）
# ============================================
# 功能：
# 1. 使用 A* 算法寻找从蛇头到苹果的最优路径
# 2. 尾随策略：虚拟探测吃到苹果后能否到达蛇尾
# 3. 安全模式：如果无法安全吃苹果，跟随蛇尾移动
# 4. 使用共享内存架构（无人机维护数据）
# ============================================

# ============================================
# 配置区域
# ============================================

# 目标尾巴长度
TARGET_LENGTH = 36

# 是否打印详细日志
VERBOSE = True

# ============================================
# 共享数据结构创建器
# ============================================

def create_shared_data():
    # 创建共享数据字典
    return {
        # 蛇身位置列表 [(x, y), ...]
        "snake_body": [],
        
        # 地图大小
        "world_size": get_world_size(),
        
        # 统计数据
        "apples_eaten": 0,
        "start_tick": 0,
        "total_ticks": 0,
        "bones_collected": 0,
        
        # 优先队列（最小堆）
        # 格式：[(priority, (x, y)), ...]
        "priority_queue": [],
        
        # A* 搜索临时数据
        "came_from": {},    # {(x,y): ((prev_x, prev_y), direction)}
        "g_score": {},      # {(x,y): cost}
        
        # 路径结果
        "path_result": None,
        
        # 状态标记
        "status": "ready"
    }

# ============================================
# 优先队列操作函数
# ============================================

def pq_push(shared, item, priority):
    # 将元素插入优先队列
    pq = shared["priority_queue"]
    pq.append((priority, item))
    
    # 插入排序（保持从小到大）
    i = len(pq) - 1
    while i > 0:
        if pq[i][0] < pq[i-1][0]:
            temp = pq[i]
            pq[i] = pq[i-1]
            pq[i-1] = temp
            i -= 1
        else:
            break

def pq_pop(shared):
    # 弹出优先级最高（值最小）的元素
    pq = shared["priority_queue"]
    if len(pq) > 0:
        return pq.pop(0)[1]
    return None

def pq_is_empty(shared):
    # 检查优先队列是否为空
    return len(shared["priority_queue"]) == 0

def pq_clear(shared):
    # 清空优先队列
    shared["priority_queue"] = []

# ============================================
# 辅助计算函数
# ============================================

def manhattan_distance(shared, x1, y1, x2, y2):
    # 曼哈顿距离
    world_size = shared["world_size"]
    
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    
    return dx + dy

def is_position_safe(shared, x, y, ignore_tail):
    # 检查位置是否安全（不在蛇身上）
    snake_body = shared["snake_body"]
    
    body_to_check = snake_body
    if ignore_tail and len(snake_body) > 0:
        # 排除蛇尾（因为蛇尾会移动）
        body_to_check = snake_body[:-1]
    
    for i in range(len(body_to_check)):
        bx = body_to_check[i][0]
        by = body_to_check[i][1]
        if bx == x and by == y:
            return False
    
    return True

def get_neighbors(shared, x, y):
    # 获取相邻位置（上下左右）
    # 重要：恐龙地图不是环形的，需要检查边界
    world_size = shared["world_size"]
    neighbors = []
    
    # 东（右）
    if x + 1 < world_size:
        neighbors.append((x + 1, y, East))
    
    # 西（左）
    if x - 1 >= 0:
        neighbors.append((x - 1, y, West))
    
    # 北（上）
    if y + 1 < world_size:
        neighbors.append((x, y + 1, North))
    
    # 南（下）
    if y - 1 >= 0:
        neighbors.append((x, y - 1, South))
    
    return neighbors

# ============================================
# A* 搜索算法
# ============================================

def astar_search(shared, start_x, start_y, goal_x, goal_y, ignore_tail):
    # A* 搜索算法
    # 返回路径（方向列表）或 None
    
    world_size = shared["world_size"]
    
    # 起点和终点相同
    if start_x == goal_x and start_y == goal_y:
        return []
    
    # 清空并初始化临时数据
    pq_clear(shared)
    shared["came_from"] = {}
    shared["g_score"] = {}
     
    # 添加起点
    start_pos = (start_x, start_y)
    pq_push(shared, start_pos, 0)
    shared["g_score"][start_pos] = 0
    
    # A* 主循环
    max_iterations = world_size * world_size * 2
    iteration = 0
    
    while not pq_is_empty(shared) and iteration < max_iterations:
        iteration += 1
        
        current = pq_pop(shared)
        if current == None:
            break
        
        current_x = current[0]
        current_y = current[1]
        
        # 到达目标
        if current_x == goal_x and current_y == goal_y:
            # 重建路径
            path = []
            pos = (current_x, current_y)
            came_from = shared["came_from"]
            
            while pos in came_from:
                prev_data = came_from[pos]
                prev_pos = prev_data[0]
                direction = prev_data[1]
                path.append(direction)
                pos = prev_pos
            
            # 反转路径（从起点到终点）
            reverse(path)
            return path
        
        # 检查所有邻居
        neighbors = get_neighbors(shared, current_x, current_y)
        g_score = shared["g_score"]
        came_from = shared["came_from"]
        
        for neighbor in neighbors:
            nx = neighbor[0]
            ny = neighbor[1]
            direction = neighbor[2]
            
            # 检查是否安全
            if not is_position_safe(shared, nx, ny, ignore_tail):
                continue
            
            # 计算新的 g_score
            current_g = g_score[(current_x, current_y)]
            tentative_g = current_g + 1
            
            neighbor_pos = (nx, ny)
            if neighbor_pos not in g_score or tentative_g < g_score[neighbor_pos]:
                # 更新最佳路径
                came_from[neighbor_pos] = ((current_x, current_y), direction)
                g_score[neighbor_pos] = tentative_g
                
                # 计算 f_score = g_score + h_score
                h = manhattan_distance(shared, nx, ny, goal_x, goal_y)
                f = tentative_g + h
                
                pq_push(shared, neighbor_pos, f)
    
    # 没有找到路径
    return None

def reverse(path):
    for i in range(len(path) // 2):
        temp = path[i]
        path[i] = path[len(path) - i - 1]
        path[len(path) - i - 1] = temp
    return path
# ============================================
# 蛇移动和安全策略
# ============================================

def get_tail_position(shared):
    # 获取蛇尾位置
    snake_body = shared["snake_body"]
    if len(snake_body) > 0:
        return snake_body[-1]
    return None

def is_safe_to_eat_apple(shared, apple_x, apple_y, head_x, head_y):
    # 尾随策略：虚拟探测
    # 模拟吃到苹果后，检查是否能到达蛇尾
    
    # 找到从蛇头到苹果的路径
    path_to_apple = astar_search(shared, head_x, head_y, apple_x, apple_y, True)
    
    if path_to_apple == None:
        return False
    
    # 虚拟模拟：假设蛇头已经到达苹果位置
    virtual_head_x = apple_x
    virtual_head_y = apple_y
    
    # 创建虚拟蛇身
    original_body = shared["snake_body"]
    virtual_body = []
    
    # 复制当前蛇身
    for i in range(len(original_body)):
        virtual_body.append(original_body[i])
    
    # 添加新的蛇头位置（吃到苹果）
    virtual_body.insert(0, (virtual_head_x, virtual_head_y))
    # 吃到苹果后长度增加，不移除蛇尾
    
    # 获取虚拟蛇尾位置
    if len(virtual_body) > 0:
        virtual_tail = virtual_body[-1]
        tail_x = virtual_tail[0]
        tail_y = virtual_tail[1]
    else:
        # 没有蛇尾，直接返回安全
        return True
    
    # 临时使用虚拟蛇身
    shared["snake_body"] = virtual_body
    
    # 检查从虚拟蛇头到虚拟蛇尾是否有路径
    path_to_tail = astar_search(shared, virtual_head_x, virtual_head_y, tail_x, tail_y, True)
    
    # 恢复原始蛇身
    shared["snake_body"] = original_body
    
    # 如果能找到路径到蛇尾，说明安全
    return path_to_tail != None

def follow_tail(shared, head_x, head_y):
    # 安全模式：跟随蛇尾移动
    tail = get_tail_position(shared)
    
    if tail == None:
        # 没有蛇尾，尝试任意安全方向
        return None
    
    tail_x = tail[0]
    tail_y = tail[1]
    
    # 找到到蛇尾的路径
    path = astar_search(shared, head_x, head_y, tail_x, tail_y, True)
    
    if path != None and len(path) > 0:
        # 返回第一步方向
        return path[0]
    else:
        # 找不到路径
        return None

def find_safe_direction(shared, head_x, head_y):
    # 尝试找到任意安全的方向
    # 重要：恐龙地图不是环形的，需要检查边界
    world_size = shared["world_size"]
    directions = [North, East, South, West]
    
    for direction in directions:
        # 计算目标位置（检查边界）
        target_x = head_x
        target_y = head_y
        valid = True
        
        if direction == East:
            if head_x + 1 < world_size:
                target_x = head_x + 1
            else:
                valid = False
        elif direction == West:
            if head_x - 1 >= 0:
                target_x = head_x - 1
            else:
                valid = False
        elif direction == North:
            if head_y + 1 < world_size:
                target_y = head_y + 1
            else:
                valid = False
        else:  # South
            if head_y - 1 >= 0:
                target_y = head_y - 1
            else:
                valid = False
        
        # 检查是否有效且安全
        if valid and is_position_safe(shared, target_x, target_y, True):
            return direction
    
    # 所有方向都不安全
    return None

def update_snake_body(shared, new_x, new_y, ate_apple):
    # 更新蛇身位置
    snake_body = shared["snake_body"]
    
    # 添加新的蛇头位置
    snake_body.insert(0, (new_x, new_y))
    
    # 如果没吃到苹果，移除蛇尾
    if not ate_apple:
        if len(snake_body) > 0:
            snake_body.pop()

# ============================================
# 主要游戏逻辑
# ============================================

def grow_tail_with_astar(shared, target_length):
    # 使用 A* 算法增长尾巴
    quick_print("开始 A* 智能吃苹果，目标长度: " + str(target_length))
    
    current_length = 0
    failed_attempts = 0
    max_failed = 100
    follow_tail_mode = False
    global apple_x
    global apple_y
    apple_x = 0
    apple_y = 0
    # 初始化蛇身（只有蛇头）
    head_x = get_pos_x()
    head_y = get_pos_y()
    shared["snake_body"] = [(head_x, head_y)]
    
    # 重要：恐龙帽机制详解
    # 1. 装备恐龙帽后，第一个苹果在脚下生成
    # 2. 只有站在苹果上时，measure() 才返回下一个苹果的位置
    # 3. 离开苹果后，旧苹果消失，新苹果在预告位置出现
    # 4. 移动回到新苹果位置才算"吃到"
    
    # 策略：开局不需要特殊处理，直接开始主循环
    # 因为：
    # - 第一次循环会在苹果上获取下一个位置
    # - 移动离开后，新苹果出现
    # - 移动回去吃掉新苹果
    
    quick_print("初始化完成，开始寻路吃苹果...")
    
    while current_length < target_length and failed_attempts < max_failed:
        # 获取当前位置
        head_x = get_pos_x()
        head_y = get_pos_y()
        
        # 关键机制（重要！）：
        # - 只有站在苹果上时，measure() 才返回下一个苹果的位置
        # - 不在苹果上时，measure() 不返回任何有效信息
        # - 策略：必须先找到当前苹果并站上去，才能知道下一个在哪
        
        # 检查是否站在苹果上
        on_apple = (get_entity_type() == Entities.Apple)
        
        if on_apple:
            # 站在苹果上，可以获取下一个苹果的位置
            if VERBOSE and current_length == 0:
                quick_print("站在开局苹果上，获取下一个位置...")
            
            # 获取下一个苹果的位置
            apple_pos = None
            while apple_pos == None:
                apple_pos = measure()
                if apple_pos == None:
                    # 苹果无法生成（位置被占），等待
                    do_a_flip()
            apple_x = apple_pos[0]
            apple_y = apple_pos[1]
            if VERBOSE and current_length == 0:
                quick_print("下一个苹果在: (" + str(apple_x) + ", " + str(apple_y) + ")")
        
        # 使用尾随策略检查是否安全去下一个苹果
        if is_safe_to_eat_apple(shared, apple_x, apple_y, head_x, head_y):
            # 安全，使用 A* 找路径到下一个苹果位置
            path = astar_search(shared, head_x, head_y, apple_x, apple_y, True)
            
            if path != None and len(path) > 0:
                next_direction = path[0]
                follow_tail_mode = False
            else:
                # 找不到路径，跟随蛇尾
                next_direction = follow_tail(shared, head_x, head_y)
                follow_tail_mode = True
        else:
            # 不安全，跟随蛇尾
            if not follow_tail_mode and VERBOSE:
                quick_print("去下一个苹果不安全，跟随蛇尾...")
            next_direction = follow_tail(shared, head_x, head_y)
            follow_tail_mode = True
        
        # 如果找不到方向，尝试任意安全方向
        if next_direction == None:
            next_direction = find_safe_direction(shared, head_x, head_y)
        
        # 执行移动（离开当前苹果）
        if next_direction != None:
            if move(next_direction):
                new_x = get_pos_x()
                new_y = get_pos_y()
                
                # 离开苹果，蛇尾移动（未吃到新苹果）
                # 此时旧苹果消失，新苹果在 apple_pos 位置出现
                update_snake_body(shared, new_x, new_y, False)
            else:
                quick_print("错误: 移动失败")
                failed_attempts += 1
        else:
            quick_print("错误: 找不到移动方向")
            failed_attempts += 1
    
    quick_print("尾巴增长完成! 最终长度: " + str(current_length))
    return current_length

def calculate_bones(length):
    return length * length

# ============================================
# 主函数（使用共享内存架构）
# ============================================

def run_dinosaur_astar():
    
    # 创建共享数据源
    shared_data_source = spawn_drone(create_shared_data)
    
    # 获取共享数据
    shared = wait_for(shared_data_source)
    
    # 记录开始时间
    shared["start_tick"] = get_tick_count()
    quick_print("开始 A* 智能恐龙养殖...")
    quick_print("目标长度: " + str(TARGET_LENGTH))
    quick_print("地图大小: " + str(shared["world_size"]) + "x" + str(shared["world_size"]))
    
    # 准备农场
    clear()
    
    # 装备恐龙帽
    quick_print("装备恐龙帽...")
    change_hat(Hats.Dinosaur_Hat)
    quick_print("恐龙帽已装备")
    
    # 使用 A* 增长尾巴
    final_length = grow_tail_with_astar(shared, TARGET_LENGTH)
    
    # 卸下恐龙帽
    quick_print("卸下恐龙帽，收获骨头...")
    change_hat(Hats.Brown_Hat)
    
    # 计算收获
    bones_collected = calculate_bones(final_length)
    total_ticks = get_tick_count() - shared["start_tick"]
    
    # 打印统计
    quick_print("======================")
    quick_print("A* 恐龙养殖完成!")
    quick_print("======================")
    quick_print("尾巴长度: " + str(final_length))
    quick_print("吃掉苹果: " + str(shared["apples_eaten"]))
    quick_print("收获骨头: " + str(bones_collected))
    quick_print("总消耗ticks: " + str(total_ticks))
    
    if bones_collected > 0:
        ticks_per_bone = total_ticks // bones_collected
        quick_print("每骨头成本: " + str(ticks_per_bone) + " ticks")
        
        if ticks_per_bone < 500:
            quick_print("效率评级: ⭐⭐⭐⭐⭐ 优秀!")
        elif ticks_per_bone < 1000:
            quick_print("效率评级: ⭐⭐⭐⭐ 良好")
        elif ticks_per_bone < 2000:
            quick_print("效率评级: ⭐⭐⭐ 一般")
        else:
            quick_print("效率评级: ⭐⭐ 需要优化")
    
    quick_print("======================")
    quick_print("当前骨头总数: " + str(num_items(Items.Bone)))
    quick_print("======================")

# ============================================
# 执行
# ============================================
set_world_size(10)
run_dinosaur_astar()
