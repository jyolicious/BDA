"""Frequent Item / Heavy-Hitters streaming detection.

Implements the Space-Saving Algorithm (Metwally et al.) to identify
dominant source IPs in real-time streams with O(1) update time and O(k) bounded memory.
"""
from collections import defaultdict
from typing import Any, Dict, List, Tuple


class FrequentItemTracker:
    """Bounded-memory Heavy Hitters tracker using the Space-Saving streaming algorithm."""

    def __init__(self, max_tracked: int = 100, decay_factor: float = 1.0):
        self.max_tracked = max_tracked
        self.decay_factor = decay_factor
        # ip -> (count, error_bound)
        self.counts: Dict[str, int] = defaultdict(int)
        self.error_bounds: Dict[str, int] = defaultdict(int)
        self.total_processed = 0

    def update(self, item: str, weight: int = 1) -> None:
        """Process an observed item (source IP) in the stream."""
        self.total_processed += weight

        if item in self.counts:
            self.counts[item] += weight
        elif len(self.counts) < self.max_tracked:
            self.counts[item] = weight
            self.error_bounds[item] = 0
        else:
            # Space-Saving replacement: find item with minimum estimated frequency
            min_item = min(self.counts, key=self.counts.get)
            min_count = self.counts[min_item]

            # Evict min_item and replace with current item
            del self.counts[min_item]
            del self.error_bounds[min_item]

            self.counts[item] = min_count + weight
            self.error_bounds[item] = min_count

    def get_top_k(self, k: int = 10) -> List[Dict[str, Any]]:
        """Return the top-k highest frequency items with frequency estimates and error bounds."""
        sorted_items = sorted(self.counts.items(), key=lambda x: x[1], reverse=True)[:k]
        result = []
        for rank, (item, count) in enumerate(sorted_items, 1):
            err = self.error_bounds.get(item, 0)
            pct = (count / self.total_processed * 100.0) if self.total_processed > 0 else 0.0
            result.append({
                "rank": rank,
                "item": item,
                "estimated_count": count,
                "error_bound": err,
                "stream_percentage": round(pct, 2)
            })
        return result

    def get_item_frequency(self, item: str) -> int:
        """Return current estimated frequency for an item."""
        return self.counts.get(item, 0)

    def decay(self, factor: float = 0.9) -> None:
        """Apply exponential decay to track concept drift across time windows."""
        for item in list(self.counts.keys()):
            self.counts[item] = int(self.counts[item] * factor)
            if self.counts[item] <= 0:
                del self.counts[item]
                if item in self.error_bounds:
                    del self.error_bounds[item]

    def reset(self) -> None:
        """Clear all frequency state."""
        self.counts.clear()
        self.error_bounds.clear()
        self.total_processed = 0
