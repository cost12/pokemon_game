from typing import Any

def tuple_to_counts(tup:tuple[Any]) -> dict[Any,int]:
    """Takes in a list of hashable objects and returns a dict where each item is mapped to the number of times it appears

    :param lis: The list to consider
    :type lis: list
    :return: The counts of each object in the list
    :rtype: dict[Any,int]
    """
    r_dict = {}
    for x in tup:
        if x in r_dict:
            r_dict[x] += 1
        else:
            r_dict[x] = 1
    return r_dict