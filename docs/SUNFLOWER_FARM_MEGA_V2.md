# 向日葵农场多无人机版本 V2 - 共享内存架构

## 📋 概述

优化后的向日葵能量农场，采用共享内存机制实现多无人机协同工作，最大化5倍能量奖励。

## 🎯 核心优化

### 1. 共享内存架构

参考南瓜农场的实现，使用 `wait_for()` 机制实现真正的共享内存：

```python
# 创建共享跟踪器（所有无人机共享）
tracker_source = spawn_drone(create_shared_sunflower_tracker)
stats_source = spawn_drone(create_shared_stats)

# 工作无人机访问共享数据
def drone_scan_and_track_batch(batch, tracker_source):
    tracker = wait_for(tracker_source)  # 获取共享引用
    # 所有无人机操作同一个 tracker
    add_sunflower_to_tracker(tracker, x, y, petals)
```

### 2. 实时跟踪机制

**共享向日葵跟踪器结构：**
```python
{
    "位置键": (花瓣数, x, y),
    "0,0": (12, 0, 0),
    "1,0": (15, 1, 0),
    ...
}
```

**优势：**
- ✅ 所有无人机实时更新同一个跟踪器
- ✅ 自动去重（同一位置只记录一次）
- ✅ 快速查询最大花瓣数
- ✅ 按花瓣数分组收获

### 3. 共享统计数据

```python
{
    "total_sunflowers": 0,    # 总向日葵数
    "mature_count": 0,         # 成熟数量
    "max_petals": 0,           # 最大花瓣数
    "harvested": 0,            # 已收获数量
    "bonus_count": 0,          # 5倍奖励次数
    "power_gained": 0          # 获得能量
}
```

**优势：**
- ✅ 多个收获无人机同时更新统计
- ✅ 实时追踪5倍奖励次数
- ✅ 精确计算能量收益

## 🏗️ 架构设计

### 阶段流程

```
1. 种植阶段（并行）
   ├─ 条带分配（每个无人机负责连续的几行）
   ├─ 并行种植整个地图
   └─ 返回种植数量

2. 扫描和收获循环
   ├─ 扫描阶段（并行）
   │  ├─ 条带分配扫描区域
   │  ├─ 并行扫描成熟向日葵
   │  └─ 更新共享跟踪器
   │
   ├─ 收获阶段（并行）
   │  ├─ 从跟踪器中按花瓣数分组
   │  ├─ 优先收获最大花瓣（15→14→...→7）
   │  ├─ 并行收获同一花瓣数的向日葵
   │  ├─ 实时更新共享统计
   │  └─ 剩余<10株时停止（保留等待）
   │
   └─ 循环直到所有成熟向日葵收获完毕
```

### 条带分配策略

**问题：** 如何最小化无人机移动距离？

**解决方案：** 条带分配（Strip Assignment）

```python
# 示例：10x10 地图，3个无人机
# 无人机1：行0-3（蛇形：0从左到右，1从右到左...）
# 无人机2：行4-6
# 无人机3：行7-9

def split_batches_by_strips(num_batches):
    # 每个无人机负责连续的几行
    # 使用蛇形遍历最小化移动
    for y in range(start_y, end_y):
        if y % 2 == 0:
            # 偶数行：从左到右
        else:
            # 奇数行：从右到左
```

**优势：**
- ✅ 无人机路径不重叠
- ✅ 最小化移动距离
- ✅ 自动负载均衡

## 🎮 5倍奖励策略

### 奖励条件

```python
# 条件1：农场上至少有10株成熟向日葵
# 条件2：收获花瓣数最多的那株

get_bonus = (remaining >= 10) and (petals == max_petals)
```

### 最大化策略

1. **按花瓣数降序收获**
   - 15瓣 → 14瓣 → 13瓣 → ... → 7瓣
   - 确保每次收获都是当前最大花瓣数

2. **剩余<10株时停止**
   - 保留<10株的向日葵
   - 等待更多成熟后继续收获
   - 避免浪费5倍奖励机会

3. **并行收获同一花瓣数**
   - 例如：有20株15瓣向日葵
   - 分配给4个无人机并行收获
   - 所有20株都获得5倍奖励

