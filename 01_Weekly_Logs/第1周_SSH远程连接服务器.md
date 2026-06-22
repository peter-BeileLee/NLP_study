在进行 NLP 大模型训练（如微调 LLaMA、BERT 等）时，**SSH、Tmux 和 SCP** 是最核心的“三板斧”。

简单来说：**SSH 让你进入服务器，Tmux 保证训练不因网络断开而中断，SCP 负责在你的电脑和服务器之间传输模型和数据集。**

---

## 一、 SSH：连接远程 GPU 服务器

### 1. 实际应用场景

训练大模型需要昂贵的显卡（如 A100、H100），通常托管在远程机房。你必须通过 SSH（Secure Shell）远程登录到服务器的命令行终端来进行所有操作。

### 2. 核心指令速查

* **基础连接：**
```bash
ssh username@remote_ip
#username:务器操作系统中的“用户名”（账户名）
#若果用的是root管理员，则需要密码：
```


*(例：`ssh root@119.23.45.67`。首次连接输入 `yes`，然后输入密码，密码输入时屏幕不显示)*
* **指定非常规端口连接（很多云服务器会修改默认的 22 端口）：**
```bash
ssh -p port_number username@remote_ip
```


*(例：`ssh -p 25532 root@119.23.45.67`)*
* **配置免密快捷登录（高频选修）：**
在本地电脑生成密钥对并发送给服务器，以后输入 `ssh gpu_server` 即可一键登录，无需密码。
```bash
ssh-keygen -t rsa  # 本地生成密钥（一路回车）
ssh-copy-id -p port_number username@remote_ip  # 把公钥发给服务器
```



---

## 二、 Tmux：终端复用器（大模型训练的“免死金牌”）

### 1. 实际应用场景

大模型训练短则几小时，长则数天。如果直接在 SSH 窗口运行训练脚本，**一旦你的电脑休眠、断网或学校 Wi-Fi 闪断，SSH 连接就会断开，训练任务会立即崩溃（前功尽弃）**。

**Tmux 的作用**：在服务器后台开辟一个独立的空间。即使你关闭本地电脑，服务器上的训练程序依然在安全地跑着。

### 2. 核心指令速查

> ⚠️ **注意：** Tmux 里的所有快捷键，都需要先按 `Ctrl + B`（称为前缀键），松开后，再按具体的字母。

#### ① 系统命令行指令（在未进入或已退出 Tmux 时使用）

* **新建一个专门跑大模型训练的会话：**
```bash
tmux new -s train_llama
```


* **查看当前服务器后台运行的所有会话：**
```bash
tmux ls
```


* **重新进入（接管）之前的训练会话：**
```bash
tmux a -t train_llama
```


* **彻底杀死并销毁某个会话：**
```bash
tmux kill-session -t train_llama
```



#### ② 会话内部快捷键（已在 Tmux 窗口内使用）

* **安全离开（Detached）**：让训练在后台跑，自己退出黑弹窗。
* 快捷键：先按 `Ctrl + B`，松开后按 `D`。


* **上下分屏**：一边看 GPU 占用，一边看训练日志。
* 快捷键：先按 `Ctrl + B`，松开后按 `"` (双引号)。


* **左右分屏**：
* 快捷键：先按 `Ctrl + B`，松开后按 `%` (百分号)。


* **在分屏间切换光标**：
* 快捷键：先按 `Ctrl + B`，松开后按 `方向键`。



---

## 三、 SCP：跨物理机文件传输

### 1. 实际应用场景

在大模型训练前，你需要把本地下载好的数据集（如 JSON 文本）**上传到服务器；训练结束后，你需要把保存的**模型权重（如 Checkpoint 文件夹）下载到本地进行部署。

### 2. 核心指令速查

> ⚠️ **关键逻辑：** 执行 scp 命令时，**一律在你的本地电脑终端执行**，不要在远程服务器的 SSH 窗口里执行！

* **上传本地数据集到服务器：**
```bash
scp -P port_number C:\Users\path\dataset.json username@remote_ip:/home/root/data/
```


* **上传整个模型文件夹（必须加 `-r` 参数，表示递归复制）：**
```bash
scp -P port_number -r C:\Users\path\my_model_folder username@remote_ip:/home/root/models/
```


* **从服务器下载训练好的模型权重到本地：**
```bash
scp -P port_number -r username@remote_ip:/home/root/models/checkpoint-1000 D:\NLP_Projects\
```



---

## 🚀 大模型训练的完整实战流水线（黄金标准演练）

当你拿到租好的服务器，准备训练一个 NLP 大模型时，标准的保姆级操作顺序如下：

### 第一步：本地传数据

在本地电脑终端，把清洗好的文本数据集上传到服务器：

```bash
scp -P 25532 -r ./dataset root@119.23.45.67:/root/workspace/
```

### 第二步：SSH 登录

```bash
ssh -p 25532 root@119.23.45.67
```

### 第三步：用 Tmux 盖后台护盾

登录成功后，立刻创建一个叫 `nlp` 的安全后台环境：

```bash
tmux new -s nlp
```

### 第四步：激活 Conda 并启动训练

此时你已经在 Tmux 里面了。

```bash
conda activate my_project_env
python fine_tune_llama.py --data_path ./dataset
```

*(代码开始滚屏， loss 开始下降...)*

### 第五步：分屏监控显存

按下 `Ctrl + B` 再按 `"`，终端下半部分被切开。在下半部分输入：

```bash
nvidia-smi -l 1
```

*(此时你可以实时看到显卡有没有吃满，显存有没有 OOM 爆掉)*

### 第六步：安心睡觉

确认训练正常后，按下 `Ctrl + B` 再按 `D`。
成功安全退出 Tmux！此时你可以直接关闭 SSH 窗口，合上笔记本电脑去睡觉。服务器在远端机房会不知疲倦地持续训练。

### 第七步：次日查看与收尾

第二天早上，打开电脑，重新 SSH 连上服务器。
输入：

```bash
tmux a -t nlp
```

瞬间回到昨晚的训练现场。如果看到训练完成，在本地电脑用 `scp` 把训练好的权重下载回来即可。