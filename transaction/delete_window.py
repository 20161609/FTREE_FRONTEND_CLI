from tkinter import messagebox
from transaction.transaction import get_transaction_daily, delete_transaction
import tkinter as tk
from tkinter import ttk
import lib_box.santizer as Df

class DeleteTransactionWindow:
    def __init__(self, query):
        self.branch = query['branch']
        self.id_token = query['id_token']
        self.begin_date = query['begin_date']
        self.end_date = query['end_date']
        self.field_names = ['T-id', 'When', 'Branch', 'Cash Flow','Description', 'Created']
        self.rows = []

        self.root = tk.Tk()  # Main window

        try:
            self.make_window()
        except Exception as e:
            messagebox.showinfo("Fail", str(e))
            self.root.destroy()

    def make_window(self):
        # Set window title and maximize
        self.root.title("Transaction Table")
        self.root.state('zoomed')

        # Define style
        style = ttk.Style()
        style.theme_use('clam')

        # Modernize Table Headers and Treeview
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#3B5998", foreground="white")
        style.configure("Treeview", font=("Arial", 10), rowheight=30)
        style.configure("TButton", font=("Arial", 12), padding=10)

        # Main frame
        main_frame = ttk.Frame(self.root, padding=(20, 20, 20, 20))
        main_frame.pack(fill="both", expand=True)

        # Title label
        title_branch_name = '/'.join([b[8:] for b in self.branch.split('/')])
        title_label = ttk.Label(main_frame, text=title_branch_name, font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 20))

        # Treeview frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)

        # Treeview setup
        columns = self.field_names[1:]  # Exclude 'T-id'
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Bind the Delete key to the Treeview
        self.tree.bind('<Delete>', lambda e: self.delete_selected())        

        # Column headers
        for col in columns:
            self.tree.heading(col, text=col)

        # Scrollbar setup
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Alternating row colors
        self.tree.tag_configure('oddrow', background='#F9F9F9')
        self.tree.tag_configure('evenrow', background='#E9E9E9')

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        delete_button = ttk.Button(button_frame, text="Delete Selected Transaction", command=self.delete_selected, style="TButton")
        delete_button.pack(pady=10)

        # Update table
        self.update_table()

        # Bind Ctrl + 'C' and Escape to close the window
        self.root.bind("<Control-c>", lambda e: self.root.destroy())
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.root.mainloop()

    def get_transactions(self):
        res = get_transaction_daily(
            id_token=self.id_token, 
            branch=self.branch, 
            begin_date=self.begin_date, end_date=self.end_date)
        
        if res.status_code == 200:
            if not res.json()['status']:
                print("...[ERROR]", res.json()['message'])
                return None

            # Retrieve transactions from response
            history = res.json()['message']
            if len(history) == 0:
                print("...[INFO] No Transaction data")
                return None

            self.rows.clear()

            for record in history:
                tid = record['tid']
                when = record['t_date']
                branch = '/'.join([b[8:] for b in record['branch'].split('/')])
                cashflow = record['cashflow']
                description = record['description']
                c_date = record['c_date']
                
                row = [tid, when, branch, 
                       Df.format_cost(cashflow), 
                       description, c_date]
                self.rows.append(row)
        else:
            print("...[ERROR] Upload failed")
            return None

    def update_table(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch transactions
        self.get_transactions()

        for idx, row in enumerate(self.rows):
            tags = (row[0], 'evenrow' if idx % 2 == 0 else 'oddrow')
            self.tree.insert("", "end", values=row[1:], tags=tags)

    def delete_selected(self):
        selected_item = self.tree.selection()
        if selected_item:
            tid = self.tree.item(selected_item, 'tags')[0]

            # Confirm deletion
            confirm = messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected transaction?")
            
            if confirm:
                try:
                    # Implement deletion logic here
                    a = delete_transaction(id_token=self.id_token, tid=int(tid))
                    self.tree.delete(selected_item)
                    print(a)
                    messagebox.showinfo("Success", "Transaction deleted successfully.")                    
                except Exception as e:
                    messagebox.showinfo("Fail", str(e))
        else:
            messagebox.showwarning("No Selection", "Please select a transaction to delete.")
