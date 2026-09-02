#!/usr/bin/env python3
"""Extract sbazar.cz ad data over plain HTTP (avoids the Seznam consent wall).

Usage:
  sbazar_fetch.py https://www.sbazar.cz/<username>          # print ad URLs on a profile
  sbazar_fetch.py <ad-url> [<ad-url> ...]                   # print ad data as JSON
  sbazar_fetch.py <ad-url> --download DIR                   # also save photos as JPEG

Notes:
  - Photo URLs are signed; only the exact ?fl=... query from the page works.
  - The CDN serves WebP regardless of the .jpeg extension; --download converts
    to JPEG via ImageMagick `convert`. Photos carry a small sbazar watermark.
  - "locality" is best-effort (first text node after "Lokalita nabídky").
"""
import html as htmllib
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return r.read()


def fetch_text(url):
    return fetch(url).decode("utf-8", "replace")


def profile_ads(html):
    return sorted({"https://www.sbazar.cz" + h
                   for h in re.findall(r'href="(/inzerat/[^"]+)"', html)})


def locality(html):
    chunk = html[html.find("Lokalita nab"):][:600]
    for text in re.findall(r">([^<]+)<", chunk):
        text = text.strip()
        if text and not text.startswith("Lokalita"):
            return text
    return None


def ad_data(url):
    html = fetch_text(url)
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',
                         html, re.S):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("@type") == "Product":
            offer = (d.get("offers") or [{}])[0]
            return {
                "url": url,
                "title": htmllib.unescape(d.get("name") or ""),
                "description": htmllib.unescape(d.get("description") or ""),
                "price": offer.get("price"),
                "currency": offer.get("priceCurrency"),
                "category": d.get("category"),
                "locality": locality(html),
                "images": [i["contentUrl"] for i in d.get("image", [])
                           if isinstance(i, dict) and i.get("contentUrl")],
            }
    sys.exit(f"no Product ld+json found at {url}")


def download_images(ad, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", (ad["title"] or "ad").lower()).strip("-")
    saved = []
    for n, url in enumerate(ad["images"], 1):
        raw = outdir / f"{slug}-{n}.webp"
        raw.write_bytes(fetch(url))
        jpg = raw.with_suffix(".jpg")
        subprocess.run(["convert", str(raw), str(jpg)], check=True)
        raw.unlink()
        saved.append(str(jpg))
    return saved


def main(argv):
    download = None
    if "--download" in argv:
        i = argv.index("--download")
        download = pathlib.Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if not argv:
        sys.exit(__doc__)
    ads = []
    for url in argv:
        if "/inzerat/" in url:
            ad = ad_data(url)
            if download:
                ad["downloaded"] = download_images(ad, download)
            ads.append(ad)
        else:
            print("\n".join(profile_ads(fetch_text(url))))
    if ads:
        print(json.dumps(ads, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
