import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3

# 数据库文件路径
DB_FILE = 'items.db'

class Item:
    def __init__(self, id, name, description, contact):
        self.id = id
        self.name = name
        self.description = description
        self.contact = contact

class ItemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("物品复活软件")
        self.create_database()
        self.items = []
        self.deleted_items = []  # 用于存放被删除的物品

        self.create_widgets()
        self.load_items()
        self.load_recovered_items()

    def create_database(self):
        """创建数据库和表"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            # 设置 journal_mode 为 WAL 以支持更好的并发访问
            cursor.execute('PRAGMA journal_mode=WAL;')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    contact TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deleted_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    contact TEXT
                )
            ''')
            conn.commit()

    def create_widgets(self):
        """创建主界面组件"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.items_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.items_frame, text="物品列表")

        self.recovery_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recovery_frame, text="回收站")

        self.create_items_tab()
        self.create_recovery_tab()

    def create_items_tab(self):
        """创建物品列表标签页"""
        add_frame = ttk.LabelFrame(self.items_frame, text="添加/编辑物品")
        add_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(add_frame, text="名称:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(add_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="描述 (可选):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.description_entry = ttk.Entry(add_frame, width=30)
        self.description_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="联系人信息 (可选):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.contact_entry = ttk.Entry(add_frame, width=30)
        self.contact_entry.grid(row=2, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(add_frame, text="添加物品", command=self.add_item)
        self.add_button.grid(row=3, column=2, padx=5, pady=10)

        self.edit_button = ttk.Button(add_frame, text="编辑物品", command=self.edit_item)
        self.edit_button.grid(row=3, column=3, padx=5, pady=10)

        operation_frame = ttk.LabelFrame(self.items_frame, text="搜索与操作")
        operation_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(operation_frame, text="搜索关键词:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_entry = ttk.Entry(operation_frame, width=35)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = ttk.Button(operation_frame, text="搜索", command=self.search_items)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.show_all_button = ttk.Button(operation_frame, text="显示所有", command=self.load_items)
        self.show_all_button.grid(row=0, column=3, padx=5, pady=5)

        list_frame = ttk.Frame(self.items_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("名称", "描述", "联系人信息")
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        bottom_frame = ttk.Frame(self.items_frame)
        bottom_frame.pack(fill="x", padx=10, pady=5)

        self.delete_button = ttk.Button(bottom_frame, text="删除选中物品", command=self.delete_item)
        self.delete_button.pack(side="right", padx=5)

    def create_recovery_tab(self):
        """创建回收站标签页"""
        recovery_frame = ttk.Frame(self.recovery_frame)
        recovery_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # 添加搜索与操作区域
        recovery_operation_frame = ttk.LabelFrame(recovery_frame, text="搜索与操作")
        recovery_operation_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(recovery_operation_frame, text="搜索关键词:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_recovery_entry = ttk.Entry(recovery_operation_frame, width=35)
        self.search_recovery_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_recovery_button = ttk.Button(recovery_operation_frame, text="搜索",
                                                 command=self.search_recovered_items)
        self.search_recovery_button.grid(row=0, column=2, padx=5, pady=5)

        self.show_all_recovery_button = ttk.Button(recovery_operation_frame, text="显示所有", command=self.show_all_recovered_items)
        self.show_all_recovery_button.grid(row=0, column=3, padx=5, pady=5)

        # 回收站物品列表
        list_frame = ttk.Frame(recovery_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("名称", "描述", "联系人信息")
        self.recovery_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.recovery_tree.heading(col, text=col)
            self.recovery_tree.column(col, width=150)
        self.recovery_tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.recovery_tree.yview)
        self.recovery_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # 回收站操作按钮
        recovery_buttons_frame = ttk.Frame(recovery_frame)
        recovery_buttons_frame.pack(fill="x", padx=10, pady=5)

        self.clear_recovery_button = ttk.Button(recovery_buttons_frame, text="清空回收站", command=self.clear_recovery_bin)
        self.clear_recovery_button.pack(side="right", padx=5)

        self.permanently_delete_button = ttk.Button(recovery_buttons_frame, text="永久删除选中物品", command=self.permanently_delete_item)
        self.permanently_delete_button.pack(side="right", padx=5)

        self.recovery_button = ttk.Button(recovery_buttons_frame, text="恢复选中物品", command=self.recover_item)
        self.recovery_button.pack(side="right", padx=5)




    def add_item(self):
        """添加新物品到数据库"""
        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()
        contact = self.contact_entry.get().strip()

        if not name:
            messagebox.showwarning("输入错误", "请填写物品名称！")
            return

        # 检查名称是否已存在（活跃物品和回收站中）
        try:
            self.insert_item_to_db(name, description, contact)
            self.load_items()
            self.clear_entries()
            messagebox.showinfo("成功", f"物品“{name}”已添加成功。")
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", f"无法添加物品“{name}”，因为名称已存在。")

    def edit_item(self):
        """准备编辑选中的物品"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("编辑错误", "请选择要编辑的物品！")
            return

        item_name = self.tree.item(selected[0], 'values')[0]
        for item in self.items:
            if item.name == item_name:
                self.name_entry.delete(0, tk.END)
                self.description_entry.delete(0, tk.END)
                self.contact_entry.delete(0, tk.END)

                self.name_entry.insert(0, item.name)
                self.description_entry.insert(0, item.description)
                self.contact_entry.insert(0, item.contact)
                break

        self.add_button.config(state=tk.DISABLED)
        self.edit_button.config(text="保存更改", command=lambda: self.save_changes(selected[0]))

    def save_changes(self, selected):
        """保存编辑后的物品信息"""
        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()
        contact = self.contact_entry.get().strip()

        if not name:
            messagebox.showwarning("输入错误", "请填写物品名称！")
            return

        original_name = self.tree.item(selected, 'values')[0]

        # 检查名称是否已存在，只有在名称发生变化时才进行检查
        if name != original_name:
            try:
                self.update_item_in_db(original_name, name, description, contact)
                self.load_items()
                self.clear_entries()
                self.add_button.config(state=tk.NORMAL)
                self.edit_button.config(text="编辑物品", command=self.edit_item)
                messagebox.showinfo("成功", f"物品“{name}”已更新成功。")
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", f"无法更新物品“{name}”，因为名称已存在。")

    def delete_item(self):
        """将选中的物品移动到回收站"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("删除错误", "请选择要删除的物品！")
            return

        confirm = messagebox.askyesno("确认删除", "你确定要删除选中的物品吗？这将移动到回收站。")
        if not confirm:
            return

        for sel in selected:
            item_name = self.tree.item(sel, 'values')[0]
            item = self.get_item_from_db(item_name)
            if item:
                try:
                    # 将物品插入到回收站，不使用 INSERT OR REPLACE
                    self.insert_deleted_item_to_db(item)
                    self.delete_item_from_db(item_name)
                except sqlite3.IntegrityError:
                    messagebox.showerror("错误", f"无法将物品“{item_name}”移动到回收站。")
                    continue  # 继续处理下一个选中的物品

        self.load_items()
        self.load_recovered_items()
        messagebox.showinfo("删除成功", "选中的物品已移动到回收站。")

    def recover_item(self):
        """从回收站恢复选中的物品"""
        selected = self.recovery_tree.selection()
        if not selected:
            messagebox.showwarning("恢复错误", "请选择要恢复的物品！")
            return

        for sel in selected:
            item_id = self.recovery_tree.item(sel, 'text')  # 使用Treeview的item ID
            item = self.get_deleted_item_from_db_by_id(item_id)
            if item:
                # 检查名称是否在活跃物品中已存在
                if self.item_exists(item.name):
                    response = messagebox.askyesno("重复名称", f"名称为“{item.name}”的物品已存在于物品列表中。是否替换？")
                    if response:
                        try:
                            self.update_item_in_db(item.name, item.name, item.description, item.contact)
                            self.delete_deleted_item_from_db(item.id)
                        except sqlite3.IntegrityError:
                            messagebox.showerror("错误", f"无法替换物品“{item.name}”。")
                    else:
                        continue
                else:
                    try:
                        self.insert_item_to_db(item.name, item.description, item.contact)
                        self.delete_deleted_item_from_db(item.id)
                    except sqlite3.IntegrityError:
                        messagebox.showerror("错误", f"无法恢复物品“{item.name}”，因为名称已存在。")

        self.load_items()
        self.load_recovered_items()
        messagebox.showinfo("恢复成功", "选中的物品已恢复。")

    def permanently_delete_item(self):
        """永久删除选中的物品"""
        selected = self.recovery_tree.selection()
        if not selected:
            messagebox.showwarning("删除错误", "请选择要永久删除的物品！")
            return

        confirm = messagebox.askyesno("确认删除", "你确定要永久删除选中的物品吗？此操作无法撤销。")
        if not confirm:
            return

        for sel in selected:
            item_id = self.recovery_tree.item(sel, 'text')  # 使用Treeview的item ID
            self.delete_deleted_item_from_db(item_id)

        self.load_recovered_items()
        messagebox.showinfo("删除成功", "选中的物品已永久删除。")

    def clear_recovery_bin(self):
        """清空回收站"""
        if not self.deleted_items:
            messagebox.showinfo("清空回收站", "回收站已为空。")
            return

        confirm = messagebox.askyesno("确认清空", "你确定要清空回收站吗？所有物品将被永久删除。")
        if not confirm:
            return

        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM deleted_items')
            conn.commit()

        self.load_recovered_items()
        messagebox.showinfo("清空成功", "回收站已被清空。")

    def load_items(self):
        """加载活跃物品"""
        self.items.clear()
        self.tree.delete(*self.tree.get_children())

        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM items')
            for row in cursor.fetchall():
                item = Item(None, row[0], row[1], row[2])  # items 表中没有 id
                self.items.append(item)
                self.insert_tree(item)

    def load_recovered_items(self):
        """加载回收站物品"""
        self.deleted_items.clear()
        self.recovery_tree.delete(*self.recovery_tree.get_children())

        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM deleted_items')
            for row in cursor.fetchall():
                item = Item(row[0], row[1], row[2], row[3])  # 包含 id
                self.deleted_items.append(item)
                self.insert_recovery_tree(item)

    def insert_tree(self, item):
        """将物品插入到Treeview中"""
        self.tree.insert('', 'end', values=(item.name, item.description, item.contact))

    def insert_recovery_tree(self, item):
        """将回收站物品插入到Treeview中"""
        # 使用item.id作为Treeview的内部ID（text参数）
        self.recovery_tree.insert('', 'end', text=item.id, values=(item.name, item.description, item.contact))

    def search_items(self):
        """在所有字段中搜索物品"""
        keyword = self.search_entry.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        for item in self.items:
            if (keyword in item.name.lower() or
                keyword in item.description.lower() or
                keyword in item.contact.lower()):
                self.insert_tree(item)

    def search_recovered_items(self):
        """在回收站中搜索物品"""
        keyword = self.search_recovery_entry.get().strip().lower()
        self.recovery_tree.delete(*self.recovery_tree.get_children())
        for item in self.deleted_items:
            if (keyword in item.name.lower() or
                keyword in item.description.lower() or
                keyword in item.contact.lower()):
                self.insert_recovery_tree(item)

    def show_all_recovered_items(self):
        """显示回收站中所有物品"""
        self.recovery_tree.delete(*self.recovery_tree.get_children())
        for item in self.deleted_items:
            self.insert_recovery_tree(item)

    def insert_item_to_db(self, name, description, contact):
        """将物品插入到数据库"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO items (name, description, contact) VALUES (?, ?, ?)', (name, description, contact))
            conn.commit()

    def insert_deleted_item_to_db(self, item):
        """将物品插入到回收站数据库"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO deleted_items (name, description, contact) VALUES (?, ?, ?)',
                           (item.name, item.description, item.contact))
            conn.commit()

    def delete_deleted_item_from_db(self, item_id):
        """从回收站数据库中删除物品"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM deleted_items WHERE id = ?', (item_id,))
            conn.commit()

    def delete_item_from_db(self, name):
        """从活跃物品数据库中删除物品"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM items WHERE name = ?', (name,))
            conn.commit()

    def update_item_in_db(self, old_name, name, description, contact):
        """更新数据库中的物品信息"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE items SET name = ?, description = ?, contact = ? WHERE name = ?',
                           (name, description, contact, old_name))
            conn.commit()

    def get_item_from_db(self, name):
        """从数据库中获取物品信息"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM items WHERE name = ?', (name,))
            row = cursor.fetchone()
            return Item(None, row[0], row[1], row[2]) if row else None

    def get_deleted_item_from_db(self, name):
        """从回收站数据库中获取物品信息（通过名称获取最近的一个）"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM deleted_items WHERE name = ? ORDER BY id DESC LIMIT 1', (name,))
            row = cursor.fetchone()
            return Item(row[0], row[1], row[2], row[3]) if row else None

    def get_deleted_item_from_db_by_id(self, item_id):
        """根据 id 从回收站数据库中获取物品信息"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM deleted_items WHERE id = ?', (item_id,))
            row = cursor.fetchone()
            return Item(row[0], row[1], row[2], row[3]) if row else None

    def item_exists(self, name):
        """检查物品是否存在于活跃物品中"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM items WHERE name = ?', (name,))
            exists = cursor.fetchone() is not None
            return exists

    def deleted_item_exists(self, name):
        """检查物品是否存在于回收站中"""
        with sqlite3.connect(DB_FILE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM deleted_items WHERE name = ?', (name,))
            exists = cursor.fetchone() is not None
            return exists

    def clear_entries(self):
        """清空输入框"""
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ItemApp(root)
    root.mainloop()
