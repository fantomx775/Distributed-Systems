import sys
import subprocess
import threading
from kazoo.client import KazooClient
from kazoo.client import KazooState
import tkinter as tk

class ZookeeperApp:
    def __init__(self, zookeeper_hosts, external_app_command):
        self.zk = KazooClient(hosts=zookeeper_hosts)
        self.zk.add_listener(self.my_listener)
        self.external_app_command = external_app_command
        self.external_app_process = None
        self.root = None
        self.init_zk()
        self.start_command_listener()

    def my_listener(self, state):
        if state == KazooState.LOST:
            print("Zookeeper connection lost!")
        elif state == KazooState.SUSPENDED:
            print("Zookeeper connection suspended!")
        else:
            print("Zookeeper connection established!")

    def init_zk(self):
        self.zk.start()
        self.zk.ensure_path("/a")
        self.watch_node("/a")
        self.watch_all_descendants("/a")
        self.start_external_app()

    def watch_node(self, path):
        @self.zk.DataWatch(path)
        def watch_node(data, stat):
            if stat is None:
                print(f"Node {path} deleted, stopping external application and quitting Tkinter main loop.")
                self.stop_external_app()
                if self.root:
                    self.root.quit()  #
                self.wait_for_node_creation(path)

    def wait_for_node_creation(self, path):
        @self.zk.DataWatch(path)
        def watch_for_creation(data, stat):
            if stat is not None:
                print(f"Node {path} recreated, restarting external application and Tkinter main loop.")
                self.init_zk()
                if self.root:
                    self.root = tk.Tk()
                    self.run()

    def watch_all_descendants(self, path):
        @self.zk.ChildrenWatch(path)
        def watch_children(children):
            total_children = self.count_total_children("/a")
            self.show_children_count(total_children)

            for child in children:
                child_path = f"{path}/{child}"
                self.watch_all_descendants(child_path)

    def start_external_app(self):
        print("Starting external application...")
        self.external_app_process = subprocess.Popen(self.external_app_command.split())

    def stop_external_app(self):
        if self.external_app_process:
            print("Stopping external application...")
            self.external_app_process.terminate()
            try:
                self.external_app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.external_app_process.kill()
            self.external_app_process = None
        print("External application stopped.")
        sys.exit(1)

    def count_total_children(self, path):
        total = 0
        children = self.zk.get_children(path)
        for child in children:
            child_path = f"{path}/{child}"
            total += 1 + self.count_total_children(child_path)
        return total

    def show_children_count(self, count):
        if self.root is None:
            self.root = tk.Tk()
            self.root.title("Zookeeper App")
        else:
            for widget in self.root.winfo_children():
                widget.destroy()

        message = f"Liczba potomków: {count}"
        label = tk.Label(self.root, text=message, font=("Helvetica", 16))
        label.pack(pady=20)
        self.root.update()

    def display_tree(self, path="/a"):
        print(f"Displaying tree structure for {path}:")
        self.display_node(path, first=True)

    def display_node(self, path, prefix="", first=False):
        if first:
            print(path)
        children = self.zk.get_children(path)
        if children:
            for i, child in enumerate(children):
                if i < len(children) - 1:
                    next_prefix = prefix + "├── "
                    child_prefix = prefix + "│   "
                else:
                    next_prefix = prefix + "└── "
                    child_prefix = prefix + "    "
                print(next_prefix + child)
                self.display_node(f"{path}/{child}", child_prefix)

    def display_all_trees(self):
        print("Displaying all tree structures:")
        root_nodes = self.zk.get_children('/')
        for node in root_nodes:
            self.display_node(f"/{node}", first=True)

    def run(self):
        self.root.mainloop()
        self.zk.stop()

    def start_command_listener(self):
        threading.Thread(target=self.command_listener, daemon=True).start()

    def command_listener(self):
        while True:
            command = input("Enter command: ")
            if command.strip().lower() == "tree":
                self.display_tree("/a")
            elif command.strip().lower() == "treeall":
                self.display_all_trees()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <zookeeper_hosts> <external_app_command>")
        sys.exit(1)

    zookeeper_hosts = sys.argv[1]
    external_app_command = sys.argv[2]

    app = ZookeeperApp(zookeeper_hosts, external_app_command)
    app.run()
