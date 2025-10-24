import utilsFarm

mapSize = get_world_size()

snakeList = []
applePosition = None


def generate_hamiltonian():
    # 汉密尔顿回归路径计算 地图大小如果不是偶数会无解
    resultList = []
    for i in range(mapSize):
        for j in range(0, mapSize - 1):
            if i % 2 == 0:
                resultList.append((i, j + 1))
            else:
                resultList.append((i, mapSize - 1 - j))
    for k in range(mapSize):
        resultList.append((mapSize - k - 1, 0))
    return resultList


# 获取蛇头在指定位置，同时蛇在汉密尔顿回归路径上，返回蛇尾巴
def getSafeTarget(goalPosition, SnakeLen):
    global hamiltonDict
    global hamiltonListLen
    global hamiltonList
    lenth = hamiltonListLen
    index = hamiltonDict[goalPosition]
    index = index - SnakeLen + 1
    while index < 0:
        index += lenth
    tailPostion = hamiltonList[index % lenth]
    targetSnakeList = []
    while len(targetSnakeList) != SnakeLen:
        targetSnakeList.append(hamiltonList[index % lenth])
        index += 1
    return tailPostion, targetSnakeList


def neighbors(pos, obstacles=set()):
    # 返回 pos的邻居list
    r, c = pos[0], pos[1]
    result = []
    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < mapSize and 0 <= nc < mapSize:
            if (nr, nc) not in obstacles:
                result.append((nr, nc))
    return result


def getManhattanDistance(fromPosition, toPostion):
    # 返回两点之间的曼哈顿距离
    return abs(fromPosition[0] - toPostion[0]) + abs(fromPosition[1] - toPostion[1])


def bubble_sort(arr, targetPostion):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            # quick_print("计算"+str(j),getManhattanDistance(arr[j], targetPostion),getManhattanDistance(arr[j+1], targetPostion))
            if getManhattanDistance(arr[j], targetPostion) > getManhattanDistance(
                arr[j + 1], targetPostion
            ):
                tmp = arr[j + 1]
                arr[j + 1] = arr[j]
                arr[j] = tmp
    return arr


def get_shortest_path(start, goal):
    # quick_print("get_shortest_path", start, goal)
    path = []
    vHeadPostion = start
    tagetIndex = hamiltonDict[goal]
    vHeadIndex = hamiltonDict[vHeadPostion]
    xDif = goal[0] - vHeadPostion[0]
    yDif = goal[1] - vHeadPostion[1]
    # 1-情况 2个都在0行
    if goal[1] == 0 and vHeadPostion[1] == 0:
        if xDif > 0:
            for i in range(xDif + 1):
                path.append((vHeadPostion[0] + i, 1))
            path.add(goal)
            return path
        else:
            for i in range(1, abs(xDif) + 1):
                path.append((vHeadPostion[0] - i, 0))
            return path
    # 2-只有goal 在0行
    if goal[1] == 0 and vHeadPostion[1] > 0:
        # GOAL 在右边
        if xDif > 0:
            for i in range(1, xDif + 1):
                path.append((vHeadPostion[0] + i, vHeadPostion[1]))
            for j in range(vHeadPostion[1]):
                path.append((goal[0], vHeadPostion[1] - 1 - j))
            return path
        # GOAL 在左边
        else:
            # start奇数行
            tmp = -1
            if vHeadPostion[0] % 2 == 1:
                # y移动到底
                for j in range(vHeadPostion[1]):
                    path.append((vHeadPostion[0], vHeadPostion[1] - 1 - j))
                # x移动
                for i in range(1, abs(xDif) + 1):
                    path.append((vHeadPostion[0] + tmp * i, 0))
                return path
            else:  # start偶数行
                # 右边移动一格
                path.append((vHeadPostion[0] + 1, vHeadPostion[1]))
                # y移动到底
                for j in range(vHeadPostion[1]):
                    path.append((vHeadPostion[0] + 1, vHeadPostion[1] - 1 - j))
                path.append((vHeadPostion[0], 0))
                # x移动
                for i in range(1, abs(xDif) + 1):
                    path.append((vHeadPostion[0] + tmp * i, 0))
                return path
    # 3-有start 在0行
    if goal[1] > 0 and vHeadPostion[1] == 0:
        if xDif > 0:
            for i in range(1, abs(yDif) + 1):
                path.append((vHeadPostion[0], vHeadPostion[1] + i))
            for j in range(1, xDif + 1):
                path.append((vHeadPostion[0] + j, goal[1]))
            return path
        else:
            if yDif > 0:
                tmpY = 1
            else:
                tmpY = -1
            tmp = -1
            if goal[0] % 2 == 0:
                # 移动X
                for j in range(1, abs(xDif) + 1):
                    path.append((vHeadPostion[0] + tmp * j, 0))
                # y移动
                for i in range(1, abs(yDif) + 1):
                    path.append((goal[0], 0 + i))
                return path
            else:
                # 移动X
                for j in range(1, abs(xDif) + 1):
                    path.append((vHeadPostion[0] + tmp * j, 0))
                path.append((goal[0] - 1, 0))
                # y移动
                for i in range(1, abs(yDif) + 1):
                    path.append((goal[0] - 1, 0 + tmpY * i))
                path.append(goal)
                return path
    # 4 两个都不在0行
    if goal[1] > 0 and vHeadPostion[1] > 0:
        if yDif > 0:
            tmpY = 1
        else:
            tmpY = -1
        # 在右边
        if xDif > 1:
            # x移动
            for j in range(1, xDif):
                path.append((vHeadPostion[0] + j, vHeadPostion[1]))
            # y移动
            for i in range(1, abs(yDif) + 1):
                path.append((goal[0] - 1, vHeadPostion[1] + i * tmpY))
            path.append(goal)
            return path
        elif xDif == 1:
            if vHeadPostion[0] % 2 == 1:
                if yDif < 0:
                    # y移动
                    for i in range(1, abs(yDif) + 1):
                        path.append((goal[0] - 1, vHeadPostion[1] + i * tmpY))
                    path.append(goal)
                    return path
                else:
                    path.append((vHeadPostion[0] + 1, vHeadPostion[1]))
                    for i in range(1, abs(yDif) + 1):
                        path.append((goal[0], vHeadPostion[1] + i * tmpY))
                    return path
            else:
                if yDif > 0:
                    # y移动
                    for i in range(1, abs(yDif) + 1):
                        path.append((goal[0] - 1, vHeadPostion[1] + i * tmpY))
                    path.append(goal)
                    return path
                else:
                    path.append((vHeadPostion[0] + 1, vHeadPostion[1]))
                    for i in range(1, abs(yDif) + 1):
                        path.append((goal[0], vHeadPostion[1] + i * tmpY))
                    return path
        elif xDif == 0:
            for i in range(1, abs(yDif) + 1):
                path.append((goal[0], vHeadPostion[1] + i * tmpY))
            return path
        # 在左边
        else:
            if vHeadPostion[0] % 2 == 1:
                yStartPosition = vHeadPostion
            else:
                yStartPosition = (vHeadPostion[0] + 1, vHeadPostion[1])
                path.append(yStartPosition)

            # y移动到底
            for j in range(yStartPosition[1]):
                path.append((yStartPosition[0], yStartPosition[1] - 1 - j))
            path1 = get_shortest_path((yStartPosition[0], 0), goal)
            return path + path1


