import os
import requests
import google.generativeai as genai

# API Yapılandırmaları
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def etkinlikleri_arastir_ve_ozetle():
    # Google Arama özelliğine (Search Grounding) sahip modelimizi seçiyoruz
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = """
    Sen İstanbul'da yaşayan uzman bir kültür-sanat asistanısız. 
    İnterneti tarayarak İstanbul'da bu hafta gerçekleşecek olan SADECE ÜCRETSİZ tiyatro, sinema gösterimleri ve konserleri araştır.
    Bunlar arasından en nitelikli, popüler ve dikkat çekici olanlardan toplam 100 tanesini seç.
    
    Listeyi şu düzende hazırla:
    - Etkinliğin Adı ve Türü (Ücretsiz Konser / Ücretsiz Tiyatro / Ücretsiz Sinema)
    - Tarih ve Saat
    - Mekan / Semt
    - Kısa Bilgi (1 cümle)
    
    Telegram mesajlaşma formatına uygun, okunabilir ve düzenli bir Türkçe liste hazırla. 
    Eğer liste çok uzun olursa Telegram karakter sınırına takılmamak için en önemli ve dolu dolu 100 etkinliği akıcı bir dille listele.
    """
    
    # Arama aracını (google_search) aktif ederek güncel ve gerçek verileri çekmesini sağlıyoruz
    response = model.generate_content(
        prompt,
        tools='google_search'
    )
    return response.text

def telegrama_gonder(mesaj):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Telegram mesajları çok uzun olduğunda bölünmesi gerekebilir, 
    # 4000 karakterlik parçalar halinde gönderelim ki hata almayalım:
    max_length = 4000
    parcalar = [mesaj[i:i+max_length] for i in range(0, len(mesaj), max_length)]
    
    for parca in parcalar:
        payload = {
            "chat_id": chat_id,
            "text": parca,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram gönderim hatası: {response.text}")
        else:
            print("Rapor Telegram'a başarıyla iletildi!")

if __name__ == "__main__":
    print("İstanbul etkinlikleri taranıyor...")
    rapor = etkinlikleri_arastir_ve_ozetle()
    print("Telegram'a aktarılıyor...")
    telegrama_gonder(rapor)
