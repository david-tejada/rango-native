#!/usr/bin/python3

import pathlib
import platform
import os
from pathlib import Path
import json
import os
import stat

messenger_path = os.path.dirname(__file__) + "/messenger.py"

# Make messenger.py executable
st = os.stat(messenger_path)
os.chmod(messenger_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def get_path(path):
  """Creates the folder if it doesn't exist and returns the full path"""
  path = os.path.expanduser(path)
  parent_folder = os.path.dirname(path)
  isExist = os.path.exists(parent_folder)

  if not isExist:
    os.makedirs(parent_folder)
    
  return Path(path)

manifest = {
  "name": "rango",
  "description": "Native application host to use in conjunction with the rango extension and talon",
  "path": messenger_path,
  "type": "stdio",
  "allowed_extensions": ["rango@david-tejada"]
}

# For Linux and macOS the only thing we have to do is to create the host manifest at 
# the specified location. For windows it doesn't matter where we put the host 
# manifest but we have to create a registry key specifying the path

if platform.system() == "Linux":
  host_manifest_path = get_path("~/.mozilla/native-messaging-hosts/rango.json")

# TODO: Check that it works in Windows and macOS

# macOS
if platform.system() == "Darwin":
  host_manifest_path = get_path("~/Library/Application Support/Mozilla/NativeMessagingHosts/rango.json")

# Since it doesn't matter where we put the file, we put it in this same folder
if platform.system() == "Windows":
  import winreg
  host_manifest_path = get_path(os.path.dirname(__file__) + "/rango.json")

  REG_PATH = R"SOFTWARE\Mozilla\NativeMessagingHosts"
  print(REG_PATH)


  def set_reg(name, value):
    try:
        winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, 
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False

  set_reg("rango", host_manifest_path)

with host_manifest_path.open("w") as out_file:
  out_file.write(json.dumps(manifest))
