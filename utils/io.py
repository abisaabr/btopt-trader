from pathlib import Path
import pandas as pd

# >>> REPLACE THIS <<<
GCS_BUCKET = "gs://infra-throne-470123-k3-btopt"  # e.g., gs://btopt-results

def write_parquet_local(df: pd.DataFrame, path: str | Path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

def read_parquet_local(path: str | Path) -> pd.DataFrame:
    return pd.read_parquet(path)
