import requests, json, yaml, uuid
import os, shutil, re
import socket, socks
from jinja2 import Environment, FileSystemLoader, select_autoescape

# BEGIN global variables
global_indexTitle = ""
global_pageList = []
global_configs = {}
# END global variables

def fileSaver(url, path):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"}
    r = requests.get(url, allow_redirects=True, headers = header)
    open(path, 'wb').write(r.content)



# BEGIN table of contents generator
def indexInfoGetter():
    r = requests.get(global_configs['notion_api_base_url'] + 'databases/' + global_configs['toc_id'], headers=headers)
    return(r.json())

def tocGetter():
    query_body = {
        "filter": {
            "property": "Name",
            "rich_text": {
                "is_not_empty": True
            }
        }
    }
    r = requests.post(global_configs['notion_api_base_url'] + 'databases/' + global_configs['toc_id'] + '/query', headers=headers, data=query_body)
    return(r.json())

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


def tocParser(content):
    full = []
    for each in content:
        item = {}
        if 'Original Create Time' in each['properties'] and each['properties']['Original Create Time']['date'] != None:
            item['date'] = dateFormatter(each['properties']['Original Create Time']['date']['start'])['date']
            item['time'] = dateFormatter(each['properties']['Original Create Time']['date']['start'])['time']
        else:
            print('Original Create Time not found, or Original Create Time is empty, switch to Create Time')
            if 'Create Time' in each['properties']:
                item['date'] = dateFormatter(each['properties']['Create Time']['created_time'])['date']
                item['time'] = dateFormatter(each['properties']['Create Time']['created_time'])['time']
            else:
                return({'code':'error', 'msg':'No Create Time or Original Create Time found'})

        item['title'] = each['properties']['Name']['title'][0]['text']['content']
        item['addr'] = each['url'][-32:]
        # !!todo empty row handling
        global_pageList.append(each['url'][-32:])
        full.append(item)
    return(full)

def tocGenerator():
    indexObject = {}
    print("Retriving database infos")
    indexInfoJson = indexInfoGetter()
    print(indexInfoJson)
    print("Done")

    if indexInfoJson['object'] == 'error':
        return({'code': 'error', 'msg':indexInfoJson['message']})
        # {'object': 'error', 'status': 404, 'code': 'object_not_found', 'message': 'Could not find database with ID: a0cb2faf-978a-4843-b982-e943986fd3c5. Make sure the relevant pages and databases are shared with your integration.'} 

    global global_indexTitle
    global_indexTitle = indexInfoJson['title'][0]['plain_text']
    indexObject['site_name'] = indexInfoJson['title'][0]['plain_text']

    if indexInfoJson['icon'] != None:
        if indexInfoJson['icon']['type'] == 'emoji':
            indexObject['icon'] = {'type': 'emoji', 'emoji':indexInfoJson['icon']['emoji']}
        elif indexInfoJson['icon']['type'] == 'file':
            fileSaver(indexInfoJson['icon']['file']['url'], './_prebuild/favicon')
            indexObject['icon'] = {'type': 'emoji'}
        elif indexInfoJson['icon']['type'] == 'external':
            indexObject['icon'] = {'type': 'external','url':indexInfoJson['icon']['external']['url']}
    else:
        indexObject['icon'] = None

    print("Retriving database pages")
    rawjson = tocGetter()
    print("Done")
    contents = rawjson['results']
    print(json.dumps(contents))
    print("Generating TOC")
    indexObject['contents'] = tocParser(contents)
    print("Done")

    # print(global_pageList)
    indexObject['ga'] = global_configs['google_analytics']

    template = env.get_template("index.html")
    print(indexObject)
    template.stream(index_object = indexObject).dump('./_prebuild/index.html')

    return({'code': 'ok', 'msg':''})

# END table of contents generator




# BEGIN page genenrator

def pageInfoGetter(pageId):
    r = requests.get(global_configs['notion_api_base_url'] + 'pages/' + pageId, headers=headers)
    return(r.json())

