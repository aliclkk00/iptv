import json
import subprocess

def get_m3u8(youtube_url):
    # YouTube kısıtlamalarını aşmak için farklı istemcileri dener
    clients = ["ios", "android", "mweb", "web"]
    
    for client in clients:
        try:
            cmd = [
                "yt-dlp",
                "-g",
                "-f", "b/best",
                "--extractor-args", f"youtube:player_client={client}",
                "--no-warnings",
                youtube_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().splitlines()
            
            for line in lines:
                if line.startswith("http"):
                    print(f"  [+] Başarılı ({client}): {line[:50]}...")
                    return line
        except Exception:
            continue
            
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
            print(f"\nİşleniyor: {channel.get('name')} ({yt_target})")
            m3u8_link = get_m3u8(yt_target)
            if m3u8_link:
                channel["url"] = m3u8_link
                updated = True
            else:
                print(f"  [-] Link çekilemedi: {channel.get('name')}")

    if updated:
        with open("kanallar.json", "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=2)
        print("\nkanallar.json başarıyla güncellendi!")
    else:
        print("\nGüncellenecek link bulunamadı.")

if __name__ == "__main__":
    main()
