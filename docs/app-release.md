# Guitar Positions (Fretboard Position Finder) als App in Google Play und im App Store

Stand: 2026-10-22. **Anleitung für den Eigentümer, nur Vorbereitung.** Noch nichts gebaut, kein Konto angelegt, keine App-Kennung belegt, nichts hochgeladen.

Grundlagen auf dem Zweig `claude/festive-payne-53db8c` (noch **nicht** in `master`): `apps/README.md` (Capacitor-Hüllen, Bundle, Icons, Builds) und `docs/STUDIO_REDESIGN.md` Abschnitt 7 (Plan für die nativen Apps, Stand 2026-10-18). Dieses Dokument ergänzt beides um die Store-Schritte.

**Keine Rechtsberatung.** Store-Regeln stehen unten mit Quelle und Lesedatum (Abschnitt 11). Was daraus rechtlich folgt, ist nicht geprüft.

## 0. Kurzfassung

| Frage | Empfehlung |
|---|---|
| Weg | **Capacitor 8** (auf dem Zweig schon angelegt: `apps/ios`, `apps/android`). Studio-Code und Musikkatalog werden in die App gepackt, die App läuft **ohne Server** und ohne Netzanfragen. |
| Konten | Die vorhandenen Konten des Eigentümers: Google Play „Schoensgibl.com“ (privat, verifiziert), Apple-Einzelmitgliedschaft (Aktivierung ausstehend). Keine neuen Konten. |
| App-Kennung | Vorschlag `com.schoensgibl.guitarpositions` (steht schon im Zweig). Unumkehrbar ab dem ersten Upload, Entscheidung des Eigentümers (Abschnitt 3). |
| Name im Store | „Guitar Positions“ (Vorschlag; Untertitel z. B. „Scales, chords, arpeggios“) |
| Daten | Keine Konten, keine Analyse, keine Werbung, CSP erlaubt nur das Bundle: Ziel „Keine Daten erhoben“ |
| Spenden | im App-Bundle schon entfernt (`build_app_bundle.py`), so lassen |
| Testphase | Play: interner Test → geschlossener Test mit mind. 12 Personen über 14 Tage → Produktion. Apple: TestFlight → App-Prüfung |
| Mac | über „iPhone- und iPad-Apps auf Mac mit Apple-Chip“ aus dem iOS-Build, kein eigener Mac-Build für den Store |
| Kosten | keine zusätzlichen Gebühren (Konten bestehen schon) |

## 1. Warum Capacitor (und nicht TWA, Flutter oder nativ)

Bestand:

- Django-Webanwendung (`fretboard/`, `positionfinder/`, `api/`), PostgreSQL; neue Oberfläche „Studio“ in reinem JavaScript (`static/studio/`, `templates/studio/index.html`) mit getesteter Musiktheorie (`theory.test.mjs`), PWA mit Service Worker (`templates/studio/sw.js`) und Manifest.
- Songs und Übungen werden nur im Browser gespeichert, kein Konto (README).
- Native Hüllen auf dem Zweig: Capacitor 8.5.3, iOS 15+ (iPhone und iPad, Swift Package Manager), Android minSdk 24, target/compile SDK 36, Mac Catalyst nur lokal. `scripts/build_app_bundle.py` erzeugt `www/` mit eingebettetem Katalog (nur Musikformeln), ohne Spendenlink, Service Worker, PWA-Manifest und SEO-Tags, mit einer Content-Security-Policy, die nur das Bundle erlaubt. Impressum und Datenschutz öffnen im System-Browser.
- Lizenz: README sagt **MIT**, im Repo liegt aber **keine `LICENSE`-Datei** (Abschnitt 10).

