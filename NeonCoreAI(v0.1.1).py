import json
import math
import os
import random
import re
import threading
import tkinter as tk
import urllib.parse
import urllib.request
import datetime
import html
from tkinter import filedialog, scrolledtext, messagebox, simpledialog

# NEON_HISTORY_START
NEON_HISTORY = json.loads('{"chats": {"1": {"name": "New Session", "time": "2026-06-24T17:38:08.545944"}}, "messages": {"1": [{"role": "user", "text": "make me some code in python"}, {"role": "bot", "text": "Web findings:\\n• The best way to learn Python is by practicing examples. This page contains examples on basic concepts of Python. We encourage you to try these examples on your own before looking at the solution. All the programs on this page are tested and should work on all platforms. Want to learn Python by writing code yourself? Enroll in our Interactive Python Course for FREE.\\n• Python is an incredibly powerful programming language, and it is becoming more popular every day. With its flexibility, it is no wonder that Python is used in so many different projects. With so many options, it can take time to figure out where to start. So if you are looking for some great Python projects to get you started, here are the 70+ best python projects out there! Master Python with ...\\n• Practice with Python program examples is always a good choice to scale up your logical understanding and programming skills and this article will provide you with the best sets of Python code examples. The below Python section contains a wide collection of Python programming examples.\\n• Explore 80 Python projects for beginners to advanced. Build real-world skills with hands-on ideas across apps, automation, data, and more.\\n• Well organized and easy to understand Web building tutorials with lots of examples of how to use HTML, CSS, JavaScript, SQL, Python, PHP, Bootstrap, Java, XML and more.\\n• Today we are going to discuss Python code snippets with their brief explanation that are highly useful for developers and programmers in their day-to-day life. We will look at various coding problems that arise on a regular basis and how to solve them using the Python code snippets provided here.\\n"}, {"role": "user", "text": "time"}, {"role": "bot", "text": "It is 05:41 PM, June 24."}]}, "next_id": 2}')
# NEON_HISTORY_END

# Image support via Pillow
try:
    from PIL import Image, ImageTk, ImageStat
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class MemoryDatabase:
    """Chat storage embedded in this file so history survives restarts."""
    _storage = None

    def __init__(self):
        if MemoryDatabase._storage is None:
            MemoryDatabase._storage = {
                "chats": {int(k): v for k, v in NEON_HISTORY.get("chats", {}).items()},
                "messages": {int(k): v for k, v in NEON_HISTORY.get("messages", {}).items()},
                "next_id": NEON_HISTORY.get("next_id", 1)
            }
    
    def create_chat(self, name):
        cid = self._storage["next_id"]
        self._storage["next_id"] += 1
        self._storage["chats"][cid] = {"name": name, "time": datetime.datetime.now().isoformat()}
        self._storage["messages"][cid] = []
        self._save_to_code()
        return cid

    def get_or_create_chat(self, name):
        if self._storage["chats"]:
            return sorted(self._storage["chats"])[0]
        return self.create_chat(name)

    def add_msg(self, cid, role, text):
        if cid in self._storage["messages"]:
            self._storage["messages"][cid].append({"role": role, "text": text})
            self._save_to_code()

    def get_history(self, cid):
        return self._storage["messages"].get(cid, [])

    def get_chats(self):
        return sorted(self._storage["chats"].items())

    def clear_all(self):
        self._storage = {"chats": {}, "messages": {}, "next_id": 1}
        MemoryDatabase._storage = self._storage
        cid = self.create_chat("New Session")
        return cid

    def _save_to_code(self):
        path = os.path.abspath(__file__)
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        history = json.dumps(self._storage, ensure_ascii=False)
        replacement = f"# NEON_HISTORY_START\nNEON_HISTORY = json.loads({history!r})\n# NEON_HISTORY_END"
        source = re.sub(
            r"# NEON_HISTORY_START\nNEON_HISTORY = .*?\n# NEON_HISTORY_END",
            replacement,
            source,
            flags=re.DOTALL
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)

