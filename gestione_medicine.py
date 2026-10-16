import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Nome del database condiviso per l'app
DB_FILE = "non_dimentico.db"


class ModuloMedicine:
    def __init__(self, master_root):
        self.window = tk.Toplevel(master_root)
        self.window.title("Gestione Medicine e Terapie - NonDimentico [SPsoft]")

        # Dimensioni e centramento della finestra
        width, height = 960, 560
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.configure(bg="#2C3E50")

        # Inizializza il database e la tabella medicine
        self.inizializza_db()

        # Titolo della finestra
        lbl_titolo = tk.Label(
            self.window,
            text="Gestione Farmaci, Terapie e Scorte",
            font=("Georgia", 18, "bold italic"),
            bg="#2C3E50",
            fg="#FFD700",
        )
        lbl_titolo.pack(pady=10)

        # --- TABELLA STILE EXCEL (Treeview) ---
        table_frame = tk.Frame(self.window, bg="#2C3E50")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Colonne specifiche per le medicine
        self.columns = (
            "ID",
            "Seleziona",
            "Per Chi",
            "Farmaco",
            "Dosaggio",
            "Orari",
            "Scorte Rimanenti",
            "Stato Scorta",
        )

        self.tree = ttk.Treeview(
            table_frame, columns=self.columns, show="headings", selectmode="browse"
        )

        # Nascondiamo la colonna ID tecnica
        self.tree.heading("ID", text="")
        self.tree.column("ID", width=0, stretch=False)

        self.tree.heading("Seleziona", text="[ ]")
        self.tree.heading("Per Chi", text="Per Chi")
        self.tree.heading("Farmaco", text="Nome Farmaco")
        self.tree.heading("Dosaggio", text="Dosaggio")
        self.tree.heading("Orari", text="Orari Assunzione")
        self.tree.heading("Scorte Rimanenti", text="Pillole Rim.")
        self.tree.heading("Stato Scorta", text="Stato Scorta")

        self.tree.column("Seleziona", width=60, anchor="center")
        self.tree.column("Per Chi", width=110, anchor="center")
        self.tree.column("Farmaco", width=200, anchor="w")
        self.tree.column("Dosaggio", width=110, anchor="center")
        self.tree.column("Orari", width=150, anchor="center")
        self.tree.column("Scorte Rimanenti", width=110, anchor="center")
        self.tree.column("Stato Scorta", width=160, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configurazione colori riga in base allo stato scorta
        self.tree.tag_configure("normale", background="#FFFFFF")
        self.tree.tag_configure(
            "in_esaurimento", background="#FADBD8"
        )  # Rosa/Rosso chiaro di avviso

        # Caricamento dei dati dal DB
        self.carica_dati()

        # Eventi click
        self.tree.bind("<Button-1>", self.on_table_click)
        self.tree.bind("<Double-1>", lambda e: self.apri_popup_modifica())

        # --- BARRA DEI PULSANTI IN BASSO ---
        btn_frame = tk.Frame(self.window, bg="#2C3E50")
        btn_frame.pack(fill="x", padx=20, pady=15)

        largh_btn = 15

        btn_nuovo = tk.Button(
            btn_frame,
            text="➕ Aggiungi",
            bg="#27AE60",
            fg="white",
            font=("Arial", 10, "bold"),
            width=largh_btn,
            command=self.apri_popup_nuovo,
        )
        btn_nuovo.pack(side="left", expand=True, padx=4)

        btn_modifica = tk.Button(
            btn_frame,
            text="✏️ Modifica",
            bg="#2980B9",
            fg="white",
            font=("Arial", 10, "bold"),
            width=largh_btn,
            command=self.apri_popup_modifica,
        )
        btn_modifica.pack(side="left", expand=True, padx=4)

        btn_scala = tk.Button(
            btn_frame,
            text="💊 Prendi 1 Dosa",
            bg="#8E44AD",
            fg="white",
            font=("Arial", 10, "bold"),
            width=largh_btn,
            command=self.scala_dose,
        )
        btn_scala.pack(side="left", expand=True, padx=4)

        btn_stampa = tk.Button(
            btn_frame,
            text="🖨️ Stampa",
            bg="#D35400",
            fg="white",
            font=("Arial", 10, "bold"),
            width=largh_btn,
            command=self.stampa_selezionati,
        )
        btn_stampa.pack(side="left", expand=True, padx=4)

        btn_elimina = tk.Button(
            btn_frame,
            text="🗑️ Elimina",
            bg="#C0392B",
            fg="white",
            font=("Arial", 10, "bold"),
            width=largh_btn,
            command=self.elimina_selezionato,
        )
        btn_elimina.pack(side="left", expand=True, padx=4)

        btn_chiudi = tk.Button(
            btn_frame,
            text="🚪 Chiudi",
            bg="#7F8C8D",
            fg="white",
            font=("Arial", 10, "bold"),
            width=largh_btn,
            command=self.window.destroy,
        )
        btn_chiudi.pack(side="left", expand=True, padx=4)

    def inizializza_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seleziona TEXT,
                per_chi TEXT,
                farmaco TEXT,
                dosaggio TEXT,
                orari TEXT,
                scorte INTEGER,
                soglia_avviso INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def carica_dati(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, seleziona, per_chi, farmaco, dosaggio, orari, scorte, soglia_avviso FROM medicine"
        )
        righe = cursor.fetchall()
        conn.close()

        for riga in righe:
            row_id, seleziona, per_chi, farmaco, dosaggio, orari, scorte, soglia = riga

            # Valutazione automatica dello stato scorta
            if scorte <= soglia:
                stato = "⚠️ IN ESAURIMENTO!"
                tag = "in_esaurimento"
            else:
                stato = "✅ Scorta Sufficiente"
                tag = "normale"

            valori_visualizzati = (
                row_id,
                seleziona,
                per_chi,
                farmaco,
                dosaggio,
                orari,
                f"{scorte} compresse",
                stato,
            )
            self.tree.insert("", "end", values=valori_visualizzati, tags=(tag,))

    def on_table_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#2":
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    values = list(self.tree.item(item_id, "values"))
                    row_id = values[0]
                    nuova_spunta = "[X]" if values[1] == "[ ]" else "[ ]"

                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE medicine SET seleziona = ? WHERE id = ?",
                        (nuova_spunta, row_id),
                    )
                    conn.commit()
                    conn.close()

                    self.carica_dati()

    def apri_popup_nuovo(self):
        self.apri_finestra_dettaglio("Aggiungi Nuova Terapia / Farmaco", None)

    def apri_popup_modifica(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Attenzione",
                "Seleziona una riga dalla tabella da modificare.",
                parent=self.window,
            )
            return
        values = self.tree.item(selected_item, "values")
        row_id = values[0]

        # Recupera i dati grezzi dal DB per la modifica
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, per_chi, farmaco, dosaggio, orari, scorte, soglia_avviso FROM medicine WHERE id = ?",
            (row_id,),
        )
        dati_db = cursor.fetchone()
        conn.close()

        self.apri_finestra_dettaglio("Modifica Terapia", dati_db)

    def apri_finestra_dettaglio(self, titolo, dati_esistenti):
        popup = tk.Toplevel(self.window)
        popup.title(titolo)
        popup.geometry("450x460")
        popup.configure(bg="#34495E")
        popup.grab_set()

        tk.Label(
            popup, text=titolo, font=("Arial", 14, "bold"), bg="#34495E", fg="#FFD700"
        ).pack(pady=10)

        form_frame = tk.Frame(popup, bg="#34495E")
        form_frame.pack(padx=20, pady=5, fill="both", expand=True)

        tk.Label(
            form_frame,
            text="Per Chi (Paziente / Familiare):",
            bg="#34495E",
            fg="white",
            anchor="w",
        ).pack(fill="x")
        entry_per_chi = tk.Entry(form_frame, font=("Arial", 11), width=35)
        entry_per_chi.pack(pady=(0, 8))

        tk.Label(
            form_frame, text="Nome Farmaco:", bg="#34495E", fg="white", anchor="w"
        ).pack(fill="x")
        entry_farmaco = tk.Entry(form_frame, font=("Arial", 11), width=35)
        entry_farmaco.pack(pady=(0, 8))

        tk.Label(
            form_frame,
            text="Dosaggio (es. 1 compressa / 15 gocce):",
            bg="#34495E",
            fg="white",
            anchor="w",
        ).pack(fill="x")
        entry_dosaggio = tk.Entry(form_frame, font=("Arial", 11), width=35)
        entry_dosaggio.pack(pady=(0, 8))

        tk.Label(
            form_frame,
            text="Orari di Assunzione:",
            bg="#34495E",
            fg="white",
            anchor="w",
        ).pack(fill="x")
        entry_orari = tk.Entry(form_frame, font=("Arial", 11), width=35)
        entry_orari.pack(pady=(0, 8))

        tk.Label(
            form_frame,
            text="Scorte Attuali (N° compresse / unità):",
            bg="#34495E",
            fg="white",
            anchor="w",
        ).pack(fill="x")
        entry_scorte = tk.Entry(form_frame, font=("Arial", 11), width=35)
        entry_scorte.pack(pady=(0, 8))

        tk.Label(
            form_frame,
            text="Soglia Avviso Scorta Minima:",
            bg="#34495E",
            fg="white",
            anchor="w",
        ).pack(fill="x")
        entry_soglia = tk.Entry(form_frame, font=("Arial", 11), width=35)
        entry_soglia.pack(pady=(0, 10))

        if dati_esistenti:
            # dati_esistenti è la tupla: (id, per_chi, farmaco, dosaggio, orari, scorte, soglia)
            entry_per_chi.insert(0, dati_esistenti[1])
            entry_farmaco.insert(0, dati_esistenti[2])
            entry_dosaggio.insert(0, dati_esistenti[3])
            entry_orari.insert(0, dati_esistenti[4])
            entry_scorte.insert(0, str(dati_esistenti[5]))
            entry_soglia.insert(0, str(dati_esistenti[6]))
        else:
            entry_soglia.insert(0, "5")  # Default avviso sotto le 5 unità

        def salva_dati():
            per_chi = entry_per_chi.get().strip()
            farmaco = entry_farmaco.get().strip()
            dosaggio = entry_dosaggio.get().strip()
            orari = entry_orari.get().strip()

            try:
                scorte = int(entry_scorte.get().strip())
                soglia = int(entry_soglia.get().strip())
            except ValueError:
                messagebox.showerror(
                    "Errore",
                    "I campi Scorte e Soglia devono essere numeri interi!",
                    parent=popup,
                )
                return

            if not per_chi or not farmaco:
                messagebox.showerror(
                    "Errore",
                    "I campi 'Per Chi' e 'Nome Farmaco' sono obbligatori!",
                    parent=popup,
                )
                return

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            if dati_esistenti:
                row_id = dati_esistenti[0]
                cursor.execute(
                    "UPDATE medicine SET per_chi = ?, farmaco = ?, dosaggio = ?, orari = ?, scorte = ?, soglia_avviso = ? WHERE id = ?",
                    (per_chi, farmaco, dosaggio, orari, scorte, soglia, row_id),
                )
                messagebox.showinfo(
                    "Successo", "Terapia modificata con successo!", parent=popup
                )
            else:
                cursor.execute(
                    "INSERT INTO medicine (seleziona, per_chi, farmaco, dosaggio, orari, scorte, soglia_avviso) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("[ ]", per_chi, farmaco, dosaggio, orari, scorte, soglia),
                )
                messagebox.showinfo(
                    "Successo", "Nuova terapia aggiunta con successo!", parent=popup
                )

            conn.commit()
            conn.close()
            self.carica_dati()
            popup.destroy()

        btn_salva = tk.Button(
            popup,
            text="💾 Salva Dati",
            bg="#27AE60",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            command=salva_dati,
        )
        btn_salva.pack(pady=10)

    def scala_dose(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Attenzione",
                "Seleziona un farmaco dalla tabella per scalare una dose.",
                parent=self.window,
            )
            return

        values = self.tree.item(selected_item, "values")
        row_id = values[0]
        farmaco_nome = values[3]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT scorte FROM medicine WHERE id = ?", (row_id,))
        res = cursor.fetchone()

        if res and res[0] > 0:
            nuove_scorte = res[0] - 1
            cursor.execute(
                "UPDATE medicine SET scorte = ? WHERE id = ?", (nuove_scorte, row_id)
            )
            conn.commit()
            conn.close()

            self.carica_dati()
            messagebox.showinfo(
                "Aggiornato",
                f"Dose assunta per '{farmaco_nome}'. Scorte rimanenti: {nuove_scorte}",
                parent=self.window,
            )
        else:
            conn.close()
            messagebox.showwarning(
                "Attenzione",
                f"Le scorte per '{farmaco_nome}' sono già a zero!",
                parent=self.window,
            )

    def stampa_selezionati(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT per_chi, farmaco, dosaggio, orari, scorte FROM medicine WHERE seleziona = '[X]'"
        )
        selezionati = cursor.fetchall()
        conn.close()

        if not selezionati:
            messagebox.showwarning(
                "Nessuna selezione",
                "Metti la spunta [X] su almeno una riga da stampare.",
                parent=self.window,
            )
            return

        testo_stampa = "=== REPORT MEDICINE E TERAPIE SELEZIONATE (SPsoft) ===\n\n"
        for row in selezionati:
            testo_stampa += f"• Paziente: {row[0]} | Farmaco: {row[1]} | Dosaggio: {row[2]} | Orari: {row[3]} | Rimasti: {row[4]} pz\n"

        messagebox.showinfo("Stampa / Esportazione", testo_stampa, parent=self.window)

    def elimina_selezionato(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Attenzione", "Seleziona una riga da eliminare.", parent=self.window
            )
            return

        values = self.tree.item(selected_item, "values")
        row_id = values[0]

        if messagebox.askyesno(
            "Conferma", "Vuoi davvero eliminare questa terapia?", parent=self.window
        ):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medicine WHERE id = ?", (row_id,))
            conn.commit()
            conn.close()

            self.carica_dati()
            messagebox.showinfo(
                "Eliminato", "Elemento rimosso con successo.", parent=self.window
            )