| Weg | Passt? | Begründung |
|---|---|---|
| **Capacitor** | **ja, empfohlen** | schon eingerichtet, gleicher Studio-Code wie die Webseite, offline, eine Person kann es warten |
| Trusted Web Activity (TWA) | nur Android | lädt die Webseite live, braucht Netz; kein iOS-Gegenstück; die PWA deckt diesen Fall schon ab |
| Flutter mit WebView | nein | zweiter Werkzeugstapel, gleicher Inhalt |
| Nativ (Swift/Kotlin) | nein | Fingersatz- und Theorie-Logik müsste doppelt portiert werden (Plan 7.1) |

Apple-Richtlinie 4.2 verlangt mehr als eine „verpackte Webseite“ (11.1). Der Plan (7.4) sieht dafür vor: Offline-Bundle, Haptik beim Tippen aufs Griffbrett, natives Teilen, Statusleiste/Safe Area, iPad-Split-View und Tastaturkürzel, dazu App-eigene Funktionen (Favoriten, Übungsmodus). Heute hat die App nur die Grundplugins (`core`, `ios`, `android`); **die 4.2-Punkte sind noch offen** und das größte Prüfrisiko.

## 2. Technische Arbeiten vor dem ersten Store-Build (eigene Aufträge)

Aus `apps/README.md` („Not done yet“) und eigenen Befunden, Stand 2026-10-22, nicht auf Geräten geprüft:

1. **Zweig zusammenführen:** `claude/festive-payne-53db8c` nach `master` (oder Release-Zweig festlegen). Die README sagt: Apps immer zusammen mit der Webversion neu bauen.
2. **4.2-Funktionen:** `@capacitor/haptics`, `@capacitor/share`, `@capacitor/status-bar`; App-eigener Mehrwert (Favoriten, Übungsmodus) vor der ersten Einreichung (Plan 7.4, 7.6).
3. **iOS-Audio:** Der Stummschalter kann Web Audio stummschalten; `navigator.audioSession.type = 'playback'` oder ein kleines Plugin mit `AVAudioSession` `.playback` am Gerät prüfen (Plan 7.6).
4. **Versionen:** `MARKETING_VERSION`/`versionName` sind `1.0`, `versionCode 1` fest. Eine Quelle (`settings.VERSION`), Build-Nummer wächst mit jedem Upload (Plan 7.8).
5. **Release-Signatur Android:** `build.gradle` hat noch keine Release-Signatur; aus `key.properties` außerhalb des Repos lesen (Abschnitt 7). `apps/android/.gitignore` hat `*.jks`/`*.keystore` nur auskommentiert: aktivieren und `key.properties` ergänzen.
6. **Exportkontrolle iOS:** `ITSAppUsesNonExemptEncryption` fehlt in `Info.plist`. Die App verschlüsselt nichts und macht keine Netzanfragen; nach Apples Tabelle wäre `false` passend (Einordnung ohne rechtliche Bewertung).
7. **Privacy Manifest:** prüfen, ob ein `PrivacyInfo.xcprivacy` für das App-Target nötig ist; der erste Upload zeigt Beanstandungen.
8. **Katalog:** vor dem Store-Build mit `--from-db` oder `--catalog` aus dem Produktionsstand bauen, wenn die Fixture älter ist (README).
9. **Geräteprüfung:** Impressum/Datenschutz öffnen im System-Browser, Safe Areas auf iPhone mit Notch und Android 15+ (Edge-to-Edge).
10. **Lizenz der gebündelten Schrift** prüfen (das Bundle kopiert die Schrift aus `studio.css`) und im App-Info-Fenster Lizenzen nennen.

## 3. App-Kennung (unumkehrbar)

Die Kennung (iOS Bundle-ID, Android `applicationId`) ist ab dem ersten Upload belegt und nicht mehr änderbar.

| Option | Bemerkung |
|---|---|
| **`com.schoensgibl.guitarpositions`** (Vorschlag) | steht in `apps/capacitor.config.json`, Xcode- und Android-Projekt; passt zur Domain `schoensgibl.com` und zum App-Namen |
| `com.schoensgibl.fretboard` | passt zum Repo- und Domainnamen `fretboard.schoensgibl.com`, Projekte müssten angepasst werden |

