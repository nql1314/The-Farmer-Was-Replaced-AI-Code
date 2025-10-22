# 终极迷宫求解器 - 最高效率版本
# 特性：
# 1. 完整地图记忆（记录所有墙壁和通路）
# 2. BFS 最短路径（保证最少移动）
# 3. 智能地图更新（处理重复迷宫的墙壁变化）
# 4. 性能优化（缓存计算，减少函数调用）

# 全局状态
g_maze_map = {}  # {(x,y): {direction: True/False}} 完整地图
g_maze_size = 0
g_reuse_count = 0

# 方向常量（避免重复访问全局变量）
DIR_NORTH = North
DIR_SOUTH = South
DIR_EAST = East
DIR_WEST = West
ALL_DIRECTIONS = [DIR_NORTH, DIR_EAST, DIR_SOUTH, DIR_WEST]

# 方向到坐标偏移的映射
DIR_OFFSETS = {
    DIR_NORTH: (0, 1),
    DIR_SOUTH: (0, -1),
    DIR_EAST: (1, 0),
    DIR_WEST: (-1, 0)
}

# 相反方向映射
OPPOSITE_DIRS = {
    DIR_NORTH: DIR_SOUTH,
    DIR_SOUTH: DIR_NORTH,
    DIR_EAST: DIR_WEST,
    DIR_WEST: DIR_EAST
}

# 快速计算下一个位置
def next_pos(x, y, direction):
    offset = DIR_OFFSETS[direction]
    return (x + offset[0], y + offset[1])

# 更新地图信息（记录某个位置某个方向是否可通行）
def update_map(x, y, direction, can_pass):
    pos = (x, y)
    if pos not in g_maze_map:
        g_maze_map[pos] = {}
    g_maze_map[pos][direction] = can_pass

# 检查地图中是否知道某个方向可通行
def is_known_passable(x, y, direction):
    pos = (x, y)
    if pos in g_maze_map:
        if direction in g_maze_map[pos]:
            return g_maze_map[pos][direction]
    return None  # 未知

# BFS 最短路径（使用已知地图）
def bfs_shortest_path(start_x, start_y, target_x, target_y):
    if start_x == target_x and start_y == target_y:
        return []
    
    # 队列：[(x, y, path)]
    queue = [(start_x, start_y, [])]
    visited = {}  # 使用字典代替 set
    visited[(start_x, start_y)] = True
    
    idx = 0
    while idx < len(queue):
        curr = queue[idx]
        idx = idx + 1
        
        curr_x = curr[0]
        curr_y = curr[1]
        path = curr[2]
        
        # 尝试四个方向
        for direction in ALL_DIRECTIONS:
            # 检查是否已知可通行
            passable = is_known_passable(curr_x, curr_y, direction)
            if passable == False:
                continue  # 已知有墙
            
            # 计算下一个位置
            next_x, next_y = next_pos(curr_x, curr_y, direction)
            next_position = (next_x, next_y)
            
            if next_position in visited:
                continue
            visited[next_position] = True
            
            new_path = path + [direction]
            
            # 到达目标
            if next_x == target_x and next_y == target_y:
                return new_path
            
            queue.append((next_x, next_y, new_path))
    
    return None  # 无已知路径

# 探索式移动到目标（边走边更新地图）
def explore_to_target(target_x, target_y):
    visited = {}  # 使用字典代替 set
    path_stack = []
    moves = 0
    max_moves = 30000
    
    while moves < max_moves:
        curr_x = get_pos_x()
        curr_y = get_pos_y()
        
        # 到达目标
        if curr_x == target_x and curr_y == target_y:
            return True
        
        curr_pos = (curr_x, curr_y)
        visited[curr_pos] = True
        
        # 计算方向优先级（朝目标）
        dx = target_x - curr_x
        dy = target_y - curr_y
        
        # 优先级排序
        priority_dirs = []
        
        # 主方向
        if abs(dx) >= abs(dy):
            if dx > 0:
                priority_dirs.append(DIR_EAST)
            elif dx < 0:
                priority_dirs.append(DIR_WEST)
            if dy > 0:
                priority_dirs.append(DIR_NORTH)
            elif dy < 0:
                priority_dirs.append(DIR_SOUTH)
        else:
            if dy > 0:
                priority_dirs.append(DIR_NORTH)
            elif dy < 0:
                priority_dirs.append(DIR_SOUTH)
            if dx > 0:
                priority_dirs.append(DIR_EAST)
            elif dx < 0:
                priority_dirs.append(DIR_WEST)
        
        # 补充其他方向
        for d in ALL_DIRECTIONS:
            if d not in priority_dirs:
                priority_dirs.append(d)
        
        # 尝试移动
        moved = False
        for direction in priority_dirs:
            # 检查是否已知有墙
            known = is_known_passable(curr_x, curr_y, direction)
            if known == False:
                continue  # 跳过已知的墙
            
            next_position = next_pos(curr_x, curr_y, direction)
            
            # 跳过已访问
            if next_position in visited:
                continue
            
            # 实际尝试移动
            if move(direction):
                # 成功移动，更新地图
                update_map(curr_x, curr_y, direction, True)
                path_stack.append(direction)
                moves = moves + 1
                moved = True
                break
            else:
                # 遇到墙，更新地图
                update_map(curr_x, curr_y, direction, False)
        
        # 无法前进，回溯
        if not moved:
            if len(path_stack) == 0:
                return False
            
            last_dir = path_stack.pop()
            opposite = OPPOSITE_DIRS[last_dir]
            move(opposite)
            moves = moves + 1
    
    return False

