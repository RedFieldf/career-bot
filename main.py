import os
import tweepy
import google.generativeai as genai
import random
import requests
import io

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
    あなたは「戦略的キャリアコーチ（ジリツ運営）」です。
    【対象業界】{industry} の 【テーマ】{topic} について、
    就活生（26卒・27卒・28卒）に向けた有益なツイートを作成してください。

    【ツイート作成のルール】
    1. 攻撃的な言葉は使わず、知的で論理的な「です・ます」調、または落ち着いた「言い切り」にする。
    2. プロだから知っている「ビジネスの本質」や「業界の裏側の面白さ」を語る。
    3. 「業界動向」の場合は、最新トレンド（DX、グローバル、サステナビリティ等）を絡める。
    4. 文字数はハッシュタグ込みで135文字以内。
    5. 最後に必ず #就活 #26卒 #27卒 #28卒 をつける。
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------------------------------------------------
# 5. 画像生成用の「英語の指示」を作る関数
# ---------------------------------------------------------
def generate_image_prompt(industry, tweet_text):
    prompt = f"""
    以下のツイート内容を補完する、抽象的でクールなビジネス画像のプロンプト（指示文）を英語で作成してください。

    【ツイート内容】
    {tweet_text}

    【業界】
    {industry}

    【制約】
- 英語で出力すること。
    - "A bright, clean, photograph-style illustration of..." から始める。（明るく清潔な写真風イラスト）
    - 「温かい自然光(warm natural light streaming through windows)」「現代的で開放的なオフィス(modern open-plan office with plants and wood furniture)」「高揚感のあるポジティブな雰囲気(uplifting and positive atmosphere)」という要素を必ず入れる。
    - 人物は「多様なチームが協力している後ろ姿やシルエット」で表現し、顔は具体的に描かないが、姿勢はポジティブにする。
    - 業界を象徴するアイテム（例：食品なら新鮮な食材、建設なら洗練された模型）を、おしゃれなインテリアの一部として自然に配置する。
    - 出力はプロンプトの英文のみにする。
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------------------------------------------------
# 6. 画像を生成してダウンロードする関数（Pollinations使用）
# ---------------------------------------------------------
def generate_and_download_image(image_prompt):
    # Pollinations.aiという無料APIを使います（登録不要）
    # プロンプトをURLに埋め込むだけで画像が生成されます
    base_url = "https://image.pollinations.ai/prompt/"
    # 日本語などが混じるとエラーになるのでURLエンコード等はrequestsがやってくれますが、念のためシンプルに
    seed = random.randint(0, 10000) # 毎回違う画像にする
    
    # URLを作成 (widthとheightを指定)
    url = f"{base_url}{image_prompt}?width=1080&height=1080&seed={seed}&nologo=true&model=flux"
    
    print(f"画像生成中...: {url}")
    response = requests.get(url)
    
    if response.status_code == 200:
        return io.BytesIO(response.content) # 画像データをメモリ上に保存
    else:
        print("画像生成に失敗しました")
        return None

# ---------------------------------------------------------
# 7. Xに投稿する（画像添付あり）
# ---------------------------------------------------------
def post_with_image(text, image_data):
    # API v1.1 (画像アップロード用)
    auth = tweepy.OAuth1UserHandler(
        X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)

    # API v2 (ツイート投稿用)
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_TOKEN_SECRET
    )

    # ※ここにあった reply_text の定義を削除しました

    try:
        media_id = None
        if image_data:
            # 1. 画像をアップロード (v1.1を使用)
            media = api.media_upload(filename="image.jpg", file=image_data)
            media_id = media.media_id
            print("画像アップロード成功")

        # 2. ツイート投稿 (画像IDを紐付け)
        if media_id:
            response = client.create_tweet(text=text, media_ids=[media_id])
        else:
            response = client.create_tweet(text=text) # 画像なしの場合
            
        tweet_id = response.data['id']
        print(f"メイン投稿成功！ ID: {tweet_id}")

        # ※ここにあった「3. 宣伝リプライ」の処理を削除しました

    except Exception as e:
        print(f"投稿エラー: {e}")

# ---------------------------------------------------------
# メイン処理
# ---------------------------------------------------------
if __name__ == "__main__":
    print("---処理開始---")
    try:
        # 1. ネタ決め
        industry = random.choice(INDUSTRIES)
        topic = random.choice(TOPICS)
        print(f"今日のテーマ: {industry} × {topic}")

        # 2. ツイート文章生成
        tweet_text = generate_tweet_text(industry, topic)
        print("ツイート生成完了")

        # 3. 画像プロンプト生成
        img_prompt = generate_image_prompt(industry, tweet_text)
        print(f"画像指示: {img_prompt}")

        # 4. 画像生成 (無料API)
        image_data = generate_and_download_image(img_prompt)

        # 5. 投稿
        post_with_image(tweet_text, image_data)

    except Exception as e:
        print(f"予期せぬエラー: {e}")
    print("---処理終了---")

