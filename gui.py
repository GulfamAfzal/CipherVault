import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import json
import os
import sys

BG        = "#0d0f14"
PANEL     = "#13161e"
CARD      = "#1a1e2a"
BORDER    = "#252a38"
ACCENT    = "#00c9a7"
ACCENT2   = "#0077ff"
DANGER    = "#ff4d6d"
TEXT      = "#e8eaf0"
MUTED     = "#6b7280"
SUCCESS   = "#00e5a0"

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_HEAD   = ("Georgia", 13, "bold")
FONT_BODY   = ("Courier New", 10)
FONT_SMALL  = ("Courier New", 9)
FONT_MONO   = ("Courier New", 10, "bold")

VAULT_FILE  = "vault_index.json"   # stores {filename: file_id}

# ── vault index helpers ───────────────────────────────────────────────────────
def load_vault():
    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE) as f:
            return json.load(f)
    return {}

def save_vault(data):
    with open(VAULT_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── main app ──────────────────────────────────────────────────────────────────
class CipherVaultApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CipherVault")
        self.geometry("860x620")
        self.minsize(820, 580)
        self.configure(bg=BG)
        self.resizable(True, True)

        self.vault = load_vault()
        self._build_ui()
        self._refresh_file_list()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── header bar ────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=PANEL, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="⬡", font=("Georgia", 26), fg=ACCENT,
                 bg=PANEL).pack(side="left", padx=(20, 6), pady=10)
        tk.Label(hdr, text="CipherVault", font=FONT_TITLE,
                 fg=TEXT, bg=PANEL).pack(side="left", pady=10)
        tk.Label(hdr, text="zero-knowledge encrypted cloud storage",
                 font=FONT_SMALL, fg=MUTED, bg=PANEL).pack(side="left", padx=14, pady=18)

        # status pill
        self.status_var = tk.StringVar(value="● ready")
        self.status_lbl = tk.Label(hdr, textvariable=self.status_var,
                                   font=FONT_SMALL, fg=ACCENT, bg=PANEL)
        self.status_lbl.pack(side="right", padx=20)

        # ── body split ────────────────────────────────────────────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    def _build_left(self, parent):
        left = tk.Frame(parent, bg=CARD, bd=0,
                        highlightthickness=1, highlightbackground=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left, text="NEW OPERATION", font=FONT_SMALL,
                 fg=ACCENT, bg=CARD).pack(anchor="w", padx=18, pady=(18, 4))
        _divider(left)

        # ── file picker ───────────────────────────────────────────────────────
        tk.Label(left, text="File", font=FONT_SMALL, fg=MUTED,
                 bg=CARD).pack(anchor="w", padx=18, pady=(14, 2))

        row = tk.Frame(left, bg=CARD)
        row.pack(fill="x", padx=18)
        self.file_var = tk.StringVar(value="no file selected")
        tk.Label(row, textvariable=self.file_var, font=FONT_SMALL,
                 fg=TEXT, bg=CARD, anchor="w", width=22,
                 wraplength=160).pack(side="left", fill="x", expand=True)
        _btn(row, "Browse", self._browse_file,
             bg=BORDER, fg=TEXT, padx=8).pack(side="right")

        # ── password ──────────────────────────────────────────────────────────
        tk.Label(left, text="Password", font=FONT_SMALL, fg=MUTED,
                 bg=CARD).pack(anchor="w", padx=18, pady=(14, 2))
        self.pw_var = tk.StringVar()
        pw_entry = tk.Entry(left, textvariable=self.pw_var, show="●",
                            font=FONT_BODY, bg=BORDER, fg=TEXT,
                            insertbackground=ACCENT, relief="flat",
                            highlightthickness=1,
                            highlightcolor=ACCENT,
                            highlightbackground=BORDER)
        pw_entry.pack(fill="x", padx=18, ipady=6)

        # show/hide toggle
        self.show_pw = False
        def toggle_pw():
            self.show_pw = not self.show_pw
            pw_entry.config(show="" if self.show_pw else "●")
            toggle_btn.config(text="hide" if self.show_pw else "show")
        toggle_btn = tk.Label(left, text="show", font=FONT_SMALL,
                              fg=ACCENT2, bg=CARD, cursor="hand2")
        toggle_btn.pack(anchor="e", padx=18)
        toggle_btn.bind("<Button-1>", lambda e: toggle_pw())

        _divider(left)

        # ── action buttons ────────────────────────────────────────────────────
        tk.Label(left, text="ACTION", font=FONT_SMALL, fg=ACCENT,
                 bg=CARD).pack(anchor="w", padx=18, pady=(12, 6))

        _btn(left, "🔒  Encrypt & Upload to Drive",
             self._do_encrypt_upload,
             bg=ACCENT, fg=BG, bold=True).pack(fill="x", padx=18, pady=(0, 8), ipady=8)

        _btn(left, "🔓  Download & Decrypt from Drive",
             self._do_download_decrypt,
             bg=ACCENT2, fg="#fff", bold=True).pack(fill="x", padx=18, pady=(0, 8), ipady=8)

        _divider(left)

        # ── manual file-id input ──────────────────────────────────────────────
        tk.Label(left, text="Manual File ID (optional)", font=FONT_SMALL,
                 fg=MUTED, bg=CARD).pack(anchor="w", padx=18, pady=(12, 2))
        self.fid_var = tk.StringVar()
        tk.Entry(left, textvariable=self.fid_var, font=FONT_SMALL,
                 bg=BORDER, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", highlightthickness=1,
                 highlightcolor=ACCENT2,
                 highlightbackground=BORDER).pack(fill="x", padx=18, ipady=5)
        tk.Label(left, text="Leave blank to use selected file from list →",
                 font=("Courier New", 8), fg=MUTED, bg=CARD,
                 wraplength=200, justify="left").pack(anchor="w", padx=18, pady=(4, 14))

    def _build_right(self, parent):
        right = tk.Frame(parent, bg=CARD, bd=0,
                         highlightthickness=1, highlightbackground=BORDER)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # header row
        hrow = tk.Frame(right, bg=CARD)
        hrow.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 4))
        tk.Label(hrow, text="YOUR ENCRYPTED FILES",
                 font=FONT_SMALL, fg=ACCENT, bg=CARD).pack(side="left")
        _btn(hrow, "⟳ refresh", self._refresh_file_list,
             bg=BORDER, fg=MUTED).pack(side="right")

        _divider(right, row=True)

        # ── file list ─────────────────────────────────────────────────────────
        list_frame = tk.Frame(right, bg=CARD)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=8)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # scrollable canvas
        canvas = tk.Canvas(list_frame, bg=CARD, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical",
                                 command=canvas.yview)
        self.file_inner = tk.Frame(canvas, bg=CARD)
        self.file_inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.file_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # ── log console ───────────────────────────────────────────────────────
        tk.Label(right, text="ACTIVITY LOG", font=FONT_SMALL,
                 fg=ACCENT, bg=CARD).grid(row=2, column=0, sticky="w",
                                          padx=18, pady=(8, 2))
        self.log = tk.Text(right, height=6, bg="#0a0c10", fg=ACCENT,
                           font=FONT_SMALL, relief="flat",
                           insertbackground=ACCENT, state="disabled",
                           wrap="word")
        self.log.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))

    # ── helpers ───────────────────────────────────────────────────────────────
    def _browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.selected_file = path
            self.file_var.set(os.path.basename(path))

    def _log(self, msg, color=TEXT):
        self.log.config(state="normal")
        self.log.insert("end", f"  {msg}\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _set_status(self, msg, color=ACCENT):
        self.status_var.set(msg)
        self.status_lbl.config(fg=color)

    def _refresh_file_list(self):
        self.vault = load_vault()
        for w in self.file_inner.winfo_children():
            w.destroy()

        if not self.vault:
            tk.Label(self.file_inner,
                     text="No encrypted files yet.\nUpload your first file →",
                     font=FONT_SMALL, fg=MUTED, bg=CARD,
                     justify="center").pack(pady=40)
            return

        for name, fid in self.vault.items():
            self._file_card(name, fid)

    def _file_card(self, name, fid):
        card = tk.Frame(self.file_inner, bg=PANEL,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", pady=4)

        # icon + name
        left = tk.Frame(card, bg=PANEL)
        left.pack(side="left", fill="x", expand=True, padx=12, pady=10)

        ext = os.path.splitext(name)[1].upper().lstrip(".") or "FILE"
        icon_bg = ACCENT if ext in ("TXT","PDF","DOCX") else ACCENT2
        tk.Label(left, text=ext, font=("Courier New", 8, "bold"),
                 fg=BG, bg=icon_bg, width=5).pack(side="left", padx=(0, 10))

        info = tk.Frame(left, bg=PANEL)
        info.pack(side="left")
        tk.Label(info, text=name, font=FONT_MONO,
                 fg=TEXT, bg=PANEL).pack(anchor="w")
        tk.Label(info, text=f"id: {fid[:28]}…", font=FONT_SMALL,
                 fg=MUTED, bg=PANEL).pack(anchor="w")

        # select button
        def select(f=fid, n=name):
            self.fid_var.set(f)
            self._log(f"▸ selected: {n}")
            self._set_status(f"● {n} selected")
        _btn(card, "Select", select,
             bg=BORDER, fg=MUTED).pack(side="right", padx=10, pady=10)

        # delete button
        def delete(n=name):
            if messagebox.askyesno("Remove", f"Remove '{n}' from vault index?\n(File stays on Drive)"):
                self.vault.pop(n, None)
                save_vault(self.vault)
                self._refresh_file_list()
                self._log(f"✕ removed from index: {n}", DANGER)
        _btn(card, "✕", delete,
             bg=PANEL, fg=DANGER).pack(side="right", pady=10)

    # ── operations ────────────────────────────────────────────────────────────
    def _do_encrypt_upload(self):
        path = getattr(self, "selected_file", None)
        if not path:
            messagebox.showwarning("No file", "Please select a file first.")
            return
        pw = self.pw_var.get()
        if not pw:
            messagebox.showwarning("No password", "Please enter a password.")
            return

        def run():
            try:
                self._set_status("● encrypting…", ACCENT)
                self._log(f"▸ encrypting: {os.path.basename(path)}")
                from crypto_engine import encrypt_file
                from drive_manager import upload_file
                tmp = "temp_upload.cvault"
                encrypt_file(path, tmp, pw)
                self._log("▸ uploading to Google Drive…")
                self._set_status("● uploading…", ACCENT2)
                fid = upload_file(tmp)
                os.remove(tmp)
                name = os.path.basename(path)
                self.vault[name] = fid
                save_vault(self.vault)
                self._refresh_file_list()
                self._log(f"✔ done! id: {fid}", SUCCESS)
                self._set_status("● upload complete", SUCCESS)
                messagebox.showinfo("Success",
                    f"'{name}' encrypted and uploaded!\n\nFile ID:\n{fid}")
            except Exception as e:
                self._log(f"✖ error: {e}", DANGER)
                self._set_status("● error", DANGER)
                messagebox.showerror("Error", str(e))

        threading.Thread(target=run, daemon=True).start()

    def _do_download_decrypt(self):
        fid = self.fid_var.get().strip()
        if not fid:
            messagebox.showwarning("No File ID",
                "Select a file from the list or paste a File ID.")
            return
        pw = self.pw_var.get()
        if not pw:
            messagebox.showwarning("No password", "Please enter a password.")
            return
        save_path = filedialog.asksaveasfilename(
            title="Save decrypted file as…",
            defaultextension="",
            filetypes=[("All files", "*.*")])
        if not save_path:
            return

        def run():
            try:
                self._set_status("● downloading…", ACCENT2)
                self._log(f"▸ downloading id: {fid[:28]}…")
                from drive_manager import download_file
                from crypto_engine import decrypt_file
                tmp = "temp_download.cvault"
                download_file(fid, tmp)
                self._log("▸ decrypting…")
                self._set_status("● decrypting…", ACCENT)
                decrypt_file(tmp, save_path, pw)
                os.remove(tmp)
                self._log(f"✔ saved: {os.path.basename(save_path)}", SUCCESS)
                self._set_status("● decrypt complete", SUCCESS)
                messagebox.showinfo("Success",
                    f"File decrypted and saved to:\n{save_path}")
            except Exception as e:
                self._log(f"✖ error: {e}", DANGER)
                self._set_status("● error", DANGER)
                messagebox.showerror("Error", str(e))

        threading.Thread(target=run, daemon=True).start()


# ── widget helpers ────────────────────────────────────────────────────────────
def _btn(parent, text, cmd, bg=ACCENT, fg=BG, bold=False, **kw):
    font = ("Courier New", 10, "bold") if bold else FONT_SMALL
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=fg, font=font,
                  relief="flat", cursor="hand2",
                  activebackground=ACCENT, activeforeground=BG,
                  bd=0, **kw)
    return b

def _divider(parent, row=False):
    f = tk.Frame(parent, bg=BORDER, height=1)
    if row:
        f.grid(row=1 if row else None, column=0, sticky="ew",
               padx=18, pady=2)
    else:
        f.pack(fill="x", padx=18, pady=4)


if __name__ == "__main__":
    app = CipherVaultApp()
    app.mainloop()