Für lokale Tests mit einem kostenlosen Personal Team **nicht** die echte Kennung registrieren, sondern z. B. `com.schoensgibl.guitarpositions.dev` (README: sonst ist die ID später womöglich blockiert). **Entscheidung des Eigentümers** (auch der Name: „Guitar Positions“ oder „Fretboard Position Finder“).

## 4. Store-Einträge und Assets

| | Google Play | App Store |
|---|---|---|
| Name | bis 30 Zeichen | 2 bis 30 Zeichen, Untertitel bis 30 |
| Texte | Kurzbeschreibung bis 80, Beschreibung bis 4000 Zeichen | Beschreibung bis 4000 (nur Text), Werbetext bis 170, Schlüsselwörter bis 100 Byte |
| Icon | 512 × 512 PNG (32 Bit, mit Alpha), höchstens 1 MB; Vorlage `static/studio/icons/app-icon-1024.png` | 1024 × 1024 im App-Paket (`npm run icons`) |
| Grafik | Feature Graphic 1024 × 500 (ohne Alpha) | – |
| Screenshots | mind. 2, bis 8 je Gerätetyp; Tablets mind. 4; für Empfehlungen mind. 4 mit mind. 1080 × 1920 | 1 bis 10 je Größe; iPhone mit Dynamic Island (z. B. 1206 × 2622) und iPad 13 Zoll (z. B. 2064 × 2752) Pflicht; ohne Alpha |
| URLs | Datenschutzerklärung (Pflicht), Website, Kontakt-E-Mail | Datenschutz-URL (Pflicht), Support-URL (Pflicht, mit Kontaktdaten) |
| Einstufung | IARC-Fragebogen; erwartet „Jedes Alter“ | Altersfreigabe-Fragebogen; erwartet niedrigste Stufe (keine Nutzerinhalte, kein Webzugang in der App) |
| Kategorie | Musik und Audio oder Bildung | Musik, Nebenkategorie Bildung |

Vorlagen für Screenshots: `docs/screenshots/` (Skalen, Akkorde, V-System, Chord Namer, Songs), am Gerät bzw. Simulator neu aufnehmen. Store-Texte Englisch (App-Sprache), optional Deutsch (**Entscheidung**). Ablage: `docs/store/` (keine Geheimnisse, keine Personendaten).

## 5. Datenschutz

**Datenschutzerklärung:** Pflicht in beiden Stores, auch ohne Datenerhebung; Apple verlangt zusätzlich einen Link in der App (5.1.1(i)). Die Seite `https://fretboard.schoensgibl.com/impressum/` enthält schon einen Datenschutzteil; laut Plan 7.7 muss er **auch die Apps beschreiben**: keine Konten, keine Analyse, keine Werbung, keine Netzanfragen aus der App, Songs und Einstellungen nur auf dem Gerät, geteilte Links und PDFs entstehen nur auf Wunsch der Person. Diese URL in beiden Stores und im Einstellungsfenster der App angeben.

**Apple App Privacy:** „Data Not Collected“ (nur auf dem Gerät verarbeitete Daten gelten nicht als erhoben).

**Google Datensicherheit:** Pflicht außerhalb des internen Tests: „Keine Daten erhoben, keine weitergegeben“, Fragen zur Datenlöschung beantworten.

**Falls später** ein Online-Abgleich des Katalogs mit `/api/catalog/` kommt (Plan 7.5, optional): Anfragen tragen keine Kennungen, aber die IP landet im Server-Log. Dann Angaben neu prüfen.

**Kontolöschung:** entfällt, keine Konten.

**EU-Händlerstatus (DSA):** Apple verlangt pro Konto eine Erklärung „Händler“/„kein Händler“; Händler zeigen Adresse (oder Postfach), Telefon, E-Mail öffentlich. Hobby-Apps ohne Absicht zur Vermarktung sind laut Apple „vielleicht“ keine Händler. Die Erklärung gilt für das ganze Konto (auch SPÖ Connect und LibreMetronome). Google-Seite dazu nicht gefunden **[offen]**. **Entscheidung des Eigentümers.**

