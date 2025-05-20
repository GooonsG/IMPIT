import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_db_connection

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("600x400")
        self.db = get_db_connection()
        self.cursor = self.db.cursor(dictionary=True)
        self.current_user = None
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        self.login_page()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def login_page(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Login", font=("Arial", 18)).pack(pady=10)

        tk.Label(self.main_frame, text="Username").pack()
        self.login_username = tk.Entry(self.main_frame)
        self.login_username.pack()

        tk.Label(self.main_frame, text="Password").pack()
        self.login_password = tk.Entry(self.main_frame, show="*")
        self.login_password.pack()

        tk.Button(self.main_frame, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.main_frame, text="Register", command=self.register_page).pack()

    def register_page(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Register", font=("Arial", 18)).pack(pady=10)

        tk.Label(self.main_frame, text="Username").pack()
        self.reg_username = tk.Entry(self.main_frame)
        self.reg_username.pack()

        tk.Label(self.main_frame, text="Password").pack()
        self.reg_password = tk.Entry(self.main_frame, show="*")
        self.reg_password.pack()

        tk.Button(self.main_frame, text="Register", command=self.register).pack(pady=10)
        tk.Button(self.main_frame, text="Back to Login", command=self.login_page).pack()

    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()
        query = "SELECT * FROM Users WHERE username=%s AND password_hash=%s"
        self.cursor.execute(query, (username, password))
        user = self.cursor.fetchone()
        if user:
            self.current_user = user
            messagebox.showinfo("Success", f"Welcome {username}!")
            self.dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        self.cursor.execute("SELECT * FROM Users WHERE username=%s", (username,))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return
        self.cursor.execute("INSERT INTO Users (username, password_hash) VALUES (%s, %s)", (username, password))
        self.db.commit()
        messagebox.showinfo("Success", "User registered!")
        self.login_page()

    def dashboard(self):
        self.clear_frame()
        tk.Label(self.main_frame, text=f"Dashboard - Logged in as {self.current_user['username']}", font=("Arial", 14)).pack(pady=10)

        tk.Button(self.main_frame, text="Manage Products", width=20, command=self.manage_products).pack(pady=5)
        tk.Button(self.main_frame, text="Logout", width=20, command=self.logout).pack(pady=5)

    def logout(self):
        self.current_user = None
        self.login_page()

    def manage_products(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Product Management", font=("Arial", 16)).pack(pady=10)

        # Product list
        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Name", "Description", "Quantity"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=30)
        self.tree.heading("Name", text="Name")
        self.tree.column("Name", width=150)
        self.tree.heading("Description", text="Description")
        self.tree.column("Description", width=200)
        self.tree.heading("Quantity", text="Quantity")
        self.tree.column("Quantity", width=80)
        self.tree.pack(pady=10)

        self.load_products()

        # Entry fields for add/update
        form_frame = tk.Frame(self.main_frame)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Name").grid(row=0, column=0)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Description").grid(row=1, column=0)
        self.desc_entry = tk.Entry(form_frame)
        self.desc_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="Quantity").grid(row=2, column=0)
        self.qty_entry = tk.Entry(form_frame)
        self.qty_entry.grid(row=2, column=1)

        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Product", command=self.add_product).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update Selected", command=self.update_product).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_product).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Back", command=self.dashboard).grid(row=0, column=3, padx=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.cursor.execute("SELECT * FROM Products")
        for product in self.cursor.fetchall():
            self.tree.insert("", "end", values=(product['product_id'], product['name'], product['description'], product['quantity_available']))

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, 'values')
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])
            self.desc_entry.delete(0, tk.END)
            self.desc_entry.insert(0, values[2])
            self.qty_entry.delete(0, tk.END)
            self.qty_entry.insert(0, values[3])

    def add_product(self):
        name = self.name_entry.get()
        desc = self.desc_entry.get()
        qty = self.qty_entry.get()
        if not name or not qty.isdigit():
            messagebox.showerror("Error", "Name and valid quantity required")
            return
        self.cursor.execute("INSERT INTO Products (name, description, quantity_available) VALUES (%s, %s, %s)", (name, desc, int(qty)))
        self.db.commit()
        messagebox.showinfo("Success", "Product added")
        self.load_products()
        self.clear_entries()

    def update_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a product to update")
            return
        product_id = self.tree.item(selected, 'values')[0]
        name = self.name_entry.get()
        desc = self.desc_entry.get()
        qty = self.qty_entry.get()
        if not name or not qty.isdigit():
            messagebox.showerror("Error", "Name and valid quantity required")
            return
        self.cursor.execute(
            "UPDATE Products SET name=%s, description=%s, quantity_available=%s WHERE product_id=%s",
            (name, desc, int(qty), product_id)
        )
        self.db.commit()
        messagebox.showinfo("Success", "Product updated")
        self.load_products()
        self.clear_entries()

    def delete_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a product to delete")
            return
        product_id = self.tree.item(selected, 'values')[0]
        self.cursor.execute("DELETE FROM Products WHERE product_id=%s", (product_id,))
        self.db.commit()
        messagebox.showinfo("Success", "Product deleted")
        self.load_products()
        self.clear_entries()

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
