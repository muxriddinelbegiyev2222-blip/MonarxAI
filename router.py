"""MonarxAI — ko'p provayderli router va failover."""
import json
import urllib.request
import urllib.error


PROVAYDERLAR = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "kalit_nomi": "GROQ_API_KEY"
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "model": "gemini-2.0-flash",
        "kalit_nomi": "GEMINI_API_KEY"
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
    "nvidia": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "meta/llama-3.3-70b-instruct",
        "kalit_nomi": "NVIDIA_API_KEY"
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "kalit_nomi": "OPENROUTER_API_KEY"
    },
}


MAVZU_TARTIBI = {
    "kod": ["groq", "cerebras", "openrouter", "mistral", "gemini", "nvidia"],
    "umumiy": ["gemini", "groq", "openrouter", "mistral", "cerebras", "nvidia"],
}


def mavzuni_aniqla(savol: str) -> str:
    kod_belgilari = ["kod", "python", "javascript", "funksiya", "dastur", "xato", "debug"]
    if any(b in savol.lower() for b in kod_belgilari):
        return "kod"
    return "umumiy"


def provayderga_sorov(provayder: str, kalitlar: dict, xabarlar: list) -> str:
    sozlama = PROVAYDERLAR[provayder]
    kalit = kalitlar.get(sozlama["kalit_nomi"])
    if not kalit:
        raise ValueError(f"{provayder} kaliti yo'q")

    data = json.dumps({
        "model": sozlama["model"],
        "messages": xabarlar
    }).encode()

    req = urllib.request.Request(
        sozlama["url"],
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {kalit}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            natija = json.loads(resp.read())
            return natija["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RuntimeError("LIMIT_TUGADI")
        raise RuntimeError(f"XATO_{e.code}")
    except Exception:
        raise RuntimeError("ULANISH_XATO")


def router(xabarlar: list, kalitlar: dict) -> str:
    savol = xabarlar[-1]["content"] if xabarlar else ""
    mavzu = mavzuni_aniqla(savol)
    provayderlar = MAVZU_TARTIBI.get(mavzu, MAVZU_TARTIBI["umumiy"])

    xatolar = []
    for p in provayderlar:
        try:
            javob = provayderga_sorov(p, kalitlar, xabarlar)
            return f"[{p}] {javob}"
        except RuntimeError as e:
            xatolar.append(f"{p}: {e}")
            continue
        except ValueError:
            continue

    return "Barcha provayderlar ishlamadi:\n" + "\n".join(xatolar)
