import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from analyzer import load_audio, detect_beats, detect_onsets
from exporters import export_to_csv_markers, export_to_edl, export_to_fcpxml

# Set theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class BeatAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AUDIO BEAT ANALYZER")
        self.geometry("600x500")
        self.resizable(False, False)

        # Data
        self.file_path = None
        self.y = None
        self.sr = None
        self.duration = 0
        self.beat_times = []
        self.onset_times = []

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=0) # File
        self.grid_rowconfigure(2, weight=1) # Status/Info
        self.grid_rowconfigure(3, weight=0) # Controls
        self.grid_rowconfigure(4, weight=0) # Export

        # 1. Header
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_label = ctk.CTkLabel(self.header_frame, text="BEAT SYNC ANALYZER", 
                                         font=("Roboto Medium", 20))
        self.header_label.pack(pady=15)

        # 2. File Selection
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        
        self.select_btn = ctk.CTkButton(self.file_frame, text="SELECT AUDIO FILE", 
                                        command=self.select_file,
                                        font=("Roboto", 14, "bold"),
                                        height=40)
        self.select_btn.pack(pady=10, padx=10, fill="x")
        
        self.file_label = ctk.CTkLabel(self.file_frame, text="No file selected", text_color="gray")
        self.file_label.pack(pady=(0, 10))

        # 3. Status / Info
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(self.info_frame, text="Ready", font=("Roboto", 14))
        self.status_label.pack(pady=20)
        
        self.details_label = ctk.CTkLabel(self.info_frame, text="", justify="left")
        self.details_label.pack(pady=10, padx=10)

        # 4. Analysis Controls
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.analyze_btn = ctk.CTkButton(self.controls_frame, text="ANALYZE BEATS", 
                                         command=self.start_analysis,
                                         state="disabled",
                                         fg_color="#2B2B2B",
                                         hover_color="#3A3A3A",
                                         border_width=1,
                                         border_color="gray")
        self.analyze_btn.pack(pady=10, fill="x", padx=10)

        # 5. Export
        self.export_frame = ctk.CTkFrame(self)
        self.export_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.export_edl_btn = ctk.CTkButton(self.export_frame, text="EXPORT EDL (CMX 3600)", 
                                            command=self.export_edl,
                                            state="disabled")
        self.export_edl_btn.pack(side="left", expand=True, padx=(10, 5), pady=10)
        
        self.export_csv_btn = ctk.CTkButton(self.export_frame, text="EXPORT MARKERS (CSV)", 
                                            command=self.export_csv,
                                            state="disabled")
        self.export_csv_btn.pack(side="right", expand=True, padx=(5, 10), pady=10)

        self.export_fcpxml_btn = ctk.CTkButton(self.export_frame, text="EXPORT FCPXML", 
                                            command=self.export_fcpxml,
                                            state="disabled")
        self.export_fcpxml_btn.pack(side="right", expand=True, padx=(5, 10), pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.aac *.flac *.m4a")])
        if file_path:
            self.file_path = file_path
            self.file_label.configure(text=os.path.basename(file_path), text_color="white")
            self.analyze_btn.configure(state="normal", fg_color="#1F6AA5", border_width=0) # Reset style
            self.status_label.configure(text="File Loaded. Ready to Analyze.")
            self.details_label.configure(text="")
            self.export_edl_btn.configure(state="disabled")
            self.export_csv_btn.configure(state="disabled")
            self.export_fcpxml_btn.configure(state="disabled")

    def start_analysis(self):
        if not self.file_path:
            return
        
        self.status_label.configure(text="Analyzing... Please Wait")
        self.analyze_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")
        
        # Run in thread to not freeze GUI
        thread = threading.Thread(target=self.run_analysis)
        thread.start()

    def run_analysis(self):
        try:
            self.y, self.sr, self.duration = load_audio(self.file_path)
            tempo, self.beat_times = detect_beats(self.y, self.sr)
            
            # Update GUI
            self.after(0, lambda: self.analysis_complete(tempo, len(self.beat_times)))
        except Exception as e:
            self.after(0, self.analysis_failed, str(e))

    def analysis_complete(self, tempo, beat_count):
        self.status_label.configure(text="Analysis Complete!")
        # Ensure tempo is a scalar float
        if hasattr(tempo, "item"):
            tempo = tempo.item()
        self.details_label.configure(text=f"Duration: {self.duration:.2f}s\nEstimated Tempo: {tempo:.1f} BPM\nTotal Beats: {beat_count}")
        
        self.analyze_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.export_edl_btn.configure(state="normal")
        self.export_csv_btn.configure(state="normal")
        self.export_fcpxml_btn.configure(state="normal")

    def analysis_failed(self, error_msg):
        self.status_label.configure(text="Analysis Failed")
        messagebox.showerror("Error", error_msg)
        self.analyze_btn.configure(state="normal")
        self.select_btn.configure(state="normal")

    def export_edl(self):
        if not self.beat_times.any():
            return
        
        out_path = filedialog.asksaveasfilename(defaultextension=".edl", filetypes=[("EDL File", "*.edl")])
        if out_path:
            try:
                export_to_edl(self.beat_times, out_path)
                messagebox.showinfo("Success", f"Saved to {out_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_csv(self):
        if not self.beat_times.any():
            return
        
        out_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv")])
        if out_path:
            try:
                export_to_csv_markers(self.beat_times, out_path)
                messagebox.showinfo("Success", f"Saved to {out_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_fcpxml(self):
        if not self.beat_times.any():
            return
        
        out_path = filedialog.asksaveasfilename(defaultextension=".fcpxml", filetypes=[("FCPXML File", "*.fcpxml")])
        if out_path:
            try:
                export_to_fcpxml(self.beat_times, out_path, duration_seconds=self.duration)
                messagebox.showinfo("Success", f"Saved to {out_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = BeatAnalyzerApp()
    app.mainloop()
