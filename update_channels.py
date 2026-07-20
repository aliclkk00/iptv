import json
import subprocess

def get_m3u8(youtube_url):
    try:
        # YouTube IP engellerini aşmak için Android istemci taklidi (player_client=android) ekliyoruz
        cmd = [
            "yt-dlp",
            "-g",
            "-f", "b/best",
            "--extractor-args", "youtube:player_client=android",
            "--no-warnings",
            youtube_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        
        for line in lines:
            if line.startswith("http"):
                return line
        return None
    except Exception as e:
        print(f"Hata ({youtube_url}): {e}")
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
            m3u8_link = get_m3u8(yt_target)
            if m3u8_link:
                channel["url"] = m3u8_link
                updated = True
                print(f"✓ Başarılı: {channel.get('name')}")
            else:
                print(f"✗ Link alınamadı: {channel.get('name')}")

    if updated:
        with open("kanallar.json", "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=2)
        print("kanallar.json başarıyla güncellendi!")
    else:
        print("Hiçbir link güncellenemedi.")

if __name__ == "__main__":
    main()
