"""
Data loading and preprocessing utilities
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import sqlite3
from src.config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_PATH


class DataLoader:
    """
    Handle data loading, validation, and preprocessing
    """
    
    def __init__(self):
        self.raw_data_dir = RAW_DATA_DIR
        self.processed_data_dir = PROCESSED_DATA_DIR
        
    def load_raw_data(self, filename: str) -> pd.DataFrame:
        """
        Load raw data from CSV or Excel file
        
        Args:
            filename: Name of the file in raw data directory
            
        Returns:
            pandas DataFrame
        """
        file_path = self.raw_data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate data
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        # For numeric columns, fill with 0 or appropriate value
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # For categorical columns, fill with 'Unknown'
        categorical_cols = df.select_dtypes(include=['object']).columns
        df[categorical_cols] = df[categorical_cols].fillna('Unknown')
        
        # Validate cost and sales values
        if 'Cost' in df.columns and 'Sales' in df.columns:
            # Remove records with invalid values
            df = df[(df['Cost'] >= 0) & (df['Sales'] >= 0)]
            
        # Ensure date columns are datetime
        date_columns = ['Order Date', 'Ship Date', 'Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate profitability metrics
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            DataFrame with calculated metrics
        """
        df = df.copy()
        
        # Calculate Gross Profit if not present
        if 'Gross Profit' not in df.columns and 'Sales' in df.columns and 'Cost' in df.columns:
            df['Gross Profit'] = df['Sales'] - df['Cost']
        
        # Calculate Gross Margin %
        if 'Sales' in df.columns and 'Gross Profit' in df.columns:
            df['Gross Margin %'] = np.where(
                df['Sales'] > 0,
                (df['Gross Profit'] / df['Sales']) * 100,
                0
            )
        
        # Calculate Profit per Unit
        if 'Gross Profit' in df.columns and 'Units' in df.columns:
            df['Profit per Unit'] = np.where(
                df['Units'] > 0,
                df['Gross Profit'] / df['Units'],
                0
            )
        
        # Calculate Revenue Contribution %
        if 'Sales' in df.columns:
            total_sales = df['Sales'].sum()
            df['Revenue Contribution %'] = (df['Sales'] / total_sales) * 100 if total_sales > 0 else 0
        
        # Calculate Profit Contribution %
        if 'Gross Profit' in df.columns:
            total_profit = df['Gross Profit'].sum()
            df['Profit Contribution %'] = (df['Gross Profit'] / total_profit) * 100 if total_profit > 0 else 0
        
        return df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str) -> None:
        """
        Save processed data
        
        Args:
            df: Processed DataFrame
            filename: Output filename
        """
        output_path = self.processed_data_dir / filename
        
        if filename.endswith('.csv'):
            df.to_csv(output_path, index=False)
        elif filename.endswith('.parquet'):
            df.to_parquet(output_path, index=False)
        else:
            raise ValueError(f"Unsupported output format: {filename}")
    
    def load_to_database(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Load data into SQLite database
        
        Args:
            df: DataFrame to load
            table_name: Database table name
        """
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
    
    def load_from_database(self, table_name: str, query: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from SQLite database
        
        Args:
            table_name: Database table name
            query: Optional SQL query
            
        Returns:
            pandas DataFrame
        """
        conn = sqlite3.connect(DB_PATH)
        
        if query:
            df = pd.read_sql_query(query, conn)
        else:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        conn.close()
        return df