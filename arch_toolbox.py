import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog, ttk


class ArchToolboxApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Arch Maintenance & Security Toolbox")
        self.root.geometry("850x680")

        self.sudo_password = None

        # Configurazione interfaccia a schede
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame Scheda Manutenzione
        self.tab_maintenance = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_maintenance, text="Manutenzione & Pulizia")

        # Frame Scheda Sicurezza
        self.tab_security = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_security, text="Screening & Sicurezza")

        self.create_maintenance_widgets()
        self.create_security_widgets()

        # Richiedi la password sudo subito dopo aver mostrato la finestra principale
        self.root.after(100, self.check_sudo_password)

    def check_sudo_password(self):
        """Apre il popup grafico per la password di root dopo l'avvio della GUI."""
        pwd = simpledialog.askstring(
            "Autenticazione Sudo",
            "Inserisci la password di root per continuare:",
            show="*",
            parent=self.root,
        )
        if not pwd:
            messagebox.showwarning(
                "Attenzione",
                "Nessuna password inserita. Alcune funzioni amministrative potrebbero non funzionare.",
            )
            return

        process = subprocess.run(
            "sudo -S true",
            input=pwd + "\n",
            shell=True,
            text=True,
            capture_output=True,
        )
        if process.returncode != 0:
            messagebox.showerror(
                "Errore", "Password errata o privilegi non sufficienti."
            )
        else:
            self.sudo_password = pwd

    def create_maintenance_widgets(self):
        lbl = ttk.Label(
            self.tab_maintenance,
            text="Gestione pacchetti e pulizia ordinaria (senza conferme):",
            font=("Arial", 11, "bold"),
        )
        lbl.pack(pady=10)

        ttk.Button(
            self.tab_maintenance,
            text="Rimuovi Pacchetti Orfani (yay -Yc)",
            command=lambda: self.run_command_live(
                "yay -Yc --noconfirm", self.m_output, "orphans"
            ),
        ).pack(fill="x", padx=20, pady=5)

        ttk.Button(
            self.tab_maintenance,
            text="Pulisci Cache Pacman (Radicale)",
            command=lambda: self.run_command_live(
                "pacman -Scc --noconfirm", self.m_output, "cache", use_sudo=True
            ),
        ).pack(fill="x", padx=20, pady=5)

        self.m_output = scrolledtext.ScrolledText(
            self.tab_maintenance, height=18, wrap=tk.WORD
        )
        self.m_output.pack(fill="both", expand=True, padx=20, pady=10)

    def create_security_widgets(self):
        lbl = ttk.Label(
            self.tab_security,
            text="Verifiche e controlli di sicurezza del sistema:",
            font=("Arial", 11, "bold"),
        )
        lbl.pack(pady=10)

        ttk.Button(
            self.tab_security,
            text="Verifica Stato Firewall (UFW)",
            command=lambda: self.run_command_live(
                "ufw status verbose", self.s_output, "ufw", use_sudo=True
            ),
        ).pack(fill="x", padx=20, pady=5)

        ttk.Button(
            self.tab_security,
            text="Controlla Porte di Rete Aperte (ss)",
            command=lambda: self.run_command_live(
                "ss -tulnp", self.s_output, "ports", use_sudo=True
            ),
        ).pack(fill="x", padx=20, pady=5)

        ttk.Button(
            self.tab_security,
            text="Verifica Vulnerabilità Pacchetti (arch-audit)",
            command=lambda: self.run_command_live(
                "arch-audit", self.s_output, "audit"
            ),
        ).pack(fill="x", padx=20, pady=5)

        self.s_output = scrolledtext.ScrolledText(
            self.tab_security, height=18, wrap=tk.WORD
        )
        self.s_output.pack(fill="both", expand=True, padx=20, pady=10)

    def run_command_live(self, cmd, text_widget, task_type, use_sudo=False):
        text_widget.delete("1.0", tk.END)
        full_cmd = cmd
        if use_sudo and self.sudo_password:
            full_cmd = f"echo {self.sudo_password} | sudo -S {cmd}"

        text_widget.insert(
            tk.END, f"$ {cmd}\n[Esecuzione in corso...]\n" + "-" * 40 + "\n"
        )

        def target():
            full_output = ""
            try:
                process = subprocess.Popen(
                    full_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )

                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        if "[sudo] password" in line:
                            continue
                        full_output += line
                        self.root.after(
                            0, lambda l=line: text_widget.insert(tk.END, l)
                        )
                        self.root.after(0, lambda: text_widget.see(tk.END))

                rc = process.poll()
                self.root.after(
                    0,
                    lambda: text_widget.insert(
                        tk.END,
                        "\n" + "-" * 40 + f"\n[Comando completato con codice {rc}]\n",
                    ),
                )

                self.root.after(
                    0, lambda: self.evaluate_and_alert(task_type, full_output, rc)
                )

            except Exception as e:
                err_msg = str(e)
                self.root.after(
                    0,
                    lambda: text_widget.insert(
                        tk.END, f"\nErrore di esecuzione: {err_msg}"
                    ),
                )
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Errore Critico", f"Impossibile completare l'azione:\n{err_msg}"
                    ),
                )

        threading.Thread(target=target, daemon=True).start()

    def evaluate_and_alert(self, task_type, output, return_code):
        if task_type == "ufw":
            if (
                "Default: deny" in output
                or "Status: active" in output
                or "Logging:" in output
            ):
                messagebox.showinfo("Esito UFW", "Firewall UFW attivo e protetto.")
            else:
                messagebox.showwarning(
                    "ATTENZIONE UFW", "Il Firewall UFW NON è attivo!"
                )

        elif task_type == "audit":
            high_risks = []
            for line in output.splitlines():
                if "high risk" in line.lower():
                    parts = line.split("is affected")
                    if len(parts) > 0:
                        high_risks.append(parts[0].strip() + " is affected")

            if high_risks:
                msg = (
                    "Rilevate vulnerabilità di livello HIGH:\n\n"
                    + "\n".join(f"• {r}" for r in high_risks)
                )
                messagebox.showerror("CRITICITÀ SICUREZZA (HIGH)", msg)
            elif return_code != 0:
                messagebox.showwarning(
                    "Avviso Audit",
                    "Il comando arch-audit ha restituito un codice anomalo.",
                )
            else:
                messagebox.showinfo(
                    "Esito Audit",
                    "Nessuna vulnerabilità di livello High rilevata nei pacchetti.",
                )

        elif task_type == "ports":
            if return_code == 0:
                lines = output.splitlines()
                services_only = []
                for line in lines:
                    if "LISTEN" in line or "UNCONN" in line:
                        proc_name = ""
                        if 'users:(("' in line:
                            try:
                                start = line.find('users:(("') + 9
                                end = line.find('"', start)
                                proc_name = line[start:end]
                            except Exception:
                                pass
                        if proc_name and proc_name not in services_only:
                            services_only.append(proc_name)

                count = len(services_only)
                summary_msg = f"Servizi con porte aperte ({count}):\n\n"
                for s in services_only:
                    summary_msg += f"• {s}\n"

                messagebox.showinfo("Servizi in Ascolto", summary_msg)
            else:
                messagebox.showerror(
                    "Errore Porte", "Impossibile eseguire il comando di scansione porte."
                )

        elif task_type == "orphans":
            if return_code == 0:
                if (
                    "no orphans" in output.lower()
                    or "nessun" in output.lower()
                    or "not found" in output.lower()
                ):
                    messagebox.showinfo(
                        "Pulizia Orfani",
                        "Controllo completato: nessun pacchetto orfano trovato.",
                    )
                else:
                    messagebox.showinfo(
                        "Pulizia Orfani",
                        "Rimozione pacchetti orfani eseguita con successo.",
                    )
            else:
                messagebox.showwarning(
                    "Errore Orfani",
                    "La pulizia dei pacchetti orfani ha riscontrato problemi.",
                )

        elif task_type == "cache":
            if return_code == 0:
                messagebox.showinfo(
                    "Pulizia Cache",
                    "Pulizia radicale della cache di Pacman completata con successo.",
                )
            else:
                messagebox.showwarning(
                    "Errore Cache",
                    "La pulizia della cache ha riscontrato anomalie.",
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = ArchToolboxApp(root)
    root.mainloop()
