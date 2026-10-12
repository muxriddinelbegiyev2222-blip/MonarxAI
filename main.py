"""MonarxAI — Universal portativ AI chat dasturi."""
import os
import sys
import json
import getpass

from security import hash_parol, tekshir_parol, shifrla, deshifrla
from database import ChatBaza
from router import router

CONFIG_FILE = "config.enc"
HASH_FILE = "parol.hash"
SALT_FILE = "salt.bin"


def birinchi_sozlash():
    print("=" * 50)
    print("   MONARXAI - BIRINCHI SOZLASH")
    print("=" * 50)

    parol = getpass.getpass("Yangi parol kiriting: ")
    parol2 = getpass.getpass("Parolni takrorlang: ")
    if parol != parol2:
        print("Parollar mos kelmadi!")
        return False

    salt = os.urandom(16)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    with open(HASH_FILE, "w") as f:
        f.write(hash_parol(parol, salt))

    print("\nAPI kalitlarni kiriting (bo'sh qoldirsangiz o'tkazib yuboriladi):")
    kalitlar = {}
    for nom in ["GROQ_API_KEY", "GEMINI_API_KEY", "CEREBRAS_API_KEY",
                "MISTRAL_API_KEY", "NVIDIA_API_KEY", "OPENROUTER_API_KEY"]:
        qiymat = input(f"  {nom}: ").strip()
        if qiymat:
            kalitlar[nom] = qiymat

    shifrlangan = shifrla(parol, salt, json.dumps(kalitlar))
    with open(CONFIG_FILE, "wb") as f:
        f.write(shifrlangan)
    print("\nSozlash muvaffaqiyatli tugadi!")
    return True


def kirish():
    if not os.path.exists(HASH_FILE):
        if not birinchi_sozlash():
            return None
        return None

    parol = getpass.getpass("Parol: ")
    salt = open(SALT_FILE, "rb").read()
    saqlangan = open(HASH_FILE, "r").read()

    if not tekshir_parol(parol, saqlangan):
        print("Parol noto'g'ri!")
        return None

    try:
        with open(CONFIG_FILE, "rb") as f:
            shifrlangan = f.read()
        kalitlar = json.loads(deshifrla(parol, salt, shifrlangan))
    except Exception:
        print("Fayl buzilgan yoki parol xato!")
        return None

    return kalitlar, parol, salt


def chat_interfeys(kalitlar, parol, salt):
    baza = ChatBaza("chats.db", parol, salt)
    chat_id = baza.yangi_chat("Yangi suhbat")

    print("\nMONARXAI - Suhbat boshlandi")
    print("Buyruqlar: /yangi, /tarix, /chiqish\n")

    while True:
        try:
            savol = input("Siz: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not savol:
            continue
        if savol == "/chiqish":
            break
        if savol == "/yangi":
            chat_id = baza.yangi_chat(f"Suhbat {chat_id + 1}")
            print("Yangi suhbat boshlandi.")
            continue
        if savol == "/tarix":
            for cid, sarlavha, vaqt in baza.chatlar_royxati():
                belgi = "->" if cid == chat_id else "  "
                print(f"  {belgi} [{cid}] {sarlavha} ({vaqt[:16]})")
            continue

        baza.xabar_qosh(chat_id, "user", savol)
        tarix = baza.tarix_ol(chat_id)
        tarix.insert(0, {
            "role": "system",
            "content": "Siz professional yordamchi AI siz. O'zbek tilida javob bering."
        })

        print("Javob kutilmoqda...")
        javob = router(tarix, kalitlar)
        baza.xabar_qosh(chat_id, "assistant", javob)
        print(f"\nAI: {javob}\n")

    baza.yop()
    print("Dastur yopildi.")


def main():
    natija = kirish()
    if natija is None:
        return
    kalitlar, parol, salt = natija
    chat_interfeys(kalitlar, parol, salt)


if __name__ == "__main__":
    main()
