import pandas as pd
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

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

def show_data_key_entry(json_type):
    return json_type == 'dict'

def dataframe_from_json(data, json_type):
    if json_type == 'list':
        df = pd.DataFrame(data[1:], columns=data[0])
        msg = 'JSON root is a list.'
    else:
        df = pd.DataFrame(data)
        msg = 'JSON root is a dict.'
    return df, msg

def get_dataframe(file_path, data_key):
    data = load_json(file_path)
    if data is None:
        return None, "Invalid JSON file."
    json_type = determine_json_structure(data)
    if json_type == 'unknown':
        return None, "Unsupported JSON structure."
    if show_data_key_entry(json_type) and (data_key not in data.keys()):
        return None, f"Key '{data_key}' not valid for this JSON."
    if show_data_key_entry(json_type):
        data = data[data_key]
    df, msg = dataframe_from_json(data, json_type)
    return df, msg

def process_json(file_path, data_key, to_csv=False):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    try:
        df, msg = get_dataframe(file_path, data_key)
        if df is None:
            messagebox.showerror("Error", msg)
            return False
        if to_csv:
            df.to_csv(f'{file_name}.csv', index=False)
            messagebox.showinfo("Success", f"CSV file '{file_name}.csv' created successfully.\n{msg}")
        else:
            df.to_excel(f'{file_name}.xlsx', index=False)
            messagebox.showinfo("Success", f"Excel file '{file_name}.xlsx' created successfully.\n{msg}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def browse_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def data_key_entry(root):
    tk.Label(root, text="Enter data key:").pack(pady=5)
    key_entry = tk.Entry(root, width=40)
    key_entry.pack(padx=10)
    return key_entry

def run_gui():
    root = tk.Tk()
    root.title("JSON to Excel Converter")

    # Initial height for file input only
    min_height = 170
    max_height = 240
    root.geometry(f"400x{min_height}")

    # File selection row
    tk.Label(root, text="Select JSON file:").pack(pady=(10, 2))
    file_entry = tk.Entry(root, width=40)
    file_entry.pack(padx=10)
    browse_btn = tk.Button(root, text="Browse")
    browse_btn.pack(pady=(2, 10))

    # Data key widgets (radio buttons for dict, hidden by default)
    key_label = tk.Label(root, text="Select data key:")
    key_var = tk.StringVar()
    key_radio_frame = tk.Frame(root)

    def show_data_key_widgets(show, keys=None):
        key_label.pack_forget()
        key_radio_frame.pack_forget()
        if show and keys:
            key_label.pack(pady=(0, 2))
            # Remove previous radio buttons
            for widget in key_radio_frame.winfo_children():
                widget.destroy()
            # Add radio buttons for each key
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
            # Check JSON type and show/hide data key
            data = load_json(file_path)
            json_type = determine_json_structure(data) if data else 'unknown'
            if show_data_key_entry(json_type) and isinstance(data, dict):
                show_data_key_widgets(True, list(data.keys()))
                key_var.set(list(data.keys())[0] if data.keys() else '')
            else:
                show_data_key_widgets(False)

    browse_btn.config(command=on_browse)

    # Hide data key widgets initially
    show_data_key_widgets(False)

    def on_convert(to_csv=False):
        file_path = file_entry.get().strip()
        if not file_path or not os.path.isfile(file_path):
            messagebox.showerror("Error", "Please select a valid JSON file.")
            return
        data = load_json(file_path)
        json_type = determine_json_structure(data) if data else 'unknown'
        if json_type == 'dict':
            data_key = key_var.get()
            if not data_key:
                messagebox.showerror("Error", "Please select a data key.")
                return
            process_json(file_path, data_key, to_csv=to_csv)
        elif json_type == 'list':
            process_json(file_path, None, to_csv=to_csv)
        else:
            messagebox.showerror("Error", "Unsupported or invalid JSON structure.")

    def copy_to_clipboard():
        file_path = file_entry.get().strip()
        if not file_path or not os.path.isfile(file_path):
            messagebox.showerror("Error", "Please select a valid JSON file.")
            return
        data = load_json(file_path)
        json_type = determine_json_structure(data) if data else 'unknown'
        data_key = key_var.get() if show_data_key_entry(json_type) else None
        df, msg = get_dataframe(file_path, data_key)
        if df is None:
            messagebox.showerror("Error", msg)
            return
        csv_str = df.to_csv(index=False)
        root.clipboard_clear()
        root.clipboard_append(csv_str)
        messagebox.showinfo("Copied", "Data copied to clipboard as CSV.")

    # Convert and clipboard buttons always at the bottom
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, pady=15)
    tk.Button(btn_frame, text="Convert to Excel", command=lambda: on_convert(False)).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Convert to CSV", command=lambda: on_convert(True)).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Copy to Clipboard", command=lambda: copy_to_clipboard()).pack(side=tk.LEFT, padx=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
