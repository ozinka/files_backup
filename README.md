# Python script for backup files and folders

##files_backup.py

File **config.yaml** should be present in the same folder as script.

If you need to additionally encrypt the content, install **7zip** into the system, create password file (e.g. **psw.txt**) and amend config.yaml respectively. It is recommended to save file in different safe place (c:\Users\username\psw.txt, etc.)

Example of file **config.yaml.example** may be used (with renaming to **config.yaml**).

## Options (config file)

**keep_version** option in the configuration means how many archives to keep. If more, older version will be deleted. If **0**, old versions won't be deleted.

**encrypt** can be **true** of **false**. In case of **true** will be additionally encrypted and required **7zip** installed. Also option **psw_file** should be set. Headers will be encrypted as well.

**psw_file** is path to text file with one line - password.

**psw.encrypt** generates MD5 or SHA256 hash and it used instead of password for archive encryption. Can be "None", "md5" or "sha256".

Folders can contain ignore files. In this case folder to compress should end with colon and files/folder to ignore should be pasted below with additional identation like:
```yaml
dir_paths:
  - C:\GIT\test:
      - .venv
      - .git
      - license
  - C:\Users\username\Documents
```
Please note, **.venv** means the same as **.venv*** and all files which contain in the file name:

c:\GIT\test\.venv

like 
```text
c:\GIT\test\.venv_01
c:\GIT\test\.venv\file.txt
c:\GIT\test\.venv_01\folder1\file2.txt
```


will be ignored.


## Additional
After every run it creates log file in the same folder.

Script was tested on Windows 10.

Name of zipped files container full path to the file, e.g. **C_Repo_SSL_update.zip**

## Framework:

* Python 3.7

## How to start

* Install Python 3.7 (may work on older version but wasn't tested). Install required packages:

`pip install -r requirements.txt`

### Usage
`<path to python3.7>python files_backup`

Possible usage - Windows scheduler (cron in Linux).

## password_encrypt.py

This script can be used to get hash from the password to decript backup.

### Usage

<pasth to python3.7>python password_encrypt.py