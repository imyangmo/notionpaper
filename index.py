from np_core import np_utils, np_block_parser, np_fetcher

import requests, json, yaml, uuid
import os, shutil, time, threading, logging
import socket, socks
from jinja2 import Environment, FileSystemLoader, select_autoescape
from urllib.parse import urlparse, parse_qs

# BEGIN global variables
global_indexTitle = ""
global_pageList = []
global_configs = {}
# END global variables

# BEGIN table of contents generator

def tocParser(content):
    full = []
    for each in content:
        item = {}
        if 'Original Create Time' in each['properties'] and each['properties']['Original Create Time']['date'] != None:
            item['date'] = np_utils.dateFormatter(each['properties']['Original Create Time']['date']['start'])['date']
            item['time'] = np_utils.dateFormatter(each['properties']['Original Create Time']['date']['start'])['time']
        else:
            print('Original Create Time not found, or Original Create Time is empty, switch to Create Time')
            if 'Create Time' in each['properties']:
                item['date'] = np_utils.dateFormatter(each['properties']['Create Time']['created_time'])['date']
                item['time'] = np_utils.dateFormatter(each['properties']['Create Time']['created_time'])['time']
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
    indexInfoJson = np_fetcher.indexInfoFetcher(global_configs['notion_api_base_url'], global_configs['toc_id'], headers)
    # print(indexInfoJson)
    print("Done retriving database infos")

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
            np_utils.fileSaver(indexInfoJson['icon']['file']['url'], './_prebuild/favicon')
            indexObject['icon'] = {'type': 'emoji'}
        elif indexInfoJson['icon']['type'] == 'external':
            indexObject['icon'] = {'type': 'external','url':indexInfoJson['icon']['external']['url']}
    else:
        indexObject['icon'] = None

    print("Retriving database pages")
    rawjson = np_fetcher.indexContentFetcher(global_configs['notion_api_base_url'], global_configs['toc_id'], headers)
    print("Done retriving database pages")
    contents = rawjson['results']
    # print(json.dumps(contents))
    print("Generating index page")
    indexObject['contents'] = tocParser(contents)
    print("Done generating index page")

    # print(global_pageList)
    indexObject['ga'] = global_configs['google_analytics']

    template = env.get_template("index.html")
    # print(indexObject)
    template.stream(index_object = indexObject).dump('./_prebuild/index.html')

    return({'code': 'ok', 'msg':''})

# END table of contents generator




# BEGIN page genenrator

