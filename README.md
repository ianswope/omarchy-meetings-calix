# Calix Clock & Meetings

Click the date and time in your Omarchy bar to see your week, with appointments
from Calix in a dropdown beneath the clock. Browse weeks, open appointment
details, and join calls without opening another window.

Clock mode is part of this plugin. It replaces the existing clock entry and
keeps its date/time format; no personal clock clone or QML edits are needed.
The original meetings label is also available if you prefer a separate button.

Your day as a column, with a line where you are in it.

Most calendar widgets answer one question: what is next. That is the least interesting thing your calendar knows. What you actually want to see is the shape of the day: where the meetings sit, where the gaps are, and whether the next two hours are yours or somebody else's. A list cannot show you that, because in a list an hour of nothing looks exactly like no time at all.

So this draws the whole day, or the whole week, the way a calendar does. Appointments sit at their place in time, a line marks now, and the space between two of them is real space.

![The week, with the current time marked](preview.png)

And when the thing you are looking at is about to start, there is a button for it. No hunting for the link in the invite, no scrolling back through the thread it was in.

The bar stays quiet: one line with whatever is running or coming up, and how much time is left on it. No badge, nothing that moves.

This is a fork of [jankeesvw/omarchy-meetings](https://github.com/jankeesvw/omarchy-meetings). The widget is his. With no provider set, this copy reads [Calix](https://github.com/ianswope/calix). Google, Outlook and iCalendar stay available by naming a provider.

## Install

Requires Omarchy's Quickshell bar, Python 3, and
[Calix 0.9.0 or newer](https://github.com/ianswope/calix#install-recommended).
Open Calix and connect your calendars first. Confirm that `calix --agenda`
prints JSON; the plugin reads that local agenda without its own calendar login.
Tested on Omarchy 4.5.0rc2-1. This plugin uses the Quickshell plugin API and does
not work with the older Waybar bar.

```bash
omarchy plugin add https://github.com/ianswope/omarchy-meetings-calix
~/.config/omarchy/plugins/ianswope.meetings/bin/meetings-clock enable
```

Click the date/time to open this week's appointments. The layout reloads
automatically. If plugin code stays cached after installation or an update,
run `omarchy restart shell` once.

The installer detects the stock clock or a clone of it, preserves its position
and date/time formats, and removes any separate meetings button. If you have
multiple clocks, select one with `meetings-clock enable --clock YOUR.CLOCK.ID`.
Other bar entries and settings are kept. Running it again is harmless.

To restore your previous clock and meetings button arrangement:

```bash
~/.config/omarchy/plugins/ianswope.meetings/bin/meetings-clock restore
```

The restore command preserves unrelated bar changes made since installation.
Use it **before removing the plugin**. It also works when `shell.json` is a
symlink to your dotfiles.

### Clock controls

- Left-click: open or close the week dropdown. Each opening starts this week.
- Right-click: switch between the normal and alternate date formats.
- Middle-click: open Omarchy's timezone picker.
- Inside the dropdown: browse weeks, switch to a day, select calendars, or open
  an appointment. Escape closes an appointment's details, then the dropdown.

Clock mode uses `"displayMode": "clock"` in the plugin's bar entry. The
`format`, `formatAlt`, `verticalFormat`, and `verticalFormatAlt` settings accept
Qt date/time formats; `ww` displays the ISO week number. For example:

```bash
omarchy bar set ianswope.meetings format 'dddd h:mm AP'
```

### Separate meetings button

After installing, or after restoring the clock, enable the original label with:

```bash
omarchy plugin enable ianswope.meetings
omarchy bar move ianswope.meetings --section right
```

### Updates

```bash
omarchy plugin update ianswope.meetings
```

Updating keeps your calendar connections and clock layout settings.

## Calix

Calix is the provider when the config does not name one. It is a native GTK calendar that syncs Google, iCloud, Fastmail and CalDAV servers. Connect those accounts in Calix; the widget reads its locally stored agenda. Keep Calix running when you want it to sync new calendar changes. The widget refreshes the visible agenda every minute and preloads the week every 30 minutes.

```bash
calix                  # connect an account in the app, once
calix --calendars      # should print your calendars
calix --agenda         # and this prints today
```

`calix --agenda` has to print JSON. A build older than that flag treats the dates as a day to open and shows a window, which on a widget that refreshes every minute is a window a minute.

Clicking the date, or a day's name, opens that day in Calix. Attendees come with the appointment, from what Calix already stored.

Set `"provider"` to `google`, `microsoft` or `ical` to use one of the sources below instead.

Google Calendar's only requirement is [gcalcli](https://github.com/insanum/gcalcli), which is in the AUR. Because gcalcli is itself a Python program, the interpreter this plugin needs comes along with it.

```bash
yay -S gcalcli
```

## Google Calendar

Until gcalcli is authenticated the panel says so, and hands you the instructions rather than an error.

![Not signed in yet](screenshots/not-signed-in.png)

Two commands:

```bash
gcalcli init     # opens your browser once, asks for calendar access
gcalcli list     # should now print your calendars
```

`init` stores a token in `~/.local/share/gcalcli`. There is nothing to log into separately: this plugin runs gcalcli, and the attendee lookup borrows that same token. If you would rather use your own Google Cloud OAuth client, pass `--client-id` and `--client-secret` to `gcalcli init` and the rest works the same.

## Outlook and Microsoft Teams

Outlook works through [CLI for Microsoft 365](https://pnp.github.io/cli-microsoft365/). Install it and set the provider in `~/.config/omarchy-meetings/config.json`:

```bash
npm i -g @pnp/cli-microsoft365
```

```json
{ "provider": "microsoft" }
```

Set up the CLI with the minimal `User.Read` permission and choose scripting use:

```bash
m365 setup
```

In Microsoft Entra, add the delegated Microsoft Graph permission `Calendars.Read` to the app that `setup` created. Some work accounts need an administrator to approve it. Then sign in:

```bash
m365 login
m365 status --output json
```

The widget uses that login for Outlook. Teams links become the join button, and attendees are fetched only when you open an appointment.

The button in that panel copies a set of instructions to your clipboard, written to be handed straight to a coding agent if you would rather not do it yourself.

![Outlook Calendar in the week view](screenshots/microsoft.png)

## iCalendar feeds

For an exported `.ics` file or a subscribed `https://`/`webcal://` feed, select
the iCalendar adapter and point it at the file or URL:

```json
{
  "provider": "ical",
  "icalPath": "webcal://example.com/private/calendar.ics"
}
```

No additional package or sign-in is required. UTC, numeric-offset and `TZID`
times are converted to local time, and daily or weekly recurring events are
expanded into the visible date range. Attendees travel with the agenda data, so
opening an appointment does not download a remote feed a second time. A meeting
link is picked up from `X-GOOGLE-CONFERENCE`, the Teams equivalents, or an
`https` link in the location or the description, so an appointment out of a feed
joins the same way one out of Google or Outlook does.

A subscribed feed has to be `https://` or `webcal://`. That URL is the whole key to your calendar, and over plain `http://` it crosses the network in the clear, so the panel refuses it and says why rather than downgrading quietly. The feed is read through the same ceiling as every other source, eight megabytes, and anything past it counts as unreachable: half a calendar looks like a week with appointments missing from it.

## What you get

**The week, or one day.** The switch in the header decides, and it remembers what you picked. The day view narrows the panel to a single column and puts the start time in front of every appointment.

![A single day](screenshots/day.png)

**Overlapping appointments side by side.** A focus block from nine to five with three meetings inside it shows all four, the way a calendar does, instead of hiding the short ones behind the long one.

**Getting into the call.** A meeting that is running, or starts within five minutes, puts a join button in the header. One click and you are in it. Outside that window the button is not there, so it never sends you into the wrong call.

**And a minute before it starts, out loud.** The bar has been counting down in a corner you were not looking at, so a call with a link announces itself once with a Join button on the notification. Pressing it opens the call, which is the whole distance between noticing and being in it. Once per appointment, never for one that has already started, and never for an appointment without a link. It needs a notification daemon that advertises actions; without one the notification still arrives, just without the button.

**Which ones are online.** Appointments with a meeting link carry a small camera after the title in the grid, so a glance tells you which ones you click into and which ones you have to walk to.

**One appointment, opened.** Press Enter or click, and it expands into a card over the grid: when it is and how long it runs, which calendar it came from, where it is, who is coming and whether they answered, and the description. Four small buttons under it: join the call, open it in the configured calendar, copy the link, and hide it. They are a glyph and one word each so they fit on one line, and the mouse gets the whole sentence as a tooltip. Escape goes back to the grid.

![An appointment opened over the week](screenshots/detail.png)

**Something you do not need to see.** Not everything on a calendar is worth a line in the bar all day. Hide takes one appointment out of the bar, the day and the week at once. It hides that single occurrence, so the same meeting next week is still there, and entries for days gone by are swept up the next time you hide something, which keeps the list from growing forever. Nothing changes in the calendar itself, only in what this panel draws.

With Google, attendees do not come out of gcalcli's output, so they are fetched from the Calendar API by reusing gcalcli's token. With Microsoft, the widget asks Graph through `m365`. Either way, this happens only for the one appointment you opened and only at the moment you ask for it.

**How much room a gap really is.** Move the mouse into the space between two appointments and it hatches, with the span named in the middle. If that gap is running right now, it counts from this minute rather than from the end of the last meeting, because the part that has already passed is not time you still have.

**Which calendars you see.** The picker at the bottom lists your calendars by name. Untick the one full of other people's birthdays and it is gone from the grid, this week and every week after, until you tick it back.

**Everything from the keyboard.** Tab walks the switch, every appointment and the controls at the bottom. Arrows move between appointments and left and right page through days or weeks. Enter opens what you are on, Escape steps back out.

**A compact bar when space is tight.** Right-click the meeting in the bar to collapse it to a calendar icon. Right-click again to bring the full label back. Left-click still opens the calendar and middle-click refreshes it.

Expanded:

![Expanded meeting label](screenshots/bar-expanded.png)

Compact:

![Compact calendar icon](screenshots/bar-compact.png)

## Colours

Without a config every calendar is drawn in the same grey. Naming them is what makes a week readable at a glance, so write `~/.config/omarchy-meetings/config.json`:

```json
{
  "calendars": [
    { "match": "Work",     "color": "#4a9eff", "priority": 1 },
    { "match": "Personal", "color": "#ff5c5c", "priority": 2 },
    { "match": "Shared",   "color": "#f5c518", "priority": 3 }
  ]
}
```

For Outlook or iCalendar, keep the corresponding `"provider"` and iCalendar's
`"icalPath"` alongside the `calendars` key in that same object.

`match` is a regular expression, tried in order against the calendar name as the selected provider prints it. `priority` decides which appointment the bar picks when two run at once, lowest number first.

Three more keys are optional:

```json
{
  "skipCalendars": ["Birthdays"],
  "skipTitles": ["Out of office"],
  "borrowedCalendar": { "name": "Sam - Work", "label": "Sam's calendar" }
}
```

`skipCalendars` is only the starting position: it decides which calendars come unticked the first time you open the picker, and after that the picker is the answer. `skipTitles` drops appointments by name, which is useful for a standing block that would otherwise take a row every day. `borrowedCalendar` adds a toggle at the bottom that swaps your own day for a colleague's, for when you are looking for a slot in their week. Leave it out and the toggle is not drawn at all.

Changes are picked up on the next refresh, within a minute. No restart needed.

## Light themes

![The same week on a light theme](screenshots/light.png)

## Trying it without a calendar

The plugin can make up a week, which is useful before you set a provider up and for taking screenshots without your own appointments in them:

```json
{ "demo": true }
```

Or from the command line, leaving your config alone:

```bash
~/.config/omarchy/plugins/ianswope.meetings/bin/meetings-widget week --demo | jq
```

## The command line

The script behind the widget is worth something on its own:

```bash
cd ~/.config/omarchy/plugins/ianswope.meetings/bin

./meetings-widget day             # today as JSON
./meetings-widget day 1           # tomorrow, -1 is yesterday
./meetings-widget week            # Monday through Sunday
./meetings-widget calendars       # your calendar names
./meetings-widget attendees "Work" <event-id>
```

Every appointment carries its start and end, its duration in minutes, the calendar it came from, its colour, its location, its description and its links. Which makes `./meetings-widget week | jq '[.days[].events[]] | length'` a fair answer to how bad next week is.

The command reads the provider from `config.json`. With none set, it reads Calix. `MEETINGS_PROVIDER=google`, `MEETINGS_PROVIDER=microsoft`
or `MEETINGS_PROVIDER=ical MEETINGS_ICAL_PATH=/path/to/calendar.ics` overrides
it for one invocation.

## Removing it

```bash
~/.config/omarchy/plugins/ianswope.meetings/bin/meetings-clock restore
omarchy plugin remove ianswope.meetings
```

That leaves three files behind, all of which you can delete by hand:

- `~/.config/omarchy-meetings/config.json`, your provider, colours and filters. Holds the names of your calendars, and the name of the colleague whose calendar you can borrow if you configured one.
- `~/.config/omarchy-meetings/state.json`, which calendars you ticked and whether you left it on the week or the day. Calendar names again.
- `~/.cache/omarchy-meetings/calendars.json`, the provider plus calendar names and ids, kept for an hour so the widget does not ask the provider every minute.

Clock mode additionally saves the prior clock and meetings entries in
`${XDG_STATE_HOME:-~/.local/state}/omarchy-meetings/clock-layout.json` until you
run `restore`. That file contains bar settings, not appointments.

The plugin does not save appointment titles, attendees or descriptions. Calix
maintains its own local calendar database and credentials; removing this plugin
does not remove those or disconnect your calendars. gcalcli and the Microsoft
365 CLI likewise keep their credentials separately.

## Development

```bash
python3 -m unittest discover -s tests -v
omarchy plugin validate .
```

Tests cover calendar providers, recurrence, hidden appointments, and clock
installation/restoration, including dotfile symlinks and subsequent bar edits.
Use demo data for screenshots; never publish a user's actual appointments.

## Licence

MIT. See [LICENSE](LICENSE).
