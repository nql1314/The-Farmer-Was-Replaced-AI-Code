# The Farmer Was Replaced - 极简多无人机南瓜农场
# 策略：种满整个地图，验证对角ID一致后收获
# 使用共享内存机制：通过 wait_for() 返回值实现跨无人机的共享集合

# 从 farm_utils.py 导入公共工具函数
from farm_utils import goto_pos, check_mega_pumpkin_formed, harvest_mega_pumpkin

world_size = get_world_size()

# ====================
# 共享内存工具函数
# ====================

def create_shared_set():
    # 源无人机：返回共享集合（用字典模拟集合）
    # 返回值会被所有 worker 共享
    return {}

def create_diagonal_checker():
    # 源无人机：返回对角线验证状态（共享字典）
    # 用于两个对角线守卫无人机通信
    return {
        "corner_0_0": None,      # 左下角(0,0)的南瓜ID
        "corner_max_max": None,  # 右上角(n-1,n-1)的南瓜ID
        "ready": False           # 是否可以收获
    }

def add_to_shared_set(shared_set, item):
    # 添加元素到共享集合（使用字典的键和值）
    # item 是 (x, y) 元组
    # key 用于快速查找，value 存储完整的位置信息
    key = str(item[0]) + "," + str(item[1])
    shared_set[key] = item

def remove_from_shared_set(shared_set, item):
    # 从共享集合中移除元素
    key = str(item[0]) + "," + str(item[1])
    if key in shared_set:
        shared_set.pop(key)

def is_in_shared_set(shared_set, item):
    # 检查元素是否在共享集合中
    key = str(item[0]) + "," + str(item[1])
    return key in shared_set

def get_shared_set_size(shared_set):
    # 获取共享集合大小
    count = 0
    for key in shared_set:
        count = count + 1
    return count

def shared_set_to_list(shared_set):
    # 将共享集合转换为位置列表
    # 字典的值直接存储位置元组，可以直接使用
    positions = []
    for key in shared_set:
        pos = shared_set[key]
        positions.append(pos)
    return positions

# ====================
# 批次分配函数
# ====================

def split_batches_balanced(positions, num_batches):
    # 将位置列表均匀分割成多个批次
    # 确保每个批次的大小尽可能接近
    if len(positions) == 0:
        return []
    if num_batches > len(positions):
        num_batches = len(positions)
    
    batches = []
    batch_size = len(positions) // num_batches
    remainder = len(positions) % num_batches
    
    start = 0
    for i in range(num_batches):
        # 前 remainder 个批次多分配一个位置
        if i < remainder:
            end = start + batch_size + 1
        else:
            end = start + batch_size
        
        batches.append(positions[start:end])
        start = end
    
    return batches

def split_batches_by_strips(num_batches):
    # 按照条带分配批次（每个无人机负责连续的几行）
    # 这样可以最小化移动距离
    if num_batches <= 0:
        return []
    
    batches = []
    rows_per_batch = world_size // num_batches
    remainder = world_size % num_batches
    
    start_y = 0
    for i in range(num_batches):
        # 前 remainder 个批次多分配一行
        if i < remainder:
            end_y = start_y + rows_per_batch + 1
        else:
            end_y = start_y + rows_per_batch
        
        # 生成这个批次的所有位置（蛇形遍历）
        batch_positions = []
        for y in range(start_y, end_y):
            if y % 2 == 0:
                # 偶数行：从左到右
                for x in range(world_size):
                    batch_positions.append((x, y))
            else:
                # 奇数行：从右到左
                for x in range(world_size - 1, -1, -1):
                    batch_positions.append((x, y))
        
        if len(batch_positions) > 0:
            batches.append(batch_positions)
        
        start_y = end_y
    
    return batches

def generate_all_positions():
    # 生成整个地图的所有位置（蛇形顺序）
    positions = []
    for y in range(world_size):
        if y % 2 == 0:
            # 偶数行：从左到右
            for x in range(world_size):
                positions.append((x, y))
        else:
            # 奇数行：从右到左
            for x in range(world_size - 1, -1, -1):
                positions.append((x, y))
    return positions

