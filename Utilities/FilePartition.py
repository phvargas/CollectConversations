import sys


def make_partition(size, number_partitions):
    blocks = []
    value = size // number_partitions

    if number_partitions <= 1:
        return [0]

    if value < 1:
        print("Could not make partitions for {} elements. Partitions TOO small".format(number_partitions),
              file=sys.stderr)
        return blocks

    for k in range(number_partitions):
        blocks.append(k * value)

    return blocks


def get_partition_range(part_list, _part):
    start_end = []

    if _part == 0:
        print("First partition MUST be one (1) not {}".format(_part), file=sys.stderr)
        return [0]

    if _part > len(part_list):
        print("The part ({}) CANNOT be greater to the number of fractions".format(_part), file=sys.stderr)
        return [0]

    for k in range(_part - 1, _part + 1):
        start_end.append(part_list[k])

        if k + 1 >= len(part_list):
            return start_end

    return start_end
