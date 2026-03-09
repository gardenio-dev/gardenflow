"""Tests for gardenflow.core.dags."""

from gardenflow.core.dags import (
    GardenDAG,
    category_tag,
    gardenio_tag,
)


class TestCategoryTag:
    def test_returns_prefixed_string(self):
        assert category_tag("features") == "category:features"

    def test_nested_path(self):
        assert (
            category_tag("features/collections")
            == "category:features/collections"
        )


class TestGardenDAGCategories:
    """Test that GardenDAG correctly converts categories to tags."""

    _base = dict(
        dag_id="test",
        schedule=None,
        start_date=None,
        catchup=False,
    )

    def test_no_categories(self):
        dag = GardenDAG(**self._base)
        tag_names = {t for t in dag.tags}
        assert gardenio_tag() in tag_names
        assert not any(t.startswith("category:") for t in tag_names)

    def test_single_category_string(self):
        dag = GardenDAG(categories="data", **self._base)
        tag_names = {t for t in dag.tags}
        assert "category:data" in tag_names
        assert gardenio_tag() in tag_names

    def test_category_list(self):
        dag = GardenDAG(
            categories=["features/collections", "spatial"],
            **self._base,
        )
        tag_names = {t for t in dag.tags}
        assert "category:features/collections" in tag_names
        assert "category:spatial" in tag_names

    def test_duplicate_categories_not_added_twice(self):
        dag = GardenDAG(
            categories=["data", "data"],
            **self._base,
        )
        tag_list = [t for t in dag.tags if t == "category:data"]
        assert len(tag_list) == 1

    def test_categories_alongside_extra_tags(self):
        dag = GardenDAG(
            categories=["data"],
            tags=["custom"],
            **self._base,
        )
        tag_names = {t for t in dag.tags}
        assert "custom" in tag_names
        assert "category:data" in tag_names
        assert gardenio_tag() in tag_names