### 示例流程

```
扫描结果：
- 15瓣：5株
- 14瓣：8株  
- 13瓣：12株
- 12瓣：6株
总计：31株

收获流程：
1. 收获15瓣（5株，满足5倍）
   剩余：26株
   
2. 收获14瓣（8株，满足5倍）
   剩余：18株
   
3. 收获13瓣（12株，满足5倍）
   剩余：6株
   
4. 停止收获（剩余6株<10）
   保留12瓣向日葵等待更多成熟

结果：25株获得5倍奖励！
```

## 🔧 关键函数

### 共享内存工具

```python
# 添加向日葵到跟踪器
add_sunflower_to_tracker(tracker, x, y, petals)

# 从跟踪器移除
remove_sunflower_from_tracker(tracker, x, y)

# 获取最大花瓣数
max_petals = get_max_petals_from_tracker(tracker)

# 获取指定花瓣数的所有位置
positions = get_sunflowers_by_petals(tracker, 15)
```

### 无人机工作函数

```python
# 扫描并跟踪
def drone_scan_and_track_batch(batch, tracker_source):
    tracker = wait_for(tracker_source)
    for pos in batch:
        # 扫描并添加到共享跟踪器
        add_sunflower_to_tracker(tracker, x, y, petals)
    return scanned_count

# 收获位置
def drone_harvest_positions(positions, tracker_source, stats_source):
    tracker = wait_for(tracker_source)
    stats = wait_for(stats_source)
    for pos in positions:
        # 收获并更新共享数据
        harvest()
        remove_sunflower_from_tracker(tracker, x, y)
        stats["harvested"] += 1
    return harvested
```

## 📊 性能对比

### V1 vs V2

| 特性 | V1（旧版） | V2（共享内存版） |
|------|-----------|-----------------|
| 扫描方式 | 区域扫描，返回列表 | 实时跟踪，共享字典 |
| 数据同步 | 主无人机合并列表 | 所有无人机共享引用 |
| 收获协调 | 路径优化 | 并行收获 |
| 5倍奖励 | 手动计算剩余 | 实时跟踪剩余 |
| 内存效率 | 多份副本 | 单一共享副本 |
| 扩展性 | 受限于列表合并 | 无限扩展 |

### 预期提升

- **扫描速度**: 4-6x（4-6个无人机并行）
- **收获速度**: 3-5x（并行收获）
- **5倍奖励率**: +20-30%（更智能的停止策略）
- **总体效率**: 5-8x

## 🎯 使用场景

### 何时使用

✅ **推荐使用 V2：**
- 已解锁多无人机（Unlocks.Megafarm）
- 地图大小 ≥ 6×6
- 需要快速获得大量能量
- 追求最高效率

### 配置建议

```python
# 最佳配置
- 地图大小：10×10 或更大
- 无人机数量：4-8个
- 向日葵数量：100+株

# 预期产出（每轮）
- 收获：80-100株
- 5倍奖励：60-80次
- 能量：300-500+
- 用时：20-40秒
```

## 🔍 调试和监控

### 实时统计

```python
quick_print("扫描到: " + str(scanned) + " 株成熟向日葵")
quick_print("收获 " + str(count) + " 株 " + str(petals) + " 瓣（5倍奖励）")
quick_print("剩余 " + str(remaining) + " 株（<10），停止收获")
quick_print("本轮总计：收获 " + str(stats["harvested"]) + " 株，5倍 " + str(stats["bonus_count"]) + " 次")
```

### 性能指标

```python
start = get_time()
farming_cycle(tracker_source, stats_source)
elapsed = get_time() - start
quick_print("用时: " + str(elapsed) + "s")
```

## 🚀 优化技巧

### 1. 动态批次大小

```python
# 根据可用无人机数量动态调整批次大小
available = max_drones() + 1
batch_size = len(positions) // available
```

### 2. 智能等待

```python
# 第一次扫描没有成熟的，等待一会儿
if scanned == 0 and round_num == 1:
    quick_print("等待向日葵成熟...")
    do_a_flip()
```

### 3. 剩余管理

