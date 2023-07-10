import { dateFormatter, youtubeParser, fileExtNameParser } from "./Utils.js"
import { pageBlockFetcher } from "./Fetchers.js";
import { v4 as uuidv4 } from 'uuid';

import Downloader from "nodejs-file-downloader";

export const indexParser = (data) => {
    let content = [];

    data.forEach((each) => {
        let item = {
            date: '',
            time: '',
            title: '',
            id: '',
            topicID: '',
            topicName: ''
        };

        if ('Original Create Time' in each.properties && each.properties['Original Create Time'].date != null) {
            item.date = dateFormatter(each.properties['Original Create Time'].date.start).date;
            item.time = dateFormatter(each.properties['Original Create Time'].date.start).time;
        } else {
            // Where there is no original create time found
            if ('Create Time' in each.properties) {
                item.date = dateFormatter(each.properties['Create Time'].created_time).date;
                item.time = dateFormatter(each.properties['Create Time'].created_time).time;
            } else {
                throw new Error('There is no Original Create Time nor Create Time property found.');
            };
        };

        item.title = each.properties.Name.title[0].text.content;
        item.id = each.id;

        // console.log(each.properties)
        if ("Topic" in each.properties) {
            // console.log("is has topic")
            if ("select" in each.properties.Topic) {
                // console.log("is has topic.select");
                if (each.properties.Topic.select != null) {
                    item.topicID = each.properties.Topic.select.id;
                    item.topicName = each.properties.Topic.select.name;
                } else {
                    console.log("No Topic specified.")
                }
            } else {
                console.log("The 'Topic' property is not a 'select' type");
            }
        } else {
            console.log("The 'Topic' is not defined");
        };

        content.push(item);
    });

    content.sort((a, b) => {
        const date1 = Date.parse(a.date + ' ' + a.time);
        const date2 = Date.parse(b.date + ' ' + b.time);
        if (date1 - date2 > 0) {
            return -1;
        } else if (date1 - date2 < 0) {
            return 1;
        } else {
            return 0;
        }
    })

    return content;
};

const richTextParser = (data) => {
    // Init block text dict
    let text = {
        type: '',
        content: '',
        color: '',
        annotations: '',
        link: '',
        page_id: ''
    }

    switch (data.type) {
        case 'text':
            /*
            Notion could display texts with strikethrough and underline simultaneously,
            but simply put two text decoration styles together
            will be override by another, so this needs to be handle seperately.
            */
            let anno = '';
            if (data.annotations.strikethrough && data.annotations.underline) {
                anno = anno + ' standul';
            } else {
                // Append rest of annotaitons
                for (let [key, value] of Object.entries(data.annotations)) {
                    if (key != 'color' && value) {
                        // Skip color annotation and others that does not applied
                        anno = anno + ' ' + key
                    }
                }
            };

            text.content = data.plain_text;
            text.color = data.annotations.color;
            text.annotations = anno;

            if (data.href != null) {
                text.link = data.href;
            } else {
                text.link = null;
            };
            break;
        case 'mention':
            if (data.mention.type == 'page') {
                text.type = 'mention_page';
                text.content = data.plain_text;
                text.page_id = data.mention.page.id.replace('-', '')
            }
            break;
    };

    return text;

};

async function blockParser(data) {
    let block = {
        type: data.type,
        // id is for html link anchor purpose
        id: '',
        text: [],
        code: '',
        rows: [],
        language: '',
        url: '',
        listItems: [],
        children: false
    };

    switch (data.type) {
        // for table of contents block, it does parses it but not generating it here
        // because if a page is larger than 100 blocks, the page content needs to be fetched multiple times
        // if it was generated here, the TOC wouldn't be correct
        case 'paragraph':
            block.text = data[data.type].rich_text.map((item) => richTextParser(item));
            break;
        case 'heading_1':
        case 'heading_2':
        case 'heading_3':
            block.id = data.id;
            block.text = data[data.type].rich_text.map((item) => richTextParser(item));
            break;
        case 'divider':
            break;
        case 'quote':
            block.text = data[data.type].rich_text.map((item) => richTextParser(item));
            break;
        case 'callout':
            block.text = data[data.type].rich_text.map((item) => richTextParser(item));
            break;
        case 'code':
            const codeArr = data[data.type].rich_text.map((item) => item.plain_text);
            block.code = codeArr.join('');
            block.language = data[data.type].language;
            break;
        case 'table':
            const tableContent = await pageBlockFetcher(data.id);

            block.rows = tableContent.results.map((eachRow) => {
                const rowArr = eachRow.table_row.cells.map((eachCell) => {
                    const textArr = eachCell.map((item) => {
                        return richTextParser(item);
                    });
                    return textArr;
                });
                return rowArr;
            });
            break;
        case 'image':
            switch (data[data.type].type) {
                case 'file':
                    const rdmName = uuidv4();
                    const downloader = new Downloader({
                        url: data[data.type].file.url,
                        directory: "./dist/post/assets",
                        fileName: rdmName
                    });
                    await downloader.download();
                    block.url = "/post/assets/" + rdmName
                    break;
                case 'external':
                    block.type = 'image_external';
                    block.url = data[data.type].external.url;
                    break;
            }
            break;
        case 'video':
            switch (data[data.type].type) {
                case 'file':
                    const rdmName = uuidv4();
                    const downloader = new Downloader({
                        url: data[data.type].file.url,
                        directory: "./dist/post/assets",
                        fileName: rdmName
                    });
                    await downloader.download();
                    block.url = "../assets/" + rdmName
                    break;
                case 'external':
                    const explode = data[data.type].external.url.split(".");
                    if (explode.includes('youtube') || explode.includes('youtu')) {
                        block.type = 'video_youtube';
                        block.url = youtubeParser(data[data.type].external.url);
                    } else {
                        block.type = 'video_external';
                        block.url = data[data.type].external.url;
                    };
                    break;
            };
            break;
        case 'numbered_list_item':
        case 'bulleted_list_item':
            block.listItems = data[data.type].rich_text.map((item) => richTextParser(item));
            break;
        case 'file':
            const extName = fileExtNameParser(data[data.type].file.url);
            const rdmName = uuidv4() + extName;
            const downloader = new Downloader({
                url: data[data.type].file.url,
                directory: "./dist/post/assets",
                fileName: rdmName
            });
            await downloader.download();
            block.url = "../assets/" + rdmName;
            break;
    };

    if (data.has_children && data.type != 'table') {
        const childrenContent = await pageBlockFetcher(data.id);
        const childrenParsedList = childrenContent.results.map((item) => blockParser(item));
        block.children = await Promise.all(childrenParsedList);
    }

    // console.log(block);
    return block;
}

export async function pageParser(data) {
    //this shit costs me five straight hours!!! remember it!!! fucking async shit
    const promList = data.results.map((item) => blockParser(item))
    return Promise.all(promList);
}
