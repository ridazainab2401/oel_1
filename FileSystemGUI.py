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
            ("📖 Read", self.read_file)
        ]
        
        for text, command in operations:
            btn = ttk.Button(right_frame, text=text, command=command)
            btn.pack(fill=tk.X, pady=3)
        
        # Bottom frame for file content
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # File content area with custom styling
        content_label = ttk.Label(bottom_frame, text="File Content:", font=('Helvetica', 10, 'bold'))
        content_label.pack(anchor=tk.W)
        
        self.content_text = scrolledtext.ScrolledText(bottom_frame, 
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
            self.file_list.insert("", "end", values=(name, "📄 File", f"{size} bytes"))
        
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
        dialog = tk.Toplevel(self.root)
        dialog.title("Write to File")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="File Descriptor:").pack(pady=5)
        fd_entry = ttk.Entry(dialog)
        fd_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Text:").pack(pady=5)
        text_entry = ttk.Entry(dialog)
        text_entry.pack(pady=5)
        
        def on_ok():
            try:
                fd = int(fd_entry.get())
                text = text_entry.get()
                self.fs.write(fd, text)
                dialog.destroy()
            except ValueError:
                messagebox.showwarning("Warning", "Invalid file descriptor")
        
        ttk.Button(dialog, text="Write", command=on_ok).pack(pady=5)

    def read_file(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Read File")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="File Descriptor:").pack(pady=5)
        fd_entry = ttk.Entry(dialog)
        fd_entry.pack(pady=5)
        
        def on_ok():
            try:
                fd = int(fd_entry.get())
                # Clear the content area
                self.content_text.delete(1.0, tk.END)
                # Read the file content
                self.fs.read(fd)
                # Get the content from the file system
                if fd in self.fs.fd_table:
                    file_obj = self.fs.fd_table[fd]
                    content = file_obj.read()
                    self.content_text.insert(tk.END, content)
                dialog.destroy()
            except ValueError:
                messagebox.showwarning("Warning", "Invalid file descriptor")
        
        ttk.Button(dialog, text="Read", command=on_ok).pack(pady=5)

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