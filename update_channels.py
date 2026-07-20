import json
import subprocess

def get_m3u8(youtube_url):
    try:
        # yt-dlp kullanarak YouTube canlı yayınından taze m3u8 adresini alır
        cmd = ["yt-dlp", "-g", "-f", "best", youtube_url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Hata oluştu ({youtube_url}): {e}")
        return None

def main():
    try:
        with open("kanallar.json", "r", encoding="utf-8") as f:
            channels = json.load(f)
    except Exception as e:
        print(f"JSON dosyası okunamadı: {e}")
        return

    updated = False
    for channel in channels:
        # Eğer objede 'youtube_url' tanımlıysa çalışır, yoksa güvenle atlar
        yt_target = channel.get("youtube_url")
        if yt_target:
            print(f"Güncelleniyor: {channel.get('name')}")
            m3u8_link = get_m3u8(yt_target)
            if m3u8_link:
                channel["url"] = m3u8_link
                updated = True

    if updated:
        with open("kanallar.json", "w", encoding="utf-8") as f:
            json.dump(channels, f, ensure_ascii=False, indent=2)
        print("kanallar.json başarıyla güncellendi!")
    else:
        print("Güncellenecek YouTube kanalı bulunamadı veya değişiklik yapılmadı.")

if __name__ == "__main__":
    main()
