import json
import re
import urllib.request

print(">>> update_channels.py başlatıldı! <<<")

def get_m3u8_from_embed(video_id):
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9',
        'Cookie': 'SOCS=CAI; CONSENT=YES+cb.20210328-17-p0.en+FX+111'
    }
    try:
        req = urllib.request.Request(embed_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
        # 1. hlsManifestUrl kontrolü
        match = re.search(r'"hlsManifestUrl"\s*:\s*"([^"]+)"', html)
        if match:
            url = match.group(1).replace(r'\/', '/').replace('\\u0026', '&')
            print(f"  [✓] Embed sayfasından hlsManifestUrl bulundu.")
            return url
            
        # 2. Googlevideo manifest URL kontrolü
        match_manifest = re.search(r'(https:\\?/\\?/manifest\.googlevideo\.com\\?/api\\?/manifest\\?/hls_playlist\\?/[^"]+)', html)
        if match_manifest:
            url = match_manifest.group(1).replace(r'\/', '/').replace('\\u0026', '&')
            print(f"  [✓] Embed sayfasından manifest URL bulundu.")
            return url
    except Exception as e:
        print(f"  [!] Embed hatası ({video_id}): {e}")
    return None

def get_m3u8_from_innertube(video_id):
    url = "https://www.youtube.com/youtubei/v1/player"
    clients = [
        {
            "clientName": "TVHTML5_SIMPLY_EMBEDDED_PLAYER",
            "clientVersion": "2.0",
            "hl": "tr",
            "gl": "TR"
        },
        {
            "clientName": "ANDROID_TESTSUITE",
            "clientVersion": "1.9",
            "androidSdkVersion": 31,
            "hl": "tr",
            "gl": "TR"
        },
        {
            "clientName": "WEB_EMBEDDED_PLAYER",
            "clientVersion": "1.20240308.00.00",
            "hl": "tr",
            "gl": "TR"
        }
    ]
    
    for client in clients:
        try:
            payload = {
                "context": {"client": client},
                "videoId": video_id
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url, 
                data=data, 
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_json = json.loads(resp.read().decode('utf-8'))
                hls_url = res_json.get('streamingData', {}).get('hlsManifestUrl')
                if hls_url:
                    print(f"  [✓] InnerTube ({client['clientName']}) ile m3u8 bulundu.")
                    return hls_url
        except Exception as e:
            print(f"  [!] InnerTube ({client['clientName']}) hatası: {e}")
            continue
    return None

def get_youtube_m3u8(youtube_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9',
        'Cookie': 'SOCS=CAI; CONSENT=YES+cb.20210328-17-p0.en+FX+111',
    }
    
    try:
        # 1. Video ID Tespiti
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
        
        # 2. Embed sayfasını dene
        m3u8_link = get_m3u8_from_embed(video_id)
        if m3u8_link:
            return m3u8_link
            
        # 3. InnerTube API alternatif istemcilerini dene
        m3u8_link = get_m3u8_from_innertube(video_id)
        if m3u8_link:
            return m3u8_link

    except Exception as e:
        print(f"  [!] Genel Hatası ({youtube_url}): {e}")
    
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
