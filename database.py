import sqlite3
from datetime import datetime
import pandas as pd
from typing import List, Dict, Optional

DB_PATH = "budget_planner.db"

class BudgetDatabase:
    def __init__(self):
        self.conn = None
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(DB_PATH, check_same_thread=False)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                icon TEXT
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                type TEXT NOT NULL
            )
        ''')
        
        # Create budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                UNIQUE(category, month, year)
            )
        ''')
        
        # Insert default expense categories if not exists
        default_categories = [
            ('Food & Dining', 'expense', '🍔'),
            ('Transportation', 'expense', '🚗'),
            ('Housing & Rent', 'expense', '🏠'),
            ('Utilities', 'expense', '💡'),
            ('Entertainment', 'expense', '🎬'),
            ('Shopping', 'expense', '🛒'),
            ('Healthcare', 'expense', '🏥'),
            ('Education', 'expense', '📚'),
            ('Other', 'expense', '📌'),
            ('Salary', 'income', '💰'),
            ('Freelance', 'income', '💼'),
            ('Investment', 'income', '📈'),
            ('Gift', 'income', '🎁'),
            ('Other Income', 'income', '💵')
        ]
        
        for name, cat_type, icon in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name, type, icon)
                VALUES (?, ?, ?)
            ''', (name, cat_type, icon))
        
        conn.commit()
        conn.close()
    
    def add_transaction(self, amount: float, category: str, description: str, date: str, trans_type: str):
        """Add a new transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (amount, category, description, date, type)
            VALUES (?, ?, ?, ?, ?)
        ''', (amount, category, description, date, trans_type))
        conn.commit()
        conn.close()
    
    def get_transactions(self, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                        trans_type: Optional[str] = None, category: Optional[str] = None) -> pd.DataFrame:
        """Get transactions with optional filters"""
        conn = self.get_connection()
        
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if trans_type:
            query += " AND type = ?"
            params.append(trans_type)
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY date DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def delete_transaction(self, trans_id: int):
        """Delete a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
        conn.commit()
        conn.close()
    
    def get_categories(self, cat_type: Optional[str] = None) -> List[str]:
        """Get categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if cat_type:
            cursor.execute("SELECT name, icon FROM categories WHERE type = ? ORDER BY name", (cat_type,))
        else:
            cursor.execute("SELECT name, icon FROM categories ORDER BY name")
        
        categories = cursor.fetchall()
        conn.close()
        return [(f"{icon} {name}") for name, icon in categories]
    
    def add_category(self, name: str, cat_type: str, icon: str = "📌"):
        """Add a new category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO categories (name, type, icon)
                VALUES (?, ?, ?)
            ''', (name, cat_type, icon))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def set_budget(self, category: str, amount: float, month: int, year: int):
        """Set or update budget for a category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO budgets (category, amount, month, year)
            VALUES (?, ?, ?, ?)
        ''', (category, amount, month, year))
        conn.commit()
        conn.close()
    
    def get_budget(self, category: str, month: int, year: int) -> Optional[float]:
        """Get budget for a category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT amount FROM budgets 
            WHERE category = ? AND month = ? AND year = ?
        ''', (category, month, year))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_all_budgets(self, month: int, year: int) -> pd.DataFrame:
        """Get all budgets for a month"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT category, amount FROM budgets 
            WHERE month = ? AND year = ?
        ''', conn, params=(month, year))
        conn.close()
        return df
    
    def get_spending_by_category(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get total spending by category"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE type = 'expense' AND date >= ? AND date <= ?
            GROUP BY category
            ORDER BY total DESC
        ''', conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def clear_all_data(self):
        """Clear all data from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        cursor.execute("DELETE FROM budgets")
        conn.commit()
        conn.close()