# ====================
# 无人机工作函数（使用共享内存）
# ====================

def drone_plant_batch(batch):
    # 无人机：种植一批位置
    # 使用 goto_pos（支持环形地图最短路径）
    planted = 0
    
    for pos in batch:
        x, y = pos
        
        # 检查胡萝卜
        if num_items(Items.Carrot) < 1:
            return -1  # 标记胡萝卜不足
        
        goto_pos(x, y)
        
        # 清理
        if can_harvest():
            harvest()
        
        # 种植
        if get_ground_type() != Grounds.Soil:
            till()
        
        plant(Entities.Pumpkin)
        planted = planted + 1
    
    return planted

def drone_verify_and_fix_shared(batch, unverified_source):
    # 无人机：验证并修复一批位置（合并验证和修复阶段）
    # unverified_source: 共享集合的源无人机
    # 返回：(验证通过数量, 修复数量)，如果胡萝卜不足返回 (-1, -1)
    
    # 获取共享集合
    unverified_set = wait_for(unverified_source)
    
    verified_count = 0
    fixed_count = 0
    
    for pos in batch:
        x, y = pos
        goto_pos(x, y)
        
        entity = get_entity_type()
        
        if entity == Entities.Pumpkin:
            # 检查是否可以收获（说明已成熟）
            if can_harvest():
                # 验证通过，从未验证集合中移除
                remove_from_shared_set(unverified_set, pos)
                verified_count = verified_count + 1
            # 未成熟的南瓜：保持在未验证集合中，无需操作
        
        elif entity == Entities.Dead_Pumpkin:
            # 检查胡萝卜
            if num_items(Items.Carrot) < 1:
                return (-1, -1)
            
            # 补种枯萎南瓜
            plant(Entities.Pumpkin)
            fixed_count = fixed_count + 1
            # 补种后需要重新验证，确保在未验证集合中
            add_to_shared_set(unverified_set, pos)
        
        elif entity == None:
            # 检查胡萝卜
            if num_items(Items.Carrot) < 1:
                return (-1, -1)
            
            # 空位置，补种
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            fixed_count = fixed_count + 1
            # 补种后需要重新验证
            add_to_shared_set(unverified_set, pos)
    
    return (verified_count, fixed_count)

def drone_diagonal_guard(corner_x, corner_y, diagonal_source):
    # 无人机：对角线守卫（持续检查对角线位置）
    # corner_x, corner_y: 负责的角落坐标
    # diagonal_source: 对角线验证状态的源无人机
    # 返回：检查次数
    
    # 获取共享状态
    diagonal_state = wait_for(diagonal_source)
    
    # 确定自己负责哪个角落
    if corner_x == 0 and corner_y == 0:
        my_key = "corner_0_0"
    else:
        my_key = "corner_max_max"
    
    check_count = 0
    
    # 持续检查对角线位置
    while not diagonal_state["ready"]:
        goto_pos(corner_x, corner_y)
        
        entity = get_entity_type()
        
        if entity == Entities.Pumpkin:
            if can_harvest():
                # 获取南瓜ID
                pumpkin_id = measure()
                if pumpkin_id != None:
                    # 更新自己的ID
                    diagonal_state[my_key] = pumpkin_id
                    
                    # 检查另一个角落是否也准备好了
                    if my_key == "corner_0_0":
                        other_id = diagonal_state["corner_max_max"]
                    else:
                        other_id = diagonal_state["corner_0_0"]
                    
                    # 如果两个ID都存在且相同，标记为准备收获
                    if other_id != None and pumpkin_id == other_id:
                        diagonal_state["ready"] = True
                        quick_print(">>> 对角线守卫：ID一致！(" + str(corner_x) + "," + str(corner_y) + ") <<<")
                        break
                else:
                    # 没有ID，清空自己的记录
                    diagonal_state[my_key] = None
            else:
                # 不可收获，清空自己的记录
                diagonal_state[my_key] = None
        else:
            # 不是南瓜，清空自己的记录
            diagonal_state[my_key] = None
        
        check_count = check_count + 1
    
    return check_count

