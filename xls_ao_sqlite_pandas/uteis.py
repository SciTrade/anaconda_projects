import tkinter as tk
from tkinter import filedialog
def openfile():
                # Create a temporary root window
                temp_root = tk.Tk()
                temp_root.withdraw()  # Hide the root window
                
                # Create a top-level window to stay on top
                top_level = tk.Toplevel(temp_root)
                top_level.withdraw()  # Hide the top-level window
                top_level.attributes('-topmost', 1)  # Make it stay on top
                
                # Open the file dialog using the top-level window
                file_path = filedialog.askopenfilename(parent=top_level)
                
                # Destroy the top-level and root windows after the dialog is closed
                top_level.destroy()
                temp_root.destroy()
                return file_path