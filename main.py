import os
import requests
from google import genai
from google.genai import types


def etkinlikleri_arastir_ve_ozetle():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY tanımlanmamış.")

    client = genai.Client(api_key=api_key)

    prompt = """
    Sen İstanbul'da yaşayan uzman bir kültür-sanat asistanısın.
    İnterneti tarayarak İstanbul'da bu hafta gerçekleşecek olan SADECE ÜCRETSİZ tiyatro,
    sinema gösterimleri ve konserleri araştır. Bunlar arasından en nitelikli, popüler ve
    dikkat çekici olanlardan toplam 100 tanesini seç.

    Listeyi şu düzende hazırla:
    - Etkinliğin Adı ve Türü (Ücretsiz Konser / Ücretsiz Tiyatro / Ücretsiz Sinema)
    - Tarih ve Saat
    - Mekan / Semt
    - Kısa Bilgi (1 cümle)

    Telegram mesajlaşma formatına uygun, okunabilir ve düzenli bir Türkçe liste hazırla.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        ),
    )
    return response.text


def telegrama_gonder(mesaj):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID tanımlanmamış.")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    max_length = 4000
    parcalar = [
        mesaj[i:i + max_length]
        for i in range(0, len(mesaj), max_length)
    ]

    for parca in parcalar:
        payload = {
            "chat_id": chat_id,
            "text": parca,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code != 200:
            print(f"Telegram gönderim hatası: {response.text}")
        else:
            print("Rapor Telegram'a başarıyla iletildi!")


if __name__ == "__main__":
    print("İstanbul etkinlikleri taranıyor...")
    rapor = etkinlikleri_arastir_ve_ozetle()
    print("Telegram'a aktarılıyor...")
    telegrama_gonder(rapor)
