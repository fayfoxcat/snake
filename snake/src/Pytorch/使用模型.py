from transformers import MarianMTModel, MarianTokenizer

model_path = "../resources/translation/model"
tokenizer_path = "../resources/translation/tokenizer"

# 通过模型名称加载对应的模型
model = MarianMTModel.from_pretrained(model_path)
# 通过模型名称加载对应的分词器
tokenizer = MarianTokenizer.from_pretrained(tokenizer_path)

# 将你要翻译的句子进行分词处理
inputs = tokenizer("Seventeen-first session", return_tensors="pt")

# 使用模型进行预测
outputs = model.generate(**inputs)

# 使用分词器将模型输出的 token ID 转换回文本
translated_sentence = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(translated_sentence)