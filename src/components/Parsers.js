import { dateFormatter, youtubeParser } from "./Utils.js"

export const indexParser = (data) => {
    let content = [];

    data.forEach((each) => {
        let item = {
            date: '',
            time: '',
            title: '',
            id: ''
        };

        if('Original Create Time' in each.properties && each.properties['Original Create Time'].date != null ){
            item.date = dateFormatter(each.properties['Original Create Time'].date.start).date;
            item.time = dateFormatter(each.properties['Original Create Time'].date.start).time;
        }else{
            // Where there is no original create time found
            if('Create Time' in each.properties){
                item.date = dateFormatter(each.properties['Create Time'].created_time).date;
                item.time = dateFormatter(each.properties['Create Time'].created_time).time;
            }else{
                throw new Error('There is no Original Create Time nor Create Time property found.');
            };
        };

        item.title = each.properties.Name.title[0].text.content;
        item.id = each.id;
    
        content.push(item);
    });

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

    switch(data.type){
        case 'text':
            /*
            Notion could display texts with strikethrough and underline simultaneously,
            but simply put two text decoration styles together
            will be override by another, so this needs to be handle seperately.
            */
            let anno = '';
            if(data.annotations.strikethrough && data.annotations.underline){
                anno = anno + ' standul';
            }else{
                // Append rest of annotaitons
                for (let [key, value ] of Object.entries(data.annotations)){
                    if(key != 'color' && value){
                        // Skip color annotation and others that does not applied
                        anno = anno + ' ' + key
                    }
                }
            };

            text.content = data.plain_text;
            text.color = data.annotations.color;
            text.annotations = anno;

            if(data.href != null){
                text.link = data.href;
            }else{
                text.link = null;
            };
            break;
        case 'mention':
            if(data.mention.type == 'page' ){
                text.type = 'mention_page';
                text.content = data.plain_text;
                text.page_id = data.mention.page.id.replace('-', '')
            }
            break;
    };

    return text;

};

const blockParser = (data) => {
    let block = {
        type: data.type,
        // id is for html link anchor purpose
        id: '', 
        content: [],
        url: ''
    };

    switch(data.type){
        case 'paragraph':
            block.text = data[data.type].rich_text.map((item) => richTextParser(item));
            break;
        case 'heading_1': 
        case 'heading_2': 
        case 'heading_3':
            block.id = data.id;
            block.text = data[data.type].rich_text.map((item) => richTextParser(item));
            break;
        case 'image':
            switch(data[data.type].type){
                case 'file':
                    block.url = data[data.type].file.url;
                    break;
                case 'external':
                    block.type = 'image_external';
                    block.url = data[data.type].external.url;
                    break;
            }
            break;
        case 'video':
            switch(data[data.type].type){
                case 'file':
                    block.url = data[data.type].file.url;
                    break;
                case 'external':
                    const explode = data[data.type].external.url.split;
                    if('youtube' in explode || 'youtu' in explode){
                        block.type = 'video_youtube';
                        block.url = youtubeParser(data[data.type].external.url);
                    }else{
                        block.type = 'video_external';
                        block.url = data[data.type].external.url;
                    };
                    break;
            };
    };

    return block;
}

//         case 'video':
//             if content[content['type']]['type'] == 'file':
//                 file_name = str(uuid.uuid1())
//                 np_utils.file_saver(content[content['type']]['file']['url'], './_prebuild/' + page_id + '/' + file_name)
//                 block['url'] = file_name
//             elif content[content['type']]['type'] == 'external':
//                 result = urlparse(content[content['type']]['external']['url'])
//                 domain = result.netloc.split('.')
//                 if 'youtube' in domain or 'youtu' in domain:
//                     block['type'] = 'video_youtube'
//                     try:
//                         vid = parse_qs(result.query, keep_blank_values=True)['v'][0]
//                         block['vid'] = vid
//                     except:
//                         logging.warning('No Youtube video ID found')
//                 else:
//                     block['type'] = "video_external"
//                     block['url'] = content[content['type']]['external']['url']
//         case 'table':
//             table_contents = np_fetcher.page_block_fetcher(GLOBAL_CONFIGS['notion_api_base_url'], content['id'], headers)
//             block['rows'] = [[ [ richtext_parser(item) for item in each_cell ] for each_cell in each_row['table_row']['cells']] for each_row in table_contents['results']]

//             # code above is equivalent to below, but faster:
//             # block['rows'] = []
//             # for each_row in table_contents['results']:
//             #     row_arr = []
//             #     for each_cell in each_row['table_row']['cells']:
//             #         text_arr = []
//             #         for item in each_cell:
//             #             text_arr.append(richtext_parser(item))
//             #         row_arr.append(text_arr)
//             #     block['rows'].append(row_arr)

//         case 'numbered_list_item' | 'bulleted_list_item':
//             block['listItems'] = [  ]
//             text_arr = [ richtext_parser(item) for item in content[content['type']]['rich_text'] ]
//             block['listItems'].append(text_arr)
//         case 'code':
//             block['language'] = "language-" + content[content['type']]['language']
//             block['contents'] = "".join([ item['plain_text'] for item in content[content['type']]['rich_text'] ])
//         case 'table_of_contents':
//             block['contents'] = []
//             for item in results['results']:
//                 levels = {
//                     "heading_1":1,
//                     "heading_2":2,
//                     "heading_3":3
//                 }
//                 if item['type'] in ['heading_1','heading_2','heading_3']:
//                     text = ""
//                     for span in item[item['type']]['rich_text']:
//                         text = text + span['plain_text']
//                     toc_item = {'level': levels[item['type']], 'text': text, 'id': item['id']}
//                     block['contents'].append(toc_item)
//         case 'quote':
//             block['text'] = [ richtext_parser(item) for item in content[content['type']]['rich_text']]

//     return(block)

export const pageParser = (data) => {
    let full = [];
    // console.log(data.results)

    data.results.forEach((item) => {
        full.push(blockParser(item));
    });

    return full;

}