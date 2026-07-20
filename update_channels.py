import json
import re
import urllib.request

print(">>> update_channels.py başlatıldı! <<<")

def get_m3u8_via_innertube(video_id):
    # YouTube'un resmi InnerTube API servisinden canlı yayın m3u8 adresini ister
    url = "https://www.youtube.com/youtubei/v1/player"
    payload = {
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "19.08.35",
                "hl": "tr",
                "gl": "TR"
            }
        },
        "videoId": video_id
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            streaming_data = res_json.get('streamingData', {})
            hls_url = streaming_data.get('hlsManifestUrl')
            return hls_url
    except Exception as e:
        print(f"  [!] InnerTube API Hatası ({video_id}): {e}")
        return None

def get_youtube_m3u8(youtube_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9',
        'Cookie': 'SOCS=CAI; CONSENT=YES+cb.20210328-17-p0.en+FX+111',
    }
    
    try:
        # Doğrudan watch?v= linki verilmişse ID'yi linkten çek
        v_match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', youtube_url)
        video_id = v_match.group(1) if v_match else None

        # Kanal/Live linki verilmişse sayfadan Video ID bul
        if not video_id:
            req = urllib.request.Request(youtube_url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                html = response.read().decode('utf-8', errors='ignore')

            video_id_match = re.search(r'"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"', html)
            if video_id_match:
                video_id = video_id_match.group(1)

        if video_id:
            print(f"  [>] Canlı Yayın ID: {video_id} -> API'den m3u8 isteniyor...")
            return get_m3u8_via_innertube(video_id)

        print(f"  [!] Video ID bulunamadı.")
    except Exception as e:
        print(f"  [!] HTTP Hatası ({youtube_url}): {e}")
    
    return None

def main():
    print(">>> main() fonksiyonu çalışıyor... <<<")
    try:
        with open("kanallar.json", "r", encoding="utf-8") as f:
            channels = json.load(f)
        print(f"JSON okundu. Toplam {len(channels)} kanal var.")
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
