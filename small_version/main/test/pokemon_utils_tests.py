from pokemon.utils import tuple_to_counts

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