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
    # 曼哈顿距离（考虑环形地图）
    world_size = shared["world_size"]
    
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    
    # 环形地图优化
    dx = min(dx, world_size - dx)
    dy = min(dy, world_size - dy)
    
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
    world_size = shared["world_size"]
    neighbors = []
    
    # 东
    nx = (x + 1) % world_size
    neighbors.append((nx, y, East))
    
    # 西
    nx = (x - 1) % world_size
    neighbors.append((nx, y, West))
    
    # 北
    ny = (y + 1) % world_size
    neighbors.append((x, ny, North))
    
    # 南
    ny = (y - 1) % world_size
    neighbors.append((x, ny, South))
    
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
    world_size = shared["world_size"]
    directions = [North, East, South, West]
    
    for direction in directions:
        # 计算目标位置
        if direction == East:
            target_x = (head_x + 1) % world_size
            target_y = head_y
        elif direction == West:
            target_x = (head_x - 1) % world_size
            target_y = head_y
        elif direction == North:
            target_x = head_x
            target_y = (head_y + 1) % world_size
        else:  # South
            target_x = head_x
            target_y = (head_y - 1) % world_size
        
        # 检查是否安全
        if is_position_safe(shared, target_x, target_y, True):
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
    
    # 初始化蛇身（只有蛇头）
    shared["snake_body"] = [(get_pos_x(), get_pos_y())]
    
    while current_length < target_length and failed_attempts < max_failed:
        # 获取当前位置
        head_x = get_pos_x()
        head_y = get_pos_y()
        
        # 获取苹果位置
        apple_x = None
        apple_y = None
        
        if get_entity_type() == Entities.Apple:
            apple_pos = measure()
            apple_x = apple_pos[0]
            apple_y = apple_pos[1]
        else:
            # 找不到苹果
            failed_attempts += 1
            if VERBOSE:
                quick_print("警告: 找不到苹果，尝试移动...")
            
            # 尝试安全移动
            safe_dir = find_safe_direction(shared, head_x, head_y)
            if safe_dir != None:
                if move(safe_dir):
                    update_snake_body(shared, get_pos_x(), get_pos_y(), False)
            else:
                quick_print("错误: 无法移动，游戏结束")
                break
            
            continue
        
        # 重置失败计数
        failed_attempts = 0
        
        # 决定移动方向
        next_direction = None
        
        # 检查是否安全吃苹果（尾随策略）
        if is_safe_to_eat_apple(shared, apple_x, apple_y, head_x, head_y):
            # 安全，使用 A* 找路径
            path = astar_search(shared, head_x, head_y, apple_x, apple_y, True)
            
            if path != None and len(path) > 0:
                next_direction = path[0]
                follow_tail_mode = False
            else:
                # 找不到路径，进入跟随模式
                next_direction = follow_tail(shared, head_x, head_y)
                follow_tail_mode = True
        else:
            # 不安全，跟随蛇尾
            if not follow_tail_mode and VERBOSE:
                quick_print("吃苹果不安全，切换到跟随蛇尾模式...")
            
            next_direction = follow_tail(shared, head_x, head_y)
            follow_tail_mode = True
        
        # 如果找不到方向，尝试任意安全方向
        if next_direction == None:
            next_direction = find_safe_direction(shared, head_x, head_y)
        
        # 执行移动
        if next_direction != None:
            if move(next_direction):
                new_x = get_pos_x()
                new_y = get_pos_y()
                
                # 检查是否吃到苹果
                ate_apple = get_entity_type() != Entities.Apple and (new_x == apple_x and new_y == apple_y)
                
                # 更新蛇身
                update_snake_body(shared, new_x, new_y, ate_apple)
                
                # 如果吃到苹果
                if new_x == apple_x and new_y == apple_y:
                    current_length += 1
                    shared["apples_eaten"] += 1
                    
                    if VERBOSE and current_length % 5 == 0:
                        quick_print("已吃苹果: " + str(current_length) + "/" + 
                                   str(target_length))
                    
                    follow_tail_mode = False
            else:
                quick_print("错误: 移动失败")
                break
        else:
            quick_print("错误: 找不到可移动的方向")
            break
    
    quick_print("尾巴增长完成! 最终长度: " + str(current_length))
    return current_length

def calculate_bones(length):
    return length * length

def print_efficiency_table():
    quick_print("======================")
    quick_print("A* 恐龙效率预测")
    quick_print("======================")
    quick_print("长度 | 骨头数")
    
    for length in [10, 16, 20, 25, 36, 49, 64, 81, 100]:
        bones = calculate_bones(length)
        quick_print(str(length) + " | " + str(bones))
    
    quick_print("======================")

# ============================================
# 主函数（使用共享内存架构）
# ============================================

def run_dinosaur_astar():
    # 打印效率表
    print_efficiency_table()
    
    # 创建共享数据源
    shared_data_source = spawn_drone(create_shared_data)
    
    # 获取共享数据
    shared = wait_for(shared_data_source)
    
    # 记录开始时间
    shared["start_tick"] = get_tick_count()
    quick_print("开始 A* 智能恐龙养殖...")
    quick_print("目标长度: " + str(TARGET_LENGTH))
    quick_print("地图大小: " + str(shared["world_size"]) + "x" + str(shared["world_size"]))
    
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
# 准备农场
clear()
set_world_size(10)
run_dinosaur_astar()
