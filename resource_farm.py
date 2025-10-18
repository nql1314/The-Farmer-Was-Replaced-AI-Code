# The Farmer Was Replaced - 智能资源平衡种植脚本
# 根据资源需求动态调整种植策略

world_size = get_world_size()

# 资源目标配置
TARGET_HAY = 1000
TARGET_WOOD = 500
TARGET_CARROT = 500

# 辅助函数：获取当前最缺的资源
def get_most_needed_crop():
    #返回当前最需要种植的作物#
    hay_ratio = num_items(Items.Hay) / TARGET_HAY
    wood_ratio = num_items(Items.Wood) / TARGET_WOOD
    carrot_ratio = num_items(Items.Carrot) / TARGET_CARROT
    
    # 找出比例最低的资源
    if hay_ratio <= wood_ratio and hay_ratio <= carrot_ratio:
        return "grass"
    elif wood_ratio <= carrot_ratio:
        return "tree"
    else:
        return "carrot"

# 优化的蛇形遍历种植
def smart_farm_cycle():
    #根据资源需求智能种植#
    priority = get_most_needed_crop()
    
    for y in range(world_size):
        for x in range(world_size):
            # 收割
            if can_harvest():
                harvest()
            
            # 根据优先级和位置决定种植
            if priority == "tree":
                # 优先木头：更多树（间隔2格）
                if x % 2 == 0 and y % 2 == 0:
                    plant(Entities.Tree)
                elif (x + y) % 2 == 0:
                    if get_ground_type() != Grounds.Soil:
                        till()
                    plant(Entities.Carrot)
                else:
                    plant(Entities.Grass)
            
            elif priority == "carrot":
                # 优先胡萝卜：更多胡萝卜
                if (x + y) % 2 == 0:
                    if get_ground_type() != Grounds.Soil:
                        till()
                    plant(Entities.Carrot)
                    if get_water() < 0.5 and num_items(Items.Water) > 0:
                        use_item(Items.Water)
                elif x % 3 == 0 and y % 3 == 0:
                    plant(Entities.Tree)
                else:
                    plant(Entities.Grass)
            
            else:  # priority == "grass"
                # 优先干草：更多草
                if x % 3 == 0 and y % 3 == 0:
                    plant(Entities.Tree)
                elif (x + y) % 4 == 0:
                    if get_ground_type() != Grounds.Soil:
                        till()
                    plant(Entities.Carrot)
                else:
                    plant(Entities.Grass)
            
            # 蛇形移动
            if not (y == world_size - 1 and x == world_size - 1):
                if x < world_size - 1:
                    if y % 2 == 0:
                        move(East)
                    else:
                        move(West)
                else:
                    move(North)

# 显示状态
def show_status():
    clear()
    quick_print("=== 资源状态 ===")
    
    hay = num_items(Items.Hay)
    wood = num_items(Items.Wood)
    carrot = num_items(Items.Carrot)
    
    quick_print("干草: " + str(hay) + "/" + str(TARGET_HAY))
    quick_print("木头: " + str(wood) + "/" + str(TARGET_WOOD))
    quick_print("胡萝卜: " + str(carrot) + "/" + str(TARGET_CARROT))
    
    # 显示当前优先级
    priority = get_most_needed_crop()
    if priority == "grass":
        quick_print("优先: 干草")
    elif priority == "tree":
        quick_print("优先: 木头")
    else:
        quick_print("优先: 胡萝卜")

# 主循环
while True:
    show_status()
    smart_farm_cycle()

