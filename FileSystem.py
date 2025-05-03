import os
import pickle
from typing import Dict, List, Optional

class File:
    def __init__(self, name: str):
        self.name = name
        self.data: List[str] = []
        self.is_open = False
        self.mode = 'r'  # 'r', 'a', 'w'

    def write(self, text: str) -> None:
        if self.mode == 'a':
            self.data.extend(list(text))
        elif self.mode == 'w':
            self.data = list(text)

    def write_at(self, pos: int, text: str) -> None:
        if pos >= len(self.data):
            self.data.extend([''] * (pos - len(self.data)))
            self.data.extend(list(text))
        else:
            for i, char in enumerate(text):
                if pos + i < len(self.data):
                    self.data[pos + i] = char
                else:
                    self.data.append(char)

    def read(self) -> str:
        return ''.join(self.data)

    def read_range(self, start: int, size: int) -> str:
        if start >= len(self.data):
            return ''
        end = min(start + size, len(self.data))
        return ''.join(self.data[start:end])

    def move_within(self, from_pos: int, to_pos: int, size: int) -> None:
        if from_pos >= len(self.data) or size == 0:
            return
        
        actual_size = min(size, len(self.data) - from_pos)
        temp = self.data[from_pos:from_pos + actual_size]
        
        # Remove the moved data
        del self.data[from_pos:from_pos + actual_size]
        
        # Insert at new position
        if to_pos >= len(self.data):
            self.data.extend([''] * (to_pos - len(self.data)))
            self.data.extend(temp)
        else:
            self.data[to_pos:to_pos] = temp

    def truncate(self, size: int) -> None:
        if size < len(self.data):
            self.data = self.data[:size]

class Directory:
    def __init__(self, name: str, parent: Optional['Directory'] = None):
        self.name = name
        self.parent = parent
        self.subdirs: Dict[str, Directory] = {}
        self.files: Dict[str, File] = {}

