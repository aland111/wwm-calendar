# Wer wird Millionär? als Kalenderabo

Dieses Projekt veröffentlicht die kommenden **RTL-Ausstrahlungen** von „Wer wird Millionär?“ als abonnierbaren iCalendar-Feed. Es übernimmt die tatsächlich gelisteten Sendetage und Uhrzeiten, einschließlich Sonderausgaben außerhalb des regulären Montags. Mehrere Episoden innerhalb eines durchgehenden Sendeplatzes werden zu einem Termin zusammengefasst.

## Lokal erzeugen

Python 3.11 oder neuer:

```sh
python -m venv .venv
python -m pip install -r requirements.txt
python wwm_calendar.py
```

Die Datei liegt danach unter `site/wwm.ics`. Ein **Dateiimport aktualisiert sich nicht automatisch**. Für laufende Aktualisierungen muss die Datei unter einer dauerhaft erreichbaren HTTPS-Adresse veröffentlicht und als Kalender abonniert werden.

## Automatisch mit GitHub Pages veröffentlichen

1. Die Dateien in diesem Repository auf den Standardbranch `main` übertragen.
2. In **Settings → Pages → Build and deployment** die Quelle **GitHub Actions** wählen.
3. Unter **Actions → Publish WWM calendar** den Workflow einmal manuell starten. Danach aktualisiert er den Feed alle sechs Stunden.
4. Die Abo-URL lautet `https://aland111.github.io/wwm-calendar/wwm.ics`.

### Google Kalender

Am Computer `calendar.google.com` öffnen → **Weitere Kalender → + → Per URL** → Abo-URL einfügen. Den Kalender in Google **nicht als Datei importieren**.

### Apple Kalender / iCloud

Auf dem iPhone in **Kalender → Kalender → Hinzufügen → Kalenderabonnement hinzufügen** dieselbe URL einfügen und als Account **iCloud** wählen. So ist das Abo von deinem getrennten Google-Kalender unabhängig.

## Daten und Grenzen

Quelle ist die [RTL-Sendeterminübersicht von fernsehserien.de](https://www.fernsehserien.de/wer-wird-millionaer/sendetermine/rtl). Sie enthält nur bereits veröffentlichte Termine; weitere Ausgaben erscheinen im Feed, sobald die Quelle sie listet. Der Workflow schlägt fehl, wenn die erwartete Seitenstruktur nicht mehr vorhanden ist, damit eine bestehende Veröffentlichung nicht durch einen leeren Feed ersetzt wird. Google und Apple bestimmen selbst, wann sie Abo-Änderungen abrufen; eine sofortige Anzeige ist nicht garantiert.
