import { v4 as uuidv4 } from "uuid";
import Downloader from "nodejs-file-downloader";
const rt = import.meta.env.RUNTIME.split("-")[0];
const mode = import.meta.env.RUNTIME.split("-")[1];
let buildDir
if (rt === 'vercel') {
    buildDir = './.vercel/output/static/post/assets'
} else {
    buildDir = './dist/post/assets'
}
import {
    pageBlockFetcher,
    pageInfoFetcher,
    indexFetcher,
    siteInfoFetcher
} from './Fetchers'
import { indexParser, pageParser } from "./Parsers.js";
import { dateFormatter, iconMaker } from "./Utils.js";


function listMerger(pageContents) {
    console.log("Merging list items...");
    let tmp = [];

    let index = 0;
    while (index < pageContents.length) {
        if (
            pageContents[index].type != "numbered_list_item" &&
            pageContents[index].type != "bulleted_list_item"
        ) {
            // current item is not a list block, copy and skip
            tmp.push(pageContents[index]);
            index += 1;
        } else {
            // current item is a list block
            try {
                tmp.at(-1).type;
            } catch (error) {
                // if there is no item in the new list, means it is the first item from the old list, append it anyways
                tmp.push({
                    type: pageContents[index].type + "_group",
                    origin_type: pageContents[index].type,
                    items: [pageContents[index]],
                    children: false,
                    // list gourp should not have children, only list item has children
                });
                index += 1;
                continue;
            }
            // if the new list not empty
            if (tmp.at(-1).type == pageContents[index].type + "_group") {
                // if the last item from the new list is as same as the current item from the old list
                tmp.at(-1).items.push(pageContents[index]);
                index += 1;
            } else {
                // means current item is a new list type
                tmp.push({
                    type: pageContents[index].type + "_group",
                    origin_type: pageContents[index].type,
                    items: [pageContents[index]],
                    children: false,
                });
                index += 1;
            }
        }
    }
    return tmp;
}

function listMergerHandler(pageContents) {
    const mergedContent = listMerger(pageContents);
    mergedContent.forEach((block) => {
        if (
            block.type == "numbered_list_item_group" ||
            block.type == "bulleted_list_item_group"
        ) {
            block.items.forEach((item) => {
                if (item.children != false) {
                    const result = listMergerHandler(item.children);
                    item.children = result;
                }
            });
        }
    });
    return mergedContent;
}

function tocGenerator(pageContents) {
    console.log("Generating table of contents...");
    const headingTypes = ["heading_1", "heading_2", "heading_3"];
    const headingLevel = {
        heading_1: 1,
        heading_2: 2,
        heading_3: 3,
    };

    let listItems = [];
    pageContents.forEach((item) => {
        if (headingTypes.includes(item.type)) {
            const text = item.text.map((span) => span.content);
            listItems.push({
                level: headingLevel[item.type],
                id: item.id,
                text: text.join(""),
            });
        }
    });
    return listItems;
}

export async function getPost(pid) {

    const pageMetaData = await pageInfoFetcher(pid);
    // ------
    let pageCover = "";
    if (pageMetaData.cover) {
        if (pageMetaData.cover.type === 'external') {
            pageCover = pageMetaData.cover.external.url;
        } else if (pageMetaData.cover.type === 'file') {
            if (mode === 'ssg') {
                const rdmName = uuidv4();
                const downloader = new Downloader({
                    url: pageMetaData.cover.file.url,
                    directory: buildDir,
                    fileName: rdmName
                });
                await downloader.download();
                pageCover = "/post/assets/" + rdmName
            } else if (mode === 'ssr') {
                pageCover = pageMetaData.cover.file.url;
            }

        }
    }
    // ------
    let createdDate = "Unspecified";
    let createdTime = "Unspecified";
    if (pageMetaData.properties["Original Create Time"].date == null) {
        ({ date: createdDate, time: createdTime } = dateFormatter(
            pageMetaData.created_time
        ));
    } else {
        ({ date: createdDate, time: createdTime } = dateFormatter(
            pageMetaData.properties["Original Create Time"].date.start
        ));
    }
    // ------
    let pageTags;
    if (pageMetaData.properties.Tags === undefined) {
        console.log(
            "Your database does not have a 'Tags' property, skip tag generation."
        );
    } else {
        pageTags = pageMetaData.properties.Tags.multi_select;
    }
    // ------
    let next_cursor = null;
    let fullPageContents = [];
    while (true) {
        const pageContentData = await pageBlockFetcher(pid, next_cursor);
        const pageParsedData = await pageParser(pageContentData);
        fullPageContents.push(...pageParsedData);
        if (pageContentData.has_more) {
            console.log("This page has more content, fetching...");
            next_cursor = pageContentData.next_cursor;
        } else {
            break;
        }
    }
    fullPageContents = listMergerHandler(fullPageContents);
    // ------
    fullPageContents.forEach((item) => {
        if (item.type == "table_of_contents") {
            item.listItems = tocGenerator(fullPageContents);
        }
    });

    // ------
    const body = {
        pageCover: pageCover,
        pageIcon: iconMaker(pageMetaData),
        pageTitle: pageMetaData.properties.Name.title[0].plain_text,
        createdDate: createdDate,
        createdTime: createdTime,
        pageTags: pageTags,
        pageContent: fullPageContents
    }

    return body
}

export async function getPostList() {
    const postListResp = await indexFetcher();
    const body = indexParser(postListResp.results);
    return body
}

export async function getSiteMeta() {
    const siteMeta = await siteInfoFetcher();

    // ------
    const body = {
        siteTitle: siteMeta.title[0].plain_text,
        siteDesc: siteMeta.description[0].plain_text,
        siteIcon: iconMaker(siteMeta)
    }

    return body
}

export async function getTopics() {
    const postListResp = await indexFetcher();
    const postListData = indexParser(postListResp.results);

    let topics = [];
    let topicIndex = [];
    postListData.forEach((each) => {
        const thisPost = {
            id: each.id,
            title: each.title,
            date: each.date,
            time: each.time,
        };

        if (each.topicID == "") {
            console.log("Empty topic, skipped");
        } else {
            if (topicIndex.includes(each.topicID)) {
                topics.forEach((eachTopic) => {
                    if (eachTopic.topicID == each.topicID) {
                        eachTopic.post.push(thisPost);
                    }
                });
            } else {
                topics.push({
                    topicID: each.topicID,
                    topicName: each.topicName,
                    post: [thisPost],
                });
                topicIndex.push(each.topicID);
            }
        }
    });

    const body = topics;
    return body
}