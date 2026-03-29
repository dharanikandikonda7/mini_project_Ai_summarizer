"""utils/extractor.py"""
from __future__ import annotations
import re, requests
from bs4 import BeautifulSoup

def extract_from_url(url: str) -> str:
    h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=h, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    for t in soup(["script","style","nav","header","footer","aside","figure"]):
        t.decompose()
    body = (soup.find("article") or soup.find("main") or soup.body)
    paras = body.find_all("p") if body else []
    text  = " ".join(p.get_text(" ", strip=True) for p in paras)
    return re.sub(r"\s+", " ", text).strip()

def extract_from_file(f) -> str:
    raw = f.read()
    try:    return raw.decode("utf-8")
    except: return raw.decode("latin-1", errors="replace")

def word_count(text: str) -> int:
    return len(text.split())
