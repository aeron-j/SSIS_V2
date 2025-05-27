import tkinter as tk
from tkinter import ttk
import re
from utils.validation import validate_id_format, validate_text_only

class ValidatedEntry(tk.Entry):
    def __init__(self, parent, validate_type="text", **kwargs):
        super().__init__(parent, **kwargs)
        
        if validate_type == "text":
            vcmd = (parent.register(self.validate_text), '%P')
            self.config(validate="key", validatecommand=vcmd)
        elif validate_type == "id":
            vcmd = (parent.register(self.validate_id), '%P')
            self.config(validate="key", validatecommand=vcmd)
    
    def validate_text(self, text):
        return all(not c.isdigit() for c in text)
    
    def validate_id(self, text):
        return re.match(r'^\d{0,4}(-\d{0,4})?$', text) is not None

class LabelInput(tk.Frame):
    def __init__(self, parent, label_text, input_class, input_args=None, 
                 validate_type=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.label = tk.Label(self, text=label_text)
        self.label.pack(side=tk.LEFT, padx=5)
        
        input_args = input_args or {}
        if validate_type:
            self.input = ValidatedEntry(self, validate_type=validate_type, **input_args)
        else:
            self.input = input_class(self, **input_args)
        
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def get(self):
        return self.input.get()
    
    def insert(self, index, text):
        self.input.insert(index, text)
    
    def delete(self, first, last=None):
        self.input.delete(first, last)