import torch
from transformers import (
    BertTokenizer, BertForSequenceClassification,
    Trainer, TrainingArguments, TrainerCallback
)
from datasets import load_dataset
from transformers import DataCollatorWithPadding

# 1. 장비 설정
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print("Using device:", device)

# 2. 데이터셋 로딩
dataset = load_dataset("stanfordnlp/imdb")

# 3. 토크나이저
tokenizer = BertTokenizer.from_pretrained("bert-base-cased")

def tokenize_fn(example):
    return tokenizer(example["text"], truncation=True, padding=False)

tokenized_dataset = dataset.map(tokenize_fn, batched=True)
tokenized_dataset = tokenized_dataset.remove_columns(["text"])
tokenized_dataset.set_format("torch")

# 4. 모델 로딩
model = BertForSequenceClassification.from_pretrained("bert-base-cased", num_labels=2)
model.to(device)

# 5. 데이터 collator
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# 6. 디버깅용 콜백: 에폭마다 출력
class DebugCallback(TrainerCallback):
    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"✅ Epoch {state.epoch} 완료! - loss: {state.log_history[-1].get('loss', 'N/A')}")

# 7. 트레이닝 설정
training_args = TrainingArguments(
    output_dir="./bert-imdb-results",
    logging_dir="./logs",  # TensorBoard 로그 저장 위치
    logging_steps=50,      # 50 step마다 로그 출력
    # evaluation_strategy="epoch",  #evaluation_strategy is deprecated
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_strategy="steps",
    disable_tqdm=False,
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    push_to_hub=False,
    load_best_model_at_end=True,
)

# 8. Trainer 구성
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"].shuffle(seed=42).select(range(2000)),
    eval_dataset=tokenized_dataset["test"].shuffle(seed=42).select(range(1000)),
    tokenizer=tokenizer,    #tokenizer is deprecated and will be removed
    data_collator=data_collator,
    callbacks=[DebugCallback()],
)

# 9. 학습 시작
trainer.train()

# 10. 학습 완료 후 모델 저장
save_path = "./bert-imdb-model"
trainer.save_model(save_path)
tokenizer.save_pretrained(save_path)

print(f"✅ 모델이 '{save_path}' 경로에 저장되었습니다.")