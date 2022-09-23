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
tbd

## Supported Features (.. or soon to be features)
- [ ] Page
    - [ ] Page cover
    - [ ] Page Icon
    - [ ] Page Tags
- [ ] Supports parsing all types of blocks that Notion has:
    - [ ] Table of Contents
    - [x] Rich Texts (all anotations and text colors)
    - [ ] Divider
    - [x] Paragraphs
    - [x] Headings
    - [ ] Table
    - [ ] Images (Uploaded and external)
    - [ ] Videos
        - [ ] Uploaded Video
        - [ ] External Video
        - [ ] Youtube Video
    - [ ] Code
    - [ ] Bulleted and numbered lists
    - [ ] Callout
    - [ ] Quote
    - [ ] Child pages
    - [ ] Embed
    - [ ] Mention
        - [ ] Page
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
**2022.09.23**
> IMPORTANT: major change
> From this release, the code of the this project has been refactored from Python into using [Astro](https://astro.build/) for multiple reasons, I may want to make a post regarding this refactoring soon.
> All features are gradually done.
> Archived code can be found on 'python_ver' branch.

---

**2022.07.07**
- **Core:**
    - ADD: Nested bulleted list and content support. Finally.
- **Theme:Simple**
    - OPTIMIZATION: some style optimization

This release is considered as mostly functional one, new features will be added gradually but main focus will be improvements.

---

**2022.06.23**
- ADD: table of contents support

---

**2022.06.21**
- ADD: video support
- ADD: divider support
- FIX: external image parsing issue
- OPTIMIZATION: theme limited extra long image or video height

---

**2022.06.20**
- ADD: page mention (inline page mention) support, which users could mention another post in a post
- ADD: post date and time display support
- OPTIMIZATION: theme display optimization for article page

---

**2022.06.17**
- ADD: quote block support

---

**2022.06.14**
- REMOVE: external objects will not be downloaded due to privacy reasons
- OPTIMIZATION: multi threads support to make generating process faster
- OPTIMIZATION: extracted core functions into np_core to make code cleaner
- ADD: Publish property support that allows user decide which articles to generate

---

**2022.05.02**
- ADD: table support

---

**2022.03.26**
- Technically first usable version release