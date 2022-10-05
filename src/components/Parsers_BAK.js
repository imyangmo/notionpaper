import { dateFormatter, youtubeParser } from "./Utils.js";
import { pageBlockFetcher } from "./Fetchers.js";

export const indexParser = (data) => {
  let content = [];

  data.forEach((each) => {
    let item = {
      date: "",
      time: "",
      title: "",
      id: "",
    };

    if (
      "Original Create Time" in each.properties &&
      each.properties["Original Create Time"].date != null
    ) {
      item.date = dateFormatter(
        each.properties["Original Create Time"].date.start
      ).date;
      item.time = dateFormatter(
        each.properties["Original Create Time"].date.start
      ).time;
    } else {
      // Where there is no original create time found
      if ("Create Time" in each.properties) {
        item.date = dateFormatter(
          each.properties["Create Time"].created_time
        ).date;
        item.time = dateFormatter(
          each.properties["Create Time"].created_time
        ).time;
      } else {
        throw new Error(
          "There is no Original Create Time nor Create Time property found."
        );
      }
    }

    item.title = each.properties.Name.title[0].text.content;
    item.id = each.id;

    content.push(item);
  });

  return content;
};

const richTextParser = (data) => {
  // Init block text dict
  let text = {
    type: "",
    content: "",
    color: "",
    annotations: "",
    link: "",
    page_id: "",
  };

  switch (data.type) {
    case "text":
      /*
            Notion could display texts with strikethrough and underline simultaneously,
            but simply put two text decoration styles together
            will be override by another, so this needs to be handle seperately.
            */
      let anno = "";
      if (data.annotations.strikethrough && data.annotations.underline) {
        anno = anno + " standul";
      } else {
        // Append rest of annotaitons
        for (let [key, value] of Object.entries(data.annotations)) {
          if (key != "color" && value) {
            // Skip color annotation and others that does not applied
            anno = anno + " " + key;
          }
        }
      }

      text.content = data.plain_text;
      text.color = data.annotations.color;
      text.annotations = anno;

      if (data.href != null) {
        text.link = data.href;
      } else {
        text.link = null;
      }
      break;
    case "mention":
      if (data.mention.type == "page") {
        text.type = "mention_page";
        text.content = data.plain_text;
        text.page_id = data.mention.page.id.replace("-", "");
      }
      break;
  }

  return text;
};

async function blockParser(data) {
  let block = {
    type: data.type,
    // id is for html link anchor purpose
    id: "",
    text: [],
    code: "",
    rows: [],
    language: "",
    url: "",
  };

  // const tableContent = pageBlockFetcher(data.id);
  // tableContent.then(
  //     (res)=>{
  //         res.results.map((eachRow) => {
  //     // console.log("entering eachrow")
  //     // console.log(eachRow)
  //     let rowArr = [];
  //     eachRow.table_row.cells.map((eachCell) => {
  //         let textArr = [];
  //         eachCell.map((item) => {
  //             textArr.push(richTextParser(item))
  //         })
  //         rowArr.push(textArr)
  //     })
  //     block.rows.push(rowArr)
  // });
  //     }
  // )

  // break;

  const tableContent = await pageBlockFetcher(data.id);
  tableContent.results.map((eachRow) => {
    let rowArr = [];
    eachRow.table_row.cells.map((eachCell) => {
      let textArr = [];
      eachCell.map((item) => {
        textArr.push(richTextParser(item));
      });
      rowArr.push(textArr);
    });
    block.rows.push(rowArr);
  });
  // console.log("table block");
  // console.log(block);

  return block;
}

// export async function pageParser(data){
//     // let full = [];
//     console.log("entering pageParser function")
//     console.log(data.results)

//     let full = data.results.map(async (item) => {
//         await blockParser(item);
//     });
//     console.log("full array in parsers.js")
//     console.log(full)
//     return full;
// }

// export async function pageParser(data) {
//   let full = [];
//   console.log("entering pageParser function");
//   // console.log(data.results)

//   async function demo() {
//     data.results.map((item) => {
//       blockParser(item).then((value) => {
//         console.log("pushing");
//         console.log(value);
//         full.push(value);
//       });
//     });
//   }
//   // console.log(demo())
//   demo().then((value) => {
//     console.log("full array in parsers.js");
//     console.log(value);
//     return full;
//   });
// }

export async function pageParser(data){
    // let full = [];
    console.log("entering pageParser function")
    // console.log(data.results)

    // const full = data.results.map(async (item) => {
    //     return await blockParser(item);
    // });

    //this shit costs me four straight hours!!! remember it!!!

    const promList = data.results.map((item) => blockParser(item))
    // console.log("full array in parsers.js")
    // console.log(full)
    return Promise.all(promList);
}