## 6. Spenden und Zahlungen

Die Webseite hat einen Stripe-Spendenlink (`STRIPE_DONATE_URL`); das App-Bundle lässt ihn schon weg. So lassen: Apple erlaubt Trinkgeld an Entwickler nur per In-App-Kauf und außerhalb des US-Stores keine Links zu anderen Zahlungswegen (3.1.1, 3.1.1(a)); Google verbietet Links zu anderen Zahlungswegen außer für steuerbefreite Spenden und in Sonderprogrammen (Payments-Richtlinie). Ein späteres Trinkgeld per In-App-Kauf/Play Billing wäre ein eigener Auftrag (Steuer, Auszahlung, Händlerstatus).

## 7. Signatur (alles außerhalb des Repos)

Vorschlag Ablageort: `~/guitarpositions-release/` (`chmod 700`, nicht in iCloud/Dropbox, Backup verschlüsselt), Kennwörter zusätzlich im Passwortmanager.

**Android**
- Play App Signing (Standard): Google verwahrt den App-Signaturschlüssel, der Eigentümer nur den **Upload-Schlüssel**; zurücksetzbar in der Play Console.
- Eigener Upload-Schlüssel für diese App (einmalig, Eigentümer):
  ```bash
  keytool -genkeypair -v -keystore ~/guitarpositions-release/upload.jks -alias upload -keyalg RSA -keysize 4096 -validity 10000
  ```
- `key.properties` mit absolutem `storeFile`-Pfad dort ablegen; Build liest sie über einen Pfad aus einer Umgebungsvariablen.
- Nur **AAB** für Play: `cd apps/android && ./gradlew bundleRelease`.

**iOS**
- Automatische Signatur in Xcode mit dem Team der Einzelmitgliedschaft; nichts davon ins Repo (keine Team-ID, Profile, Geräte-IDs).
- Archiv in Xcode, Upload über Organizer oder Transporter.

Der Plan (7.8) sieht später GitHub Actions mit fastlane vor, Schlüssel nur als Actions-Secrets. Erst nach ausdrücklicher Entscheidung des Eigentümers, nicht für den ersten Release nötig.

## 8. Testphase und Veröffentlichung

### Google Play

1. Play Console (Konto „Schoensgibl.com“): App anlegen (Name, Standardsprache, App, kostenlos). **Ab dem ersten Upload ist die Kennung belegt.**
2. **Interner Test:** E-Mail-Liste (bis 100), AAB hochladen, veröffentlichen, Teilnahme-Link verschicken. Keine Standardprüfung, Datensicherheitsformular nicht nötig. Vorläufig zeigt Play einen Namen wie „com.schoensgibl.guitarpositions (unreviewed)“ (bei SPÖ Connect so beobachtet).
3. **Geschlossener Test (Pflicht für private Konten nach 2023-11-13):** mind. **12 Testpersonen, 14 Tage ununterbrochen** eingetragen; Austritt und Wiedereintritt startet neu. Vorher Store-Eintrag, Datensicherheit, Altersfreigabe, Datenschutz-URL fertig. Der interne Test zählt nicht. Ob die Pflicht je App gilt, sagt die Hilfeseite nicht ausdrücklich; vorsichtshalber je App einplanen. Tipp: gemeinsame Testgruppe (Google Group) mit LibreMetronome, beide Tests parallel.
4. **Zugriff auf Produktion beantragen** (Dashboard, drei Abschnitte), Prüfung meist bis 7 Tage.
5. Produktions-Release.

Den AAB lädt der Eigentümer selbst hoch (Claude in Chrome lädt nur bis 10 MB).

### Apple

