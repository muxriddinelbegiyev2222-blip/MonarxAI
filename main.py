"""MonarxAI — Universal Multimedia AI Chat (GUI)"""
import os
import json
import threading
import webbrowser
import customtkinter as ctk
from tkinter import messagebox

from security import hash_parol, tekshir_parol, shifrla, deshifrla
from database import ChatBaza
from router import matn_router, rasm_yarat, video_yarat

CONFIG_FILE = "config.enc"
HASH_FILE = "parol.hash"
SALT_FILE = "salt.bin"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ParolOyna(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MonarxAI — Kirish")
        self.geometry("420x320")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="MONARXAI", font=("Arial", 26, "bold")).pack(pady=25)
        ctk.CTkLabel(self, text="Parolni kiriting:", font=("Arial", 13)).pack(pady=5)

        self.parol_entry = ctk.CTkEntry(self, placeholder_text="Parol", show="*", width=280, height=40)
        self.parol_entry.pack(pady=10)
        self.parol_entry.bind("<Return>", lambda e: self.tekshir())

        self.xato_label = ctk.CTkLabel(self, text="", text_color="red", font=("Arial", 11))
        self.xato_label.pack(pady=5)

        ctk.CTkButton(self, text="Kirish", command=self.tekshir, width=280, height=40).pack(pady=10)

    def tekshir(self):
        parol = self.parol_entry.get()
        if not parol:
            self.xato_label.configure(text="Parol bo'sh bo'lmasin!")
            return

        if not os.path.exists(HASH_FILE):
            self.destroy()
            SozlashOyna(parol).mainloop()
            return

        salt = open(SALT_FILE, "rb").read()
        saqlangan = open(HASH_FILE, "r").read()

        if not tekshir_parol(parol, saqlangan):
            self.xato_label.configure(text="Parol noto'g'ri!")
            return

        try:
            with open(CONFIG_FILE, "rb") as f:
                shifrlangan = f.read()
            kalitlar = json.loads(deshifrla(parol, salt, shifrlangan))
        except Exception:
            self.xato_label.configure(text="Fayl buzilgan!")
            return

        self.destroy()
        AsosiyOyna(kalitlar, parol, salt).mainloop()


class SozlashOyna(ctk.CTk):
    def __init__(self, parol):
        super().__init__()
        self.title("MonarxAI — Birinchi sozlash")
        self.geometry("620x720")
        self.parol = parol

        ctk.CTkLabel(self, text="BIRINCHI SOZLASH", font=("Arial", 22, "bold")).pack(pady=15)
        ctk.CTkLabel(self, text="API kalitlarni kiriting (bo'sh qoldirsangiz o'tkazib yuboriladi)",
                     font=("Arial", 12)).pack(pady=5)

        self.entries = {}
        provayderlar = [
            ("GROQ_API_KEY", "Groq (console.groq.com) — tez va bepul"),
            ("GEMINI_API_KEY", "Gemini (aistudio.google.com) — bepul"),
            ("CEREBRAS_API_KEY", "Cerebras (cloud.cerebras.ai) — bepul"),
            ("MISTRAL_API_KEY", "Mistral (console.mistral.ai) — bepul"),
            ("OPENROUTER_API_KEY", "OpenRouter (openrouter.ai) — bepul modellar"),
            ("MAGIC_HOUR_API_KEY", "Magic Hour (magichour.ai) — video uchun"),
        ]

        frame = ctk.CTkScrollableFrame(self, width=560, height=480)
        frame.pack(pady=10, padx=20, fill="both", expand=True)

        for kalit, tavsif in provayderlar:
            ctk.CTkLabel(frame, text=tavsif, font=("Arial", 12, "bold"), anchor="w").pack(pady=(10, 2), fill="x")
            entry = ctk.CTkEntry(frame, width=520, placeholder_text=kalit, height=35)
            entry.pack(pady=2, fill="x")
            self.entries[kalit] = entry

        ctk.CTkButton(self, text="Saqlash va boshlash", command=self.saqlash,
                      width=280, height=45, font=("Arial", 14, "bold")).pack(pady=15)

    def saqlash(self):
        kalitlar = {}
        for kalit, entry in self.entries.items():
            qiymat = entry.get().strip()
            if qiymat:
                kalitlar[kalit] = qiymat

        if not kalitlar:
            messagebox.showwarning("Ogohlantirish", "Kamida bitta API kalit kiriting!")
            return

        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
        with open(HASH_FILE, "w") as f:
            f.write(hash_parol(self.parol, salt))

        shifrlangan = shifrla(self.parol, salt, json.dumps(kalitlar))
        with open(CONFIG_FILE, "wb") as f:
            f.write(shifrlangan)

        messagebox.showinfo("Muvaffaqiyat", "Sozlash tugadi! Endi parolingiz bilan kiring.")
        self.destroy()
        ParolOyna().mainloop()


