# 最后一轮优化策略说明

## 问题背景

在南瓜挑战中，目标是达到 200M 南瓜。但在最后一轮，不需要所有无人机都种植自己的区域，因为：
1. 总产量已经接近目标（195M）
2. 完成快的无人机可以帮助慢的区域
3. 减少无人机等待时间，提高整体效率

## 优化方案

### 核心思路

**分阶段策略**：
- **正常阶段**（0-195M）：每个无人机负责自己的 6x6 区域
- **最后一轮**（195M-200M）：完成的无人机转为"帮手模式"，协助其他区域

### 关键机制

#### 1. 阈值触发机制
```python
FINAL_ROUND_THRESHOLD = 195000000  # 195M 触发最后一轮
TARGET = 200000000  # 200M 目标
```

当任意无人机检测到南瓜数量达到 195M 时：
- 设置全局标志 `shared["final_round"] = True`
- 所有无人机进入最后一轮模式

#### 2. 全局任务池（Global Task Pool）
```python
shared = {
    "global_task_pool": [],  # [(x, y, region_x, region_y), ...]
    "final_round": False,
    "completed_drones": 0,
}
```

**任务池作用**：
- 收集所有未成熟的南瓜位置
- 供空闲无人机认领和处理
- 使用"最近任务优先"策略

#### 3. 无人机模式切换

**正常模式**：
1. 种植自己区域的 18 个位置
2. 扫描未成熟南瓜
3. 验证和补种（本地处理）
4. 收获

**最后一轮模式触发条件**（当 `pumpkin_count >= 195M`）：
- ✅ 设置全局标志 `shared["final_round"] = True`
- ⚠️ **但不影响当前轮次的正常流程**

**最后一轮完整流程**：
1. ✅ 种植自己区域（正常执行）
2. ✅ 扫描未成熟南瓜（正常执行）
3. ✅ 验证和补种（正常执行，不跳过）
4. ✅ 收获（正常执行）
5. 🔄 **收获完成后**检查：如果 `final_round=True` 且 `pumpkin_count >= 195M`，转为"帮手模式"

**关键设计原则**：
- ⚠️ **绝不在完成收获前提前退出或跳过任何步骤**
- ✅ 只在收获完成后才判断是否转为帮手模式
- ✅ 确保每个无人机都完整完成自己区域的当前轮次

**帮手模式**（`final_round_helper`）：
```python
while True:
    if pumpkin_count >= TARGET:
        return  # 达标，退出
    
    # 1. 从任务池获取最近的任务
    task = get_nearest_task(shared, current_x, current_y)
    
    # 2. 处理任务
    if task:
        process_task(task_x, task_y)
    else:
        # 3. 没有任务，帮忙验证其他区域
        help_other_regions()
```

### 算法详解

#### 执行时机（重要！）

```python
# worker_left 的执行流程
while True:
    # 阶段1：种植（正常执行）
    plant_all()
    
    # 阶段2：扫描（正常执行）
    scan_unverified()
    
    # 可能触发最后一轮标志
    if pumpkin_count >= 195M:
        shared["final_round"] = True
    
    # 阶段3：验证和补种（正常执行，不跳过！）
    verify_and_replant()  # 即使 final_round=True 也要完成
    
    # 阶段4：收获（正常执行）
    harvest()
    
    # ⭐ 关键检查点：收获完成后
    if pumpkin_count >= TARGET:
        return  # 达标退出
    
    if shared["final_round"] and pumpkin_count >= 195M:
        # 转为帮手模式
        final_round_helper()
        return
    
    # 否则继续下一轮
```

**为什么必须完成当前轮次？**
1. **保证产量**：跳过验证会导致该轮次产量降低
2. **避免浪费**：已种植的南瓜必须收获才能计入总数
3. **同步问题**：左右无人机需要同步，提前退出会破坏同步
4. **效率最优**：完成当前轮次比留下未完成任务更高效

#### 最近任务选择算法（Manhattan Distance）

```python
def get_nearest_task(shared, current_x, current_y):
    task_pool = shared["global_task_pool"]
    best_distance = 999999
    
    for task in task_pool:
        task_x, task_y, _, _ = task
        distance = manhattan_distance(current_x, current_y, task_x, task_y)
        if distance < best_distance:
            best_distance = distance
            best_task = task
    
    # 移除并返回最近的任务
    task_pool.remove(best_task)
    return best_task
```

**为什么用曼哈顿距离？**
- 游戏中移动是按方向（上下左右）进行的
- 曼哈顿距离 = |dx| + |dy| 准确反映移动成本
- 考虑环形地图：`dx = min(abs(x2-x1), 32-abs(x2-x1))`

#### 任务处理流程

```python
def process_task(task_x, task_y):
    goto(task_x, task_y)
    entity = get_entity_type()
    
    if entity == Entities.Pumpkin:
        if not can_harvest():
            # 浇水 → 施肥 → 验证
            if get_water() < THRESHOLD:
                use_item(Items.Water)
            while not can_harvest():
                use_item(Items.Fertilizer)
            # 如果还是未成熟，补种
            if not can_harvest():
                plant(Entities.Pumpkin)
                use_water_and_fertilizer()
                return False  # 任务失败，需要重新加入任务池
    
    elif entity == Entities.Dead_Pumpkin:
        plant(Entities.Pumpkin)
        use_water_and_fertilizer()
        return False  # 需要重新处理
    
    return True  # 任务完成
```

### 优化效果预估

#### 时间节省分析

**假设场景**：
- 16 个区域，32 个无人机
- 最后一轮有 10% 的南瓜未成熟（约 160 个位置）
- 平均每个位置需要 2 个验证周期

