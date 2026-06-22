这里是一份为你整理的 Linux 常用基本命令及 Python 环境管理指令的详细用法指南。

---

## 📁 目录与文件操作基础

### 1. `pwd` (Print Working Directory)

* **功能**：显示当前你所在的绝对路径。
* **常见用法**：
* `pwd`：直接输入即可，告诉你“你在哪”。



### 2. `ls` (List)

* **功能**：列出当前目录下的文件和文件夹。
* **常见用法**：
* `ls`：只列出可见文件名称。
* `ls -l`：以列表详细格式显示（包含权限、大小、修改时间等）。
* `ls -a`：显示所有文件，包括以 `.` 开头的隐藏文件。
* `ls -la`：组合技，以详细列表形式显示所有文件。



### 3. `cd` (Change Directory)

* **功能**：切换工作目录。
* **常见用法**：
* `cd 文件夹名`：进入指定的文件夹。
* `cd ..`：返回上一级目录。
* `cd ~` 或 `cd`：直接回到当前用户的家目录（Home 目录）。
* `cd -`：回到上一次所在的目录（类似遥控器的返回键）。



### 4. `mkdir` (Make Directory)

* **功能**：创建新文件夹。
* **常见用法**：
* `mkdir my_folder`：创建一个名为 `my_folder` 的文件夹。
* `mkdir -p path/to/folder`：递归创建多层未存在的文件夹。



---

## 📄 文件增删改查

### 5. `touch`

* **功能**：创建一个空白文件（或者更新已有文件的时间戳）。
* **常见用法**：
* `touch script.py`：创建一个名为 `script.py` 的空 Python 文件。



### 6. `rm` (Remove)

* **功能**：删除文件或文件夹（**注意：Linux 中没有回收站，删了就很难找回！**）。
* **常见用法**：
* `rm file.txt`：删除单个文件。
* `rm -r folder_name`：递归删除整个文件夹及其内部所有内容（`-r` 表示 recursive）。
* `rm -rf folder_name`：强制删除，不进行任何提示（**极度危险，新手慎用**）。



### 7. `cp` (Copy)

* **功能**：复制文件或文件夹。
* **常见用法**：
* `cp file.txt backup.txt`：把 `file.txt` 复制一份并命名为 `backup.txt`。
* `cp -r folder1 folder2`：复制整个文件夹（复制文件夹必须加 `-r`）。



### 8. `mv` (Move)

* **功能**：移动文件/文件夹，或者重命名。
* **常见用法**：
* `mv file.txt /path/to/destination/`：把文件移动到指定路径。
* `mv old_name.txt new_name.txt`：在当前目录下，将文件改名为 `new_name.txt`。



---

## 🔍 查看与检索内容

### 9. `cat` (Concatenate)

* **功能**：一次性查看并打印出文件的全部内容。
* **常见用法**：
* `cat standard.txt`：直接将文件内容刷在终端屏幕上（适合内容少的文件）。



### 10. `less`

* **功能**：分页查看大文件内容（不会一次性加载整张大表，省内存）。
* **操作快捷键**：
* `less large_log.txt`：打开文件。
* `空格键`：向下翻一页；`B` 键：向上翻一页。
* `方向键`：上下逐行滚动。
* `/关键词`：在文件中搜索关键词，按 `n` 查找下一个。
* `Q`：退出查看。



### 11. `grep` (Global Regular Expression Print)

* **功能**：强大的文本搜索工具，用来过滤特定关键词。
* **常见用法**：
* `grep "error" log.txt`：在 `log.txt` 中查找包含 "error" 的所有行。
* `ls -l | grep "txt"`：配合管道符 `|`，筛选当前目录下所有扩展名为 txt 的文件信息。



---

## 🐍 Python 与环境管理

### 12. `python` (或 `python3`)

* **功能**：启动 Python 解释器或执行 Python 脚本。
* **常见用法**：
* `python`：直接输入进入交互式命令行（出现 `>>>`），输入 `exit()` 退出。
* `python script.py`：运行编写好的 Python 脚本文件。



### 13. `pip` (Package Installer for Python)

* **功能**：Python 的官方第三方库包管理器。
* **常见用法**：
* `pip install numpy`：安装第三方库（如 numpy）。
* `pip uninstall numpy`：卸载第三方库。
* `pip list`：查看当前环境下已经安装了哪些库。
* `pip install -r requirements.txt`：根据一键清单批量安装依赖库。



### 14. `conda`

* **功能**：Anaconda / Miniconda 的多环境与包管理工具（常用于深度学习和数据科学，能完美隔离不同项目的 Python 版本和依赖）。
* **常见用法**：
* `conda create -n myenv python=3.10`：创建一个名叫 `myenv` 且 Python 版本为 3.10 的虚拟环境。
* `conda activate myenv`：激活/进入 `myenv` 虚拟环境。
* `conda deactivate`：退出当前虚拟环境，回到基础环境。
* `conda env list`：列出电脑上所有已创建的虚拟环境。
* `conda remove -n myenv --all`：删除整个 `myenv` 环境。