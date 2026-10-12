"""SQLite asosidagi chat bazasi."""
import sqlite3
from datetime import datetime
from security import shifrla, deshifrla


class ChatBaza:
    def __init__(self, fayl: str = "chats.db", parol: str = None, salt: bytes = None):
        self.conn = sqlite3.connect(fayl)
        self.parol = parol
        self.salt = salt
        self._jadvallar_yarat()

    def _jadvallar_yarat(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sarlavha TEXT,
                yaratilgan TEXT,
                yangilangan TEXT
            );
            CREATE TABLE IF NOT EXISTS xabarlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                rol TEXT,
                mazmun TEXT,
                provayder TEXT,
                model TEXT,
                vaqt TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id)
            );
        """)
        self.conn.commit()

    def yangi_chat(self, sarlavha: str = "Yangi suhbat") -> int:
        vaqt = datetime.now().isoformat()
        cur = self.conn.execute(
            "INSERT INTO chats (sarlavha, yaratilgan, yangilangan) VALUES (?, ?, ?)",
            (sarlavha, vaqt, vaqt)
        )
        self.conn.commit()
        return cur.lastrowid

    def xabar_qosh(self, chat_id: int, rol: str, mazmun: str,
                   provayder: str = None, model: str = None):
        if self.parol and self.salt:
            mazmun = shifrla(self.parol, self.salt, mazmun).decode()
        self.conn.execute(
            "INSERT INTO xabarlar (chat_id, rol, mazmun, provayder, model, vaqt) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (chat_id, rol, mazmun, provayder, model, datetime.now().isoformat())
        )
        self.conn.execute(
            "UPDATE chats SET yangilangan=? WHERE id=?",
            (datetime.now().isoformat(), chat_id)
        )
        self.conn.commit()

    def tarix_ol(self, chat_id: int) -> list:
        cur = self.conn.execute(
            "SELECT rol, mazmun FROM xabarlar WHERE chat_id=? ORDER BY id",
            (chat_id,)
        )
        natija = []
        for rol, mazmun in cur.fetchall():
            if self.parol and self.salt:
                mazmun = deshifrla(self.parol, self.salt, mazmun.encode())
            natija.append({"role": rol, "content": mazmun})
        return natija

    def chatlar_royxati(self) -> list:
        cur = self.conn.execute(
            "SELECT id, sarlavha, yangilangan FROM chats ORDER BY yangilangan DESC"
        )
        return cur.fetchall()

    def yop(self):
        self.conn.close()
