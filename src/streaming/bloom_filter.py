"""Probabilistic Bloom Filter for high-velocity IP stream membership testing.

Why Bloom Filters in Cyber Threat Streaming Analytics:
1. Space Efficiency: In high-velocity network streams with millions of unique IPs,
   maintaining a standard hash set requires gigabytes of RAM. A Bloom Filter represents
   set membership in a compact bit array using logarithmic space.
2. Query Speed: Membership testing is O(k) where k is the constant number of hash functions.
3. No False Negatives: If an IP has been processed by the pipeline, `contains(ip)` is guaranteed
   to return True.
4. Bounded False Positives: If `contains(ip)` returns True, there is a small, mathematically
   controlled probability (e.g. 1%) that the IP was not actually seen.
"""
import hashlib
import math
from typing import Any, Dict


class BloomFilter:
    """Configurable probabilistic Bloom Filter with optimal bit sizing and double hashing."""

    def __init__(self, capacity: int = 1000000, error_rate: float = 0.01):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than zero.")
        if not (0 < error_rate < 1):
            raise ValueError("Error rate must be between 0 and 1.")

        self.capacity = capacity
        self.error_rate = error_rate

        # Calculate optimal bit array size: m = - (n * ln(p)) / (ln(2)^2)
        self.num_bits = int(math.ceil(- (capacity * math.log(error_rate)) / (math.log(2) ** 2)))

        # Calculate optimal number of hash functions: k = (m / n) * ln(2)
        self.num_hashes = max(1, int(round((self.num_bits / capacity) * math.log(2))))

        # Byte array for bit storage (num_bits // 8 + 1 bytes)
        self.num_bytes = int(math.ceil(self.num_bits / 8))
        self.bit_array = bytearray(self.num_bytes)
        self.count = 0

    def _get_hashes(self, item: str):
        """Generate k distinct hash indices using double-hashing technique."""
        # Kirsch-Mitzenmacher optimization: g_i(x) = (h1(x) + i * h2(x)) mod m
        data = item.encode("utf-8")
        h1 = int(hashlib.sha256(data).hexdigest()[:16], 16)
        h2 = int(hashlib.md5(data).hexdigest()[:16], 16)

        for i in range(self.num_hashes):
            yield (h1 + i * h2) % self.num_bits

    def add(self, item: str) -> None:
        """Add an item (e.g. IP address) to the Bloom Filter."""
        for bit_index in self._get_hashes(item):
            byte_idx = bit_index // 8
            bit_offset = bit_index % 8
            self.bit_array[byte_idx] |= (1 << bit_offset)
        self.count += 1

    def contains(self, item: str) -> bool:
        """Test if item has appeared in the filter. Returns True if probably seen, False if definitely not."""
        for bit_index in self._get_hashes(item):
            byte_idx = bit_index // 8
            bit_offset = bit_index % 8
            if not (self.bit_array[byte_idx] & (1 << bit_offset)):
                return False
        return True

    def __contains__(self, item: str) -> bool:
        return self.contains(item)

    def current_fpp(self) -> float:
        """Estimate current false positive probability based on elements added."""
        if self.count == 0:
            return 0.0
        # Formula: (1 - e^(-k * n / m))^k
        exponent = - (self.num_hashes * self.count) / float(self.num_bits)
        return float((1.0 - math.exp(exponent)) ** self.num_hashes)

    def get_stats(self) -> Dict[str, Any]:
        """Return operational telemetry metrics for dashboard visualization."""
        # Count set bits
        set_bits = sum(bin(byte).count("1") for byte in self.bit_array)
        fill_ratio = (set_bits / self.num_bits) if self.num_bits > 0 else 0.0

        return {
            "capacity": self.capacity,
            "target_error_rate": self.error_rate,
            "elements_added": self.count,
            "num_bits": self.num_bits,
            "num_bytes": self.num_bytes,
            "num_hash_functions": self.num_hashes,
            "bits_set": set_bits,
            "fill_ratio": round(fill_ratio, 4),
            "current_fpp": round(self.current_fpp(), 6),
            "memory_usage_kb": round(self.num_bytes / 1024.0, 2)
        }

    def clear(self) -> None:
        """Reset the Bloom Filter bit array."""
        self.bit_array = bytearray(self.num_bytes)
        self.count = 0
