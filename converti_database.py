import argparse
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def converti(database: Path, destinazione: Path) -> int:
    if not database.is_file():
        raise FileNotFoundError(f"Database non trovato: {database}")

    with closing(sqlite3.connect(database)) as conn:
        conn.row_factory = sqlite3.Row
        colonne = {
            row["name"] for row in conn.execute("PRAGMA table_info(medicine)")
        }
        richieste = {
            "id",
            "seleziona",
            "per_chi",
            "farmaco",
            "dosaggio",
            "orari",
            "scorte",
            "soglia_avviso",
        }
        if not richieste.issubset(colonne):
            raise ValueError("Il database non contiene la tabella medicine attesa.")
        righe = conn.execute(
            """
            SELECT id, seleziona, per_chi, farmaco, dosaggio, orari,
                   scorte, soglia_avviso
            FROM medicine
            ORDER BY id
            """
        ).fetchall()

    elementi = [
        {
            "id": str(riga["id"]),
            "person": riga["per_chi"] or "",
            "name": riga["farmaco"] or "",
            "dose": riga["dosaggio"] or "",
            "schedule": riga["orari"] or "",
            "quantity": int(riga["scorte"] or 0),
            "threshold": int(riga["soglia_avviso"] or 0),
            "selected": riga["seleziona"] == "[X]",
        }
        for riga in righe
    ]
    backup = {
        "schemaVersion": 1,
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "items": elementi,
    }
    destinazione.write_text(
        json.dumps(backup, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return len(elementi)


def main() -> None:
    cartella = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Esporta il database SQLite di Gestione Medicine in JSON."
    )
    parser.add_argument(
        "database",
        nargs="?",
        type=Path,
        default=cartella / "non_dimentico.db",
        help="percorso del database SQLite (predefinito: non_dimentico.db)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=cartella / "backup-medicine.json",
        help="file JSON da creare",
    )
    args = parser.parse_args()
    count = converti(args.database, args.output)
    print(f"Esportati {count} farmaci in: {args.output}")


if __name__ == "__main__":
    main()
