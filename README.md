# NotionPaper
NotionPaper is tool that helps you generate static sites from Notion, so that you can use Notion like a CMS.

## Why NotionPaper
My initial thoughts are simple: I want a blogging platform that is simple and good to use enough, so that I could focus on writing instead of setting up a bulky environment. Notion is the perfect tool for that, however you need to pay some money on the subscription in order to let search engines to crawl your site. And I don't wanna spend money on that.

I've used many blogging platforms such as Hexo, Wordpress and etc., you can find my comparison among those platforms and why NotionPaper is a better choice on my blog.

```
Note: 
I am not a professional developer, this project was written as a hobby.
You are more than welcome to make this project better.
```

## How to use
Complete guide on [here](https://docs.notionpaper.cc/c76ecb0140fb4b529bab6b5bdadd60d7/c76ecb0140fb4b529bab6b5bdadd60d7.html) .

Short version:
1. Clone this repo
2. Prepare environment
3. Setup a Notion Intergration (internal or public)
4. Setup the ```config.yml``` file
5. Run ```index.py```
6. Find your site in ```/public``` directory
7. Upload the directory on any hosting services, and you are done.

## Supported Features (.. or soon to be features)
- [ ] Page
    - [x] Page cover
    - [x] Page Icon
    - [ ] Page Tags
- [ ] Supports parsing all types of blocks that Notion has:
    - [x] Table of Contents
    - [x] Rich Texts (all anotations and text colors)
    - [x] Divider
    - [x] Paragraphs
    - [x] Headings
    - [x] Table
    - [x] Images (Uploaded and external)
    - [x] Videos
        - [x] Uploaded Video
        - [x] External Video
        - [x] Youtube Video
    - [x] Code
    - [x] Bulleted and numbered lists
    - [ ] Callout
    - [x] Quote
    - [ ] Child pages
    - [ ] Embed
    - [ ] Mention
        - [x] Page
        - [ ] Person
    - [ ] File
    - [ ] PDF
    - [ ] Bookmark
    - [ ] Equation
    - [ ] Breadcrumb
    - [ ] Columns
    - [ ] Nested blocks
- [x] Custom styles
- [ ] Custom pages
- [ ] Search

## Update Notes

**2022.06.23**
- ADD: table of contents support

**2022.06.21**
- ADD: video support
- ADD: divider support
- FIX: external image parsing issue
- OPTIMIZATION: theme limited extra long image or video height

**2022.06.20**
- ADD: page mention (inline page mention) support, which users could mention another post in a post
- ADD: post date and time display support
- OPTIMIZATION: theme display optimization for article page

**2022.06.17**
- ADD: quote block support

**2022.06.14**
- REMOVE: external objects will not be downloaded due to privacy reasons
- OPTIMIZATION: multi threads support to make generating process faster
- OPTIMIZATION: extracted core functions into np_core to make code cleaner
- ADD: Publish property support that allows user decide which articles to generate

**2022.05.02**
- ADD: table support

**2022.03.26**
- Technically first usable version release