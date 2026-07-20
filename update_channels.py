import json
import subprocess

def get_m3u8(youtube_url):
    # GitHub IP engelini aşmak için sırasıyla farklı istemcileri dener
    clients = ["ios", "mweb", "android", "tvhtml5"]
    
    for client in clients:
        try:
            cmd = [
                "yt-dlp",
                "-g",
                "-f", "best",
                "--extractor-args", f"youtube:player_client={client}",
                "--no-warnings",
                "--no-check-certificates",
                youtube_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().splitlines()
            
            for line in lines:
                if line.startswith("http"):
                    print(f"İstemci başarılı: {client}")
                    return line
        except Exception as e:
            continue
            
    print(f"Tüm istemciler başarısız oldu: {youtube_url}")
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
            print(f"İşleniyor: {channel.get('name')}")
            m3u8_link = get_m3u8(yt_target)
            if m3u8_link:
                channel["url"] = m3u8_link
                updated = True
                print(f"✓ Link Güncellendi: {channel.get('name')}")
            else:
                print(f"✗ Link alınamadı: {channel.get('name')}")

    if updated:
        with open("kanallar.json", "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=2)
        print("kanallar.json başarıyla güncellendi!")
    else:
        print("Güncellenecek link bulunamadı.")

if __name__ == "__main__":
    main()
