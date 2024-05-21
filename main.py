import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from deep_translator import GoogleTranslator
import pysrt
import chardet
import threading


class SRTTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT Translator")
        self.root.state('zoomed')  # Open window in full screen

        self.file_paths = []
        self.output_dir = ""

        # Create widgets
        self.select_button = tk.Button(
            root,
            text="Carregar",
            command=self.select_files,
            width=20
        )
        self.output_dir_button = tk.Button(
            root,
            text="Salvar em...",
            command=self.select_output_dir,
            width=20
        )
        self.translate_button = tk.Button(
            root,
            text="Traduzir",
            command=self.start_translation_thread,
            width=20
        )
        self.exit_button = tk.Button(
            root,
            text="Sair",
            command=root.quit,
            width=20
        )

        self.file_listbox = tk.Listbox(
            root,
            width=100,  # Adjust the width to display only file names
            height=15
        )
        self.progress = ttk.Progressbar(
            root,
            orient='horizontal',
            length=600,
            mode='determinate'
        )
        self.progress_label = tk.Label(
            root,
            text="",
            font=("Calibri", 11, "bold")
        )
        self.path_label = tk.Label(
            root,
            text="",
            wraplength=600,  # Adjust wraplength as necessary
            anchor='w',
            font=("Calibri", 11, "bold")  # Make the label text bold
        )

        # Layout widgets
        self.select_button.pack(pady=10)
        # Position the label below the select button
        self.path_label.pack(pady=10)
        self.output_dir_button.pack(pady=10)
        self.file_listbox.pack(pady=10)
        self.translate_button.pack(pady=10)
        self.progress.pack(pady=10)
        self.progress_label.pack(pady=10)
        self.exit_button.pack(pady=10)

    def select_files(self):
        self.file_paths = filedialog.askopenfilenames(
            title="Selecionar arquivos .srt",
            filetypes=[("SRT files", "*.srt")]
        )
        if self.file_paths:
            self.file_listbox.delete(0, tk.END)
            for file_path in self.file_paths:
                file_name = os.path.basename(file_path)
                self.file_listbox.insert(tk.END, file_name)

            # Extract directory path and update the path label
            directory_path = os.path.dirname(self.file_paths[0])
            self.path_label.config(text=f"Diretório: {directory_path}")
            self.path_label.pack()

            messagebox.showinfo(
                "Arquivos Selecionados",
                f"{len(self.file_paths)} arquivos selecionados."
            )

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(
            title="Selecionar Diretório de Saída"
        )
        if self.output_dir:
            messagebox.showinfo(
                "Diretório Selecionado",
                f"Arquivos traduzidos serão salvos em: {self.output_dir}"
            )

    def detect_encoding(self, file_path):
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        return encoding

    def load_srt(self, file_path):
        encoding = self.detect_encoding(file_path)
        subtitles = pysrt.open(file_path, encoding=encoding)
        return subtitles

    def clear_progress_label(self):
        self.progress_label.config(text="")

    def start_translation_thread(self):
        translation_thread = threading.Thread(target=self.translate_files)
        translation_thread.start()

    def translate_files(self):
        if not self.file_paths:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado.")
            return

        if not self.output_dir:
            messagebox.showwarning("Aviso", "Nenhum diretório selecionado.")
            return

        translator = GoogleTranslator(source='en', target='pt')

        for idx, file_path in enumerate(self.file_paths):
            try:
                self.progress['value'] = 0
                self.root.update_idletasks()
                subtitles = self.load_srt(file_path)

                for i, subtitle in enumerate(subtitles):
                    subtitle.text = translator.translate(subtitle.text)
                    progress_percent = ((i + 1) / len(subtitles)) * 100
                    self.progress['value'] = progress_percent
                    self.progress_label.config(
                        text=f"Traduzindo arquivo [{os.path.basename(
                            file_path
                        )}] --> {int(progress_percent)}%"
                    )
                    self.root.update_idletasks()

                base_name = os.path.basename(file_path)
                output_path = os.path.join(
                    self.output_dir, base_name.replace("_en.srt", "_pt.srt")
                )
                subtitles.save(output_path, encoding='utf-8')

                # Update file listbox to show "[Traduzido]"
                self.file_listbox.delete(idx)
                texto = " >>>> [Traduzido]"
                file_name_translated = os.path.basename(file_path) + texto
                self.file_listbox.insert(idx, file_name_translated)

                # Clear progress label after each file is translated
                self.clear_progress_label()

            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao traduzir {file_path}: {e}"
                )

        messagebox.showinfo("Sucesso", "Tradução concluída!")


if __name__ == "__main__":
    root = tk.Tk()
    app = SRTTranslatorApp(root)
    root.mainloop()
