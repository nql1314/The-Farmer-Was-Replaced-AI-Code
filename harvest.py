def harvest_all():
    for y in range(get_world_size()):
        for x in range(get_world_size()):
            if can_harvest():
                harvest()
            move(East)
        move(North)
        
harvest_all()