def pageParser(pageId, results):  
    full = []

    headingBlocks = ['heading_1','heading_2','heading_3','paragraph']
    listBlocks = ['numbered_list_item','bulleted_list_item']
    listGroupBlocks = ['numbered_list_item_group','bulleted_list_item_group']

    # jsonfied = json.loads(results)
    for each in results['results']:
        block = {}
        block['type'] = each['type']

        match each['type']:
            case 'paragraph':
                block['text'] = []
                for eachTxt in each[each['type']]['rich_text']:
                    block['text'].append(np_block_parser.richTextParser(eachTxt))
            case 'heading_1' | 'heading_2' | 'heading_3' | 'paragraph':
                block['text'] = []
                for eachTxt in each[each['type']]['rich_text']:
                    block['text'].append(np_block_parser.richTextParser(eachTxt))
                block['id'] = each['id']
            case 'image':
                if each[each['type']]['type'] == 'file':
                    fileName = str(uuid.uuid1())
                    # print("Retriving image from {}".format(each[each['type']]['file']['url']))
                    # urllib.request.urlretrieve(each[each['type']]['file']['url'],'./_prebuild/' + pageId + '/' + fileName )
                    np_utils.fileSaver(each[each['type']]['file']['url'], './_prebuild/' + pageId + '/' + fileName)
                    block['url'] = fileName
                elif each[each['type']]['type'] == 'external':
                    # fileName = str(uuid.uuid1())
                    # print("A external image, skip downloading")
                    block['type'] = 'image_external'
                    # urllib.request.urlretrieve(each[each['type']]['external']['url'],'./_prebuild/' + pageId + '/' + fileName )
                    # fileSaver(each[each['type']]['external']['url'], './_prebuild/' + pageId + '/' + fileName)
                    block['url'] = each[each['type']]['external']['url']
            case 'video':
                if each[each['type']]['type'] == 'file':
                    fileName = str(uuid.uuid1())
                    np_utils.fileSaver(each[each['type']]['file']['url'], './_prebuild/' + pageId + '/' + fileName)
                    block['url'] = fileName
                elif each[each['type']]['type'] == 'external':
                    result = urlparse(each[each['type']]['external']['url'])
                    domain = result.netloc.split('.')
                    if 'youtube' in domain or 'youtu' in domain:
                        block['type'] = 'video_youtube'
                        try:
                            vid = parse_qs(result.query, keep_blank_values=True)['v'][0]
                            block['vid'] = vid
                        except:
                            print('No Youtube video ID found')
                    else:
                        block['type'] = "video_external"
                        block['url'] = each[each['type']]['external']['url']
            case 'table':
                block['rows'] = []
                # tableContentRaw = pageBlockGetter(each['id'])
                tableContentRaw = np_fetcher.pageBlockFetcher(global_configs['notion_api_base_url'], each['id'], headers)

                for eachResult in tableContentRaw['results']:
                # eachResult is an row of the table
                    rowArr = []
                    for eachCell in eachResult['table_row']['cells']:
                    # eachCell is a cell in each row
                        textArr = []
                        for eachText in eachCell:
                            textArr.append(np_block_parser.richTextParser(eachText))
                        rowArr.append(textArr)
                    block['rows'].append(rowArr)
            case 'numbered_list_item' | 'bulleted_list_item':
                block['listItems'] = []
                textArr = []
                for eachTxt in each[each['type']]['rich_text']:
                    textArr.append(np_block_parser.richTextParser(eachTxt))
                block['listItems'].append(textArr)
            case 'code':
                block['language'] = "language-" + each[each['type']]['language']
                block['contents'] = ""
                for eachTxt in each[each['type']]['rich_text']:
                    block['contents'] = block['contents'] + eachTxt['plain_text']
            case 'table_of_contents':
                block['contents'] = []
                for item in results['results']:
                    levels = {
                        "heading_1":1,
                        "heading_2":2,
                        "heading_3":3
                    }
                    if item['type'] in ['heading_1','heading_2','heading_3']:
                        text = ""
                        for span in item[item['type']]['rich_text']:
                            text = text + span['plain_text']
                        tocItem = {'level': levels[item['type']], 'text': text, 'id': item['id']}
                        block['contents'].append(tocItem)
            case 'quote':
                block['text'] = []
                for eachTxt in each[each['type']]['rich_text']:
                    block['text'].append(np_block_parser.richTextParser(eachTxt))
        # if each['type'] == 'paragraph':
        #     block['text'] = []
        #     for eachTxt in each[each['type']]['rich_text']:
        #         block['text'].append(np_block_parser.richTextParser(eachTxt))
        # elif each['type'] in headingBlocks:
        #     block['text'] = []
        #     for eachTxt in each[each['type']]['rich_text']:
        #         block['text'].append(np_block_parser.richTextParser(eachTxt))
        #     block['id'] = each['id']
        # elif each['type'] == 'image':
        #     if each[each['type']]['type'] == 'file':
        #         fileName = str(uuid.uuid1())
        #         # print("Retriving image from {}".format(each[each['type']]['file']['url']))
        #         # urllib.request.urlretrieve(each[each['type']]['file']['url'],'./_prebuild/' + pageId + '/' + fileName )
        #         np_utils.fileSaver(each[each['type']]['file']['url'], './_prebuild/' + pageId + '/' + fileName)
        #         block['url'] = fileName
        #     elif each[each['type']]['type'] == 'external':
        #         # fileName = str(uuid.uuid1())
        #         # print("A external image, skip downloading")
        #         block['type'] = 'image_external'
        #         # urllib.request.urlretrieve(each[each['type']]['external']['url'],'./_prebuild/' + pageId + '/' + fileName )
        #         # fileSaver(each[each['type']]['external']['url'], './_prebuild/' + pageId + '/' + fileName)
        #         block['url'] = each[each['type']]['external']['url']
        # elif each['type'] == 'video':
        #     if each[each['type']]['type'] == 'file':
        #         fileName = str(uuid.uuid1())
        #         np_utils.fileSaver(each[each['type']]['file']['url'], './_prebuild/' + pageId + '/' + fileName)
        #         block['url'] = fileName
        #     elif each[each['type']]['type'] == 'external':
        #         result = urlparse(each[each['type']]['external']['url'])
        #         domain = result.netloc.split('.')
        #         if 'youtube' in domain or 'youtu' in domain:
        #             block['type'] = 'video_youtube'
        #             try:
        #                 vid = parse_qs(result.query, keep_blank_values=True)['v'][0]
        #                 block['vid'] = vid
        #             except:
        #                 print('No Youtube video ID found')
        #         else:
        #             block['type'] = "video_external"
        #             block['url'] = each[each['type']]['external']['url']
        # elif each['type'] == 'table':
        #     block['rows'] = []
        #     # tableContentRaw = pageBlockGetter(each['id'])
        #     tableContentRaw = np_fetcher.pageBlockFetcher(global_configs['notion_api_base_url'], each['id'], headers)

        #     for eachResult in tableContentRaw['results']:
        #     # eachResult is an row of the table
        #         rowArr = []
        #         for eachCell in eachResult['table_row']['cells']:
        #         # eachCell is a cell in each row
        #             textArr = []
        #             for eachText in eachCell:
        #                 textArr.append(np_block_parser.richTextParser(eachText))
        #             rowArr.append(textArr)
        #         block['rows'].append(rowArr)
        # elif each['type'] in listBlocks:
        #     block['listItems'] = []
        #     textArr = []
        #     for eachTxt in each[each['type']]['rich_text']:
        #         textArr.append(np_block_parser.richTextParser(eachTxt))
        #     block['listItems'].append(textArr)
        # elif each['type'] == 'code':
        #     block['language'] = "language-" + each[each['type']]['language']
        #     block['contents'] = ""
        #     for eachTxt in each[each['type']]['rich_text']:
        #         block['contents'] = block['contents'] + eachTxt['plain_text']
        # elif each['type'] == 'table_of_contents':
        #     block['contents'] = []
        #     for item in results['results']:
        #         levels = {
        #             "heading_1":1,
        #             "heading_2":2,
        #             "heading_3":3
        #         }
        #         if item['type'] in ['heading_1','heading_2','heading_3']:
        #             text = ""
        #             for span in item[item['type']]['rich_text']:
        #                 text = text + span['plain_text']
        #             tocItem = {'level': levels[item['type']], 'text': text, 'id': item['id']}
        #             block['contents'].append(tocItem)
        # elif each['type'] == 'quote':
        #     block['text'] = []
        #     for eachTxt in each[each['type']]['rich_text']:
        #         block['text'].append(np_block_parser.richTextParser(eachTxt))
                
        if each['has_children']:
            print("this item has children, fetching....")
            contentRst = np_fetcher.pageBlockFetcher(global_configs['notion_api_base_url'], each['id'], headers)

            block['children'] = pageParser(eachId, contentRst)
        else:
            block['children'] = None

        full.append(block)
    
    
    
    print("=====before==========================================")
    print(full)
    # print(json.dumps(full))
    def merger(full):
        newFull = []
        i = 0
        while i in range(len(full)):
            print("===================================")
            print("当前处理full[%d]" % i)
            if full[i]['type'] not in listBlocks:
                print("当前项full[%d]不为列表，跳过" % i)
                newFull.append(full[i])
                i += 1
            else:
                print("当前项full[%d]为列表" % i)
                try:
                    newFull[-1]
                except:
                    print("newFull是空的")
                    newFull.append({"type":full[i]['type'] + '_group',"origin_type":full[i]['type'],"items":[full[i]]})
                    i += 1
                else:
                    print("newFull不是空的")
                    if newFull[-1]['type'] == full[i]['type'] + '_group':
                        print("newFull最后一项的type和full[%d]一致" % i)
                        newFull[-1]['items'].append(full[i])
                        i += 1
                    else:
                        print("newFull最后一项的type和full[%d]不一致，即新的列表类型" % i)
                        newFull.append({"type":full[i]['type'] + '_group',"origin_type":full[i]['type'],"items":[full[i]]})
                        i += 1
        return newFull
    result = merger(full)
    def iterator(original):
    # rst = merger(original)
        print("开始处理子节点")
        for item in original:
            print("开始处理")
            print(item)
            if item['type'] in listGroupBlocks:
                for each in item['items']:
                    if each['children'] != None:
                        anotherresult = merger(each['children'])
                        print("=====================children")
                        print(anotherresult)
                        print("=====================children end")
                        each['children'] = anotherresult
                        iterator(anotherresult)
    iterator(result)

    # merge list items
    # i = 0
    # while i in range(len(full)):
    #     if full[i]['type'] in listBlocks:
    #     # if current item is a list item, then countinue, otherwise skip
    #         try:
    #             full[i+1]
    #             # if current item is the last in the list, then skip
    #         except IndexError:
    #             # print("this is the last item")
    #             i += 1
    #         else:
    #             if full[i]['type'] == full[i+1]['type']:
    #                 # full[i]['listItems'].append(full[i+1]['listItems'][0])
    #                 full[i]['listItems'].append(full[i+1])
    #                 del full[i+1]
    #             else:
    #                 i += 1
    #     else:
    #         i += 1
    
    
    
    
    
    
    
    
    # i = 0
    # while i in range(len(full)):
    # # start iterating the whole content
    #     if full[i]['type'] in listBlocks:
    #         listGroup = {}
    #         listGroup['type'] = full[i]['type']
    #         listGroup['items'] = []
    #         listGroup['items'].append(full[i])
    #         del full[i]
    #         j = 0
    #         # if current item of the full is a list block, then start a sub iteration to merge them tgt
    #         while j in range(len(full) - i):
    #             try:
    #                 full[i+j+1]
    #             except IndexError:
    #                 # if there is no next item of the full, then quit the sub iteration
    #                 break
    #             else:
    #                 if full[i+j+1]['type'] == listGroup['type']:
    #                     listGroup['items'].append(full[i+j+1])
    #                     del full[i+j+1]
    #                     j += 1
    #                 else:
    #                     full.append(listGroup)
    #                     break
            
    #         print("======list group=========================================")
    #         print(json.dumps(listGroup))
    #         i += 1
    #     else:
    #         i += 1
            
            
            
            
            
            # listGroup.append(full[i])
            # try:
            #     full[i+1]
            # except IndexError:
            #     i += 1
            # else:
            #     if full[i]['type'] == full[i+1]['type']:
            #         # full[i]['items'].append(full[i])
            #         # full[i]['items'].append(full[i+1])
            #         # del full[i+1]
            #         listGroup['type'] = full[i]['type']
            #         listGroup['items'].append(full[i])
            #         i += 1
            #     else:
            #         i += 1
    
    print("======after=========================================")
    print(json.dumps(result))

    return(result)

