import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser
import sys


class WebPConverterApp:
    def __init__(self, root):
        self.root = root  # ✅ IMPORTANTE para que funcione bien
        self.root.title("Optimizador WebP - MikeWordpress")

        # Manejo del icono
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'mikewordpress_icon.ico')
        else:
            icon_path = os.path.join(os.path.dirname(__file__), 'mikewordpress_icon.ico')

        self.root.iconbitmap(icon_path)

        self.selected_files = []
        self.output_folder = ""
        self.custom_title = tk.StringVar()
        self.quality = tk.StringVar(value="80")
        self.full_directory_mode = False
        self.base_input_folder = None

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        # Campo título
        ttk.Label(frame, text="Título (opcional):").pack(anchor="w")
        self.title_entry = ttk.Entry(frame, textvariable=self.custom_title, width=40)
        self.title_entry.pack(fill="x", pady=5)

        # Calidad
        ttk.Label(frame, text="Nivel de compresión (calidad):").pack(anchor="w", pady=(10, 0))
        quality_combo = ttk.Combobox(
            frame,
            textvariable=self.quality,
            values=[
                "100 - Baja compresión (mejor calidad)",
                "80 - Media",
                "60 - Alta compresión",
                "40 - Muy alta compresión",
                "20 - Extrema compresión"
            ],
            state="readonly"
        )
        quality_combo.current(1)
        quality_combo.pack(fill="x", pady=5)

        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10, fill="x")
        ttk.Button(btn_frame, text="Seleccionar 1 archivo", command=self.select_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Seleccionar carpeta", command=self.select_folder).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Optimizar directorio completo", command=self.select_full_directory).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Elegir carpeta destino", command=self.select_output_folder).pack(side="left", padx=5)

        # Botón conversión
        ttk.Button(frame, text="Iniciar optimización y conversión", bootstyle="success", command=self.start_conversion).pack(pady=15, fill="x")

        # Progreso
        self.progress = ttk.Progressbar(frame, mode="determinate", bootstyle="info")
        self.progress.pack(fill="x", pady=5)

        # Footer
        footer = ttk.Label(frame, text="Creado por MikeWordpress para sus amigos", font=("Segoe UI", 9), foreground="#aaa")
        footer.pack(side="bottom", pady=10)

    def select_file(self):
        file = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
        if file:
            self.selected_files = [file]
            self.full_directory_mode = False

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.full_directory_mode = False

    def select_full_directory(self):
        folder = filedialog.askdirectory(title="Selecciona el directorio raíz")
        if folder:
            self.full_directory_mode = True
            self.base_input_folder = folder
            self.selected_files = self.get_all_images_in_directory(folder)

    def get_all_images_in_directory(self, root_folder):
        image_files = []
        for dirpath, _, filenames in os.walk(root_folder):
            for f in filenames:
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_files.append(os.path.join(dirpath, f))
        return image_files

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder

    def start_conversion(self):
        if not self.selected_files:
            messagebox.showerror("Error", "Primero selecciona un archivo o carpeta.")
            return
        if not self.output_folder:
            messagebox.showerror("Error", "Selecciona una carpeta de destino.")
            return

        threading.Thread(target=self.convert_images).start()

    def convert_images(self):
        self.progress["maximum"] = len(self.selected_files)
        self.progress["value"] = 0

        quality_value = self.quality.get().split(" - ")[0]

        for i, file_path in enumerate(self.selected_files, start=1):
            name, _ = os.path.splitext(os.path.basename(file_path))
            if self.custom_title.get():
                name = f"{self.custom_title.get()}_{i}"

            if self.full_directory_mode:
                relative_path = os.path.relpath(os.path.dirname(file_path), self.base_input_folder)
                output_dir = os.path.join(self.output_folder, relative_path)
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f"{name}.webp")
            else:
                output_file = os.path.join(self.output_folder, f"{name}.webp")

            command = f'"{os.getcwd()}\\cwebp.exe" -q {quality_value} "{file_path}" -o "{output_file}"'
            subprocess.run(command, shell=True)

            self.progress["value"] = i
            self.root.update_idletasks()

        self.full_directory_mode = False
        webbrowser.open(self.output_folder)
        messagebox.showinfo("Completado", "¡Conversión finalizada!")


if __name__ == "__main__":
    app = ttk.Window(themename="darkly")
    WebPConverterApp(app)
    app.mainloop()
