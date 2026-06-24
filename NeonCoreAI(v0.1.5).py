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

# ============================================================================
# PERSISTENT HISTORY STORAGE (Embedded)
# ============================================================================
# NEON_HISTORY_START
NEON_HISTORY = json.loads('{"chats": {"1": {"name": "New Session", "time": "2026-06-24T19:45:45.965570"}}, "messages": {"1": [{"role": "user", "text": "what is a banana"}, {"role": "bot", "text": "A banana is an edible fruit from banana plants. It is usually yellow when ripe, soft inside, sweet, and high in carbohydrates and potassium."}]}, "next_id": 2}')
# NEON_HISTORY_END

# NEON_SETTINGS_START
NEON_SETTINGS = json.loads('{"theme": "Neon", "intelligence": "Balanced", "speed": "Normal", "result_count": 5, "font_size": 12, "web_search": true, "wikipedia": true, "ad_filter": true, "response_style": "Balanced"}')
# NEON_SETTINGS_END

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
        self._save()
        return cid
    def get_or_create_chat(self, name):
        if self._storage["chats"]: return sorted(self._storage["chats"].keys())[0]
        return self.create_chat(name)
    def add_msg(self, cid, role, text):
        if cid in self._storage["messages"]:
            self._storage["messages"][cid].append({"role": role, "text": text})
            self._save()
    def get_history(self, cid): return self._storage["messages"].get(cid, [])
    def get_chats(self): return sorted(self._storage["chats"].items())
    def clear_all(self):
        self._storage = {"chats": {}, "messages": {}, "next_id": 1}
        MemoryDatabase._storage = self._storage
        return self.create_chat("New Session")
    def _save(self):
        try:
            path = os.path.abspath(__file__)
            with open(path, "r", encoding="utf-8") as f: source = f.read()
            history = json.dumps(self._storage, ensure_ascii=False)
            replacement = f"# NEON_HISTORY_START\nNEON_HISTORY = json.loads({history!r})\n# NEON_HISTORY_END"
            source = re.sub(r"# NEON_HISTORY_START\nNEON_HISTORY = .*?\n# NEON_HISTORY_END", replacement, source, flags=re.DOTALL)
            with open(path, "w", encoding="utf-8") as f: f.write(source)
        except: pass

class SettingsStore:
    """Settings embedded in ai.py beside the chat history."""
    defaults = {
        "theme": "Neon",
        "intelligence": "Balanced",
        "speed": "Normal",
        "result_count": 5,
        "font_size": 12,
        "web_search": True,
        "wikipedia": True,
        "ad_filter": True,
        "response_style": "Balanced"
    }
    def __init__(self):
        self.data = dict(self.defaults)
        self.data.update(NEON_SETTINGS)
    def save(self):
        try:
            path = os.path.abspath(__file__)
            with open(path, "r", encoding="utf-8") as f: source = f.read()
            settings = json.dumps(self.data, ensure_ascii=False)
            replacement = f"# NEON_SETTINGS_START\nNEON_SETTINGS = json.loads({settings!r})\n# NEON_SETTINGS_END"
            source = re.sub(r"# NEON_SETTINGS_START\nNEON_SETTINGS = .*?\n# NEON_SETTINGS_END", replacement, source, flags=re.DOTALL)
            with open(path, "w", encoding="utf-8") as f: f.write(source)
        except: pass

# ============================================================================
# OMNI-BRAIN: THE COMPLETE INTELLIGENCE ENGINE
# ============================================================================

