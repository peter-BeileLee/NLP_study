## 🌐 Conda 环境管理

| 指令 | 功能描述 |
| --- | --- |
| `conda create -n <env_name> python=<version>` | 创建指定 Python 版本的虚拟环境 |
| `conda activate <env_name>` | 激活/进入指定虚拟环境 |
| `conda deactivate` | 退出当前虚拟环境 |
| `conda env list` 或 `conda info --envs` | 查看本地所有已创建的虚拟环境 |
| `conda remove -n <env_name> --all` | 删除指定虚拟环境及其全部安装包 |
| `conda create -n <new_env> --clone <old_env>` | 复制/克隆现有的虚拟环境 |

---

## 📦 库与依赖包管理

* **在当前环境安装包**：`conda install <package_name>`
* **在当前环境卸载包**：`conda remove <package_name>`
* **更新指定的包**：`conda update <package_name>`
* **查看当前环境已安装的包**：`conda list`
* **搜索可用的包版本**：`conda search <package_name>`
* **清理缓存以释放磁盘空间**：`conda clean --all`

---

## 💾 环境导出与导入（跨设备迁移）

* **导出当前环境到配置文件 (`.yml`)**：
```bash
conda env export > environment.yml

```


* **依据配置文件导入并创建新环境**：
```bash
conda env create -f environment.yml

```



---

## ⚙️ 镜像源配置（加速下载）

* **添加清华大学 TUNA 镜像源**：
```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes

```


* **查看当前配置的镜像源**：`conda config --show channels`
* **恢复默认官方下载源**：`conda config --remove-key channels`