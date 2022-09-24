import { DATABASE_ID, NOTION_TOKEN, NOTION_VERSION, NOTION_API_BASE_URL } from "../config"

export async function pageBlockFetcher(id){
    const pageContentResp = await fetch(NOTION_API_BASE_URL + 'blocks/' + id + '/children', {
        method: 'GET',
        headers: {
            'Authorization':'Bearer ' + NOTION_TOKEN,
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        }
    });
    const pageContentData = await pageContentResp.json();
    // console.log(pageContentData)
    
    // const pageParsedDate = pageParser(pageContentData);
    // console.log(pageParsedDate)
    return pageContentData;
}

export async function pageInfoFetcher(id){
    const pageInfoResp = await fetch(NOTION_API_BASE_URL + 'pages/' + id, {
        method: 'GET',
        headers: {
            'Authorization':'Bearer ' + NOTION_TOKEN,
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        }
    });
    const pageInfoData = await pageInfoResp.json();
    return pageInfoData;
}

export async function indexFetcher(){
    const query = {
        "filter": {
            "and": [
                {
                    "property": "Name",
                    "rich_text": {
                        "is_not_empty": true
                    }
                },
                {
                    "property": "Publish",
                    "checkbox": {
                        "equals": true
                    }
                }
            ]
        }
    };

    const response = await fetch(NOTION_API_BASE_URL + 'databases/' + DATABASE_ID + '/query', {
        method: 'POST',
        headers: {
            'Authorization':'Bearer ' + NOTION_TOKEN,
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(query)
    });
    const data = await response.json();
    return data;
}