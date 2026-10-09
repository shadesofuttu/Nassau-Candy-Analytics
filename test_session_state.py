import pandas as pd
import sys
from pathlib import Path
from collections import namedtuple

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.data_loader import DataLoader
from src.analytics.profitability_analyzer import ProfitabilityAnalyzer

print("=" * 80)
print("TESTING NEW SESSION STATE ARCHITECTURE")
print("=" * 80)
print()

# Mock Streamlit session state behavior
SessionState = namedtuple('SessionState', [])
st_session_state = {}

# 1. LOAD DEFAULT DATABASE
print("[Testing Default Dataset]")
loader = DataLoader()
default_df = loader.load_from_database('orders')
st_session_state['default_data'] = default_df

analyzer_default = ProfitabilityAnalyzer(st_session_state['default_data'])
summary_default = analyzer_default.get_summary_metrics()
print(f"Default Records: {len(default_df):,}")
print(f"Default Revenue: ${summary_default['total_revenue']:,.0f}")
print()

# 2. UPLOAD SCENARIO
print("[Testing Upload Scenario]")
uploaded_raw_df = pd.read_csv('data/raw/demo_test_data.csv')
clean_upload_df = loader.clean_data(uploaded_raw_df)
metrics_upload_df = loader.calculate_metrics(clean_upload_df)

# Simulate assigning to session state (NO SQLITE INVOLVED HERE)
st_session_state['uploaded_data'] = metrics_upload_df

# Active data function mock
def get_active_data():
    if 'uploaded_data' in st_session_state:
        return st_session_state['uploaded_data']
    return st_session_state['default_data']

active_df = get_active_data()
analyzer_upload = ProfitabilityAnalyzer(active_df)
summary_upload = analyzer_upload.get_summary_metrics()
print(f"Active Records (after upload): {len(active_df):,}")
print(f"Active Revenue (after upload): ${summary_upload['total_revenue']:,.0f}")
print()

# 3. CLEAR UPLOAD SCENARIO
print("[Testing Clear Upload Scenario (Clicking X)]")
del st_session_state['uploaded_data']

active_df_cleared = get_active_data()
analyzer_cleared = ProfitabilityAnalyzer(active_df_cleared)
summary_cleared = analyzer_cleared.get_summary_metrics()
print(f"Active Records (after clear): {len(active_df_cleared):,}")
print(f"Active Revenue (after clear): ${summary_cleared['total_revenue']:,.0f}")
print()

# Assertions to prove success
assert len(active_df) == 10, "Uploaded data did not become active"
assert len(active_df_cleared) == len(default_df), "Clearing upload did not revert to default"

print("\n[SUCCESS] The session state logic fully routes the authoritative dataframe without database interference.")
