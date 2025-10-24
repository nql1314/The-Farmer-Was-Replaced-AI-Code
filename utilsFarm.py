currentSize = get_world_size()


def moveTo(targetX, targetY):
    # 移动到目标坐标
    # Args:
    #     areaX (整数): 目标坐标X
    #     areaY (整数): 目标坐标y
    # 获取当前位置
    currentX, currentY = get_pos_x(), get_pos_y()
    # 计算横向移动参数
    dx = abs(targetX - currentX)
    if dx < currentSize - dx:
        # 往近的方向移动
        if targetX > currentX:
            dirX = East
        else:
            dirX = West
        moveStepX = dx
    else:
        if targetX < currentX:
            dirX = East
        else:
            dirX = West
        moveStepX = currentSize - dx
    # 计算纵向移动参数
    dy = abs(targetY - currentY)
    if dy < currentSize - dy:
        # 往近的方向移动
        if targetY > currentY:
            dirY = North
        else:
            dirY = South
        moveStepY = dy
    else:
        if targetY < currentY:
            dirY = North
        else:
            dirY = South
        moveStepY = currentSize - dy
    # 执行横向移动
    for _ in range(moveStepX):
        if not move(dirX):
            quick_print('移动出错',get_pos_x(), get_pos_y())
    # 执行纵向移动
    for _ in range(moveStepY):
       
        if not  move(dirY):
            quick_print('移动出错',get_pos_x(), get_pos_y())



# 把所有地till一遍
def makeMulTills():
    
    def tillTask():
        while True:
            if get_ground_type() == Grounds.Grassland:
                till()
                # plant(Entities.Cactus)
                move(East)            
            else:
                break

    for i in range(get_world_size()):
        moveTo(0,get_world_size()-1-i)
        if not spawn_drone(tillTask):
            tillTask()


# 把所有地till一遍
def makeTills():
    for j in range(currentSize):
        for i in range(currentSize):
            if get_entity_type() == Entities.Grass:
                till()
                move(North)
        move(East)


# 所有点位都种某植物
def plantAll(Object):
    for j in range(currentSize):
        for i in range(currentSize):
            plant(Object)
            move(North)
        move(East)


def getMoveListByArea(areaX, areaY):
    # 使用哈密尔顿回归路径 或 当无解时使用最近似路径
    # Args:
    #     areaX (整数): 区域x长度
    #     areaY (整数): 区域y长度
    # Returns:
    #     list: 移动路径列表

    moveList = []
    for i in range(areaX - 1):
        moveList.append(East)
    moveList.append(North)
    for i in range(areaX - 2):
        for j in range(areaY - 2):
            if i % 2 == 0:
                moveList.append(North)
            else:
                moveList.append(South)
        moveList.append(West)
    if areaX % 2 == 0:
        for j in range(areaY - 2):
            moveList.append(North)
        moveList.append(West)
        for j in range(areaY - 2):
            moveList.append(South)
    else:
        for i in range(areaY - 1):
            if i % 2 == 0:
                moveList.append(West)
            else:
                moveList.append(East)
            moveList.append(South)
        moveList.pop()
    return moveList


def zigzagTraversal(size):
    # 蛇形遍历坐标list
    # Args:
    #     aresizeaX (整数): 区域大小
    # Returns:
    #     list: 蛇形遍历坐标列表
    x = 0
    y = 0
    resultList = []
    for i in range(1, 2 * size):
        step = 2 * (i % 2) - 1
        # tag = int(i / size)
        if i >= size:
            tag = 1
        else:
            tag = 0
        for j in range(abs(i % size - tag * size)):
            resultList.append((x, y))
            x += step
            y -= step

        if step > 0:
            y += 1 + tag
            x -= tag
        else:
            x += 1 + tag
            y -= tag
    return resultList
    