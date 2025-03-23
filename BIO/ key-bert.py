from keybert import KeyBERT
from transformers import AutoTokenizer
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 모델은 ~/.cache/huggingface/transformers/ 아래에 저장
# 한 번 다운로드되면 이후부터는 로컬에서 로딩되므로 다운로드 메시지는 뜨지 않습니다

# KeyBERT에 사용할 한국어 모델 로드
model_name = "allenai/scibert_scivocab_uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
kw_model = KeyBERT(model_name)

doc = """
How is 5G beneficial for businesses?
Businesses can leverage 5G capabilities to foster innovation and improve customer experience. Here are a few areas worth exploring:

Autonomous Mobility Solutions

In the past, fully autonomous vehicles were not considered feasible because it took too long for vehicles to send and receive information. However, with 5G’s ultra-low latency, self-driving cars can become widespread. Roads can be connected to transmitters and sensors, enabling vehicles to send and receive information within 1/1000 of a second. This time reduction is critical for interpreting visual data (other vehicles, pedestrians, stop signs) with AI and radar technology and controlling the vehicle accordingly.

Smart Factories

5G mobile networks offer manufacturers an opportunity to build hyper-connected smart factories. With IoT support, 5G can seamlessly connect thousands of smart devices like cameras and sensors within factories to automatically collect real-time data. This data can then be analyzed and processed to improve operational efficiency and cost-effectiveness.
For example, smart sensor technology can accurately predict equipment life cycles, inform planning decisions, and anticipate when machine maintenance is needed.

Virtual Reality (VR)

With VR and AR (augmented reality) technologies, digital overlays can be added to the real world via mobile phones, headsets, smart glasses, and other connected devices. VR/AR has numerous use cases including guided maintenance, repair and operations (MRO), workplace training, sales and marketing, and real-time collaboration.
The low latency and high bandwidth of 5G mobile technology will enable more businesses and use cases to adopt VR/AR solutions.

Edge Computing

Edge computing is the process of bringing data storage and processing closer to endpoints. By processing and storing data closer to where it is generated, high-performance applications can deliver intelligent real-time responses with ultra-low latency.
As use cases for edge computing and data demands increase, high-speed networks are essential to meet near-real-time responsiveness. The 5G network infrastructure supports and ensures the increasing complexity and specialization of edge computing.

⸻

How is 5G beneficial for society?
The growth of 5G networks is expected to generate trillions of dollars in economic value and create millions of jobs, while also benefiting many areas of society.

Smart Cities

Smart cities use IoT devices to collect real-time data on traffic, people, and infrastructure. Urban planners can analyze this data to make better decisions, reduce emissions, improve public services, alleviate congestion, and enhance air quality.
The rise of 5G can serve as a catalyst to truly connect major cities around the world.

Healthcare

5G networks can add immense value to healthcare technology. For instance, its low latency enables the sharing of real-time information via HD video, making remote surgery a real possibility.
Wearables and ingestibles are also expected to become more common, providing feedback data to healthcare professionals. With real-time monitoring, more patients will receive personalized care, and doctors will have access to the early signs needed for disease detection.

Environment

5G has the potential to help reduce global emissions. One of the benefits of 5G is its higher transmission efficiency and lower power consumption compared to previous networks. It also supports real-time monitoring of emissions, air quality, water quality, and other environmental indicators.
By enabling efficient resource use and reducing pollutants, 5G can support the development of electric vehicles, smart buildings, smart grids, and remote work—all of which contribute to a healthier planet.

⸻

How does 5G technology work?
Like previous cellular networks, 5G technology uses cell sites to transmit data via radio waves. These sites connect to the network through wireless technology or wired connections.
5G works by modifying how data is encoded and greatly increasing the available radio spectrum for carriers.

OFDM

Orthogonal Frequency-Division Multiplexing (OFDM) is a key part of 5G technology. OFDM is a modulation format that encodes high-frequency radio waves not compatible with 4G. Compared to LTE networks, it reduces latency and increases flexibility.

Smaller Towers

5G technology uses small transmitters installed on buildings and other infrastructure, unlike 4G and previous cellular technologies that relied on standalone mobile towers.
With small cell sites running the network, 5G will be able to support more devices at exceptional speeds.

Network Slicing

Mobile network operators can use 5G technology to deploy multiple independent virtual networks over the same infrastructure.
Each network slice can be customized for different services or business cases such as streaming services or enterprise tasks. By creating collections of 5G network features tailored to specific use cases or business models, it’s possible to support the diverse requirements of all vertical industries.
This separation of services can deliver more reliable user experiences and improve device efficiency."""

# model = KeyBERT("beomi/kcbert-base")   # 한국어 모델을 사용하게 되면, 영어만 있는 경우 추출 정확도가 떨어진다.
# doc = "5G란 무엇인가요? 5G는 5세대 무선 셀룰러 기술로, 이전 네트워크보다 높은 업로드 및 다운로드 속도, 보다 일관된 연결, 개선된 용량을 제공합니다."

# 최대 토큰 길이 설정 (BERT 계열은 512)
MAX_TOKENS = 128

def split_doc_by_tokens(doc, max_tokens=MAX_TOKENS):
    tokens = tokenizer.tokenize(doc)
    chunks = []

    # 토큰을 max_tokens 개씩 나눔
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = tokenizer.convert_tokens_to_string(chunk_tokens)
        chunks.append(chunk_text.strip())

    return chunks

chunks = split_doc_by_tokens(doc)
for chunk in chunks:
    print("chunk: ", chunk)
    keywords_with_scores = kw_model.extract_keywords(
        chunk,
        # keyphrase_ngram_range=(1, 1),   # 1~3단어 키워드 후보
        stop_words=None,                # 불용어 제거 안 함 → 더 많은 키워드 후보 유지
        use_maxsum=False,  # 다양성 제약 없음 (많이 뽑는 데 유리)
        use_mmr=False,  # 유사도 다양성 제약 없음
        top_n=64  # 최대한 많이 뽑는다
    )
    filtered = [
        {"keyword": kw, "score": float(score)}
        for kw, score in keywords_with_scores if score >= 0.5
    ]
    # filtered = [kw for kw, score in keywords_with_scores if score >= 0.5
    # ]
    # print("filtered: ", filtered)

    # 중복 키워드 제거 (선택)
    seen = set()
    unique_keywords = []
    for kw in filtered:
        if kw['keyword'] not in seen:
            unique_keywords.append(kw["keyword"])
            seen.add(kw['keyword'])
    print("unique_keywords: ", unique_keywords)



# keywords = model.extract_keywords(doc, top_n=5)
# keywords_with_scores = model.extract_keywords(doc)
# keywords_with_scores = model.extract_keywords(doc, use_maxsum=False, use_mmr=False)
# keywords_with_scores = model.extract_keywords(doc, use_maxsum=False, use_mmr=True, diversity=0.9)

# filtered_keywords = [kw for kw, score in unique_keywords if score > 0.5]
# print(filtered_keywords)