def pageBlockGetter(pageId, next_cursor=None):
    print("Retriving contents for {} with cursor {}".format(pageId, next_cursor))
    params = {}
    if next_cursor != None:
        params = {'start_cursor':next_cursor}
    r = requests.get(global_configs['notion_api_base_url'] + 'blocks/' + pageId + '/children', headers=headers, params=params)
    print("Done")
    # print(r.json())
    return(r.json())

def richTextParser(content):
    # Init block text dict
    textBlock = {}
    # Append text contents
    textBlock['content'] = content['plain_text']
    # Append text color
    textBlock['color'] = content['annotations']['color']
    # Init annotation list
    annotations = ""
    # Notion could display texts with strikethrough and underline simultaneously, but simply put two text decoration styles together will be override by another, so this needs to be handle seperately.
    if content['annotations']['strikethrough'] == True and content['annotations']['underline'] == True:
        annotations = annotations + " standul"
    # Append rest of annotaitons
    for key, value in content['annotations'].items():
        if key != 'color' and key != 'strikethrough' and key != 'underline' and value != False:
        # Skip color annotation and others that does not applied
            annotations = annotations + " " + key

    textBlock['annotations'] = annotations

    if content['href'] != None:
        textBlock['link'] = content['href']
    else:
        textBlock['link'] = None

    return(textBlock)

def pageParser(pageId, results):
    full = []

    textBlocks = ['heading_1','heading_2','heading_3','paragraph']
    mediaBlocks = ['image','video']
    listBlocks = ['numbered_list_item','bulleted_list_item']

    # jsonfied = json.loads(results)
    for each in results['results']:
        block = {}
        block['type'] = each['type']
        

        if each['type'] in textBlocks:
            block['text'] = []
            for eachTxt in each[each['type']]['rich_text']:
                block['text'].append(richTextParser(eachTxt))
        elif each['type'] in mediaBlocks:
            if each[each['type']]['type'] == 'file':
                fileName = str(uuid.uuid1())
                print("Retriving image from {}".format(each[each['type']]['file']['url']))
                # urllib.request.urlretrieve(each[each['type']]['file']['url'],'./_prebuild/' + pageId + '/' + fileName )
                fileSaver(each[each['type']]['file']['url'], './_prebuild/' + pageId + '/' + fileName)
                block['url'] = fileName
            elif each[each['type']]['type'] == 'external':
                fileName = str(uuid.uuid1())
                print("Retriving image from {}".format(each[each['type']]['external']['url']))
                # urllib.request.urlretrieve(each[each['type']]['external']['url'],'./_prebuild/' + pageId + '/' + fileName )
                fileSaver(each[each['type']]['external']['url'], './_prebuild/' + pageId + '/' + fileName)
                block['url'] = fileName
        elif each['type'] == 'table':
            block['rows'] = []
            tableContentRaw = pageBlockGetter(each['id'])
            for eachResult in tableContentRaw['results']:
            # eachResult is an row of the table
                rowArr = []
                for eachCell in eachResult['table_row']['cells']:
                # eachCell is a cell in each row
                    textArr = []
                    for eachText in eachCell:
                        textArr.append(richTextParser(eachText))
                    rowArr.append(textArr)
                block['rows'].append(rowArr)
        elif each['type'] in listBlocks:
            block['listItems'] = []
            textArr = []
            for eachTxt in each[each['type']]['rich_text']:
                textArr.append(richTextParser(eachTxt))
            block['listItems'].append(textArr)
        elif each['type'] == 'code':
            block['language'] = "language-" + each[each['type']]['language']
            block['contents'] = ""
            for eachTxt in each[each['type']]['rich_text']:
                block['contents'] = block['contents'] + eachTxt['plain_text']

        full.append(block)

    # merge list items
    i = 0
    while i in range(len(full)):
        if full[i]['type'] in listBlocks:
        # if current item is a list item, then countinue, otherwise skip
            try:
                full[i+1]
                # if current item is the last in the list, then skip
            except IndexError:
                print("this is the last item")
                i += 1
            else:
                if full[i]['type'] == full[i+1]['type']:
                    full[i]['listItems'].append(full[i+1]['listItems'][0])
                    del full[i+1]
                else:
                    i += 1
        else:
            i += 1

    return(full)

