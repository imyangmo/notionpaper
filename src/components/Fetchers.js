// import { DATABASE_ID, NOTION_TOKEN, NOTION_VERSION, NOTION_API_BASE_URL } from "../config"

const DATABASE_ID = import.meta.env.DATABASE_ID
const NOTION_TOKEN = import.meta.env.NOTION_TOKEN
const NOTION_VERSION = import.meta.env.NOTION_VERSION
const NOTION_API_BASE_URL = import.meta.env.NOTION_API_BASE_URL

export async function pageBlockFetcher(id, next_cursor = null) {
    let param = ""
    if (next_cursor != null) {
        param = "start_cursor=" + next_cursor
    }

    const fetchURL = NOTION_API_BASE_URL + 'blocks/' + id + '/children?' + param;
    const fetchOptions = {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + NOTION_TOKEN,
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        }
    }
    const pageContentResp = await fetch(fetchURL, fetchOptions);
    const pageContentData = await pageContentResp.json();
    return pageContentData;
}

export async function pageInfoFetcher(id) {
    const pageInfoResp = await fetch(NOTION_API_BASE_URL + 'pages/' + id, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + NOTION_TOKEN,
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        }
    });
    const pageInfoData = await pageInfoResp.json();
    return pageInfoData;
}

export async function indexFetcher() {
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
            'Authorization': 'Bearer ' + NOTION_TOKEN,
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(query)
    });
    const data = await response.json();
    return data;
}

export async function siteInfoFetcher() {
    const response = await fetch(NOTION_API_BASE_URL + 'databases/' + DATABASE_ID, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + NOTION_TOKEN,
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        }
    });
    const data = await response.json();
    return data;
}