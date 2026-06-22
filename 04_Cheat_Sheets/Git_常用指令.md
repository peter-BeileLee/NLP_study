## ⚙️ 代码提交与同步

| 快捷键/指令 | 功能描述 |
| --- | --- |
| `git init` | 在当前目录初始化一个新的 Git 本地仓库 |
| `git clone <url>` | 克隆远程仓库到本地 |
| `git status` | 查看当前工作区和暂存区的状态 |
| `git add <file>` | 将指定文件添加到暂存区（`git add .` 表示添加所有修改） |
| `git commit -m "msg"` | 将暂存区的内容提交到本地仓库，并添加提交信息 |
| `git push` | 将本地分支的修改推送到远程仓库 |
| `git pull` | 拉取远程仓库的最新代码并直接合并到本地 |
| `git fetch` | 从远程仓库获取最新版本，但不自动合并 |

---

## 🌿 分支管理

* **查看所有本地分支**：`git branch`
* **查看所有远程和本地分支**：`git branch -a`
* **创建新分支**：`git branch <branch_name>`
* **切换分支**：`git checkout <branch_name>`（新版 Git 推荐：`git switch <branch_name>`）
* **创建并切换到新分支**：`git checkout -b <branch_name>`（新版 Git: `git switch -c <branch_name>`）
* **合并分支**：`git merge <branch_name>`（将指定分支合并到当前分支）
* **删除本地分支**：`git branch -d <branch_name>`

---

## 🔍 历史与撤销

* **查看提交日志**：`git log`
* **以简洁的一行形式查看日志**：`git log --oneline`
* **查看特定文件的修改差异**：`git diff <file>`
* **撤销工作区文件的修改**：`git checkout -- <file>`（恢复到上次提交的状态）
* **取消暂存区的文件**：`git reset HEAD <file>`
* **版本回退**：`git reset --hard <commit_id>`（强制回退到指定的提交版本，慎用）