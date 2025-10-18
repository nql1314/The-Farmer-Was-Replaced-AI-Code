# The Farmer Was Replaced - 6x6农场优化脚本
# 策略：树间隔种植（每隔2格）、胡萝卜、草均衡分配
# 树需要四周不相邻，避免生长速度降低

# 全局变量
world_size = get_world_size()

# 辅助函数：检查是否应该种树（间隔模式，确保不相邻）
def should_plant_tree(x, y):
    # 每隔2格种一棵树（行和列都间隔）
    # 模式：(0,0) (0,3) (3,0) (3,3)...
    # 这样树在东西南北四个方向都不相邻
    return x % 3 == 0 and y % 3 == 0

# 辅助函数：蛇形遍历并执行操作
def traverse_and_plant():
    for y in range(world_size):
        for x in range(world_size):
            # 收割成熟的植物
            if can_harvest():
                harvest()
            
            # 决定种植什么
            if should_plant_tree(x, y):
                # 间隔位置种树（四周不相邻）
                plant(Entities.Tree)
            
            else:
                # 非树位置：在草和胡萝卜之间交替
                if (x + y) % 3 == 1:
                    # 种植胡萝卜（需要土壤）
                    if get_ground_type() != Grounds.Soil:
                        till()
                    plant(Entities.Carrot)
                    # 浇水加速生长（水不足时才浇）
                    if get_water() < 0.5:
                        use_item(Items.Water)
                
                else:
                    # 种植草（快速生长，填充剩余空间）
                    plant(Entities.Grass)
            
            # 蛇形移动
            if x < world_size - 1:
                if y % 2 == 0:
                    move(East)
                else:
                    move(West)
        
        # 移动到下一行
        if y < world_size - 1:
            move(North)

# 主循环
while True:
    traverse_and_plant()
