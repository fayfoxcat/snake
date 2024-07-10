# 导入所需的库和模块
import torch
from datasets import load_dataset
from transformers import MarianMTModel, MarianTokenizer, Seq2SeqTrainingArguments, Seq2SeqTrainer, \
    DataCollatorWithPadding

# 指定模型名称，这里使用的是'Helsinki-NLP/opus-mt-en-zh'，是一个英文到中文的预训练模型
model_name = 'Helsinki-NLP/opus-mt-en-zh'

# 通过模型名称加载对应的分词器
tokenizer = MarianTokenizer.from_pretrained(model_name)

# 通过模型名称加载对应的模型
model = MarianMTModel.from_pretrained(model_name)
# 如果有可用的 GPU，将模型移动到 GPU 上
if torch.cuda.is_available():
    model = model.to("cuda")

# 加载opus100数据集的英文到中文的部分
raw_datasets = load_dataset("opus100", "en-zh")


# 定义预处理函数，该函数将输入数据转化为模型可接受的格式
def preprocess(examples):
    # 对于每个样本，提取英文和中文文本
    en_texts = [ex['en'] for ex in examples['translation']]
    zh_texts = [ex['zh'] for ex in examples['translation']]

    # 使用分词器对英文文本进行处理，生成模型的输入数据
    en_inputs = tokenizer(en_texts, max_length=128, truncation=True, padding="max_length", return_tensors="pt")
    # 使用分词器对中文文本进行处理，生成模型的目标输出
    labels = tokenizer(zh_texts, max_length=128, truncation=True, padding="max_length", return_tensors="pt")

    # 为了将数据传递给模型，返回一个字典，包含输入ids，注意力掩码和目标输出
    return {
        "input_ids": en_inputs.input_ids.tolist(),
        "attention_mask": en_inputs.attention_mask.tolist(),
        "labels": labels.input_ids.tolist()
    }


# 应用预处理函数对整个数据集进行处理，生成模型的输入数据和目标输出
tokenized_datasets = raw_datasets.map(preprocess, batched=True, remove_columns=raw_datasets["train"].column_names)

# 设置训练参数
args = Seq2SeqTrainingArguments(
    "test-translation",  # 输出目录，模型和训 练日志将保存到这里
    evaluation_strategy="epoch",  # 评估模型的策略，这里是每一轮结束后进行评估
    learning_rate=2e-5,  # 学习率
    per_device_train_batch_size=1024,  # 每个设备的训练批次大小，提高了批次大小
    per_device_eval_batch_size=1024,  # 每个设备的评估批次大小，提高了批次大小
    weight_decay=0.01,  # 权重衰减率
    save_total_limit=3,  # 最多保存的模型数量
)

# 创建一个 DataCollatorWithPadding 对象，它将在训练过程中动态地将不同长度的序列填充到相同的长度
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# 创建训练器并进行训练
trainer = Seq2SeqTrainer(
    model,  # 使用的模型
    args,  # 训练参数
    train_dataset=tokenized_datasets["train"],  # 训练数据集
    eval_dataset=tokenized_datasets["validation"],  # 评估数据集
    data_collator=data_collator,  # 数据整理器
)

# 开始训练
trainer.train()

# 保存模型和分词器
model_path = "/resources/translation/model"
tokenizer_path = "/resources/translation/tokenizer"

model.save_pretrained(model_path)
tokenizer.save_pretrained(tokenizer_path)
