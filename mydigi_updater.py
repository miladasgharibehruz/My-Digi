import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from urllib.request import Request, urlopen, build_opener, ProxyHandler

APP_NAME = "My Digi"

def log(data_dir, message):
    try:
        path=Path(data_dir)/'update.log'
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path,'a',encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {message}\n")
    except Exception:
        pass

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
    safe_version=''.join(c for c in str(version) if c.isalnum() or c in '.-_') or 'previous'
    dst=root/f"{safe_version}__{time.strftime('%Y%m%d-%H%M%S')}"
    suffix=1
    while dst.exists():
        dst=root/f"{safe_version}__{time.strftime('%Y%m%d-%H%M%S')}-{suffix}"
        suffix+=1
    copy_tree(install_dir,dst/'app')
    data_snapshot=dst/'data'
    data_snapshot.mkdir(parents=True,exist_ok=True)
    excluded={'versions','Updater','update.log','startup-error.log'}
    for item in Path(data_dir).iterdir():
        if item.name in excluded:
            continue
        target=data_snapshot/item.name
        if item.is_dir():
            shutil.copytree(item,target)
        elif item.is_file():
            shutil.copy2(item,target)
    (dst/'backup.json').write_text(json.dumps({
        'version':str(version),
        'created_at':time.strftime('%Y-%m-%dT%H:%M:%S'),
        'app_backup':'app',
        'data_backup':'data',
    },ensure_ascii=False,indent=2),encoding='utf-8')
    # Keep only three backups.
    dirs=sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p:p.stat().st_mtime, reverse=True)
    for old in dirs[3:]: shutil.rmtree(old, ignore_errors=True)
    return dst

def download(url, out):
    req=Request(url,headers={'User-Agent':'My-Digi-Updater/2.0','Accept':'application/octet-stream'})
    try:
        response=urlopen(req,timeout=60)
    except Exception as first_error:
        try:
            response=build_opener(ProxyHandler({})).open(req,timeout=60)
        except Exception as direct_error:
            raise RuntimeError(f'دانلود معمول: {first_error} | دانلود مستقیم: {direct_error}') from direct_error
    with response as r, open(out,'wb') as f:
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
    app_backup=backup/'app'
    if not app_backup.exists():
        app_backup=backup  # Compatibility with backups created by older versions.
    tmp=install_dir.parent/(install_dir.name+'.rollback-temp')
    if tmp.exists(): shutil.rmtree(tmp,ignore_errors=True)
    copy_tree(app_backup,tmp)
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
        log(a.data_dir, f"Updater started: update={a.update}, rollback={a.rollback}, current={a.current_version}, target={a.version}")
        wait_pid(int(a.pid or 0))
        install_dir=Path(a.install_dir).resolve(); data_dir=Path(a.data_dir).resolve()
        if a.rollback:
            log(data_dir, f"Restoring application backup: {a.backup}")
            rollback(a.backup,install_dir)
        elif a.update:
            version=str(a.version or '').strip() or 'unknown'
            backup_path=safe_backup(install_dir,data_dir,version=str(a.current_version or 'previous'))
            log(data_dir, f"Application and user-data backup created: {backup_path}")
            with tempfile.TemporaryDirectory(prefix='mydigi-update-') as td:
                installer=Path(td)/'My-Digi-Setup.exe'
                log(data_dir, f"Downloading release {version} from GitHub")
                download(a.url,installer)
                if a.sha256:
                    got=sha256(installer).lower()
                    expected=str(a.sha256).strip().lower().replace('sha256:','')
                    if got != expected: raise RuntimeError('صحت فایل به‌روزرسانی تأیید نشد؛ نصب متوقف شد.')
                    log(data_dir, "SHA-256 verification succeeded")
                rc=run_installer(installer)
                if rc != 0: raise RuntimeError(f'نصب نسخه جدید با کد {rc} تمام شد.')
                log(data_dir, f"Release {version} installed successfully")
        exe=install_dir/'My Digi.exe'
        if exe.exists(): subprocess.Popen([str(exe)],cwd=str(install_dir),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        return 0
    except Exception as exc:
        log(a.data_dir, f"ERROR: {type(exc).__name__}: {exc}")
        try:
            import tkinter as tk
            from tkinter import messagebox
            r=tk.Tk(); r.withdraw(); messagebox.showerror('My Digi',str(exc)); r.destroy()
        except Exception: pass
        return 1

if __name__=='__main__': raise SystemExit(main())
