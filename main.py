import os
import tweepy
import google.generativeai as genai
import random

# ---------------------------------------------------------
# 1. 環境変数
# ---------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")

# ---------------------------------------------------------
# 2. ガチャ用データ
# ---------------------------------------------------------
INDUSTRIES = [
    "食品・農林・水産", "建設・住宅・インテリア", "繊維・化学・薬品・化粧品",
    "鉄鋼・金属・鉱業", "機械・プラント", "電子・電気機器",
    "自動車・輸送用機器", "精密・医療機器", "印刷・事務機器関連", "スポーツ・玩具",
    "総合商社", "専門商社",
    "百貨店・スーパー", "コンビニ", "専門店",
    "銀行・証券", "クレジット・信販・リース", "生保・損保",
    "不動産", "鉄道・航空・運輸・物流", "電力・ガス・エネルギー",
    "フードサービス", "ホテル・旅行", "医療・福祉",
    "アミューズメント・レジャー", "コンサルティング・調査", "人材サービス", "教育",
    "ソフトウェア", "インターネット", "通信",
    "放送", "新聞", "出版", "広告",
    "官公庁", "公社・団体"
]

TOPICS = [
    "事業内容（ビジネスモデルの『収益源』を鋭く解説）",
    "最新の業界動向（日経新聞レベルのトレンド・将来性）",
    "仕事内容・職種（現場のリアルと求められる能力）",
    "魅力・やりがい（市場価値やキャリアの広がり）"
]

# ---------------------------------------------------------
# 3. Geminiの設定
# ---------------------------------------------------------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------------------------------------------------
# 4. ツイート本文を作る関数
# ---------------------------------------------------------
def generate_tweet_text(industry, topic):
    prompt = f"""
    あなたは「戦略的キャリアコーチ」です。
    【対象業界】{industry} の 【テーマ】{topic} について、
    就活生（26卒・27卒・28卒）に向けた有益なツイートを作成してください。

    【ツイート作成のルール】
    1. 攻撃的な言葉は使わず、知的で論理的な「です・ます」調、または落ち着いた「言い切り」にする。
    2. プロだから知っている「ビジネスの本質」や「業界の裏側の面白さ」を語る。
    3. 「業界動向」の場合は、最新トレンド（DX、グローバル、サステナビリティ等）を絡める。
    4. 文字数はハッシュタグ込みで135文字以内。
    5. 最後に必ず #就活 #26卒 #27卒 #28卒 をつける。
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini生成エラー: {e}")
        return None
        
# ---------------------------------------------------------
# 5. 投稿関数 (テキストのみ)
# ---------------------------------------------------------
def post_tweet(text):
    if not text:
        return

    # テキスト投稿は Client (API v2) だけでOK
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )

    try:
        response = client.create_tweet(text=text)
        print(f"投稿成功！ ID: {response.data['id']}")
        print(f"内容:\n{text}")
    except Exception as e:
        print(f"投稿エラー: {e}")

# ---------------------------------------------------------
# メイン処理
# ---------------------------------------------------------
if __name__ == "__main__":
    print("---処理開始---")
    
    # ネタ決め
    industry = random.choice(INDUSTRIES)
    topic = random.choice(TOPICS)
    print(f"今日のテーマ: {industry} × {topic}")

    # 生成と投稿
    tweet_text = generate_tweet_text(industry, topic)
    post_tweet(tweet_text)

    print("---処理終了---")
