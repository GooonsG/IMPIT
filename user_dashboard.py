import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_db_connection
from utils import clear_frame

PRIMARY_BLUE = "#1F1B4F"
LIGHT_BLUE = "#20141c"
ACCENT_YELLOW = "#F9BF3B"
WHITE = "#ffffff"
FF = "#f4eee2"
FONT = ("Segoe UI", 12)
BOLD_FONT = ("Segoe UI", 12, "bold")
HEADER_FONT = ("Segoe UI", 16, "bold")

def style_widgets(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview",
                    background=FF,
                    foreground="#222",
                    rowheight=28,
                    fieldbackground=FF,
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
             font=HEADER_FONT, bg=LIGHT_BLUE, fg=ACCENT_YELLOW
             ).pack(pady=8)

    def view_products():
        clear_frame(frame)
        frame.configure(bg=LIGHT_BLUE)
        tk.Label(frame, text="Products",
                 font=HEADER_FONT, bg=LIGHT_BLUE, fg=ACCENT_YELLOW
                 ).pack(pady=(0, 6))

        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT product_id, name, description, quantity_available FROM Products")
            products = cursor.fetchall()
            db.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not fetch products.\n{e}")
            return

        # Treeview table
        tree_frame = tk.Frame(frame, bg=ACCENT_YELLOW, bd=2, relief="solid")
        tree_frame.pack(padx=5, pady=5)

        columns = ("Product ID", "Name", "Description", "Quantity")
        product_table = ttk.Treeview(tree_frame, columns=columns, show="headings", height=5)

        product_table.column("Product ID", width=90)
        product_table.column("Name", width=150)
        product_table.column("Quantity", width=80)
        product_table.column("Description", width=280)

        for col in columns:
            product_table.heading(col, text=col)
            product_table.column(col, anchor='center')
        for prod in products:
            product_table.insert("", "end", values=prod)
        product_table.pack(pady=8, padx=6)

        combo_values = [f"{p[0]} - {p[1]}" for p in products]  # product_id - name
        combo = ttk.Combobox(frame, values=combo_values, font=FONT, width=40)
        combo.pack(pady=(4, 2))

        tk.Label(frame, text="Quantity to Order", font=BOLD_FONT, bg=LIGHT_BLUE, fg=ACCENT_YELLOW).pack()
        qty_entry = tk.Entry(frame, font=FONT)
        qty_entry.pack(pady=(0, 6))

        def on_select(event):
            selected = product_table.focus()
            if not selected:
                return
            values = product_table.item(selected, "values")
            combo.set(f"{values[0]} - {values[1]}")
            qty_entry.focus()

        product_table.bind("<<TreeviewSelect>>", on_select)

        def place_order():
            if not combo.get() or not qty_entry.get().isdigit():
                messagebox.showerror("Error", "Invalid input")
                return
            try:
                product_id = int(combo.get().split(" - ")[0])
                qty = int(qty_entry.get())

                db = get_db_connection()
                cursor = db.cursor()
                cursor.execute("SELECT quantity_available FROM Products WHERE product_id=%s", (product_id,))
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror("Error", "Product not found.")
                    return

                stock = result[0]
                if stock >= qty:
                    cursor.execute("INSERT INTO Orders (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                                   (user_id, product_id, qty))
                    cursor.execute("UPDATE Products SET quantity_available = quantity_available - %s WHERE product_id = %s",
                                   (qty, product_id))
                    db.commit()
                    messagebox.showinfo("Success", "Order placed successfully.")
                    view_products()
                else:
                    messagebox.showerror("Error", "Insufficient stock")
                db.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Order failed.\n{e}")

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
        tk.Label(frame, text="Your Orders", font=HEADER_FONT, bg=LIGHT_BLUE, fg=ACCENT_YELLOW).pack(pady=8)

        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("""
                SELECT o.order_id, p.name, p.description, o.quantity, o.order_date
                FROM Orders o
                JOIN Products p ON o.product_id = p.product_id
                WHERE o.user_id = %s
            """, (user_id,))
            orders = cursor.fetchall()
            db.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not fetch orders.\n{e}")
            return

        tree_frame = tk.Frame(frame, bg=ACCENT_YELLOW, bd=2, relief="solid")
        tree_frame.pack(padx=5, pady=5)

        columns = ("Order ID", "Product", "Description", "Quantity", "Date")
        order_table = ttk.Treeview(tree_frame, columns=columns, show="headings", height=6)
        order_table.column("Order ID", width=70)
        order_table.column("Product", width=150)
        order_table.column("Quantity", width=70)
        for col in columns:
            order_table.heading(col, text=col)
            order_table.column(col, anchor='center')
        for order in orders:
            order_table.insert("", "end", values=order)
        order_table.pack(pady=8, padx=6)

        def remove_order():
            selected = order_table.focus()
            if not selected:
                messagebox.showwarning("Select Order", "Please select an order to remove.")
                return
            order_id = order_table.item(selected, "values")[0]
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to remove this order?")
            if confirm:
                try:
                    db = get_db_connection()
                    cursor = db.cursor()
                    cursor.execute("SELECT product_id, quantity FROM Orders WHERE order_id=%s", (order_id,))
                    result = cursor.fetchone()
                    if result:
                        product_id, qty = result
                        cursor.execute("DELETE FROM Orders WHERE order_id=%s", (order_id,))
                        cursor.execute("UPDATE Products SET quantity_available = quantity_available + %s WHERE product_id = %s",
                                       (qty, product_id))
                        db.commit()
                    db.close()
                    messagebox.showinfo("Removed", "Order has been removed.")
                    view_orders()
                except Exception as e:
                    messagebox.showerror("Database Error", f"Could not remove order.\n{e}")

        button_frame = tk.Frame(frame, bg=LIGHT_BLUE)
        button_frame.pack(pady=8)
        ttk.Button(button_frame, text="Remove Selected Order", style="Accent.TButton",
                   command=remove_order).pack(side=tk.LEFT, padx=4)
        ttk.Button(button_frame, text="Back", style="Primary.TButton",
                   command=lambda: open_user_dashboard(root, frame, user_id, username)).pack(side=tk.LEFT, padx=4)

    dashboard_btn_frame = tk.Frame(frame, bg=LIGHT_BLUE)
    dashboard_btn_frame.pack(pady=15)
    ttk.Button(dashboard_btn_frame, text="Place Order", style="Primary.TButton",
               command=view_products).pack(side=tk.LEFT, padx=7)
    ttk.Button(dashboard_btn_frame, text="View Orders", style="Accent.TButton",
               command=view_orders).pack(side=tk.LEFT, padx=7)
    ttk.Button(dashboard_btn_frame, text="Logout", style="Primary.TButton",
               command=lambda: __import__('login').show_login(root, frame)).pack(side=tk.LEFT, padx=7)
