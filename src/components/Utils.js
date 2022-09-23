export const dateFormatter = (input) => {
    let result = {
        date: '',
        time: ''
    };
    const timePattern = /(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d/g;
    const datePattern = /([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8])))/g;

    const time = input.match(timePattern);
    const date = input.match(datePattern);

    if(time != null ){
        result.time = time[0]
    };

    if(date != null){
        result.date = date[0]
    };

    return result;

};

export function youtubeParser(url){
    // modified from: https://stackoverflow.com/questions/3452546/how-do-i-get-the-youtube-video-id-from-a-url
    const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    const match = url.match(regExp);
    return (match&&match[7].length==11)? match[7] : null;
}