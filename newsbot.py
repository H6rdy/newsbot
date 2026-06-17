import feedparser
import requests
import g4f

# ==================== [ 설정 값 입력 ] ====================
TELEGRAM_TOKEN = "8198338892:AAF-vAEP0ls3IuNbtuKXXAtpHBnV9R3LyRo"
TELEGRAM_CHAT_ID = "8578881683"
# =========================================================

def get_sector_news():
    """경제와 시사 RSS 피드를 각각 수집하여 분류"""
    
    # 1. 경제 섹터 (구글 뉴스 Business)
    economy_url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
    economy_feed = feedparser.parse(economy_url)
    economy_list = []
    for entry in economy_feed.entries[:7]: # 최신 경제 뉴스 7개
        economy_list.append(f"- {entry.title} (링크: {entry.link})")
        
    # 2. 시사/국제 섹터 (구글 뉴스 World)
    current_url = "https://news.google.com/rss/headlines/section/topic/WORLD?hl=ko&gl=KR&ceid=KR:ko"
    current_feed = feedparser.parse(current_url)
    current_list = []
    for entry in current_feed.entries[:7]: # 최신 시사 뉴스 7개
        current_list.append(f"- {entry.title} (링크: {entry.link})")
        
    # 두 섹터의 데이터를 구조화된 텍스트로 합침
    formatted_raw_text = f"""
    [수집된 경제 뉴스 원본]
    {"\n".join(economy_list)}
    
    [수집된 시사/일반 뉴스 원본]
    {"\n".join(current_list)}
    """
    return formatted_raw_text

def summarize_news_by_sector(raw_news_text):
    """AI를 통해 경제와 시사 섹터를 완벽히 분리하여 요약"""
    
    prompt = f"""
    너는 바쁜 현대인을 위해 매일 아침 뉴스를 경제와 시사로 핵심만 큐레이션해주는 전문 에디터야.
    아래 제공된 원본 뉴스들을 바탕으로 아침 브리핑을 작성해줘.

    [요약 및 편집 규칙]
    1. 반드시 '📈 경제 섹터 브리핑'과 '🌍 시사/일반 섹터 브리핑' 두 개의 큰 권역으로 명확히 나눌 것.
    2. 각 섹터별로 중복되거나 무의미한 뉴스는 제외하고, 가장 중요한 핵심 이슈를 3~4개씩 선정할 것.
    3. 선정된 각 이슈는 바쁜 출근길에 한눈에 파악할 수 있도록 딱 2~3줄로 요약할 것.
    4. 요약 아래에는 독자가 원본을 읽을 수 있도록 제공된 링크([링크](url) 형태)를 깔끔하게 첨부할 것.
    5. 친절하면서도 정중한 문체(~입니다, ~할 것으로 보입니다)를 유지할 것.

    [뉴스 데이터]
    {raw_news_text}
    """
    
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4o,
        messages=[
            {"role": "system", "content": "너는 경제 및 시사 전문 뉴스레터 편집장이야."},
            {"role": "user", "content": prompt}
        ]
    )
    return response

def send_telegram_message(text):
    """텔레그램 봇으로 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("섹터별 아침 뉴스 알림 전송 성공!")
    else:
        print(f"전송 실패: {response.text}")

if __name__ == "__main__":
    print("1. [경제] 및 [시사] 각 섹터별 실시간 속보 수집 중...")
    raw_data = get_sector_news()
    
    print("2. AI 섹터별 맞춤 요약 진행 중...")
    try:
        summary = summarize_news_by_sector(raw_data)
        print("3. 텔레그램 발송 중...")
        send_telegram_message(summary)
    except Exception as e:
        print(f"AI 요약 중 오류 발생: {e}")
        print("요약 없이 섹터별 원본 뉴스를 발송합니다.")
        send_telegram_message(f"🚨 [AI 요약 오류] 원본 뉴스 목록입니다.\n\n{raw_data}")