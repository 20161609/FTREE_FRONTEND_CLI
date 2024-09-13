import os
from io import BytesIO
import tkinter as tk
import io
import base64
import textwrap
from tkinter import ttk, messagebox, filedialog
from transaction.transaction import get_receipt_image
from lib_box.santizer import *
from transaction.transaction import get_transaction_daily
from transaction.transaction import modify_transaction
from firebase.tree import get_firebase_path
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps

valid_date_formats = [
    '19960513', '960513', '1996/05/13', '1996-05-13',
    '96/05/13', '96-05-13', '96/5/13', '96-5-13'
]

class ModifyWindow(tk.Tk):
    def __init__(self, id_token, tree, branch, branch_options=['Home']):
        super().__init__()
        self.tree = tree
        self.id_token = id_token
        self.branch = branch
        self.transactions = []
        self.branch_options = branch_options
        self.image = None
        self.current_index = 0

        self.get_transaction()

        self.title("Transaction Image Browser")
        self.geometry("1000x700")
        self.minsize(800, 600)
        self.center_window()

        # Apply modern theme
        style = ttk.Style(self)
        style.theme_use('clam')

        # Configure styles
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 12))
        style.configure('TButton', font=('Helvetica', 12), padding=6)
        style.configure('TCombobox', font=('Helvetica', 12))
        style.configure('TFrame', background='#f0f0f0')

        # UI components creation
        self.create_widgets()
        self.bind_events()
        self.show_image()
        self.mainloop()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def get_transaction(self):
        res = get_transaction_daily(self.id_token, self.branch)
        if res.status_code != 200:
            print("...[ERROR] Failed to fetch transaction data.")
            self.destroy()
            return

        history = res.json()['message']
        if len(history) == 0:
            print("...[INFO] No transaction data available.")
            self.destroy()
            return

        for record in history:
            try:
                if record['receipt']:
                    res = get_receipt_image(self.id_token, record['receipt'])
                    image_base64 = res['message']
                    image_bytes = base64.b64decode(image_base64)
                    image_stream = io.BytesIO(image_bytes)
                    image = Image.open(image_stream)
                else:
                    image = None
            except:
                image = None

            self.transactions.append({
                'tid': record['tid'],
                'Date': record['t_date'],
                'branch': record['branch'],
                'cashflow': record['cashflow'],
                'description': record['description'],
                'receipt': record['receipt'],
                'receipt_image': image
            })

    def create_widgets(self):
        # Create main frame
        self.main_frame = ttk.Frame(self, style='TFrame')
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.image_frame = ttk.Frame(self.main_frame)
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.info_frame = ttk.Frame(self.main_frame)
        self.info_frame.grid(row=0, column=1, sticky="nsew")

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=0)
        self.main_frame.rowconfigure(0, weight=1)

        # Set fixed size for image display area
        self.image_display_width = 600
        self.image_display_height = 600

        # Image display label with border
        image_border_frame = ttk.Frame(self.image_frame, borderwidth=2, relief="sunken")
        image_border_frame.pack(fill="both", expand=False)
        image_border_frame.config(width=self.image_display_width, height=self.image_display_height)
        image_border_frame.pack_propagate(False)

        self.image_label = ttk.Label(image_border_frame)
        self.image_label.pack(fill="both", expand=True)

        # Bind click event to image_label
        self.image_label.bind("<Button-1>", self.upload_image)

        # Information frame widgets
        self.info_frame.columnconfigure(1, weight=1)

        self.date_label = ttk.Label(self.info_frame, text="Date:")
        self.date_label.grid(row=0, column=0, sticky="e", pady=10, padx=5)
        self.date_entry = ttk.Entry(self.info_frame, width=30)
        self.date_entry.grid(row=0, column=1, sticky="w", pady=10, padx=5)

        self.branch_label = ttk.Label(self.info_frame, text="Branch:")
        self.branch_label.grid(row=1, column=0, sticky="e", pady=10, padx=5)
        self.branch_var = tk.StringVar()
        
        # Wrap branch options
        def wrap_text(text, width=45):
            return "\n".join(textwrap.wrap(text, width))
        wrap_branch_options = [wrap_text(option) for option in self.branch_options]  
        
        self.branch_dropdown = ttk.Combobox(
            self.info_frame,
            textvariable=self.branch_var,
            values=wrap_branch_options,
            state='readonly',
            width=50
        )
        self.branch_dropdown.grid(row=1, column=1, sticky="w", pady=10, padx=5)

        self.transaction_label = ttk.Label(self.info_frame, text="Cash Flow:")
        self.transaction_label.grid(row=2, column=0, sticky="e", pady=10, padx=5)
        self.transaction_entry = ttk.Entry(self.info_frame, width=30)
        self.transaction_entry.grid(row=2, column=1, sticky="w", pady=10, padx=5)

        self.description_label = ttk.Label(self.info_frame, text="Description:")
        self.description_label.grid(row=3, column=0, sticky="ne", pady=10, padx=5)
        self.description_entry = ttk.Entry(self.info_frame, width=30)
        self.description_entry.grid(row=3, column=1, sticky="w", pady=10, padx=5)

        # Button frame
        self.button_frame = ttk.Frame(self.info_frame)
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=30)

        self.prev_button = ttk.Button(self.button_frame, text="<< Previous", command=self.prev_image)
        self.prev_button.pack(side="left", padx=10)

        self.save_button = ttk.Button(self.button_frame, text="Save", command=self.save_data)
        self.save_button.pack(side="left", padx=10)

        self.refresh_button = ttk.Button(self.button_frame, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(side="left", padx=10)

        self.next_button = ttk.Button(self.button_frame, text="Next >>", command=self.next_image)
        self.next_button.pack(side="left", padx=10)

        # Progress label
        self.progress_label = ttk.Label(self.info_frame, text="")
        self.progress_label.grid(row=5, column=0, columnspan=2, pady=10)

    def bind_events(self):
        self.bind("<Control-Right>", self.next_image)
        self.bind("<Control-Left>", self.prev_image)
        self.bind("<Escape>", self.on_escape)

    def on_escape(self, event):
        self.destroy()

    def show_image(self):
        transaction = self.transactions[self.current_index]
        self.image = transaction['receipt_image']

        self.display_image(self.image)

        date = transaction['Date']
        branch = transaction['branch']
        cashflow = transaction['cashflow']
        description = transaction['description']
        self.load_info(date, branch, cashflow, description)

        # Update progress
        total = len(self.transactions)
        current = self.current_index + 1
        self.progress_label.config(text=f"Transaction {current} / {total}")

    def display_image(self, image):
        if image:
            # Resize and display the image within the fixed display area
            image_width, image_height = image.size
            max_width, max_height = self.image_display_width, self.image_display_height
            ratio = min(max_width / image_width, max_height / image_height, 1)
            new_size = (int(image_width * ratio), int(image_height * ratio))
            resized_image = image.resize(new_size, Image.LANCZOS)
        else:
            # Create a placeholder image with 'No Image' text
            resized_image = Image.new('RGB', (self.image_display_width, self.image_display_height), color=(220, 220, 220))
            draw = ImageDraw.Draw(resized_image)
            text = "No Image"
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except IOError:
                font = ImageFont.load_default()
            textwidth, textheight = draw.textsize(text, font=font)
            x = (resized_image.width - textwidth) / 2
            y = (resized_image.height - textheight) / 2
            draw.text((x, y), text, fill=(0, 0, 0), font=font)

        photo = ImageTk.PhotoImage(resized_image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

    def load_info(self, date, branch, cashflow, description):
        # Load transaction info into widgets
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date)
        branch = '/'.join([b[8:] for b in branch.split('/')])
        self.branch_var.set(branch)

        self.transaction_entry.delete(0, tk.END)
        self.transaction_entry.insert(0, cashflow)

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, description)

    def next_image(self, event=None):
        self.current_index = (self.current_index + 1) % len(self.transactions)
        self.show_image()

    def prev_image(self, event=None):
        self.current_index = (self.current_index - 1) % len(self.transactions)
        self.show_image()

    def save_data(self):
        # Get data from widgets
        date = self.date_entry.get()
        branch = self.branch_var.get()
        cashflow = self.transaction_entry.get()
        description = self.description_entry.get()

        # Convert image
        if self.image:
            rgb_image = self.image.convert('RGB')
            buffer = BytesIO()
            rgb_image.save(buffer, format='JPEG')
            buffer.seek(0)
            files = {'receipt': ('receipt.jpg', buffer, 'image/jpeg')}
        else:
            files = None

        # Send to server
        try:
            res = modify_transaction(
                id_token=self.id_token,
                tid=self.transactions[self.current_index]['tid'],
                t_date=date,
                branch=get_firebase_path(self.tree, branch),
                cashflow=cashflow,
                description=description,
                receipt=files
            )

            if res.status_code == 200:
                print("...[SUCCESS]", "Modification successfully.")
                messagebox.showinfo("Success", "Transaction saved successfully.")
                self.on_escape()
            else:
                print("...[ERROR]", res.json()['message'])
                messagebox.showerror("Error", "Failed to save transaction.")
        except Exception as e:
            print("...[ERROR]", e)
            messagebox.showerror("Error", "Failed to save transaction.")

        else:
            messagebox.showerror("Error", "Failed to save transaction.")

    def upload_image(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=(("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.png"), ("All files", "*.*"))
        )
        if file_path:
            self.image = Image.open(file_path)
            self.display_image(self.image)

    def refresh_data(self):
        # Reload the original data for the current transaction
        transaction = self.transactions[self.current_index]
        self.image = transaction['receipt_image']
        self.show_image()
