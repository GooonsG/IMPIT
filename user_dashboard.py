import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_db_connection
from utils import clear_frame

PRIMARY_BLUE = "#2563eb"
LIGHT_BLUE = "#dbeafe"
ACCENT_YELLOW = "#fde047"
WHITE = "#ffffff"
FONT = ("Segoe UI", 12)
HEADER_FONT = ("Segoe UI", 16, "bold")

def style_widgets(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview",
                    background=WHITE,
                    foreground="#222",
                    rowheight=28,
                    fieldbackground=WHITE,
                    font=FONT)
    style.configure("Treeview.Heading",
                    font=FONT,
                    background=PRIMARY_BLUE,
                    foreground=WHITE)
    style.map("Treeview", background=[('selected', PRIMARY_BLUE)])
    style.configure("Accent.TButton",
                    background=ACCENT_YELLOW,
                    foreground="#1e293b",
                    font=FONT)
    style.configure("Primary.TButton",
                    background=PRIMARY_BLUE,
                    foreground=WHITE,
                    font=FONT)
    style.map("Accent.TButton",
              background=[('active', "#facc15"), ('!active', ACCENT_YELLOW)])
    style.map("Primary.TButton",
              background=[('active', "#1d4ed8"), ('!active', PRIMARY_BLUE)])

def open_user_dashboard(root, frame, user_id, username):
    clear_frame(frame)
    root.geometry("700x500")
    style_widgets(root)
    frame.configure(bg=LIGHT_BLUE)

    tk.Label(frame, text=f"Welcome, {username}",
             font=HEADER_FONT, bg=LIGHT_BLUE, fg=PRIMARY_BLUE
             ).pack(pady=8)

    def view_products():
        clear_frame(frame)
        frame.configure(bg=LIGHT_BLUE)
        tk.Label(frame, text="Products",
                 font=HEADER_FONT, bg=LIGHT_BLUE, fg=PRIMARY_BLUE
                 ).pack(pady=(0, 6))

        # Fetch & display product table
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT product_id, name, quantity_available FROM Products")
        products = cursor.fetchall()
        db.close()

        # Product Table
        columns = ("ID", "Name", "Quantity")
        product_table = ttk.Treeview(frame, columns=columns, show="headings", height=5)
        for col in columns:
            product_table.heading(col, text=col)
            product_table.column(col, anchor='center')
        for prod in products:
            product_table.insert("", "end", values=prod)
        product_table.pack(pady=8, padx=6)

        combo = ttk.Combobox(frame, values=[f"{p[0]} - {p[1]} (Qty: {p[2]})" for p in products], font=FONT)
        combo.pack(pady=(4,2))

        tk.Label(frame, text="Quantity to Order", font=FONT, bg=LIGHT_BLUE, fg=PRIMARY_BLUE).pack()
        qty_entry = tk.Entry(frame, font=FONT)
        qty_entry.pack(pady=(0, 6))

        def place_order():
            if not combo.get() or not qty_entry.get().isdigit():
                messagebox.showerror("Error", "Invalid input")
                return
            product_id = int(combo.get().split(" - ")[0])
            qty = int(qty_entry.get())

            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT quantity_available FROM Products WHERE product_id=%s", (product_id,))
            stock = cursor.fetchone()[0]
            if stock >= qty:
                cursor.execute("INSERT INTO Orders (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                               (user_id, product_id, qty))
                cursor.execute("UPDATE Products SET quantity_available = quantity_available - %s WHERE product_id = %s",
                               (qty, product_id))
                db.commit()
                messagebox.showinfo("Success", "Order placed")
            else:
                messagebox.showerror("Error", "Insufficient stock")
            db.close()

        # Horizontal buttons
        button_frame = tk.Frame(frame, bg=LIGHT_BLUE)
        button_frame.pack(pady=8)
        ttk.Button(button_frame, text="Place Order", style="Accent.TButton",
                   command=place_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back", style="Primary.TButton",
                   command=lambda: open_user_dashboard(root, frame, user_id, username)).pack(side=tk.LEFT, padx=5)

    def view_orders():
        clear_frame(frame)
        root.geometry("800x450")
        frame.configure(bg=LIGHT_BLUE)
        tk.Label(frame, text="Your Orders", font=HEADER_FONT, bg=LIGHT_BLUE, fg=PRIMARY_BLUE).pack(pady=8)
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT o.order_id, p.name, o.quantity, o.order_date
            FROM Orders o
            JOIN Products p ON o.product_id = p.product_id
            WHERE o.user_id = %s
        """, (user_id,))
        orders = cursor.fetchall()
        db.close()

        # Orders table view
        columns = ("Order ID", "Product", "Quantity", "Date")
        order_table = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        for col in columns:
            order_table.heading(col, text=col)
            order_table.column(col, anchor='center')
        for order in orders:
            order_table.insert("", "end", values=order)
        order_table.pack(pady=8, padx=6)

        ttk.Button(frame, text="Back", style="Primary.TButton",
                   command=lambda: open_user_dashboard(root, frame, user_id, username)).pack(pady=6)

    # Horizontal dashboard buttons
    dashboard_btn_frame = tk.Frame(frame, bg=LIGHT_BLUE)
    dashboard_btn_frame.pack(pady=15)
    ttk.Button(dashboard_btn_frame, text="Place Order", style="Primary.TButton",
               command=view_products).pack(side=tk.LEFT, padx=7)
    ttk.Button(dashboard_btn_frame, text="View Orders", style="Accent.TButton",
               command=view_orders).pack(side=tk.LEFT, padx=7)
    ttk.Button(dashboard_btn_frame, text="Logout", style="Primary.TButton",
               command=lambda: __import__('login').show_login(root, frame)).pack(side=tk.LEFT, padx=7)