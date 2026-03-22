import pytest
import time
from app.services.cache import SimpleCache, hash_request


class TestSimpleCache:
    def test_get_nonexistent_key(self):
        cache = SimpleCache()
        result = cache.get("nonexistent")
        assert result is None

    def test_set_and_get(self):
        cache = SimpleCache()
        cache.set("key1", "value1")
        result = cache.get("key1")
        assert result == "value1"

    def test_set_overwrites_existing(self):
        cache = SimpleCache()
        cache.set("key1", "value1")
        cache.set("key1", "value2")
        result = cache.get("key1")
        assert result == "value2"

    def test_ttl_expiration(self):
        cache = SimpleCache(ttl=1)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_ttl_not_expired(self):
        cache = SimpleCache(ttl=2)
        cache.set("key1", "value1")
        time.sleep(0.5)
        assert cache.get("key1") == "value1"

    def test_max_size_eviction(self):
        cache = SimpleCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_clear(self):
        cache = SimpleCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_stats(self):
        cache = SimpleCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        stats = cache.stats()
        assert stats["size"] == 2
        assert stats["max_size"] == 100
        assert stats["ttl"] == 300

    def test_stats_empty_cache(self):
        cache = SimpleCache()
        stats = cache.stats()
        assert stats["size"] == 0

    def test_complex_value_types(self):
        cache = SimpleCache()
        cache.set("dict", {"key": "value"})
        cache.set("list", [1, 2, 3])
        cache.set("int", 42)
        assert cache.get("dict") == {"key": "value"}
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("int") == 42


class TestHashRequest:
    def test_same_data_same_hash(self):
        data1 = {"name": "John", "age": 30}
        data2 = {"name": "John", "age": 30}
        assert hash_request(data1) == hash_request(data2)

    def test_different_data_different_hash(self):
        data1 = {"name": "John", "age": 30}
        data2 = {"name": "Jane", "age": 25}
        assert hash_request(data1) != hash_request(data2)

    def test_order_independent(self):
        data1 = {"name": "John", "age": 30}
        data2 = {"age": 30, "name": "John"}
        assert hash_request(data1) == hash_request(data2)

    def test_nested_objects(self):
        data1 = {"user": {"name": "John", "age": 30}}
        data2 = {"user": {"name": "John", "age": 30}}
        assert hash_request(data1) == hash_request(data2)

    def test_empty_dict(self):
        data = {}
        hash_val = hash_request(data)
        assert isinstance(hash_val, str)
        assert len(hash_val) > 0

    def test_hash_is_hexadecimal(self):
        data = {"test": "value"}
        hash_val = hash_request(data)
        assert all(c in "0123456789abcdef" for c in hash_val)

    def test_hash_length_sha256(self):
        data = {"test": "value"}
        hash_val = hash_request(data)
        assert len(hash_val) == 64  # SHA256 produces 64 hex characters
