"""install が、設定ディレクトリの agent-config-path.txt に agent-config の場所を書くことを確かめる中のテスト。

子プロセスで install を走らせ、設定ディレクトリを一時フォルダに向ける。
大きさは中(ADR 0009-2: 印の無い道具ではファイル名に .medium)。
実行(リポジトリのルートで): python tests/test_install_records_repo_path.medium.py -v
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = sys.platform == "win32"


def norm(path):
    return os.path.normcase(os.path.realpath(str(path).strip()))


def main_working_tree():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "worktree", "list", "--porcelain"],
        capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL,
    ).stdout
    first = out.splitlines()[0]
    assert first.startswith("worktree ")
    return first[len("worktree "):]


def copy_outside_git(tmp, script_name):
    """git の外に install と claude/ だけを写す。"""
    dest = Path(tmp) / "outside-git"
    dest.mkdir()
    shutil.copy2(ROOT / script_name, dest / script_name)
    shutil.copytree(ROOT / "claude", dest / "claude")
    return dest


@unittest.skipUnless(WINDOWS and shutil.which("powershell"), "Windows の powershell でだけ走らせる")
class install_ps1が書く場所(unittest.TestCase):
    def run_install(self, script):
        home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, home, True)
        (Path(home) / ".claude-work").mkdir()
        env = dict(os.environ, USERPROFILE=home)
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), "-Yes"],
            env=env, stdin=subprocess.DEVNULL, capture_output=True, check=True,
        )
        return home

    def recorded(self, home):
        return [
            (Path(home) / d / "agent-config-path.txt").read_text(encoding="utf-8")
            for d in (".claude", ".claude-work")
        ]

    def test_install_ps1は_worktreeから走らせても_どの設定ディレクトリにも本体の作業ツリーの場所を書く(self):
        home = self.run_install(ROOT / "install.ps1")
        for text in self.recorded(home):
            self.assertEqual(norm(text), norm(main_working_tree()))

    def test_install_ps1は_gitの外から走らせると_install_ps1のある場所を書く(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        outside = copy_outside_git(tmp, "install.ps1")
        home = self.run_install(outside / "install.ps1")
        for text in self.recorded(home):
            self.assertEqual(norm(text), norm(outside))


@unittest.skipUnless(not WINDOWS and shutil.which("bash"), "Windows 以外の bash でだけ走らせる")
class install_shが書く場所(unittest.TestCase):
    def run_install(self, script):
        home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, home, True)
        (Path(home) / ".claude-work").mkdir()
        env = dict(os.environ, HOME=home)
        subprocess.run(
            ["bash", str(script), "--yes"],
            env=env, stdin=subprocess.DEVNULL, capture_output=True, check=True,
        )
        return home

    def recorded(self, home):
        return [
            (Path(home) / d / "agent-config-path.txt").read_text(encoding="utf-8")
            for d in (".claude", ".claude-work")
        ]

    def test_install_shは_worktreeから走らせても_どの設定ディレクトリにも本体の作業ツリーの場所を書く(self):
        home = self.run_install(ROOT / "install.sh")
        for text in self.recorded(home):
            self.assertEqual(norm(text), norm(main_working_tree()))

    def test_install_shは_gitの外から走らせると_install_shのある場所を書く(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        outside = copy_outside_git(tmp, "install.sh")
        home = self.run_install(outside / "install.sh")
        for text in self.recorded(home):
            self.assertEqual(norm(text), norm(outside))


if __name__ == "__main__":
    unittest.main()
