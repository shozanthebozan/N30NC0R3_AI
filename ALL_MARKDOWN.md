# N30N C0R3 AI

> One-file local AI with saved chats, selective context intelligence, live web research, and a full settings panel.

```
███╗   ██╗██████╗  ██████╗ ███╗   ██╗     ██████╗ ██████╗ ██████╗ ██████╗
████╗  ██║╚════██╗██╔═══██╗████╗  ██║    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
██╔██╗ ██║ █████╔╝██║   ██║██╔██╗ ██║    ██║     ██║   ██║██████╔╝█████╗  
██║╚██╗██║ ╚═══██╗██║   ██║██║╚██╗██║    ██║     ██║   ██║██╔══██╗██╔══╝  
██║ ╚████║██████╔╝╚██████╔╝██║ ╚████║    ╚██████╗╚██████╔╝██║  ██║███████╗
╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
                                                                          
                                  █████╗ ██╗                              
                                 ██╔══██╗██║                              
                                 ███████║██║                              
                                 ██╔══██║██║                              
                                 ██║  ██║██║                              
                                 ╚═╝  ╚═╝╚═╝                              
```

## Run

```bash
python3 ai.py
```

## Main Features

| Feature | What It Does |
|---|---|
| ThinkingBrain | Tiered intelligence engine for facts, code, and live research |
| Persistent Memory | Chat history and settings are safe-saved using Base64 encoding |
| Live Data | Scours the web for real-time info like business hours and news |
| Themes | Dual-mode palettes: High-contrast Neons and Eye-friendly Soft Nights |
| Settings Panel | Total control over intelligence, speed, sources, and storage |
| External Storage | Option to save chat database to an external JSON file |
| Image Analysis | Real-time .png and .jpg rendering (requires Pillow) |
| Smart Context | Selective memory: uses context for short follow-ups, but avoids confusion on new topics |

## Brain Powers

| Skill | Example |
|---|---|
| Identity | `who are you` |
| Live Hours | `when does Kmart close today?` |
| Deep Facts | `what is quantum entanglement` |
| Math | `sqrt(144) * (25 / 5)` |
| Follow-ups | `how big is it?` (Triggers selective context) |
| Code | `python script to sort a list` |
| Search | `define photosynthesis` |

## Settings

Open **⚙ Settings** from the sidebar.

| Setting | Options |
|---|---|
| UI Theme | Orange, Pink, Green, Blue, Red, Soft Night (Green), Soft Night (Blue) |
| Intelligence Mode | Fast, Balanced, Deep, Local Only |
| Response Style | Short, Balanced, Detailed |
| Search Speed | Fast, Normal, Deep |
| Active Sources | Web, Wiki, Live Hours, GitHub, Reddit, News |
| Preferences | Ad-Filter, Save Memory, External Database |

## Intelligence & Context

The AI uses **Selective Context Balancing**:
*   **Independent Queries**: Multi-word sentences are treated as fresh topics to prevent "topic bleed."
*   **Follow-ups**: Single-word queries or those using pronouns (`it`, `that`, `they`, etc.) trigger the memory system.
*   **Subject Extraction**: Automatically identifies the core subject of a query for more accurate research.

## Themes

| Style | Names | Description |
|---|---|---|
| **Neon** | Orange, Pink, Green, Blue, Red | Vibrant, high-contrast cyberpunk aesthetics. |
| **Soft Night** | Green, Blue | Eye-friendly, low-light optimized charcoal themes. |

## Safe Storage

The AI uses **Base64 Encoding** to store data inside `ai.py` to prevent Python syntax errors:

```python
# NEON_HISTORY_START
NEON_HISTORY_B64 = '...'
# NEON_HISTORY_END
```

## Optional Image Support

```bash
pip install pillow
```

Supported formats: `.png`, `.jpg`, `.jpeg`, `.webp`

---

**N30N C0R3 AI** is your advanced local intelligence hub, combining high-speed research with a sleek interface. No external models, no cloud, just raw code and global knowledge.