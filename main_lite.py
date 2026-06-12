import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from openpyxl import Workbook

def determine_json_structure(data):
	if isinstance(data, list):
		return 'list'
	elif isinstance(data, dict):
		return 'dict'
	else:
		return 'unknown'

def load_json(file_path):
	try:
		with open(file_path, 'r') as f:
			data = json.load(f)
	except json.JSONDecodeError:
		data = None
	return data

def get_table_data(data, json_type, data_key=None):
	if json_type == 'list':
		if len(data) > 1 and isinstance(data[0], list):
			headers = data[0]
			rows = data[1:]
		elif len(data) > 0 and isinstance(data[0], dict):
			headers = list(data[0].keys())
			rows = [list(item.values()) for item in data]
		else:
			headers = []
			rows = []
	elif json_type == 'dict' and data_key:
		subdata = data.get(data_key, [])
		if isinstance(subdata, list) and len(subdata) > 0 and isinstance(subdata[0], dict):
			headers = list(subdata[0].keys())
			rows = [list(item.values()) for item in subdata]
		else:
			headers = []
			rows = []
	else:
		headers = []
		rows = []
	return headers, rows

def save_to_excel(file_name, headers, rows):
	wb = Workbook()
	ws = wb.active
	ws.append(headers)
	for row in rows:
		ws.append(row)
	wb.save(f'{file_name}.xlsx')

def save_to_csv(file_name, headers, rows):
	with open(f'{file_name}.csv', 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f)
		writer.writerow(headers)
		writer.writerows(rows)

def copy_to_clipboard(root, headers, rows):
	output = ''
	if headers:
		output += ','.join(map(str, headers)) + '\n'
	for row in rows:
		output += ','.join(map(str, row)) + '\n'
	root.clipboard_clear()
	root.clipboard_append(output)
	messagebox.showinfo("Copied", "Data copied to clipboard as CSV.")

def run_gui():
	root = tk.Tk()
	root.title("JSON to Excel Converter (No pandas)")

	min_height = 170
	max_height = 240
	root.geometry(f"400x{min_height}")

	tk.Label(root, text="Select JSON file:").pack(pady=(10, 2))
	file_entry = tk.Entry(root, width=40)
	file_entry.pack(padx=10)
	browse_btn = tk.Button(root, text="Browse")
	browse_btn.pack(pady=(2, 10))

	key_label = tk.Label(root, text="Select data key:")
	key_var = tk.StringVar()
	key_radio_frame = tk.Frame(root)

	def show_data_key_widgets(show, keys=None):
		key_label.pack_forget()
		key_radio_frame.pack_forget()
		if show and keys:
			key_label.pack(pady=(0, 2))
			for widget in key_radio_frame.winfo_children():
				widget.destroy()
			for k in keys:
				tk.Radiobutton(key_radio_frame, text=k, variable=key_var, value=k).pack(anchor='w')
			key_radio_frame.pack(padx=10, pady=(0, 10))
			root.geometry(f"400x{max_height}")
		else:
			root.geometry(f"400x{min_height}")

	def on_browse():
		file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
		if file_path:
			file_entry.delete(0, tk.END)
			file_entry.insert(0, file_path)
			data = load_json(file_path)
			json_type = determine_json_structure(data) if data else 'unknown'
			if json_type == 'dict' and isinstance(data, dict):
				show_data_key_widgets(True, list(data.keys()))
				key_var.set(list(data.keys())[0] if data.keys() else '')
			else:
				show_data_key_widgets(False)

	browse_btn.config(command=on_browse)
	show_data_key_widgets(False)

	def get_selected_table():
		file_path = file_entry.get().strip()
		if not file_path or not os.path.isfile(file_path):
			messagebox.showerror("Error", "Please select a valid JSON file.")
			return None, None, None
		data = load_json(file_path)
		json_type = determine_json_structure(data) if data else 'unknown'
		if json_type == 'dict':
			data_key = key_var.get()
			if not data_key:
				messagebox.showerror("Error", "Please select a data key.")
				return None, None, None
			headers, rows = get_table_data(data, json_type, data_key)
		elif json_type == 'list':
			headers, rows = get_table_data(data, json_type)
		else:
			messagebox.showerror("Error", "Unsupported or invalid JSON structure.")
			return None, None, None
		file_name = os.path.splitext(os.path.basename(file_path))[0]
		return file_name, headers, rows

	def on_convert(to_csv=False):
		file_name, headers, rows = get_selected_table()
		if file_name and headers:
			if to_csv:
				save_to_csv(file_name, headers, rows)
				messagebox.showinfo("Success", f"CSV file '{file_name}.csv' created successfully.")
			else:
				save_to_excel(file_name, headers, rows)
				messagebox.showinfo("Success", f"Excel file '{file_name}.xlsx' created successfully.")

	def on_copy():
		_, headers, rows = get_selected_table()
		if headers:
			copy_to_clipboard(root, headers, rows)

	btn_frame = tk.Frame(root)
	btn_frame.pack(side=tk.BOTTOM, pady=15)
	tk.Button(btn_frame, text="Convert to Excel", command=lambda: on_convert(False)).pack(side=tk.LEFT, padx=10)
	tk.Button(btn_frame, text="Convert to CSV", command=lambda: on_convert(True)).pack(side=tk.LEFT, padx=10)
	tk.Button(btn_frame, text="Copy to Clipboard", command=on_copy).pack(side=tk.LEFT, padx=10)

	root.mainloop()

if __name__ == "__main__":
	run_gui()
