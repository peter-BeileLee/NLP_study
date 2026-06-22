# NLP 大模型训练必备：SSH / Tmux / SCP 完全指南（含底层原理）

在进行 NLP 大模型训练（如微调 LLaMA、BERT 等）时，**SSH、Tmux 和 SCP** 是最核心的“三板斧”。

简单来说：  
**SSH 让你进入服务器，Tmux 保证训练不因网络断开而中断，SCP 负责在你的电脑和服务器之间传输模型和数据集。**

---

## 一、SSH：连接远程 GPU 服务器（含底层机制）

### 1. 实际应用场景

训练大模型需要昂贵的显卡（如 A100、H100），通常托管在远程机房。  
你必须通过 **SSH（Secure Shell）** 远程登录到服务器的命令行终端进行操作。

---

### 2. SSH 连接时，服务器内部发生了什么？（重点）

当你在本地执行：

```bash
ssh username@remote_ip
```

远程服务器内部会精确发生以下步骤：

1. **sshd（主守护进程）监听端口 22**
   - 常驻后台，等待连接
2. **sshd fork 出子进程**
   - 每个 SSH 登录 = 一个独立的 `sshd(子)`
3. **sshd(子) 向内核申请 PTY（伪终端）**
   - PTY 由一对组成：
     - **PTY Master**：由 `sshd(子)` 持有（网络侧）
     - **PTY Slave**：交给 bash（终端侧）
4. **sshd(子) fork + exec → bash**
   - bash 的 stdin/stdout/stderr 重定向到 PTY Slave
5. **TCP 加密通道建立**
   - 本地键盘 → sshd(子) → PTY → bash
   - bash 输出 → PTY → sshd(子) → 本地屏幕

👉 **此时：bash 的生死完全绑定在 sshd(子) 上**

---

### 3. 为什么 SSH 断网会导致训练中断？

当 SSH 断开（断网 / 休眠 / exit）：

1. TCP 连接关闭
2. `sshd(子)` 退出
3. **PTY Master 被关闭**
4. 内核判定：控制终端丢失
5. 向 **会话首进程（bash）** 发送 **SIGHUP**
6. bash 终止，并向前台进程组转发 SIGHUP
7. 训练进程（python）随之终止
8. PTY 被内核回收

✅ **这就是为什么普通 SSH 里跑训练，一断网就全没了**

---

### 4. 核心指令速查

* **基础连接：**
```bash
ssh username@remote_ip
```

* **指定端口：**
```bash
ssh -p port_number username@remote_ip
```

* **免密登录（强烈推荐）：**
```bash
ssh-keygen -t rsa
ssh-copy-id -p port_number username@remote_ip
```

---

## 二、Tmux：终端复用器（训练“免死金牌”）

### 1. 实际应用场景

大模型训练往往持续数小时甚至数天。  
**Tmux 的作用：在服务器后台创建一个“独立房间”，即使 SSH 断开，训练仍在房间内继续运行。**

---

### 2. Tmux 是如何解决 SSH 断网问题的？（核心原理）

当你在 SSH 里执行：

```bash
tmux new -s train_llama
```

服务器内部发生的是：

1. **bash fork → exec → tmux client**
2. **tmux client fork → tmux server**
3. **tmux server：**
   - 被 `systemd/init` 收养（PPID = 1）
   - **不再依赖 sshd(子)**
4. **tmux server 自己申请 PTY**
   - 新建 PTY（Master/Slave）
   - 启动 bash'（tmux 内 bash）
5. **tmux client：**
   - 通过 Unix Socket 连接 tmux server
   - 作为 sshd(子) 与 tmux server 之间的桥梁

👉 **训练进程挂在 tmux server 的 PTY 下，而不是 sshd(子) 的 PTY 下**

---

### 3. 为什么 SSH 断开后 Tmux 不死？

| 组件 | SSH 断开时 |
|---|---|
| sshd(子) | 退出 |
| SSH PTY | 回收 |
| tmux client | 退出 |
| tmux server | ✅ 存活 |
| tmux PTY | ✅ 存活 |
| bash' | ✅ 存活 |
| python | ✅ 存活 |

原因：
- tmux server 的父进程是 `systemd`
- tmux PTY 仍被 tmux server 打开
- 内核 **不会发送 SIGHUP**

---

### 4. 核心指令速查

#### ① 系统命令行（未进入 Tmux）

* **新建会话：**
```bash
tmux new -s train_llama
```

* **查看会话：**
```bash
tmux ls
```

* **重新接入：**
```bash
tmux a -t train_llama
```

* **彻底销毁：**
```bash
tmux kill-session -t train_llama
```

---

#### ② 会话内快捷键

| 功能 | 快捷键 |
|---|---|
| 安全脱离（后台跑） | `Ctrl+B` → `D` |
| 上下分屏 | `Ctrl+B` → `"` |
| 左右分屏 | `Ctrl+B` → `%` |
| 切换分屏 | `Ctrl+B` → 方向键 |

---

## 三、SCP：跨机器文件传输

### 1. 实际应用场景

SCP 解决的是：  
**“代码和数据在本地，但训练在远程 GPU 上”**

- 上传：数据集 / 训练脚本
- 下载：模型权重 / 日志

---

### 2. 为什么不能用 SSH 直接跑文件？

SSH 只能：
- 执行远程命令
- 传输终端 IO

**SSH 不能：**
- 把本地文件“变”到远程磁盘
- 让远程 bash 直接读取本地文件内容

