# Draft: privacy section for the apps

Target: the privacy part of https://fretboard.schoensgibl.com/impressum/ (template and view of the
Impressum page). **Not published.** Publishing is a task for a session on almalinux9 (content change
plus deploy), see the brief at the end. The text must be reviewed by the owner before it goes live;
it is not legal advice.

## English

### Guitar Positions apps (Android, later iOS)

The Guitar Positions apps for Android and iOS do not collect, store or transmit personal data.

- **No account, no sign-in.**
- **No analytics, no advertising, no tracking, no crash reporting.** The apps contain no third-party
  SDKs for these purposes.
- **No network requests.** The apps run completely offline; the Android app does not even request the
  internet permission. All music data is inside the app.
- **Data on your device only.** Songs, favourites and settings (tuning, theme, tempo) are stored in
  the app's local storage on your device. They are not sent anywhere. Uninstalling the app deletes them.
- **Sharing and PDF export happen only when you ask for them.** When you share a link or a PDF, the
  content goes to the app you choose in the system share sheet. A shared link points to
  fretboard.schoensgibl.com; opening that link in a browser is subject to this website's privacy section.
- **Links to this website** (About, Imprint and Privacy, the privacy policy) open in your browser, not
  inside the app. Then the website's privacy section applies.
- **Purchase:** the app is sold through Google Play (and later the App Store). Payment and purchase
  records are handled by Google or Apple under their own policies; the developer receives no personal
  data about buyers beyond what the store reports in aggregate.

Contact: see the Imprint above.

## Deutsch

### Guitar-Positions-Apps (Android, später iOS)

Die Guitar-Positions-Apps für Android und iOS erheben, speichern und übertragen keine personenbezogenen Daten.

- **Kein Konto, keine Anmeldung.**
- **Keine Analyse, keine Werbung, kein Tracking, keine Absturzberichte.** Die Apps enthalten dafür keine SDKs von Dritten.
- **Keine Netzwerkanfragen.** Die Apps laufen vollständig offline; die Android-App fordert nicht einmal die Internetberechtigung an. Alle Musikdaten sind in der App enthalten.
- **Daten nur auf deinem Gerät.** Songs, Favoriten und Einstellungen (Stimmung, Design, Tempo) liegen im lokalen Speicher der App auf deinem Gerät und werden nirgendwohin gesendet. Beim Deinstallieren der App werden sie gelöscht.
- **Teilen und PDF-Export nur auf deinen Wunsch.** Beim Teilen eines Links oder PDFs geht der Inhalt an die App, die du im Teilen-Fenster des Systems wählst. Ein geteilter Link zeigt auf fretboard.schoensgibl.com; für das Öffnen im Browser gilt der Datenschutzteil dieser Website.
- **Links zu dieser Website** (Über, Impressum und Datenschutz, Datenschutzerklärung) öffnen im Browser, nicht in der App. Dann gilt der Datenschutzteil der Website.
- **Kauf:** Die App wird über Google Play (später den App Store) verkauft. Zahlung und Kaufdaten verarbeiten Google bzw. Apple nach ihren eigenen Bestimmungen; der Entwickler erhält keine personenbezogenen Daten der Käufer, nur zusammengefasste Berichte des Stores.

Kontakt: siehe Impressum oben.

## Brief for the almalinux9 session (not sent)

> Assignment: in the fretboard project (path under /home/jarvis, ask the owner which checkout is live),
> add the approved privacy text from `docs/store/privacy-apps.md` to the privacy section of the
> Impressum template, keep the page's language handling, run the site's tests, deploy, and check
> https://fretboard.schoensgibl.com/impressum/ afterwards. Authorized: that content change and the
> deploy. Not authorized: anything else. No personal data is involved. Report the commit and the check.
