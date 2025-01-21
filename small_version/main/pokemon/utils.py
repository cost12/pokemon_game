from typing import Any
from frozendict import frozendict
from dataclasses import dataclass, field

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

@dataclass(frozen=True)
class Collection[T]:
    collectibles: frozendict[T,int] = field(default_factory=frozendict[T,int])

    def size(self) -> int:
        return sum(self.collectibles.values())
    
    def size_of(self, item:T) -> int:
        return self.collectibles[item] if item in self.collectibles else 0 
    
    def unique(self) -> int:
        return len(self.collectibles)

    def add_item(self, item:T) -> 'Collection':
        collectibles_dict = dict(self.collectibles)
        if item in self.collectibles:
            collectibles_dict[item] += 1
        else:
            collectibles_dict[item] = 1        
        return Collection(frozendict(collectibles_dict))
    
    def add_items(self, items:'Collection') -> 'Collection':
        collectibles_dict = dict(self.collectibles)
        for item, count in items.collectibles.items():
            if item in collectibles_dict:
                collectibles_dict[item] += count
            else:
                collectibles_dict[item] = count
        return Collection(frozendict(collectibles_dict))

    def remove_item(self, item:T) -> 'Collection':
        collectibles_dict = dict(self.collectibles)
        if self.size_of(item) > 0:
            collectibles_dict[item] -= 1
            return Collection(frozendict(collectibles_dict))
        raise ValueError
    
    def remove_items(self, items:'Collection') -> 'Collection':
        collectibles_dict = dict(self.collectibles)
        for item, count in items.collectibles.items():
            if self.size_of(item) >= count:
                collectibles_dict[item] -= count
            else:
                raise ValueError
        return Collection(frozendict(collectibles_dict))
    
    def at_least_as_big(self, items:'Collection',*, ignore:T|None=None) -> bool:
        for item, count in items.collectibles.items():
            if count > self.size_of(item) and (ignore is None or not item == ignore):
                return False
        return self.size() >= items.size()