def pageGenerator(eachId):
    # for eachId in pageIdList:
    pageObject = {}
    # Create a dir for each page
    path = os.getcwd() + '/_prebuild/' + eachId
    os.makedirs(path)

    # Fetch page contents
    pageContent = []
    next_cursor = None
    while True:
        # contentRst = pageBlockGetter(eachId, next_cursor)
        contentRst = np_fetcher.pageBlockFetcher(global_configs['notion_api_base_url'], eachId, headers, next_cursor)

        parsedContentRst = pageParser(eachId, contentRst)
        pageContent = pageContent + parsedContentRst
        if contentRst['has_more'] == False:
            break
        else:
            next_cursor = contentRst['next_cursor']

    # Fetch page information
    titleRst = np_fetcher.pageInfoFetcher(global_configs['notion_api_base_url'], eachId, headers)
    pageObject['page_title'] = titleRst['properties']['Name']['title'][0]['plain_text']
    
    if titleRst['cover'] == None:
        pageObject['cover'] = None
    elif titleRst['cover']['type'] == 'file':
        fileName = str(uuid.uuid1())
        # print("Retriving cover image from {}".format(titleRst['cover']['file']['url']))
        print("Retriving uploaded cover image")
        np_utils.fileSaver(titleRst['cover']['file']['url'], './_prebuild/' + eachId + '/' + fileName)
        
        pageObject['cover'] = {'type': 'file', 'fileName': fileName}
    elif titleRst['cover']['type'] == 'external':
        fileName = str(uuid.uuid1())
        # print("Retriving cover image from {}".format(titleRst['cover']['external']['url']))
        print("Cover image is external, skip retriving")
        # np_utils.fileSaver(titleRst['cover']['external']['url'], './_prebuild/' + eachId + '/' + fileName)
        pageObject['cover'] = {'type': 'external', 'url': titleRst['cover']['external']['url']}

    if 'Original Create Time' in titleRst['properties'] and titleRst['properties']['Original Create Time']['date'] != None:
        pageObject['create_date'] = np_utils.dateFormatter(titleRst['properties']['Original Create Time']['date']['start'])['date']
        pageObject['create_time'] = np_utils.dateFormatter(titleRst['properties']['Original Create Time']['date']['start'])['time']
    else:
        print('Original Create Time not found, or Original Create Time is empty, switch to Create Time')
        if 'Create Time' in titleRst['properties']:
            pageObject['create_date'] = np_utils.dateFormatter(titleRst['properties']['Create Time']['created_time'])['date']
            pageObject['create_time'] = np_utils.dateFormatter(titleRst['properties']['Create Time']['created_time'])['time']
        else:
            return({'code':'error', 'msg':'No Create Time or Original Create Time found'})


    pageObject['site_name'] = global_indexTitle
    pageObject['contents'] = pageContent
    pageObject['ga'] = global_configs['google_analytics']

    template = env.get_template("article.html")
    if debug_mode == 1:
        print(json.dumps(pageObject))
    template.stream(page_object = pageObject).dump('./_prebuild/' + eachId + '/' + eachId + '.html')
    thread_pool.release()
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
    # print(global_configs)
    print("Done reading config file.")
    return True
