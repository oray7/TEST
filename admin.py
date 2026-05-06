import json
import os
from tkinter import messagebox, simpledialog
import customtkinter as ctk
from keygen import generate_key, load_keys, save_keys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

STATUS_COLOR = {"active": "#22c55e", "revoked": "#ef4444"}


class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EmailPro — Admin Panel")
        self.geometry("820x560")
        self.minsize(700, 480)
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="#0d1117", corner_radius=0, height=64)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        ctk.CTkLabel(header, text="🛡️  Admin Panel",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=24, pady=16)

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=16, pady=12)

        ctk.CTkButton(btn_frame, text="+ New Key", width=110, height=36,
                      corner_radius=8, font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._new_key).pack(side="left", padx=(0, 8))

        ctk.CTkButton(btn_frame, text="↻ Refresh", width=100, height=36,
                      corner_radius=8, fg_color="#21262d", hover_color="#30363d",
                      font=ctk.CTkFont(size=13), command=self._refresh).pack(side="left")

        # Table area
        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="#0d1117", corner_radius=0)
        self.table_frame.grid(row=1, column=0, sticky="nsew")
        self.table_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        self._draw_table_header()
        self._refresh()

    def _draw_table_header(self):
        cols = ["License Key", "Note / Customer", "Created", "Status", "Actions"]
        widths = [200, 200, 140, 80, 140]
        for i, (col, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(self.table_frame, text=col, width=w, anchor="w",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="#6e7681").grid(row=0, column=i, padx=(16 if i == 0 else 8, 0), pady=(12, 6), sticky="w")

    def _refresh(self):
        for w in self.table_frame.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()

        keys = load_keys()
        if not keys:
            ctk.CTkLabel(self.table_frame, text="No keys yet. Click '+ New Key' to generate one.",
                         text_color="#6e7681").grid(row=1, column=0, columnspan=5, pady=40)
            return

        for i, entry in enumerate(reversed(keys), start=1):
            row = len(keys) - i

            ctk.CTkLabel(self.table_frame, text=entry["key"], anchor="w",
                         font=ctk.CTkFont(family="Courier", size=12), width=200).grid(
                row=i, column=0, padx=(16, 8), pady=6, sticky="w")

            note_lbl = ctk.CTkLabel(self.table_frame, text=entry.get("note") or "—",
                                    anchor="w", width=200, text_color="#8b949e")
            note_lbl.grid(row=i, column=1, padx=8, pady=6, sticky="w")

            ctk.CTkLabel(self.table_frame, text=entry.get("created", "—"),
                         anchor="w", width=140, text_color="#6e7681",
                         font=ctk.CTkFont(size=12)).grid(row=i, column=2, padx=8, pady=6, sticky="w")

            status = entry.get("status", "active")
            ctk.CTkLabel(self.table_frame, text=f"● {status.capitalize()}",
                         text_color=STATUS_COLOR.get(status, "gray"),
                         font=ctk.CTkFont(size=12), width=80, anchor="w").grid(
                row=i, column=3, padx=8, pady=6, sticky="w")

            actions = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            actions.grid(row=i, column=4, padx=8, pady=4, sticky="w")

            ctk.CTkButton(actions, text="Copy", width=52, height=28, corner_radius=6,
                          fg_color="#1f3a5f", hover_color="#1a4a7a", text_color="#58a6ff",
                          font=ctk.CTkFont(size=11),
                          command=lambda k=entry["key"]: self._copy_key(k)).pack(side="left", padx=(0, 4))

            ctk.CTkButton(actions, text="Note", width=52, height=28, corner_radius=6,
                          fg_color="#21262d", hover_color="#30363d",
                          font=ctk.CTkFont(size=11),
                          command=lambda r=row: self._edit_note(r)).pack(side="left", padx=(0, 4))

            if status == "active":
                ctk.CTkButton(actions, text="Revoke", width=64, height=28, corner_radius=6,
                              fg_color="#3d1a1a", hover_color="#5a1a1a", text_color="#ef4444",
                              font=ctk.CTkFont(size=11),
                              command=lambda r=row: self._revoke(r)).pack(side="left", padx=(0, 4))
            else:
                ctk.CTkButton(actions, text="Restore", width=64, height=28, corner_radius=6,
                              fg_color="#1a3a1a", hover_color="#1a5a1a", text_color="#22c55e",
                              font=ctk.CTkFont(size=11),
                              command=lambda r=row: self._restore(r)).pack(side="left", padx=(0, 4))

            ctk.CTkButton(actions, text="Delete", width=58, height=28, corner_radius=6,
                          fg_color="#2a0a0a", hover_color="#4a0a0a", text_color="#ff6b6b",
                          font=ctk.CTkFont(size=11),
                          command=lambda r=row: self._delete(r)).pack(side="left")

    def _new_key(self):
        note = simpledialog.askstring("New Key", "Customer name or note (optional):", parent=self)
        if note is None:
            return
        key = generate_key(note.strip())
        self._refresh()
        self.clipboard_clear()
        self.clipboard_append(key)
        messagebox.showinfo("Key Generated", f"{key}\n\nCopied to clipboard.")

    def _copy_key(self, key):
        self.clipboard_clear()
        self.clipboard_append(key)
        self.update()

    def _edit_note(self, row):
        keys = load_keys()
        current = keys[row].get("note", "")
        new_note = simpledialog.askstring("Edit Note", "Customer name / note:", initialvalue=current, parent=self)
        if new_note is not None:
            keys[row]["note"] = new_note.strip()
            save_keys(keys)
            self._refresh()

    def _revoke(self, row):
        keys = load_keys()
        key = keys[row]["key"]
        if messagebox.askyesno("Revoke Key", f"Revoke this key?\n{key}"):
            keys[row]["status"] = "revoked"
            save_keys(keys)
            self._refresh()

    def _restore(self, row):
        keys = load_keys()
        keys[row]["status"] = "active"
        save_keys(keys)
        self._refresh()

    def _delete(self, row):
        keys = load_keys()
        key = keys[row]["key"]
        if messagebox.askyesno("Delete Key", f"Permanently delete this key?\n{key}\n\nThis cannot be undone."):
            keys.pop(row)
            save_keys(keys)
            self._refresh()


if __name__ == "__main__":
    AdminApp().mainloop()
