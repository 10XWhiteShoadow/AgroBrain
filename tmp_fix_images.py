import re
import urllib.parse

filepath = r"C:\Users\Asus\OneDrive\Desktop\AgroBrain\myapp\views.py"

with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

def replacer(match):
    title = match.group(1)
    # create a short version of the title for the placeholder
    words = title.split()
    short_title = " ".join(words[:4])
    encoded_title = urllib.parse.quote(short_title)
    return f'"title": "{title}", "img": "https://placehold.co/500x500/10b981/ffffff?text={encoded_title}"'

# Match the title and image
new_text = re.sub(r'"title":\s*"([^"]+)",\s*"img":\s*"https://m\.media-[^"]+"', replacer, text)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_text)

print("Replaced Amazon image links with placeholders")
