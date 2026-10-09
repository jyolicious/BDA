"""Dataset persistence and streaming loader utilities."""
import csv
from pathlib import Path
from typing import Generator, Iterable, List, Union
import pandas as pd
from src.data.schema import EVENT_SCHEMA_FIELDS, NetworkEvent


class DatasetLoader:
    """Manages reading, writing, and transforming NetworkEvent datasets."""

    @staticmethod
    def save_csv(
        events: Iterable[NetworkEvent],
        filepath: Union[str, Path],
        include_header: bool = True
    ) -> int:
        """Write events to CSV file with schema headers."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        count = 0
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if include_header:
                writer.writerow(EVENT_SCHEMA_FIELDS)
            for event in events:
                writer.writerow(event.to_tuple())
                count += 1
        return count

    @staticmethod
    def load_csv(filepath: Union[str, Path]) -> Generator[NetworkEvent, None, None]:
        """Stream NetworkEvents from CSV file line by line."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if not row:
                    continue
                yield NetworkEvent(
                    timestamp=row[0],
                    source_ip=row[1],
                    destination_ip=row[2],
                    source_port=int(row[3]),
                    destination_port=int(row[4]),
                    protocol=row[5],
                    packet_count=int(row[6]),
                    bytes_sent=int(row[7]),
                    bytes_received=int(row[8]),
                    duration_ms=int(row[9]),
                    connection_status=row[10],
                    attack_label=row[11]
                )

    @staticmethod
    def to_dataframe(events: Iterable[NetworkEvent]) -> pd.DataFrame:
        """Convert an iterable of events to a typed Pandas DataFrame."""
        rows = [ev.to_tuple() for ev in events]
        return pd.DataFrame(rows, columns=EVENT_SCHEMA_FIELDS)
