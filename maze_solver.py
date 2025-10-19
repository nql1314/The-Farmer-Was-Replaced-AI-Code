# 迷宫生成和寻宝脚本
# 使用 BFS 算法导航到宝藏位置

# 生成迷宫
# 参数：size - 迷宫大小（默认为全场）
def generate_maze(size=None):
    # 如果未指定大小，使用全场大小
    if size == None:
        size = get_world_size()
    
    # 种植灌木
    plant(Entities.Bush)
    
    # 计算所需的奇异物质数量
    # 根据迷宫解锁等级调整
    maze_level = num_unlocked(Unlocks.Mazes)
    substance_needed = size * (2 ** (maze_level - 1))
    
    # 检查是否有足够的奇异物质
    current_substance = num_items(Items.Weird_Substance)
    if current_substance < substance_needed:
        quick_print("奇异物质不足！需要:", substance_needed, "当前:", current_substance)
        return False
    
    # 使用奇异物质生成迷宫
    use_item(Items.Weird_Substance, substance_needed)
    quick_print("已生成", size, "x", size, "迷宫")
    return True

# BFS 寻路算法
# 从当前位置找到通往目标位置的路径
def find_path_bfs(target_x, target_y):
    start_x = get_pos_x()
    start_y = get_pos_y()
    
    # 如果已经在目标位置
    if start_x == target_x and start_y == target_y:
        return []
    
    # BFS 队列：存储 (x, y, 路径)
    queue = [(start_x, start_y, [])]
    visited = set()
    visited.add((start_x, start_y))
    
    # 方向映射
    directions = [
        (North, 0, 1),
        (East, 1, 0),
        (South, 0, -1),
        (West, -1, 0)
    ]
    
    while len(queue) > 0:
        # 取出队首元素
        current = queue[0]
        queue = queue[1:]
        
        curr_x = current[0]
        curr_y = current[1]
        path = current[2]
        
        # 尝试四个方向
        for direction_data in directions:
            direction = direction_data[0]
            dx = direction_data[1]
            dy = direction_data[2]
            
            new_x = curr_x + dx
            new_y = curr_y + dy
            
            # 检查是否已访问
            if (new_x, new_y) in visited:
                continue
            
            # 暂时移动到该位置检查是否可达
            # 需要实际尝试移动来检查墙壁
            # 但这里我们用一个更简单的方法：记录当前位置，尝试移动
            # 实际上在 BFS 中我们需要实际移动来检查
            
            # 标记为已访问
            visited.add((new_x, new_y))
            
            # 创建新路径
            new_path = path + [direction]
            
            # 如果到达目标
            if new_x == target_x and new_y == target_y:
                return new_path
            
            # 加入队列
            queue.append((new_x, new_y, new_path))
    
    # 未找到路径
    return None

# 更实用的 DFS 寻路（在迷宫中实际移动和探索）
def find_treasure_dfs():
    target_x, target_y = measure()
    quick_print("宝藏位置:", target_x, target_y)
    
    # 使用递归 DFS
    visited = set()
    path = []
    
    def dfs_helper():
        curr_x = get_pos_x()
        curr_y = get_pos_y()
        
        # 到达目标
        if curr_x == target_x and curr_y == target_y:
            return True
        
        # 标记已访问
        pos = (curr_x, curr_y)
        if pos in visited:
            return False
        visited.add(pos)
        
        # 尝试四个方向
        directions = [North, East, South, West]
        for direction in directions:
            # 检查是否可以移动
            if can_move(direction):
                # 移动
                move(direction)
                path.append(direction)
                
                # 递归搜索
                if dfs_helper():
                    return True
                
                # 回溯
                path.pop()
                opposite = get_opposite_direction(direction)
                move(opposite)
        
        return False
    
    # 开始搜索
    if dfs_helper():
        quick_print("找到宝藏！移动次数:", len(path))
        return True
    else:
        quick_print("未找到宝藏路径")
        return False

# 获取相反方向
def get_opposite_direction(direction):
    if direction == North:
        return South
    if direction == South:
        return North
    if direction == East:
        return West
    if direction == West:
        return East
    return North

