---
name: matura-diary-workflow
description: "This session/project exists to keep a German-language project diary for the user's Matura project, one Markdown file per day."
metadata: 
  node_type: memory
  type: project
  originSessionId: 06351956-4a56-4b25-9bc4-52c81aceafa9
  modified: 2026-10-28T15:00:29.461Z
---

Ab 2026-08-12: Der Nutzer (und Projektpartner) schicken Nachrichten, Notizen und
Dateien darüber, was am jeweiligen Tag am Maturaprojekt gearbeitet wurde. Ich
analysiere das und schreibe daraus einen Tagebucheintrag.

- Sprache der Einträge: **Deutsch**.
- **Ab 19.08.2026: Das laufende Logbuch wird direkt in
  `Unsere-Materialien/Logbuch/Logbuch neu.docx` weitergeführt** (Word-Tabelle, TT/MM/JJ).
  **Seit 28.10.2026 sechs Spalten:** Datum | Dauer / Wer | Arbeitsschritte | Ergebnisse |
  Reflexionen | KI-Nutzung, Querformat, Seitenzahlen, danach Anhang «KI-Nachweis» mit
  Prompts im Wortlaut (K1…K21). Neue KI-Nutzung → nächste K-Nummer (Tool+Version, Datum,
  Prompt wörtlich, eingefügte Dateien/fremde Texte als «[eingefügt: …]», Namen als [Name],
  Art der Übernahme). Reflexionen schreiben die Nutzer selbst; ich setze nur gelb
  markierte Leitfragen (gelb = von ihnen zu ergänzen).
  **Stil (Nutzerwunsch 28/10/26):** Logbuch knapp halten — *was* erreicht/verstanden
  wurde, keine Erklärungen (die gehören in den schriftlichen Kommentar) und keine
  Hilfsmittel/Wege (z. B. Skripte), nur das Ergebnis. Meine Rolle im Logbuch:
  «Organisator» (lege ihre Dateien, Quellen, Bilder ab, gebe Auskunft zum Projektstand,
  führe das Logbuch teilweise mit).
  Neue Arbeitstage kommen als neue Tabellenzeile dorthin, nicht mehr als eigene Tagesdatei.
  Bearbeitung: docx entpacken, `word/document.xml` ändern, neu zippen (siehe docx-Skill).
  Achtung: pandoc, zip, LibreOffice und pdftoppm fehlen auf diesem Rechner —
  Text mit Python/zipfile+ElementTree extrahieren, validate.py braucht `PYTHONIOENCODING=utf-8`.
- Alte Ablage (weiterhin als Detailnotizen): `diary/JJJJ-MM-TT.md` im Projektordner `C:\Users\<user>\Downloads\MaturaProjekt`,
  Vorlage in `diary/_vorlage.md`, Index in `diary/README.md` (dort pro Eintrag eine Zeile ergänzen).
- Das Projekt läuft schon seit ~einem halben Jahr; nach den Sommerferien wird die
  Dokumentation nachgeholt/fortgeführt. Frühere Tage können nachträglich eingetragen werden.
- **Datumsregel:** Wenn der Nutzer kein Datum angibt, gilt der Tag, an dem er schreibt.
  Nicht nachfragen.
- Quellen (Videos, Datenblätter, Artikel) kommen zusätzlich in `quellen/lernmaterial.md`
  — das wird später das Quellenverzeichnis der schriftlichen Arbeit.

**Why:** Das Tagebuch ist Teil der Maturaprojekt-Dokumentation und muss lückenlos sein.
**How to apply:** Bei jeder Nachricht über getane Arbeit prüfen, welches Datum gemeint ist,
den passenden Tageseintrag anlegen oder ergänzen, und den Index aktualisieren.
Bei fehlenden Angaben (Dauer, Beteiligte) nachfragen statt erfinden.
