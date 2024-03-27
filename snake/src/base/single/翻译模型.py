# 导入所需的库
from transformers import MarianMTModel, MarianTokenizer

# 定义源语言和目标语言
src_lang = 'en'
trg_lang = 'zh'

# 加载适当的预训练模型和分词器
model_name = f'Helsinki-NLP/opus-mt-{src_lang}-{trg_lang}'
model = MarianMTModel.from_pretrained(model_name)
tokenizer = MarianTokenizer.from_pretrained(model_name)

# 定义翻译函数
def translate(text: str) -> str:
    """将给定的文本从源语言翻译为目标语言"""
    # 对文本进行编码
    inputs = tokenizer.encode(text, return_tensors='pt')
    # 进行翻译
    outputs = model.generate(inputs, max_length=500)
    # 将输出的张量转换为文本
    translated_text = tokenizer.decode(outputs[0])
    return translated_text

# 测试翻译函数
text = "em1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500"
translated_text = translate(text)
print(translated_text)