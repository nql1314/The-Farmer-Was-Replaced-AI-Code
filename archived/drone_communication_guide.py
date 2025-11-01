# 无人机通信指南 - 基于实际测试结果
# 结论：无人机完全隔离，只能通过返回值通信

# ========================================
# ❌ 错误模式：尝试共享内存
# ========================================

# 错误1：全局变量
results = []

def bad_collect_data():
    global results
    results.append(harvest())  # 这不会影响主程序的 results

# 错误2：列表引用
shared_list = [0, 0, 0]

def bad_modify_list():
    shared_list[0] = 100  # 这只修改了副本，不影响原列表

# 错误3：字典引用
shared_dict = {}

def bad_store_result():
    shared_dict["result"] = harvest()  # 这只修改了副本

# ========================================
# ✅ 正确模式：通过返回值通信
# ========================================

# 正确1：收集单个结果
def collect_harvest():
    items = harvest()
    return items

if num_unlocked(Unlocks.Megafarm) > 0:
    drone = spawn_drone(collect_harvest)
    result = wait_for(drone)  # 获取返回值
    quick_print("Harvested:", result)

# 正确2：收集多个数据
def collect_row_data():
    row_data = []
    for x in range(get_world_size()):
        if can_harvest():
            row_data.append([get_pos_x(), get_pos_y(), harvest()])
        move(East)
    return row_data

if num_unlocked(Unlocks.Megafarm) > 0:
    drone = spawn_drone(collect_row_data)
    data = wait_for(drone)
    quick_print("Row data:", data)

# 正确3：多无人机并行收集
def harvest_column():
    column_total = 0
    for y in range(get_world_size()):
        if can_harvest():
            column_total += harvest()
        move(North)
    return column_total

if num_unlocked(Unlocks.Megafarm) > 0:
    drones = []
    totals = []
    
    # 生成无人机收割每一列
    for x in range(get_world_size()):
        drone = spawn_drone(harvest_column)
        if drone:
            drones.append(drone)
            move(East)
        else:
            break
    
    # 收集所有结果
    for drone in drones:
        total = wait_for(drone)
        totals.append(total)
    
    # 计算总和
    grand_total = 0
    for t in totals:
        grand_total += t
    
    quick_print("Total harvested:", grand_total)

# ========================================
# ✅ 高级模式：返回复杂数据结构
# ========================================

# 返回字典（状态报告）
def scan_area():
    report = {
        "grass": 0,
        "trees": 0,
        "empty": 0,
        "positions": []
    }
    
    for y in range(get_world_size()):
        for x in range(get_world_size()):
            entity = get_entity_type()
            pos = [get_pos_x(), get_pos_y()]
            
            if entity == Entities.Grass:
                report["grass"] += 1
                report["positions"].append(pos)
            elif entity == Entities.Tree:
                report["trees"] += 1
            else:
                report["empty"] += 1
            
            if x < get_world_size() - 1:
                move(East)
        
        if y < get_world_size() - 1:
            move(North)
            for _ in range(get_world_size() - 1):
                move(West)
    
    return report

if num_unlocked(Unlocks.Megafarm) > 0:
    scanner = spawn_drone(scan_area)
    area_report = wait_for(scanner)
    
    quick_print("Grass count:", area_report["grass"])
    quick_print("Tree count:", area_report["trees"])
    quick_print("Empty count:", area_report["empty"])

# ========================================
# ✅ 实用模式：条件生成
# ========================================

def process_section():
    # 执行某些任务
    result = 0
    for i in range(10):
        if can_harvest():
            result += harvest()
        move(East)
    return result

# 如果能生成就生成，否则自己执行
if num_unlocked(Unlocks.Megafarm) > 0:
    drone = spawn_drone(process_section)
    if drone:
        result = wait_for(drone)
    else:
        # 无法生成更多无人机，自己执行
        result = process_section()
    
    quick_print("Result:", result)

# ========================================
# ✅ 最佳实践：并行处理大农场
# ========================================

def process_zone():
    # 每个无人机处理自己的区域
    count = 0
    
    # 假设已经移动到起始位置
    for y in range(5):  # 处理 5x5 区域
        for x in range(5):
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Carrot)
            
            if x < 4:
                move(East)
        
        if y < 4:
            move(North)
            for _ in range(4):
                move(West)
        
        count += 1
    
    return count

if num_unlocked(Unlocks.Megafarm) > 0:
    # 将大农场分成 4 个区域
    zones = [
        [0, 0],   # 左下
        [5, 0],   # 右下
        [0, 5],   # 左上
        [5, 5]    # 右上
    ]
    
    drones = []
    
    for zone_pos in zones:
        # 移动到区域起始位置
        # goto(zone_pos[0], zone_pos[1])
        
        drone = spawn_drone(process_zone)
        if drone:
            drones.append(drone)
    
    # 等待所有无人机完成
    results = []
    for drone in drones:
        result = wait_for(drone)
        results.append(result)
    
    quick_print("All zones processed:", results)

# ========================================
# 关键要点总结
# ========================================
# 1. 无人机之间完全隔离，没有共享内存
# 2. 全局变量、列表、字典都会被复制
# 3. 唯一的通信方式是通过返回值
# 4. 使用 wait_for() 获取无人机的返回值
# 5. 可以返回任何类型：数字、字符串、列表、字典等
# 6. 设计时应该让每个无人机独立工作，最后汇总结果
# ========================================

