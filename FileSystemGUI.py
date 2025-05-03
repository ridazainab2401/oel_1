import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from FileSystem import FileSystem
import tkinter.font as tkFont

class FileSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File System GUI")
        self.root.geometry("1000x700")
        
        # Configure dark theme colors
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.accent_color = "#4a9eff"
        self.text_color = "#ffffff"
        self.tree_bg = "#3c3f41"
        self.tree_fg = "#ffffff"
        self.tree_sel = "#4a9eff"
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam theme as base
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Configure styles
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TButton", 
                           background=self.accent_color,
                           foreground=self.fg_color,
                           padding=6,
                           relief="flat")
        self.style.configure("Treeview",
                           background=self.tree_bg,
                           foreground=self.tree_fg,
                           fieldbackground=self.tree_bg,
                           rowheight=25)
        self.style.configure("Treeview.Heading",
                           background=self.tree_bg,
                           foreground=self.fg_color,
                           font=('Helvetica', 10, 'bold'))
        self.style.map("Treeview",
                      background=[('selected', self.tree_sel)],
                      foreground=[('selected', self.fg_color)])
        
        self.fs = FileSystem()
        
        # Create main frames
        self.create_widgets()
        
        # Update initial display
        self.update_file_list()
        self.update_path_label()

    def create_widgets(self):
        # Top frame for path and navigation
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Path label with icon
        path_frame = ttk.Frame(top_frame)
        path_frame.pack(fill=tk.X)
        
        self.path_label = ttk.Label(path_frame, text="", font=('Helvetica', 10))
        self.path_label.pack(side=tk.LEFT)
        
        # Navigation buttons
        nav_frame = ttk.Frame(top_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(nav_frame, text="↑ Up", command=self.navigate_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="⌂ Root", command=self.navigate_root).pack(side=tk.LEFT, padx=2)
        
        # Main content area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel for file list
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # File list with custom styling
        self.file_list = ttk.Treeview(left_frame, columns=("Name", "Type", "Size"), show="headings")
        self.file_list.heading("Name", text="Name")
        self.file_list.heading("Type", text="Type")
        self.file_list.heading("Size", text="Size")
        
        # Configure column widths
        self.file_list.column("Name", width=200)
        self.file_list.column("Type", width=100)
        self.file_list.column("Size", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=scrollbar.set)
        
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right panel for operations
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Operation buttons with icons
        operations = [
            ("📄 Create File", self.create_file),
            ("📁 Create Directory", self.create_directory),
            ("🗑️ Delete", self.delete_item),
            ("↔️ Move", self.move_item),
            ("📂 Open", self.open_file),
            ("✏️ Write", self.write_file),
            ("📖 Read", self.read_file),
            ("✂️ Truncate", self.truncate_file),
            ("⇄ Move Content", self.move_content)
        ]
        
        for text, command in operations:
            btn = ttk.Button(right_frame, text=text, command=command)
            btn.pack(fill=tk.X, pady=3)
        
        # Bottom frame for file content
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # File content area with custom styling
        content_frame = ttk.Frame(bottom_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        content_header = ttk.Frame(content_frame)
        content_header.pack(fill=tk.X)
        
        content_label = ttk.Label(content_header, text="File Content:", font=('Helvetica', 10, 'bold'))
        content_label.pack(side=tk.LEFT)
        
        # Add file info label
        self.file_info_label = ttk.Label(content_header, text="", font=('Helvetica', 9))
        self.file_info_label.pack(side=tk.RIGHT)
        
        self.content_text = scrolledtext.ScrolledText(content_frame, 
                                                    height=10, 
                                                    font=('Consolas', 10),
                                                    bg=self.tree_bg,
                                                    fg=self.fg_color,
                                                    insertbackground=self.fg_color)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind double click to open file
        self.file_list.bind("<Double-1>", self.on_double_click)
        
        # Add status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def navigate_up(self):
        if self.fs.cwd.parent:
            self.fs.chdir("..")
            self.update_file_list()
            self.update_path_label()

    def navigate_root(self):
        self.fs.chdir("/")
        self.update_file_list()
        self.update_path_label()

    def update_status(self, message):
        self.status_bar.config(text=message)

    def update_file_list(self):
        # Clear current items
        for item in self.file_list.get_children():
            self.file_list.delete(item)
        
        # Add directories
        for name, dir_obj in self.fs.cwd.subdirs.items():
            self.file_list.insert("", "end", values=(name, "📁 Directory", "-"))
        
        # Add files
        for name, file_obj in self.fs.cwd.files.items():
            size = len(file_obj.data)
            status = "Open" if file_obj.is_open else "Closed"
            self.file_list.insert("", "end", values=(name, "📄 File", f"{size} bytes ({status})"))
        
        self.update_status(f"Displaying contents of {self.fs.cwd_path()}")

    def update_path_label(self):
        self.path_label.config(text=f"📂 Current Path: {self.fs.cwd_path()}")

    def create_file(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create File")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="File Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(pady=5)
        
        def on_ok():
            name = name_entry.get()
            if name:
                self.fs.create(name)
                self.update_file_list()
                dialog.destroy()
        
        ttk.Button(dialog, text="Create", command=on_ok).pack(pady=5)

    def create_directory(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Directory")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Directory Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(pady=5)
        
        def on_ok():
            name = name_entry.get()
            if name:
                self.fs.mkdir(name)
                self.update_file_list()
                dialog.destroy()
        
        ttk.Button(dialog, text="Create", command=on_ok).pack(pady=5)

    def delete_item(self):
        selection = self.file_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item = self.file_list.item(selection[0])
        name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {name}?"):
            if item['values'][1] == "Directory":
                # TODO: Implement directory deletion
                pass
            else:
                self.fs.delete(name)
            self.update_file_list()

    def move_item(self):
        selection = self.file_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to move")
            return
        
        item = self.file_list.item(selection[0])
        src_name = item['values'][0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Move Item")
        dialog.geometry("400x300")
        dialog.configure(bg=self.bg_color)
        
        # Create a frame for the directory tree
        tree_frame = ttk.Frame(dialog)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a treeview for directory navigation
        dir_tree = ttk.Treeview(tree_frame)
        dir_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=dir_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        dir_tree.configure(yscrollcommand=scrollbar.set)
        
        # Add root directory
        dir_tree.insert("", "end", "root", text="/")
        
        # Function to populate directory tree
        def populate_tree(node, parent_id):
            if node == self.fs.root:
                for name, subdir in node.subdirs.items():
                    item_id = dir_tree.insert(parent_id, "end", text=name)
                    populate_tree(subdir, item_id)
            else:
                for name, subdir in node.subdirs.items():
                    item_id = dir_tree.insert(parent_id, "end", text=name)
                    populate_tree(subdir, item_id)
        
        # Populate the tree
        populate_tree(self.fs.root, "root")
        
        # New name entry
        name_frame = ttk.Frame(dialog)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(name_frame, text="New Name:").pack(side=tk.LEFT)
        name_entry = ttk.Entry(name_frame)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        name_entry.insert(0, src_name)  # Default to current name
        
        # Create a frame for the OK button (initially hidden)
        ok_frame = ttk.Frame(dialog)
        ok_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Function to show/hide OK button based on selection
        def on_tree_select(event):
            selected = dir_tree.selection()
            if selected:
                ok_button.pack(side=tk.RIGHT, padx=5)
            else:
                ok_button.pack_forget()
        
        # Bind selection event
        dir_tree.bind("<<TreeviewSelect>>", on_tree_select)
        
        def on_ok():
            selected = dir_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a destination directory")
                return
            
            new_name = name_entry.get()
            if not new_name:
                messagebox.showwarning("Warning", "Please enter a name")
                return
            
            # Get the full path of the selected directory
            path_parts = []
            current = selected[0]
            while current != "root":
                path_parts.insert(0, dir_tree.item(current)["text"])
                current = dir_tree.parent(current)
            
            # Construct the destination path
            dst_path = "/".join(path_parts)
            if dst_path:
                dst_path += "/"
            dst_path += new_name
            
            # Perform the move
            self.fs.move(src_name, dst_path)
            self.update_file_list()
            self.update_path_label()
            self.update_status(f"Moved {src_name} to {dst_path}")
            dialog.destroy()
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create OK button but don't pack it yet
        ok_button = ttk.Button(button_frame, text="OK", command=on_ok)
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def open_file(self):
        selection = self.file_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to open")
            return
        
        item = self.file_list.item(selection[0])
        if item['values'][1] != "📄 File":
            messagebox.showwarning("Warning", "Please select a file")
            return
        
        name = item['values'][0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Open File")
        dialog.geometry("300x150")
        dialog.configure(bg=self.bg_color)
        
        # Mode selection
        mode_frame = ttk.Frame(dialog)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        mode_var = tk.StringVar(value="r")
        
        # Create radio buttons for mode selection
        ttk.Radiobutton(mode_frame, text="Read (r)", variable=mode_var, value="r").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Write (w)", variable=mode_var, value="w").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Append (a)", variable=mode_var, value="a").pack(side=tk.LEFT, padx=5)
        
        def on_ok():
            mode = mode_var.get()
            fd = self.fs.open(name, mode)
            if fd != -1:
                self.content_text.delete(1.0, tk.END)
                if mode == "r":
                    # Read and display the file content
                    file_obj = self.fs.fd_table[fd]
                    content = file_obj.read()
                    self.content_text.insert(tk.END, content)
                    self.update_status(f"Opened file {name} in read mode (fd: {fd})")
                else:
                    self.update_status(f"Opened file {name} in {mode} mode (fd: {fd})")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to open file")
        
        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Open", command=on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def write_file(self):
        selection = self.file_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to write to")
            return
        
        item = self.file_list.item(selection[0])
        if item['values'][1] != "📄 File":
            messagebox.showwarning("Warning", "Please select a file")
            return
        
        name = item['values'][0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Write to File")
        dialog.geometry("400x300")
        dialog.configure(bg=self.bg_color)
        
        # Mode selection
        mode_frame = ttk.Frame(dialog)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        mode_var = tk.StringVar(value="append")
        
        ttk.Radiobutton(mode_frame, text="Append", variable=mode_var, value="append").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Write At Position", variable=mode_var, value="write_at").pack(side=tk.LEFT, padx=5)
        
        # Position entry (only shown for write_at mode)
        pos_frame = ttk.Frame(dialog)
        pos_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(pos_frame, text="Position:").pack(side=tk.LEFT)
        pos_entry = ttk.Entry(pos_frame)
        pos_entry.pack(side=tk.LEFT, padx=5)
        pos_entry.pack_forget()  # Initially hidden
        
        # Text entry
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(text_frame, text="Text:").pack(side=tk.LEFT)
        text_entry = ttk.Entry(text_frame)
        text_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def on_mode_change(*args):
            if mode_var.get() == "write_at":
                pos_entry.pack(side=tk.LEFT, padx=5)
            else:
                pos_entry.pack_forget()
        
        mode_var.trace("w", on_mode_change)
        
        def on_ok():
            try:
                text = text_entry.get()
                if mode_var.get() == "append":
                    self.fs.write(name, text)
                    self.update_status(f"Appended text to {name}")
                else:
                    pos = int(pos_entry.get())
                    if pos < 0:
                        raise ValueError("Position must be non-negative")
                    self.fs.write_at(name, pos, text)
                    self.update_status(f"Wrote text at position {pos} in {name}")
                
                self.update_file_list()
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Write", command=on_ok).pack(pady=5)

    def read_file(self):
        selection = self.file_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to read")
            return
        
        item = self.file_list.item(selection[0])
        if item['values'][1] != "📄 File":
            messagebox.showwarning("Warning", "Please select a file")
            return
        
        name = item['values'][0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Read File")
        dialog.geometry("400x300")
        dialog.configure(bg=self.bg_color)
        
        # Mode selection
        mode_frame = ttk.Frame(dialog)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        mode_var = tk.StringVar(value="sequential")
        
        ttk.Radiobutton(mode_frame, text="Sequential", variable=mode_var, value="sequential").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Read From Position", variable=mode_var, value="read_from").pack(side=tk.LEFT, padx=5)
        
        # Parameters frame (only shown for read_from mode)
        params_frame = ttk.Frame(dialog)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start position
        start_frame = ttk.Frame(params_frame)
        start_frame.pack(fill=tk.X, pady=2)
        ttk.Label(start_frame, text="Start Position:").pack(side=tk.LEFT)
        start_entry = ttk.Entry(start_frame)
        start_entry.pack(side=tk.LEFT, padx=5)
        start_frame.pack_forget()  # Initially hidden
        
        # Size
        size_frame = ttk.Frame(params_frame)
        size_frame.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, text="Size:").pack(side=tk.LEFT)
        size_entry = ttk.Entry(size_frame)
        size_entry.pack(side=tk.LEFT, padx=5)
        size_frame.pack_forget()  # Initially hidden
        
        def on_mode_change(*args):
            if mode_var.get() == "read_from":
                start_frame.pack(fill=tk.X, pady=2)
                size_frame.pack(fill=tk.X, pady=2)
            else:
                start_frame.pack_forget()
                size_frame.pack_forget()
        
        mode_var.trace("w", on_mode_change)
        
        def on_ok():
            try:
                if mode_var.get() == "sequential":
                    # Clear the content area
                    self.content_text.delete(1.0, tk.END)
                    # Read the file content
                    content = self.fs.read(name)
                    self.content_text.insert(tk.END, content)
                    self.update_status(f"Read entire content of {name}")
                else:
                    start = int(start_entry.get())
                    size = int(size_entry.get())
                    if start < 0 or size < 0:
                        raise ValueError("Start position and size must be non-negative")
                    
                    # Clear the content area
                    self.content_text.delete(1.0, tk.END)
                    # Read the specified range
                    content = self.fs.read_range(name, start, size)
                    self.content_text.insert(tk.END, content)
                    self.update_status(f"Read {size} bytes from position {start} in {name}")
                
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Read", command=on_ok).pack(pady=5)

    def truncate_file(self):
        selection = self.file_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to truncate")
            return
        
        item = self.file_list.item(selection[0])
        if item['values'][1] != "📄 File":
            messagebox.showwarning("Warning", "Please select a file")
            return
        
        name = item['values'][0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Truncate File")
        dialog.geometry("300x150")
        dialog.configure(bg=self.bg_color)
        
        ttk.Label(dialog, text=f"Truncate {name} to size:").pack(pady=5)
        size_entry = ttk.Entry(dialog)
        size_entry.pack(pady=5)
        
        def on_ok():
            try:
                size = int(size_entry.get())
                if size < 0:
                    raise ValueError("Size must be non-negative")
                
                self.fs.truncate(name, size)
                self.update_file_list()
                self.update_status(f"Truncated {name} to {size} bytes")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Truncate", command=on_ok).pack(pady=5)

    def move_content(self):
        selection = self.file_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to move content from")
            return
        
        item = self.file_list.item(selection[0])
        if item['values'][1] != "📄 File":
            messagebox.showwarning("Warning", "Please select a file")
            return
        
        source_file = item['values'][0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Move Content")
        dialog.geometry("400x400")
        dialog.configure(bg=self.bg_color)
        
        # Source file info
        src_frame = ttk.Frame(dialog)
        src_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(src_frame, text=f"Source File: {source_file}").pack(side=tk.LEFT)
        
        # Destination file selection
        dest_frame = ttk.Frame(dialog)
        dest_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(dest_frame, text="Destination File:").pack(side=tk.LEFT)
        
        # Create a listbox for destination files
        dest_listbox = tk.Listbox(dest_frame, height=5)
        dest_listbox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(dest_frame, orient=tk.VERTICAL, command=dest_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        dest_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Populate the listbox with files
        for name, file_obj in self.fs.cwd.files.items():
            if name != source_file:  # Don't include source file
                dest_listbox.insert(tk.END, name)
        
        # Parameters frame
        params_frame = ttk.Frame(dialog)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # From position
        from_frame = ttk.Frame(params_frame)
        from_frame.pack(fill=tk.X, pady=2)
        ttk.Label(from_frame, text="From Position:").pack(side=tk.LEFT)
        from_entry = ttk.Entry(from_frame)
        from_entry.pack(side=tk.LEFT, padx=5)
        
        # To position
        to_frame = ttk.Frame(params_frame)
        to_frame.pack(fill=tk.X, pady=2)
        ttk.Label(to_frame, text="To Position:").pack(side=tk.LEFT)
        to_entry = ttk.Entry(to_frame)
        to_entry.pack(side=tk.LEFT, padx=5)
        
        # Size
        size_frame = ttk.Frame(params_frame)
        size_frame.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, text="Size:").pack(side=tk.LEFT)
        size_entry = ttk.Entry(size_frame)
        size_entry.pack(side=tk.LEFT, padx=5)
        
        def on_ok():
            try:
                if not dest_listbox.curselection():
                    raise ValueError("Please select a destination file")
                
                dest_file = dest_listbox.get(dest_listbox.curselection())
                from_pos = int(from_entry.get())
                to_pos = int(to_entry.get())
                size = int(size_entry.get())
                
                if from_pos < 0 or to_pos < 0 or size < 0:
                    raise ValueError("Positions and size must be non-negative")
                
                self.fs.move_content(source_file, dest_file, from_pos, to_pos, size)
                self.update_file_list()
                self.update_status(f"Moved {size} bytes from position {from_pos} in {source_file} to position {to_pos} in {dest_file}")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Move Content", command=on_ok).pack(pady=5)

    def on_double_click(self, event):
        selection = self.file_list.selection()
        if not selection:
            return
        
        item = self.file_list.item(selection[0])
        name = item['values'][0]
        
        if item['values'][1] == "📁 Directory":
            self.fs.chdir(name)
            self.update_file_list()
            self.update_path_label()
            self.update_status(f"Entered directory: {name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSystemGUI(root)
    root.mainloop() 