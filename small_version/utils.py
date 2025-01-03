from typing import Any

def list_to_counts(lis:list[Any]) -> dict[Any,int]:
    """Takes in a list of hashable objects and returns a dict where each item is mapped to the number of times it appears

    :param lis: The list to consider
    :type lis: list
    :return: The counts of each object in the list
    :rtype: dict[Any,int]
    """
    r_dict = {}
    for x in lis:
        if x in r_dict:
            r_dict[x] += 1
        else:
            r_dict[x] = 1
    return r_dict