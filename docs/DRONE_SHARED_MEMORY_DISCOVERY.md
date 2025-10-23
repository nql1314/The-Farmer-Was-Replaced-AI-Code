# 无人机共享内存技巧 - 重大发现！

## 发现日期
2025-10-23

## 突破性发现

虽然无人机之间**不能通过全局变量共享内存**，但可以通过 **`wait_for()` 返回值机制**实现跨无人机的共享内存！

## 核心机制

### 原理
1. 主程序生成一个"源无人机"，返回一个引用类型（列表/字典）
2. 多个"工作无人机"通过 `wait_for(源无人机)` 获取**同一个对象引用**
3. 所有工作无人机修改这个对象时，修改会相互可见
4. 实现了跨无人机的共享内存！

### 示例代码

```python
clear()

# 步骤1：创建返回共享对象的源无人机
def commonRet():
    return []  # 返回一个空列表

drone = spawn_drone(commonRet)

# 步骤2：工作无人机通过 wait_for 获取共享对象
def worker():
    sid = num_drones()
    do_a_flip()
    do_a_flip()
    do_a_flip()
    
    # 关键：所有 worker 等待同一个 drone，获得同一个列表引用
    data = wait_for(drone)
    
    # 修改共享列表
    data.append(sid)
    print(sid, data)

# 步骤3：生成多个工作无人机
for x in range(10):
    move(East)
    move(East)
    move(North)
    move(North)
    spawn_drone(worker)
    do_a_flip()
```

### 运行结果

```
2 [2]
3 [2,3]
4 [2,3,4]
5 [2,3,4,5]
5 [2,3,4,5,5]
5 [2,3,4,5,5,5]
5 [2,3,4,5,5,5,5]
5 [2,3,4,5,5,5,5,5]
5 [2,3,4,5,5,5,5,5,5]
5 [2,3,4,5,5,5,5,5,9,10]
```

**分析：**
- 列表从 `[]` 开始
- 每个 worker 都能看到之前 worker 的修改
- `[2,3,4,...]` 说明修改是累积的
- 证明了所有 worker 共享同一个列表对象！

## 技术细节

### 为什么这个方法有效？

```python
# 关键理解：
drone = spawn_drone(commonRet)  # drone 是一个"句柄"

# 在不同的 worker 中：
data = wait_for(drone)  # 所有 worker 等待同一个 drone
                        # wait_for() 返回 drone 执行的结果
                        # 因为 drone 只执行一次，返回一个列表
                        # 所有 worker 获得的是同一个列表对象的引用！
```

### 与之前测试的区别

**之前的测试（不共享）：**
```python
shared_list = [0, 0, 0]  # 主程序的全局变量

def modify():
    shared_list[0] = 100  # 修改闭包中捕获的副本

spawn_drone(modify)  # spawn 时复制了 shared_list
```

**新发现（共享）：**
```python
source = spawn_drone(lambda: [0, 0, 0])  # 源无人机

def modify():
    data = wait_for(source)  # 获取源无人机返回的对象引用
    data[0] = 100            # 修改的是同一个对象

spawn_drone(modify)  # 不是通过闭包，而是通过 wait_for 获取
```

## 实用模式

### 模式1：共享列表（收集数据）

```python
# 创建共享列表
def create_shared_list():
    return []

shared_list_drone = spawn_drone(create_shared_list)

# 多个工作者收集数据
def collect_data():
    results = []
    for i in range(10):
        if can_harvest():
            results.append(harvest())
        move(East)
    
    # 添加到共享列表
    data = wait_for(shared_list_drone)
    for item in results:
        data.append(item)
    
    return len(results)

# 启动多个收集者
for i in range(4):
    spawn_drone(collect_data)

# 主程序获取所有数据
do_a_flip()  # 等待工作完成
all_data = wait_for(shared_list_drone)
quick_print("Total items:", len(all_data))
```

### 模式2：共享字典（状态汇总）

```python
# 创建共享字典
def create_shared_dict():
    return {
        "grass": 0,
        "trees": 0,
        "empty": 0,
        "total": 0
    }

shared_dict_drone = spawn_drone(create_shared_dict)

# 工作者扫描区域并更新统计
def scan_zone():
    local_count = {"grass": 0, "trees": 0, "empty": 0}
    
    # 扫描 5x5 区域
    for y in range(5):
        for x in range(5):
            entity = get_entity_type()
            if entity == Entities.Grass:
                local_count["grass"] += 1
            elif entity == Entities.Tree:
                local_count["trees"] += 1
            else:
                local_count["empty"] += 1
            
            if x < 4:
                move(East)
        if y < 4:
            move(North)
            for _ in range(4):
                move(West)
    
    # 更新共享字典
    stats = wait_for(shared_dict_drone)
    stats["grass"] += local_count["grass"]
    stats["trees"] += local_count["trees"]
    stats["empty"] += local_count["empty"]
    stats["total"] += 25
    
    return local_count

# 启动多个扫描器
drones = []
for i in range(4):
    # 移动到不同区域...
    drone = spawn_drone(scan_zone)
    if drone:
        drones.append(drone)

# 等待所有完成
for drone in drones:
    wait_for(drone)

# 获取汇总结果
final_stats = wait_for(shared_dict_drone)
quick_print("Total grass:", final_stats["grass"])
quick_print("Total trees:", final_stats["trees"])
```

### 模式3：共享计数器

```python
# 创建共享计数器
def create_counter():
    return [0]  # 用列表包装，使其可修改

counter_drone = spawn_drone(create_counter)

# 工作者增加计数
def process_task():
    # 执行任务...
    result = do_work()
    
    # 增加共享计数器
    counter = wait_for(counter_drone)
    counter[0] += 1
    
    return result

# 启动多个工作者
for i in range(10):
    spawn_drone(process_task)

do_a_flip()

# 获取总完成数
counter = wait_for(counter_drone)
quick_print("Tasks completed:", counter[0])
```

