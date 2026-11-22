---
name: blog-base
description: "Shared knowledge, specs, templates, and scripts for the blog-* writing skills of this repository's knowledge base (blog-intake, blog-plan, blog-write, blog-add-images, blog-write-migrate-from-confluence): what the knowledge base is for and how it differs from a blog, the document spec (folder tree under docs/source with category READMEs, plan.md and resources/ excluded from the build, front matter doc_id / description / tags / created_at / updated_at, the site's language (ASCII punctuation in Chinese), tone, MyST body rules, the build-time AI Reader link, optional images, checklist), the document lifecycle and writing process, and blog_utils.py for creating, finding, searching and checking documents. Load it to answer questions about writing in the knowledge base or before any blog-* invoker."
---

# blog-base

知识库写作 skill family 的 base. 这里放所有 `blog-*` skill 共用的东西: 知识库为什么存在, 写给谁, 每篇文档的目录和文件长什么样, 一篇文档从种子到写完怎么走. 本 skill 不负责任何具体动作, 动作由文末的 invoker 来做.

站点本身 (Sphinx 配置, MyST 语法, 构建, 搜索, 部署, `doc_id` 的机制) 归 `sphinx-myst-kb-site` skill 管. 本 family 只管 "怎么写一篇好文档", 用到站点规则时指过去, 不复述.

`ref/` 下每个目录里的文件按依赖顺序编号: 编号小的不依赖编号大的, 从上往下读就行.

## 文件索引

`ref/01-strategy/`: 为什么这么做.

| 文件 | 管什么 |
| :--- | :--- |
| [01-positioning.md](ref/01-strategy/01-positioning.md) | kb 是什么, 三类读者 (未来的自己, agent, 收到链接的人), 好文档和坏文档 (AI 摘要式笔记), 和一般博客的区别 |

`ref/02-spec/`: 怎么写. 每篇文档都要遵守的规范.

| 文件 | 管什么 |
| :--- | :--- |
| [01-repository-layout.md](ref/02-spec/01-repository-layout.md) | `docs/source` 文档树, 分类也是文档, 一篇文档的目录, `plan.md` / `resources/` 不进网站, 英文 slug 默认不加序号, 写到一半也要能构建 |
| [02-metadata.md](ref/02-spec/02-metadata.md) | front matter 五个字段: `doc_id`, `description` (喂给 `llms.txt` 的两句话), `tags`, `created_at`, `updated_at` |
| [03-language-punctuation.md](ref/02-spec/03-language-punctuation.md) | 中文为主术语留英文, 全部英文半角标点, `c2ep` 和它对 MyST 的误伤 |
| [04-tone.md](ref/02-spec/04-tone.md) | 基本口气, kb 多加的 (有头有尾, 讲判断) 和放宽的 (可以更技术); 作者个人文风另行指定 |
| [05-resources.md](ref/02-spec/05-resources.md) | `resources/` 放什么 (含 Confluence 原稿), 文件名, 素材 frontmatter, 正文原样保留 |
| [06-plan.md](ref/02-spec/06-plan.md) | `plan.md` 的固定几节 (比 blog 多一节 `背景`), 素材的四种用法: 改写, 引用, 提到, 背景 |
| [07-readme-body.md](ref/02-spec/07-readme-body.md) | H1 和开头段, AI 伴读链接由构建自动加, 用 doc_id 链接, 标题层级, 能用的 MyST 写法, 代码块规则, 正文不放的东西 |
| [08-images.md](ref/02-spec/08-images.md) | 默认不配图; 封面和章节图的命名和位置, `editorial-ink-art` 画风, 只有 Antigravity 能生图, `imgsqueeze` 压缩 |
| [09-checklist.md](ref/02-spec/09-checklist.md) | 收工检查清单 |

`ref/03-workflow/`: 一篇文档怎么写出来.

| 文件 | 管什么 |
| :--- | :--- |
| [01-lifecycle.md](ref/03-workflow/01-lifecycle.md) | 每个 invoker 负责哪一段, 读什么写什么, 交接规则 (没有 ship, 部署和 commit 归作者) |
| [02-writing-process.md](ref/03-workflow/02-writing-process.md) | 写正文的过程: 先问背景, 先给提纲, 怎么写开头, 操作节和结尾, 改稿时 AI 摘要式笔记的常见毛病和改法 |

`assets/`: 模板, 由 `blog_utils.py` 或 invoker 复制使用. 字段和章节以对应的 spec 为准.

| 文件 | 管什么 |
| :--- | :--- |
| [readme-template.md](assets/readme-template.md) | 文档 `README.md` 骨架, 见 `02-metadata.md` |
| [category-readme-template.md](assets/category-readme-template.md) | 分类 `README.md` 骨架, 带 `kb-toctree` |
| [plan-template.md](assets/plan-template.md) | `plan.md` 骨架, 见 `06-plan.md` |
| [resource-template.md](assets/resource-template.md) | 一份素材的骨架, 见 `05-resources.md` |

`scripts/`:

| 文件 | 管什么 |
| :--- | :--- |
| [blog_utils.py](scripts/blog_utils.py) | 只依赖标准库的 CLI. 文档发现和站点 lint 复用 `sphinx-myst-kb-site/scripts/kb_docs.py`, 所以和 `mise run lint-doc` 规则一致 |

从项目根目录跑:

