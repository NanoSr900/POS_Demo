import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import datetime

# --- Database Setup ---
conn = sqlite3.connect("pos_demo.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL,
    stock INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    product TEXT,
    qty INTEGER,
    total REAL,
    date TEXT
)
""")

cursor.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', '1234')")
conn.commit()

# --- Login Window ---
def login():
    user = entry_user.get()
    pwd = entry_pass.get()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
    if cursor.fetchone():
        messagebox.showinfo("Login", "Login successful!")
        login_win.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Login", "Invalid credentials")

login_win = tk.Tk()
login_win.title("POS Login")
login_win.geometry("350x200")
login_win.configure(bg="#f0f0f0")

tk.Label(login_win, text="Point of Sale System", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)
tk.Label(login_win, text="Username", bg="#f0f0f0").pack()
entry_user = tk.Entry(login_win)
entry_user.pack(pady=5)

tk.Label(login_win, text="Password", bg="#f0f0f0").pack()
entry_pass = tk.Entry(login_win, show="*")
entry_pass.pack(pady=5)

tk.Button(login_win, text="Login", bg="#4CAF50", fg="white", command=login).pack(pady=10)

# --- Dashboard ---
def open_dashboard():
    dash = tk.Tk()
    dash.title("POS Dashboard")
    dash.geometry("700x500")
    dash.configure(bg="#e6f7ff")

    tk.Label(dash, text="POS Dashboard", font=("Arial", 16, "bold"), bg="#e6f7ff").pack(pady=10)

    # --- Add Product Frame ---
    product_frame = tk.LabelFrame(dash, text="Add Product", padx=10, pady=10, bg="#ffffff")
    product_frame.pack(fill="x", padx=20, pady=10)

    def add_product():
        name = entry_name.get()
        price = float(entry_price.get())
        stock = int(entry_stock.get())
        cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
        conn.commit()
        messagebox.showinfo("Product", f"{name} added successfully!")

    tk.Label(product_frame, text="Name").grid(row=0, column=0, padx=5, pady=5)
    entry_name = tk.Entry(product_frame)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(product_frame, text="Price").grid(row=1, column=0, padx=5, pady=5)
    entry_price = tk.Entry(product_frame)
    entry_price.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(product_frame, text="Stock").grid(row=2, column=0, padx=5, pady=5)
    entry_stock = tk.Entry(product_frame)
    entry_stock.grid(row=2, column=1, padx=5, pady=5)

    tk.Button(product_frame, text="Add Product", bg="#2196F3", fg="white", command=add_product).grid(row=3, columnspan=2, pady=10)

    # --- Sales Frame ---
    sales_frame = tk.LabelFrame(dash, text="Sales Form", padx=10, pady=10, bg="#ffffff")
    sales_frame.pack(fill="x", padx=20, pady=10)

    def process_sale():
        product = entry_sale_name.get()
        qty = int(entry_sale_qty.get())
        cursor.execute("SELECT price, stock FROM products WHERE name=?", (product,))
        result = cursor.fetchone()
        if result:
            price, stock = result
            if qty <= stock:
                total = price * qty
                new_stock = stock - qty
                cursor.execute("UPDATE products SET stock=? WHERE name=?", (new_stock, product))
                cursor.execute("INSERT INTO sales (product, qty, total, date) VALUES (?, ?, ?, ?)",
                               (product, qty, total, datetime.date.today().isoformat()))
                conn.commit()
                messagebox.showinfo("Sale", f"Sale successful!\nTotal: ${total}")
                with open("receipt.txt", "a") as f:
                    f.write(f"{datetime.datetime.now()} - {product} x{qty} = ${total}\n")
            else:
                messagebox.showerror("Sale", "Not enough stock!")
        else:
            messagebox.showerror("Sale", "Product not found!")

    tk.Label(sales_frame, text="Product").grid(row=0, column=0, padx=5, pady=5)
    entry_sale_name = tk.Entry(sales_frame)
    entry_sale_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(sales_frame, text="Quantity").grid(row=1, column=0, padx=5, pady=5)
    entry_sale_qty = tk.Entry(sales_frame)
    entry_sale_qty.grid(row=1, column=1, padx=5, pady=5)

    tk.Button(sales_frame, text="Process Sale", bg="#FF5722", fg="white", command=process_sale).grid(row=2, columnspan=2, pady=10)

    # --- Reporting Button ---
    def open_report():
        report = tk.Toplevel(dash)
        report.title("Sales & Inventory Report")
        report.geometry("600x400")
        report.configure(bg="#fffbe6")

        tk.Label(report, text="Daily Sales Report", font=("Arial", 14, "bold"), bg="#fffbe6").pack(pady=10)
        today = datetime.date.today().isoformat()
        cursor.execute("SELECT product, qty, total FROM sales WHERE date=?", (today,))
        sales = cursor.fetchall()

        tree = ttk.Treeview(report, columns=("Product", "Qty", "Total"), show="headings")
        tree.heading("Product", text="Product")
        tree.heading("Qty", text="Quantity")
        tree.heading("Total", text="Total ($)")
        tree.pack(fill="both", expand=True)

        for s in sales:
            tree.insert("", "end", values=s)

        tk.Label(report, text="Current Inventory", font=("Arial", 14, "bold"), bg="#fffbe6").pack(pady=10)
        cursor.execute("SELECT name, stock FROM products")
        inventory = cursor.fetchall()

        inv_tree = ttk.Treeview(report, columns=("Product", "Stock"), show="headings")
        inv_tree.heading("Product", text="Product")
        inv_tree.heading("Stock", text="Stock")
        inv_tree.pack(fill="both", expand=True)

        for i in inventory:
            inv_tree.insert("", "end", values=i)

    tk.Button(dash, text="View Report", bg="#795548", fg="white", command=open_report).pack(pady=20)

    dash.mainloop()

login_win.mainloop()