1. Mitgliedschaft aktiv (ausstehend).
2. App Store Connect: neue App, iOS, Bundle-ID, Name, SKU. **Ab hier ist die Bundle-ID belegt.**
3. Build hochladen, Exportkontrolle beantworten.
4. **TestFlight intern** (Team-Nutzer, bis 100, ohne Prüfung), dann **extern** (bis 10 000 per E-Mail oder Link, erster Build mit Beta-App-Prüfung). Builds laufen 90 Tage.
5. Store-Eintrag, App Privacy, Altersfreigabe, Preis (kostenlos), Länder, DSA-Status; zur **App-Prüfung** einreichen, „manuell veröffentlichen“.
6. Mac: „iPhone- und iPad-Apps auf Mac mit Apple-Chip“ aktiv lassen (Plan 7.2, „Designed for iPad“); vorher in Xcode auf „My Mac (Designed for iPad)“ testen.

## 9. Kosten

| Posten | Betrag | Bemerkung |
|---|---|---|
| Apple Developer Program | 99 USD pro Jahr (Landeswährung) | schon für SPÖ Connect bezahlt, gilt für alle Apps; Ablauf = Apps verschwinden aus dem Store |
| Google Play Konto | 25 USD einmalig | schon bezahlt |
| Store-Provision | 0 | kostenlos, keine Käufe |
| Werkzeuge | vorhanden | Xcode 26.6, Android Studio, Emulator (Stand 2026-10-18) |

Apple zeigt bei Einzelmitgliedschaften den **bürgerlichen Namen** als Anbieter, Google den Kontonamen „Schoensgibl.com“.

## 10. Offene Entscheidungen des Eigentümers

1. **App-Kennung** (Abschnitt 3) und **Name** („Guitar Positions“ oder „Fretboard Position Finder“).
2. **Zweig `claude/festive-payne-53db8c`** nach `master` zusammenführen und als Release-Grundlage festlegen.
3. **Umfang der ersten Store-Version:** welche 4.2-Funktionen (Haptik, Teilen, Favoriten, Übungsmodus) vor der Einreichung fertig sein müssen.
4. **Lizenz:** `LICENSE`-Datei (MIT laut README) ergänzen; Git-Verlauf zeigt einen kleinen Fremdbeitrag (1 Commit), unter MIT unproblematisch, aber Lizenzdatei fehlt.
5. **Online-Katalogabgleich** ja/nein (Datenschutzangaben, Abschnitt 5).
6. **DSA-Händlerstatus** des Apple- und Play-Kontos (gilt für alle Apps); bei Zweifel Beratung.
7. **Testpersonen** für den geschlossenen Play-Test (mind. 12, 14 Tage) und TestFlight; gemeinsame Gruppe mit LibreMetronome?
8. **Store-Sprachen** und **Länder**.
9. **Mac:** nur „Designed for iPad“ (Vorschlag) oder später Catalyst/Tauri.
10. **CI mit fastlane** (Plan 7.8) jetzt oder später.

## 11. Store-Regeln (Quellen)

Gelesen am **2026-10-22**, außer wo „2026-10-21“ (Recherche für SPÖ Connect, `connect-spoe/docs/chat-app-pilot-release.md` Abschnitt 9) oder „2026-10-18“ (Plan 7.3) steht. Keine rechtliche Bewertung.

### 11.1 Apple