👉 **SCP 的作用：把文件完整地复制到远程磁盘，再由 SSH 执行**

---

### 3. 核心指令速查

> ⚠️ 以下命令 **一律在本地终端执行**

* **上传文件：**
```bash
scp -P port_number local_file username@remote_ip:/remote/path/
```

* **上传目录（递归）：**
```bash
scp -P port_number -r local_dir username@remote_ip:/remote/path/
```

* **下载模型：**
```bash
scp -P port_number -r username@remote_ip:/remote/model ./local_dir/
```

---

## 🚀 大模型训练完整实战流水线（黄金标准）

### 第一步：本地传数据

```bash
scp -P 25532 -r ./dataset root@119.23.45.67:/root/workspace/
```

---

### 第二步：SSH 登录

```bash
ssh -p 25532 root@119.23.45.67
```

---

### 第三步：Tmux 护盾

```bash
tmux new -s nlp
```

---

### 第四步：启动训练

```bash
conda activate my_env
python fine_tune_llama.py --data_path ./dataset
```

---

### 第五步：分屏监控

`Ctrl+B` → `"`

```bash
nvidia-smi -l 1
```

---

### 第六步：安心睡觉

`Ctrl+B` → `D`  
关闭电脑 ✅ 训练继续

---

### 第七步：次日收尾

```bash
tmux a -t nlp
```

训练完成 → `scp` 下载模型 ✅

---

## 四、一句话终极总结（给未来的你）

> **SSH 提供远程登录与 PTY，sshd(子) 的 PTY 决定了训练是否脆弱；  
> Tmux 通过独立 tmux server 和 PTY 解耦 SSH，让训练在断网后存活；  
> SCP 负责把代码和数据送到远程磁盘，SSH 只负责发令执行。**

---

## 五、实践与纠错（本地沙箱全流程）

> **目标**：在 Windows 上利用 WSL2 + Docker 构建 100% 安全的本地“虚拟服务器”，复现上述所有操作。

### 1. 环境搭建与初始化

#### ① 安装 WSL2 与 Ubuntu
在 **PowerShell (管理员)** 中执行：
```powershell
wsl --update
wsl --set-default-version 2
wsl --install -d Ubuntu
```
*注：安装完成后必须重启电脑。首次打开 Ubuntu 需设置用户名和密码。*

#### ② 安装 Docker Desktop
- 下载并安装 Docker Desktop。
- **关键配置**：Settings → General → 勾选 `Use the WSL 2 based engine`。
- **关键配置**：Settings → Resources → WSL Integration → 勾选 `Ubuntu` → Apply & Restart。

#### ③ 验证 Docker 权限（常见坑）
在 **Ubuntu 终端** 执行：
```bash
docker run hello-world
```
*如果遇到 `permission denied`：*
```bash
sudo usermod -aG docker $USER
```
**必须关闭 Ubuntu 终端并重新打开**，再次验证。

---

### 2. 创建“虚拟服务器”容器

在 **Ubuntu 终端** 执行：

```bash
docker run -d \
  --name practice-vm \
  -p 127.0.0.1:2222:22 \
  --memory=512m \
  --cpus=1 \
  ubuntu:22.04 \
  tail -f /dev/null
```

---

### 3. 配置容器内的 SSH 服务

进入容器并安装环境：
```bash
docker exec -it practice-vm bash
```

*（以下命令均在容器内部执行）*
```bash
apt update && apt upgrade -y
apt install -y openssh-server tmux vim sudo net-tools iputils-ping

mkdir -p /var/run/sshd
echo 'root:123456' | chpasswd

sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

service ssh start
exit
```

---

### 4. 连接与传输测试

#### ① SSH 登录（Windows PowerShell 执行）
```powershell
ssh -p 2222 root@localhost
```

#### ② SCP 文件传输（Windows PowerShell 执行）
```powershell
# 上传
scp -P 2222 C:\Users\BeileLee\Desktop\test.txt root@localhost:/tmp/
# 下载
scp -P 2222 root@localhost:/tmp/test.txt C:\Users\BeileLee\Desktop\
```

#### ③ Tmux 后台训练演示
```bash
tmux new -s test
ping 8.8.8.8
# 按 Ctrl+B 然后 D 脱离
```

---

### 5. 常见问题与解决方案（Troubleshooting）

| 问题描述 | 原因 | 解决方案 |
|---|---|---|
| Docker Desktop 图标不变绿 | WSL2 集成未生效或 Windows 虚拟化未开 | 检查 BIOS 虚拟化是否开启；Docker Settings 中确认 WSL2 勾选。 |
| `Ctrl+V` 粘贴导致 tmux 异常 | tmux 中 `Ctrl+V` 不是粘贴键 | 使用 **右键粘贴** 或 **Shift+Insert**。 |
| tmux 里看不到光标/界面混乱 | 进入了特殊视图或被遮挡 | 按 `Ctrl+B` 然后 `D` 脱离，执行 `tmux kill-session -t test` 清理，重新新建。 |
| SSH 提示指纹未知 | 首次连接的安全确认 | 输入 `yes` 回车即可。 |
| 忘记容器密码/进不去 | 配置错误 | 在 Ubuntu 终端执行 `docker rm -f practice-vm`，重新从第 2 步开始。 |

---

### 6. 环境清理（练完即焚）

```bash
docker stop practice-vm
docker rm practice-vm
```