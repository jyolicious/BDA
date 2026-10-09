"""Unit tests for Bloom Filter probabilistic data structure."""
import pytest
from src.streaming.bloom_filter import BloomFilter


def test_bloom_filter_membership():
    bf = BloomFilter(capacity=1000, error_rate=0.01)

    ips = [f"192.168.1.{i}" for i in range(1, 100)]
    for ip in ips:
        bf.add(ip)

    # Standard Bloom Filter guarantees NO false negatives
    for ip in ips:
        assert bf.contains(ip) is True
        assert ip in bf

    # Unseen IP check (most should be False with 1% error rate)
    unseen_count = 0
    for i in range(101, 200):
        unseen_ip = f"10.200.50.{i}"
        if not bf.contains(unseen_ip):
            unseen_count += 1

    # At least 95% of unseen IPs must return False
    assert unseen_count >= 90


def test_bloom_filter_stats():
    bf = BloomFilter(capacity=5000, error_rate=0.01)
    bf.add("1.1.1.1")
    stats = bf.get_stats()
    assert stats["elements_added"] == 1
    assert stats["num_hash_functions"] > 0
    assert stats["memory_usage_kb"] > 0