# 删除 drone_wait_batch 函数，不再需要等待阶段

# ====================
# 阶段函数（使用共享内存机制）
# ====================

def stage_plant(unverified_source):
    # 阶段1：并行种植整个地图
    # unverified_source: 共享未验证集合的源无人机
    # 返回：是否成功
    
    quick_print("=== 阶段1：种植 ===")
    
    # 获取共享集合并清空
    unverified_set = wait_for(unverified_source)
    for key in unverified_set:
        unverified_set.pop(key)
    
    # 获取所有位置
    all_pos = generate_all_positions()
    quick_print("位置数: " + str(len(all_pos)))
    
    # 初始化：所有位置都未验证
    for pos in all_pos:
        add_to_shared_set(unverified_set, pos)
    
    # 并行种植（使用条带分配，每个无人机负责连续的几行）
    available = max_drones() + 1
    batches = split_batches_by_strips(available)
    quick_print("分批: " + str(len(batches)) + " 条带")
    
    # 显示每个批次的大小
    for i in range(len(batches)):
        quick_print("批次" + str(i) + ": " + str(len(batches[i])) + " 个位置")
    
    drones = []
    results = []
    
    for i in range(len(batches)):
        def create_task(b):
            def task():
                return drone_plant_batch(b)
            return task
        
        task = create_task(batches[i])
        
        if i < len(batches) - 1:
            drone = spawn_drone(task)
            if drone:
                drones.append(drone)
            else:
                results.append(task())
        else:
            results.append(task())
    
    for drone in drones:
        results.append(wait_for(drone))
    
    # 检查结果
    total = 0
    for result in results:
        if result == -1:
            quick_print("!!! 胡萝卜不足 !!!")
            return False
        total = total + result
    
    quick_print("已种植: " + str(total))
    return True

def stage_verify_and_fix(unverified_source):
    # 阶段2：并行验证和修复（合并原来的验证和修复阶段）
    # unverified_source: 共享未验证集合的源无人机
    # 返回：是否成功
    
    # 获取共享集合
    unverified_set = wait_for(unverified_source)
    
    # 转换为列表用于分批
    unverified_list = shared_set_to_list(unverified_set)
    
    if len(unverified_list) == 0:
        quick_print("=== 全部已验证 ===")
        return True
    
    quick_print("=== 验证和修复 " + str(len(unverified_list)) + " 个位置 ===")
    
    # 并行验证和修复（使用均衡分批）
    available = max_drones() + 1
    batches = split_batches_balanced(unverified_list, available)
    
    drones = []
    results = []
    
    for i in range(len(batches)):
        def create_task(b, src):
            def task():
                return drone_verify_and_fix_shared(b, src)
            return task
        
        task = create_task(batches[i], unverified_source)
        
        if i < len(batches) - 1:
            drone = spawn_drone(task)
            if drone:
                drones.append(drone)
            else:
                results.append(task())
        else:
            results.append(task())
    
    for drone in drones:
        results.append(wait_for(drone))
    
    # 统计结果
    total_verified = 0
    total_fixed = 0
    for result in results:
        verified, fixed = result
        if verified == -1:
            quick_print("!!! 胡萝卜不足 !!!")
            return False
        total_verified = total_verified + verified
        total_fixed = total_fixed + fixed
    
    # 获取最新的未验证数量
    remaining = get_shared_set_size(unverified_set)
    
    quick_print("已验证: " + str(total_verified) + " | 已修复: " + str(total_fixed) + " | 剩余: " + str(remaining))
    quick_print("剩余南瓜位置: " + str(shared_set_to_list(unverified_set)))
    return True

# ====================
# 主循环
# ====================

