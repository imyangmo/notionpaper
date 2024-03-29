<h1 align="center">NotionPaper (Beta)</h1>
<p align="center">
  <i>NotionPaper is tool that helps you use Notion like a CMS.</i>
   <br/>
  <img width="120" src="./logo.png" />
  <br/>
  <b><a href="https://dreambulare.com/">Blog Usage Showcase</a></b> | <b><a href="https://np.dreambulare.com/9696241a-abad-4807-a8ee-b5452ab68cb9">Getting Started</a></b> | <b><a href="https://np.dreambulare.com/">Documentation</a></b> | <b><a href="https://github.com/imyangmo/notionpaper">GitHub</a></b>
  <br/><br/>
</p>

## Why NotionPaper
My initial thoughts are simple: I want a blogging platform that is simple and good to use enough, so that I could focus on writing instead of setting up a bulky environment. 

Notion is the perfect tool for that, however you need to pay some money on the subscription in order to let search engines to crawl your site. And I don't wanna spend money on that.

I've used many blogging platforms such as Hexo, Wordpress and etc., you can find my comparison among those platforms and why NotionPaper is a better choice on my blog.

Please take note: 
I am not a professional developer, this project was written as a hobby.
You are more than welcome to make this project better.


## How to use
### Deploy on Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fimyangmo%2Fnotionpaper&env=DATABASE_ID,NOTION_TOKEN,THEME)

Click button above to deploy on Vercel.

For environment variable settings, please check tutorials on [here](https://np.dreambulare.com/).

## Supported Features / Roadmap
<table>
    <tr>
        <th>Category</th>
        <th>Features</th>
        <th>Support Status</th>
        <th>Remarks</th>
    </tr>

<tr>
    <td rowspan="3">Site</td>
    <td>Site name</td>
    <td>✅</td>
    <td>Uses database title as site name</td>
</tr>
    <tr>
        <td>Site description</td>
        <td>✅</td>
        <td>Uses database description as site description</td>
    </tr>
    <tr>
        <td>Site favicon</td>
        <td>✅</td>
        <td>Uses database icon as site icon</td>
    </tr>

<tr>
    <td rowspan="3">Page</td>
    <td>Page cover</td>
    <td>✅</td>
    <td>Uses page cover. ** Please noted **, external images will not be hosted for security reasons</td>
</tr>
    <tr>
        <td>Page favicon</td>
        <td>✅</td>
        <td></td>
    </tr>
    <tr>
        <td>Page Tags</td>
        <td>✅</td>
        <td>Supported tag display on page, but need to improve.</td>
    </tr>

<tr>
    <td rowspan="22">Blocks</td>
    <td>Table of Contents</td>
    <td>✅</td>
    <td></td>
</tr>
    <tr>
        <td>Rich Texts</td>
        <td>✅</td>
        <td>Supports all anotations and text colors</td>
    </tr>
    <tr>
        <td>Divider</td>
        <td>✅</td>
        <td></td>
    </tr>
    <tr>
        <td>Paragraphs</td>
        <td>✅</td>
        <td></td>
    </tr>
    <tr>
        <td>Headings</td>
        <td>✅</td>
        <td></td>
    </tr>
    <tr>
        <td>Table</td>
        <td>✅</td>
        <td></td>
    </tr>
    <tr>
        <td>Images</td>
        <td>✅</td>
        <td>Supports uploads and externals. External images will not be hosted for security reasons</td>
    </tr>   
    <tr>
        <td>Videos</td>
        <td>✅</td>
        <td>Supports uploads, externals, and Youtube videos. External videos will not be hosted for security reasons</td>
    </tr> 
    <tr>
        <td>Code</td>
        <td>✅</td>
        <td></td>
    </tr> 
    <tr>
        <td>Bulleted and numbered lists</td>
        <td>✅</td>
        <td></td>
    </tr> 
    <tr>
        <td>Quote</td>
        <td>✅</td>
        <td></td>
    </tr> 
    <tr>
        <td>Callout</td>
        <td>✅</td>
        <td>Supported, but texts only, needs to improve.</td>
    </tr> 
    <tr>
        <td>Child pages</td>
        <td>📅 Planned</td>
        <td></td>
    </tr> 
    <tr>
        <td>Embed</td>
        <td>📅 Planned</td>
        <td></td>
    </tr> 
    <tr>
        <td>Mention</td>
        <td>📅 Planned</td>
        <td>Including mentioned page and person</td>
    </tr> 
    <tr>
        <td>File</td>
        <td>✅</td>
        <td>Uploaded files only</td>
    </tr> 
    <tr>
        <td>PDF</td>
        <td>📅 Planned</td>
        <td></td>
    </tr> 
    <tr>
        <td>Bookmark</td>
        <td>📅 Planned</td>
        <td></td>
    </tr> 
    <tr>
        <td>Equation</td>
        <td>📅 Planned</td>
        <td></td>
    </tr> 
    <tr>
        <td>Breadcrumb</td>
        <td>📅 Planned</td>
        <td></td>
    </tr> 
    <tr>
        <td>Columns</td>
        <td>📅 Planned</td>
        <td></td>
    </tr> 
    <tr>
        <td>Nested blocks</td>
        <td>✅</td>
        <td>Children blocks</td>
    </tr> 
<tr>
    <td rowspan="4">Expandability</td>
    <td>Custom styles / Themes</td>
    <td>✅</td>
    <td>You could design and apply your own or others' theme</td>
</tr>
    <tr>
        <td>Custom pages</td>
        <td>📅 Planned</td>
        <td></td>
    </tr>
    <tr>
        <td>Search</td>
        <td>📅 Planned</td>
        <td></td>
    </tr>
    <tr>
        <td>i18n</td>
        <td>📅 Planned</td>
        <td></td>
    </tr>
</table>



## Update Notes
**2023.8.13**
 - Notionpaper can change your content dynamically by using SSR now, you don't need to re-deploy to update your site after every change.

Notes histories see [here](./UpdateNotes.md).
