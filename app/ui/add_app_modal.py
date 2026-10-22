import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from app.icon_extractor import get_app_icon
from app.launcher import launch_app

CATEGORIES = ["Geral", "Produtividade", "Navegadores", "Comunicação", "Desenvolvimento", "Jogos", "Sistema"]

class AddAppModal(ctk.CTkToplevel):
    def __init__(self, master, config_manager, app_to_edit=None, on_saved=None):
        super().__init__(master)
        self.config_manager = config_manager
        self.app_to_edit = app_to_edit
        self.on_saved = on_saved

        self.title("Editar Aplicativo" if app_to_edit else "Adicionar Novo Aplicativo")
        self.geometry("450x610")
        self.resizable(False, False)
        self.configure(fg_color="#12151d")

        # Keep on top and center
        self.attributes("-topmost", True)
        self._center_window()

        self._build_ui()
        self.transient(master)
        self.grab_set()

    def _center_window(self):
        self.update_idletasks()
        w = 450
        h = 610
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(20, 10))

        title_text = "Editar Aplicativo" if self.app_to_edit else "✦ Adicionar Aplicativo"
        title_lbl = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#f8fafc"
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            header_frame,
            text="Adicione um executável, atalho ou comando para acesso rápido.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94a3b8"
        )
        subtitle_lbl.pack(anchor="w")

        # Main Form Container
        form_frame = ctk.CTkFrame(self, fg_color="#181b24", corner_radius=12, border_width=1, border_color="#262b3a")
        form_frame.pack(fill="both", expand=True, padx=24, pady=10)

        # 1. Caminho do Executável / Atalho
        path_lbl = ctk.CTkLabel(form_frame, text="Caminho do Executável ou Atalho:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1")
        path_lbl.pack(anchor="w", padx=16, pady=(14, 4))

        path_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        path_row.pack(fill="x", padx=16, pady=(0, 10))

        self.path_entry = ctk.CTkEntry(
            path_row,
            placeholder_text="C:\\Program Files\\... ou nome.exe",
            fg_color="#0f1118",
            border_color="#2c3345",
            font=ctk.CTkFont(size=12),
            height=34
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.path_entry.bind("<KeyRelease>", lambda e: self._on_path_changed())

        browse_btn = ctk.CTkButton(
            path_row,
            text="📁 Procurar",
            width=80,
            height=34,
            corner_radius=8,
            fg_color="#334155",
            hover_color="#475569",
            command=self._browse_file
        )
        browse_btn.pack(side="right")

        # 2. Nome do App & Preview do Ícone
        name_lbl = ctk.CTkLabel(form_frame, text="Nome de Exibição:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1")
        name_lbl.pack(anchor="w", padx=16, pady=(0, 4))

        name_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        name_row.pack(fill="x", padx=16, pady=(0, 10))

        # Icon preview box (clickable to choose custom icon)
        self.icon_preview = ctk.CTkLabel(name_row, text="", width=36, height=36, fg_color="#0f1118", corner_radius=8)
        self.icon_preview.pack(side="left", padx=(0, 8))
        self.icon_preview.bind("<Button-1>", lambda e: self._browse_custom_icon())

        self.name_entry = ctk.CTkEntry(
            name_row,
            placeholder_text="Ex: Google Chrome, Discord, Spotify...",
            fg_color="#0f1118",
            border_color="#2c3345",
            font=ctk.CTkFont(size=12),
            height=34
        )
        self.name_entry.pack(side="left", fill="x", expand=True)

        # 3. Ícone Personalizado (Opcional)
        icon_field_lbl = ctk.CTkLabel(form_frame, text="Ícone Personalizado (Opcional):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1")
        icon_field_lbl.pack(anchor="w", padx=16, pady=(0, 4))

        icon_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        icon_row.pack(fill="x", padx=16, pady=(0, 10))

        self.icon_path_entry = ctk.CTkEntry(
            icon_row,
            placeholder_text="Automático (ou escolha .ico, .png, .jpg...)",
            fg_color="#0f1118",
            border_color="#2c3345",
            font=ctk.CTkFont(size=11),
            height=34
        )
        self.icon_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.icon_path_entry.bind("<KeyRelease>", lambda e: self._on_path_changed())

        clear_icon_btn = ctk.CTkButton(
            icon_row,
            text="✕",
            width=32,
            height=34,
            corner_radius=8,
            fg_color="#242b3a",
            hover_color="#ef4444",
            text_color="#94a3b8",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._clear_custom_icon
        )
        clear_icon_btn.pack(side="right")

        choose_icon_btn = ctk.CTkButton(
            icon_row,
            text="🖼 Escolher...",
            width=88,
            height=34,
            corner_radius=8,
            fg_color="#334155",
            hover_color="#475569",
            command=self._browse_custom_icon
        )
        choose_icon_btn.pack(side="right", padx=(0, 4))

        # 4. Categoria
        cat_lbl = ctk.CTkLabel(form_frame, text="Categoria:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1")
        cat_lbl.pack(anchor="w", padx=16, pady=(0, 4))

        self.cat_menu = ctk.CTkComboBox(
            form_frame,
            values=CATEGORIES,
            fg_color="#0f1118",
            border_color="#2c3345",
            button_color="#334155",
            button_hover_color="#475569",
            height=32
        )
        self.cat_menu.pack(fill="x", padx=16, pady=(0, 10))
        self.cat_menu.set("Geral")

        # 5. Argumentos Opcionais
        arg_lbl = ctk.CTkLabel(form_frame, text="Parâmetros / Argumentos (Opcional):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1")
        arg_lbl.pack(anchor="w", padx=16, pady=(0, 4))

        self.arg_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: --incognito, --profile-directory, etc.",
            fg_color="#0f1118",
            border_color="#2c3345",
            font=ctk.CTkFont(size=12),
            height=34
        )
        self.arg_entry.pack(fill="x", padx=16, pady=(0, 12))

        # 6. Switch: Auto-Start
        self.auto_switch = ctk.CTkSwitch(
            form_frame,
            text="⚡ Iniciar este app automaticamente com o Sidebar",
            font=ctk.CTkFont(size=12, weight="bold"),
            progress_color="#10b981",
            text_color="#e2e8f0"
        )
        self.auto_switch.pack(anchor="w", padx=16, pady=(4, 16))

        # Populate if editing
        if self.app_to_edit:
            self.path_entry.insert(0, self.app_to_edit.get("path", ""))
            self.name_entry.insert(0, self.app_to_edit.get("name", ""))
            custom_icon = self.app_to_edit.get("custom_icon", "")
            if custom_icon:
                self.icon_path_entry.insert(0, custom_icon)
            self.arg_entry.insert(0, self.app_to_edit.get("arguments", ""))
            cat = self.app_to_edit.get("category", "Geral")
            if cat in CATEGORIES:
                self.cat_menu.set(cat)
            if self.app_to_edit.get("auto_start", False):
                self.auto_switch.select()
            else:
                self.auto_switch.deselect()
            self._update_icon_preview()

        # Footer Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(10, 20))

        test_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Testar",
            width=80,
            height=36,
            corner_radius=8,
            fg_color="#222734",
            hover_color="#333b4e",
            text_color="#94a3b8",
            command=self._test_run
        )
        test_btn.pack(side="left")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=90,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#1e2433",
            text_color="#94a3b8",
            command=self.destroy
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Salvar",
            width=110,
            height=36,
            corner_radius=8,
            fg_color="#4f46e5",
            hover_color="#6366f1",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._save
        )
        save_btn.pack(side="right")

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Selecione o Executável ou Atalho",
            filetypes=[
                ("Aplicativos e Atalhos (*.exe, *.lnk, *.bat)", "*.exe;*.lnk;*.bat;*.cmd"),
                ("Todos os Arquivos (*.*)", "*.*")
            ]
        )
        if file_path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, file_path)

            # Auto suggest name if empty
            if not self.name_entry.get().strip():
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                # Capitalize nicely
                clean_name = base_name.replace("_", " ").replace("-", " ").title()
                self.name_entry.insert(0, clean_name)

            self._update_icon_preview()

    def _browse_custom_icon(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Selecione um Ícone Personalizado (Opcional)",
            filetypes=[
                ("Imagens e Ícones (*.ico, *.png, *.jpg, *.webp)", "*.ico;*.png;*.jpg;*.jpeg;*.webp;*.bmp"),
                ("Todos os Arquivos (*.*)", "*.*")
            ]
        )
        if file_path:
            self.icon_path_entry.delete(0, "end")
            self.icon_path_entry.insert(0, file_path)
            self._update_icon_preview()

    def _clear_custom_icon(self):
        self.icon_path_entry.delete(0, "end")
        self._update_icon_preview()

    def _on_path_changed(self):
        self._update_icon_preview()

    def _update_icon_preview(self):
        path = self.path_entry.get().strip()
        name = self.name_entry.get().strip() or "App"
        custom_icon = self.icon_path_entry.get().strip() if hasattr(self, "icon_path_entry") else ""
        icon_pil = get_app_icon(path, app_name=name, size=32, custom_icon=custom_icon)
        ctk_img = ctk.CTkImage(light_image=icon_pil, dark_image=icon_pil, size=(28, 28))
        self.icon_preview.configure(image=ctk_img)

    def _test_run(self):
        path = self.path_entry.get().strip()
        if not path:
            messagebox.showwarning("Aviso", "Informe o caminho para testar a execução.", parent=self)
            return
        temp_data = {"path": path, "arguments": self.arg_entry.get().strip()}
        success, msg = launch_app(temp_data)
        if success:
            messagebox.showinfo("Sucesso", "Aplicativo disparado com sucesso!", parent=self)
        else:
            messagebox.showerror("Erro", f"Não foi possível iniciar o aplicativo:\n{msg}", parent=self)

    def _save(self):
        path = self.path_entry.get().strip()
        name = self.name_entry.get().strip()
        args = self.arg_entry.get().strip()
        cat = self.cat_menu.get().strip() or "Geral"
        auto_start = bool(self.auto_switch.get())
        custom_icon = self.icon_path_entry.get().strip() if hasattr(self, "icon_path_entry") else ""

        if not path:
            messagebox.showwarning("Aviso", "Por favor, especifique o caminho do aplicativo.", parent=self)
            return

        if not name:
            name = os.path.splitext(os.path.basename(path))[0].title()

        if self.app_to_edit:
            self.config_manager.update_app(
                self.app_to_edit["id"],
                name=name,
                path=path,
                arguments=args,
                category=cat,
                auto_start=auto_start,
                custom_icon=custom_icon
            )
        else:
            self.config_manager.add_app(
                name=name,
                path=path,
                arguments=args,
                category=cat,
                auto_start=auto_start,
                custom_icon=custom_icon
            )

        if self.on_saved:
            self.on_saved()

        self.destroy()
