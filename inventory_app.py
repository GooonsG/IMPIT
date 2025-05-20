import tkinter as tk
from tkinter import messagebox, ttk
from db_config import connect_db

db = connect_db()
cursor = db.cursor()

root = tk.Tk()
root.title("Inventory Management System")
root.geometry("500x500")
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def login_page():
    clear_frame(main_frame)

    tk.Label(main_frame, text="Username").pack()
    username_entry = tk.Entry(main_frame)
    username_entry.pack()

    tk.Label(main_frame, text="Password").pack()
    password_entry = tk.Entry(main_frame, show="*")
    password_entry.pack()

    def login():
        username = username_entry.get()
        password = password_entry.get()
        cursor.execute("SELECT user_id, role FROM Users WHERE username=%s AND password_hash=%s", (username, password))
        result = cursor.fetchone()
        if result:
            user_id, role = result
            messagebox.showinfo("Success", f"Welcome, {role}")
            if role == 'admin':
                admin_dashboard(user_id, username)
            else:
                user_dashboard(user_id, username)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    tk.Button(main_frame, text="Login", command=login).pack(pady=10)
    tk.Button(main_frame, text="Register", command=register_page).pack()

def register_page():
    clear_frame(main_frame)

    tk.Label(main_frame, text="New Username").pack()
    username_entry = tk.Entry(main_frame)
    username_entry.pack()

    tk.Label(main_frame, text="New Password").pack()
    password_entry = tk.Entry(main_frame, show="*")
    password_entry.pack()

    def register():
        username = username_entry.get()
        password = password_entry.get()
        cursor.execute("SELECT * FROM Users WHERE username=%s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return
        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (%s, %s, 'user')", (username, password))
        db.commit()
        messagebox.showinfo("Success", "Registered")
        login_page()

    tk.Button(main_frame, text="Register", command=register).pack(pady=10)
    tk.Button(main_frame, text="Back to Login", command=login_page).pack()

def admin_dashboard(user_id, username):
    clear_frame(main_frame)
    tk.Label(main_frame, text=f"Admin Panel - {username}", font=('Arial', 14)).pack(pady=10)

    tk.Label(main_frame, text="Product Name").pack()
    name_entry = tk.Entry(main_frame)
    name_entry.pack()

    tk.Label(main_frame, text="Description").pack()
    desc_entry = tk.Entry(main_frame)
    desc_entry.pack()

    tk.Label(main_frame, text="Quantity").pack()
    qty_entry = tk.Entry(main_frame)
    qty_entry.pack()

    def add_product():
        cursor.execute("INSERT INTO Products (name, description, quantity_available) VALUES (%s, %s, %s)",
                       (name_entry.get(), desc_entry.get(), int(qty_entry.get())))
        db.commit()
        messagebox.showinfo("Success", "Product added")
        admin_dashboard(user_id, username)

    tk.Button(main_frame, text="Add Product", command=add_product).pack(pady=5)

    # Product list
    cursor.execute("SELECT * FROM Products")
    rows = cursor.fetchall()
    for row in rows:
        tk.Label(main_frame, text=f"{row[0]} | {row[1]} | Qty: {row[3]}").pack()

    tk.Button(main_frame, text="Logout", command=login_page).pack(pady=10)

def user_dashboard(user_id, username):
    clear_frame(main_frame)
    tk.Label(main_frame, text=f"User Panel - {username}", font=('Arial', 14)).pack(pady=10)

    def view_orders():
        clear_frame(main_frame)
        tk.Label(main_frame, text="Your Orders").pack()
        cursor.execute("""SELECT o.order_id, p.name, o.quantity, o.order_date
                          FROM Orders o JOIN Products p ON o.product_id = p.product_id
                          WHERE o.user_id = %s""", (user_id,))
        for row in cursor.fetchall():
            tk.Label(main_frame, text=f"Order #{row[0]}: {row[1]} x{row[2]} on {row[3]}").pack()
        tk.Button(main_frame, text="Back", command=lambda: user_dashboard(user_id, username)).pack()

    def view_products_and_order():
        clear_frame(main_frame)
        tk.Label(main_frame, text="Products").pack()

        cursor.execute("SELECT product_id, name, quantity_available FROM Products")
        products = cursor.fetchall()
        product_combo = ttk.Combobox(main_frame, values=[
            f"{p[0]} - {p[1]} (Available: {p[2]})" for p in products])
        product_combo.pack()

        tk.Label(main_frame, text="Quantity to Order").pack()
        qty_entry = tk.Entry(main_frame)
        qty_entry.pack()

        def place_order():
            selection = product_combo.get()
            if not selection or not qty_entry.get().isdigit():
                messagebox.showerror("Error", "Invalid input")
                return
            product_id = int(selection.split(" - ")[0])
            quantity = int(qty_entry.get())
            cursor.execute("SELECT quantity_available FROM Products WHERE product_id=%s", (product_id,))
            result = cursor.fetchone()
            if result and result[0] >= quantity:
                cursor.execute("INSERT INTO Orders (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                               (user_id, product_id, quantity))
                cursor.execute("UPDATE Products SET quantity_available = quantity_available - %s WHERE product_id = %s",
                               (quantity, product_id))
                db.commit()
                messagebox.showinfo("Success", "Order placed!")
                user_dashboard(user_id, username)
            else:
                messagebox.showerror("Error", "Not enough stock")

        tk.Button(main_frame, text="Place Order", command=place_order).pack()
        tk.Button(main_frame, text="Back", command=lambda: user_dashboard(user_id, username)).pack()

    tk.Button(main_frame, text="View My Orders", command=view_orders).pack(pady=5)
    tk.Button(main_frame, text="Place New Order", command=view_products_and_order).pack(pady=5)
    tk.Button(main_frame, text="Logout", command=login_page).pack(pady=10)

# Start app
login_page()
root.mainloop()
