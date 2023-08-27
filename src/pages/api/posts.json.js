// import { indexFetcher } from '../../components/Fetchers'
// import { indexParser } from '../../components/Parsers';
import { getPostList } from "../../components/APIHandlers"

export async function get({ params }) {
    // const postListResp = await indexFetcher();
    // const body = indexParser(postListResp.results);

    const body = await getPostList()

    return new Response(JSON.stringify(body), {
        status: 200,
        headers: {
            "Content-Type": "application/json"
        }
    })
}