PATH_6X6 = {
    (0, 0): [North, North, North, North, North, East, East, South, West, South, East, South, West, South, East, South, West, West],
    (0, 1): [North, North, North, North, East, East, South, West, South, East, South, West, South, East, South, West, West, North],
    (0, 2): [North, North, North, East, East, South, West, South, East, South, West, South, East, South, West, West, North, North],
    (0, 3): [North, North, East, East, South, West, South, East, South, West, South, East, South, West, West, North, North, North],
    (0, 4): [North, East, East, South, West, South, East, South, West, South, East, South, West, West, North, North, North, North],
    (0, 5): [East, East, South, West, South, East, South, West, South, East, South, West, West, North, North, North, North, North],
    (1, 5): [East, South, West, South, East, South, West, South, East, South, West, West, North, North, North, North, North, East],
    (2, 5): [South, West, South, East, South, West, South, East, South, West, West, North, North, North, North, North, East, East],
    (2, 4): [West, South, East, South, West, South, East, South, West, West, North, North, North, North, North, East, East, South],
    (1, 4): [South, East, South, West, South, East, South, West, West, North, North, North, North, North, East, East, South, West],
    (1, 3): [East, South, West, South, East, South, West, West, North, North, North, North, North, East, East, South, West, South],
    (2, 3): [South, West, South, East, South, West, West, North, North, North, North, North, East, East, South, West, South, East],
    (2, 2): [West, South, East, South, West, West, North, North, North, North, North, East, East, South, West, South, East, South],
    (1, 2): [South, East, South, West, West, North, North, North, North, North, East, East, South, West, South, East, South, West],
    (1, 1): [East, South, West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South],
    (2, 1): [South, West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East],
    (2, 0): [West, West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East, South],
    (1, 0): [West, North, North, North, North, North, East, East, South, West, South, East, South, West, South, East, South, West]
}

clear()
quick_print(get_tick_count())
path = PATH_6X6[(get_pos_x() - 0, get_pos_y() - 0)]
quick_print(get_tick_count())
for direction in path:
    if get_ground_type() != Grounds.Soil:
        till()
    plant(Entities.Pumpkin)
    move(direction)


# 阶段2：扫描未成熟南瓜
unverified = []
for direction in path:
    if not can_harvest():
        plant(Entities.Pumpkin)
        unverified.append((get_pos_x(), get_pos_y()))
        use_item(Items.Water)
    move(direction)