class OmniBrain:
    """Local-first brain for chat, math, code, memory, explanations, and research."""
    def __init__(self, settings=None):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        self.blacklist = ["ebay", "amazon", "aliexpress", "walmart", "target", "etsy", "wish", "temu", "alibaba"]
        self.ad_triggers = ["price", "shipping", "buy now", "discount", "sale", "stock", "cart", "$", "€", "£"]
        self.last_subject = ""
        self.small_facts = {
            "banana": "A banana is an edible fruit from banana plants. It is usually yellow when ripe, soft inside, sweet, and high in carbohydrates and potassium.",
            "python": "Python is a high-level programming language known for readable syntax, fast development, and broad use in automation, web apps, data work, AI, and scripting.",
            "ai": "AI means artificial intelligence: software designed to perform tasks that normally require human-like reasoning, language understanding, perception, or decision-making.",
            "computer": "A computer is an electronic machine that processes data using instructions called programs."
        }
        self.settings = settings or dict(SettingsStore.defaults)

    def update_settings(self, settings):
        self.settings = settings

    def _timeout(self):
        return {"Fast": 5, "Normal": 10, "Deep": 15}.get(self.settings.get("speed"), 10)

    def _fetch(self, url):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            with urllib.request.urlopen(req, timeout=self._timeout()) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception:
            return ""

    def _clean(self, text):
        text = html.unescape(re.sub(r'<.*?>', '', text))
        text = re.sub(r'(?<!\w)#\d+\b', '', text)
        return re.sub(r'\s+', ' ', text).strip(" -\n\t")

    def _history_text(self, history, limit=8):
        recent = history[-limit:] if history else []
        return "\n".join(f"{m.get('role', 'unknown')}: {m.get('text', '')}" for m in recent)

    def _safe_math(self, query):
        expr = query.lower()
        replacements = {
            "plus": "+", "minus": "-", "times": "*", "x": "*",
            "multiplied by": "*", "divided by": "/", "over": "/",
            "to the power of": "**", "^": "**"
        }
        for old, new in replacements.items():
            expr = expr.replace(old, new)
        expr = re.sub(r'[^0-9+\-*/().% ]', '', expr)
        if not expr.strip() or not re.search(r'\d\s*[+\-*/%]|\*\*', expr):
            return None
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return f"🧮 {query.strip()} = {result}"
        except Exception:
            return None

    def _code_answer(self, query):
        q = query.lower()
        if not any(k in q for k in ["code", "program", "script", "function", "make", "create", "write"]):
            return None
        if "python" in q:
            if "calculator" in q:
                code = """def calculate(a, op, b):
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': return a / b
    raise ValueError('Unknown operator')

print(calculate(10, '+', 5))"""
            elif "hello" in q:
                code = "name = input('Name: ')\nprint(f'Hello, {name}!')"
            else:
                code = """def main():
    print('Your Python program starts here')

if __name__ == '__main__':
    main()"""
            return f"Here is a clean Python starting point:\n```python\n{code}\n```"
        if "javascript" in q or "js" in q:
            return "Here is a simple JavaScript starting point:\n```javascript\nfunction main() {\n  console.log('Hello from JavaScript');\n}\n\nmain();\n```"
        if "html" in q or "website" in q:
            return "Here is a simple HTML page:\n```html\n<!doctype html>\n<html>\n  <head><title>My Page</title></head>\n  <body>\n    <h1>Hello</h1>\n  </body>\n</html>\n```"
        return None

    def _memory_answer(self, query, history):
        q = query.lower()
        if not any(k in q for k in ["remember", "history", "what did i say", "last message", "recap", "summary"]):
            return None
        if not history:
            return "I do not have any saved messages in this chat yet."
        limit = 4 if self.settings.get("response_style") == "Short" else 10 if self.settings.get("response_style") == "Detailed" else 6
        recent = history[-limit:]
        lines = []
        for item in recent:
            role = "You" if item.get("role") == "user" else "NEON"
            text = item.get("text", "").replace("\n", " ")
            if len(text) > 140:
                text = text[:137] + "..."
            lines.append(f"• {role}: {text}")
        return "Recent chat history:\n" + "\n".join(lines)

    def _explain_answer(self, query):
        q = query.lower()
        if not q.startswith(("explain ", "why ", "how ")):
            return None
        topic = re.sub(r'^(explain|why|how)\s+', '', query, flags=re.I).strip()
        if not topic:
            return None
        if self.settings.get("response_style") == "Short":
            return f"{topic}: identify what goes in, what happens, and what comes out."
        extra = "\n• Deep mode: I can also research current sources if you ask for latest/current info." if self.settings.get("response_style") == "Detailed" else ""
        return (f"Here is the simple version of {topic}:\n"
                f"• Core idea: it is a concept or process with parts that interact.\n"
                f"• How to understand it: identify the inputs, the steps, and the output.\n"
                f"• Best next step: ask me for an example, a diagram-style breakdown, or code.{extra}")

    def _research(self, query):
        if not self.settings.get("web_search", True):
            return None
        encoded = urllib.parse.quote(query)
        results = []
        if self.settings.get("wikipedia", True):
            try:
                wiki_search = json.loads(self._fetch(f"https://en.wikipedia.org/w/api.php?action=opensearch&search={encoded}&limit=1&format=json"))
                if len(wiki_search) > 1 and wiki_search[1]:
                    title = wiki_search[1][0]
                    wiki_sum = json.loads(self._fetch(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title.replace(' ', '_'))}"))
                    extract = self._clean(wiki_sum.get("extract", ""))
                    if extract:
                        results.append(("Core Fact", extract))
            except Exception:
                pass
        try:
            instant = json.loads(self._fetch(f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1"))
            answer = self._clean(instant.get("AbstractText") or instant.get("Answer") or "")
            if answer:
                results.append(("Direct Answer", answer))
        except Exception:
            pass
        try:
            html_data = self._fetch(f"https://html.duckduckgo.com/html/?q={encoded}")
            snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', html_data, re.DOTALL)
            cleaned = []
            for snippet in snippets:
                text = self._clean(snippet)
                low = text.lower()
                if self.settings.get("ad_filter", True) and any(t in low for t in self.ad_triggers) and not any(k in query.lower() for k in ["buy", "shop", "price"]):
                    continue
                if len(text) > 30 and text not in cleaned:
                    cleaned.append(text)
            if cleaned:
                results.append(("Web Findings", cleaned[:int(self.settings.get("result_count", 5))]))
        except Exception:
            pass
        if not results:
            return None
        response = []
        for label, content in results:
            if isinstance(content, list):
                response.append(f"🌐 **{label}:**")
                response.extend(f"• {item}" for item in content)
            else:
                response.append(f"💡 **{label}:**\n{content}")
        return "\n\n".join(response)

    def respond(self, query, history):
        q_low = query.lower().strip()
        if not q_low:
            return "Type something and I will work with it."

        if q_low in ["hi", "hello", "hey", "yo", "sup"]:
            return "NEON is online. Ask me for code, math, explanations, memory, or live info."
        if "thank" in q_low:
            return "Anytime."
        if q_low in ["time", "date", "today"]:
            return f"It's {datetime.datetime.now().strftime('%I:%M %p, %A, %B %d, %Y')}."
        if "what can you do" in q_low or q_low == "help":
            return "I can answer locally, calculate math, write starter code, explain topics, recap chat history, preview images, research the web, and change behavior from Settings."

        for answerer in (self._memory_answer,):
            ans = answerer(query, history)
            if ans:
                return ans

        math_ans = self._safe_math(query)
        if math_ans:
            return math_ans

        code_ans = self._code_answer(query)
        if code_ans:
            return code_ans

        for key, fact in self.small_facts.items():
            if re.search(rf'\b{re.escape(key)}s?\b', q_low) and any(k in q_low for k in ["what is", "what are", "tell me", "define"]):
                self.last_subject = key
                return fact

        explain_ans = self._explain_answer(query)
        if explain_ans and not any(k in q_low for k in ["latest", "current", "news", "today"]):
            return explain_ans

        if self.settings.get("intelligence") == "Local Only":
            return "Local-only intelligence is enabled. I handled math, code, memory, and built-in facts first, but this needs web research. Turn on Balanced or Deep in Settings."

        needs_research = any(k in q_low for k in ["latest", "current", "news", "today", "search", "find", "who is", "what is", "where is", "when did"])
        if self.settings.get("intelligence") == "Fast" and not needs_research:
            return "Fast intelligence is enabled, so I skipped deep research. Ask with `search` or switch to Balanced/Deep for broader answers."

        search_query = query
        if len(query.split()) < 4 and self.last_subject and any(w in q_low for w in ["it", "this", "that", "more", "why", "how"]):
            search_query = f"{self.last_subject} {query}"
        if self.settings.get("intelligence") == "Deep":
            history_context = self._history_text(history, limit=4)
            if history_context:
                search_query = f"{history_context}\nCurrent question: {search_query}"
        if len(query.split()) > 2:
            self.last_subject = query

        research = self._research(search_query)
        if research:
            return research

        return (
            "I could not get a solid answer from my local rules or web research.\n"
            "Try asking with a specific topic, for example: `what is photosynthesis`, `write python code for a calculator`, or `12 * 8 + 4`."
        )

# ============================================================================
# GUI ARCHITECTURE
# ============================================================================

class NeonUI:
    themes = {
        "Neon": {"bg": "#000000", "panel": "#080808", "field": "#0F0F0F", "accent": "#FF5F00", "bot": "#00FFCC", "text": "#FFFFFF", "muted": "#666666"},
        "Cyber Blue": {"bg": "#020712", "panel": "#071426", "field": "#0B1D33", "accent": "#4DA3FF", "bot": "#6EFFD2", "text": "#EAF4FF", "muted": "#7D8EA3"},
        "Matrix": {"bg": "#000000", "panel": "#031007", "field": "#06180C", "accent": "#00FF66", "bot": "#B6FFB6", "text": "#E8FFE8", "muted": "#4E8F61"},
        "Light": {"bg": "#F4F4F4", "panel": "#E5E5E5", "field": "#FFFFFF", "accent": "#C44700", "bot": "#006B5B", "text": "#111111", "muted": "#555555"},
        "Midnight": {"bg": "#070A14", "panel": "#10182A", "field": "#141F35", "accent": "#D78CFF", "bot": "#7DD3FC", "text": "#F8FAFC", "muted": "#8A95AA"}
    }
    def __init__(self, root):
        self.root = root
        self.root.title("NEON CORE AI")
        self.root.geometry("1100x850")
        
        self.memory = MemoryDatabase()
        self.chat_id = self.memory.get_or_create_chat("Main Session")
        self.settings_store = SettingsStore()
        self.settings = self.settings_store.data
        self.brain = OmniBrain(self.settings)
        self.img_cache = []
        
        self.theme = self.themes.get(self.settings.get("theme"), self.themes["Neon"])
        self.orange, self.cyan = self.theme["accent"], self.theme["bot"]
        self.root.configure(bg=self.theme["bg"])
        self._build_ui()
        self.apply_theme()
        self.load_history()

    def _build_ui(self):
        side = tk.Frame(self.root, bg=self.theme["panel"], width=200)
        side.pack(side=tk.LEFT, fill=tk.Y)
        side.pack_propagate(False)
        
        tk.Label(side, text="SESSIONS", bg=self.theme["panel"], fg=self.orange, font=("Consolas", 12, "bold")).pack(pady=20)
        self.chat_list = tk.Listbox(side, bg=self.theme["panel"], fg=self.theme["muted"], bd=0, highlightthickness=0, font=("Consolas", 10))
        self.chat_list.pack(fill=tk.BOTH, expand=True, padx=10)
        self.refresh_chats()
        
        tk.Button(side, text="+ New Chat", bg=self.theme["panel"], fg=self.cyan, bd=0, command=self.new_chat).pack(pady=5)
        tk.Button(side, text="⚙ Settings", bg=self.theme["panel"], fg=self.theme["text"], bd=0, command=self.open_settings).pack(pady=5)
        tk.Button(side, text="× Clear History", bg=self.theme["panel"], fg=self.orange, bd=0, command=self.clear_history).pack(pady=10)
        
        main = tk.Frame(self.root, bg=self.theme["bg"])
        main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        header = tk.Frame(main, bg=self.theme["panel"], height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="NEON CORE AI", bg=self.theme["panel"], fg=self.orange, font=("Consolas", 14, "bold")).pack(side=tk.LEFT, padx=30)
        
        self.display = scrolledtext.ScrolledText(main, bg=self.theme["bg"], fg=self.theme["text"], font=("Consolas", int(self.settings.get("font_size", 12))), bd=0, wrap=tk.WORD, state='disabled', padx=20, pady=20)
        self.display.pack(fill=tk.BOTH, expand=True)
        self.display.tag_config("user", foreground=self.orange, font=("Consolas", int(self.settings.get("font_size", 12)), "bold"))
        self.display.tag_config("bot", foreground=self.cyan)
        self.display.tag_config("code", foreground=self.theme["text"], background=self.theme["field"])

        footer = tk.Frame(main, bg=self.theme["bg"], height=90)
        footer.pack(fill=tk.X, padx=20, pady=10)
        footer.pack_propagate(False)
        
        wrap = tk.Frame(footer, bg=self.theme["field"], highlightthickness=1, highlightbackground=self.theme["muted"])
        wrap.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(wrap, text="+", bg=self.theme["field"], fg=self.orange, bd=0, font=("Arial", 20), command=self.load_file).pack(side=tk.LEFT, padx=15)
        self.entry = tk.Entry(wrap, bg=self.theme["field"], fg=self.theme["text"], font=("Consolas", int(self.settings.get("font_size", 12)) + 1), bd=0, insertbackground=self.orange)
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.entry.bind("<Return>", lambda e: self.send())
        tk.Button(wrap, text="➜", bg=self.theme["field"], fg=self.orange, bd=0, font=("Arial", 20), command=self.send).pack(side=tk.RIGHT, padx=15)

    def apply_theme(self):
        self.theme = self.themes.get(self.settings.get("theme"), self.themes["Neon"])
        self.orange, self.cyan = self.theme["accent"], self.theme["bot"]
        self.root.configure(bg=self.theme["bg"])
        self.display.configure(bg=self.theme["bg"], fg=self.theme["text"], font=("Consolas", int(self.settings.get("font_size", 12))))
        self.display.tag_config("user", foreground=self.orange, font=("Consolas", int(self.settings.get("font_size", 12)), "bold"))
        self.display.tag_config("bot", foreground=self.cyan)
        self.display.tag_config("code", foreground=self.theme["text"], background=self.theme["field"])
        self.entry.configure(bg=self.theme["field"], fg=self.theme["text"], font=("Consolas", int(self.settings.get("font_size", 12)) + 1), insertbackground=self.orange)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("NEON Settings")
        win.geometry("420x520")
        win.configure(bg=self.theme["bg"])
        values = {
            "theme": tk.StringVar(value=self.settings.get("theme", "Neon")),
            "intelligence": tk.StringVar(value=self.settings.get("intelligence", "Balanced")),
            "speed": tk.StringVar(value=self.settings.get("speed", "Normal")),
            "response_style": tk.StringVar(value=self.settings.get("response_style", "Balanced")),
            "result_count": tk.IntVar(value=int(self.settings.get("result_count", 5))),
            "font_size": tk.IntVar(value=int(self.settings.get("font_size", 12))),
            "web_search": tk.BooleanVar(value=bool(self.settings.get("web_search", True))),
            "wikipedia": tk.BooleanVar(value=bool(self.settings.get("wikipedia", True))),
            "ad_filter": tk.BooleanVar(value=bool(self.settings.get("ad_filter", True)))
        }

        def row(label):
            tk.Label(win, text=label, bg=self.theme["bg"], fg=self.theme["text"], anchor="w", font=("Consolas", 10, "bold")).pack(fill=tk.X, padx=18, pady=(12, 2))

        row("Theme")
        tk.OptionMenu(win, values["theme"], *self.themes.keys()).pack(fill=tk.X, padx=18)
        row("Intelligence")
        tk.OptionMenu(win, values["intelligence"], "Fast", "Balanced", "Deep", "Local Only").pack(fill=tk.X, padx=18)
        row("Speed")
        tk.OptionMenu(win, values["speed"], "Fast", "Normal", "Deep").pack(fill=tk.X, padx=18)
        row("Response Style")
        tk.OptionMenu(win, values["response_style"], "Short", "Balanced", "Detailed").pack(fill=tk.X, padx=18)
        row("Web Result Count")
        tk.Scale(win, from_=1, to=10, orient=tk.HORIZONTAL, variable=values["result_count"], bg=self.theme["bg"], fg=self.theme["text"], highlightthickness=0).pack(fill=tk.X, padx=18)
        row("Font Size")
        tk.Scale(win, from_=9, to=18, orient=tk.HORIZONTAL, variable=values["font_size"], bg=self.theme["bg"], fg=self.theme["text"], highlightthickness=0).pack(fill=tk.X, padx=18)
        tk.Checkbutton(win, text="Enable web search", variable=values["web_search"], bg=self.theme["bg"], fg=self.theme["text"], selectcolor=self.theme["field"]).pack(anchor="w", padx=18, pady=4)
        tk.Checkbutton(win, text="Use Wikipedia context", variable=values["wikipedia"], bg=self.theme["bg"], fg=self.theme["text"], selectcolor=self.theme["field"]).pack(anchor="w", padx=18, pady=4)
        tk.Checkbutton(win, text="Filter ads/shopping noise", variable=values["ad_filter"], bg=self.theme["bg"], fg=self.theme["text"], selectcolor=self.theme["field"]).pack(anchor="w", padx=18, pady=4)

        def save_settings():
            for key, var in values.items():
                self.settings[key] = var.get()
            self.settings_store.save()
            self.brain.update_settings(self.settings)
            self.apply_theme()
            win.destroy()

        tk.Button(win, text="Save Settings", bg=self.theme["field"], fg=self.orange, bd=0, font=("Consolas", 12, "bold"), command=save_settings).pack(fill=tk.X, padx=18, pady=18)

    def refresh_chats(self):
        self.chat_list.delete(0, tk.END)
        for cid, chat in self.memory.get_chats(): self.chat_list.insert(tk.END, chat["name"])

    def new_chat(self):
        name = simpledialog.askstring("New Chat", "Chat name:")
        if name:
            self.chat_id = self.memory.create_chat(name)
            self.brain.chat_id = self.chat_id
            self.refresh_chats()
            self.clear_display()

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Wipe all chat history?"):
            self.chat_id = self.memory.clear_all()
            self.refresh_chats()
            self.clear_display()

    def clear_display(self):
        self.display.config(state='normal')
        self.display.delete("1.0", tk.END)
        self.display.config(state='disabled')

    def load_history(self):
        for item in self.memory.get_history(self.chat_id):
            sender = "YOU" if item.get("role") == "user" else "NEON"
            tag = "user" if item.get("role") == "user" else "bot"
            self.add_msg(sender, item.get("text", ""), tag)

    def load_file(self):
        path = filedialog.askopenfilename()
        if path:
            filename = os.path.basename(path)
            if any(path.lower().endswith(e) for e in ['.png', '.jpg', '.jpeg', '.webp']) and HAS_PIL:
                img = Image.open(path); img.thumbnail((400, 400))
                photo = ImageTk.PhotoImage(img); self.img_cache.append(photo)
                self.display.config(state='normal'); self.display.image_create(tk.END, image=photo); self.display.insert(tk.END, "\n"); self.display.config(state='disabled')
                self.add_msg("SYSTEM", f"Visual scan of {filename} completed.", "bot")
            else: self.add_msg("SYSTEM", f"Document {filename} loaded.", "bot")

    def send(self):
        text = self.entry.get().strip()
        if text:
            self.add_msg("YOU", text, "user")
            self.memory.add_msg(self.chat_id, "user", text)
            self.entry.delete(0, tk.END)
            threading.Thread(target=self._process, args=(text,)).start()

    def _process(self, text):
        history = self.memory.get_history(self.chat_id)
        resp = self.brain.respond(text, history)
        self.root.after(0, lambda: self.add_msg("NEON", resp, "bot"))
        self.memory.add_msg(self.chat_id, "bot", resp)

    def add_msg(self, sender, msg, tag):
        self.display.config(state='normal')
        self.display.insert(tk.END, f"\n{sender}\n", tag)
        if "```" in msg:
            parts = msg.split("```")
            for i, p in enumerate(parts): self.display.insert(tk.END, p, "code" if i % 2 == 1 else None)
        else: self.display.insert(tk.END, msg + "\n")
        self.display.config(state='disabled'); self.display.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    NeonUI(root)
    root.mainloop()