def pageGenerator(pageIdList):
    for eachId in pageIdList:
        pageObject = {}
        # Create a dir for each page
        path = os.getcwd() + '/_prebuild/' + eachId
        os.makedirs(path)

        # Fetch page contents
        pageContent = []
        next_cursor = None
        while True:
            contentRst = pageBlockGetter(eachId, next_cursor)
            parsedContentRst = pageParser(eachId, contentRst)
            pageContent = pageContent + parsedContentRst
            if contentRst['has_more'] == False:
                break
            else:
                next_cursor = contentRst['next_cursor']

        # Fetch page information
        titleRst = pageInfoGetter(eachId)
        pageObject['page_title'] = titleRst['properties']['Name']['title'][0]['plain_text']
        
        if titleRst['cover'] == None:
            pageObject['cover'] = None
        elif titleRst['cover']['type'] == 'file':
            fileName = str(uuid.uuid1())
            print("Retriving cover image from {}".format(titleRst['cover']['file']['url']))
            fileSaver(titleRst['cover']['file']['url'], './_prebuild/' + eachId + '/' + fileName)
            pageObject['cover'] = fileName
        elif titleRst['cover']['type'] == 'external':
            fileName = str(uuid.uuid1())
            print("Retriving cover image from {}".format(titleRst['cover']['external']['url']))
            fileSaver(titleRst['cover']['external']['url'], './_prebuild/' + eachId + '/' + fileName)
            pageObject['cover'] = fileName

        pageObject['site_name'] = global_indexTitle
        pageObject['contents'] = pageContent
        pageObject['ga'] = global_configs['google_analytics']

        template = env.get_template("article.html")
        print(json.dumps(pageObject))
        template.stream(page_object = pageObject).dump('./_prebuild/' + eachId + '/' + eachId + '.html')
# END page generator

# BEGIN before building
def proxySetter(settings):
    if settings['enable'] != False:
        print("Setting proxy: {}:{}".format(settings['address'],settings['port']))
        socks.set_default_proxy(socks.SOCKS5, settings['address'], settings['port'])
        socket.socket = socks.socksocket
        return True
    else:
        print("Proxy is empty, skipping proxy setting.")
        return True

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

def configReader():
    print("Reading config file.")
    f = open(r'config.yml')
    config = yaml.safe_load(f)
    f.close()

    if len(config['toc_id']) - config['toc_id'].count(" ") == 0:
        print("You need to specify your table of contents page id.")
        return(False)
    if len(config['notion_token']) - config['notion_token'].count(" ") == 0:
        print("You need generate an valid global_configs['notion_token'].")
        return(False)
    if len(config['notion_version']) - config['notion_version'].count(" ") == 0:
        print("You need specify an notion version.")
        return(False)
    if len(config['notion_api_base_url']) - config['notion_api_base_url'].count(" ") == 0:
        print("You need specify an notion api address.")
        return(False)
    if len(config['theme']) - config['theme'].count(" ") == 0:
        print("You need specify an theme.")
        return(False)
    global global_configs
    global_configs = config
    print(global_configs)
    print("Done")
    return True
# END before building

# BEGIN after building
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
# END after building

if __name__ == '__main__':
    if configReader():
        print(global_configs)
        # BEGIN Set up global variables
        env = Environment(
            loader=FileSystemLoader("./themes/" + global_configs['theme']),
            autoescape=select_autoescape()
        )

        headers = {'Authorization':'Bearer ' + global_configs['notion_token'], 'Notion-Version': global_configs['notion_version']}
        # END Set up global variables
        proxySetter(global_configs['proxy'])
        buildDirPrep("./themes/" + global_configs['theme'] + "/style", "./_prebuild/style")
        tocResult = tocGenerator()
        if tocResult['code'] == 'ok':
            pageGenerator(global_pageList)
            buildDirFinisher()
        else:
            print(tocResult['msg'])
            exit()
        
