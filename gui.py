import threading
import time
import os
import json
from tkinter import filedialog, messagebox
import customtkinter as ctk

from license import check_license, activate
from send_emails import get_smtp_settings, get_email_list, send_email

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG       = "#0a0a12"
CARD     = "#12121e"
CARD2    = "#1a1a2e"
BORDER   = "#252545"
ACCENT   = "#5b5ef4"
SUCCESS  = "#22c55e"
DANGER   = "#ef4444"
MUTED    = "#6e7691"
SETTINGS_FILE = "settings.json"

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {"email": "", "delay": 12}

def save_settings_file(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EmailPro")
        self.configure(fg_color=BG)
        self.geometry("780x640")
        self.resizable(False, False)

        self.file_path       = None
        self.email_list_path = None
        self.email_count     = 0
        self.settings        = load_settings()
        self.sending         = False

        if not check_license():
            self._build_activation()
        else:
            self._build_main()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ── Activation ────────────────────────────────────────────────────────────

    def _build_activation(self):
        self._clear()
        self.geometry("460x420")

        outer = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        outer.pack(fill="both", expand=True)

        card = ctk.CTkFrame(outer, fg_color=CARD, corner_radius=24,
                            border_width=1, border_color=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86)

        # Icon circle
        ic = ctk.CTkFrame(card, width=64, height=64, corner_radius=32, fg_color=ACCENT)
        ic.pack(pady=(36, 0))
        ic.pack_propagate(False)
        ctk.CTkLabel(ic, text="✉", font=ctk.CTkFont(size=28)).pack(expand=True)

        ctk.CTkLabel(card, text="EmailPro",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(card, text="Enter your license key to get started",
                     text_color=MUTED, font=ctk.CTkFont(size=13)).pack(pady=(0, 22))

        self.key_entry = ctk.CTkEntry(
            card, height=44, corner_radius=12,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            font=ctk.CTkFont(size=14), border_color=BORDER
        )
        self.key_entry.pack(fill="x", padx=30, pady=(0, 12))
        self.key_entry.bind("<Control-v>", self._paste_key)
        self.key_entry.bind("<Button-3>",  self._paste_key)
        self.key_entry.bind("<Return>",    lambda e: self._try_activate())

        ctk.CTkButton(
            card, text="Activate License", height=46, corner_radius=12,
            fg_color=ACCENT, hover_color="#4a4dd4",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._try_activate
        ).pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkButton(
            card, text="Paste & Activate", height=38, corner_radius=12,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color=CARD2, font=ctk.CTkFont(size=13),
            command=self._paste_and_activate
        ).pack(fill="x", padx=30, pady=(0, 36))

    def _paste_key(self, event=None):
        try:
            self.key_entry.delete(0, "end")
            self.key_entry.insert(0, self.clipboard_get().strip())
        except Exception:
            pass

    def _paste_and_activate(self):
        self._paste_key()
        self._try_activate()

    def _try_activate(self):
        if activate(self.key_entry.get().strip()):
            self.geometry("780x640")
            self.resizable(False, False)
            self._build_main()
        else:
            messagebox.showerror("Invalid Key", "This license key is not valid.")

    # ── Main UI ───────────────────────────────────────────────────────────────

    def _build_main(self):
        self._clear()

        root = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        root.pack(fill="both", expand=True)

        # ── Top bar
        topbar = ctk.CTkFrame(root, fg_color=CARD, corner_radius=0, height=58,
                              border_width=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkLabel(topbar, text="✉  EmailPro",
                     font=ctk.CTkFont(size=17, weight="bold")).pack(side="left", padx=24)

        badge = ctk.CTkFrame(topbar, fg_color="#0f2d1a", corner_radius=20)
        badge.pack(side="right", padx=20, pady=14)
        ctk.CTkLabel(badge, text="● Licensed",
                     text_color=SUCCESS, font=ctk.CTkFont(size=12)).pack(padx=14, pady=4)

        # ── Main content
        body = ctk.CTkFrame(root, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # 3-column top cards
        cols = ctk.CTkFrame(body, fg_color="transparent")
        cols.pack(fill="x")
        cols.columnconfigure((0, 1, 2), weight=1)

        # ── Card 1: Account
        c1 = self._card(cols, "1  Account", col=0)
        self._field_label(c1, "Email address")
        self.email_entry = ctk.CTkEntry(c1, height=38, corner_radius=10,
                                         placeholder_text="you@example.com",
                                         border_color=BORDER)
        self.email_entry.insert(0, self.settings.get("email", ""))
        self.email_entry.pack(fill="x", padx=14, pady=(0, 10))

        self._field_label(c1, "Password")
        self.pass_entry = ctk.CTkEntry(c1, height=38, corner_radius=10,
                                        show="*", placeholder_text="••••••••",
                                        border_color=BORDER)
        self.pass_entry.pack(fill="x", padx=14, pady=(0, 10))

        test_row = ctk.CTkFrame(c1, fg_color="transparent")
        test_row.pack(fill="x", padx=14, pady=(0, 14))
        self.login_btn = ctk.CTkButton(test_row, text="Test Login", height=34,
                                       corner_radius=8, fg_color=CARD2,
                                       hover_color=BORDER, border_width=1,
                                       border_color=BORDER,
                                       font=ctk.CTkFont(size=12),
                                       command=self._test_login)
        self.login_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.login_status = ctk.CTkLabel(test_row, text="—", width=28,
                                          font=ctk.CTkFont(size=18), text_color=MUTED)
        self.login_status.pack(side="left")

        # ── Card 2: Files
        c2 = self._card(cols, "2  Files", col=1)

        self._field_label(c2, "Email list (.txt)")
        list_row = ctk.CTkFrame(c2, fg_color="transparent")
        list_row.pack(fill="x", padx=14, pady=(0, 10))
        self.list_btn = ctk.CTkButton(list_row, text="Browse file", height=38,
                                      corner_radius=10, fg_color=CARD2,
                                      hover_color=BORDER, border_width=1,
                                      border_color=BORDER,
                                      command=self._load_list)
        self.list_btn.pack(fill="x")
        self.list_info = ctk.CTkLabel(list_row, text="No file selected",
                                       text_color=MUTED, font=ctk.CTkFont(size=11))
        self.list_info.pack(anchor="w", pady=(4, 0))

        self._field_label(c2, "Attach CV (optional)")
        cv_row = ctk.CTkFrame(c2, fg_color="transparent")
        cv_row.pack(fill="x", padx=14, pady=(0, 16))
        self.cv_btn = ctk.CTkButton(cv_row, text="Browse file", height=38,
                                    corner_radius=10, fg_color=CARD2,
                                    hover_color=BORDER, border_width=1,
                                    border_color=BORDER,
                                    command=self._load_cv)
        self.cv_btn.pack(fill="x")
        self.cv_info = ctk.CTkLabel(cv_row, text="No file attached",
                                     text_color=MUTED, font=ctk.CTkFont(size=11))
        self.cv_info.pack(anchor="w", pady=(4, 0))

        # ── Card 3: Stats + Delay
        c3 = self._card(cols, "3  Stats & Delay", col=2)

        self.stat_sent = self._stat_widget(c3, "Sent", "0", SUCCESS)
        ctk.CTkFrame(c3, height=1, fg_color=BORDER).pack(fill="x", padx=14, pady=2)
        self.stat_fail = self._stat_widget(c3, "Failed", "0", DANGER)
        ctk.CTkFrame(c3, height=1, fg_color=BORDER).pack(fill="x", padx=14, pady=2)
        self.stat_left = self._stat_widget(c3, "Remaining", "—", MUTED)
        ctk.CTkFrame(c3, height=1, fg_color=BORDER).pack(fill="x", padx=14, pady=6)

        delay_row = ctk.CTkFrame(c3, fg_color="transparent")
        delay_row.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(delay_row, text="Delay", font=ctk.CTkFont(size=12),
                     text_color=MUTED).pack(side="left")
        self.delay_lbl = ctk.CTkLabel(delay_row, text=f"{self.settings.get('delay', 12)}s",
                                       font=ctk.CTkFont(size=12, weight="bold"),
                                       text_color=ACCENT)
        self.delay_lbl.pack(side="right")

        self.delay_slider = ctk.CTkSlider(c3, from_=5, to=60, number_of_steps=55,
                                           button_color=ACCENT, button_hover_color="#4a4dd4",
                                           command=self._on_delay_change)
        self.delay_slider.set(self.settings.get("delay", 12))
        self.delay_slider.pack(fill="x", padx=14, pady=(0, 14))

        # ── Progress bar
        prog_card = ctk.CTkFrame(body, fg_color=CARD, corner_radius=16,
                                  border_width=1, border_color=BORDER)
        prog_card.pack(fill="x", pady=(14, 0))

        prog_inner = ctk.CTkFrame(prog_card, fg_color="transparent")
        prog_inner.pack(fill="x", padx=16, pady=12)

        self.status_dot = ctk.CTkLabel(prog_inner, text="●  Ready to send",
                                        text_color=MUTED, font=ctk.CTkFont(size=13))
        self.status_dot.pack(side="left")

        self.progress_pct = ctk.CTkLabel(prog_inner, text="0%",
                                          text_color=MUTED, font=ctk.CTkFont(size=13))
        self.progress_pct.pack(side="right")

        self.progress = ctk.CTkProgressBar(prog_card, height=6, corner_radius=3,
                                            progress_color=ACCENT, fg_color=CARD2)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=16, pady=(0, 14))

        # ── Send button
        self.send_btn = ctk.CTkButton(
            body, text="🚀  Start Sending", height=52, corner_radius=16,
            fg_color=ACCENT, hover_color="#4a4dd4",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start
        )
        self.send_btn.pack(fill="x", pady=14)

        # ── Log
        log_card = ctk.CTkFrame(body, fg_color=CARD, corner_radius=16,
                                  border_width=1, border_color=BORDER)
        log_card.pack(fill="both", expand=True)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(log_header, text="Activity Log",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=MUTED).pack(side="left")
        ctk.CTkButton(log_header, text="Clear", width=52, height=24,
                      corner_radius=6, fg_color=CARD2, hover_color=BORDER,
                      font=ctk.CTkFont(size=11), text_color=MUTED,
                      command=self._clear_log).pack(side="right")

        self.log = ctk.CTkTextbox(log_card, corner_radius=0, fg_color="transparent",
                                   font=ctk.CTkFont(family="Courier", size=12),
                                   state="disabled", wrap="none")
        self.log.pack(fill="both", expand=True, padx=8, pady=(6, 10))

        self.log.tag_config("ok",   foreground=SUCCESS)
        self.log.tag_config("err",  foreground=DANGER)
        self.log.tag_config("info", foreground=MUTED)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _card(self, parent, title, col):
        outer = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16,
                             border_width=1, border_color=BORDER)
        outer.grid(row=0, column=col, sticky="nsew",
                   padx=(0 if col == 0 else 10, 0), pady=0)
        ctk.CTkLabel(outer, text=title, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=MUTED).pack(anchor="w", padx=14, pady=(14, 8))
        ctk.CTkFrame(outer, height=1, fg_color=BORDER).pack(fill="x", padx=14, pady=(0, 10))
        return outer

    def _field_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, anchor="w",
                     font=ctk.CTkFont(size=12), text_color=MUTED).pack(
            fill="x", padx=14, pady=(0, 4))

    def _stat_widget(self, parent, label, value, color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=6)
        ctk.CTkLabel(row, text=label, anchor="w",
                     font=ctk.CTkFont(size=12), text_color=MUTED).pack(side="left")
        val_lbl = ctk.CTkLabel(row, text=value, anchor="e",
                               font=ctk.CTkFont(size=18, weight="bold"),
                               text_color=color)
        val_lbl.pack(side="right")
        return val_lbl

    def _on_delay_change(self, val):
        v = int(val)
        self.delay_lbl.configure(text=f"{v}s")
        self.settings["delay"] = v
        save_settings_file(self.settings)

    def _test_login(self):
        import smtplib
        email    = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not email or not password:
            messagebox.showwarning("Missing Info", "Enter your email and password first.")
            return
        self.login_btn.configure(state="disabled", text="Checking...")
        self.login_status.configure(text="⏳", text_color=MUTED)

        def _check():
            try:
                smtp_server, smtp_port = get_smtp_settings(email)
                with smtplib.SMTP(smtp_server, smtp_port) as s:
                    s.starttls()
                    s.login(email, password)
                self.after(0, self._login_ok)
            except Exception as e:
                self.after(0, self._login_fail, str(e))

        threading.Thread(target=_check, daemon=True).start()

    def _login_ok(self):
        self.login_btn.configure(state="normal", text="✔ Connected",
                                  text_color=SUCCESS, fg_color="#0f2d1a",
                                  border_color=SUCCESS)
        self.login_status.configure(text="✔", text_color=SUCCESS)

    def _login_fail(self, err):
        self.login_btn.configure(state="normal", text="✖ Failed — Retry",
                                  text_color=DANGER, fg_color="#2d0f0f",
                                  border_color=DANGER)
        self.login_status.configure(text="✖", text_color=DANGER)
        messagebox.showerror("Login Failed", f"Could not connect:\n{err}")

    def _load_list(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.email_list_path = path
            self.email_count = sum(1 for l in open(path) if l.strip())
            name = os.path.basename(path)
            self.list_btn.configure(text=f"✔  {name}", text_color=SUCCESS)
            self.list_info.configure(text=f"{self.email_count} recipients found", text_color=SUCCESS)
            self.stat_left.configure(text=str(self.email_count))

    def _load_cv(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_path = path
            name = os.path.basename(path)
            self.cv_btn.configure(text=f"✔  {name}", text_color=SUCCESS)
            self.cv_info.configure(text="Ready to attach", text_color=SUCCESS)

    def _log_write(self, text, tag="info"):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _set_status(self, text, color):
        self.status_dot.configure(text=f"●  {text}", text_color=color)

    def _start(self):
        if self.sending:
            return

        email    = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Missing Info", "Please enter your email and password.")
            return
        if not self.email_list_path:
            messagebox.showwarning("Missing Info", "Please load an email list first.")
            return

        try:
            smtp_server, smtp_port = get_smtp_settings(email)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.settings["email"] = email
        save_settings_file(self.settings)

        emails = get_email_list(self.email_list_path)
        delay  = int(self.delay_slider.get())

        self.sending = True
        self.send_btn.configure(state="disabled", text="⏳  Sending...")
        self.progress.set(0)
        self._set_status("Sending in progress...", ACCENT)

        threading.Thread(
            target=self._send_all,
            args=(emails, smtp_server, smtp_port, email, password, delay),
            daemon=True
        ).start()

    def _send_all(self, emails, smtp_server, smtp_port, email, password, delay):
        total  = len(emails)
        sent   = 0
        failed = 0

        for i, recipient in enumerate(emails):
            ok = send_email(recipient, smtp_server, smtp_port, email, password, self.file_path)

            if ok:
                sent += 1
                self.after(0, self._log_write, f"✔  {recipient}", "ok")
            else:
                failed += 1
                self.after(0, self._log_write, f"✖  {recipient}", "err")

            prog = (i + 1) / total
            remaining = total - (i + 1)
            pct = int(prog * 100)

            self.after(0, self.progress.set, prog)
            self.after(0, self.progress_pct.configure, {"text": f"{pct}%"})
            self.after(0, self.stat_sent.configure, {"text": str(sent)})
            self.after(0, self.stat_fail.configure, {"text": str(failed)})
            self.after(0, self.stat_left.configure, {"text": str(remaining)})

            time.sleep(delay)

        summary = f"\n── Done  ·  ✔ Sent: {sent}  ·  ✖ Failed: {failed} ──"
        self.after(0, self._log_write, summary, "info")
        self.after(0, self._set_status, f"Done — {sent} sent, {failed} failed",
                   SUCCESS if failed == 0 else DANGER)
        self.after(0, lambda: self.send_btn.configure(
            state="normal", text="🚀  Start Sending"))
        self.sending = False


if __name__ == "__main__":
    App().mainloop()
