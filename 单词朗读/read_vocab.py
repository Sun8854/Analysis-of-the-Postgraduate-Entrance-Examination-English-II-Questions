import asyncio
import ctypes
import os
import re
import tempfile
import threading
import time
import tkinter as tk
from typing import Optional
from tkinter import filedialog, messagebox

try:
    import pyttsx3
except ImportError:  # pragma: no cover
    pyttsx3 = None

try:
    import edge_tts
except ImportError:  # pragma: no cover
    edge_tts = None



SECTION_STOP = "#### 反向查询"


def strip_parentheses(text: str) -> str:
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"（[^）]*）", "", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_vocab_file(path: str):
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(SECTION_STOP):
                break
            if line.startswith("####"):
                continue
            if "," not in line:
                continue

            left, right = line.split(",", 1)
            en = strip_parentheses(left)
            zh = strip_parentheses(right)
            if en and zh:
                entries.append((en, zh))
    return entries


def pick_voice(engine, keywords):
    if not engine:
        return None
    for voice in engine.getProperty("voices"):
        name = (voice.name or "").lower()
        vid = (voice.id or "").lower()
        if any(k in name or k in vid for k in keywords):
            return voice.id
    return None


def pick_preferred_voice(engine):
    return pick_voice(engine, ["chinese", "zh", "mandarin"]) or pick_voice(
        engine, ["english", "en-us", "en-gb"]
    )


class VocabReaderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("生词本朗读")
        self.root.geometry("520x260")

        self.file_path = tk.StringVar(value="未选择文件")
        self.en_text = tk.StringVar(value="英文")
        self.zh_text = tk.StringVar(value="中文")
        self.rate_text = tk.StringVar(value="语速：150")
        self.voice_mode_text = tk.StringVar(value="语音：普通")
        self.status_text = tk.StringVar(value="状态：就绪")

        self.entries = []
        self.current_index = 0
        self._stop_event = threading.Event()
        self._thread = None
        self._engine_lock = threading.Lock()
        self._play_lock = threading.Lock()
        self._mci_alias = None
        self.speech_rate = 150
        self.use_natural_voice = False
        self._edge_error_shown = False

        self.engine = None
        self.en_voice = None
        self.zh_voice = None

        self._build_ui()
        self._init_voice_mode()

    def _init_voice_mode(self):
        if edge_tts:
            self.use_natural_voice = True
            self.voice_mode_text.set("语音：自然")
        else:
            self.use_natural_voice = False
            self.voice_mode_text.set("语音：普通")

    def _notify(self, title: str, msg: str):
        self.root.after(0, messagebox.showinfo, title, msg)

    def _set_status(self, msg: str):
        self.root.after(0, self.status_text.set, f"状态：{msg}")

    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=12, pady=10)

        tk.Label(top, text="文件：").pack(side="left")
        tk.Label(top, textvariable=self.file_path, anchor="w").pack(side="left", fill="x", expand=True)
        tk.Button(top, text="选择文件", command=self.choose_file).pack(side="right")

        display = tk.Frame(self.root)
        display.pack(fill="both", expand=True, padx=12)

        tk.Label(display, textvariable=self.en_text, font=("Segoe UI", 16, "bold"), fg="#1a73e8").pack(pady=(10, 4))
        tk.Label(display, textvariable=self.zh_text, font=("Segoe UI", 14)).pack(pady=(0, 10))

        controls = tk.Frame(self.root)
        controls.pack(fill="x", padx=12, pady=10)

        self.play_btn = tk.Button(controls, text="开始朗读", command=self.start_reading, width=12)
        self.play_btn.pack(side="left")

        self.stop_btn = tk.Button(controls, text="停止", command=self.stop_reading, width=8, state="disabled")
        self.stop_btn.pack(side="left", padx=8)

        rate_box = tk.Frame(controls)
        rate_box.pack(side="right")
        tk.Button(rate_box, text="慢", width=4, command=self.decrease_rate).pack(side="left")
        tk.Label(rate_box, textvariable=self.rate_text, width=10, anchor="center").pack(side="left", padx=4)
        tk.Button(rate_box, text="快", width=4, command=self.increase_rate).pack(side="left")

        voice_box = tk.Frame(self.root)
        voice_box.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(voice_box, textvariable=self.voice_mode_text, anchor="w").pack(side="left")
        tk.Button(voice_box, text="切换语音", command=self.toggle_voice_mode, width=10).pack(side="right")

        status_box = tk.Frame(self.root)
        status_box.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(status_box, textvariable=self.status_text, anchor="w").pack(side="left")

    def _update_rate_label(self):
        self.rate_text.set(f"语速：{self.speech_rate}")

    def increase_rate(self):
        self.speech_rate = min(240, self.speech_rate + 20)
        self._update_rate_label()

    def decrease_rate(self):
        self.speech_rate = max(80, self.speech_rate - 20)
        self._update_rate_label()

    def toggle_voice_mode(self):
        if not edge_tts:
            messagebox.showinfo("提示", "未安装自然语音依赖：pip install edge-tts")
            self.use_natural_voice = False
            self.voice_mode_text.set("语音：普通")
            self._set_status("自然语音不可用")
            return
        self.use_natural_voice = not self.use_natural_voice
        self.voice_mode_text.set("语音：自然" if self.use_natural_voice else "语音：普通")
        self._set_status("已切换语音")

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="选择生词本文件",
            filetypes=[("Markdown", "*.md"), ("All Files", "*")],
        )
        if not path:
            return
        self.file_path.set(path)
        try:
            self.entries = parse_vocab_file(path)
            self.current_index = 0
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("错误", f"读取文件失败：{exc}")
            self.entries = []
            self.current_index = 0
            return
        if not self.entries:
            messagebox.showwarning("提示", "未解析到生词条目。")

    def start_reading(self):
        if not self.entries:
            messagebox.showwarning("提示", "请先选择包含生词的文件。")
            return
        if self.use_natural_voice:
            if not edge_tts:
                messagebox.showinfo("提示", "未安装自然语音依赖：pip install edge-tts，将使用普通语音。")
                self.use_natural_voice = False
                self.voice_mode_text.set("语音：普通")
                self._set_status("自然语音不可用")
        if not self.use_natural_voice and not pyttsx3:
            messagebox.showerror("缺少依赖", "未检测到 pyttsx3，请先安装：pip install pyttsx3")
            return
        if self._thread and self._thread.is_alive():
            return
        if self.current_index >= len(self.entries):
            self.current_index = 0
        self._stop_event.clear()
        self.play_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self._set_status("朗读中")
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop_reading(self):
        self._stop_event.set()
        with self._engine_lock:
            if self.engine:
                try:
                    self.engine.stop()
                except Exception:
                    pass
        with self._play_lock:
            if self._mci_alias:
                try:
                    self._mci_send(f"stop {self._mci_alias}")
                    self._mci_send(f"close {self._mci_alias}")
                except Exception:
                    pass
                self._mci_alias = None
        self.play_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self._set_status("已停止")

    def _edge_rate(self) -> str:
        percent = int(round((self.speech_rate - 150) / 150 * 100))
        if percent == 0:
            return "+0%"
        return f"{percent:+d}%"

    def _edge_tts_voice(self, is_english: bool) -> str:
        return "en-US-JennyNeural" if is_english else "zh-CN-XiaoxiaoNeural"

    def _edge_tts_play(self, text: str, is_english: bool) -> bool:
        if not edge_tts:
            return False
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_path = tmp.name
        tmp.close()
        voice = self._edge_tts_voice(is_english)
        rate = self._edge_rate()

        async def _synth():
            communicator = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
            )
            await communicator.save(tmp_path)

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_synth())
        finally:
            loop.close()

        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            if not self._edge_error_shown:
                self._edge_error_shown = True
                self._notify("自然语音失败", "生成语音文件失败或文件为空。")
            self._set_status("自然语音生成失败")
            return False

        try:
            alias = f"tts_{threading.get_ident()}"
            self._mci_send(f"open \"{tmp_path}\" type mpegvideo alias {alias}")
            with self._play_lock:
                self._mci_alias = alias
            self._mci_send(f"play {alias} from 0")
            start = time.time()
            while True:
                if self._stop_event.is_set():
                    self._mci_send(f"stop {alias}")
                    break
                mode = self._mci_status(alias, "mode")
                if mode in ("stopped", "paused"):
                    break
                if mode == "" and time.time() - start > 2:
                    raise RuntimeError("播放器未开始播放")
                time.sleep(0.05)
        except Exception as exc:
            if not self._edge_error_shown:
                self._edge_error_shown = True
                self._notify("自然语音失败", f"无法播放自然语音：{exc}")
            self._set_status("自然语音播放失败")
            return False
        finally:
            with self._play_lock:
                if self._mci_alias:
                    try:
                        self._mci_send(f"close {self._mci_alias}")
                    except Exception:
                        pass
                    self._mci_alias = None
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        self._set_status("自然语音播放完成")
        return True

    def _mci_send(self, command: str):
        ctypes.windll.winmm.mciSendStringW(command, None, 0, 0)

    def _mci_status(self, alias: str, item: str) -> str:
        buffer = ctypes.create_unicode_buffer(128)
        cmd = f"status {alias} {item}"
        ctypes.windll.winmm.mciSendStringW(cmd, buffer, len(buffer), 0)
        return buffer.value.strip().lower()

    def _say(self, text: str, voice_id: Optional[str]):
        if voice_id:
            self.engine.setProperty("voice", voice_id)
        self.engine.say(text)
        self.engine.runAndWait()

    def _read_loop(self):
        try:
            start_at = self.current_index
            for idx in range(start_at, len(self.entries)):
                en, zh = self.entries[idx]
                if self._stop_event.is_set():
                    break
                self.root.after(0, self.en_text.set, en)
                self.root.after(0, self.zh_text.set, zh)

                if self.use_natural_voice:
                    if not self._edge_tts_play(en, True):
                        self.use_natural_voice = False
                        self.voice_mode_text.set("语音：普通")
                        if not self._edge_error_shown:
                            self._edge_error_shown = True
                            self._notify("提示", "自然语音不可用，已切换为普通语音。")
                    if self._stop_event.is_set():
                        break
                    if not self.use_natural_voice:
                        pass
                    else:
                        self._edge_tts_play(zh, False)
                if not self.use_natural_voice:
                    with self._engine_lock:
                        if self._stop_event.is_set():
                            break
                        self.engine = pyttsx3.init()
                        voice_id = pick_preferred_voice(self.engine)
                        if voice_id:
                            self.engine.setProperty("voice", voice_id)
                        self.engine.setProperty("rate", self.speech_rate)
                        self.engine.say(en)
                        self.engine.say(zh)
                    try:
                        self.engine.runAndWait()
                    except Exception:
                        break
                    finally:
                        with self._engine_lock:
                            if self.engine:
                                try:
                                    self.engine.stop()
                                except Exception:
                                    pass
                                self.engine = None
                if not self._stop_event.is_set():
                    self.current_index = idx + 1
        finally:
            with self._engine_lock:
                if self.engine:
                    try:
                        self.engine.stop()
                    except Exception:
                        pass
                    self.engine = None
            self.root.after(0, self.play_btn.config, {"state": "normal"})
            self.root.after(0, self.stop_btn.config, {"state": "disabled"})
            self._set_status("就绪")


if __name__ == "__main__":
    app_root = tk.Tk()
    app = VocabReaderApp(app_root)
    app_root.mainloop()
