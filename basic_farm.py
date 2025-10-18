# The Farmer Was Replaced - 基础资源种植脚本
# 专门种植：干草（Hay）、木头（Wood）、胡萝卜（Carrot）
# 优化策略：蛇形遍历，智能作物分配

world_size = get_world_size()

# 辅助函数：检查是否应该种树（间隔种植）
def should_plant_tree(x, y):
    #树每隔3格种植，避免相邻减速#
    return x % 3 == 0 and y % 3 == 0

# 主遍历和种植函数
def farm_cycle():
    #一次蛇形遍历完成收割和种植#
    for y in range(world_size):
        for x in range(world_size):
            # 收割成熟的植物
            if can_harvest():
                harvest()
            
            # 决定种植什么
            if should_plant_tree(x, y):
                # 间隔位置种树（四周不相邻，避免生长减速）
                plant(Entities.Tree)
            
            elif (x + y) % 3 == 1:
                # 种植胡萝卜（约33%位置）
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Carrot)
                
                # 智能浇水（水位低于50%时浇水）
                if get_water() < 0.5:
                    if num_items(Items.Water) > 0:
                        use_item(Items.Water)
                
                # 使用肥料加速（如果有富余）
                if num_items(Items.Fertilizer) > 10:
                    use_item(Items.Fertilizer)
            
            else:
                # 种植草（快速生长，填充剩余空间）
                plant(Entities.Grass)
            
            # 蛇形移动（最后一个位置不移动）
            if not (y == world_size - 1 and x == world_size - 1):
                if x < world_size - 1:
                    # 向右或向左移动
                    if y % 2 == 0:
                        move(East)
                    else:
                        move(West)
                else:
                    # 移动到下一行
                    move(North)

# 显示库存状态
def show_inventory():
    #显示当前资源库存#
    clear()
    quick_print("=== 资源库存 ===")
    quick_print("干草: " + str(num_items(Items.Hay)))
    quick_print("木头: " + str(num_items(Items.Wood)))
    quick_print("胡萝卜: " + str(num_items(Items.Carrot)))
    quick_print("水: " + str(num_items(Items.Water)))
    quick_print("肥料: " + str(num_items(Items.Fertilizer)))

# 主循环
while True:
    # 显示当前库存
    show_inventory()
    
    # 执行一次完整的农场循环
    farm_cycle()
    
    # 可选：等待一段时间让植物生长
    # do_a_flip()

