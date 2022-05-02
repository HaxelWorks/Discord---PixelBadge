#%% SETUP
from time import sleep
import os
import pathlib
from mp.mpfshell import MpFileShell
from mp.mpfexp import RemoteIOError
from tqdm import tqdm

APP_NAME = "Disclock"
LOCAL_PATH = f"./{APP_NAME}/"
REMOTE_PATH = f"apps/{APP_NAME}/"


mpfs = MpFileShell()
mpfs.do_open("COM3")
fe = mpfs.fe
fe.cd("apps")
fe.cd(APP_NAME)

#%%
local_filenames = set([f for f in os.listdir(LOCAL_PATH) if f.endswith(".py")])
remote_filenames = set([f for f in fe.ls() if f.endswith(".py")])

deleted_files = remote_filenames - local_filenames
added_files = local_filenames - remote_filenames
existing_files = remote_filenames & local_filenames


print(f"Deleted files: {deleted_files}")
print(f"Added files: {added_files}")
print(f"Existing files: {existing_files}")

# %% Delete unused files
if deleted_files:
    print(f"Deleting {len(deleted_files)} files...")
    for f in tqdm(deleted_files, desc="💣"):
        try:
            fe.rm(f)
            print(f"Deleted {f} ")
        except RemoteIOError:
            print(f"Failed to delete {f}")

# %% Upload new files
if added_files:
    print(f"Uploading {len(added_files)} new files...")
    for f in tqdm(added_files, desc="📁"):
        try:
            fe.put(LOCAL_PATH + f, f)
            print(f"Uploaded {f}")
        except RemoteIOError:
            print(f"Failed to upload {f}")


# %% Find changed files
if existing_files:
    for f in tqdm(existing_files, desc="🔍"):
        remote = fe.gets(f)
        local = open(LOCAL_PATH + f, "rb").read().decode("ascii")
        
        if remote != local:
            #remove old file
            fe.rm(f)
            #upload new file
            fe.puts(f, local)
            print(f"Updated {f}")

#%% Restart the system
print("Restarting...")
mpfs.do_exec("from system import reboot")
mpfs.do_exec("reboot()")
sleep(3)
mpfs.do_repl()

# %%
