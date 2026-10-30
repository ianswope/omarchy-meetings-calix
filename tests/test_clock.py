import copy
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("meetings_clock", str(ROOT / "bin/meetings-clock"))
spec = importlib.util.spec_from_loader(loader.name, loader)
clock = importlib.util.module_from_spec(spec)
loader.exec_module(clock)


def fixture():
    return {"version": 1, "idle": {"lock": 300}, "bar": {"layout": {
        "left": [{"id": "omarchy.menu"}], "centerBegin": [{"id": clock.PLUGIN_ID, "compact": True}],
        "center": [{"id": "omarchy.clock", "format": "dddd h:mm AP"}],
        "centerEnd": [{"id": "omarchy.weather"}], "right": [], "tray": []}},
        "disabledPlugins": ["unrelated.plugin", clock.PLUGIN_ID]}


class ClockLayoutTests(unittest.TestCase):
    def test_enable_and_restore_preserve_original_settings(self):
        original = fixture()
        enabled, snapshot = clock.enable(original, {}, {"omarchy.clock"})
        self.assertEqual(original, fixture())
        self.assertEqual(enabled["bar"]["layout"]["center"], [{
            "id": clock.PLUGIN_ID, "displayMode": "clock", "format": "dddd h:mm AP", "compact": True}])
        self.assertEqual(enabled["bar"]["layout"]["centerBegin"], [])
        self.assertNotIn(clock.PLUGIN_ID, enabled["disabledPlugins"])
        self.assertEqual(clock.restore(enabled, snapshot), original)

    def test_restore_keeps_later_unrelated_changes(self):
        enabled, snapshot = clock.enable(fixture(), {}, {"omarchy.clock"})
        enabled["bar"]["background"] = "glassy"
        enabled["bar"]["layout"]["right"].append({"id": "new.plugin"})
        enabled["disabledPlugins"].append("new.disabled")
        restored = clock.restore(enabled, snapshot)
        self.assertEqual(restored["bar"]["background"], "glassy")
        self.assertEqual(restored["bar"]["layout"]["right"], [{"id": "new.plugin"}])
        self.assertIn("new.disabled", restored["disabledPlugins"])

    def test_inherits_default_sections_without_losing_user_sections(self):
        enabled, snapshot = clock.enable({"bar": {"layout": {"right": [{"id": "custom"}]}}},
                                         fixture(), {"omarchy.clock"})
        self.assertEqual(enabled["bar"]["layout"]["right"], [{"id": "custom"}])
        self.assertEqual(snapshot["clock"]["entry"]["id"], "omarchy.clock")
        self.assertEqual(enabled["bar"]["layout"]["left"], [{"id": "omarchy.menu"}])

    def test_replaces_cloned_clock_and_restores_same_slot(self):
        original = fixture()
        original["bar"]["layout"]["center"][0]["id"] = "someone.clock"
        original["bar"]["layout"]["center"].insert(0, {"id": clock.PLUGIN_ID})
        enabled, snapshot = clock.enable(original, {}, {"someone.clock"})
        self.assertEqual(clock.restore(enabled, snapshot), original)

    def test_ambiguous_or_missing_clock_does_not_modify_config(self):
        original = fixture()
        before = copy.deepcopy(original)
        with self.assertRaises(ValueError):
            clock.enable(original, {}, {"unknown.clock"})
        self.assertEqual(original, before)
        original["bar"]["layout"]["right"].append({"id": "other.clock"})
        with self.assertRaises(ValueError):
            clock.enable(original, {}, {"omarchy.clock", "other.clock"})

    def test_restore_does_not_duplicate_manually_restored_clock(self):
        enabled, snapshot = clock.enable(fixture(), {}, {"omarchy.clock"})
        enabled["bar"]["layout"]["right"].append({"id": "omarchy.clock", "format": "HH:mm"})
        restored = clock.restore(enabled, snapshot)
        clocks = [e for _, _, e in clock.entries(restored["bar"]["layout"]) if clock.entry_id(e) == "omarchy.clock"]
        self.assertEqual(clocks, [{"id": "omarchy.clock", "format": "HH:mm"}])

    def test_string_clock_entry(self):
        original = fixture()
        original["bar"]["layout"]["center"] = ["omarchy.clock"]
        enabled, snapshot = clock.enable(original, {}, {"omarchy.clock"})
        self.assertEqual(clock.restore(enabled, snapshot), original)

    def test_cli_is_idempotent_and_keeps_dotfile_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_home = root / "config"
            shell = config_home / "omarchy/shell.json"
            shell.parent.mkdir(parents=True)
            dotfile = root / "dotfile.json"
            dotfile.write_text(json.dumps(fixture()))
            shell.symlink_to(dotfile)
            manifest = config_home / f"omarchy/plugins/{clock.PLUGIN_ID}/manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"id": clock.PLUGIN_ID}))
            env = dict(os.environ, XDG_CONFIG_HOME=str(config_home), XDG_STATE_HOME=str(root / "state"),
                       OMARCHY_PATH=str(root / "no-defaults"))
            def run(action):
                return subprocess.run([str(ROOT / "bin/meetings-clock"), action], env=env,
                                      capture_output=True, text=True, check=True)
            run("enable")
            saved = (root / "state/omarchy-meetings/clock-layout.json").read_text()
            run("enable")
            self.assertEqual(saved, (root / "state/omarchy-meetings/clock-layout.json").read_text())
            self.assertTrue(shell.is_symlink())
            run("restore")
            self.assertEqual(json.loads(dotfile.read_text()), fixture())
            self.assertIn("nothing changed", run("restore").stdout)


if __name__ == "__main__":
    unittest.main()
