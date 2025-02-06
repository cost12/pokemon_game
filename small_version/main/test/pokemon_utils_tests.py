from pokemon.utils import tuple_to_counts
from pokemon.utils import PriorityQueue

def test_empty():
    tup = tuple()
    dic = tuple_to_counts(tup)
    assert len(dic) == 0

def test_single():
    tup = ("hi",)
    dic = tuple_to_counts(tup)
    assert len(dic) == 1
    assert dic["hi"] == 1

def test_many():
    tup = ("hi","hi","a","a","a","B")
    dic = tuple_to_counts(tup)
    assert dic["hi"] == 2
    assert dic["a"] == 3
    assert dic["B"] == 1

def test_pq():
    pq = PriorityQueue[str]()
    pq.push(5, 'a')
    pq.push(3, 'c')
    pq.push(3, 'b')
    pq.push(10, 'z')
    pq.push(1, 'z')
    assert pq.size() == 5
    assert pq.pop() == 'z'
    assert pq.pop() == 'c'
    assert pq.size() == 3
    assert pq.top() == 'b'
    assert pq.size() == 3
    assert pq.pop() == 'b'
    assert pq.pop() == 'a'
    assert pq.pop() == 'z'