class DynamicEngine:
    """Advanced scour engine for facts, code, and real-time updates."""
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'

    def _clean_text(self, text):
        text = html.unescape(re.sub(r'<.*?>', '', text))
        text = re.sub(r'(?<!\w)#\d+\b', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip(" -\n\t")

    def _fetch(self, url):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            with urllib.request.urlopen(req, timeout=12) as response:
                return response.read().decode('utf-8', errors='ignore')
        except: return ""

    def scour(self, query, history_context=""):
        q_lower = query.lower()
        is_latest = any(k in q_lower for k in ['latest', 'news', 'update', 'current', 'today', '2024'])
        
        # Balance Context: Use previous chat history to refine small queries
        search_term = query
        if len(query.split()) < 3 and history_context:
            search_term = f"{history_context} {query}"
        
        if is_latest: search_term += " latest news"
            
        encoded = urllib.parse.quote(search_term)
        
        # 1. Live Web Scrape (DDG HTML)
        html = self._fetch(f"https://html.duckduckgo.com/html/?q={encoded}")
        snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', html, re.DOTALL)
        clean_snippets = [self._clean_text(s) for s in snippets if len(s) > 25]
        clean_snippets = [s for s in clean_snippets if s]

        # 2. Fact Check (Wikipedia)
        wiki = ""
        try:
            w_api = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={encoded}&limit=1&format=json"
            w_data = json.loads(self._fetch(w_api))
            if w_data[1]:
                title = w_data[1][0]
                sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title.replace(' ', '_'))}"
                wiki = self._clean_text(json.loads(self._fetch(sum_url)).get("extract", ""))
        except: pass

        return wiki, clean_snippets[:6], is_latest

class SmartBrain:
    def __init__(self, memory, chat_id):
        self.engine = DynamicEngine()
        self.memory = memory
        self.chat_id = chat_id
        self.casual_patterns = {
            r"hi|hello|hey|yo": ["Hey! Need some info?", "Hi! What's the plan?", "Yo! Ready to work."],
            r"how are you": ["Feeling fast and local. You?", "All systems green. How are you?"],
            r"who are you": ["I'm NEON CORE, your dynamic local AI."],
            r"thanks|thank you": ["Happy to help!", "Anytime!"]
        }

    def respond(self, text):
        t_low = text.lower().strip()
        history = self.memory.get_history(self.chat_id)
        context = history[-1]["text"] if history else ""

        # 1. Casual Chat
        for p, r in self.casual_patterns.items():
            if re.search(p, t_low): return random.choice(r)

        # 2. Local Tools
        if t_low in ["time", "date"]:
            return f"It is {datetime.datetime.now().strftime('%I:%M %p, %B %d')}."

        # 3. Dynamic Scour
        wiki, snippets, is_latest = self.engine.scour(text, context)
        
        if not wiki and not snippets:
            return "I couldn't find a clear answer on that. Try rephrasing?"

        # 4. Contextual Balancing
        resp = ""
        if is_latest: resp += "⚡ **LATEST UPDATES:**\n"
        
        if wiki and not is_latest:
            resp += f"{wiki}\n\n"
        elif wiki:
            resp += f"(Wiki context: {wiki[:150]}...)\n\n"

        if snippets:
            resp += "Real-time findings:\n" if is_latest else "Web findings:\n"
            for s in snippets:
                # Dynamic Code Detection
                if any(k in s.lower() for k in ['def ', 'function', 'void', 'var ', 'int ']):
                    resp += f"```\n{s}\n```\n"
                else:
                    resp += f"• {s}\n"
        
        return resp

class NeonUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NEON CORE AI")
        self.root.geometry("1100x850")
        self.root.configure(bg="#000000")
        
        self.memory = MemoryDatabase()
        self.chat_id = self.memory.get_or_create_chat("New Session")
        self.brain = SmartBrain(self.memory, self.chat_id)
        self.img_cache = []
        
        self.orange = "#FF5F00"
        self.cyan = "#00FFCC"
        
        self.setup_ui()
        self.load_chat_history()

    def setup_ui(self):
        # Sidebar for Multi-Chat
        side = tk.Frame(self.root, bg="#080808", width=200)
        side.pack(side=tk.LEFT, fill=tk.Y)
        side.pack_propagate(False)
        
        tk.Label(side, text="SESSIONS", bg="#080808", fg=self.orange, font=("Consolas", 12, "bold")).pack(pady=20)
        self.chat_list = tk.Listbox(side, bg="#080808", fg="#666666", bd=0, highlightthickness=0, font=("Consolas", 10))
        self.chat_list.pack(fill=tk.BOTH, expand=True, padx=10)
        self.refresh_chat_list()
        tk.Button(side, text="New Chat", bg="#080808", fg=self.cyan, bd=0, font=("Consolas", 10), command=self.new_chat).pack(pady=4)
        tk.Button(side, text="Clear History", bg="#080808", fg=self.orange, bd=0, font=("Consolas", 10), command=self.clear_history).pack(pady=12)
        
        # Main Area
        main = tk.Frame(self.root, bg="#000000")
        main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        header = tk.Frame(main, bg="#0A0A0A", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="NEON CORE AI", bg="#0A0A0A", fg=self.orange, font=("Consolas", 14, "bold")).pack(side=tk.LEFT, padx=30)
        
        self.display = scrolledtext.ScrolledText(main, bg="#000000", fg="#FFFFFF", font=("Consolas", 12), bd=0, wrap=tk.WORD, state='disabled', padx=20, pady=20)
        self.display.pack(fill=tk.BOTH, expand=True)
        self.display.tag_config("user", foreground=self.orange, font=("Consolas", 12, "bold"))
        self.display.tag_config("bot", foreground=self.cyan)
        self.display.tag_config("code", foreground="#FFFFFF", background="#111111")

        footer = tk.Frame(main, bg="#000000", height=90)
        footer.pack(fill=tk.X, padx=20, pady=10)
        footer.pack_propagate(False)
        
        entry_wrap = tk.Frame(footer, bg="#0F0F0F", highlightthickness=1, highlightbackground="#222222")
        entry_wrap.pack(fill=tk.BOTH, expand=True)
        
        self.btn_file = tk.Button(entry_wrap, text="+", bg="#0F0F0F", fg=self.orange, bd=0, font=("Arial", 20), command=self.load_file)
        self.btn_file.pack(side=tk.LEFT, padx=15)
        
        self.entry = tk.Entry(entry_wrap, bg="#0F0F0F", fg="#FFFFFF", font=("Consolas", 13), bd=0, insertbackground=self.orange)
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.entry.bind("<Return>", lambda e: self.send())
        
        self.btn_send = tk.Button(entry_wrap, text="➜", bg="#0F0F0F", fg=self.orange, bd=0, font=("Arial", 20), command=self.send)
        self.btn_send.pack(side=tk.RIGHT, padx=15)

    def refresh_chat_list(self):
        self.chat_list.delete(0, tk.END)
        for cid, chat in self.memory.get_chats():
            label = chat.get("name", f"Chat {cid}")
            self.chat_list.insert(tk.END, label)

    def new_chat(self):
        name = simpledialog.askstring("New Chat", "Chat name:", initialvalue="New Session")
        if not name:
            return
        self.chat_id = self.memory.create_chat(name)
        self.brain.chat_id = self.chat_id
        self.refresh_chat_list()
        self.chat_list.selection_clear(0, tk.END)
        self.chat_list.selection_set(tk.END)
        self.display.config(state='normal')
        self.display.delete("1.0", tk.END)
        self.display.config(state='disabled')

    def load_chat_history(self):
        for item in self.memory.get_history(self.chat_id):
            sender = "YOU" if item.get("role") == "user" else "NEON"
            tag = "user" if item.get("role") == "user" else "bot"
            self.add_msg(sender, item.get("text", ""), tag)

    def clear_history(self):
        if not messagebox.askyesno("Clear History", "Clear all saved chat history from ai.py?"):
            return
        self.chat_id = self.memory.clear_all()
        self.brain.chat_id = self.chat_id
        self.refresh_chat_list()
        self.display.config(state='normal')
        self.display.delete("1.0", tk.END)
        self.display.config(state='disabled')

    def load_file(self):
        path = filedialog.askopenfilename()
        if path:
            filename = os.path.basename(path)
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.webp'] and HAS_PIL:
                self.show_img(path)
                self.add_msg("SYSTEM", f"Captured {filename}. Scanned for data.", "bot")
            else:
                self.add_msg("SYSTEM", f"File {filename} loaded into context.", "bot")

    def show_img(self, path):
        img = Image.open(path)
        img.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img)
        self.img_cache.append(photo)
        self.display.config(state='normal')
        self.display.image_create(tk.END, image=photo)
        self.display.insert(tk.END, "\n")
        self.display.config(state='disabled')

    def send(self):
        text = self.entry.get().strip()
        if not text: return
        self.add_msg("YOU", text, "user")
        self.memory.add_msg(self.chat_id, "user", text)
        self.entry.delete(0, tk.END)
        threading.Thread(target=self.process, args=(text,)).start()

    def process(self, text):
        resp = self.brain.respond(text)
        self.root.after(0, lambda: self.add_msg("NEON", resp, "bot"))
        self.memory.add_msg(self.chat_id, "bot", resp)

    def add_msg(self, sender, msg, tag):
        self.display.config(state='normal')
        self.display.insert(tk.END, f"\n{sender}\n", tag)
        if "```" in msg:
            parts = msg.split("```")
            for i, p in enumerate(parts):
                if i % 2 == 1: self.display.insert(tk.END, p, "code")
                else: self.display.insert(tk.END, p)
        else: self.display.insert(tk.END, msg + "\n")
        self.display.config(state='disabled')
        self.display.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    NeonUI(root)
    root.mainloop()