# 混合策略：先尝试已知路径，失败则探索
def navigate_to_treasure(target_x, target_y):
    start_x = get_pos_x()
    start_y = get_pos_y()
    
    # 尝试使用已知地图计算最短路径
    path = bfs_shortest_path(start_x, start_y, target_x, target_y)
    
    if path != None and len(path) > 0:
        # 尝试跟随路径
        for direction in path:
            if not move(direction):
                # 路径被阻挡（墙壁变化），更新地图并切换到探索模式
                curr_x = get_pos_x()
                curr_y = get_pos_y()
                update_map(curr_x, curr_y, direction, False)
                # 从当前位置继续探索
                return explore_to_target(target_x, target_y)
        
        # 路径成功
        return True
    
    # 无已知路径，直接探索
    return explore_to_target(target_x, target_y)

# 生成新迷宫
def create_maze():
    global g_maze_map
    global g_maze_size
    global g_reuse_count
    
    g_maze_size = get_world_size()
    maze_level = num_unlocked(Unlocks.Mazes)
    substance_needed = g_maze_size * (2 ** (maze_level - 1))
    
    if num_items(Items.Weird_Substance) < substance_needed:
        return False
    
    # 生成迷宫
    plant(Entities.Bush)
    use_item(Items.Weird_Substance, substance_needed)
    
    # 重置状态
    g_maze_map = {}
    g_reuse_count = 0
    
    return True

# 重复使用迷宫（移动宝藏）
def relocate_treasure():
    global g_reuse_count
    
    if get_entity_type() != Entities.Treasure:
        return False
    
    if g_reuse_count >= 300:
        return False
    
    maze_level = num_unlocked(Unlocks.Mazes)
    substance_needed = g_maze_size * (2 ** (maze_level - 1))
    
    if num_items(Items.Weird_Substance) < substance_needed:
        return False
    
    # 使用奇异物质移动宝藏
    use_item(Items.Weird_Substance, substance_needed)
    g_reuse_count = g_reuse_count + 1
    
    # 部分清理地图（因为墙壁可能变化）
    # 策略：保留通路信息，清除墙壁信息（因为墙可能被移除）
    global g_maze_map
    new_map = {}
    
    # 遍历地图中的所有位置
    all_positions = []
    for pos in g_maze_map:
        all_positions.append(pos)
    
    for pos in all_positions:
        new_map[pos] = {}
        # 遍历该位置的所有方向
        all_directions = []
        for direction in g_maze_map[pos]:
            all_directions.append(direction)
        
        for direction in all_directions:
            if g_maze_map[pos][direction] == True:
                # 保留通路信息（通路一般不会变成墙）
                new_map[pos][direction] = True
            # 墙壁信息不保留（可能被移除）
    
    g_maze_map = new_map
    
    return True

# 检查是否在迷宫中
def is_in_maze():
    entity = get_entity_type()
    return entity == Entities.Hedge or entity == Entities.Treasure

# 解决现有迷宫（不重复使用）
def solve_existing_maze():
    global g_maze_size
    
    quick_print("检测到现有迷宫，先完成它")
    
    # 获取世界大小作为迷宫大小
    g_maze_size = get_world_size()
    
    # 获取宝藏位置
    target_x, target_y = measure()
    quick_print("宝藏位置:", target_x, target_y)
    
    # 导航到宝藏
    if navigate_to_treasure(target_x, target_y):
        if get_entity_type() == Entities.Treasure:
            # 收获宝藏
            gold_before = num_items(Items.Gold)
            harvest()
            gold_gained = num_items(Items.Gold) - gold_before
            quick_print("完成现有迷宫，获得金币:", gold_gained)
            return gold_gained
        else:
            quick_print("错误：未到达宝藏位置")
            return 0
    else:
        quick_print("错误：无法到达宝藏")
        return 0

