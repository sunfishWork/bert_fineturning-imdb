from flask import Flask, request, jsonify
from keybert import KeyBERT
from transformers import AutoTokenizer
import torch

# KeyBERT에 사용할 한국어 모델 로드
model_name = "allenai/scibert_scivocab_uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
kw_model = KeyBERT(model_name)

# 최대 토큰 길이 설정 (BERT 계열은 512)
MAX_TOKENS = 128

app = Flask(__name__)

def split_doc_by_tokens(doc, max_tokens=MAX_TOKENS):
    tokens = tokenizer.tokenize(doc)
    chunks = []

    # 토큰을 max_tokens 개씩 나눔
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = tokenizer.convert_tokens_to_string(chunk_tokens)
        chunks.append(chunk_text.strip())

    return chunks

@app.route("/extract_keywords", methods=["POST"])
def extract_keywords():
    data = request.get_json()

    if not data or 'doc' not in data:
        return jsonify({"error": "Missing 'doc' in request body"}), 400

    doc = data['doc']
    chunks = split_doc_by_tokens(doc)

    all_keywords = []

    for chunk in chunks:
        # print("chunk: ", chunk)
        keywords_with_scores = kw_model.extract_keywords(
            chunk,
            # keyphrase_ngram_range=(1, 1),   # 1~3단어 키워드 후보
            stop_words=None,  # 불용어 제거 안 함 → 더 많은 키워드 후보 유지
            use_maxsum=False,  # 다양성 제약 없음 (많이 뽑는 데 유리)
            use_mmr=False,  # 유사도 다양성 제약 없음
            top_n=32  # 최대한 많이 뽑는다
        )
        filtered = [
            {"keyword": kw, "score": float(score)}
            for kw, score in keywords_with_scores if score >= 0.5
        ]

        all_keywords.extend(filtered)

    # 중복 키워드 제거 (선택)
    seen = set()
    unique_keywords = []
    for kw in all_keywords:
        if kw['keyword'] not in seen:
            unique_keywords.append(kw)
            seen.add(kw['keyword'])

    # 🔽 score를 기준으로 내림차순 정렬
    filtered_sorted = sorted(unique_keywords, key=lambda x: x["score"], reverse=True)

    # 🔽 keyword 값만 추출
    keywords_only = [item["keyword"] for item in filtered_sorted]

    return jsonify({"keywords": keywords_only})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)