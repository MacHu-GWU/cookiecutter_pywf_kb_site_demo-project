---
name: blog-intake
description: "Collect source material for a knowledge base document: fetch web articles, PDFs, YouTube or other video subtitles, or files and text the author drops in, and save each as a Markdown file with metadata under the document's resources/ (excluded from the site build). Use when the author gives a URL or file and says 收进来, intake, 存一下这个素材, 把这个视频/文章下载下来, for a knowledge base document."
---

> Usage: `/blog-intake <doc_id 或文档目录 或主题> <URL 或文件路径...>`

# blog-intake

把作者给的链接或文件收进一篇文档的 `resources/`, 每份素材一个带元信息的 Markdown 文件.

先读 [../blog-base/SKILL.md](../blog-base/SKILL.md), 再读:

- [../blog-base/ref/03-workflow/01-lifecycle.md](../blog-base/ref/03-workflow/01-lifecycle.md)
- [../blog-base/ref/02-spec/01-repository-layout.md](../blog-base/ref/02-spec/01-repository-layout.md)
- [../blog-base/ref/02-spec/05-resources.md](../blog-base/ref/02-spec/05-resources.md)

按这些文档做. 下面只记本 skill 自己的做法.

## 1. 找到这篇文档

输入: `$ARGUMENTS`.

- 给了 doc_id 或文档目录: 用 `get` 确认它存在.
- 只给了主题, 或者什么都没给: 跑 `list-recent` 和 `search`, 问作者是哪一篇. 是新的一篇, 问作者放在哪个分类下 (用 `list-categories` 列出来), 按 `01-repository-layout.md` 起一个英文 slug, 连同暂定标题和临时 `description` 给作者确认, 再跑 `new-post`.

```bash
python3 .agents/skills/blog-base/scripts/blog_utils.py get --doc_id <doc_id>
python3 .agents/skills/blog-base/scripts/blog_utils.py list-categories
python3 .agents/skills/blog-base/scripts/blog_utils.py new-post --parent <分类路径> --slug <english-slug> --title "<暂定标题>" --description "<临时的两句话>"
```

## 2. 抓内容

下载的中间文件 (字幕, 网页原文) 放在临时目录 (有 scratchpad 就放 scratchpad), 不要放进仓库. 每份素材按来源选办法:

**网页, 在线 PDF.** 用 markitdown 转成 Markdown, 再删掉导航, 广告, 评论区:

```bash
uvx --from "markitdown[all]" markitdown "<URL>"
```

失败了 (404, 反爬, 要登录) 就改用 agent 自带的网页抓取工具, 要求它返回原文全文而不是摘要. 都拿不到全文, 就请作者把正文复制过来.

**YouTube 和其他视频网站.** 用 yt-dlp 只下载字幕, 不下视频, 一次只要一种语言 (同时要多种容易被限流 429). 英文视频用 `en`, 中文视频用 `zh-Hans` 或 `zh`:

```bash
uvx yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs en --sub-format vtt \
  --print "%(title)s | %(uploader)s | %(upload_date)s" --no-simulate \
  -o "<临时目录>/%(id)s.%(ext)s" "<URL>"
python3 .agents/skills/blog-intake/scripts/vtt_to_text.py --path "<临时目录>/<id>.en.vtt"
```

`--print` 那一行给出标题, 作者, 发布日期 (`YYYYMMDD`, 改写成 `YYYY-MM-DD`). 没有字幕就只记元信息, 正文第一行写 `> 只抓到了元信息, 没有字幕.`, 请作者补充要点.

**作者直接丢过来的文件.** 原文件复制进 `resources/`, 按 `05-resources.md` 改成英文文件名, 旁边配一个同名的 `.md`. PDF 或 Word 用 `uvx --from "markitdown[all]" markitdown "<文件>"` 转出正文.

**作者贴过来的文字.** 原样写进 `.md` 正文. 是 Confluence 页面而且作者想把它改成一篇文章, 告诉作者用 `blog-write-migrate-from-confluence` 一次做完; 作者只想先收着, 就按 `source_type: "confluence"` 收.

## 3. 落盘

按 `../blog-base/assets/resource-template.md` 写 `resources/<文件名>.md`:

- `intake_at` 填今天, `published_at` 填原文日期, 查不到就 `""`.
- `note` 用作者给链接时说的话概括成一句. 作者什么都没说就留 `""`, 不要替作者编理由.
- 正文原样保留, 不翻译, 不总结, 不跑 `c2ep`.

全部写完跑 `check`, 把 `resources/` 相关的 WARN 修掉:

```bash
python3 .agents/skills/blog-base/scripts/blog_utils.py check --path <文档目录>
```

## 4. 告诉作者

列出这次收进来的每个文件: 文件名, 标题, 大概多长, 有没有缺内容. 不要复述原文内容. 最后提一句: 想开始理思路就用 `blog-plan`.

## 边界

- 只写 `resources/`. 新建文档时才会碰 `README.md` 和 `plan.md` (由 `new-post` 生成).
- 不下载视频和音频本身.