# 完整的单个重复迷宫流程
def run_one_reusable_maze():
    # 先检查是否已经在迷宫中
    if is_in_maze():
        solve_existing_maze()
        # 移动到安全位置准备生成新迷宫
        while get_pos_x() > 0:
            move(West)
        while get_pos_y() > 0:
            move(South)
    
    if not create_maze():
        return 0
    
    maze_gold_value = g_maze_size * g_maze_size
    total_treasure = 0
    max_reuses = 300
    
    quick_print("=== 新迷宫 ===")
    quick_print("大小:", g_maze_size, "x", g_maze_size)
    quick_print("单次金币:", maze_gold_value)
    
    start_tick = get_tick_count()
    
    # 循环寻找并重复使用宝藏
    while total_treasure <= max_reuses:
        total_treasure = total_treasure + 1
        
        # 获取宝藏位置
        target_x, target_y = measure()
        
        # 导航到宝藏
        if navigate_to_treasure(target_x, target_y):
            # 验证到达
            if get_entity_type() == Entities.Treasure:
                # 尝试重复使用
                if relocate_treasure():
                    # 继续下一个宝藏
                    if total_treasure % 10 == 0:
                        quick_print("进度:", total_treasure, "/", max_reuses, "已知路径:", len(g_maze_map))
                else:
                    # 无法重复（资源不足或达到上限），收获最后一次
                    gold_before = num_items(Items.Gold)
                    harvest()
                    gold_gained = num_items(Items.Gold) - gold_before
                    
                    end_tick = get_tick_count()
                    ticks_used = end_tick - start_tick
                    
                    quick_print("=== 迷宫完成 ===")
                    quick_print("总宝藏数:", total_treasure)
                    quick_print("获得金币:", gold_gained)
                    quick_print("消耗 ticks:", ticks_used)
                    quick_print("平均 ticks/宝藏:", ticks_used // total_treasure)
                    
                    return gold_gained
            else:
                quick_print("错误：未到达宝藏")
                return 0
        else:
            quick_print("错误：无法到达宝藏")
            return 0
    
    # 达到最大次数，收获
    harvest()
    return num_items(Items.Gold)

# 批量处理所有奇异物质
def farm_all_mazes():
    maze_level = num_unlocked(Unlocks.Mazes)
    world_size = get_world_size()
    base_substance = world_size * (2 ** (maze_level - 1))
    
    quick_print("========================================")
    quick_print("终极迷宫农场启动")
    quick_print("========================================")
    quick_print("世界大小:", world_size)
    quick_print("迷宫等级:", maze_level)
    quick_print("基础物质需求:", base_substance)
    quick_print("当前物质:", num_items(Items.Weird_Substance))
    quick_print("预计可完成迷宫数:", num_items(Items.Weird_Substance) // base_substance)
    quick_print("")
    
    maze_count = 0
    total_gold = 0
    start_tick = get_tick_count()
    
    # 检查初始状态：如果在迷宫中，先解决它
    if is_in_maze():
        quick_print("========================================")
        quick_print("检测到初始状态在迷宫中")
        quick_print("========================================")
        gold_gained = solve_existing_maze()
        total_gold = total_gold + gold_gained
        quick_print("初始迷宫完成，获得金币:", gold_gained)
        quick_print("")
        
        # 移动到起点
        while get_pos_x() > 0:
            move(West)
        while get_pos_y() > 0:
            move(South)
    
    while num_items(Items.Weird_Substance) >= base_substance:
        maze_count = maze_count + 1
        quick_print("")
        quick_print("########## 迷宫 #", maze_count, "##########")
        
        # 返回起点
        while get_pos_x() > 0:
            move(West)
        while get_pos_y() > 0:
            move(South)
        
        gold_before = num_items(Items.Gold)
        run_one_reusable_maze()
        gold_gained = num_items(Items.Gold) - gold_before
        total_gold = total_gold + gold_gained
        
        quick_print("迷宫 #", maze_count, "获得:", gold_gained, "金币")
    
    end_tick = get_tick_count()
    total_ticks = end_tick - start_tick
    
    quick_print("")
    quick_print("========================================")
    quick_print("终极迷宫农场完成")
    quick_print("========================================")
    quick_print("完成迷宫:", maze_count)
    quick_print("总金币:", total_gold)
    quick_print("总 ticks:", total_ticks)
    if maze_count > 0:
        quick_print("平均 ticks/迷宫:", total_ticks // maze_count)
        quick_print("平均金币/迷宫:", total_gold // maze_count)
    quick_print("剩余物质:", num_items(Items.Weird_Substance))

# 执行主程序
farm_all_mazes()

