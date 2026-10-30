import QtQuick
import Quickshell
import qs.Commons as Commons
import qs.Ui

WidgetButton {
  id: root
  property var settings: ({})
  property bool alternate: false

  function setting(name, fallback) {
    var value = settings ? settings[name] : undefined
    return value === undefined || value === null ? fallback : String(value)
  }

  // Qt's date formatter has no ISO week token; support the stock clock's ww.
  function isoWeek(date) {
    var thursday = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
    thursday.setUTCDate(thursday.getUTCDate() + 4 - (thursday.getUTCDay() || 7))
    var yearStart = new Date(Date.UTC(thursday.getUTCFullYear(), 0, 1))
    return String(Math.ceil(((thursday - yearStart) / 86400000 + 1) / 7)).padStart(2, "0")
  }

  readonly property string format: vertical
    ? setting(alternate ? "verticalFormatAlt" : "verticalFormat", alternate ? "dd\nMMM" : "HH\n—\nmm")
    : setting(alternate ? "formatAlt" : "format", alternate ? "d MMMM yyyy" : "dddd HH:mm")

  text: Qt.locale(Commons.I18n.formatLocale).toString(clock.date, format.replace(/ww/g, isoWeek(clock.date)))
  labelVisible: true
  hasVisualContent: true
  horizontalMargin: 8.75
  verticalPadding: 8.75

  SystemClock {
    id: clock
    precision: SystemClock.Minutes
  }
}
