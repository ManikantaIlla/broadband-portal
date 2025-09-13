import streamlit as st
import sqlite3
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
import uuid
from dateutil import parser

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import io
import math

# ---------------------------
# Configuration & Styling
# ---------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "broadband.db")
SALT = "broadband_demo_salt"
MOCK_DATA_CREATED_FLAG = "mock_data_created"
DB_MIGRATION_FLAG = "db_migrated_v3"

# Custom CSS for modern UI including semi-circular progress
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .plan-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .plan-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
        border-color: #667eea;
    }
    
    .recommended-plan {
        border: 2px solid #10b981;
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    }
    
    .current-plan-card {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border-left: 4px solid #667eea;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Expiry Warning */
    .expiry-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .expiry-critical {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 2px solid #ef4444;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Status Badges */
    .status-active {
        background-color: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-inactive {
        background-color: #f59e0b;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-cancelled {
        background-color: #ef4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-expired {
        background-color: #6b7280;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Usage Progress Cards */
    .usage-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    .usage-exceeded {
        border-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 8px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px 0 rgba(102, 126, 234, 0.4);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #1f2937;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Comparison Table */
    .comparison-table {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* File Upload */
    .uploadedFile {
        border-radius: 8px;
        border: 2px dashed #d1d5db;
        padding: 1rem;
    }
    
    /* Alert Styles */
    .alert-info {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .alert-warning {
        background-color: #fefce8;
        border-left: 4px solid #eab308;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .alert-success {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .alert-danger {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------
# Database Utilities
# ---------------------------
def safe_to_datetime(s, *, utc=True, drop_na=True):
    """Robust datetime conversion"""
    dt = pd.to_datetime(s, errors='coerce', utc=utc)
    try:
        dt = dt.dt.tz_convert(None)
    except Exception:
        try:
            dt = dt.dt.tz_localize(None)
        except Exception:
            pass
    if drop_na:
        dt = dt[~dt.isna()]
    return dt

def utcnow_naive():
    """Naive current UTC timestamp"""
    return pd.Timestamp.utcnow().tz_localize(None)

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def exec_query(query, params=(), fetch=False):
    conn = get_conn()
    c = conn.cursor()
    c.execute(query, params)
    if fetch:
        rows = c.fetchall()
        conn.close()
        return rows
    conn.commit()
    conn.close()

def exec_query_safe(query, params=(), fetch=False):
    """Execute query with error handling for missing columns"""
    try:
        return exec_query(query, params, fetch)
    except sqlite3.OperationalError as e:
        if "no such column" in str(e):
            if fetch:
                return []
            return None
        raise e

def df_from_query(query, params=()):
    rows = exec_query(query, params, fetch=True)
    if not rows:
        return pd.DataFrame()
    cols = rows[0].keys()
    data = [tuple(r) for r in rows]
    return pd.DataFrame(data, columns=cols)

def row_to_dict(row):
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}

def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    try:
        result = exec_query(f"PRAGMA table_info({table_name})", fetch=True)
        columns = [row[1] for row in result]
        return column_name in columns
    except:
        return False

def add_column_if_not_exists(table_name, column_name, column_type, default_value=None):
    """Add a column to a table if it doesn't exist"""
    if not column_exists(table_name, column_name):
        try:
            default_clause = f" DEFAULT {default_value}" if default_value is not None else ""
            exec_query(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}{default_clause}")
            return True
        except Exception as e:
            print(f"Error adding column {column_name} to {table_name}: {e}")
            return False
    return False

# ---------------------------
# Schema & Database Migration
# ---------------------------
def create_tables():
    conn = get_conn()
    c = conn.cursor()
    
    # Create base tables (original schema)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            name TEXT,
            email TEXT,
            address TEXT,
            phone TEXT,
            is_autopay_enabled INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY,
            name TEXT,
            speed_mbps INTEGER,
            data_limit_gb REAL,
            price REAL,
            validity_days INTEGER,
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            plan_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            auto_renew INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(plan_id) REFERENCES plans(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            subscription_id INTEGER,
            user_id INTEGER,
            amount REAL,
            payment_date TEXT,
            status TEXT,
            bill_month INTEGER,
            bill_year INTEGER,
            FOREIGN KEY(subscription_id) REFERENCES subscriptions(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            date TEXT,
            data_used_gb REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)
    ''')
    
    # Create new tables for enhanced features
    c.execute('''
        CREATE TABLE IF NOT EXISTS plan_comparisons (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            plan_ids TEXT,
            created_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            message TEXT,
            notification_type TEXT,
            is_read INTEGER DEFAULT 0,
            created_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    create_admins_table()
    
    conn.commit()
    conn.close()

def create_admins_table():
    """Create the admins table to store admin user details"""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            name TEXT,
            email TEXT,
            address TEXT,
            phone TEXT,
            city TEXT,
            state TEXT,
            signup_date TEXT,
            last_login TEXT,
            notification_preferences TEXT,
            is_autopay_enabled INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()




def migrate_database():
    """Add new columns to existing tables"""
    if meta_get(DB_MIGRATION_FLAG) == '1':
        return
    
    # ... existing migration code ...
    
    # Create admins table if it doesn't exist
    create_admins_table()
    
    # Move default admin to admins table if it exists in users table
    ensure_default_admin()
    
    meta_set(DB_MIGRATION_FLAG, '1')


def hash_password(password: str) -> str:
    salt = SALT + uuid.uuid4().hex
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${h}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, h = stored.split('$')
    except Exception:
        return False
    calc = hashlib.sha256((salt + password).encode()).hexdigest()
    return calc == h



def ensure_default_admin():
    # Check if default admin exists in admins table
    r = exec_query("SELECT * FROM admins WHERE username = ?", ("admin",), fetch=True)
    if len(r) == 0:
        pw = hash_password("admin123")
        signup_date = (datetime.utcnow() - timedelta(days=365)).isoformat()
        
        # Create in admins table
        exec_query(
            "INSERT INTO admins (username, password_hash, role, name, email, signup_date, city, state) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("admin", pw, "admin", "Administrator", "admin@example.com", signup_date, "Mumbai", "Maharashtra"),
        )
    
    # Also check if default admin exists in users table and remove if found
    r = exec_query("SELECT * FROM users WHERE username = ?", ("admin",), fetch=True)
    if r:
        exec_query("DELETE FROM users WHERE username = ?", ("admin",))



def meta_get(k):
    r = exec_query("SELECT v FROM meta WHERE k = ?", (k,), fetch=True)
    return r[0][0] if r else None

def meta_set(k, v):
    exec_query("INSERT OR REPLACE INTO meta (k, v) VALUES (?, ?)", (k, v))

def create_comprehensive_mock_data():
    """Create rich, realistic demo data for meaningful analytics"""
    if meta_get(MOCK_DATA_CREATED_FLAG) == '1':
        return
    
    # Enhanced plans with more realistic variety
    plans = [
        ("Basic Starter", 25, 50, 299, 30, "Perfect for light browsing and social media", "basic", 0, "Email Support", 5),
        ("Home Essential", 50, 100, 499, 30, "Great for small families", "basic", 0, "Phone Support, Basic Wi-Fi", 10),
        ("Family Connect", 100, 200, 699, 30, "Ideal for families with streaming", "standard", 0, "24/7 Support, Dual-band Wi-Fi", 20),
        ("Power User", 300, 500, 999, 30, "High-speed for gaming and streaming", "premium", 0, "Priority Support, Gaming Mode", 50),
        ("Pro Unlimited", 500, 1000, 1499, 30, "Professional use with high speeds", "premium", 1, "VIP Support, Static IP", 100),
        ("Unlimited Elite", 1000, 2000, 1999, 30, "Ultimate speed and data", "elite", 1, "Dedicated Support, Enterprise Features", 200),
        ("Student Special", 50, 75, 399, 30, "Affordable plan for students", "basic", 0, "Student Support, Study Mode", 10),
        ("Business Basic", 200, 300, 1299, 30, "Small business package", "premium", 0, "Business Support, Fixed IP", 40),
        ("Enterprise", 1500, 5000, 2999, 30, "Large business solution", "elite", 1, "Enterprise Support, SLA", 300),
        ("Gaming Pro", 800, 1500, 1799, 30, "Optimized for gaming", "premium", 0, "Gaming Support, Low Latency", 150),
    ]
    
    today = datetime.utcnow().date()
    for i, p in enumerate(plans):
        created_date = (today - timedelta(days=300 - i*20)).isoformat()
        if column_exists('plans', 'plan_type') and column_exists('plans', 'features') and column_exists('plans', 'upload_speed_mbps'):
            exec_query(
                "INSERT INTO plans (name, speed_mbps, data_limit_gb, price, validity_days, description, plan_type, is_unlimited, created_date, features, upload_speed_mbps) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*p, created_date),
            )
        else:
            exec_query(
                "INSERT INTO plans (name, speed_mbps, data_limit_gb, price, validity_days, description) VALUES (?, ?, ?, ?, ?, ?)",
                p[:6],
            )
    
    # Create diverse user base with realistic patterns
    cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]
    states = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "West Bengal", "Telangana", "Maharashtra", "Gujarat", "Rajasthan", "Uttar Pradesh"]
    
    # Define user profiles with different behavior patterns
    user_profiles = [
        ("Professional", "heavy", "reliable", "low", 0.8),
        ("Family", "moderate", "reliable", "medium", 0.7),
        ("Student", "moderate", "unreliable", "low", 0.9),
        ("Senior", "light", "reliable", "high", 0.3),
        ("Gamer", "heavy", "reliable", "medium", 0.85),
        ("Remote Worker", "heavy", "reliable", "low", 0.75),
        ("Casual User", "light", "unreliable", "low", 0.4),
        ("Streamer", "heavy", "reliable", "medium", 0.9),
        ("Small Business", "heavy", "reliable", "medium", 0.6),
        ("Tech Enthusiast", "heavy", "reliable", "low", 0.95),
    ]
    
    users_data = []
    for i in range(100):  # Increased to 100 users for more realistic data
        username = f"user{i+1:03d}"
        profile = user_profiles[i % len(user_profiles)]
        name = f"{profile[0]} User {i+1}"
        email = f"user{i+1:03d}@example.com"
        city = cities[i % len(cities)]
        state = states[i % len(states)]
        # Stagger signup dates over past 2 years
        signup_days_ago = np.random.randint(1, 730)
        signup_date = (today - timedelta(days=signup_days_ago)).isoformat()
        users_data.append((username, name, email, city, state, signup_date, profile))
    
    for udata in users_data:
        pw = hash_password("password")
        existing = exec_query("SELECT id FROM users WHERE username = ?", (udata[0],), fetch=True)
        if not existing:
            if column_exists('users', 'city') and column_exists('users', 'signup_date'):
                exec_query(
                    "INSERT INTO users (username, password_hash, role, name, email, city, state, signup_date, is_autopay_enabled, notification_preferences) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (udata[0], pw, "user", udata[1], udata[2], udata[3], udata[4], udata[5], 1 if udata[6][1] == "reliable" else 0, "email,sms" if udata[6][1] == "reliable" else "email"),
                )
            else:
                exec_query(
                    "INSERT INTO users (username, password_hash, role, name, email, is_autopay_enabled) VALUES (?, ?, ?, ?, ?, ?)",
                    (udata[0], pw, "user", udata[1], udata[2], 1 if udata[6][1] == "reliable" else 0),
                )
    
    # Get plan and user IDs
    plan_rows = exec_query("SELECT id, price, data_limit_gb FROM plans", fetch=True)
    plan_data = [(r[0], r[1], r[2]) for r in plan_rows]
    user_rows = exec_query("SELECT id FROM users WHERE role = 'user'", fetch=True)
    user_data = [(r[0],) for r in user_rows]
    
    # Create realistic subscription and usage history
    for uid_tuple in user_data:
        uid = uid_tuple[0]
        user_profile_data = exec_query("SELECT city, state, signup_date FROM users WHERE id = ?", (uid,), fetch=True)
        if user_profile_data:
            city, state, signup_date = user_profile_data[0]
            profile_index = int(uid) % len(user_profiles)
            usage_pattern = user_profiles[profile_index][1]
            payment_pattern = user_profiles[profile_index][2]
            support_pattern = user_profiles[profile_index][3]
            tech_savviness = user_profiles[profile_index][4]
            
            # Create multiple subscriptions per user (subscription history)
            num_subscriptions = np.random.randint(1, 5)  # 1-4 subscriptions
            subscription_start = datetime.fromisoformat(signup_date)
            
            for sub_idx in range(num_subscriptions):
                # Choose plan based on usage pattern and tech savviness
                if usage_pattern == "light":
                    suitable_plans = [p for p in plan_data if p[2] <= 200]  # Up to 200GB
                elif usage_pattern == "moderate":
                    suitable_plans = [p for p in plan_data if 100 <= p[2] <= 1000]  # 100-1000GB
                else:  # heavy
                    suitable_plans = [p for p in plan_data if p[2] >= 300]  # 300GB+
                
                if not suitable_plans:
                    suitable_plans = plan_data
                
                plan_id, plan_price, plan_limit = random.choice(suitable_plans)
                
                # Determine subscription dates
                if sub_idx == 0:
                    start_date = subscription_start + timedelta(days=np.random.randint(1, 7))
                else:
                    start_date = previous_end + timedelta(days=np.random.randint(1, 30))
                
                duration_days = np.random.randint(28, 35) if payment_pattern == "reliable" else np.random.randint(15, 32)
                end_date = start_date + timedelta(days=duration_days)
                previous_end = end_date
                
                # Determine status
                if end_date > datetime.utcnow():
                    status = 'active'
                elif sub_idx == num_subscriptions - 1 and end_date <= datetime.utcnow():
                    status = 'expired'
                else:
                    status = np.random.choice(['cancelled', 'expired'], p=[0.3, 0.7])
                
                # Create subscription
                renewal_count = max(0, sub_idx)
                if column_exists('subscriptions', 'created_date') and column_exists('subscriptions', 'renewal_count'):
                    exec_query(
                        "INSERT INTO subscriptions (user_id, plan_id, start_date, end_date, status, auto_renew, created_date, renewal_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (uid, plan_id, start_date.isoformat(), end_date.isoformat(), status, 
                         1 if payment_pattern == "reliable" else 0, start_date.isoformat(), renewal_count),
                    )
                else:
                    exec_query(
                        "INSERT INTO subscriptions (user_id, plan_id, start_date, end_date, status, auto_renew) VALUES (?, ?, ?, ?, ?, ?)",
                        (uid, plan_id, start_date.isoformat(), end_date.isoformat(), status, 
                         1 if payment_pattern == "reliable" else 0),
                    )
                
                sub_id = exec_query("SELECT last_insert_rowid()", fetch=True)[0][0]
                
                # Create multiple payments for this subscription (monthly billing)
                current_payment_date = start_date
                while current_payment_date < end_date:
                    payment_status = 'paid' if payment_pattern == "reliable" or np.random.random() < 0.85 else 'failed'
                    payment_method = np.random.choice(['credit_card', 'debit_card', 'upi', 'net_banking'], p=[0.35, 0.25, 0.3, 0.1])
                    
                    # Calculate taxes and discounts
                    base_amount = plan_price
                    tax_amount = base_amount * 0.18  # 18% GST
                    discount = 0
                    if renewal_count > 0:  # Loyalty discount
                        discount = base_amount * 0.05
                    
                    total_amount = base_amount + tax_amount - discount
                    
                    if column_exists('payments', 'payment_method') and column_exists('payments', 'tax_amount'):
                        exec_query(
                            "INSERT INTO payments (subscription_id, user_id, amount, payment_date, status, payment_method, bill_month, bill_year, tax_amount, discount, transaction_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (sub_id, uid, total_amount, current_payment_date.isoformat(), payment_status, payment_method, 
                             current_payment_date.month, current_payment_date.year, tax_amount, discount, f"TXN{uuid.uuid4().hex[:8].upper()}"),
                        )
                    else:
                        exec_query(
                            "INSERT INTO payments (subscription_id, user_id, amount, payment_date, status, bill_month, bill_year) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (sub_id, uid, base_amount, current_payment_date.isoformat(), payment_status, 
                             current_payment_date.month, current_payment_date.year),
                        )
                    
                    current_payment_date += timedelta(days=30)
                
                # Create usage data for this subscription period
                if status in ['active', 'expired']:
                    usage_days = min((datetime.utcnow().date() - start_date.date()).days, 
                                   (end_date.date() - start_date.date()).days)
                    
                    # Set base usage based on pattern and plan
                    if usage_pattern == "light":
                        base_daily = np.random.uniform(0.5, 2.0) * tech_savviness
                    elif usage_pattern == "moderate":
                        base_daily = np.random.uniform(2.0, 6.0) * tech_savviness
                    else:  # heavy
                        base_daily = np.random.uniform(6.0, 15.0) * tech_savviness
                    
                    for day_offset in range(usage_days):
                        usage_date = (start_date + timedelta(days=day_offset)).date()
                        if usage_date <= datetime.utcnow().date():
                            
                            # Add weekly patterns (higher usage on weekends)
                            weekend_factor = 1.4 if usage_date.weekday() >= 5 else 1.0
                            
                            # Add monthly patterns (higher usage mid-month)
                            month_factor = 1.2 if 10 <= usage_date.day <= 20 else 0.9
                            
                            # Add occasional spikes
                            spike_factor = np.random.uniform(2.0, 4.0) if np.random.random() < 0.08 else 1.0
                            
                            daily_usage = np.clip(
                                np.random.normal(base_daily * weekend_factor * month_factor * spike_factor, 
                                               base_daily * 0.3),
                                0.1, plan_limit * 0.8  # Cap at 80% of plan limit per day
                            )
                            
                            # Split into peak and off-peak hours
                            peak_usage = daily_usage * np.random.uniform(0.6, 0.8)
                            off_peak_usage = daily_usage - peak_usage
                            upload_usage = daily_usage * np.random.uniform(0.1, 0.3)
                            avg_speed = plan_limit * np.random.uniform(0.7, 0.95)  # 70-95% of advertised speed
                            
                            if column_exists('usage', 'peak_hour_usage') and column_exists('usage', 'upload_usage'):
                                exec_query(
                                    "INSERT INTO usage (user_id, date, data_used_gb, peak_hour_usage, off_peak_usage, upload_usage, average_speed) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (uid, usage_date.isoformat(), daily_usage, peak_usage, off_peak_usage, upload_usage, avg_speed),
                                )
                            else:
                                exec_query(
                                    "INSERT INTO usage (user_id, date, data_used_gb) VALUES (?, ?, ?)",
                                    (uid, usage_date.isoformat(), daily_usage),
                                )
                
                # Create support tickets based on support pattern
                if support_pattern == "high" or (support_pattern == "medium" and np.random.random() < 0.4):
                    num_tickets = np.random.randint(1, 3) if support_pattern == "high" else 1
                    for _ in range(num_tickets):
                        ticket_date = start_date + timedelta(days=np.random.randint(1, min(30, (end_date - start_date).days)))
                        categories = ['billing', 'technical', 'service', 'plan_change', 'connection_issue', 'speed_complaint']
                        ticket_category = np.random.choice(categories)
                        ticket_priority = np.random.choice(['low', 'medium', 'high'], p=[0.5, 0.3, 0.2])
                        ticket_status = np.random.choice(['resolved', 'closed'], p=[0.8, 0.2])
                        
                        subjects = {
                            'billing': ['Billing inquiry', 'Payment issue', 'Invoice clarification'],
                            'technical': ['Connection problem', 'Speed issue', 'Equipment malfunction'],
                            'service': ['Service interruption', 'Installation query', 'Account update'],
                            'plan_change': ['Plan upgrade request', 'Plan downgrade', 'Plan comparison'],
                            'connection_issue': ['No internet', 'Frequent disconnection', 'Slow connection'],
                            'speed_complaint': ['Speed not as promised', 'Slow during peak hours', 'Upload speed issue']
                        }
                        
                        subject = np.random.choice(subjects[ticket_category])
                        
                        if column_exists('support_tickets', 'created_date'):
                            exec_query(
                                "INSERT INTO support_tickets (user_id, subject, description, category, status, priority, created_date, resolved_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (uid, subject, f"Customer reported issue with {ticket_category}", ticket_category, 
                                 ticket_status, ticket_priority, ticket_date.isoformat(), 
                                 (ticket_date + timedelta(days=np.random.randint(1, 7))).isoformat() if ticket_status == 'resolved' else None),
                            )
    
    # Create notifications for users (expiry reminders, etc.)
    active_subscriptions = exec_query(
        "SELECT s.*, u.notification_preferences FROM subscriptions s JOIN users u ON s.user_id = u.id WHERE s.status = 'active'",
        fetch=True
    )
    
    for sub in active_subscriptions:
        end_date = datetime.fromisoformat(sub[4])  # end_date is index 4
        days_until_expiry = (end_date.date() - datetime.utcnow().date()).days
        
        # Create expiry reminder notifications
        if 1 <= days_until_expiry <= 7:
            notification_message = f"Your broadband plan expires in {days_until_expiry} day{'s' if days_until_expiry > 1 else ''}. Renew now to avoid interruption."
            
            if column_exists('notifications', 'created_date'):
                exec_query(
                    "INSERT INTO notifications (user_id, message, notification_type, created_date) VALUES (?, ?, ?, ?)",
                    (sub[1], notification_message, 'expiry_reminder', datetime.utcnow().isoformat()),  # user_id is index 1
                )
    
    meta_set(MOCK_DATA_CREATED_FLAG, '1')


def generate_usage_for_user(user_id, days=60):
    """Generate random usage data for a given user"""
    conn = get_conn()
    cur = conn.cursor()

    today = datetime.today().date()
    for i in range(days):
        date = today - timedelta(days=i)
        data_used = round(random.uniform(1, 10), 2)  # 1–10 GB/day
        peak = round(data_used * random.uniform(0.5, 0.8), 2)
        off_peak = round(data_used - peak, 2)
        upload = round(data_used * random.uniform(0.1, 0.3), 2)
        avg_speed = round(random.uniform(20, 100), 2)  # Mbps

        cur.execute("""
            INSERT INTO usage (user_id, date, data_used_gb, peak_hour_usage, off_peak_usage, upload_usage, average_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date.isoformat(), data_used, peak, off_peak, upload, avg_speed))

    conn.commit()
    conn.close()


def populate_usage_for_all_users(days=60):
    """Populate usage for all users if they don't already have data"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE role='user'")
    user_ids = [row[0] for row in cur.fetchall()]
    conn.close()

    for uid in user_ids:
        existing = exec_query("SELECT COUNT(*) FROM usage WHERE user_id = ?", (uid,), fetch=True)[0][0]
        if existing == 0:  # Only populate if no usage exists
            generate_usage_for_user(uid, days)
            print(f"✅ Inserted {days} days of usage for user {uid}")


# ---------------------------
# Business Logic
# ---------------------------
def signup(username, password, name, email):
    try:
        pw = hash_password(password)
        signup_date = utcnow_naive().isoformat()
        if column_exists('users', 'signup_date'):
            exec_query(
                "INSERT INTO users (username, password_hash, role, name, email, signup_date, city, state) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (username, pw, 'user', name, email, signup_date, 'Mumbai', 'Maharashtra'),
            )
        else:
            exec_query(
                "INSERT INTO users (username, password_hash, role, name, email) VALUES (?, ?, ?, ?, ?)",
                (username, pw, 'user', name, email),
            )
        return True, "User created successfully"
    except Exception as e:
        return False, str(e)



def signin(username, password):
    # First check users table
    r = exec_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True)
    if r:
        row = r[0]
        if verify_password(password, row[2]):
            # Update last login if column exists
            if column_exists('users', 'last_login'):
                exec_query("UPDATE users SET last_login = ? WHERE id = ?", (utcnow_naive().isoformat(), row[0]))
            return True, row_to_dict(row)
    
    # Then check admins table
    r = exec_query("SELECT * FROM admins WHERE username = ?", (username,), fetch=True)
    if r:
        row = r[0]
        if verify_password(password, row[2]):
            # Update last login if column exists
            if column_exists('admins', 'last_login'):
                exec_query("UPDATE admins SET last_login = ? WHERE id = ?", (utcnow_naive().isoformat(), row[0]))
            return True, row_to_dict(row)
    
    return False, "Invalid credentials"




def get_user_by_id(uid):
    # First check users table
    r = exec_query("SELECT * FROM users WHERE id = ?", (uid,), fetch=True)
    if r:
        return row_to_dict(r[0])
    
    # Then check admins table
    r = exec_query("SELECT * FROM admins WHERE id = ?", (uid,), fetch=True)
    if r:
        return row_to_dict(r[0])
    
    return None


def get_all_plans():
    rows = exec_query("SELECT * FROM plans ORDER BY price ASC", fetch=True)
    return [row_to_dict(r) for r in rows]

def get_plan(plan_id):
    r = exec_query("SELECT * FROM plans WHERE id = ?", (plan_id,), fetch=True)
    return row_to_dict(r[0]) if r else None

def get_user_active_subscription(user_id):
    r = exec_query(
        "SELECT s.*, p.name AS plan_name, p.data_limit_gb, p.price FROM subscriptions s JOIN plans p ON s.plan_id = p.id WHERE s.user_id = ? AND s.status = 'active' ORDER BY s.start_date DESC LIMIT 1",
        (user_id,),
        fetch=True,
    )
    return row_to_dict(r[0]) if r else None

def get_user_subscription_history(user_id):
    """Get all subscription history for a user"""
    query = """
        SELECT s.*, p.name AS plan_name, p.data_limit_gb, p.price, p.speed_mbps
        FROM subscriptions s 
        JOIN plans p ON s.plan_id = p.id 
        WHERE s.user_id = ? 
        ORDER BY s.start_date DESC
    """
    rows = exec_query(query, (user_id,), fetch=True)
    return [row_to_dict(r) for r in rows]

def subscribe_user_to_plan(user_id, plan_id, auto_renew=1):
    # Cancel any existing active subscription
    exec_query("UPDATE subscriptions SET status = 'cancelled' WHERE user_id = ? AND status = 'active'", (user_id,))
    
    today = datetime.utcnow().date()
    plan = get_plan(plan_id)
    end = today + timedelta(days=plan['validity_days'])
    
    if column_exists('subscriptions', 'created_date'):
        exec_query(
            "INSERT INTO subscriptions (user_id, plan_id, start_date, end_date, status, auto_renew, created_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, plan_id, today.isoformat(), end.isoformat(), 'active', auto_renew, utcnow_naive().isoformat()),
        )
    else:
        exec_query(
            "INSERT INTO subscriptions (user_id, plan_id, start_date, end_date, status, auto_renew) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, plan_id, today.isoformat(), end.isoformat(), 'active', auto_renew),
        )

def create_payment(subscription_id, user_id, amount, status='paid', payment_method='credit_card'):
    now = utcnow_naive()
    tax_amount = amount * 0.18
    total_amount = amount + tax_amount
    
    if column_exists('payments', 'payment_method') and column_exists('payments', 'tax_amount'):
        exec_query(
            "INSERT INTO payments (subscription_id, user_id, amount, payment_date, status, payment_method, bill_month, bill_year, tax_amount, transaction_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (subscription_id, user_id, total_amount, now.isoformat(), status, payment_method, now.month, now.year, tax_amount, f"TXN{uuid.uuid4().hex[:8].upper()}"),
        )
    else:
        exec_query(
            "INSERT INTO payments (subscription_id, user_id, amount, payment_date, status, bill_month, bill_year) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (subscription_id, user_id, amount, now.isoformat(), status, now.month, now.year),
        )

def get_usage_for_user(user_id, days=30):
    query = "SELECT date, data_used_gb"
    if column_exists('usage', 'peak_hour_usage'):
        query += ", peak_hour_usage, off_peak_usage"
    if column_exists('usage', 'upload_usage'):
        query += ", upload_usage, average_speed"
    query += f" FROM usage WHERE user_id = ? ORDER BY date DESC LIMIT {days}"
    
    rows = exec_query(query, (user_id,), fetch=True)
    if not rows:
        return pd.DataFrame(columns=['date', 'data_used_gb'])
    cols = rows[0].keys()
    data = [tuple(r) for r in rows]
    return pd.DataFrame(data, columns=cols)



def get_user_notifications(user_id, limit=10, unread_only=False):
    """Get recent notifications for a user, optionally only unread ones"""
    if not column_exists('notifications', 'created_date'):
        return []
    
    base_query = "SELECT * FROM notifications WHERE user_id = ?"
    params = [user_id]
    
    if unread_only:
        base_query += " AND is_read = 0"
    
    base_query += " ORDER BY created_date DESC LIMIT ?"
    params.append(limit)
    
    rows = exec_query(base_query, tuple(params), fetch=True)
    return [row_to_dict(r) for r in rows]

def mark_notification_read(notification_id):
    """Mark a notification as read"""
    if column_exists('notifications', 'is_read'):
        exec_query("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))

def send_message_to_users(audience, message):
    """Send a message to selected users (active, inactive, or all)"""
    # Determine user IDs based on audience
    if audience == "Active Users":
        query = """
            SELECT DISTINCT u.id FROM users u
            JOIN subscriptions s ON u.id = s.user_id
            WHERE s.status = 'active'
        """
    elif audience == "Inactive Users":
        query = """
            SELECT DISTINCT u.id FROM users u
            JOIN subscriptions s ON u.id = s.user_id
            WHERE u.id NOT IN (
                SELECT DISTINCT user_id FROM subscriptions WHERE status = 'active'
            )
        """
    else:  # All Users
        query = "SELECT id FROM users WHERE role = 'user'"
    
    user_ids = [row[0] for row in exec_query(query, fetch=True)]
    
    # Insert a notification for each user
    for user_id in user_ids:
        exec_query(
            "INSERT INTO notifications (user_id, message, notification_type, created_date) VALUES (?, ?, ?, ?)",
            (user_id, message, "admin_message", utcnow_naive().isoformat())
        )
    
    return len(user_ids)

def check_expiry_reminders(user_id):
    """Check if user has any expiry reminders"""
    subscription = get_user_active_subscription(user_id)
    if not subscription:
        return []
    
    try:
        end_date = datetime.fromisoformat(subscription['end_date'])
        days_until_expiry = (end_date.date() - datetime.utcnow().date()).days
        
        reminders = []
        if days_until_expiry <= 7 and days_until_expiry > 0:
            reminders.append({
                'type': 'warning',
                'message': f"Your plan expires in {days_until_expiry} day{'s' if days_until_expiry > 1 else ''}!",
                'days': days_until_expiry
            })
        elif days_until_expiry <= 0:
            reminders.append({
                'type': 'critical',
                'message': "Your plan has expired!",
                'days': days_until_expiry
            })
        
        return reminders
    except:
        return []

def save_plan_comparison(user_id, plan_ids):
    """Save plan comparison for user"""
    if column_exists('plan_comparisons', 'created_date'):
        exec_query(
            "INSERT INTO plan_comparisons (user_id, plan_ids, created_date) VALUES (?, ?, ?)",
            (user_id, ','.join(map(str, plan_ids)), utcnow_naive().isoformat())
        )

def get_plan_comparison_history(user_id, limit=5):
    """Get recent plan comparisons for user"""
    if not column_exists('plan_comparisons', 'created_date'):
        return []
    
    rows = exec_query(
        "SELECT * FROM plan_comparisons WHERE user_id = ? ORDER BY created_date DESC LIMIT ?",
        (user_id, limit),
        fetch=True
    )
    return [row_to_dict(r) for r in rows]

def bulk_create_plans_from_csv(csv_data):
    """Create plans from CSV data"""
    try:
        df = pd.read_csv(io.StringIO(csv_data))
        
        # Expected columns: name, speed_mbps, data_limit_gb, price, validity_days, description, plan_type, features, upload_speed_mbps
        required_columns = ['name', 'speed_mbps', 'data_limit_gb', 'price', 'validity_days', 'description']
        
        for col in required_columns:
            if col not in df.columns:
                return False, f"Missing required column: {col}"
        
        created_count = 0
        for _, row in df.iterrows():
            try:
                # Check if plan already exists
                existing = exec_query("SELECT id FROM plans WHERE name = ?", (row['name'],), fetch=True)
                if existing:
                    continue
                
                # Set default values for optional columns
                plan_type = row.get('plan_type', 'standard')
                features = row.get('features', '')
                upload_speed = row.get('upload_speed_mbps', row['speed_mbps'] // 10)
                is_unlimited = 1 if row.get('is_unlimited', '').lower() in ['true', '1', 'yes'] else 0
                
                if column_exists('plans', 'plan_type') and column_exists('plans', 'features'):
                    exec_query(
                        "INSERT INTO plans (name, speed_mbps, data_limit_gb, price, validity_days, description, plan_type, is_unlimited, features, upload_speed_mbps, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (row['name'], row['speed_mbps'], row['data_limit_gb'], row['price'], 
                         row['validity_days'], row['description'], plan_type, is_unlimited, 
                         features, upload_speed, utcnow_naive().isoformat())
                    )
                else:
                    exec_query(
                        "INSERT INTO plans (name, speed_mbps, data_limit_gb, price, validity_days, description) VALUES (?, ?, ?, ?, ?, ?)",
                        (row['name'], row['speed_mbps'], row['data_limit_gb'], row['price'], row['validity_days'], row['description'])
                    )
                
                created_count += 1
                
            except Exception as e:
                print(f"Error creating plan from row: {e}")
                continue
        
        return True, f"Successfully created {created_count} plans"
        
    except Exception as e:
        return False, f"Error processing CSV: {str(e)}"


def transfer_user_to_admin(user_id):
    """Transfer a user from users table to admins table"""
    # Get user details
    user = exec_query("SELECT * FROM users WHERE id = ?", (user_id,), fetch=True)
    if not user:
        return False, "User not found"
    
    user_data = row_to_dict(user[0])
    
    # Insert into admins table
    columns = ', '.join(user_data.keys())
    placeholders = ', '.join(['?'] * len(user_data))
    values = tuple(user_data.values())
    
    try:
        exec_query(f"INSERT INTO admins ({columns}) VALUES ({placeholders})", values)
        
        # Delete from users table
        exec_query("DELETE FROM users WHERE id = ?", (user_id,))
        
        return True, "User successfully transferred to admin"
    except Exception as e:
        return False, f"Error transferring user to admin: {str(e)}"

def remove_admin_from_user(admin_id):
    """Remove admin role and move back to users table"""
    # Check if it's the default admin
    admin = exec_query("SELECT username FROM admins WHERE id = ?", (admin_id,), fetch=True)
    if admin and admin[0][0] == "admin":
        return False, "Cannot remove default admin"
    
    # Get admin details
    admin_data = exec_query("SELECT * FROM admins WHERE id = ?", (admin_id,), fetch=True)
    if not admin_data:
        return False, "Admin not found"
    
    admin_dict = row_to_dict(admin_data[0])
    
    # Change role to user
    admin_dict['role'] = 'user'
    
    # Insert into users table
    columns = ', '.join(admin_dict.keys())
    placeholders = ', '.join(['?'] * len(admin_dict))
    values = tuple(admin_dict.values())
    
    try:
        exec_query(f"INSERT INTO users ({columns}) VALUES ({placeholders})", values)
        
        # Delete from admins table
        exec_query("DELETE FROM admins WHERE id = ?", (admin_id,))
        
        return True, "Admin successfully removed and moved to users"
    except Exception as e:
        return False, f"Error removing admin: {str(e)}"

def get_all_admins():
    """Get all admin users"""
    rows = exec_query("SELECT * FROM admins ORDER BY id", fetch=True)
    return [row_to_dict(r) for r in rows] if rows else []

# ---------------------------
# ML Model Functions (Enhanced)
# ---------------------------
def collect_training_data():
    """Collect data for training the recommendation model"""
    query = """
    SELECT 
        u.id as user_id,
        u.city,
        u.state,
        u.signup_date,
        s.id as subscription_id,
        s.start_date,
        s.end_date,
        p.id as plan_id,
        p.name as plan_name,
        p.plan_type,
        p.speed_mbps,
        p.data_limit_gb,
        p.price
    FROM subscriptions s
    JOIN users u ON s.user_id = u.id
    JOIN plans p ON s.plan_id = p.id
    WHERE s.status IN ('active', 'expired')
    """
    
    subscriptions_df = df_from_query(query)
    
    # Get usage features
    usage_features = []
    for _, row in subscriptions_df.iterrows():
        user_id = row['user_id']
        usage_df = get_usage_for_user(user_id, days=90)
        
        if not usage_df.empty:
            avg_daily = usage_df['data_used_gb'].mean()
            max_daily = usage_df['data_used_gb'].max()
            std_daily = usage_df['data_used_gb'].std()
            total_monthly = usage_df['data_used_gb'].sum() * (30/len(usage_df))
            
            # Calculate usage patterns
            weekday_usage = 0
            weekend_usage = 0
            if 'date' in usage_df.columns:
                usage_df['date'] = pd.to_datetime(usage_df['date'])
                usage_df['weekday'] = usage_df['date'].dt.weekday
                weekday_usage = usage_df[usage_df['weekday'] < 5]['data_used_gb'].mean()
                weekend_usage = usage_df[usage_df['weekday'] >= 5]['data_used_gb'].mean()
            
            usage_features.append({
                'user_id': user_id,
                'avg_daily_usage': avg_daily,
                'max_daily_usage': max_daily,
                'usage_std': std_daily,
                'estimated_monthly_usage': total_monthly,
                'weekday_avg': weekday_usage,
                'weekend_avg': weekend_usage,
                'usage_consistency': 1 - (std_daily / avg_daily if avg_daily > 0 else 0)
            })
    
    if usage_features:
        usage_df = pd.DataFrame(usage_features)
        training_data = pd.merge(subscriptions_df, usage_df, on='user_id', how='left')
    else:
        training_data = subscriptions_df.copy()
        for col in ['avg_daily_usage', 'max_daily_usage', 'usage_std', 'estimated_monthly_usage', 
                   'weekday_avg', 'weekend_avg', 'usage_consistency']:
            training_data[col] = 0
    
    # Fill missing values
    numeric_cols = ['avg_daily_usage', 'max_daily_usage', 'usage_std', 'estimated_monthly_usage', 
                   'weekday_avg', 'weekend_avg', 'usage_consistency']
    for col in numeric_cols:
        training_data[col].fillna(0, inplace=True)
    
    return training_data

def engineer_features(df):
    """Create features for the ML model"""
    df = df.copy()
    
    # Handle date columns
    date_columns = ['signup_date', 'start_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Calculate user tenure
    if 'signup_date' in df.columns:
        current_date = pd.Timestamp.now()
        df['days_since_signup'] = (current_date - df['signup_date']).dt.days
    else:
        df['days_since_signup'] = 0
    
    # Create usage-based features
    df['usage_to_limit_ratio'] = df['estimated_monthly_usage'] / df['data_limit_gb']
    df['price_per_gb'] = df['price'] / df['data_limit_gb']
    df['speed_efficiency'] = df['speed_mbps'] / df['price']
    df['weekend_weekday_ratio'] = df['weekend_avg'] / (df['weekday_avg'] + 0.001)  # Avoid division by zero
    
    # Categorize users based on usage patterns
    def categorize_user(row):
        monthly_usage = row['estimated_monthly_usage']
        consistency = row['usage_consistency']
        
        if monthly_usage < 50:
            return 'light'
        elif monthly_usage < 200:
            return 'moderate'
        elif monthly_usage < 500:
            return 'heavy'
        else:
            return 'extreme'
    
    df['usage_category'] = df.apply(categorize_user, axis=1)
    
    # Set target variable
    if 'plan_type' in df.columns:
        df['plan_category'] = df['plan_type']
    else:
        df['plan_category'] = 'basic'
    
    return df

#

def train_recommendation_model():
    """Train a recommendation model for plan suggestions"""
    try:
        # Collect training data
        df = collect_training_data()
        
        if df.empty:
            st.error("No training data available. Please ensure there is subscription data.")
            return None
        
        # Check if required columns exist, if not add them with default values
        required_columns = ['city', 'state', 'signup_date', 'start_date', 'end_date', 'plan_id', 'plan_type']
        for col in required_columns:
            if col not in df.columns:
                if col == 'city':
                    df[col] = 'Unknown'
                elif col == 'state':
                    df[col] = 'Unknown'
                elif col == 'signup_date':
                    df[col] = datetime.utcnow().isoformat()
                elif col == 'start_date':
                    df[col] = datetime.utcnow().isoformat()
                elif col == 'end_date':
                    df[col] = (datetime.utcnow() + timedelta(days=30)).isoformat()
                elif col == 'plan_id':
                    df[col] = 1  # Default to first plan
                elif col == 'plan_type':
                    df[col] = 'basic'
        
        # Remove rows where target (plan_id) is NaN
        df = df.dropna(subset=['plan_id'])
        
        if df.empty:
            st.error("No valid training data available after removing missing target values.")
            return None
        
        # Feature engineering with robust date parsing
        # Convert date columns with multiple format attempts
        date_columns = ['signup_date', 'start_date', 'end_date']
        for col in date_columns:
            # Try parsing with different formats
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce')
            
            # Fill any remaining NaT values with current date
            df[col] = df[col].fillna(datetime.utcnow())
        
        # Calculate durations
        df['subscription_duration'] = (df['end_date'] - df['start_date']).dt.days
        df['user_tenure'] = (datetime.utcnow() - df['signup_date']).dt.days
        
        # Handle any NaN values in the calculated durations
        df['subscription_duration'] = df['subscription_duration'].fillna(30)  # Default to 30 days
        df['user_tenure'] = df['user_tenure'].fillna(365)  # Default to 1 year
        
        # Prepare features and target
        feature_cols = ['city', 'state', 'subscription_duration', 'user_tenure', 'plan_type']
        target_col = 'plan_id'
        
        # Handle NaN values - this is the key fix
        # For numeric columns, fill with median
        numeric_cols = ['subscription_duration', 'user_tenure']
        for col in numeric_cols:
            if col in df.columns:
                median_val = df[col].median()
                # If median is NaN (all values are NaN), fill with 0
                if pd.isna(median_val):
                    median_val = 0
                df[col].fillna(median_val, inplace=True)
        
        # For categorical columns, fill with mode or a default value
        categorical_cols = ['city', 'state', 'plan_type']
        for col in categorical_cols:
            if col in df.columns:
                try:
                    mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 'unknown'
                    df[col].fillna(mode_val, inplace=True)
                except:
                    df[col].fillna('unknown', inplace=True)
        
        # Prepare data
        X = df[feature_cols]
        y = df[target_col]
        
        # Preprocessing pipeline
        numeric_features = ['subscription_duration', 'user_tenure']
        categorical_features = ['city', 'state', 'plan_type']
        
        numeric_transformer = StandardScaler()
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        # Create model pipeline
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        st.success(f"Model trained successfully with accuracy: {accuracy:.2f}")
        
        # Save model
        joblib.dump(model, 'recommendation_model.joblib')
        
        return model
    
    except Exception as e:
        st.error(f"Error training model: {str(e)}")
        return None


def ml_recommendation_for_user(user_id, num_recommendations=3):
    """Enhanced ML-based plan recommendation"""
    if not os.path.exists('plan_recommendation_model.pkl'):
        return advanced_recommendation_for_user(user_id, num_recommendations)
    
    model = joblib.load('plan_recommendation_model.pkl')
    user = get_user_by_id(user_id)
    if not user:
        return []
    
    usage_df = get_usage_for_user(user_id, days=90)
    
    # Prepare features
    if not usage_df.empty:
        avg_daily = usage_df['data_used_gb'].mean()
        max_daily = usage_df['data_used_gb'].max()
        std_daily = usage_df['data_used_gb'].std()
        total_monthly = usage_df['data_used_gb'].sum() * (30/len(usage_df))
        
        # Calculate weekday/weekend patterns
        if len(usage_df) > 7:  # Enough data for pattern analysis
            usage_df['date'] = pd.to_datetime(usage_df['date'])
            usage_df['weekday'] = usage_df['date'].dt.weekday
            weekday_avg = usage_df[usage_df['weekday'] < 5]['data_used_gb'].mean()
            weekend_avg = usage_df[usage_df['weekday'] >= 5]['data_used_gb'].mean()
        else:
            weekday_avg = avg_daily
            weekend_avg = avg_daily
        
        usage_consistency = 1 - (std_daily / avg_daily if avg_daily > 0 else 0)
    else:
        avg_daily = max_daily = std_daily = total_monthly = 0
        weekday_avg = weekend_avg = usage_consistency = 0
    
    # Calculate user tenure
    signup_date = pd.to_datetime(user.get('signup_date', pd.Timestamp.now()))
    days_since_signup = (pd.Timestamp.now() - signup_date).days
    
    # Create feature dataframe
    features = pd.DataFrame({
        'avg_daily_usage': [avg_daily],
        'max_daily_usage': [max_daily],
        'usage_std': [std_daily],
        'estimated_monthly_usage': [total_monthly],
        'days_since_signup': [days_since_signup],
        'weekday_avg': [weekday_avg],
        'weekend_avg': [weekend_avg],
        'usage_consistency': [usage_consistency],
        'city': [user.get('city', 'Unknown')],
        'state': [user.get('state', 'Unknown')]
    })
    
    # Predict plan category
    predicted_category = model.predict(features)[0]
    
    # Get plans and score them
    all_plans = get_all_plans()
    scored_plans = []
    
    for plan in all_plans:
        score = 0
        
        # Category match bonus
        if plan.get('plan_type', 'basic') == predicted_category:
            score += 40
        
        # Usage suitability
        if total_monthly > 0:
            if plan['data_limit_gb'] >= total_monthly * 1.2:  # 20% buffer
                score += 30
            elif plan['data_limit_gb'] >= total_monthly:
                score += 20
            else:
                score += 10 * (plan['data_limit_gb'] / total_monthly)
        
        # Price efficiency
        price_per_gb = plan['price'] / plan['data_limit_gb']
        if price_per_gb < 5:  # Good value
            score += 20
        elif price_per_gb < 10:
            score += 10
        
        # Speed adequacy
        if plan['speed_mbps'] >= max_daily * 10:  # 10x daily usage as speed
            score += 10
        
        scored_plans.append((plan, score))
    
    # Sort by score and return top recommendations
    scored_plans.sort(key=lambda x: x[1], reverse=True)
    return [plan for plan, score in scored_plans[:num_recommendations]]

def advanced_recommendation_for_user(user_id, num_recommendations=3):
    """Enhanced rule-based recommendation engine"""
    usage_df = get_usage_for_user(user_id, days=60)
    plans = get_all_plans()
    
    if usage_df.empty:
        # For new users, recommend based on popular/starter plans
        return sorted(plans, key=lambda x: x['price'])[:num_recommendations]
    
    usage_df['data_used_gb'] = pd.to_numeric(usage_df['data_used_gb'], errors='coerce')
    
    # Calculate usage statistics
    avg_daily = usage_df['data_used_gb'].dropna().mean()
    max_daily = usage_df['data_used_gb'].dropna().max()
    std_daily = usage_df['data_used_gb'].dropna().std()
    
    # Estimate monthly need with growth factor
    monthly_est = avg_daily * 30
    peak_monthly_est = max_daily * 30
    growth_factor = 1.2 + (std_daily / avg_daily if avg_daily > 0 else 0) * 0.1
    
    target_limit = max(monthly_est * growth_factor, peak_monthly_est * 1.1)
    
    # Score plans
    scored_plans = []
    for plan in plans:
        # Capacity score
        if plan['data_limit_gb'] >= target_limit:
            capacity_score = 1.0 - ((plan['data_limit_gb'] - target_limit) / target_limit) * 0.1
        else:
            capacity_score = 0.5 * (plan['data_limit_gb'] / target_limit)
        
        # Price efficiency
        price_per_gb = plan['price'] / plan['data_limit_gb']
        all_prices_per_gb = [p['price'] / p['data_limit_gb'] for p in plans]
        min_price_per_gb = min(all_prices_per_gb)
        price_score = min_price_per_gb / price_per_gb if price_per_gb > 0 else 0
        
        # Speed adequacy
        required_speed = avg_daily * 8  # 8 Mbps per GB daily usage (rough estimate)
        speed_score = min(1.0, plan['speed_mbps'] / max(required_speed, 25))
        
        # Combined score
        total_score = (capacity_score * 0.5) + (price_score * 0.3) + (speed_score * 0.2)
        scored_plans.append((plan, total_score))
    
    # Return top recommendations
    best_plans = sorted(scored_plans, key=lambda x: x[1], reverse=True)
    return [plan for plan, score in best_plans[:num_recommendations]]


# -------- Admin CRUD Helpers (Users & Plans) --------
def admin_create_user(username, password, name, email, role='user', city=None, state=None, phone=None, address=None):
    # Enforce unique username; return (ok, msg)
    existing = exec_query("SELECT id FROM users WHERE username = ?", (username,), fetch=True)
    if existing:
        return False, "Username already exists."
    pw = hash_password(password)
    cols = ['username','password_hash','role','name','email']
    vals = [username, pw, role, name, email]
    # Optional columns
    if column_exists('users','city'):
        cols += ['city']; vals += [city or '']
    if column_exists('users','state'):
        cols += ['state']; vals += [state or '']
    if column_exists('users','phone'):
        cols += ['phone']; vals += [phone or '']
    if column_exists('users','address'):
        cols += ['address']; vals += [address or '']
    if column_exists('users','signup_date'):
        cols += ['signup_date']; vals += [utcnow_naive().isoformat()]
    placeholders = ",".join(["?"]*len(vals))
    exec_query(f"INSERT INTO users ({','.join(cols)}) VALUES ({placeholders})", tuple(vals))
    return True, "User created."

# def admin_send_message(message, target='all'):
    """
    Send a custom message from admin to active, inactive, or all users.
    target: 'active', 'inactive', or 'all'
    """
    now = utcnow_naive().isoformat()

    if target == 'active':
        users = exec_query("""
            SELECT DISTINCT u.id 
            FROM users u 
            JOIN subscriptions s ON u.id = s.user_id
            WHERE s.status = 'active' AND u.role = 'user'
        """, fetch=True)
    elif target == 'inactive':
        users = exec_query("""
            SELECT DISTINCT u.id 
            FROM users u 
            LEFT JOIN subscriptions s ON u.id = s.user_id
            WHERE (s.status IS NULL OR s.status != 'active') 
              AND u.role = 'user'
        """, fetch=True)
    else:  # all users
        users = exec_query("SELECT id FROM users WHERE role = 'user'", fetch=True)

    for row in users:
        uid = row[0]
        exec_query(
            "INSERT INTO notifications (user_id, message, notification_type, created_date) VALUES (?, ?, ?, ?)",
            (uid, message, 'admin_broadcast', now)
        )
    return True, f"Message sent to {len(users)} users"



def admin_update_user(user_id, **kwargs):
    # Only allow known columns
    allowed = {'username','name','email','role','city','state','phone','address','is_autopay_enabled','notification_preferences'}
    sets = []
    vals = []
    for k,v in kwargs.items():
        if k in allowed and (column_exists('users', k) or k in {'username','name','email','role'}):
            sets.append(f"{k} = ?")
            vals.append(v)
    if not sets:
        return False, "No valid fields to update."
    vals.append(user_id)
    exec_query(f"UPDATE users SET {', '.join(sets)} WHERE id = ?", tuple(vals))
    return True, "User updated."

def admin_delete_user(user_id):
    # Prevent delete if user has subscriptions/payments
    deps = exec_query("SELECT COUNT(*) FROM subscriptions WHERE user_id = ?", (user_id,), fetch=True)[0][0]
    if deps and deps > 0:
        return False, "Cannot delete: user has subscriptions. Cancel/delete those first."
    exec_query("DELETE FROM users WHERE id = ?", (user_id,))
    return True, "User deleted."

def admin_create_plan(name, speed_mbps, data_limit_gb, price, validity_days, description='', plan_type='basic', is_unlimited=0, features='', upload_speed_mbps=None):
    existing = exec_query("SELECT id FROM plans WHERE name = ?", (name,), fetch=True)
    if existing:
        return False, "Plan name already exists."
    cols = ['name','speed_mbps','data_limit_gb','price','validity_days','description']
    vals = [name, int(speed_mbps), float(data_limit_gb), float(price), int(validity_days), description or '']
    if column_exists('plans','plan_type'):
        cols += ['plan_type']; vals += [plan_type or 'basic']
    if column_exists('plans','is_unlimited'):
        cols += ['is_unlimited']; vals += [1 if is_unlimited else 0]
    if column_exists('plans','features'):
        cols += ['features']; vals += [features or '']
    if column_exists('plans','upload_speed_mbps'):
        cols += ['upload_speed_mbps']; vals += [int(upload_speed_mbps) if upload_speed_mbps is not None else int(speed_mbps)//10]
    if column_exists('plans','created_date'):
        cols += ['created_date']; vals += [utcnow_naive().isoformat()]
    placeholders = ",".join(["?"]*len(vals))
    exec_query(f"INSERT INTO plans ({','.join(cols)}) VALUES ({placeholders})", tuple(vals))
    return True, "Plan created."

def admin_update_plan(plan_id, **kwargs):
    allowed = {'name','speed_mbps','data_limit_gb','price','validity_days','description','plan_type','is_unlimited','features','upload_speed_mbps'}
    sets = []; vals = []
    for k,v in kwargs.items():
        if k in allowed and (column_exists('plans', k) or k in {'name','speed_mbps','data_limit_gb','price','validity_days','description'}):
            sets.append(f"{k} = ?")
            if k in {'speed_mbps','upload_speed_mbps','validity_days'} and v is not None:
                vals.append(int(v))
            elif k in {'data_limit_gb','price'} and v is not None:
                vals.append(float(v))
            else:
                vals.append(v)
    if not sets:
        return False, "No valid fields to update."
    vals.append(plan_id)
    exec_query(f"UPDATE plans SET {', '.join(sets)} WHERE id = ?", tuple(vals))
    return True, "Plan updated."

def admin_delete_plan(plan_id):
    deps = exec_query("SELECT COUNT(*) FROM subscriptions WHERE plan_id = ?", (plan_id,), fetch=True)[0][0]
    if deps and deps > 0:
        return False, "Cannot delete: plan is referenced in subscriptions."
    exec_query("DELETE FROM plans WHERE id = ?", (plan_id,))
    return True, "Plan deleted."

def admin_send_message(message, target="all"):
    """
    Send a custom message from admin to users.
    target: "all", "active", "inactive"
    """
    now = utcnow_naive().isoformat()

    if target == "all":
        user_rows = exec_query("SELECT id FROM users WHERE role = 'user'", fetch=True)
    elif target == "active":
        user_rows = exec_query("""
            SELECT DISTINCT u.id 
            FROM users u
            JOIN subscriptions s ON u.id = s.user_id
            WHERE u.role = 'user' AND s.status = 'active'
        """, fetch=True)
    elif target == "inactive":
        user_rows = exec_query("""
            SELECT id FROM users
            WHERE role = 'user' AND id NOT IN (
                SELECT user_id FROM subscriptions WHERE status = 'active'
            )
        """, fetch=True)
    else:
        return False, "Invalid target"

    for row in user_rows:
        exec_query(
            "INSERT INTO notifications (user_id, message, notification_type, created_date) VALUES (?, ?, ?, ?)",
            (row[0], message, "admin_broadcast", now)
        )
    return True, f"Message sent to {len(user_rows)} users."

# ---------------------------
# UI Components (Enhanced)
# ---------------------------
def render_metric_card(title, value, delta=None, delta_color="normal"):
    if delta:
        delta_html = f"<div style='color: {'green' if delta_color == 'normal' else 'red'}; font-size: 0.8rem;'>{delta}</div>"
    else:
        delta_html = ""
    
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="color: white; margin: 0; height : 5px ; width:400px;">{title}</h4>
        <h2 style="color: white; margin: 0.5rem 0; height : 50px ; width : 400px;">{value}</h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_partial_circle_progress(days_left, start_date, end_date, pct_visible=80):
    """
    Donut-style circle with missing slice at bottom.
    pct_visible = percent of circle filled (e.g. 80 means 80% arc shown).
    Color by days_left:
      - 30–16 = green
      - 15–6 = orange
      - 5–0 = red
    """
    # Pick color by days_left
    if days_left >= 16:
        bar_color = "#10b981"   # green
    elif days_left >= 6:
        bar_color = "#f59e0b"   # orange
    else:
        bar_color = "#ef4444"   # red

    visible = pct_visible
    hidden = 100 - pct_visible
    values = [visible, hidden]

    import plotly.graph_objects as go
    fig = go.Figure(go.Pie(
        values=values,
        hole=0.70,
        sort=False,
        direction="clockwise",
        rotation=220,   # <-- shift so missing slice is at bottom center
        textinfo="none",
        hoverinfo="skip",
        marker=dict(colors=[bar_color, "rgba(0,0,0,0)"]),
        showlegend=False
    ))

    # Center label
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"<b>{int(days_left)}</b><br>days left",
        showarrow=False, font=dict(size=16, color=bar_color), align="center"
    )

    # Dates
    fig.add_annotation(x=0.5, y=0.05, text=f"Started: {start_date}",
                       showarrow=False, font=dict(size=10, color="#6b7280"))
    fig.add_annotation(x=0.5, y=0.95, text=f"Expires: {end_date}",
                       showarrow=False, font=dict(size=10, color="#6b7280"))

    fig.update_layout(
                        margin=dict(l=0, r=0, t=0, b=0),
                        height=250,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
    return fig







def render_plan_card(
    plan,
    is_current: bool = False,
    is_recommended: bool = False,
    show_actions: bool = True,
    current_user_id: int | None = None,
    section: str = "test"
        ):
    card_class = "current-plan-card" if is_current else "recommended-plan" if is_recommended else "plan-card"

    status_badge = ""
    if is_current:
        status_badge = '<span class="status-active">Current Plan</span>'
    elif is_recommended:
        status_badge = '<span class="status-active">Recommended</span>'

    features_text = plan.get('features', '')
    upload_speed = plan.get('upload_speed_mbps', plan['speed_mbps'] // 10)

    st.markdown(f"""
    <div class="{card_class}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h3 style="margin: 0; color: #1f2937;">{plan['name']} {status_badge}</h3>
                <p style="color: #6b7280; margin: 0.5rem 0;">{plan['description']}</p>
                {f"<p style='color: #4f46e5; font-size: 0.9rem; margin: 0.5rem 0;'><strong>Features:</strong> {features_text}</p>" if features_text else ""}
            </div>
            <div style="text-align: right;">
                <h2 style="margin: 0; color: #667eea;">₹{plan['price']}</h2>
                <p style="color: #6b7280; margin: 0;">/month</p>
            </div>
        </div>
        <div style="margin: 1rem 0;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                <div><strong>Download:</strong> {plan['speed_mbps']} Mbps</div>
                <div><strong>Upload:</strong> {upload_speed} Mbps</div>
                <div><strong>Data:</strong> {'Unlimited' if plan.get('is_unlimited') else f"{plan['data_limit_gb']} GB"}</div>
                <div><strong>Validity:</strong> {plan['validity_days']} days</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if show_actions and not is_current:
        # ensure section-specific unique keys
        sec = section or "default"
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(
                f"Subscribe to {plan['name']}",
                key=f"{sec}_sub_{plan['id']}_{current_user_id}",
                use_container_width=True
            ):
                subscribe_user_to_plan(current_user_id, plan['id'])
                create_payment(None, current_user_id, plan['price'])
                st.success(f"Successfully subscribed to {plan['name']}!")
                st.rerun()
        with col2:
            if st.button(
                "Add to Compare",
                key=f"{sec}_comp_{plan['id']}_{current_user_id}",
                use_container_width=True
            ):
                if 'comparison_plans' not in st.session_state:
                    st.session_state['comparison_plans'] = []
                if plan['id'] not in [p['id'] for p in st.session_state['comparison_plans']]:
                    st.session_state['comparison_plans'].append(plan)
                    st.success(f"Added {plan['name']} to comparison!")
                else:
                    st.info("Plan already in comparison list!")
        with col3:
            if st.button(
                "View Details",
                key=f"{sec}_det_{plan['id']}_{current_user_id}",
                use_container_width=True
            ):
                st.session_state[f'show_plan_details_{plan["id"]}'] = True




def render_expiry_reminder(reminder):
    """Render expiry reminder with appropriate styling"""
    if reminder['type'] == 'critical':
        st.markdown(f"""
        <div class="expiry-critical">
            <h4 style="margin: 0; color: #dc2626;">⚠️ Plan Expired!</h4>
            <p style="margin: 0.5rem 0; color: #991b1b;">{reminder['message']}</p>
        </div>
        """, unsafe_allow_html=True)
    elif reminder['type'] == 'warning':
        st.markdown(f"""
        <div class="expiry-warning">
            <h4 style="margin: 0; color: #d97706;">⏰ Plan Expiring Soon!</h4>
            <p style="margin: 0.5rem 0; color: #92400e;">{reminder['message']}</p>
        </div>
        """, unsafe_allow_html=True)

def render_usage_analytics(user_id):
    """Render detailed usage analytics"""
    usage_df = get_usage_for_user(user_id, days=30)
    
    if usage_df.empty:
        st.info("No usage data available yet.")
        return
    
    usage_df['date'] = pd.to_datetime(usage_df['date'])
    usage_df = usage_df.sort_values('date')
    
    # Calculate statistics
    total_usage = usage_df['data_used_gb'].sum()
    avg_daily = usage_df['data_used_gb'].mean()
    max_daily = usage_df['data_used_gb'].max()
    
    # Usage metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Usage (30d)", f"{total_usage:.1f} GB")
    with col2:
        st.metric("Daily Average", f"{avg_daily:.1f} GB")
    with col3:
        st.metric("Peak Day", f"{max_daily:.1f} GB")
    with col4:
        projected_monthly = avg_daily * 30
        st.metric("Projected Monthly", f"{projected_monthly:.1f} GB")
    
    # Usage trend chart
    fig = px.line(usage_df, x='date', y='data_used_gb',
                 title="Daily Usage Trend (Last 30 Days)",
                 labels={'data_used_gb': 'Usage (GB)', 'date': 'Date'})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Peak vs Off-peak usage (if available)
    if 'peak_hour_usage' in usage_df.columns and 'off_peak_usage' in usage_df.columns:
        st.subheader("Peak vs Off-Peak Usage")
        
        peak_avg = usage_df['peak_hour_usage'].mean()
        off_peak_avg = usage_df['off_peak_usage'].mean()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Peak Hours Avg", f"{peak_avg:.1f} GB")
        with col2:
            st.metric("Off-Peak Avg", f"{off_peak_avg:.1f} GB")
        
        # Peak vs off-peak chart
        usage_comparison = pd.DataFrame({
            'Type': ['Peak Hours', 'Off-Peak'],
            'Average Usage': [peak_avg, off_peak_avg]
        })
        
        fig = px.bar(usage_comparison, x='Type', y='Average Usage',
                    title="Peak vs Off-Peak Usage Comparison",
                    color='Type')
        st.plotly_chart(fig, use_container_width=True)

def render_plan_comparison():
    """Render plan comparison functionality"""
    st.subheader("Compare Plans")
    
    # Initialize comparison list in session state
    if 'comparison_plans' not in st.session_state:
        st.session_state['comparison_plans'] = []
    
    # Plan search and add functionality
    all_plans = get_all_plans()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_plan_name = st.selectbox(
            "Search and add plans to compare:",
            options=["Select a plan..."] + [p['name'] for p in all_plans],
            key="plan_search_select"
        )
    with col2:
        if st.button("Add Plan", disabled=(selected_plan_name == "Select a plan...")):
            selected_plan = next((p for p in all_plans if p['name'] == selected_plan_name), None)
            if selected_plan and selected_plan not in st.session_state['comparison_plans']:
                st.session_state['comparison_plans'].append(selected_plan)
                st.success(f"Added {selected_plan['name']} to comparison!")
                st.rerun()
            elif selected_plan in st.session_state['comparison_plans']:
                st.info("Plan already in comparison!")
    
    # Display comparison table
    if st.session_state['comparison_plans']:
        st.markdown("### Comparison Table")
        
        # Create comparison dataframe
        comparison_data = []
        for plan in st.session_state['comparison_plans']:
            comparison_data.append({
                'Plan Name': plan['name'],
                'Price (₹)': plan['price'],
                'Speed (Mbps)': plan['speed_mbps'],
                'Upload (Mbps)': plan.get('upload_speed_mbps', plan['speed_mbps'] // 10),
                'Data Limit': 'Unlimited' if plan.get('is_unlimited') else f"{plan['data_limit_gb']} GB",
                'Validity': f"{plan['validity_days']} days",
                'Type': plan.get('plan_type', 'basic').title(),
                'Price/GB': f"₹{plan['price']/plan['data_limit_gb']:.2f}" if not plan.get('is_unlimited') else 'N/A'
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Clear comparison button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Clear All", type="secondary"):
                st.session_state['comparison_plans'] = []
                st.rerun()
        
        # Save comparison (if user is logged in)
        with col2:
            if st.button("Save Comparison", key="save_comparison"):
                if st.session_state.get('user'):
                    plan_ids = [p['id'] for p in st.session_state['comparison_plans']]
                    save_plan_comparison(st.session_state['user']['id'], plan_ids)
                    st.success("Comparison saved!")
    else:
        st.info("Add plans to compare them side by side.")

def render_billing_history(user_id):
    """Render comprehensive billing history"""
    st.subheader("Billing History")
    
    # Get payment history with enhanced details
    payment_query = """
    SELECT 
        p.amount, p.payment_date, p.status, p.bill_month, p.bill_year,
        s.start_date, s.end_date,
        pl.name as plan_name
    """
    
    if column_exists('payments', 'payment_method'):
        payment_query += ", p.payment_method"
    if column_exists('payments', 'transaction_id'):
        payment_query += ", p.transaction_id"
    if column_exists('payments', 'tax_amount'):
        payment_query += ", p.tax_amount, p.discount"
    
    payment_query += """
    FROM payments p
    LEFT JOIN subscriptions s ON p.subscription_id = s.id
    LEFT JOIN plans pl ON s.plan_id = pl.id
    WHERE p.user_id = ?
    ORDER BY p.payment_date DESC
    LIMIT 50
    """
    
    payments_df = df_from_query(payment_query, (user_id,))
    
    if payments_df.empty:
        st.info("No billing history found.")
        return
    
    # Payment statistics
    total_paid = payments_df[payments_df['status'] == 'paid']['amount'].sum()
    failed_payments = len(payments_df[payments_df['status'] == 'failed'])
    avg_monthly = payments_df[payments_df['status'] == 'paid']['amount'].mean()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Paid", f"₹{total_paid:,.0f}")
    with col2:
        st.metric("Failed Payments", failed_payments)
    with col3:
        st.metric("Average Payment", f"₹{avg_monthly:,.0f}")
    
    # Payment history table
    st.markdown("### Payment Records")
    
    # Format dates and amounts for display
    display_df = payments_df.copy()
    display_df['payment_date'] = pd.to_datetime(display_df['payment_date']).dt.strftime('%Y-%m-%d')
    display_df['amount'] = display_df['amount'].apply(lambda x: f"₹{x:,.0f}")
    
    # Select columns to display
    display_columns = ['payment_date', 'plan_name', 'amount', 'status']
    if 'payment_method' in display_df.columns:
        display_columns.append('payment_method')
    if 'transaction_id' in display_df.columns:
        display_columns.append('transaction_id')
    
    st.dataframe(display_df[display_columns], use_container_width=True)
    
    # Payment trends chart
    if len(payments_df) > 3:
        st.markdown("### Payment Trends")
        
        # Monthly payment trends
        payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])
        payments_df['month_year'] = payments_df['payment_date'].dt.to_period('M')
        
        monthly_trends = payments_df[payments_df['status'] == 'paid'].groupby('month_year')['amount'].sum().reset_index()
        monthly_trends['month_year'] = monthly_trends['month_year'].astype(str)
        
        fig = px.line(monthly_trends, x='month_year', y='amount',
                     title="Monthly Payment Trends",
                     labels={'amount': 'Amount (₹)', 'month_year': 'Month'})
        st.plotly_chart(fig, use_container_width=True)



def user_dashboard(user):
    st.title("🏠 My Dashboard")
    st.markdown(f"Welcome back, **{user['name']}**!")
    
    # Add notifications in sidebar
    st.sidebar.subheader("Notifications")
    unread_notifications = get_user_notifications(user['id'], limit=5, unread_only=True)

    if unread_notifications:
        for notification in unread_notifications:
            with st.sidebar.expander(f"New: {notification['notification_type'].replace('_', ' ').title()}"):
                st.write(notification['message'])
                if st.button("Mark as read", key=f"mark_read_{notification['id']}"):
                    mark_notification_read(notification['id'])
                    st.rerun()
    else:
        st.sidebar.write("No new notifications")
    
    # Check for expiry reminders first
    reminders = check_expiry_reminders(user['id'])
    for reminder in reminders:
        render_expiry_reminder(reminder)
    
    # Get current subscription for later use
    current_sub = get_user_active_subscription(user['id'])
    
    # ============================================================================
    # STATIC CARDS SECTION (Always visible at top)
    # ============================================================================
    
    st.markdown("---")
    st.markdown("### 🎛️ Quick Actions")
    
    # CSS for card styling
    st.markdown("""
            <style>
            .card-container {
                transition: all 0.3s ease;
            }

            .card-container:hover {
                transform: translateY(-8px);
                box-shadow: 0 12px 24px rgba(0,0,0,0.15) !important;
                background: linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%) !important;
                border-color: #87CEEB !important;
            }

            .card-container:hover .card-title {
                color: white !important;
            }

            .card-container:hover .card-icon {
                filter: drop-shadow(0 2px 4px rgba(255,255,255,0.3)) !important;
            }

            .card-button {
                transition: all 0.3s ease;
            }

            .card-button:hover {
                background: white !important;
                color: #2563eb !important;
                transform: scale(1.05);
                border-color: white !important;
            }
            </style>
            """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    card_style = """
            <div class="card-container" style="
            background: white;
            border: 2px solid #f1f5f9;
            border-radius: 20px;
            padding: 2rem 1rem;
            text-align: center;
            color: #334155;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin-bottom: 1rem;
        ">
            <div style="
                font-size: 2.5rem; 
                margin-bottom: 0.8rem;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
            ">{icon}</div>
            <div style="
                font-size: 1.1rem; 
                font-weight: 600; 
                margin-bottom: 1.2rem;
                color: #1e293b;
            ">{title}</div>
            <button class="card-button" style="
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 0.6rem 1.8rem;
                background: #f8fafc;
                color: #475569;
                font-weight: 600;
                cursor: pointer;
                font-size: 0.9rem;
            ">{btn_text}</button>
        </div>
        """

    with col1:
        st.markdown(card_style.format(
                    icon="📶", 
                    title="My WiFi", 
                    btn_text="Manage"
                ), unsafe_allow_html=True)

    with col2:
        st.markdown(card_style.format(
                    icon="🆕", 
                    title="New Connection", 
                    btn_text="Apply"
                ), unsafe_allow_html=True)

    with col3:
        st.markdown(card_style.format(
                    icon="💳", 
                    title="Pay Bills", 
                    btn_text="Pay Now"
                ), unsafe_allow_html=True)

    with col4:
        st.markdown(card_style.format(
                    icon="🛠️", 
                    title="Support", 
                    btn_text="Get Help"
                ), unsafe_allow_html=True)

    st.markdown("---")
    
    # ============================================================================
    # SECTION TABS/NAVIGATION
    # ============================================================================
    
    if 'active_section' not in st.session_state:
        st.session_state.active_section = 'current_plan'
    
    st.markdown("### 📋 Dashboard Sections")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📶 Current Plan", use_container_width=True, 
                    type="primary" if st.session_state.active_section == 'current_plan' else "secondary"):
            st.session_state.active_section = 'current_plan'
    
    with col2:
        if st.button("📊 Data Usage Insights", use_container_width=True,
                    type="primary" if st.session_state.active_section == 'data_usage' else "secondary"):
            st.session_state.active_section = 'data_usage'
    
    with col3:
        if st.button("📋 All Plans", use_container_width=True,
                    type="primary" if st.session_state.active_section == 'all_plans' else "secondary"):
            st.session_state.active_section = 'all_plans'
    
    with col4:
        if st.button("⚖️ Compare Plans", use_container_width=True,
                    type="primary" if st.session_state.active_section == 'compare_plans' else "secondary"):
            st.session_state.active_section = 'compare_plans'
    
    with col5:
        if st.button("📋 Subscription History", use_container_width=True,
                    type="primary" if st.session_state.active_section == 'subscription_history' else "secondary"):
            st.session_state.active_section = 'subscription_history'
    
    st.markdown("---")
    
    # ============================================================================
    # SECTION CONTENT BASED ON SELECTION
    # ============================================================================
    
    # CURRENT PLAN SECTION
    if st.session_state.active_section == 'current_plan':
        st.markdown("## 📶 Your Current Plan")
        
        if current_sub:
            current_plan = get_plan(current_sub['plan_id'])
            
            try:
                start_date = datetime.fromisoformat(current_sub['start_date']).date()
                end_date = datetime.fromisoformat(current_sub['end_date']).date()
                today = datetime.utcnow().date()
                
                total_days = (end_date - start_date).days
                days_passed = (today - start_date).days
                days_remaining = (end_date - today).days
                
                percentage = min(100, max(0, (days_passed / total_days) * 100))
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    fig = render_partial_circle_progress(
                        days_left=max(0, days_remaining),
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d'),
                        pct_visible=80
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                with col2:
                    render_plan_card(current_plan, is_current=True, show_actions=False)

            except Exception as e:
                render_plan_card(current_plan, is_current=True, show_actions=False)

        else:
            st.info("🎯 You don't have an active plan. Choose one below to get started!")
    
    # DATA USAGE INSIGHTS SECTION
    elif st.session_state.active_section == 'data_usage':
        st.markdown("## 📊 Data Usage Insights")
        
        st.markdown("### 📈 Usage Overview")
        render_usage_analytics(user['id'])
        
        st.markdown("---")
        st.markdown("### 📈 Usage Insights & Smart Recommendations")
        
        usage_df = get_usage_for_user(user['id'], days=60)
        if not usage_df.empty:
            avg_daily = usage_df['data_used_gb'].mean()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Usage Pattern Analysis")
                if avg_daily < 2:
                    pattern = "Light User"
                    recommendation = "You're a light user. Consider our Basic plans for cost savings."
                elif avg_daily < 5:
                    pattern = "Moderate User"
                    recommendation = "You have moderate usage. Standard plans offer good value."
                else:
                    pattern = "Heavy User"
                    recommendation = "You're a heavy user. Premium plans with higher limits suit you best."
                
                st.info(f"**Pattern:** {pattern}")
                st.success(f"**Recommendation:** {recommendation}")
            
            with col2:
                if current_sub:
                    current_plan = get_plan(current_sub['plan_id'])
                    monthly_usage = avg_daily * 30
                    usage_ratio = monthly_usage / current_plan['data_limit_gb'] * 100
                    
                    st.markdown("#### Plan Utilization")
                    st.progress(min(usage_ratio / 100, 1.0))
                    st.write(f"You're using {usage_ratio:.1f}% of your plan limit")
                    
                    if usage_ratio > 80:
                        st.warning("Consider upgrading to a higher limit plan!")
                    elif usage_ratio < 30:
                        st.info("You might save money with a lower limit plan.")
        else:
            st.info("No usage data available for analysis.")
    
    # ALL PLANS SECTION
    elif st.session_state.active_section == 'all_plans':
        st.markdown("## 📋 All Available Plans")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            price_filter = st.selectbox("Filter by Price", 
                                       ["All", "Under ₹500", "₹500-₹1000", "Above ₹1000"])
        with col2:
            speed_filter = st.selectbox("Filter by Speed", 
                                       ["All", "Up to 100 Mbps", "100-500 Mbps", "500+ Mbps"])
        with col3:
            type_filter = st.selectbox("Filter by Type",
                                      ["All", "Basic", "Standard", "Premium", "Elite"])
        
        all_plans = get_all_plans()
        filtered_plans = all_plans.copy()
        
        if price_filter != "All":
            if price_filter == "Under ₹500":
                filtered_plans = [p for p in filtered_plans if p['price'] < 500]
            elif price_filter == "₹500-₹1000":
                filtered_plans = [p for p in filtered_plans if 500 <= p['price'] <= 1000]
            else:
                filtered_plans = [p for p in filtered_plans if p['price'] > 1000]
        
        if speed_filter != "All":
            if speed_filter == "Up to 100 Mbps":
                filtered_plans = [p for p in filtered_plans if p['speed_mbps'] <= 100]
            elif speed_filter == "100-500 Mbps":
                filtered_plans = [p for p in filtered_plans if 100 < p['speed_mbps'] <= 500]
            else:
                filtered_plans = [p for p in filtered_plans if p['speed_mbps'] > 500]
        
        if type_filter != "All":
            filtered_plans = [p for p in filtered_plans if p.get('plan_type', 'basic').lower() == type_filter.lower()]
        
        if filtered_plans:
            for plan in filtered_plans:
                is_current_plan = current_sub and plan['id'] == current_sub['plan_id']
                render_plan_card(
                    plan,
                    is_current=is_current_plan,
                    current_user_id=user['id'],
                    section="all"
                )
        else:
            st.warning("No plans match your filter criteria.")
    
    # COMPARE PLANS SECTION
    elif st.session_state.active_section == 'compare_plans':
        st.markdown("## ⚖️ Compare Plans")
        render_plan_comparison()
    
    # SUBSCRIPTION HISTORY SECTION
    elif st.session_state.active_section == 'subscription_history':
        st.markdown("## 📋 Subscription History")
        
        subscription_history = get_user_subscription_history(user['id'])
        if subscription_history:
            history_data = []
            for sub in subscription_history:
                history_data.append({
                    'Plan': sub['plan_name'],
                    'Start Date': sub['start_date'],
                    'End Date': sub['end_date'],
                    'Status': sub['status'].title(),
                    'Price': f"₹{sub['price']}",
                    'Speed': f"{sub['speed_mbps']} Mbps",
                    'Data': f"{sub['data_limit_gb']} GB"
                })
            
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No subscription history available.")



# ---------------------------
# Enhanced Admin Dashboard
# ---------------------------
def admin_dashboard(user):
    st.title("🛠️ Admin Dashboard")
    st.markdown(f"Welcome back, **{user['name']}**!")
    
    

    


    """Evaluate the ML model performance"""
    if not os.path.exists('plan_recommendation_model.pkl'):
        st.error("No model found to evaluate")
        return
    
    try:
        model = joblib.load('plan_recommendation_model.pkl')
        training_data = collect_training_data()
        
        if training_data.empty:
            st.error("Not enough data to evaluate model")
            return
        
        training_data = engineer_features(training_data)
        
        feature_columns = [
            'avg_daily_usage', 'max_daily_usage', 'usage_std',
            'estimated_monthly_usage', 'days_since_signup',
            'weekday_avg', 'weekend_avg', 'usage_consistency',
            'city', 'state'
        ]
        
        # Check which features are actually available
        available_features = [col for col in feature_columns if col in training_data.columns]
        
        if not available_features:
            st.error("No suitable features available for evaluation")
            return
        
        target_column = 'plan_category'
        
        X = training_data[available_features]
        y = training_data[target_column]
        
        # Make predictions
        y_pred = model.predict(X)
        
        # Display metrics
        st.subheader("Model Performance Metrics")
        
        accuracy = accuracy_score(y, y_pred)
        accuracy_percent = accuracy * 100
        
        st.metric("Model Accuracy", f"{accuracy_percent:.1f}%")
        
        # Classification report
        report = classification_report(y, y_pred, output_dict=True)
        report_df = pd.DataFrame(report).transpose()
        st.dataframe(report_df.style.format("{:.3f}"))
        
        # Feature importance if available
        if hasattr(model.named_steps['classifier'], 'feature_importances_'):
            st.subheader("Feature Importance")
            
            # Get feature names after preprocessing
            numeric_features = [col for col in ['avg_daily_usage', 'max_daily_usage', 'usage_std', 
                              'estimated_monthly_usage', 'days_since_signup',
                              'weekday_avg', 'weekend_avg', 'usage_consistency'] if col in available_features]
            categorical_features = [col for col in ['city', 'state'] if col in available_features]
            
            if categorical_features:
                try:
                    cat_encoder = model.named_steps['preprocessor'].named_transformers_['cat']
                    cat_feature_names = cat_encoder.get_feature_names_out(categorical_features)
                    all_features = numeric_features + list(cat_feature_names)
                except:
                    all_features = available_features
            else:
                all_features = numeric_features
            
            importances = model.named_steps['classifier'].feature_importances_
            
            if len(all_features) == len(importances):
                feature_importance = pd.DataFrame({
                    'Feature': all_features,
                    'Importance': importances
                }).sort_values('Importance', ascending=False)
                
                fig = px.bar(feature_importance.head(10), x='Importance', y='Feature', 
                           orientation='h', title="Top 10 Feature Importances")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Feature names and importances don't match. Skipping feature importance chart.")
        
    except Exception as e:
        st.error(f"Error evaluating model: {str(e)}")

# ---------------------------
# Main Application
# ---------------------------
def main():
    st.set_page_config(
        page_title="Enhanced Broadband Portal",
        layout='wide',
        initial_sidebar_state="expanded",
        page_icon="📡"
    )
    
    load_css()
    create_tables()
    migrate_database()
    ensure_default_admin()
    create_comprehensive_mock_data()
    populate_usage_for_all_users(days=60)

    
    if 'user' not in st.session_state:
        st.session_state['user'] = None

    # Sidebar Authentication
    with st.sidebar:
        st.title("📡 Broadband Portal")
        
        if st.session_state['user'] is None:
            st.markdown("### Welcome Back")
            
            tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
            
            with tab1:
                with st.form("signin_form"):
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type='password', placeholder="Enter your password")
                    submit = st.form_submit_button("Sign In", use_container_width=True)
                    
                    if submit and username and password:
                        ok, res = signin(username, password)
                        if ok:
                            st.session_state['user'] = res
                            st.success("Welcome back!")
                            st.rerun()
                        else:
                            st.error(res)
            
            with tab2:
                with st.form("signup_form"):
                    new_username = st.text_input("Choose Username", placeholder="Enter username")
                    new_password = st.text_input("Password", type='password', placeholder="Create password")
                    full_name = st.text_input("Full Name", placeholder="Enter your full name")
                    email = st.text_input("Email", placeholder="Enter your email")
                    submit_signup = st.form_submit_button("Create Account", use_container_width=True)
                    
                    if submit_signup and new_username and new_password and full_name and email:
                        ok, msg = signup(new_username, new_password, full_name, email)
                        if ok:
                            st.success("Account created! Please sign in.")
                        else:
                            st.error(msg)
        else:
            user = st.session_state['user']
            st.markdown("---")
            st.markdown(f"**👤 {user['name']}**")
            st.markdown(f"*{user['role'].title()}*")
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state['user'] = None
                st.rerun()

    # Main Content Area
    if st.session_state['user'] is None:
        # Landing page for non-authenticated users
        st.markdown("""
        <div style="text-align: center; padding: 4rem 0;">
            <h1 style="font-size: 3rem; margin-bottom: 1rem;">📡 Welcome to Enhanced Broadband Portal</h1>
            <p style="font-size: 1.2rem; color: #6b7280; margin-bottom: 2rem;">
                Your gateway to intelligent internet plans with AI-powered recommendations
            </p>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 12px; padding: 2rem; color: white; margin: 2rem 0;">
                <h3>Why Choose Our Enhanced Service?</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; margin-top: 1rem;">
                    <div>🚀 High-Speed Internet</div>
                    <div>🤖 AI-Powered Recommendations</div>
                    <div>📊 Usage Analytics</div>
                    <div>💰 Smart Plan Comparison</div>
                    <div>🛡️ Reliable Service</div>
                    <div>📱 Mobile-First Design</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show sample plans
        st.markdown("### 📋 Featured Plans")
        plans = get_all_plans()[:4]
        
        if len(plans) >= 2:
            cols = st.columns(2)
            for i, plan in enumerate(plans):
                with cols[i % 2]:
                    render_plan_card(plan, show_actions=False)
        
        return

    user = st.session_state['user']
    if user['role'] == 'admin':
        admin_dashboard(user)
    else:
        user_dashboard(user)

if __name__ == '__main__':
    main()