class AsosiyOyna(ctk.CTk):
    def __init__(self, kalitlar, parol, salt):
        super().__init__()
        self.title("MonarxAI — Universal Chat")
        self.geometry("1150x780")
        self.kalitlar = kalitlar
        self.parol = parol
        self.salt = salt

        self.baza = ChatBaza("chats.db", parol, salt)
        self.chat_id = None
        self.joriy_rejim = "Chat"

        self._interfeys_yarat()
        self.yangi_suhbat()

    def _interfeys_yarat(self):
        # Chap panel
        self.chap_panel = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.chap_panel.pack(side="left", fill="y")
        self.chap_panel.pack_propagate(False)

        ctk.CTkLabel(self.chap_panel, text="MONARXAI",
                     font=("Arial", 20, "bold")).pack(pady=18)

        ctk.CTkButton(self.chap_panel, text="+ Yangi suhbat",
                      command=self.yangi_suhbat, height=42,
                      font=("Arial", 13, "bold")).pack(pady=5, padx=12, fill="x")

        ctk.CTkLabel(self.chap_panel, text="Suhbatlar:",
                     font=("Arial", 12, "bold")).pack(pady=(18, 5), padx=12, anchor="w")

        self.chatlar_frame = ctk.CTkScrollableFrame(self.chap_panel, width=210)
        self.chatlar_frame.pack(pady=5, padx=5, fill="both", expand=True)

        self.chatlar_yangila()

        # O'ng panel
        self.ong_panel = ctk.CTkFrame(self, corner_radius=0)
        self.ong_panel.pack(side="right", fill="both", expand=True)

        # Yuqori panel
        self.top_frame = ctk.CTkFrame(self.ong_panel, height=55, corner_radius=0)
        self.top_frame.pack(fill="x", padx=0, pady=0)
        self.top_frame.pack_propagate(False)

        ctk.CTkLabel(self.top_frame, text="Rejim:", font=("Arial", 13)).pack(side="left", padx=(15, 5), pady=12)

        self.rejim_menu = ctk.CTkOptionMenu(
            self.top_frame,
            values=["Chat", "Rasm", "Video"],
            command=self.rejim_ozgartir,
            width=150, height=35
        )
        self.rejim_menu.pack(side="left", padx=5, pady=12)

        self.holat_label = ctk.CTkLabel(self.top_frame, text="Chat rejimi",
                                        font=("Arial", 12), text_color="gray")
        self.holat_label.pack(side="left", padx=15)

        # Chat maydoni
        self.chat_frame = ctk.CTkScrollableFrame(self.ong_panel, corner_radius=0)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Pastki panel
        self.bottom_frame = ctk.CTkFrame(self.ong_panel, height=85, corner_radius=0)
        self.bottom_frame.pack(fill="x", padx=10, pady=10)
        self.bottom_frame.pack_propagate(False)

        self.entry = ctk.CTkEntry(self.bottom_frame,
                                  placeholder_text="Xabar yozing...",
                                  height=50, font=("Arial", 13))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=17)
        self.entry.bind("<Return>", lambda e: self.yubor())

        self.send_btn = ctk.CTkButton(self.bottom_frame, text="Yuborish",
                                      command=self.yubor, width=130, height=50,
                                      font=("Arial", 13, "bold"))
        self.send_btn.pack(side="right", pady=17)

    def rejim_ozgartir(self, tanlov):
        self.joriy_rejim = tanlov
        self.holat_label.configure(text=f"{tanlov} rejimi")
        if tanlov == "Chat":
            self.entry.configure(placeholder_text="Xabar yozing...")
        elif tanlov == "Rasm":
            self.entry.configure(placeholder_text="Rasm tavsifini yozing...")
        elif tanlov == "Video":
            self.entry.configure(placeholder_text="Video tavsifini yozing...")

    def yangi_suhbat(self):
        self.chat_id = self.baza.yangi_chat("Yangi suhbat")
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        self.xabar_qosh("System", "Yangi suhbat boshlandi.")
        self.chatlar_yangila()

    def chatlar_yangila(self):
        for widget in self.chatlar_frame.winfo_children():
            widget.destroy()

        for cid, sarlavha, vaqt in self.baza.chatlar_royxati():
            btn = ctk.CTkButton(
                self.chatlar_frame,
                text=f"{sarlavha[:22]}",
                command=lambda c=cid: self.suhbat_och(c),
                anchor="w", height=38, font=("Arial", 12)
            )
            btn.pack(pady=3, padx=2, fill="x")

    def suhbat_och(self, chat_id):
        self.chat_id = chat_id
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

        for xabar in self.baza.tarix_ol(chat_id):
            self.xabar_qosh("Siz" if xabar["role"] == "user" else "AI", xabar["content"])

    def xabar_qosh(self, kim, matn):
        if kim == "Siz":
            rang = "#1f6aa5"
            anchor = "e"
            label_text = f"Siz:\n{matn}"
        elif kim == "AI":
            rang = "#2b2b2b"
            anchor = "w"
            label_text = f"AI:\n{matn}"
        else:
            rang = "#3a3a3a"
            anchor = "center"
            label_text = matn

        bubble = ctk.CTkFrame(self.chat_frame, fg_color=rang, corner_radius=12)
        bubble.pack(pady=6, padx=10, anchor=anchor)

        label = ctk.CTkLabel(bubble, text=label_text, wraplength=680,
                             justify="left", font=("Arial", 12))
        label.pack(padx=14, pady=10)

        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def yubor(self):
        matn = self.entry.get().strip()
        if not matn:
            return

        self.entry.delete(0, "end")
        self.xabar_qosh("Siz", matn)
        self.baza.xabar_qosh(self.chat_id, "user", matn)

        self.send_btn.configure(state="disabled", text="Kutilmoqda...")

        thread = threading.Thread(target=self.javob_ol, args=(matn,))
        thread.daemon = True
        thread.start()

    def javob_ol(self, matn):
        try:
            if self.joriy_rejim == "Chat":
                tarix = self.baza.tarix_ol(self.chat_id)
                tarix.insert(0, {
                    "role": "system",
                    "content": "Siz professional yordamchi AI siz. O'zbek tilida javob bering."
                })
                javob = matn_router(tarix, self.kalitlar)

            elif self.joriy_rejim == "Rasm":
                url = rasm_yarat(matn)
                javob = f"Rasm tayyor!\nURL: {url}\n\n(Rasm brauzerda ochildi.)"
                try:
                    webbrowser.open(url)
                except Exception:
                    pass

            elif self.joriy_rejim == "Video":
                javob = video_yarat(matn, self.kalitlar)

            else:
                javob = "Noma'lum rejim."

        except Exception as e:
            javob = f"XATO: {e}"

        self.baza.xabar_qosh(self.chat_id, "assistant", javob)
        self.after(0, lambda: self.xabar_qosh("AI", javob))
        self.after(0, lambda: self.send_btn.configure(state="normal", text="Yuborish"))


def main():
    ParolOyna().mainloop()


if __name__ == "__main__":
    main()
