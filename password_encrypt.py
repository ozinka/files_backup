import getpass


def encrypt(psw, pswEncrypt):
    import hashlib
    if str(pswEncrypt).lower() == 'md5':
        m = hashlib.md5()
        m.update(psw.encode('utf-8'))
        return m.hexdigest()
    if str(pswEncrypt).lower() == 'sha256':
        m = hashlib.sha256()
        m.update(psw.encode('utf-8'))
        return m.hexdigest()


def main():
    print('This script generating MD5 and SHA256 hashes for the password.')
    pswd = getpass.getpass('Enter password:')
    md5 = encrypt(pswd, "md5")
    sha256 = encrypt(pswd, "sha256")
    print(f'MD5    : {md5}')
    print(f'SHA256 : {sha256}')


if __name__ == '__main__': main()

# for test
# 098f6bcd4621d373cade4e832627b4f6
# 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
