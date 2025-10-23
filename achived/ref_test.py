clear()
def commonRet():
    return []
drone = spawn_drone(commonRet)
def worker():
    sid = num_drones()
    do_a_flip()
    do_a_flip()
    do_a_flip()
    data = wait_for(drone)
    data.append(sid)
    print(sid, data)
for x in range(10):
    move(East)
    move(East)
    move(North)
    move(North)
    spawn_drone(worker)
    do_a_flip()