**传统方式**（每个无人机处理自己区域）：
- 每个区域约有 10 个未成熟南瓜
- 最慢的区域可能有 15 个
- 最快完成时间：10 × 2 × 500 ticks = 10,000 ticks
- 最慢完成时间：15 × 2 × 500 ticks = 15,000 ticks
- **总时间 = 最慢的那个 = 15,000 ticks**

**优化方式**（任务池协作）：
- 完成快的无人机（16 个）立即帮忙
- 160 个任务由 32 个无人机共同处理
- 平均每个无人机：160 / 32 = 5 个任务
- **总时间 ≈ 5 × 2 × 500 ticks = 5,000 ticks**

**时间节省：15,000 - 5,000 = 10,000 ticks（约 66% 提升）**

### 竞态条件处理

#### 问题：多个无人机同时访问任务池

**解决方案 1：原子操作**
```python
# 使用 pop() 而不是 remove()
task = task_pool.pop(best_index)  # 原子操作，线程安全
```

**解决方案 2：任务失败重试**
```python
if not process_task(task):
    # 任务失败，重新加入任务池
    shared["global_task_pool"].append(task)
```

**解决方案 3：任务验证**
```python
# 处理任务前先检查
goto(task_x, task_y)
if can_harvest():
    return True  # 已被其他无人机处理，跳过
```

### 边界情况处理

#### 1. 任务池为空
```python
if not task:
    # 尝试帮忙验证其他区域的 unverified 列表
    for region in all_regions:
        if region["unverified_left"]:
            help(region, "unverified_left")
            break
    else:
        # 真的没事做了，等待或快进
        do_a_flip()
```

#### 2. 提前达标
```python
# 在每个关键点检查
pumpkin_count = num_items(Items.Pumpkin)
if pumpkin_count >= TARGET:
    clear()  # 清理场地
    return  # 退出
```

#### 3. 阈值调整
```python
# 如果 195M 太晚，可以降低到 190M
# 如果 195M 太早，可以提高到 197M
# 需要根据实际测试调整
FINAL_ROUND_THRESHOLD = 195000000
```

## 使用方法

### 1. 直接运行
```python
# 在游戏中运行 pumpkin_v4.py
# 脚本会自动检测并切换到最后一轮模式
```

### 2. 监控日志
```python
# 关键日志输出：
# [FINAL_ROUND] Activated at 195123456 pumpkins
# [worker_left] 7 19 Entering helper mode at 195234567
# [final_round_helper] Drone at region 7 19 entering helper mode
```

### 3. 调整参数
```python
# 在文件开头修改：
FINAL_ROUND_THRESHOLD = 190000000  # 更早进入（更保守）
FINAL_ROUND_THRESHOLD = 197000000  # 更晚进入（更激进）
```

## 性能优化建议

### 1. 阈值选择
- **太低（如 180M）**：浪费正常阶段的并行性
- **太高（如 198M）**：来不及协作，效果不明显
- **推荐：195M**（还剩 5M，约 2.5%，足够协作但不浪费）

### 2. 任务池策略
- ✅ **最近任务优先**：减少移动成本
- ❌ **先进先出（FIFO）**：可能导致长距离移动
- ❌ **随机选择**：效率不稳定

### 3. 帮手模式触发时机
```python
# 当前实现：完成自己区域后立即转为帮手
if shared["final_round"] and pumpkin_count >= FINAL_ROUND_THRESHOLD:
    final_round_helper()

# 可选实现：只有快的无人机才帮忙（前 50%）
if shared["final_round"] and shared["completed_drones"] < 16:
    final_round_helper()
```

## 预期效果

### 场景 1：均衡分布
- 所有区域同时完成
- 效果：**提升 30-40%**（减少最后的等待时间）

### 场景 2：不均衡分布
- 部分区域有大量枯萎南瓜
- 效果：**提升 50-70%**（快的帮助慢的）

### 场景 3：极端不均衡
- 个别区域严重落后
- 效果：**提升 70-90%**（集中火力攻坚）

## 后续优化方向

### 1. 动态阈值
```python
# 根据未成熟南瓜数量动态调整
unverified_count = count_all_unverified()
if unverified_count < 50:
    THRESHOLD = 198000000  # 很少，可以晚一点
else:
    THRESHOLD = 195000000  # 很多，早点开始
```

### 2. 任务优先级
```python
# 给任务添加优先级
# 优先处理多次失败的任务
task = {
    "x": x, "y": y,
    "retry_count": 0,
    "priority": 0
}
```

### 3. 区域负载均衡
```python
# 记录每个区域的工作负载
# 优先帮助负载最重的区域
region_load = {
    (0, 7): len(region["unverified_left"]) + len(region["unverified_right"])
}
```

## 注意事项

1. **共享内存安全**：
   - 使用 `pop()` 而不是 `remove()` 来避免竞态
   - 任务失败时重新加入任务池

2. **性能监控**：
   - 使用 `quick_print()` 记录关键时间点
   - 比较优化前后的总时间

3. **阈值调试**：
   - 首次运行建议用 195M
   - 根据日志调整（太早/太晚）

4. **边界条件**：
   - 检查任务池是否为空
   - 检查是否提前达标
   - 处理枯萎南瓜的特殊情况

## 总结

这个优化方案通过"最后一轮协作机制"，将无人机从固定区域模式转换为动态任务池模式，显著提高了整体效率。核心优势是：

1. ✅ **零浪费**：完成快的无人机不再等待
2. ✅ **就近帮忙**：减少移动成本
3. ✅ **动态平衡**：自动处理不均衡情况
4. ✅ **提前达标**：预计节省 10,000-15,000 ticks

预期总时间从 ~30 秒降低到 ~25 秒，提升约 **15-20%**。

