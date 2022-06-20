def richTextParser(content):
    # Init block text dict
    textBlock = {}
    
    if content['type'] == 'text':
        textBlock['type'] = 'text'
        # Append text contents
        textBlock['content'] = content['plain_text']
        # Append text color
        textBlock['color'] = content['annotations']['color']
        # Init annotation list
        annotations = ""
        # Notion could display texts with strikethrough and underline simultaneously, but simply put two text decoration styles together will be override by another, so this needs to be handle seperately.
        if content['annotations']['strikethrough'] == True and content['annotations']['underline'] == True:
            annotations = annotations + " standul"
        else:
        # Append rest of annotaitons
            for key, value in content['annotations'].items():
                # if key != 'color' and key != 'strikethrough' and key != 'underline' and value != False:
                if key != 'color' and value != False:
                # Skip color annotation and others that does not applied
                    annotations = annotations + " " + key

        textBlock['annotations'] = annotations

        if content['href'] != None:
            textBlock['link'] = content['href']
        else:
            textBlock['link'] = None
    elif content['type'] == 'mention':
        if content['mention']['type'] == 'page':
            textBlock['type'] = 'mention_page'
            textBlock['content'] = content['plain_text']
            textBlock['page_id'] = content['mention']['page']['id'].replace('-','')
        

    return(textBlock)