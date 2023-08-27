import { getPost, getPostList } from "../../../components/APIHandlers";

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

export async function getStaticPaths() {
    const postListData = await getPostList();
    //todo
    return postListData.map((each) => {
        return {
            params: { pid: each.id },
        };
    });
}

export async function get({ params }) {
    const pid = params.pid;

    const body = await getPost(pid)

    return new Response(JSON.stringify(body), {
        status: 200,
        headers: {
            "Content-Type": "application/json"
        }
    })
}