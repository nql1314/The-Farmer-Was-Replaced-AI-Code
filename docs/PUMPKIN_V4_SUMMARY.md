# Pumpkin V4 - 最后一轮优化总结

## 核心改进

在达到 195M 南瓜后，完成收获的无人机转为"帮手模式"，协助其他区域完成最后 5M 的冲刺。

## 关键设计原则 ⭐

### 1. 完整完成当前轮次
```python
# ❌ 错误：提前退出
if final_round:
    add_to_task_pool()  # 跳过验证
    goto_help_others()  # 未完成收获

# ✅ 正确：完成后再转
plant() → scan() → verify() → harvest()  # 完整流程
if final_round and pumpkin_count >= 195M:
    goto_help_others()  # 收获后才帮忙
```

**原因**：
- 保证当前轮次产量（不浪费已种植的南瓜）
- 维持左右无人机同步
- 避免破坏正常流程效率

### 2. 两阶段触发机制

**阶段1：标志设置**（195M 时）
```python
if pumpkin_count >= 195M and not shared["final_round"]:
    shared["final_round"] = True  # 只设置标志
    # 但继续当前轮次！
```

**阶段2：模式切换**（收获后）
```python
harvest()  # 先完成收获
if shared["final_round"] and pumpkin_count >= 195M:
    final_round_helper()  # 才转为帮手
```

## 执行流程图

```
开始循环
    ↓
种植 18 个位置
    ↓
扫描未成熟南瓜
    ↓
[检查] 是否 >= 195M? → 是 → 设置 final_round = True
    ↓                          ↓
    否 ← ← ← ← ← ← ← ← ← ← ← ← ←
    ↓
验证和补种（正常执行，不跳过！）
    ↓
收获
    ↓
[检查] 是否 >= 200M? → 是 → 退出
    ↓
    否
    ↓
[检查] final_round && >= 195M? → 是 → 转帮手模式 → 退出
    ↓
    否
    ↓
回到开始（下一轮）
```

## 帮手模式工作流程

```python
def final_round_helper(shared, my_region_x, my_region_y):
    while True:
        # 1. 检查是否达标
        if num_items(Items.Pumpkin) >= 200M:
            return
        
        # 2. 获取最近的任务
        task = get_nearest_task(shared, get_pos_x(), get_pos_y())
        
        # 3. 处理任务
        if task:
            process_task(task)
        else:
            # 4. 没有任务，帮忙验证其他区域
            help_other_regions()
```

## 优化效果

### 场景示例

**传统方式**（各自完成）：
- 快的区域：5 轮完成，18×5=90 个南瓜
- 慢的区域：8 轮完成，18×8=144 个南瓜（有枯萎）
- **总时间 = 8 轮**

**优化方式**（协作完成）：
- 前 5 轮：所有区域正常执行
- 快的完成后（5 轮）：转帮手，协助慢的区域
- 16 个帮手 + 原区域无人机 → 快速完成剩余 3 轮
- **总时间 ≈ 6 轮**（节省 25%）

### 预期提升

- **均衡情况**：15-20% 提升
- **不均衡情况**：30-50% 提升
- **极端情况**：50-70% 提升

## 关键参数

```python
FINAL_ROUND_THRESHOLD = 195000000  # 195M 触发
TARGET = 200000000                  # 200M 目标
```

### 调整建议

- **太保守**（190M）：浪费前期并行性，提前转帮手但效果不明显
- **太激进**（198M）：来不及协作，剩余时间太少
- **推荐**（195M）：还剩 5M（2.5%），足够协作空间

## 代码要点

### Worker Left（左侧无人机）

```python
while True:
    # 正常流程（不受 final_round 影响）
    plant_all()
    scan_unverified()
    verify_and_replant()
    harvest()
    
    # 收获后检查
    if pumpkin_count >= TARGET:
        return  # 达标
    
    if shared["final_round"] and pumpkin_count >= 195M:
        final_round_helper()  # 转帮手
        return
```

### Worker Right（右侧无人机）

```python
while True:
    # 正常流程
    plant_all()
    scan_unverified()
    verify_and_replant()
    
    # 设置 ready 标志（让左边收获）
    region_data["ready"] = True
    
    # 不收获，直接检查是否转帮手
    if pumpkin_count >= TARGET:
        return
    
    if shared["final_round"] and pumpkin_count >= 195M:
        final_round_helper()
        return
```

## 竞态条件处理

### 任务池访问
```python
# 使用 pop() 原子操作
task = task_pool.pop(best_index)  # 安全

# 任务失败重试
if not process_task(task):
    shared["global_task_pool"].append(task)
```

### 完成标志
```python
# 每个无人机独立计数
shared["completed_drones"] += 1
```

## 监控和调试

### 关键日志
```python
# 最后一轮触发
quick_print("[FINAL_ROUND] Activated at", pumpkin_count)

# 无人机转为帮手
quick_print("[worker_left]", x, y, "Entering helper mode at", count)

# 任务处理
quick_print("[helper] Processing task at", task_x, task_y)
```

### 性能测量
```python
# 记录关键时间点
start_time = get_time()
# ... 运行脚本 ...
quick_print("Total time:", get_time() - start_time)
```

## 注意事项

1. ✅ **绝不跳过当前轮次的任何阶段**
2. ✅ **只在收获完成后才判断模式切换**
3. ✅ **保持左右无人机同步**
4. ✅ **检查达标条件在每个关键点**
5. ⚠️ **任务池操作使用原子方法**
6. ⚠️ **处理任务失败的重试逻辑**

## 快速对比

| 特性 | V3（原版） | V4（优化版） |
|------|-----------|------------|
| 工作模式 | 固定区域 | 动态协作 |
| 最后一轮 | 各自完成 | 互相帮助 |
| 任务分配 | 无 | 全局任务池 |
| 任务选择 | - | 最近优先 |
| 流程完整性 | ✅ | ✅（关键！） |
| 预期提升 | - | 15-50% |

## 总结

V4 版本的核心是"**完成后协作**"而不是"**提前帮忙**"：

- ✅ 保证每个无人机完整完成当前轮次
- ✅ 收获后才判断是否转为帮手模式
- ✅ 使用全局任务池实现动态负载均衡
- ✅ 最近任务优先减少移动成本

这样既保证了正常流程的效率，又充分利用了完成快的无人机的空闲时间，实现了最优的协作效果。