```bash
python3 .agents/skills/blog-base/scripts/blog_utils.py list-categories
python3 .agents/skills/blog-base/scripts/blog_utils.py new-category --parent "<上级分类或空>" --slug <english-slug> --title "<分类名>" --description "<两句话>"
python3 .agents/skills/blog-base/scripts/blog_utils.py new-post --parent <分类路径> --slug <english-slug> --title "<暂定标题>" --description "<临时的两句话>"
python3 .agents/skills/blog-base/scripts/blog_utils.py get --doc_id <doc_id>
python3 .agents/skills/blog-base/scripts/blog_utils.py get --path docs/source/<分类>/<文档>
python3 .agents/skills/blog-base/scripts/blog_utils.py list-recent --k 10
python3 .agents/skills/blog-base/scripts/blog_utils.py search --query "<关键词>" --k 20
python3 .agents/skills/blog-base/scripts/blog_utils.py check [--doc_id <doc_id> | --path <文档目录>]
```

- `--parent` 和 `--path` 相对 `docs/source` (`--path` 也接受相对仓库根的路径).
- `new-post`: 建 `docs/source/<parent>/<slug>/`, 生成不重复的 `doc_id`, 从模板写 `README.md` (front matter + H1) 和 `plan.md`. `--description` 必填, 不合 lint 规则就什么都不建. `--date` 可以指定 `created_at`.
- `new-category`: 建分类目录和带 `kb-toctree` 的 `README.md`, 没有 `plan.md`.
- `list-categories`: 列出所有用 `kb-toctree` 列子文档的文档, 就是可以当 `--parent` 的地方.
- `get`: 打印 metadata, 有没有 `plan.md`, `resources/` 里有哪些素材, 子文档.
- `search`: 在标题, `description`, `tags` 里找. 英文按整词, 中文按子串. 找 doc_id 来写 `{ref}` 就用它.
- `check`: 先跑站点 lint (和 `lint-doc` 同一套), 再加本 family 的规则: ERROR 有源文件里手写的 AI 伴读链接, 引用了不存在的图, `resources/` 里有 `README.*`; WARN 有缺日期, front matter 多出的字段和字段顺序, 全角标点 (`description` 里, 以及正文代码以外, MyST 指令里的正文也查), H5 以下的标题, ✅ ❌ ⚠️, 没有 `plan.md`, 素材 frontmatter 不全, 素材超过 10 MB, 没被引用的图. 有 ERROR 退出码 1. 不带参数时查全部文档; 早期演示文档的 WARN 是已知的, 不用管.

## Invoker

谁先谁后, 怎么交接, 见 [01-lifecycle.md](ref/03-workflow/01-lifecycle.md).

| Skill | 动作 | 读哪些 base 文件 |
| :--- | :--- | :--- |
| `blog-intake` | 把链接, 视频, 文件收进 `resources/` | `03-workflow/01`, `02-spec/01`, `05` |
| `blog-plan` | 陪作者理思路, 问背景, 边聊边写 `plan.md` | `03-workflow/01`, `02`, `01-strategy/01`, `02-spec/01`, `03`, `05`, `06` |
| `blog-write` | 主力写作: 按 plan 和素材写 `README.md` 正文; 或把已有粗稿改成规范稿 | `03-workflow/01`, `02`, `01-strategy/01`, `02-spec/01` 到 `07`, `09` |
| `blog-add-images` | 作者要求时配图: 封面和章节图, 嵌入正文, 压缩. 生图只在 Antigravity | `02-spec/01`, `07`, `08`, 外加 `editorial-ink-art`, `pypi-imgsqueeze` |
| `blog-write-migrate-from-confluence` | 把 Confluence 页面 (`.md`) 迁成一篇有头有尾的文章: 存原稿, 问背景, 写 plan, 改写 | `03-workflow/01`, `02`, `01-strategy/01`, `02-spec/01` 到 `07`, `09` |

所有 invoker 都用 `scripts/blog_utils.py`.

## 本 family 用到但不拥有的东西

| 东西 | 在哪 | 谁用 |
| :--- | :--- | :--- |
| `sphinx-myst-kb-site` skill | 站点规则, MyST 写法示例, `kb_docs.py`, `lint_docs.py` | 全部 (`blog_utils.py` 直接 import `kb_docs.py`) |
| `editorial-ink-art` skill | 配图画风和 prompt 模板, 跨仓库共用 | `blog-add-images` |
| `pypi-imgsqueeze` skill | 图片原地压缩和 `.json` sidecar | `blog-add-images` |
| `esc_mini_tools_chatbot_deeplink` 库 | AI 伴读链接的编码规则. kb 不依赖它, 由 `cookiecutter_pywf_kb_site_demo/ai_reader.py` 按同样的编码在构建时生成 | 无 invoker 直接用 |
| `cookiecutter_pywf_kb_site_demo/ai_reader.py` + `cookiecutter_pywf_kb_site_demo/sphinx_ext.py` | 构建时在每页 H1 下插入 AI 伴读链接 | 构建 |
| `docs/source/conf.py` 的 `exclude_patterns` | 把 `**/plan.md` 和 `**/resources` 挡在构建之外 | 构建 |

`editorial-ink-art` 和 `pypi-imgsqueeze` 是跨仓库共用的 skill, 不在这里改; 要改就在源头改完再复制过来.
