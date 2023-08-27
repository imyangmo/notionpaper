// import { siteInfoFetcher } from '../../components/Fetchers'
// import { iconMaker } from '../../components/Utils';
import { getSiteMeta } from "../../components/APIHandlers"

export async function get({ params }) {
    // const siteMeta = await siteInfoFetcher();

    // // ------
    // const body = {
    //     siteTitle: siteMeta.title[0].plain_text,
    //     siteDesc: siteMeta.description[0].plain_text,
    //     siteIcon: iconMaker(siteMeta)
    // }

    const body = await getSiteMeta()

    return new Response(JSON.stringify(body), {
        status: 200,
        headers: {
            "Content-Type": "application/json"
        }
    })
}