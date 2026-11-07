# KI-Protokolle (Claude Code)

Alle Claude-Code-Sitzungen zum Maturaprojekt, die auf dem PC von Projektmitglied 1 liefen. Persönliche Daten (Namen, E-Mail, Benutzername, Schule) sind durch Platzhalter wie [Name] ersetzt. Dient als **digitaler Anhang zum KI-Nachweis** im Logbuch (Anhang K1 ff.) und als Archiv. Die Sitzungen des anderen Projektmitglieds (10/09–12/09, K12) fehlen noch.

| Datum | Thema | Modell | Prompts | Datei |
|---|---|---|---|---|
| 2026-08-12 – 2026-08-19 | Tagebuch/Logbuch einrichten, Zeitplan, Bilder-Ablage | claude-opus-5 | 12 | [2026-08-12_06351956.md](2026-08-12_06351956.md) |
| 2026-09-09 | Gesamtschaltplan Rev. 2 | claude-opus-5 | 8 | [2026-09-09_1fea6b0a.md](2026-09-09_1fea6b0a.md) |
| 2026-09-09 | Mixer-Debugging in Falstad | claude-opus-5 | 2 | [2026-09-09_dde0fce2.md](2026-09-09_dde0fce2.md) |
| 2026-09-11 | GitHub-Projekt einrichten | claude-opus-5 | 2 | [2026-09-11_c1dcfd51.md](2026-09-11_c1dcfd51.md) |
| 2026-10-21 | Schul-Unterlagen, Standortbestimmung, KI-Deklaration | claude-opus-5-5 | 8 | [2026-10-21_9a1cd49d.md](2026-10-21_9a1cd49d.md) |
| 2026-10-21 | Abzweigung: Eingrenzung schriftlicher Kommentar | claude-opus-5-5 | 5 | [2026-10-21_f8199d6a.md](2026-10-21_f8199d6a.md) |
| 2026-10-28 – 2026-11-04 | Logbuch nachtragen und umstrukturieren, Protokoll-Export | claude-opus-5-5 | 5 | [2026-10-28_b0e88781.md](2026-10-28_b0e88781.md) |
| 2026-10-28 – 2026-11-04 | Schriftlicher Kommentar Review | claude-opus-5-5 | 2 | [2026-10-28_cbc54aa2.md](2026-10-28_cbc54aa2.md) |

## Inhalt

- `*.md` – lesbare Fassung: eigene Prompts und Antworten im Wortlaut, Werkzeugaufrufe als Kurzzeile.
- Die vollständigen Originalprotokolle (JSONL, inkl. Werkzeug-Ausgaben) liegen **nicht** im öffentlichen Repo, weil sie persönliche Daten enthalten. Projektmitglied 1 hat sie privat als ZIP.
- `memory/` – Claudes Projektnotizen (Gedächtnis), die in jeder Sitzung geladen wurden.

## Auf einem neuen Gerät weiterarbeiten

Damit Claude Code die alten Sitzungen fortsetzen kann (`claude --resume`) und das Gedächtnis wieder hat:

1. Repo klonen.
2. Den Inhalt des privaten ZIP (die `.jsonl`-Dateien und Ordner) nach `~/.claude/projects/<Ordnername>/` kopieren (das ZIP enthält auch `memory/`). `<Ordnername>` ist der Projektpfad, bei dem `:`, `\` und `/` durch `-` ersetzt sind (z. B. `C--Users-name-MaturaProjekt`). Am einfachsten: einmal Claude Code im Projektordner starten, dann ist der Ordner angelegt.
3. Pfade in alten Sitzungen zeigen noch auf den alten PC – für Nachschlagen reicht das, Dateien liegen im Repo.

Stand des Exports: 04/11/26.
