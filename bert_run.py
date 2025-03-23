import torch
from transformers import BertTokenizer, BertForSequenceClassification

# 모델 & 토크나이저 불러오기
model = BertForSequenceClassification.from_pretrained("./bert-imdb-model")
tokenizer = BertTokenizer.from_pretrained("./bert-imdb-model")

# 예측용 입력
inputs = tokenizer("The movie was bad!", return_tensors="pt", truncation=True)

# MPS 또는 CPU 사용
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model.to(device)
inputs = {k: v.to(device) for k, v in inputs.items()}

# 예측 실행
with torch.no_grad():
    outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=1)
x = print("✅ 예측 결과:", "긍정" if prediction.item() == 1 else "부정")

