"""
图形界面模块
使用tkinter创建简洁的配置界面
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from hotkey_manager import HotkeyManager
from power_manager import PowerManager
from config_manager import ConfigManager
from logger import Logger


class HotkeyManagerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("快捷键启动工具")
        self.root.geometry("700x500")

        self.hotkey_manager = HotkeyManager()
        self.power_manager = PowerManager()
        self.config_manager = ConfigManager()
        self.logger = Logger()

        self.is_monitoring = False
        self._setup_ui()
        self._load_config()

        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self):
        """设置界面"""
        # 顶部控制面板
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(control_frame, text="启动监听", command=self._toggle_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(control_frame, text="状态: 未启动", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=20)

        self.process_label = ttk.Label(control_frame, text="运行中程序: 0")
        self.process_label.pack(side=tk.LEFT, padx=20)

        # 快捷键列表
        list_frame = ttk.LabelFrame(self.root, text="快捷键配置", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建表格
        columns = ("快捷键", "目标路径")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.tree.heading("快捷键", text="快捷键")
        self.tree.heading("目标路径", text="目标路径")
        self.tree.column("快捷键", width=150)
        self.tree.column("目标路径", width=500)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 添加快捷键面板
        add_frame = ttk.LabelFrame(self.root, text="添加快捷键", padding="10")
        add_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(add_frame, text="快捷键:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.hotkey_entry = ttk.Entry(add_frame, width=30)
        self.hotkey_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(add_frame, text="(例: Ctrl+A)").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        ttk.Label(add_frame, text="目标路径:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.path_entry = ttk.Entry(add_frame, width=50)
        self.path_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(add_frame, text="浏览文件", command=self._browse_file).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(add_frame, text="浏览文件夹", command=self._browse_folder).grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="(支持: 程序、网页URL、文件夹等)").grid(row=2, column=1, padx=5, pady=0, sticky=tk.W)

        button_frame = ttk.Frame(add_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="添加", command=self._add_hotkey).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除选中", command=self._remove_hotkey).pack(side=tk.LEFT, padx=5)

    def _load_config(self):
        """加载配置"""
        hotkeys = self.config_manager.get_hotkeys()
        for hotkey, path in hotkeys.items():
            self.tree.insert("", tk.END, values=(hotkey, path))
            self.hotkey_manager.add_hotkey(hotkey, path)

    def _browse_file(self):
        """浏览文件"""
        filename = filedialog.askopenfilename(
            title="选择目标",
            filetypes=[
                ("所有文件", "*.*"),
                ("可执行文件", "*.exe"),
                ("批处理文件", "*.bat;*.cmd"),
                ("快捷方式", "*.lnk")
            ]
        )
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)

    def _browse_folder(self):
        """浏览文件夹"""
        foldername = filedialog.askdirectory(
            title="选择文件夹"
        )
        if foldername:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, foldername)

    def _add_hotkey(self):
        """添加快捷键"""
        hotkey = self.hotkey_entry.get().strip()
        path = self.path_entry.get().strip()

        # 输入验证
        if not hotkey or not path:
            messagebox.showwarning("输入不完整", "请填写快捷键和目标路径")
            return

        # 验证快捷键格式
        if not self._validate_hotkey_format(hotkey):
            messagebox.showerror(
                "快捷键格式错误",
                f"快捷键格式不正确: '{hotkey}'\n\n"
                "正确格式示例:\n"
                "• ctrl+alt+n\n"
                "• ctrl+shift+t\n"
                "• win+e\n\n"
                "注意：必须包含至少一个修饰键（ctrl、alt、shift、win）"
            )
            return

        # 验证目标路径
        if not path.startswith(('http://', 'https://', 'www.')):
            # 不是 URL，检查文件或文件夹是否存在
            import os
            if not os.path.exists(path):
                messagebox.showerror(
                    "目标不存在",
                    f"指定的目标不存在:\n{path}\n\n请检查路径是否正确"
                )
                return

        # 检查快捷键冲突
        existing_hotkeys = self.config_manager.get_hotkeys()
        if hotkey.lower() in [k.lower() for k in existing_hotkeys.keys()]:
            result = messagebox.askyesno(
                "快捷键冲突",
                f"快捷键 '{hotkey}' 已存在\n\n是否覆盖现有配置？"
            )
            if not result:
                return
            # 移除旧配置
            for old_key in list(existing_hotkeys.keys()):
                if old_key.lower() == hotkey.lower():
                    self.hotkey_manager.remove_hotkey(old_key)
                    self.config_manager.remove_hotkey(old_key)
                    # 从树视图中移除
                    for item in self.tree.get_children():
                        if self.tree.item(item, "values")[0].lower() == hotkey.lower():
                            self.tree.delete(item)
                            break

        # 添加快捷键
        if self.hotkey_manager.add_hotkey(hotkey, path):
            self.config_manager.add_hotkey(hotkey, path)
            self.tree.insert("", tk.END, values=(hotkey, path))

            # 如果正在监听，重新注册快捷键
            if self.is_monitoring:
                self.hotkey_manager.stop()
                self.hotkey_manager.start()

            self.hotkey_entry.delete(0, tk.END)
            self.path_entry.delete(0, tk.END)
            messagebox.showinfo("添加成功", f"快捷键 '{hotkey}' 已成功添加")
            self.logger.info(f"用户添加快捷键: {hotkey} -> {path}")
        else:
            messagebox.showerror(
                "添加失败",
                f"无法添加快捷键 '{hotkey}'\n\n可能原因:\n"
                "• 快捷键格式不正确\n"
                "• 系统资源不足\n"
                "• 快捷键已被其他程序占用"
            )
            self.logger.error(f"添加快捷键失败: {hotkey} -> {path}")

    def _validate_hotkey_format(self, hotkey):
        """验证快捷键格式"""
        if not hotkey:
            return False

        # 转换为小写进行验证
        hotkey_lower = hotkey.lower()

        # 检查是否包含修饰键
        modifiers = ['ctrl', 'alt', 'shift', 'win']
        has_modifier = any(mod in hotkey_lower for mod in modifiers)

        if not has_modifier:
            return False

        # 检查是否使用加号连接
        if '+' not in hotkey:
            return False

        return True

    def _remove_hotkey(self):
        """删除快捷键"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("未选择项目", "请先选择要删除的快捷键")
            return

        # 确认删除
        if len(selected) == 1:
            values = self.tree.item(selected[0], "values")
            hotkey = values[0]
            result = messagebox.askyesno(
                "确认删除",
                f"确定要删除快捷键 '{hotkey}' 吗？"
            )
        else:
            result = messagebox.askyesno(
                "确认删除",
                f"确定要删除选中的 {len(selected)} 个快捷键吗？"
            )

        if not result:
            return

        deleted_count = 0
        for item in selected:
            values = self.tree.item(item, "values")
            hotkey = values[0]

            self.hotkey_manager.remove_hotkey(hotkey)
            self.config_manager.remove_hotkey(hotkey)
            self.tree.delete(item)
            deleted_count += 1
            self.logger.info(f"用户删除快捷键: {hotkey}")

        if deleted_count == 1:
            messagebox.showinfo("删除成功", "快捷键已成功删除")
        else:
            messagebox.showinfo("删除成功", f"已成功删除 {deleted_count} 个快捷键")

    def _toggle_monitoring(self):
        """切换监听状态"""
        if not self.is_monitoring:
            # 检查是否有配置的快捷键
            if len(self.config_manager.get_hotkeys()) == 0:
                messagebox.showwarning(
                    "无快捷键配置",
                    "请先添加至少一个快捷键配置后再启动监听"
                )
                return

            try:
                self.hotkey_manager.start()
                self.is_monitoring = True
                self.start_btn.config(text="停止监听")
                self.status_label.config(text="状态: 运行中", foreground="green")
                self.logger.info("快捷键监听已启动")

                # 启动状态更新线程
                threading.Thread(target=self._update_status, daemon=True).start()

                messagebox.showinfo("启动成功", "快捷键监听已启动\n\n现在可以使用配置的快捷键启动程序")
            except Exception as e:
                messagebox.showerror(
                    "启动失败",
                    f"无法启动快捷键监听\n\n错误信息: {str(e)}"
                )
                self.logger.error(f"启动监听失败: {str(e)}")
        else:
            try:
                self.hotkey_manager.stop()
                self.power_manager.allow_sleep()
                self.is_monitoring = False
                self.start_btn.config(text="启动监听")
                self.status_label.config(text="状态: 已停止", foreground="red")
                self.process_label.config(text="运行中程序: 0")
                self.logger.info("快捷键监听已停止")

                messagebox.showinfo("停止成功", "快捷键监听已停止")
            except Exception as e:
                messagebox.showerror(
                    "停止失败",
                    f"无法停止快捷键监听\n\n错误信息: {str(e)}"
                )
                self.logger.error(f"停止监听失败: {str(e)}")

    def _update_status(self):
        """更新状态显示"""
        while self.is_monitoring:
            count = self.hotkey_manager.get_running_count()
            self.process_label.config(text=f"运行中程序: {count}")

            # 根据运行程序数量控制防休眠
            if count > 0:
                self.power_manager.prevent_sleep()
            else:
                self.power_manager.allow_sleep()

            time.sleep(2)

    def _on_closing(self):
        """关闭窗口"""
        self.logger.info("窗口关闭事件触发，开始清理资源")

        if self.is_monitoring:
            self.logger.info("停止快捷键监听")
            self.hotkey_manager.stop()
            self.is_monitoring = False

        self.logger.info("恢复系统休眠功能")
        self.power_manager.allow_sleep()

        self.logger.info("销毁GUI窗口")
        self.root.destroy()

        self.logger.info("资源清理完成")

    def run(self):
        """运行程序"""
        self.logger.info("程序启动")
        self.root.mainloop()
