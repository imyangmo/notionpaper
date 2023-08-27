// import { indexFetcher } from '../../components/Fetchers'
// import { indexParser } from '../../components/Parsers';
import { getTopics } from "../../components/APIHandlers";

export async function get({ params }) {
    // const postListResp = await indexFetcher();
    // const postListData = indexParser(postListResp.results);

    // let topics = [];
    // let topicIndex = [];
    // postListData.forEach((each) => {
    //     const thisPost = {
    //         id: each.id,
    //         title: each.title,
    //         date: each.date,
    //         time: each.time,
    //     };

    //     if (each.topicID == "") {
    //         console.log("Empty topic, skipped");
    //     } else {
    //         if (topicIndex.includes(each.topicID)) {
    //             topics.forEach((eachTopic) => {
    //                 if (eachTopic.topicID == each.topicID) {
    //                     eachTopic.post.push(thisPost);
    //                 }
    //             });
    //         } else {
    //             topics.push({
    //                 topicID: each.topicID,
    //                 topicName: each.topicName,
    //                 post: [thisPost],
    //             });
    //             topicIndex.push(each.topicID);
    //         }
    //     }
    // });

    // const body = topics;
    const body = await getTopics()


    return new Response(JSON.stringify(body), {
        status: 200,
        headers: {
            "Content-Type": "application/json"
        }
    })
}