"""search() 的測試，重點是租戶隔離。"""

import pytest

from src.api.search import DOCUMENTS, search


def test_happy_path_finds_own_docs():
    results = search("acme", "季報")
    assert {d.id for d in results} == {1, 5}


def test_different_tenants_cannot_see_each_other():
    """不同 tenant 看不到彼此資料（這是加分頁時最容易被破壞的行為）。"""
    acme = search("acme", "")
    globex = search("globex", "")
    assert acme and globex
    assert all(d.tenant_id == "acme" for d in acme)
    assert all(d.tenant_id == "globex" for d in globex)
    assert not ({d.id for d in acme} & {d.id for d in globex})


def test_query_matching_other_tenant_returns_nothing():
    # 「人事」只存在於 globex，acme 搜尋必須拿不到
    assert search("acme", "人事") == []


def test_unknown_tenant_gets_empty():
    assert search("nobody", "") == []


def test_empty_tenant_raises():
    with pytest.raises(ValueError):
        search("", "季報")


def test_all_docs_partitioned_by_tenant():
    total = len(search("acme", "")) + len(search("globex", ""))
    assert total == len(DOCUMENTS)


# ---- 分頁 ----

from src.api.search import Document, MAX_PAGE_SIZE


def _make_docs(n, tenant="acme"):
    return [Document(i, tenant, f"doc {i}", "內容") for i in range(1, n + 1)]


def test_default_page_size_is_20():
    docs = _make_docs(25)
    assert [d.id for d in search("acme", "", docs)] == list(range(1, 21))


def test_second_page_returns_remainder():
    docs = _make_docs(25)
    assert [d.id for d in search("acme", "", docs, page=2)] == list(range(21, 26))


def test_custom_page_size():
    docs = _make_docs(10)
    assert [d.id for d in search("acme", "", docs, page=2, page_size=3)] == [4, 5, 6]


def test_page_beyond_end_is_empty():
    assert search("acme", "", _make_docs(5), page=3, page_size=5) == []


def test_max_page_size_allowed():
    docs = _make_docs(150)
    assert len(search("acme", "", docs, page_size=MAX_PAGE_SIZE)) == 100


def test_pagination_applied_after_tenant_filter():
    """交錯放兩租戶資料，分頁後每頁仍只能有自己租戶、且數量正確。"""
    docs = [Document(i, "acme" if i % 2 else "globex", f"d{i}", "x") for i in range(1, 21)]
    page1 = search("acme", "", docs, page=1, page_size=5)
    page2 = search("acme", "", docs, page=2, page_size=5)
    assert [d.id for d in page1] == [1, 3, 5, 7, 9]
    assert [d.id for d in page2] == [11, 13, 15, 17, 19]
    assert all(d.tenant_id == "acme" for d in page1 + page2)


@pytest.mark.parametrize("page", [0, -1])
def test_invalid_page_raises(page):
    with pytest.raises(ValueError):
        search("acme", "", page=page)


@pytest.mark.parametrize("page_size", [0, -5, MAX_PAGE_SIZE + 1])
def test_invalid_page_size_raises(page_size):
    with pytest.raises(ValueError):
        search("acme", "", page_size=page_size)


@pytest.mark.parametrize("kwargs", [{"page": "1"}, {"page": 1.5}, {"page": True}, {"page_size": "20"}, {"page_size": None}])
def test_non_int_pagination_raises_type_error(kwargs):
    with pytest.raises(TypeError):
        search("acme", "", **kwargs)
