import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from urllib.request import Request, urlopen

APP_NAME = "My Digi"

def wait_pid(pid, timeout=60):
    if not pid: return
    if os.name != 'nt': return
    try:
        import ctypes
        SYNCHRONIZE = 0x00100000
        h = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, False, int(pid))
        if not h: return
        ctypes.windll.kernel32.WaitForSingleObject(h, int(timeout*1000))
        ctypes.windll.kernel32.CloseHandle(h)
    except Exception:
        for _ in range(int(timeout*10)):
            try:
                os.kill(int(pid), 0)
                time.sleep(.1)
            except Exception:
                break

def elevate_if_needed(argv):
    if os.name != 'nt': return False
    try:
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin(): return False
        params = subprocess.list2cmdline(argv)
        rc = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 1)
        if rc > 32:
            return True
    except Exception:
        pass
    return False

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def copy_tree(src, dst):
    src=Path(src); dst=Path(dst)
    if dst.exists(): shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src,dst)

def safe_backup(install_dir, data_dir, version):
    root=Path(data_dir)/'versions'; root.mkdir(parents=True, exist_ok=True)
    dst=root/version
    if dst.exists(): return dst
    copy_tree(install_dir,dst)
    # Keep only three backups.
    dirs=sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p:p.name, reverse=True)
    for old in dirs[3:]: shutil.rmtree(old, ignore_errors=True)
    return dst

def download(url, out):
    req=Request(url,headers={'User-Agent':'My-Digi-Updater/2.0','Accept':'application/octet-stream'})
    with urlopen(req,timeout=60) as r, open(out,'wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b)

def run_installer(installer):
    # Inno Setup accepts these flags for a quiet upgrade.
    return subprocess.run([str(installer), '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/CLOSEAPPLICATIONS'], check=False).returncode

def rollback(backup, install_dir):
    backup=Path(backup); install_dir=Path(install_dir)
    if not backup.exists(): raise RuntimeError('پشتیبان نسخه قبلی پیدا نشد.')
    tmp=install_dir.parent/(install_dir.name+'.rollback-temp')
    if tmp.exists(): shutil.rmtree(tmp,ignore_errors=True)
    copy_tree(backup,tmp)
    old=install_dir.parent/(install_dir.name+'.rollback-old')
    if old.exists(): shutil.rmtree(old,ignore_errors=True)
    install_dir.rename(old)
    tmp.rename(install_dir)
    shutil.rmtree(old,ignore_errors=True)

def main():
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--update',action='store_true'); ap.add_argument('--rollback',action='store_true')
    ap.add_argument('--pid'); ap.add_argument('--install-dir',required=True); ap.add_argument('--data-dir',required=True)
    ap.add_argument('--url'); ap.add_argument('--version'); ap.add_argument('--current-version'); ap.add_argument('--sha256'); ap.add_argument('--backup')
    a=ap.parse_args()
    if elevate_if_needed(sys.argv[1:]): return 0
    try:
        wait_pid(int(a.pid or 0))
        install_dir=Path(a.install_dir).resolve(); data_dir=Path(a.data_dir).resolve()
        if a.rollback:
            rollback(a.backup,install_dir)
        elif a.update:
            version=str(a.version or '').strip() or 'unknown'
            safe_backup(install_dir,data_dir,version=str(a.current_version or 'previous'))
            with tempfile.TemporaryDirectory(prefix='mydigi-update-') as td:
                installer=Path(td)/'My Digi.exe'
                download(a.url,installer)
                if a.sha256:
                    got=sha256(installer).lower()
                    expected=str(a.sha256).strip().lower().replace('sha256:','')
                    if got != expected: raise RuntimeError('صحت فایل به‌روزرسانی تأیید نشد؛ نصب متوقف شد.')
                rc=run_installer(installer)
                if rc != 0: raise RuntimeError(f'نصب نسخه جدید با کد {rc} تمام شد.')
        exe=install_dir/'My Digi.exe'
        if exe.exists(): subprocess.Popen([str(exe)],cwd=str(install_dir),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        return 0
    except Exception as exc:
        try:
            import tkinter as tk
            from tkinter import messagebox
            r=tk.Tk(); r.withdraw(); messagebox.showerror('My Digi',str(exc)); r.destroy()
        except Exception: pass
        return 1

if __name__=='__main__': raise SystemExit(main())
