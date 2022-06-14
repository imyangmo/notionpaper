import requests

# def indexInfoGetter(global_configs):
#     r = requests.get(global_configs['notion_api_base_url'] + 'databases/' + global_configs['toc_id'], headers=headers)
#     return(r.json())


def indexInfoFetcher(baseURL, tocID, headers):
    r = requests.get(baseURL + 'databases/' + tocID, headers=headers)
    return(r.json())


def indexContentFetcher(baseURL, tocID, headers):
    # query_body = ""



    query_body = {
        "filter": {
            "and": [
                {
                    "property": "Name",
                    "rich_text": {
                        "is_not_empty": True
                    }
                },
                {
                    "property": "Publish",
                    "checkbox": {
                        "equals": True
                    }
                }
            ]
        }
    }
    # query_body = "{'filter':{'and':[{'property':'Name','rich_text':{'is_not_empty':True}},{'property':'Publish','checkbox':{'equals':True}}]}}"
    r = requests.post(baseURL + 'databases/' + tocID +
                      '/query', headers=headers, json=query_body)
    print(r.json())
    return(r.json())

# def pageInfoGetter(pageId):
#     r = requests.get(global_configs['notion_api_base_url'] + 'pages/' + pageId, headers=headers)
#     return(r.json())


def pageInfoFetcher(baseURL, pageId, headers):
    r = requests.get(baseURL + 'pages/' + pageId, headers=headers)
    return(r.json())


# def pageBlockGetter(pageId, next_cursor=None):
#     print("Retriving contents for {} with cursor {}".format(pageId, next_cursor))
#     params = {}
#     if next_cursor != None:
#         params = {'start_cursor':next_cursor}
#     r = requests.get(global_configs['notion_api_base_url'] + 'blocks/' + pageId + '/children', headers=headers, params=params)
#     print("Done retriving contents for {} with cursor {}".format(pageId, next_cursor))
#     # print(r.json())
#     return(r.json())

def pageBlockFetcher(baseURL, pageId, headers, next_cursor=None):
    print("Retriving contents for {} with cursor {}".format(pageId, next_cursor))
    params = {}
    if next_cursor != None:
        params = {'start_cursor': next_cursor}
    r = requests.get(baseURL + 'blocks/' + pageId +
                     '/children', headers=headers, params=params)
    print("Done retriving contents for {} with cursor {}".format(pageId, next_cursor))
    return(r.json())