```python
# 剩余<10株时停止，保留等待更多成熟
if remaining > 0 and remaining < 10:
    quick_print("剩余 " + str(remaining) + " 株未收获（保留等待更多成熟）")
```

### 4. 安全检查

```python
# 避免无限循环
if round_num > 50:
    quick_print("警告：超过50轮循环，结束本轮")
    break
```

## 🔬 技术细节

### 共享内存机制

**原理：**
```python
# 源无人机创建并返回对象
def create_shared_sunflower_tracker():
    return {}  # 返回一个字典

# 源无人机被 spawn
tracker_source = spawn_drone(create_shared_sunflower_tracker)

# 所有工作无人机通过 wait_for 获取同一个引用
tracker = wait_for(tracker_source)

# 修改会立即对所有无人机可见
tracker["0,0"] = (15, 0, 0)  # 其他无人机也能看到
```

**关键点：**
- ✅ 引用类型（字典、列表）会共享
- ⚠️ 值类型（数字、字符串）不会共享
- ✅ 多次 `wait_for()` 同一个源获得同一个引用

### 竞态条件处理

**问题：** 多个无人机同时修改同一个字典

**解决方案：** 使用独立键

```python
# ❌ 危险：竞态条件
stats["count"] = stats["count"] + 1

# ✅ 安全：原子操作
stats["count"] += 1

# ✅ 最安全：独立键
key = str(x) + "," + str(y)
tracker[key] = (petals, x, y)
```

## 📝 常见问题

### Q1: 为什么使用字符串作为字典键？

**A:** 因为元组作为键在游戏中可能不稳定，字符串更可靠：

```python
# 使用字符串键
key = str(x) + "," + str(y)  # "0,0", "1,0" 等
tracker[key] = (petals, x, y)
```

### Q2: 如何处理快速成熟的向日葵？

**A:** 使用滚动收获循环：

```python
while True:
    # 扫描成熟的
    scanned = stage_scan_and_track(tracker_source)
    
    if scanned == 0:
        break  # 没有更多成熟的
    
    # 收获
    stage_harvest_by_petals(tracker_source, stats_source)
```

### Q3: 为什么剩余<10株时停止？

**A:** 保护5倍奖励机会：

- 如果继续收获，剩余<10株后无法获得5倍奖励
- 停止后等待更多成熟，可以继续享受5倍奖励
- 最大化能量收益

### Q4: 共享内存会导致冲突吗？

**A:** 使用独立键避免冲突：

```python
# 每个位置有唯一的键
key = str(x) + "," + str(y)

# 不同位置不会冲突
tracker["0,0"] = (15, 0, 0)
tracker["1,0"] = (12, 1, 0)
```

## 🎓 学习要点

### 核心概念

1. **共享内存通过 wait_for() 实现**
   - 所有无人机获取同一个对象引用
   - 修改立即对所有无人机可见

2. **条带分配最小化移动**
   - 每个无人机负责连续的几行
   - 蛇形遍历避免重复移动

3. **实时跟踪提高效率**
   - 共享跟踪器记录所有成熟向日葵
   - 避免重复扫描

4. **智能停止最大化奖励**
   - 剩余<10株时停止收获
   - 等待更多成熟后继续

### 可复用模式

此模式可应用于其他需要实时协调的场景：

- ✅ 实时库存管理
- ✅ 动态任务分配
- ✅ 协同搜索算法
- ✅ 多目标优先级队列

## 📚 相关文档

- [南瓜农场 V2](PUMPKIN_FARM_MEGA_V2.md) - 共享内存模式参考
- [持久化无人机池](PERSISTENT_DRONE_POOL.md) - 无人机管理
- [V1 vs V2 对比](V1_VS_V2_COMPARISON.md) - 架构演进

## 🎉 总结

V2 版本通过引入共享内存机制，实现了真正的多无人机协同工作：

- ✅ **实时协调**：所有无人机共享同一个跟踪器
- ✅ **并行效率**：扫描和收获都并行执行
- ✅ **智能优化**：动态调整策略最大化5倍奖励
- ✅ **可扩展性**：无缝支持更多无人机

这是目前最高效的向日葵能量农场实现！🌻⚡

