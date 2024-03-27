from transformers import pipeline

# 指定预定义任务（情感分析）和具体模型（distilbert-base-uncased-finetuned-sst-2-english）修订版本（af0f99b）
classifier = pipeline(task="sentiment-analysis", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student")

results = classifier(["我们非常高兴向您展示🤗Transformers库。", "希望您会喜欢它。"])
for result in results:
    print(f"标签: {result['label']}, 分数: {round(result['score'], 4)}")
