## 🔥 PyTorch 核心代码块

### 1. 设备配置与模型迁移

```python
import torch

# 自动选择最快硬件加速器 (支持 CUDA / MPS / CPU)
device = (
    "cuda" if torch.cuda.is_available() 
    else "mps" if torch.backends.mps.is_available() 
    else "cpu"
)
print(f"Using device: {device}")

# 将模型与数据迁移至指定设备
# model = MyModel().to(device)
# inputs = inputs.to(device)

```

### 2. 混合精度训练 (AMP) 与显存优化

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)

for inputs, targets in dataloader:
    optimizer.zero_grad()
    inputs, targets = inputs.to(device), targets.to(device)
    
    # 前向传播：自动混合精度（减少显存，加速计算）
    with autocast():
        outputs = model(inputs)
        loss = criterion(outputs, targets)
    
    # 反向传播：梯度缩放
    scaler.scale(loss).backward()
    
    # 梯度裁剪：防止大模型训练时梯度爆炸
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    
    scaler.step(optimizer)
    scaler.update()

```

### 3. 分布式训练初始化 (DDP)

```python
import os
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def setup_ddp(rank, world_size):
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

# 在训练主循环中包装模型
# model = DDP(model.to(rank), device_ids=[rank])

```

---

## 🤗 Hugging Face 核心代码块

### 1. 加载 Tokenizer 与模型（支持量化加速）

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

# 加载分词器
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

# 加载大语言模型（4-bit 量化加载以节省显存）
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",                     # 自动分配多张显卡
    torch_dtype=torch.float16,             # 使用半精度节省显存
    load_in_4bit=True                      # 需要安装 bitsandbytes 库
)

```

### 2. 大模型文本生成推理 (Generation)

```python
messages = [
    {"role": "system", "content": "你是一个人工智能助手。"},
    {"role": "user", "content": "请解释什么是检索增强生成 (RAG)？"}
]

# 结构化输入转换
input_ids = tokenizer.apply_chat_template(
    messages, 
    add_generation_prompt=True, 
    return_tensors="pt"
).to(model.device)

# 文本生成参数配置
outputs = model.generate(
    input_ids,
    max_new_tokens=512,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    eos_token_id=tokenizer.eos_token_id
)

# 解码输出文本
response = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
print(response)

```

### 3. 使用 PEFT (LoRA) 进行大模型高效微调配置

```python
from peft import LoraConfig, get_peft_model, TaskType

# 1. 定义 LoRA 配置参数
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM, 
    inference_mode=False, 
    r=8,                           # LoRA 秩数
    lora_alpha=32,                 # 缩放系数
    lora_dropout=0.1,              # 随机失活率
    target_modules=["q_proj", "v_proj"] # 针对 Transformer 层的注意力机制进行微调
)

# 2. 包装原始模型，使其仅训练少量 LoRA 参数
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()  # 打印可训练参数占比

```

### 4. 使用 Trainer API 快速启动训练

```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,   # 梯度累积，变相放大 Batch Size
    learning_rate=2e-4,
    logging_steps=10,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    fp16=True,                       # 开启半精度训练
    optim="paged_adamw_8bit"         # 优化器显存优化
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8, return_tensors="pt")
)

# 启动微调
trainer.train()

```