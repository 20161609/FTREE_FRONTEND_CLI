import tkinter as tk
from transaction.transaction import *
from lib_box.santizer import *
from tkinter import filedialog, messagebox
from tkinter import ttk
from firebase.tree import get_absolute_path, get_firebase_path
from PIL import Image, ImageTk


class TransactionUploader:
    def __init__(self, id_token ,branch_path='Home', branch_options = ['Home'], tree=None):
        # Identity User
        self.id_token = id_token

        # Create the root window
        self.root = tk.Tk()

        # Branch info
        self.tree = tree
        self.branch_path = branch_path
        self.branch_options = branch_options
        self.file_path = None

        # Input Session
        self.date_entry = None
        self.in_entry, self.out_entry = None, None
        self.branch_dropdown = None
        self.description_entry = None

        # Image data and viewer
        self.img = None
        self.large_image_window = None
        self.panel = None
        try:
            self.make_window()
        except Exception as e:
            messagebox.showinfo("Fail", str(e))
            self.root.destroy()

    def make_window(self):  # Window's main structure
        self.root.title("Photo Upload and Data Entry Example")
        self.root.grid_anchor("center")

        # Setting the window size and centering it on the screen
        window_width, window_height = 600, 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = 0
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        # ttk style
        style = ttk.Style(self.root)
        style.configure('TLabel', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12))

        # Basic Image Setting
        self.img = Image.new("RGB", (200, 200), (192, 192, 192))

        # Image Upload Section
        self.panel = ttk.Label(self.root, anchor="center")
        self.panel.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        upload_button = ttk.Button(self.root, text="Upload Photo", command=self.upload_photo)
        upload_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Constitute Data Input Fields
        ttk.Label(self.root, text="Date:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.date_entry = ttk.Entry(self.root, width=48)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        # Input - branch Name
        ttk.Label(self.root, text="Branch:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        branch_var = tk.StringVar()
        branch_var.set(self.branch_path)
        self.branch_dropdown = ttk.Combobox(
            self.root,
            textvariable=branch_var,
            width=45,
            values=self.branch_options,
            state="readonly")
        self.branch_dropdown.grid(row=3, column=1, padx=5, pady=5)

        # Input - CashFlow (Income)
        ttk.Label(self.root, text="In:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.in_entry = ttk.Entry(self.root, width=48)
        self.in_entry.grid(row=4, column=1, padx=5, pady=5)

        # Input - CashFlow (Expense)
        ttk.Label(self.root, text="Out:").grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.out_entry = ttk.Entry(self.root, width=48)
        self.out_entry.grid(row=5, column=1, padx=5, pady=5)

        # Input - Description
        ttk.Label(self.root, text="Description:").grid(row=6, column=0, sticky='e', padx=5, pady=5)
        self.description_entry = tk.Entry(self.root, width=48)
        self.description_entry.grid(row=6, column=1, padx=5, pady=5)

        # Save Image and Data
        save_button = ttk.Button(self.root, text="SAVE", command=self.save_data)
        save_button.grid(row=7, column=0, columnspan=2, pady=10)
        panel_image = ImageTk.PhotoImage(self.img)
        self.panel.config(image=panel_image)
        self.panel.image = panel_image
        self.root.mainloop()

    def upload_photo(self):  # Upload Image
        self.file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if self.file_path:
            # load Image from local
            self.img = Image.open(self.file_path)
            self.img.show()

            # Create panel image
            self.img.thumbnail((250, 250))
            panel_image = ImageTk.PhotoImage(self.img)
            self.panel.config(image=panel_image)
            self.panel.image = panel_image

    def save_data(self):  # Save Data and Image
        # Validate the input
        # validation - Date
        _date = format_date(self.date_entry.get().strip())

        # validation - Branch
        _branch = get_firebase_path(self.tree, self.branch_dropdown.get().strip())

        # validation - CashFlow
        try:
            _in = self.in_entry.get().strip() or '0'
            _out = self.out_entry.get().strip() or '0'
            _cashflow = int(_in) - int(_out)
        except:
            messagebox.showinfo("Fail", "Invalid input for cash flow. Please enter numeric values.")
            return

        # validation - Description
        _description = self.description_entry.get().strip()

        try:
            input_valid = make_image_file_name(_date, _branch, _cashflow, _description)
            if not input_valid['status']:
                messagebox.showinfo("Fail", input_valid['tag'])
                print(f"...[ERROR] {input_valid['tag']}")
                return
            upload_transaction(
                id_token=self.id_token, 
                t_date=_date, branch=_branch, cashflow=_cashflow, description=_description, 
                file_path=self.file_path
            )
            print('...[INFO] Transaction data uploaded successfully')
        except Exception as e:
            messagebox.showinfo("Fail", str(e))
            print('...[ERROR] Transaction data upload failed')
            print(str(e))

        # Close the window
        self.root.destroy()
        return