class FileSystem:
    def __init__(self):
        self.root = Directory("/")
        self.cwd = self.root
        self.fd_table: Dict[int, File] = {}
        self.next_fd = 1
        self.storage_file = "./filesystem.dat"

        # Try to load existing data
        self.load()
        
        # If no file exists, create an empty one
        if not os.path.exists(self.storage_file):
            print("Creating new filesystem.dat in current directory")
            self.save()
        else:
            print("Loaded existing filesystem.dat from current directory")

    def cwd_path(self) -> str:
        names = []
        cur = self.cwd
        while cur and cur != self.root:
            names.append(cur.name)
            cur = cur.parent
        path = "/"
        for name in reversed(names):
            path += name + "/"
        return path

    def create(self, fname: str) -> None:
        if fname in self.cwd.files:
            print("File already exists")
            return
        self.cwd.files[fname] = File(fname)
        print(f"Created file: {fname}")

    def delete(self, fname: str) -> None:
        if fname not in self.cwd.files:
            print("File not found")
            return
        del self.cwd.files[fname]
        print(f"Deleted file: {fname}")

    def mkdir(self, dname: str) -> None:
        if dname in self.cwd.subdirs:
            print("Directory already exists")
            return
        self.cwd.subdirs[dname] = Directory(dname, self.cwd)
        print(f"Created directory: {dname}")

    def chdir(self, dname: str) -> None:
        if dname == "..":
            if self.cwd.parent:
                self.cwd = self.cwd.parent
        elif dname == "/":
            self.cwd = self.root
        elif dname in self.cwd.subdirs:
            self.cwd = self.cwd.subdirs[dname]
        else:
            print("Directory not found")
            return
        print(f"Current directory: {self.cwd_path()}")

    def move(self, src: str, dst: str) -> None:
        # Split destination into path and filename
        dst_parts = dst.split('/')
        dst_name = dst_parts[-1]
        dst_path = dst_parts[:-1]

        # Find the target directory
        target_dir = self.cwd
        if dst_path:
            for dir_name in dst_path:
                if dir_name == '..':
                    if target_dir.parent:
                        target_dir = target_dir.parent
                    else:
                        print("Error: Cannot move above root directory")
                        return
                elif dir_name == '.':
                    continue
                elif dir_name in target_dir.subdirs:
                    target_dir = target_dir.subdirs[dir_name]
                else:
                    print(f"Error: Directory {dir_name} not found")
                    return

        # Handle file move
        if src in self.cwd.files:
            if dst_name in target_dir.files:
                print("Error: Destination file already exists")
                return
            f = self.cwd.files[src]
            del self.cwd.files[src]
            f.name = dst_name
            target_dir.files[dst_name] = f
            print(f"Moved file: {src} -> {dst}")
        # Handle directory move
        elif src in self.cwd.subdirs:
            if dst_name in target_dir.subdirs:
                print("Error: Destination directory already exists")
                return
            d = self.cwd.subdirs[src]
            del self.cwd.subdirs[src]
            d.name = dst_name
            d.parent = target_dir
            target_dir.subdirs[dst_name] = d
            print(f"Moved directory: {src} -> {dst}")
        else:
            print("Error: Source not found")

    def open(self, fname: str, mode: str) -> int:
        if fname not in self.cwd.files:
            print("File not found")
            return -1
        f = self.cwd.files[fname]
        f.is_open = True
        f.mode = mode
        fd = self.next_fd
        self.next_fd += 1
        self.fd_table[fd] = f
        print(f"Opened file {fname} with descriptor {fd}")
        return fd

    def close(self, fd: int) -> None:
        if fd not in self.fd_table:
            print("Invalid descriptor")
            return
        f = self.fd_table[fd]
        f.is_open = False
        del self.fd_table[fd]
        print(f"Closed descriptor {fd}")

    def write(self, fname: str, text: str) -> None:
        if fname not in self.cwd.files:
            print("File not found")
            return
        f = self.cwd.files[fname]
        if f.mode not in ['a', 'w']:
            print("File not open for writing")
            return
        f.write(text)
        print(f"Wrote to file {fname}")

    def write_at(self, fname: str, pos: int, text: str) -> None:
        if fname not in self.cwd.files:
            print("File not found")
            return
        f = self.cwd.files[fname]
        if f.mode != 'w':
            print("File not open for writing")
            return
        f.write_at(pos, text)
        print(f"Wrote to file {fname} at position {pos}")

    def read(self, fname: str) -> str:
        if fname not in self.cwd.files:
            print("File not found")
            return ""
        f = self.cwd.files[fname]
        return f.read()

    def read_range(self, fname: str, start: int, size: int) -> str:
        if fname not in self.cwd.files:
            print("File not found")
            return ""
        f = self.cwd.files[fname]
        return f.read_range(start, size)

    def move_content(self, src_file: str, dest_file: str, from_pos: int, to_pos: int, size: int) -> None:
        if src_file not in self.cwd.files or dest_file not in self.cwd.files:
            print("Source or destination file not found")
            return
        src = self.cwd.files[src_file]
        dest = self.cwd.files[dest_file]
        
        # Read the content from source file
        content = src.read_range(from_pos, size)
        
        # Write the content to destination file
        dest.write_at(to_pos, content)
        
        # Remove the content from source file
        if from_pos + size <= len(src.data):
            src.data[from_pos:from_pos + size] = []
        else:
            src.data = src.data[:from_pos]
        
        print(f"Moved {size} bytes from {src_file} to {dest_file}")

    def truncate(self, fname: str, size: int) -> None:
        if fname not in self.cwd.files:
            print("File not found")
            return
        f = self.cwd.files[fname]
        f.truncate(size)
        print(f"Truncated file {fname} to {size} bytes")

    def show_memory_map(self) -> None:
        print(f"Memory Map - Files in {self.cwd_path()}:")
        print(f"{'Name':<15} | {'Size':<10} | {'Mode':<10} | Status")
        print("-" * 50)
        
        for name, file in self.cwd.files.items():
            print(f"{name:<15} | {len(file.data):<10} | {file.mode:<10} | {'Open' if file.is_open else 'Closed'}")

    def show_file_structure(self) -> None:
        print("File Structure in current directory:")
        print("----------------------------------")
        
        def print_dir(d: Directory, depth: int = 0) -> None:
            indent = "  " * depth
            print(f"{indent}[{d.name}]")
            
            # Print files
            for name, file in d.files.items():
                print(f"{indent}  {name} ({len(file.data)} bytes)")
            
            # Print subdirectories
            for name, subdir in d.subdirs.items():
                print_dir(subdir, depth + 1)
        
        print_dir(self.root)

    def save(self) -> None:
        print(f"Saving to {self.storage_file}...")
        try:
            with open(self.storage_file, 'wb') as f:
                pickle.dump(self.root, f)
            print(f"Successfully saved to {self.storage_file}")
        except Exception as e:
            print(f"Error saving to {self.storage_file}: {e}")

    def load(self) -> None:
        print(f"Attempting to load from {self.storage_file}...")
        if not os.path.exists(self.storage_file):
            print("No existing filesystem.dat found - will create new one")
            return
        
        try:
            with open(self.storage_file, 'rb') as f:
                self.root = pickle.load(f)
            self.cwd = self.root
            print("Successfully loaded from filesystem.dat")
        except Exception as e:
            print(f"Error loading from {self.storage_file}: {e}")

    def loop(self) -> None:
        print("Simple FS CLI. Type 'help' for commands.")
        while True:
            try:
                cmd = input(f"{self.cwd_path()}> ").strip()
                if not cmd:
                    continue
                
                parts = cmd.split()
                op = parts[0]
                
                if op == "exit":
                    break
                elif op == "help":
                    self.print_help()
                elif op == "Create":
                    if len(parts) > 1:
                        self.create(parts[1])
                elif op == "Delete":
                    if len(parts) > 1:
                        self.delete(parts[1])
                elif op == "Mkdir":
                    if len(parts) > 1:
                        self.mkdir(parts[1])
                elif op == "chDir":
                    if len(parts) > 1:
                        self.chdir(parts[1])
                elif op == "Move":
                    if len(parts) > 2:
                        self.move(parts[1], parts[2])
                elif op == "Open":
                    if len(parts) > 2:
                        self.open(parts[1], parts[2])
                elif op == "Close":
                    if len(parts) > 1:
                        self.close(int(parts[1]))
                elif op == "Write":
                    if len(parts) > 2:
                        try:
                            fname = parts[1]
                            if len(parts) > 3:
                                pos = int(parts[2])
                                text = ' '.join(parts[3:])
                                self.write_at(fname, pos, text)
                            else:
                                text = ' '.join(parts[2:])
                                self.write(fname, text)
                        except ValueError:
                            print("Invalid file name")
                elif op == "Read":
                    if len(parts) > 1:
                        try:
                            fname = parts[1]
                            if len(parts) > 3:
                                start = int(parts[2])
                                size = int(parts[3])
                                self.read_range(fname, start, size)
                            else:
                                self.read(fname)
                        except ValueError:
                            print("Invalid file name")
                elif op == "MoveContent":
                    if len(parts) > 5:
                        try:
                            src_file = parts[1]
                            dest_file = parts[2]
                            from_pos = int(parts[3])
                            to_pos = int(parts[4])
                            size = int(parts[5])
                            self.move_content(src_file, dest_file, from_pos, to_pos, size)
                        except ValueError:
                            print("Invalid parameters")
                elif op == "Truncate":
                    if len(parts) > 2:
                        try:
                            fname = parts[1]
                            size = int(parts[2])
                            self.truncate(fname, size)
                        except ValueError:
                            print("Invalid parameters")
                elif op == "ShowMem":
                    self.show_memory_map()
                elif op == "ShowFiles":
                    self.show_file_structure()
                else:
                    print("Unknown command")
            except Exception as e:
                print(f"Error: {e}")

    def print_help(self) -> None:
        print("Commands:")
        print(" Create <fname>")
        print(" Delete <fname>")
        print(" Mkdir <dirname>")
        print(" chDir <dirname>")
        print(" Move <src> <dst>")
        print(" Open <fname> <mode:r/w/a>")
        print(" Close <fd>")
        print(" Write <fname> [pos] <text>")
        print(" Read <fname> [start size]")
        print(" MoveContent <src_file> <dest_file> <from_pos> <to_pos> <size>")
        print(" Truncate <fname> <size>")
        print(" ShowMem")
        print(" ShowFiles")
        print(" exit")

if __name__ == "__main__":
    fs = FileSystem()
    fs.loop() 