# 真正的 DFS 回溯算法（能够从死胡同返回）
# 使用路径栈实现完整回溯
# 
# 算法原理：
# 1. 优先探索朝向目标的未访问路径
# 2. 当所有方向都访问过或被墙挡住时，从路径栈回溯
# 3. 回溯会返回到上一个有未探索分支的位置
# 4. 重复直到找到宝藏或回溯到起点
#
# 这样可以保证：
# - 不会在两个位置之间来回（visited 防止）
# - 不会卡在死胡同（path_stack 回溯）
# - 能够完整探索迷宫直到找到出路
def solve_maze_dfs_iterative():
    target_x, target_y = measure()
    quick_print("宝藏位置:", target_x, target_y)
    
    # 访问记录（记录从哪个方向访问过）
    visited = set()
    # 路径栈：记录移动路径以便回溯
    path_stack = []
    
    max_steps = 10000
    steps = 0
    
    while steps < max_steps:
        curr_x = get_pos_x()
        curr_y = get_pos_y()
        
        # 检查是否到达宝藏
        if curr_x == target_x and curr_y == target_y:
            quick_print("找到宝藏！总移动:", steps)
            return True
        
        # 标记当前位置为已访问
        curr_pos = (curr_x, curr_y)
        visited.add(curr_pos)
        
        # 计算到目标的方向
        dx = target_x - curr_x
        dy = target_y - curr_y
        
        # 构建方向优先级（朝目标方向）
        priority_dirs = []
        if dx > 0:
            priority_dirs.append(East)
        elif dx < 0:
            priority_dirs.append(West)
        if dy > 0:
            priority_dirs.append(North)
        elif dy < 0:
            priority_dirs.append(South)
        
        # 添加其他方向
        all_dirs = [North, East, South, West]
        for d in all_dirs:
            if d not in priority_dirs:
                priority_dirs.append(d)
        
        # 尝试找到一个未访问的可移动方向
        found_new = False
        for direction in priority_dirs:
            if can_move(direction):
                # 计算目标位置
                next_x = curr_x
                next_y = curr_y
                if direction == North:
                    next_y = next_y + 1
                elif direction == South:
                    next_y = next_y - 1
                elif direction == East:
                    next_x = next_x + 1
                elif direction == West:
                    next_x = next_x - 1
                
                next_pos = (next_x, next_y)
                
                # 如果是未访问的位置，前进
                if next_pos not in visited:
                    move(direction)
                    path_stack.append(direction)
                    found_new = True
                    steps = steps + 1
                    break
        
        # 如果没有找到新路径，需要回溯
        if not found_new:
            if len(path_stack) == 0:
                quick_print("无法到达宝藏（已回溯到起点）")
                return False
            
            # 回溯：沿着来时的路返回
            last_direction = path_stack.pop()
            opposite = get_opposite_direction(last_direction)
            move(opposite)
            steps = steps + 1
            
            # 每回溯100步打印一次状态
            if steps % 100 == 0:
                quick_print("回溯中... 已探索:", len(visited), "位置")
    
    quick_print("超过最大步数限制")
    return False

# 完整的迷宫求解流程
def solve_maze():
    # 测量宝藏位置
    treasure_x, treasure_y = measure()
    quick_print("开始寻找宝藏，位置:", treasure_x, treasure_y)
    
    # 记录起始 tick
    start_tick = get_tick_count()
    
    # 使用 DFS 回溯算法
    if solve_maze_dfs_iterative():
        # 检查是否在宝藏上
        if get_entity_type() == Entities.Treasure:
            # 收割宝藏
            gold_before = num_items(Items.Gold)
            harvest()
            gold_after = num_items(Items.Gold)
            gold_gained = gold_after - gold_before
            
            # 计算用时
            ticks_used = get_tick_count() - start_tick
            
            quick_print("成功获得宝藏！")
            quick_print("获得金币:", gold_gained)
            quick_print("消耗 ticks:", ticks_used)
            return True
        else:
            quick_print("位置错误，不是宝藏")
            return False
    else:
        quick_print("寻宝失败")
        return False

# 主函数：生成迷宫并寻宝
def run_maze():
    quick_print("=== 迷宫寻宝开始 ===")
    
    # 检查是否已经在迷宫中
    entity = get_entity_type()
    if entity == Entities.Hedge or entity == Entities.Treasure:
        quick_print("已在迷宫中，直接寻宝")
        solve_maze()
    else:
        # 生成新迷宫
        if generate_maze():
            # 寻找宝藏
            solve_maze()
        else:
            quick_print("迷宫生成失败")
    
    quick_print("=== 迷宫寻宝完成 ===")

# 批量迷宫寻宝（消耗所有奇异物质）
def farm_mazes():
    maze_level = num_unlocked(Unlocks.Mazes)
    world_size = get_world_size()
    substance_per_maze = world_size * (2 ** (maze_level - 1))
    
    quick_print("=== 开始批量迷宫寻宝 ===")
    quick_print("每个迷宫需要奇异物质:", substance_per_maze)
    
    total_gold = 0
    maze_count = 0
    
    while num_items(Items.Weird_Substance) >= substance_per_maze:
        maze_count = maze_count + 1
        quick_print("--- 第", maze_count, "个迷宫 ---")
        
        # 移动到安全位置（0, 0）
        move(South)
        while get_pos_x() > 0:
            move(West)
        while get_pos_y() > 0:
            move(South)
        
        gold_before = num_items(Items.Gold)
        run_maze()
        gold_after = num_items(Items.Gold)
        gold_gained = gold_after - gold_before
        total_gold = total_gold + gold_gained
        
        quick_print("本次获得金币:", gold_gained)
    
    quick_print("=== 批量迷宫寻宝完成 ===")
    quick_print("总共完成迷宫:", maze_count)
    quick_print("总共获得金币:", total_gold)

# 执行
run_maze()  # 单次迷宫
# farm_mazes()  # 批量迷宫

