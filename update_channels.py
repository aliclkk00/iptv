import json
import re
import urllib.request

def get_youtube_m3u8(youtube_url):
    # YouTube'un Rıza/Consent sayfasını aşmak için özel çerez ve header ekliyoruz
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'SOCS=CAI; CONSENT=YES+cb.20210328-17-p0.en+FX+111',
    }
    
    try:
        req = urllib.request.Request(youtube_url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # 1. Doğrudan hlsManifestUrl adresini arıyoruz
        match = re.search(r'"hlsManifestUrl"\s*:\s*"([^"]+)"', html)
        if match:
            m3u8_url = match.group(1).replace(r'\/', '/').replace('\\u0026', '&')
            return m3u8_url

        # 2. Doğrudan bulunamazsa canlı yayının videoId'sini çekip video sayfasına gidiyoruz
        video_id_match = re.search(r'"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"', html)
        if video_id_match:
            video_id = video_id_match.group(1)
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"  [>] Canlı Yayın ID bulundu ({video_id}), video sayfası taranıyor...")
            
            req2 = urllib.request.Request(watch_url, headers=headers)
            with urllib.request.urlopen(req2, timeout=12) as resp2:
                html2 = resp2.read().decode('utf-8', errors='ignore')
                
            match2 = re.search(r'"hlsManifestUrl"\s*:\s*"([^"]+)"', html2)
            if match2:
                m3u8_url = match2.group(1).replace(r'\/', '/').replace('\\u0026', '&')
                return m3u8_url

        print(f"  [!] hlsManifestUrl bulunamadı.")
    except Exception as e:
        print(f"  [!] HTTP/Okuma Hatası ({youtube_url}): {e}")
    
    return None

def main():
    try:
        with open("kanallar.json", "r", encoding="utf-8") as f:
            channels = json.load(f)
    except Exception as e:
        print(f"JSON okuma hatası: {e}")
        return

    updated = False
    for channel in channels:
        yt_target = channel.get("youtube_url")
        if yt_target:
            print(f"\nİşleniyor: {channel.get('name')} -> {yt_target}")
            m3u8_link = get_youtube_m3u8(yt_target)
            if m3u8_link:
                channel["url"] = m3u8_link
                updated = True
                print(f"  [✓] Başarıyla Çekildi: {m3u8_link[:60]}...")
            else:
                print(f"  [✗] Link Çekilemedi: {channel.get('name')}")

    if updated:
        with open("kanallar.json", "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=2)
        print("\n[BAŞARILI] kanallar.json başarıyla güncellendi ve kaydedildi!")
    else:
        print("\n[BİLGİ] Güncellenecek link bulunamadı.")

if __name__ == "__main__":
    main()
