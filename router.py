"""MonarxAI — Universal Router: Matn, Rasm va Video uchun"""
import json
import urllib.request
import urllib.error
import urllib.parse

# --- Matn Provayderlari ---
MATN_PROVAYDERLAR = {
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "model": "gemini-2.0-flash",
        "kalit_nomi": "GEMINI_API_KEY"
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "kalit_nomi": "GROQ_API_KEY"
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "deepseek/deepseek-r1:free",
        "kalit_nomi": "OPENROUTER_API_KEY"
    },
    "cerebras": {
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "model": "llama3.1-8b",
        "kalit_nomi": "CEREBRAS_API_KEY"
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-small-latest",
        "kalit_nomi": "MISTRAL_API_KEY"
    },
}

MAVZU_TARTIBI = {
    "kod": ["groq", "cerebras", "openrouter", "gemini", "mistral"],
    "umumiy": ["gemini", "groq", "openrouter", "mistral", "cerebras"],
}


def mavzuni_aniqla(savol: str) -> str:
    """Savol mavzusini aniqlaydi."""
    kod_belgilari = ["kod", "python", "javascript", "funksiya", "dastur", "xato", "debug"]
    if any(b in savol.lower() for b in kod_belgilari):
        return "kod"
    return "umumiy"


def matn_sorov(provayder: str, kalitlar: dict, xabarlar: list) -> str:
    """Bitta matn provayderiga so'rov yuboradi."""
    sozlama = MATN_PROVAYDERLAR[provayder]
    kalit = kalitlar.get(sozlama["kalit_nomi"])
    if not kalit:
        raise ValueError(f"{provayder} kaliti yo'q")

    data = json.dumps({
        "model": sozlama["model"],
        "messages": xabarlar
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {kalit}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    if provayder == "openrouter":
        headers["HTTP-Referer"] = "https://github.com/muxriddinbelgiyev2222-blip/MonarxAI"
        headers["X-Title"] = "MonarxAI"

    req = urllib.request.Request(
        sozlama["url"],
        data=data,
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            natija = json.loads(resp.read())
            return natija["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        xato_matni = ""
        try:
            xato_matni = e.read().decode()[:200]
        except Exception:
            pass
        if e.code == 429:
            raise RuntimeError("LIMIT_TUGADI")
        if e.code == 401:
            raise RuntimeError(f"KALIT_XATO: {xato_matni}")
        if e.code == 403:
            raise RuntimeError(f"RUXSAT_YOQ: {xato_matni}")
        if e.code == 404:
            raise RuntimeError(f"MODEL_TOPILMADI: {xato_matni}")
        raise RuntimeError(f"XATO_{e.code}: {xato_matni}")
    except Exception as ex:
        raise RuntimeError(f"ULANISH_XATO: {ex}")


def matn_router(xabarlar: list, kalitlar: dict) -> str:
    """Matn uchun router — failover bilan."""
    savol = xabarlar[-1]["content"] if xabarlar else ""
    mavzu = mavzuni_aniqla(savol)
    provayderlar = MAVZU_TARTIBI.get(mavzu, MAVZU_TARTIBI["umumiy"])

    xatolar = []
    for p in provayderlar:
        try:
            javob = matn_sorov(p, kalitlar, xabarlar)
            return f"[{p}] {javob}"
        except RuntimeError as e:
            xatolar.append(f"{p}: {e}")
            continue
        except ValueError:
            continue

    return "Barcha matn provayderlari ishlamadi:\n" + "\n".join(xatolar)


def rasm_yarat(prompt: str, model: str = "flux", width: int = 1024, height: int = 1024) -> str:
    """Pollinations orqali bepul rasm yaratadi. URL qaytaradi."""
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?model={model}&width={width}&height={height}&nologo=true"
    )
    return url


def video_yarat(prompt: str, kalitlar: dict, model: str = "wan-2.2", duration: int = 5) -> str:
    """Magic Hour orqali video yaratadi."""
    kalit = kalitlar.get("MAGIC_HOUR_API_KEY")
    if not kalit:
        return "XATO: MAGIC_HOUR_API_KEY topilmadi. magichour.ai saytidan bepul kalit oling."

    data = json.dumps({
        "prompt": prompt,
        "model": model,
        "duration_seconds": duration,
        "resolution": "480p",
        "aspect_ratio": "16:9"
    }).encode()

    req = urllib.request.Request(
        "https://api.magichour.ai/v1/text-to-video",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {kalit}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            natija = json.loads(resp.read())
            project_id = natija["project_id"]
            return f"VIDEO_YARATILDI: {project_id} (tugashini kuting)"
    except urllib.error.HTTPError as e:
        xato = e.read().decode()[:200]
        if e.code == 402:
            return "XATO: Magic Hour kreditingiz tugagan."
        return f"XATO: {xato}"
    except Exception as ex:
        return f"ULANISH_XATO: {ex}"
