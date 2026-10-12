"""MonarxAI — Universal Multimedia AI Chat (GUI Version)"""
import os
import json
import threading
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
from security import hash_parol, tekshir_parol, shifrla, deshifrla
from database import ChatBaza
from router import router  # Bizning router funksiyamiz

CONFIG_FILE = "config.enc"
HASH_FILE = "parol.hash"
SALT_FILE = "salt.bin"

# --- Interfeys Sozlamalari ---
ctk.set_appearance_mode("Dark")  # "System", "Light", "Dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class MonarxAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MonarxAI — Universal Chat")
        self.geometry("900x700")

        # --- Chat Tarixi Maydoni ---
        self.chat_frame = ctk.CTkScrollableFrame(self, label_text="Chat History")
        self.chat_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # --- Pastki Boshqaruv Panel ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(pady=10, padx=20, fill="x")

        # Amal tanlash (Kod, Rasm, Video)
        self.action_menu = ctk.CTkOptionMenu(self.control_frame, values=["Chat (Kod/Matn)", "Rasm Yaratish", "Video Yaratish"])
        self.action_menu.pack(side="left", padx=5)

        # Matn kiritish maydoni
        self.entry = ctk.CTkEntry(self.control_frame, placeholder_text="Savolingizni yoki promptni kiriting...")
        self.entry.pack(side="left", padx=5, fill="x", expand=True)
        self.entry.bind("<Return>", self.on_send)

        # Yuborish Tugmasi
        self.send_button = ctk.CTkButton(self.control_frame, text="Yuborish", command=self.on_send)
        self.send_button.pack(side="right", padx=5)

        # --- Ma'lumotlar Bazasi va Router ---
        self.baza = None
        self.chat_id = None
        self.router_ready = False
        self.kalitlar = {}

        # Dasturni ishga tushirishda parol so'rash
        self.after(100, self.initialize_app)

    def initialize_app(self):
        """Dastur ishga tushganda parolni so'raydi yoki sozlashni boshlaydi."""
        if not os.path.exists(HASH_FILE):
            self.birinchi_sozlash()
        else:
            self.kirish()
        
        if self.router_ready:
            self.baza = ChatBaza("chats.db", self.parol, self.salt)
            self.chat_id = self.baza.yangi_chat("Yangi suhbat")
            self.add_message("System", "MonarxAI ishga tushdi. Savolingizni yozing!")

    def birinchi_sozlash(self):
        """Birinchi marta ishga tushganda parol va API kalitlarni sozlash."""
        # Bu qismni soddalashtirish uchun hozircha oldingi terminal versiyasidagi
        # funksiyalarni ishlatamiz, lekin UI orqali.
        # Aslida, bu yerda chiroyli "Sozlash" oynasi yasash mumkin.
        # Hozircha terminal usulini qoldiramiz, keyin UI ga o'tkazamiz.
        pass

    def kirish(self):
        """Parolni tekshirib, API kalitlarni ochadi."""
        # Xuddi shu terminal usuli, lekin UI orqali.
        # Bu qismni keyingi qadamda to'liq UI ga o'tkazamiz.
        pass

    def add_message(self, sender, message):
        """Chat oynasiga yangi xabar qo'shadi (chiroyli pufakcha ko'rinishida)."""
        # Xabar turiga qarab rang tanlash
        if sender == "Siz":
            color = "#2b719e"
            anchor = "e"  # o'ngga
        elif sender == "AI":
            color = "#3a3a3a"
            anchor = "w"  # chapga
        else:
            color = "#5a5a5a"
            anchor = "center"

        # Xabar pufakchasi (Frame)
        bubble = ctk.CTkFrame(self.chat_frame, fg_color=color, corner_radius=10)
        bubble.pack(pady=5, padx=10, anchor=anchor, fill="x")

        # Matn
        label = ctk.CTkLabel(bubble, text=f"{sender}: {message}", wraplength=600, justify="left")
        label.pack(padx=10, pady=5)

        # Scrollni eng pastga tushirish
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def on_send(self, event=None):
        """Yuborish tugmasi bosilganda ishlaydi."""
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.entry.delete(0, "end")
        self.add_message("Siz", user_text)

        # Amalni aniqlash
        action = self.action_menu.get()

        # Yangi oqimda AI javobini olish (UI qotib qolmasligi uchun)
        thread = threading.Thread(target=self.get_ai_response, args=(user_text, action))
        thread.start()

    def get_ai_response(self, user_text, action):
        """AI dan javob olish (background thread)."""
        if not self.router_ready:
            self.add_message("System", "Xato: Router tayyor emas.")
            return

        # Bazaga saqlash
        self.baza.xabar_qosh(self.chat_id, "user", user_text)
        tarix = self.baza.tarix_ol(self.chat_id)
        tarix.insert(0, {"role": "system", "content": "Siz professional yordamchi AI siz. O'zbek tilida javob bering."})

        # Amalga qarab yo'naltirish
        if action == "Chat (Kod/Matn)":
            javob = router(tarix, self.kalitlar)
            self.after(0, self.add_message, "AI", javob)
        elif action == "Rasm Yaratish":
            # Bu yerda rasm yaratish API si chaqiriladi
            # Hozircha placeholder
            self.after(0, self.add_message, "System", "Rasm yaratish funksiyasi hali qo'shilmagan.")
        elif action == "Video Yaratish":
            # Bu yerda video yaratish API si chaqiriladi
            # Hozircha placeholder
            self.after(0, self.add_message, "System", "Video yaratish funksiyasi hali qo'shilmagan.")

        # AI javobini bazaga saqlash
        # self.baza.xabar_qosh(self.chat_id, "assistant", javob)

if __name__ == "__main__":
    app = MonarxAIApp()
    app.mainloop()