# END before building

if __name__ == '__main__':
    debug_mode = 0
    # 0: disable;
    # 1: page debug 



    startts = time.perf_counter()

    max_threads = 10
    thread_list = []
    thread_pool = threading.BoundedSemaphore(max_threads)
    
    if configReader():
        # print(global_configs)
        # BEGIN Set up global variables
        env = Environment(
            loader=FileSystemLoader("./themes/" + global_configs['theme']),
            autoescape=select_autoescape()
        )

        headers = {'Authorization':'Bearer ' + global_configs['notion_token'], 'Notion-Version': global_configs['notion_version'], 'Content-Type': 'application/json'}
        # END Set up global variables
        proxySetter(global_configs['proxy'])
        np_utils.buildDirPrep("./themes/" + global_configs['theme'] + "/style", "./_prebuild/style")
        tocResult = tocGenerator()
        if tocResult['code'] == 'ok':
            # pageGenerator(global_pageList)


            if debug_mode == 1:
                global_pageList = ['6ca9e43462b147a281145abf9ccbd187']




            for eachId in global_pageList:
                # pageGenerator(eachId)
                thread_pool.acquire()
                thread = threading.Thread(target=pageGenerator, args=[eachId])
                thread.start()
                thread_list.append(thread)
            for t in thread_list:
                t.join()
            np_utils.buildDirFinisher()
            
        else:
            print(tocResult['msg'])
            exit()
            
        finishts = time.perf_counter()
        print(f"Completed, time elapsed {round(finishts - startts,2)} seconds")
        
