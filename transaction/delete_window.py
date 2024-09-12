# import sqlite3
# from PIL import Image, ImageTk, ImageDraw, ImageFont
# from collections import deque
# import json
# from tkinterdnd2 import TkinterDnD, DND_FILES
# from tkinter import filedialog, messagebox, ttk, NW
# import lib_sanitizer as Df
# import lib_branch as Br
# import os
# import tkinter as tk
# from tkinter import messagebox
# import lib_sanitizer as Df

# class DeleteWindow:
#     def __init__(self, sync_function, branch_path='Home'):
#         self.branch_path = branch_path  # 브랜치 경로
#         self.sync = sync_function  # 동기화 함수
#         self.root = tk.Tk()  # 메인 윈도우

#         try:
#             self.main_frame = tk.Frame(self.root)  # 메인 프레임
#             self.canvas = tk.Canvas(self.main_frame)  # 캔버스
#             self.table_frame = tk.Frame(self.canvas)  # 테이블 프레임
#             self.make_window()
#         except Exception as e:
#             messagebox.showinfo("Fail", str(e))
#             self.root.destroy()

#     def make_window(self):
#         # 최상단 타이틀 설정
#         self.root.title("Transaction Table")
#         title_label = tk.Label(self.root, text=self.branch_path, font=("Arial", 17, "bold"))
#         title_label.pack(pady=10)

#         # 메인 프레임 설정
#         self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

#         # 캔버스 및 스크롤바 설정
#         self.canvas.pack(side="left", fill="both", expand=True)
#         scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
#         scrollbar.pack(side="right", fill="y")
#         self.canvas.configure(yscrollcommand=scrollbar.set)
#         self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

#         # 마우스 휠 이벤트 바인딩
#         self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

#         # 테이블 프레임을 캔버스에 추가
#         self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

#         # 테이블 업데이트
#         self.update_table()

#         # 창 크기 설정 및 루프 실행
#         screen_width = self.root.winfo_screenwidth()
#         screen_height = self.root.winfo_screenheight()
#         self.root.geometry(f"{screen_width}x{screen_height}")
#         self.root.mainloop()

#     def delete_row(self, file_name):
#         _date, _branch, _cashflow, _description = file_name.split('.')[0].split('_')
#         _branch = _branch.replace('-', '/')
#         _cashflow = Df.format_cost(int(_cashflow))
#         info_txt = f'{_date} {_branch} {_cashflow} {_description}'
#         floating_message = f"Are you sure you want to delete this row?\n\n{info_txt}"
#         if messagebox.askyesno("Delete", floating_message):
#             try:
#                 os.remove(f'transactions/{file_name}')
#                 self.sync()
#                 self.update_table()
#             except:
#                 pass

#     def get_transactions(self):
#         rows, file_names = [], []
#         balance = 0
#         total_in, total_out = 0, 0
#         index = -1
#         for file_name in os.listdir('transactions'):
#             try:
#                 _date, _branch, _cashflow, _description = file_name.split('.')[0].split('_')
#                 _branch = _branch.replace('-', '/')

#                 if Br.is_sub_path(main_path=self.branch_path, sub_path=_branch):
#                     _in = max(int(_cashflow), 0)
#                     _out = -min(int(_cashflow), 0)
#                     total_out += _out
#                     total_in += _in
#                     balance += int(_cashflow)
#                     index += 1
#                     row = [index,
#                            _date,_branch,
#                            Df.format_cost(_in), Df.format_cost(_out), Df.format_cost(balance),
#                            _description
#                            ]
#                     rows.append(row)
#                     file_names.append(file_name)
#             except:
#                 pass

#         rows.append(['', '', '',
#                      Df.format_cost(total_in),
#                      Df.format_cost(total_out),
#                      Df.format_cost(balance),
#                      ''])

#         return rows, file_names

#     def update_table(self):
#         for widget in self.table_frame.winfo_children():
#             widget.destroy()

#         headers = ["Date", "Branch", "In", "Out", "Balance", "Description"]# , "Delete"]
#         for col, header in enumerate(headers):
#             tk.Label(self.table_frame, text=header, bg="#89abcd", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5).grid(row=0, column=col, sticky="nsew")

#         rows, file_names = self.get_transactions()
#         for i, row in enumerate(rows):
#             for j, val in enumerate(row[1:]):
#                 font = ("Arial", 9, "normal")
#                 tk.Label(self.table_frame, text=val, bg="#dfdfdf", padx=10, pady=5, font=font).grid(row=i + 1, column=j, sticky="nsew")

#             if i < len(rows) - 1:
#                 delete_button = tk.Button(
#                     self.table_frame,
#                     text="Delete",
#                     command=lambda file=file_names[row[0]]: self.delete_row(file),
#                     bg="red", fg="white")

#                 delete_button.grid(row=i + 1, column=len(row) - 1, padx=5, pady=5)

#     # 스크롤 이벤트 처리 함수
#     def on_mouse_wheel(self, event):
#         self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


# def get_paths():
#     with open('BudgetTree2.json', encoding='utf-8') as f:
#         root = json.load(f)
#     path_box = []

#     def dfs(node, path_list):
#         path_txt = '/'.join(path_list)
#         if len(path_txt) > 0:
#             path_box.append(path_txt)
#         for child_name in node:
#             path_list.append(child_name)
#             dfs(node[child_name], path_list)
#             path_list.pop()

#     dfs(root, deque([]))
#     return path_box

# def delete_transaction(sync, branch):
#     TransactionController(sync, branch)