while num_items(Items.Bone) < 33488928:
    quick_print("###########开始#########")
    # 先犁地
    clear()
    # utilsFarm.makeMulTills()
    # do_a_flip()
    # 准备哈密尔顿路径常量
    hamiltonList = generate_hamiltonian()
    hamiltonDict = {}  # 空间复杂度换时间复杂度
    hamiltonListLen = len(hamiltonList)
    tmp = 0
    for i in range(len(hamiltonList)):
        hamiltonDict[hamiltonList[i]] = i

    # 到起始位置准备开始
    utilsFarm.moveTo(0, 0)
    change_hat(Hats.Dinosaur_Hat)
    applePosition = measure()
    utilsFarm.moveTo(0, 1)

    snakeList = [(0, 1), (0, 0)]
    tmpTime = get_time()
    while len(snakeList) <= 32 * 32:
        quick_print("蛇长", len(snakeList))
        targetPosition, targetSnakeList = getSafeTarget(applePosition, len(snakeList))

        targetIndex = hamiltonDict[targetPosition]
        headIndex = hamiltonDict[snakeList[0]]
        tailIndex = hamiltonDict[snakeList[-2]]
        isInSnake = False
        if headIndex >= targetIndex >= tailIndex:
            isInSnake = True
        if headIndex < tailIndex:
            if targetIndex <= headIndex or targetIndex >= tailIndex:
                isInSnake = True
        if not isInSnake:
            moveStep = get_shortest_path(snakeList[0], targetPosition)
            quick_print(
                "蛇头",
                snakeList[0],
                "安全点",
                targetPosition,
                "苹果",
                applePosition,
                "路径",
                moveStep,
                "蛇",
                targetSnakeList,
            )
            moveStep.pop()
            moveStep += targetSnakeList

            for i in moveStep:
                # quick_print(get_pos_x(), get_pos_y(), "移动到", i)
                utilsFarm.moveTo(i[0], i[1])
                snakeList.insert(0, i)
                tmp = snakeList.pop()
            applePosition = measure()
            while applePosition == None:
                applePosition = measure()
            snakeList.append(tmp)

            # quick_print(get_pos_x(), get_pos_y(), "蛇头", snakeList[0])
        else:
            quick_print(
                "安全点在蛇身体内 苹果在",
                applePosition,
                "当前",
                get_pos_x(),
                get_pos_y(),
                "蛇",
                snakeList,
            )
            oldLen = len(snakeList)

            while True:
                nextPosion = hamiltonList[
                    (hamiltonDict[snakeList[0]] + 1) % hamiltonListLen
                ]
                utilsFarm.moveTo(nextPosion[0], nextPosion[1])

                snakeList.insert(0, nextPosion)
                tmp = snakeList.pop()
                if applePosition == nextPosion:
                    applePosition = measure()
                    # 走的时候 正好吃到苹果
                    while applePosition == None:
                        applePosition = measure()
                        if oldLen >= 1024:
                            break
                    snakeList.append(tmp)
                    break

                if oldLen == 1024:
                    break
            if oldLen == 1024:
                break
    # while True:
    #     do_a_flip()
    change_hat(Hats.Brown_Hat)
    quick_print(num_items(Items.Bone))
    quick_print(num_items(Items.Bone) >= 33488928)
    quick_print(num_items(Items.Bone) - 33488928)

quick_print("###########结束#########")
