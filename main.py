import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

class SRTGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video SRT Altyazı Üretici")
        self.root.geometry("640x680")
        self.root.minsize(520, 560)
        
        # Modern Renk Paleti (Koyu Tema)
        self.bg_color = "#18181b"        # Zinc 900
        self.card_color = "#27272a"      # Zinc 800
        self.text_color = "#f4f4f5"      # Zinc 100
        self.text_muted = "#a1a1aa"      # Zinc 400
        self.primary_color = "#6366f1"   # Indigo 500
        self.primary_hover = "#4f46e5"   # Indigo 600
        self.accent_color = "#10b981"    # Emerald 500
        self.border_color = "#3f3f46"    # Zinc 700
        
        self.root.configure(bg=self.bg_color)
        
        # Modern Progress Bar Stili
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor=self.card_color,
            bordercolor=self.border_color,
            background=self.accent_color,
            lightcolor=self.accent_color,
            darkcolor=self.accent_color,
            thickness=12
        )
        
        self.video_paths = []  # Çoklu video listesi
        self.model_size = tk.StringVar(value="medium")
        self.lang_display = tk.StringVar(value="Türkçe")
        self.device_choice = tk.StringVar(value="CPU (Daha Kararlı)")
        self.progress_val = tk.DoubleVar(value=0)
        self.running = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # 1. Üst Başlık
        title_label = tk.Label(
            self.root, 
            text="Video SRT Altyazı Üretici", 
            font=("Segoe UI", 14, "bold"), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        title_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # --- EN ALT ELEMANLAR (Öncelikli pack edilerek gizlenmeleri önlenir) ---
        
        # Alt Buton Frame
        bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        bottom_frame.pack(fill="x", padx=20, pady=(5, 15), side="bottom")
        
        self.btn_generate = tk.Button(
            bottom_frame, 
            text="Altyazı Üretmeye Başla", 
            command=self.start_generation,
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_color,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            pady=8
        )
        self.btn_generate.pack(fill="x")
        self.btn_generate.bind("<Enter>", lambda e: self.btn_generate.configure(bg="#059669") if not self.running else None)
        self.btn_generate.bind("<Leave>", lambda e: self.btn_generate.configure(bg=self.accent_color) if not self.running else None)
        
        # İlerleme Çubuğu Frame
        progress_frame = tk.Frame(self.root, bg=self.bg_color)
        progress_frame.pack(fill="x", padx=20, pady=5, side="bottom")
        
        self.progress_label = tk.Label(
            progress_frame,
            text="",
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg=self.text_muted,
            anchor="w"
        )
        self.progress_label.pack(fill="x", pady=(0, 4))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            style="Modern.Horizontal.TProgressbar",
            variable=self.progress_val,
            maximum=100
        )
        self.progress_bar.pack(fill="x")
        
        # --- DİĞER KARTLAR ---
        
        # Kart 1: Video Seçimi (çoklu)
        video_card = tk.Frame(self.root, bg=self.card_color, bd=1, relief="flat", highlightbackground=self.border_color, highlightthickness=1)
        video_card.pack(fill="x", padx=20, pady=5)
        
        header_row = tk.Frame(video_card, bg=self.card_color)
        header_row.pack(fill="x", padx=12, pady=(8, 3))
        
        tk.Label(header_row, text="Video Seçimi (Çoklu)", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_color).pack(side="left")
        self.video_count_label = tk.Label(header_row, text="0 dosya", font=("Segoe UI", 8), bg=self.card_color, fg=self.text_muted)
        self.video_count_label.pack(side="right")
        
        list_frame = tk.Frame(video_card, bg=self.card_color)
        list_frame.pack(fill="x", padx=12, pady=(0, 6))
        
        self.video_listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.text_color,
            selectbackground=self.primary_color,
            selectforeground="white",
            bd=0,
            highlightbackground=self.border_color,
            highlightthickness=1,
            activestyle="none",
            height=5,
            selectmode=tk.EXTENDED
        )
        self.video_listbox.pack(side="left", fill="both", expand=True)
        
        list_scroll = tk.Scrollbar(list_frame, orient="vertical", command=self.video_listbox.yview)
        list_scroll.pack(side="right", fill="y")
        self.video_listbox.config(yscrollcommand=list_scroll.set)
        
        btn_row = tk.Frame(video_card, bg=self.card_color)
        btn_row.pack(fill="x", padx=12, pady=(0, 10))
        
        self.btn_select = tk.Button(
            btn_row, 
            text="Dosya Ekle", 
            command=self.select_videos,
            font=("Segoe UI", 8, "bold"),
            bg=self.primary_color,
            fg="white",
            activebackground=self.primary_hover,
            activeforeground="white",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=3
        )
        self.btn_select.pack(side="left")
        self.btn_select.bind("<Enter>", lambda e: self.btn_select.configure(bg=self.primary_hover) if not self.running else None)
        self.btn_select.bind("<Leave>", lambda e: self.btn_select.configure(bg=self.primary_color) if not self.running else None)
        
        self.btn_remove = tk.Button(
            btn_row,
            text="Seçileni Kaldır",
            command=self.remove_selected_videos,
            font=("Segoe UI", 8, "bold"),
            bg=self.border_color,
            fg="white",
            activebackground="#52525b",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=3
        )
        self.btn_remove.pack(side="left", padx=(8, 0))
        
        self.btn_clear = tk.Button(
            btn_row,
            text="Listeyi Temizle",
            command=self.clear_videos,
            font=("Segoe UI", 8, "bold"),
            bg=self.border_color,
            fg="white",
            activebackground="#52525b",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=3
        )
        self.btn_clear.pack(side="left", padx=(8, 0))
        
        # Kart 2: Ayarlar
        settings_card = tk.Frame(self.root, bg=self.card_color, bd=1, relief="flat", highlightbackground=self.border_color, highlightthickness=1)
        settings_card.pack(fill="x", padx=20, pady=5)
        
        tk.Label(settings_card, text="Ayarlar", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_color).pack(anchor="w", padx=12, pady=(8, 5))
        grid_frame = tk.Frame(settings_card, bg=self.card_color)
        grid_frame.pack(fill="x", padx=12, pady=(0, 10))
        grid_frame.columnconfigure(1, weight=1)
        
        # Model seçimi
        tk.Label(grid_frame, text="Whisper Modeli:", font=("Segoe UI", 9), bg=self.card_color, fg=self.text_muted).grid(row=0, column=0, sticky="w", pady=3)
        models = ["tiny", "base", "small", "medium", "large-v3"]
        model_menu = tk.OptionMenu(grid_frame, self.model_size, *models)
        self.style_option_menu(model_menu)
        model_menu.grid(row=0, column=1, sticky="w", padx=10, pady=3)
        
        # Dil Seçimi
        tk.Label(grid_frame, text="Altyazı Dili:", font=("Segoe UI", 9), bg=self.card_color, fg=self.text_muted).grid(row=1, column=0, sticky="w", pady=3)
        languages = ["Türkçe", "İngilizce", "Otomatik Algıla"]
        lang_menu = tk.OptionMenu(grid_frame, self.lang_display, *languages)
        self.style_option_menu(lang_menu)
        lang_menu.grid(row=1, column=1, sticky="w", padx=10, pady=3)
        
        # Cihaz Seçimi
        tk.Label(grid_frame, text="Donanım (Cihaz):", font=("Segoe UI", 9), bg=self.card_color, fg=self.text_muted).grid(row=2, column=0, sticky="w", pady=3)
        devices = ["CPU (Daha Kararlı)", "CUDA / GPU (Nvidia)"]
        device_menu = tk.OptionMenu(grid_frame, self.device_choice, *devices)
        self.style_option_menu(device_menu)
        device_menu.grid(row=2, column=1, sticky="w", padx=10, pady=3)
        
        # Kart 3: Durum ve Loglar (Esnek orta alan)
        log_card = tk.Frame(self.root, bg=self.card_color, bd=1, relief="flat", highlightbackground=self.border_color, highlightthickness=1)
        log_card.pack(fill="both", expand=True, padx=20, pady=5)
        
        tk.Label(log_card, text="İşlem Durumu", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_color).pack(anchor="w", padx=12, pady=(8, 3))
        
        self.log_text = ScrolledText(
            log_card, 
            font=("Consolas", 9), 
            bg=self.bg_color, 
            fg=self.text_muted,
            insertbackground=self.text_color,
            bd=0, 
            highlightbackground=self.border_color,
            highlightthickness=1,
            padx=8,
            pady=8,
            height=6
        )
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.log_text.config(state="disabled")
        
    def style_option_menu(self, menu):
        menu.configure(
            bg=self.bg_color, 
            fg=self.text_color, 
            activebackground=self.primary_hover, 
            activeforeground="white",
            bd=1,
            relief="flat",
            highlightbackground=self.border_color,
            highlightthickness=1,
            font=("Segoe UI", 8),
            direction="below",
            indicatoron=True
        )
        menu["menu"].configure(
            bg=self.bg_color,
            fg=self.text_color,
            activebackground=self.primary_hover,
            activeforeground="white",
            font=("Segoe UI", 8),
            bd=1
        )

    def log(self, message):
        self.root.after(0, self._safe_log, message)

    def _safe_log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        
    def _refresh_video_list(self):
        self.video_listbox.delete(0, tk.END)
        for path in self.video_paths:
            self.video_listbox.insert(tk.END, os.path.basename(path))
        count = len(self.video_paths)
        self.video_count_label.config(text=f"{count} dosya")

    def select_videos(self):
        file_paths = filedialog.askopenfilenames(
            title="Video Dosyaları Seçin (çoklu seçim)",
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.webm *.mpeg *.mpg")]
        )
        if not file_paths:
            return

        added = 0
        for path in file_paths:
            if path not in self.video_paths:
                self.video_paths.append(path)
                added += 1

        self._refresh_video_list()
        if added:
            self.log(f"{added} video eklendi. Toplam: {len(self.video_paths)}")
        else:
            self.log("Seçilen dosyalar zaten listede.")

    def remove_selected_videos(self):
        selected = list(self.video_listbox.curselection())
        if not selected:
            return
        for index in reversed(selected):
            del self.video_paths[index]
        self._refresh_video_list()
        self.log(f"Seçilen videolar kaldırıldı. Kalan: {len(self.video_paths)}")

    def clear_videos(self):
        if not self.video_paths:
            return
        self.video_paths.clear()
        self._refresh_video_list()
        self.log("Video listesi temizlendi.")

    def set_controls_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        btn_bg = self.primary_color if enabled else self.border_color
        gen_bg = self.accent_color if enabled else self.border_color
        gen_text = "Altyazı Üretmeye Başla" if enabled else "İşlem Yapılıyor..."

        self.btn_generate.config(state=state, bg=gen_bg, text=gen_text)
        self.btn_select.config(state=state, bg=btn_bg)
        self.btn_remove.config(state=state)
        self.btn_clear.config(state=state)
        self.video_listbox.config(state=state)

    def start_generation(self):
        if self.running:
            return

        if not self.video_paths:
            messagebox.showerror("Hata", "Lütfen en az bir video dosyası ekleyin.")
            return

        missing = [p for p in self.video_paths if not os.path.exists(p)]
        if missing:
            messagebox.showerror(
                "Hata",
                f"Bazı dosyalar bulunamadı:\n" + "\n".join(os.path.basename(p) for p in missing[:5])
            )
            return

        self.running = True
        self.progress_val.set(0)
        self.progress_label.config(text="")
        self.set_controls_enabled(False)
        self.log(f"\n--- Yeni İşlem Başlatıldı ({len(self.video_paths)} video) ---")

        threading.Thread(target=self.generate_srt, daemon=True).start()

    def generate_srt(self):
        completed = []
        failed = []
        try:
            from faster_whisper import WhisperModel
            videos = list(self.video_paths)
            total_videos = len(videos)
            model_name = self.model_size.get()

            selected_lang = self.lang_display.get()
            if selected_lang == "Türkçe":
                lang_code = "tr"
            elif selected_lang == "İngilizce":
                lang_code = "en"
            else:
                lang_code = None

            device_sel = "cuda" if "CUDA" in self.device_choice.get() else "cpu"
            model = None
            threads = max(1, (os.cpu_count() or 2) // 2)

            # Model bir kez yüklenir, tüm videolarda kullanılır
            if device_sel == "cuda":
                try:
                    self.log(f"Model yükleniyor: '{model_name}' (CUDA/GPU modu)...")
                    model = WhisperModel(model_name, device="cuda", compute_type="float16", cpu_threads=threads)
                    self.log("CUDA (GPU) modeli yüklendi.")
                except Exception as cuda_err:
                    self.log(f"CUDA Hatası: {str(cuda_err)}")
                    self.log("CUDA/GPU yüklenemedi veya DLL eksik. CPU moduna geçiliyor...")
                    model = None

            if model is None:
                self.log(f"Model yükleniyor: '{model_name}' (CPU modu, {threads} Thread)...")
                model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=threads)
                self.log("CPU modeli yüklendi.")

            for idx, video_file in enumerate(videos, 1):
                name = os.path.basename(video_file)
                self.log(f"\n[{idx}/{total_videos}] İşleniyor: {name}")
                self.root.after(0, self.progress_label.config, {"text": f"Video {idx}/{total_videos}: {name}"})
                self.root.after(0, self.progress_val.set, 0)

                try:
                    self.log("Ses analizi yapılıyor...")
                    segments_gen, info = model.transcribe(video_file, language=lang_code)

                    if lang_code:
                        self.log(f"Dil: {lang_code.upper()}")
                    else:
                        self.log(
                            f"Algılanan Dil: {info.language.upper()} "
                            f"(Olasılık: %{info.language_probability * 100:.2f})"
                        )

                    duration = info.duration
                    self.log(f"Süre: {self.format_time(duration)}")

                    output_srt = os.path.splitext(video_file)[0] + ".srt"
                    self.log("Altyazı yazılıyor...")

                    with open(output_srt, "w", encoding="utf-8") as f:
                        for i, segment in enumerate(segments_gen, 1):
                            start_str = self.format_time(segment.start)
                            end_str = self.format_time(segment.end)
                            f.write(f"{i}\n")
                            f.write(f"{start_str} --> {end_str}\n")
                            f.write(f"{segment.text.strip()}\n\n")

                            if duration > 0:
                                # Genel ilerleme: tamamlanan videolar + mevcut video oranı
                                video_progress = min(1.0, max(0.0, segment.end / duration))
                                overall = ((idx - 1) + video_progress) / total_videos * 100
                                self.root.after(0, self.progress_val.set, overall)

                    completed.append(output_srt)
                    self.log(f"Tamamlandı: {output_srt}")

                except Exception as video_err:
                    failed.append((name, str(video_err)))
                    self.log(f"Hata ({name}): {video_err}")

            self.root.after(0, self.progress_val.set, 100)
            self.root.after(0, self.progress_label.config, {"text": f"Bitti: {len(completed)} başarılı, {len(failed)} hata"})

            if completed and not failed:
                msg = f"{len(completed)} video için altyazı oluşturuldu.\n\n"
                msg += "\n".join(completed[:8])
                if len(completed) > 8:
                    msg += f"\n... ve {len(completed) - 8} dosya daha"
                self.log(f"\nTüm işlemler başarıyla tamamlandı! ({len(completed)} video)")
                self.root.after(0, lambda m=msg: messagebox.showinfo("Başarılı", m))
            elif completed and failed:
                msg = (
                    f"Başarılı: {len(completed)}\n"
                    f"Hatalı: {len(failed)}\n\n"
                    "Hatalı dosyalar:\n" + "\n".join(f"- {n}" for n, _ in failed[:5])
                )
                self.log(f"\nKısmi tamamlandı: {len(completed)} OK, {len(failed)} hata")
                self.root.after(0, lambda m=msg: messagebox.showwarning("Kısmi Başarı", m))
            else:
                err_detail = failed[0][1] if failed else "Bilinmeyen hata"
                self.log(f"\nHiçbir video işlenemedi.")
                self.root.after(0, lambda e=err_detail: messagebox.showerror("Hata", f"İşlem başarısız:\n{e}"))

        except Exception as e:
            self.log(f"\nHata oluştu: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Hata", f"İşlem sırasında bir hata meydana geldi:\n{str(e)}"))

        finally:
            self.running = False
            self.root.after(0, self.set_controls_enabled, True)
            
    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

if __name__ == "__main__":
    root = tk.Tk()
    app = SRTGeneratorApp(root)
    root.mainloop()