def farming_cycle():
    # 主农场循环
    # 使用共享内存机制协调多个无人机
    # 策略：持续验证和修复循环，当剩余位置少时启动对角线守卫
    
    quick_print("=== 新一轮 ===")
    quick_print("胡萝卜: " + str(num_items(Items.Carrot)) + " | 南瓜: " + str(num_items(Items.Pumpkin)))
    
    start = get_time()
    
    # 创建共享未验证集合和对角线验证状态
    unverified_source = spawn_drone(create_shared_set)
    diagonal_source = spawn_drone(create_diagonal_checker)
    
    # 阶段1：种植
    if not stage_plant(unverified_source):
        return False
    
    # 对角线守卫无人机（初始化为None，稍后启动）
    diagonal_guards = None
    guards_started = False
    
    # 持续循环：验证和修复（合并在一起），直到对角线ID一致
    round_num = 0
    while True:
        round_num = round_num + 1
        quick_print("--- 循环 " + str(round_num) + " ---")
        
        # 获取当前未验证数量
        unverified_set = wait_for(unverified_source)
        remaining = get_shared_set_size(unverified_set)
        
        # 智能启动对角线守卫：当剩余位置 <= 无人机数-2 时
        available_drones = max_drones()
        if not guards_started and remaining <= available_drones - 2 and remaining > 0:
            quick_print("=== 启动对角线守卫（剩余: " + str(remaining) + "）===")
            
            # 启动两个对角线守卫无人机
            diagonal_guards = []
            
            # 守卫1：左下角 (0, 0)
            def guard_task_0():
                return drone_diagonal_guard(0, 0, diagonal_source)
            
            guard_0 = spawn_drone(guard_task_0)
            if guard_0:
                diagonal_guards.append(guard_0)
                quick_print("对角线守卫1启动: (0,0)")
            
            # 守卫2：右上角 (n-1, n-1)
            def guard_task_max():
                return drone_diagonal_guard(world_size - 1, world_size - 1, diagonal_source)
            
            guard_max = spawn_drone(guard_task_max)
            if guard_max:
                diagonal_guards.append(guard_max)
                quick_print("对角线守卫2启动: (" + str(world_size-1) + "," + str(world_size-1) + ")")
            
            guards_started = True
        
        # 检查对角线守卫是否已经验证通过
        if guards_started:
            diagonal_state = wait_for(diagonal_source)
            if diagonal_state["ready"]:
                quick_print(">>> 对角线守卫报告：ID一致！立即收获 <<<")
                break
        
        # 验证和修复（合并阶段）
        if not stage_verify_and_fix(unverified_source):
            return False
        
        # 安全检查：避免无限循环
        if round_num > 100:
            quick_print("警告：超过100轮循环，可能出现问题")
            break
    
    # 等待对角线守卫完成（如果已启动）
    if diagonal_guards:
        quick_print("等待对角线守卫完成...")
        for guard in diagonal_guards:
            check_count = wait_for(guard)
            quick_print("守卫完成，检查次数: " + str(check_count))
    
    # 收获（使用 farm_utils 的方法）
    elapsed = get_time() - start
    quick_print("用时: " + str(elapsed) + "s")
    harvest_mega_pumpkin(world_size)
    
    quick_print("=== 完成 ===")
    return True

# ====================
# 主程序
# ====================

clear()
quick_print("=== 极简多无人机南瓜农场 ===")
quick_print("地图: " + str(world_size) + "x" + str(world_size))
quick_print("无人机: " + str(max_drones()))
quick_print("策略: 种满地图，对角ID一致后收获")
quick_print("共享内存: 通过 wait_for() 机制实现")
quick_print("")

cycle = 0
while True:
    cycle = cycle + 1
    quick_print(">>> 轮次 " + str(cycle) + " <<<")
    
    if not farming_cycle():
        quick_print("")
        quick_print("==================")
        quick_print("胡萝卜耗尽！")
        quick_print("完成: " + str(cycle - 1) + " 轮")
        quick_print("南瓜: " + str(num_items(Items.Pumpkin)))
        quick_print("==================")
        break
    
    quick_print("")
