import sqlite3
from typing import Dict, Any

# Database setup
def init_db():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 0,
        phone TEXT,
        address TEXT,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id TEXT,
        price REAL,
        status TEXT DEFAULT 'processing',
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# User functions
async def get_user_balance(user_id: int) -> float:
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return 0.0

async def update_user_balance(user_id: int, amount: float) -> bool:
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        # Create new user
        cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (user_id, amount))
    else:
        # Update existing user
        cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    
    conn.commit()
    conn.close()
    return True

async def create_order(user_id: int, product_id: str, price: float) -> int:
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO orders (user_id, product_id, price) VALUES (?, ?, ?)',
        (user_id, product_id, price)
    )
    
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return order_id

async def get_user_orders(user_id: int) -> list:
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT order_id, product_id, price, status, order_date FROM orders WHERE user_id = ?',
        (user_id,)
    )
    
    orders = cursor.fetchall()
    conn.close()
    
    return orders

# Initialize database on import
init_db()