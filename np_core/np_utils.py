import requests, re, os, shutil, hashlib

def genMD5(str):
    md5 = hashlib.md5()
    md5.update(str.encode('utf-8'))
    return(md5.hexdigest())

def fileSaver(url, path):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"}
    r = requests.get(url, allow_redirects=True, headers = header)
    open(path, 'wb').write(r.content)
    
def dateFormatter(date):
    result = {}
    timePattern = '(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d'
    datePattern = '([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8])))'
    
    time = re.search(timePattern, date)
    date = re.search(datePattern, date)

    if time != None:
        result['time'] = time.group()
    else:
        result['time'] = ''

    if date != None:
        result['date'] = date.group()
    else:
        result['date'] = ''

    return(result)


def buildDirPrep(src,dest):
    path = os.getcwd() + '/_prebuild'

    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except OSError as error:
            print(error)
            print("The prebuild dir '% s' can not be removed" % path)

    os.makedirs(path)
    # copy style folder from theme to prebuild dir
    shutil.copytree(src, dest)
    
def buildDirFinisher():
    path = os.getcwd() + '/build'

    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except OSError as error:
            print(error)
            print("The previous build dir can not be removed, but the build has been completed, you can use _prebuild dir.")

    try:
        os.rename('./_prebuild','./build')
    except OSError as error:
        print(error)
        print("The build dir can not be created, but the build has been completed, you can use _prebuild dir.")