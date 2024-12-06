import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt


class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("World happiness analysis")
        
        # File Selection
        self.file_label = tk.Label(root, text="No file selected")
        self.file_label.pack(pady=10)
        
        self.browse_button = tk.Button(root, text="Browse File", command=self.browse_file)
        self.browse_button.pack(pady=10)

        # Data Options for Filtering
        self.filter_label = tk.Label(root, text="Filter Data (e.g., Column=value or Column=value1,value2):")
        self.filter_label.pack(pady=5)

        self.filter_entry = tk.Entry(root, width=50)
        self.filter_entry.pack(pady=5)

        self.apply_filter_button = tk.Button(root, text="Apply Filter", command=self.apply_filter)
        self.apply_filter_button.pack(pady=5)

        # Clear Filter Button
        self.clear_filter_button = tk.Button(root, text="Clear Filter", command=self.clear_filter)
        self.clear_filter_button.pack(pady=5)
        
        # Data Preview
        self.preview_label = tk.Label(root, text="Data Preview:")
        self.preview_label.pack(pady=5)
        
        self.text_preview = tk.Text(root, height=10, width=80)
        self.text_preview.pack(pady=10)
        
        # Plotting Options
        self.options_frame = tk.Frame(root)
        self.options_frame.pack(pady=10)
        
        self.x_label = tk.Label(self.options_frame, text="X-axis Columns:")
        self.x_label.grid(row=0, column=0, padx=5)

        self.x_listbox = tk.Listbox(self.options_frame, selectmode="multiple", exportselection=False, height=5)
        self.x_listbox.grid(row=0, column=1, padx=5)

        self.y_label = tk.Label(self.options_frame, text="Y-axis Columns:")
        self.y_label.grid(row=0, column=2, padx=5)

        self.y_listbox = tk.Listbox(self.options_frame, selectmode="multiple", exportselection=False, height=5)
        self.y_listbox.grid(row=0, column=3, padx=5)

        self.plot_type_label = tk.Label(self.options_frame, text="Plot Type:")
        self.plot_type_label.grid(row=0, column=4, padx=5)

        self.plot_type_combobox = ttk.Combobox(self.options_frame, state="readonly")
        self.plot_type_combobox["values"] = ["Line", "Scatter", "Bar"]
        self.plot_type_combobox.grid(row=0, column=5, padx=5)
        self.plot_type_combobox.current(0)  # Default to "Line"
        
        self.plot_button = tk.Button(root, text="Plot", command=self.plot_data)
        self.plot_button.pack(pady=10)

    def browse_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), 
                                                         ("Text files", "*.txt"), 
                                                         ("Excel files", "*.xlsx;*.xls")])
        if filepath:
            self.file_label.config(text=filepath)
            self.load_data(filepath)

    def load_data(self, filepath):
        try:
            # Read the file based on its extension
            if filepath.endswith('.csv'):
                self.data = pd.read_csv(filepath, delimiter=';')  # Try using semicolon first
                #self.data = pd.read_csv(filepath, delimiter=',') 
            elif filepath.endswith('.txt'):
                self.data = pd.read_csv(filepath, delimiter='\t', encoding='ISO-8859-1')
            elif filepath.endswith(('.xlsx', '.xls')):
                self.data = pd.read_excel(filepath)
            else:
                raise ValueError("Unsupported file format")
            
            self.original_data = self.data.copy()
            
            # Update the text preview with the first few rows
            self.text_preview.delete("1.0", tk.END)
            self.text_preview.insert(tk.END, self.data.head().to_string())
            
            # Populate Listboxes with column names
            columns = self.data.columns.tolist()
            self.x_listbox.delete(0, tk.END)
            self.y_listbox.delete(0, tk.END)
            for column in columns:
                self.x_listbox.insert(tk.END, column)
                self.y_listbox.insert(tk.END, column)
        except Exception as e:
            self.text_preview.delete("1.0", tk.END)
            self.text_preview.insert(tk.END, f"Error loading file: {e}")

    def apply_filter(self):
      filter_text = self.filter_entry.get().strip()
      if not hasattr(self, 'data') or self.data.empty:
        self.text_preview.insert(tk.END, "\nPlease upload a file first!")
        return

      try:
        if "=" in filter_text:
            column, values = filter_text.split("=")
            column = column.strip()

            # Split the values by comma and strip extra spaces
            values = [v.strip() for v in values.split(",")]

            if column in self.data.columns:
                # Filter the data for rows where the column's value is in the list of values
                self.data = self.data[self.data[column].isin(values)]
                
                if self.data.empty:
                    messagebox.showwarning("No Data", f"No data matches the filter for '{column}'.")
                
                # Update the preview
                self.text_preview.delete("1.0", tk.END)
                self.text_preview.insert(tk.END, self.data.head().to_string())
            else:
                self.text_preview.insert(tk.END, f"\nColumn '{column}' not found!")
        else:
            self.text_preview.insert(tk.END, "\nInvalid filter format! Use Column=value or Column=value1,value2,...")
      except Exception as e:
        self.text_preview.insert(tk.END, f"\nError applying filter: {e}")


    def clear_filter(self):
        if hasattr(self, 'original_data'):
            self.data = self.original_data.copy()  # Reset to the original data
            self.text_preview.delete("1.0", tk.END)
            self.text_preview.insert(tk.END, self.data.head().to_string())  # Show the original data

    def plot_data(self):
        x_columns = [self.x_listbox.get(i) for i in self.x_listbox.curselection()]
        y_columns = [self.y_listbox.get(i) for i in self.y_listbox.curselection()]
        plot_type = self.plot_type_combobox.get()

        if not x_columns or not y_columns:
            messagebox.showerror("Error", "Please select both X and Y columns to plot.")
            return

        try:
            # Aggregate selected columns
            x_data = self.data[x_columns].sum(axis=1)
            y_data = self.data[y_columns].sum(axis=1)

            # Create a new Matplotlib figure
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot based on type
            if plot_type == "Line":
                ax.plot(x_data, y_data)
            elif plot_type == "Scatter":
                ax.scatter(x_data, y_data)
            elif plot_type == "Bar":
                ax.bar(x_data, y_data)

            # Add labels and title
            ax.set_xlabel(" + ".join(x_columns))
            ax.set_ylabel(" + ".join(y_columns))
            ax.set_title(f"{plot_type} plot of {y_columns} vs {x_columns}")

            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # Show the plot in a separate window
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Error while plotting: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()
