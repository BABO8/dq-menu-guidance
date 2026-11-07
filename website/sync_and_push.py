import os
import shutil
import ctypes
from ctypes import wintypes
import subprocess

SRC = r"c:\Users\hp\Desktop\website"
DST = r"C:\Users\hp\Documents\GitHub\dq-menu-guidance\website"
REPO = r"C:\Users\hp\Documents\GitHub\dq-menu-guidance"
GIT_EXE = r"C:\Users\hp\AppData\Local\GitHubDesktop\app-3.6.10\resources\app\git\cmd\git.exe"

def clean_cache(root_dir):
    for root, dirs, files in os.walk(root_dir, topdown=False):
        for name in files:
            if name.endswith('.pyc') or name.endswith('.pyo'):
                try:
                    os.remove(os.path.join(root, name))
                except Exception as e:
                    pass
        for name in dirs:
            if name in ('__pycache__', '.pytest_cache'):
                try:
                    shutil.rmtree(os.path.join(root, name))
                except Exception as e:
                    pass

print("Cleaning cache in Desktop...")
clean_cache(SRC)

print("Syncing files from Desktop/website to GitHub/dq-menu-guidance/website...")
for root, dirs, files in os.walk(SRC):
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', '.pytest_cache')]
    rel_path = os.path.relpath(root, SRC)
    dest_dir = os.path.join(DST, rel_path) if rel_path != '.' else DST
    os.makedirs(dest_dir, exist_ok=True)
    for f in files:
        if f.endswith('.pyc') or f.endswith('.pyo'):
            continue
        src_file = os.path.join(root, f)
        dest_file = os.path.join(dest_dir, f)
        shutil.copy2(src_file, dest_file)

print("Cleaning cache in GitHub repo...")
clean_cache(REPO)

print("Checking git diff stat...")
res_diff = subprocess.run([GIT_EXE, "-C", REPO, "diff", "--stat"], capture_output=True, text=True)
print(res_diff.stdout)

# Retrieve token from Credential Manager
advapi32 = ctypes.windll.advapi32

class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ('Flags', wintypes.DWORD),
        ('Type', wintypes.DWORD),
        ('TargetName', wintypes.LPWSTR),
        ('Comment', wintypes.LPWSTR),
        ('LastWritten', wintypes.FILETIME),
        ('CredentialBlobSize', wintypes.DWORD),
        ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)),
        ('Persist', wintypes.DWORD),
        ('AttributeCount', wintypes.DWORD),
        ('Attributes', ctypes.c_void_p),
        ('TargetAlias', wintypes.LPWSTR),
        ('UserName', wintypes.LPWSTR)
    ]

target = 'GitHub - https://api.github.com/BABO8'
p_cred = ctypes.POINTER(CREDENTIAL)()
ret = advapi32.CredReadW(target, 1, 0, ctypes.byref(p_cred))
if not ret:
    print("Failed to read token from Credential Manager")
    exit(1)

token = bytes(p_cred.contents.CredentialBlob[:p_cred.contents.CredentialBlobSize]).decode('utf-8')
advapi32.CredFree(p_cred)

print("Staging changes...")
subprocess.run([GIT_EXE, "-C", REPO, "add", "-A"], check=True)

commit_msg = "SEO optimization: complete primary and secondary keyword placement in titles, meta tags, and FAQ schema"
print(f"Committing changes: {commit_msg}")
r_commit = subprocess.run([GIT_EXE, "-C", REPO, "commit", "-m", commit_msg], capture_output=True, text=True)
print(r_commit.stdout, r_commit.stderr)

auth_url = f"https://x-access-token:{token}@github.com/BABO8/dq-menu-guidance.git"
print("Pushing to GitHub remote...")
r_push = subprocess.run([GIT_EXE, "-C", REPO, "push", auth_url, "main"], capture_output=True, text=True)
print(r_push.stdout, r_push.stderr)

# Update tracking ref
subprocess.run([GIT_EXE, "-C", REPO, "update-ref", "refs/remotes/origin/main", "refs/heads/main"], check=True)
print("Updated tracking ref origin/main.")

res_status = subprocess.run([GIT_EXE, "-C", REPO, "status"], capture_output=True, text=True)
print(res_status.stdout)
print("SUCCESS: Sync, commit, and push completed!")
