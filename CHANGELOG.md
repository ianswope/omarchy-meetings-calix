# Changelog

## 1.5.0 — 2026-10-30

First public release of the Calix fork, based on Jankees van Woezik's
Omarchy Meetings plugin.

- Read appointments and attendees from Calix's local agenda by default.
- Replace the bar clock with a date/time label that opens the current week.
- Preserve clock position and date/time formats during installation.
- Restore the previous clock and meetings entries without overwriting other
  bar changes, including when configuration lives in a dotfiles symlink.
- Keep separate meetings-button mode and the Google, Microsoft and iCalendar
  providers available.
- Test provider behavior and clock installation/restoration in GitHub Actions.

Requires Omarchy's Quickshell plugin API and Python 3. Calix 0.9.0 or newer is
required for the default provider. Verified on Omarchy 4.5.0rc2-1.