- Richtlinie 4.2 („elevate it beyond a repackaged website“), 4.2.2 (keine Web-Ausschnitte/Linksammlungen), 3.1.1 Trinkgeld per In-App-Kauf, 3.1.1(a) keine Links zu anderen Zahlungswegen außer im US-Store, 3.2.2(iv) Spenden nur anerkannte Gemeinnützige, 5.1.1(i) Datenschutz-Link in Metadaten und App, 5.1.1(v) Kontolöschung bei Kontoerstellung. Quelle: [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- 99 USD pro Jahr in Landeswährung; Einzelperson erscheint mit bürgerlichem Namen. Quelle: [Program enrollment](https://developer.apple.com/help/account/membership/program-enrollment).
- Name 2–30, Untertitel 30, Datenschutz-URL Pflicht (iOS). Quelle: [App information](https://developer.apple.com/help/app-store-connect/reference/app-information/app-information).
- Beschreibung 4000, Werbetext 170, Schlüsselwörter 100 Byte, Support-URL Pflicht. Quelle: [Platform version information](https://developer.apple.com/help/app-store-connect/reference/app-information/platform-version-information).
- Screenshots 1–10 je Größe, iPhone (Dynamic Island) und iPad 13 Zoll Pflicht. Quelle: [Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications).
- DSA-Händlerstatus. Quelle: [Manage EU DSA trader requirements](https://developer.apple.com/help/app-store-connect/manage-compliance-information/manage-european-union-digital-services-act-trader-requirements).
- Datenschutzangaben, „collect“ nur bei Übertragung vom Gerät. Quelle: [App privacy details](https://developer.apple.com/app-store/app-privacy-details/) (2026-10-21).
- TestFlight intern/extern, Beta-App-Prüfung, 90 Tage. Quellen: [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview), [Invite external testers](https://developer.apple.com/help/app-store-connect/test-a-beta-version/invite-external-testers) (2026-10-21).
- Exportkontrolle, „Missing Compliance“. Quellen: [ITSAppUsesNonExemptEncryption](https://developer.apple.com/documentation/bundleresources/information-property-list/itsappusesnonexemptencryption), [Export compliance for beta builds](https://developer.apple.com/help/app-store-connect/test-a-beta-version/provide-export-compliance-information-for-beta-builds) (2026-10-21).
- Xcode 26 / iOS-26-SDK seit 2026-04-28. Quelle: [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) (2026-10-21).
- Privacy Manifest seit 2024-05-01. Quelle: [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files) (2026-10-21).

### 11.2 Google Play

- Geschlossener Test für private Konten nach 2023-11-13: 12 Tester, 14 Tage ununterbrochen, Prüfung meist ≤ 7 Tage. Quelle: [14151465](https://support.google.com/googleplay/android-developer/answer/14151465).
- 25 USD einmalig, Zusatzpflichten für private Konten. Quelle: [6112435](https://support.google.com/googleplay/android-developer/answer/6112435).
- Datensicherheit Pflicht für alle veröffentlichten Apps (auch ohne Erhebung, mit Datenschutz-Link), interne Tests ausgenommen, lokale Verarbeitung nicht „erhoben“. Quelle: [10787469](https://support.google.com/googleplay/android-developer/answer/10787469).
- Zahlungen: keine Links zu anderen Zahlungswegen, Ausnahmen u. a. steuerbefreite Spenden. Quelle: [9858738](https://support.google.com/googleplay/android-developer/answer/9858738).
- Store-Grafiken und Texte: [9866151](https://support.google.com/googleplay/android-developer/answer/9866151), [9859152](https://support.google.com/googleplay/android-developer/answer/9859152).
- Interner Test bis 100, keine Standardprüfung: [9845334](https://support.google.com/googleplay/android-developer/answer/9845334) (2026-10-21). Play App Signing: [9842756](https://support.google.com/googleplay/android-developer/answer/9842756) (2026-10-21). AAB-Pflicht: [developer.android.com/guide/app-bundle](https://developer.android.com/guide/app-bundle) (2026-10-21).
- Ziel-API 36 seit 2026-08-31 (Projekt: SDK 36). Quelle: [11926878](https://support.google.com/googleplay/android-developer/answer/11926878) (2026-10-21).
- Kontolöschung nur bei Kontoerstellung. Quelle: [13327111](https://support.google.com/googleplay/android-developer/answer/13327111) (2026-10-21).
- Capacitor 8: iOS 15+, Android API 24+, Node 22, Xcode 26. Quelle: [Capacitor support policy](https://capacitorjs.com/docs/next/main/reference/support-policy) (2026-10-18).
- DSA-Händlerstatus bei Google Play: offizielle Hilfeseite nicht gefunden **[offen]**.
