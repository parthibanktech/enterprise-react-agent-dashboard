import os
import sqlite3

# Define relative path safely
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "products.sqlite")

def seed_database():
    """Seed a local SQLite database with product catalog information."""
    print("[DB] Initializing SQLite database at:", DB_PATH)
    
    # Ensure parent folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Robust failover: if file doesn't exist and we have the pre-seeded file in root, copy it
    root_preseeded = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mission2_products.sqlite")
    if not os.path.exists(DB_PATH) and os.path.exists(root_preseeded):
        print(f"[DB] Copying pre-seeded database from root '{root_preseeded}' to '{DB_PATH}'...")
        try:
            import shutil
            shutil.copy2(root_preseeded, DB_PATH)
            print("[DB] Database successfully copied and prepared.")
            return
        except Exception as e:
            print(f"[DB] Warning: Failed to copy pre-seeded database: {e}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
        """)
        
        # Check if table has rows already
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("[DB] Seeding product catalog rows...")
            products = [
                ("Ergonomic Desk Chair", "Furniture", 249.99, 45),
                ("Mechanical Keyboard", "Electronics", 129.50, 80),
                ("UltraWide 34-inch Monitor", "Electronics", 499.00, 20),
                ("USB-C Hub Multiport", "Electronics", 39.99, 150),
                ("Noise-Cancelling Headphones", "Electronics", 299.99, 35),
                ("Bamboo Standing Desk", "Furniture", 599.00, 15),
                ("Wireless Ergonomic Mouse", "Electronics", 79.99, 110)
            ]
            cursor.executemany("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)", products)
            conn.commit()
            print("[DB] Database successfully seeded with 7 products.")
        else:
            print(f"[DB] Database already contains {count} rows. Skipping seeding.")
        conn.close()
    except sqlite3.OperationalError as e:
        if "disk I/O error" in str(e) and os.path.exists(root_preseeded):
            print(f"[DB] SQLite Disk I/O Error detected. Fallback: Copying '{root_preseeded}'...")
            import shutil
            shutil.copy2(root_preseeded, DB_PATH)
            print("[DB] Fallback database copy completed successfully.")
        else:
            raise e

if __name__ == "__main__":
    seed_database()
