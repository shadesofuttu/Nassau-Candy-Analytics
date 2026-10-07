# Product Line Profitability & Margin Performance Analysis
## Nassau Candy Distributor Analytics Platform

### Overview
Advanced analytics platform for product profitability analysis, margin performance tracking, and data-driven business insights for Nassau Candy Distributor.

### Project Objectives
- Identify high-margin vs high-volume products
- Analyze profitability variance across product divisions
- Perform Pareto analysis for revenue and profit concentration
- Provide actionable insights for pricing and portfolio optimization

### Tech Stack
- **Backend:** Python 3.11+
- **Web Framework:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Database:** SQLite
- **Testing:** Pytest

### Project Structure
```
├── data/                   # Raw and processed datasets
├── src/
│   ├── analytics/          # Core analytics engine
│   ├── visualization/      # Chart and dashboard components
│   ├── utils/              # Helper functions
│   └── config/             # Configuration files
├── dashboard/              # Streamlit dashboard modules
├── notebooks/              # EDA and analysis notebooks
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation and reports
└── requirements.txt        # Dependencies
```

### Setup Instructions
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard/app.py
```

### Features
- 📊 Interactive profitability dashboards
- 📈 Division-level performance analysis
- 🎯 Pareto analysis (80/20 rule)
- 💰 Margin and profit contribution tracking
- 🔍 Product-level diagnostic insights
- 📋 Executive summary reports

### Analytics Modules
1. **Product Profitability Analysis**
2. **Division Performance Comparison**
3. **Profit Concentration Analysis**
4. **Cost Structure Diagnostics**
5. **Margin Risk Identification**

---
*Built for internship project demonstration*
```