### 模式4：任务队列（生产者-消费者）

```python
# 创建任务队列
def create_queue():
    return {
        "tasks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "results": []
    }

queue_drone = spawn_drone(create_queue)

# 消费者从队列获取任务
def worker():
    while True:
        queue = wait_for(queue_drone)
        
        # 获取任务（如果有）
        if len(queue["tasks"]) > 0:
            task = queue["tasks"][0]
            queue["tasks"] = queue["tasks"][1:]  # 移除第一个
        else:
            break  # 没有任务了
        
        # 处理任务
        result = process(task)
        
        # 存储结果
        queue["results"].append(result)
        
        do_a_flip()  # 给其他无人机机会

# 启动多个工作者
for i in range(3):
    spawn_drone(worker)

# 等待完成
do_a_flip()
do_a_flip()

# 获取所有结果
queue = wait_for(queue_drone)
quick_print("Results:", queue["results"])
```

## 重要注意事项

### ⚠️ 竞态条件风险

与传统共享内存一样，这个方法**有竞态条件风险**！

```python
# ❌ 危险：竞态条件
def unsafe_worker():
    data = wait_for(shared_drone)
    value = data["count"]      # 读取
    # 其他无人机可能在这里修改 data["count"]
    value += 1                 # 计算
    data["count"] = value      # 写入 - 可能覆盖其他无人机的修改

# ✅ 较安全：原子操作
def safer_worker():
    data = wait_for(shared_drone)
    data["count"] += 1  # 单步操作，减少竞态窗口（但仍不完全安全）

# ✅ 最安全：只追加，不修改
def safest_worker():
    data = wait_for(shared_drone)
    data.append(my_result)  # 追加是相对安全的
```

### 🎯 最佳实践

1. **只追加，不修改**
   ```python
   data = wait_for(shared)
   data.append(result)  # 安全
   ```

2. **使用独立的键**
   ```python
   data = wait_for(shared)
   drone_id = num_drones()
   data[drone_id] = result  # 每个无人机有自己的键
   ```

3. **避免读-修改-写序列**
   ```python
   # ❌ 危险
   count = data["count"]
   count += 1
   data["count"] = count
   
   # ✅ 更好
   data["count"] += 1
   ```

4. **尽量减少共享状态**
   - 只在必要时使用共享内存
   - 优先使用返回值汇总结果
   - 如果可以，让每个无人机独立工作

### 📊 性能考虑

**优势：**
- ✅ 无需等待所有无人机完成即可共享数据
- ✅ 实时更新，其他无人机可以看到最新状态
- ✅ 减少数据复制开销

**劣势：**
- ❌ 竞态条件风险
- ❌ 需要小心设计避免冲突
- ❌ 调试更困难

## 使用场景

### ✅ 适合使用共享内存的场景

1. **数据收集**：多个无人机收集数据到同一个列表
2. **统计汇总**：实时更新统计信息
3. **进度跟踪**：多个任务的完成进度
4. **结果聚合**：无需等待所有完成即可查看部分结果

### ❌ 不适合使用共享内存的场景

1. **需要强一致性**：银行账户类操作
2. **复杂的数据结构修改**：容易产生竞态
3. **可以用返回值的场景**：简单的数据汇总
4. **独立任务**：无需共享状态的并行任务

## 代码模板

### 完整的共享内存框架

```python
# ========================================
# 共享内存框架
# ========================================

# 1. 创建共享数据源
def create_shared_data():
    return {
        "results": [],      # 结果列表
        "counters": {},     # 计数器字典
        "status": "running" # 状态标志
    }

shared = spawn_drone(create_shared_data)

# 2. 工作者函数
def worker():
    drone_id = num_drones()
    
    # 执行任务
    local_results = []
    for i in range(10):
        # ... 工作逻辑 ...
        local_results.append(i)
    
    # 更新共享数据（安全模式：使用独立键）
    data = wait_for(shared)
    data["counters"][drone_id] = len(local_results)
    
    # 追加结果（相对安全）
    for result in local_results:
        data["results"].append(result)
    
    return drone_id

# 3. 主程序
drones = []
for i in range(4):
    drone = spawn_drone(worker)
    if drone:
        drones.append(drone)

# 4. 等待完成
for drone in drones:
    wait_for(drone)

# 5. 获取最终结果
final_data = wait_for(shared)
quick_print("Total results:", len(final_data["results"]))
quick_print("Worker counts:", final_data["counters"])
```

## 对比总结

| 特性 | 全局变量（不共享） | 返回值通信 | wait_for 共享内存 |
|------|------------------|-----------|------------------|
| 实现难度 | 简单 | 简单 | 中等 |
| 数据共享 | ❌ 不支持 | ⚠️ 单向 | ✅ 支持 |
| 实时性 | ❌ 无法实时 | ❌ 需等待完成 | ✅ 实时共享 |
| 竞态条件 | ✅ 无风险 | ✅ 无风险 | ⚠️ 有风险 |
| 使用场景 | 独立任务 | 结果汇总 | 实时协作 |
| 推荐度 | 不推荐 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 结论

这个发现揭示了 TFWR 无人机系统的一个强大特性：

- **通过 `wait_for()` 可以实现真正的跨无人机共享内存**
- **这是一个巧妙利用返回值引用的技巧**
- **使用时需要小心竞态条件**
- **适合需要实时协作的场景**

但要记住：**大多数情况下，使用返回值通信仍然是更安全、更简单的选择**。

共享内存应该作为高级技巧，只在确实需要实时协作时使用。

