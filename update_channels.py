import json
import re
import urllib.request

print(">>> update_channels.py başlatıldı! <<<")

def get_m3u8_from_apis(video_id):
    # Yöntem 1: Lemnoslife API (YouTube Engellerini Aşan Özel Proxy)
    try:
        url = f"https://yt.lemnoslife.com/noKey/player?videoId={video_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            hls_url = data.get('streamingData', {}).get('hlsManifestUrl')
            if hls_url:
                print(f"  [✓] m3u8 bulundu! (Kaynak: Lemnoslife API)")
                return hls_url
    except Exception:
        pass

    # Yöntem 2: Piped API Sunucuları (Yedek Aracı Sunucular)
    instances = [
        "https://pipedapi.kavin.rocks",
        "https://pipedapi.tokhmi.xyz",
        "https://pipedapi.syncpundit.io"
    ]
    for instance in instances:
        try:
            url = f"{instance}/streams/{video_id}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                hls_url = data.get('hls')
                if hls_url:
                    print(f"  [✓] m3u8 bulundu! (Kaynak: {instance})")
                    return hls_url
        except Exception:
            continue
            
    return None

def get_youtube_m3u8(youtube_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9',
    }
    
    try:
        # 1. Önce Canlı Yayının Video ID'sini Buluyoruz
        video_id = None
        v_match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', youtube_url)
        if v_match:
            video_id = v_match.group(1)
        else:
            req = urllib.request.Request(youtube_url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                html = response.read().decode('utf-8', errors='ignore')

            video_id_match = re.search(r'"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"', html)
            if video_id_match:
                video_id = video_id_match.group(1)

        if not video_id:
            print(f"  [!] Video ID bulunamadı.")
            return None

        print(f"  [>] Canlı Yayın ID: {video_id}")
        
        # 2. ID bulunduktan sonra IP engeline takılmamak için Proxy API'lere soruyoruz!
        m3u8_link = get_m3u8_from_apis(video_id)
        if m3u8_link:
            return m3u8_link

    except Exception as e:
        print(f"  [!] Genel Hata ({youtube_url}): {e}")
    
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
