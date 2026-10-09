import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.utils.data_loader import DataLoader

loader = DataLoader()
# Load original CSV
raw_df = pd.read_csv('data/raw/Nassau Candy Distributor.csv')
clean_df = loader.clean_data(raw_df)
metrics_df = loader.calculate_metrics(clean_df)

# Overwrite the db
loader.load_to_database(metrics_df, 'orders')
print(f"Database restored successfully! {len(metrics_df):,} records injected.")
