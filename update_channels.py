import json
import re
import urllib.request

def get_youtube_m3u8(youtube_url):
    try:
        # YouTube canlı yayın sayfasını taranan bir Google Chrome gibi çağırıyoruz
        req = urllib.request.Request(
            youtube_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'tr-TR,tr;q=0.9'
            }
        )
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        # Sayfa kaynak kodundaki gizli hlsManifestUrl (m3u8) adresini buluyoruz
        match = re.search(r'"hlsManifestUrl"\s*:\s*"([^"]+)"', html)
        if match:
            m3u8_url = match.group(1).replace(r'\/', '/')
            return m3u8_url
        else:
            print(f"  [!] hlsManifestUrl bulunamadı: {youtube_url}")
    except Exception as e:
        print(f"  [!] HTTP/Sayfa Okuma Hatası ({youtube_url}): {e}")
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
            print(f"İşleniyor: {channel.get('name')} -> {yt_target}")
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
        print("\n[BAŞARILI] kanallar.json güncellendi ve kaydedildi!")
    else:
        print("\n[BİLGİ] Güncellenecek link bulunamadı.")

if __name__ == "__main__":
    main()
