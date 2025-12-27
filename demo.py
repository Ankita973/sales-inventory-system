import sqlite3
from datetime import datetime

DB = "sales_inventory.db"

def connect():
    return sqlite3.connect(DB)

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        total REAL,
        date TEXT,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    conn.commit()
    conn.close()

# ---------- Product CRUD ----------

def add_product():
    name = input("Product name: ")
    price = float(input("Price: "))
    stock = int(input("Stock: "))

    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                (name, price, stock))
    conn.commit()
    conn.close()
    print("✅ Product added.")

def view_products():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()

    print("\nID | Name | Price | Stock")
    print("-" * 30)
    for r in rows:
        print(r)

def update_product():
    pid = int(input("Product ID to update: "))
    price = float(input("New price: "))
    stock = int(input("New stock: "))

    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE products SET price=?, stock=? WHERE id=?",
                (price, stock, pid))
    conn.commit()
    conn.close()
    print("✅ Product updated.")

def delete_product():
    pid = int(input("Product ID to delete: "))

    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    print("✅ Product deleted.")

# ---------- Sales ----------

def record_sale():
    view_products()
    pid = int(input("Enter product ID: "))
    qty = int(input("Quantity sold: "))

    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT price, stock FROM products WHERE id=?", (pid,))
    row = cur.fetchone()

    if not row:
        print("❌ Product not found.")
        conn.close()
        return

    price, stock = row

    if qty > stock:
        print("❌ Not enough stock.")
        conn.close()
        return

    total = price * qty
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("INSERT INTO sales (product_id, quantity, total, date) VALUES (?, ?, ?, ?)",
                (pid, qty, total, date))

    cur.execute("UPDATE products SET stock = stock - ? WHERE id=?",
                (qty, pid))

    conn.commit()
    conn.close()
    print(f"✅ Sale recorded. Total = ₹{total}")

# ---------- Analytics ----------

def total_revenue():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT SUM(total) FROM sales")
    rev = cur.fetchone()[0]
    conn.close()
    print(f"💰 Total Revenue: ₹{rev if rev else 0}")

def top_selling():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name, SUM(s.quantity) as total_sold
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY total_sold DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()

    if row:
        print(f"🏆 Top Product: {row[0]} ({row[1]} sold)")
    else:
        print("No sales yet.")

def low_stock():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, name, stock FROM products WHERE stock < 5")
    rows = cur.fetchall()
    conn.close()

    print("\n⚠️ Low Stock Products:")
    for r in rows:
        print(r)

# ---------- Menu ----------

def menu():
    while True:
        print("""
====== Sales & Inventory System ======
1. Add Product
2. View Products
3. Update Product
4. Delete Product
5. Record Sale
6. Total Revenue
7. Top Selling Product
8. Low Stock Alert
0. Exit
""")
        ch = input("Choose: ")

        if ch == "1":
            add_product()
        elif ch == "2":
            view_products()
        elif ch == "3":
            update_product()
        elif ch == "4":
            delete_product()
        elif ch == "5":
            record_sale()
        elif ch == "6":
            total_revenue()
        elif ch == "7":
            top_selling()
        elif ch == "8":
            low_stock()
        elif ch == "0":
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    init_db()
    menu()
