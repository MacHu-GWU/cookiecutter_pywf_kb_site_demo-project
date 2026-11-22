# Spec: 目录结构与命名

> 管辖范围: 文档放在哪, 一篇文档的目录里有什么, 目录怎么起名, 哪些文件不进网站. 站点本身 (Sphinx 配置, 构建, 部署) 的规则在 `sphinx-myst-kb-site` skill 里, 本文只记写文档时要知道的部分.

---

## 1. 文档树

```text
docs/source/
├── README.md                    # 首页
├── <分类>/                      # 分类: 本身也是一篇文档, 列出它下面的文档
│   ├── README.md
│   └── <文档>/
│       └── README.md
└── <分类>/
    └── <子分类>/                # 可以继续往下分
        └── <文档>/
```

- **一篇文档 = 一个文件夹 + 里面一个 `README.md`** (或 `README.rst`, `README.ipynb`, 一个文件夹只能有一个).
- **分类也是文档.** 它的 `README.md` 有自己的 `doc_id` 和 `description`, 正文是一两句介绍加一个 ```` ```{kb-toctree} ```` (自动列出子文件夹). 新分类用 `blog_utils.py new-category` 建.
- 作者会告诉你文档放在哪个分类下. 没说就用 `list-categories` 列出现有分类, 问作者; 不要自己决定建新分类.

---

## 2. 一篇文档的目录

```text
<文档>/
├── README.md        # 正文, 网站上看到的就是它
├── plan.md          # 写作计划, 不进网站
├── resources/       # 写作素材 (别人的东西, 含 Confluence 原稿), 不进网站
├── img/             # 正文引用的图片
└── <其他文件>        # 被 literalinclude 引用的代码文件, 可下载的附件
```

| 路径 | 谁写的 | 进网站吗 | 格式 |
| :--- | :--- | :--- | :--- |
| `README.md` | 作者 | 进 | [02-metadata.md](02-metadata.md), [07-readme-body.md](07-readme-body.md) |
| `plan.md` | 作者 | 不进 | [06-plan.md](06-plan.md) |
| `resources/` | 别人 | 不进 | [05-resources.md](05-resources.md) |
| `img/` | 作者 | 进 (被正文引用的) | [08-images.md](08-images.md) |

`plan.md` 和 `resources/` 靠 `docs/source/conf.py` 的 `exclude_patterns` 挡在构建之外: 不生成页面, 不复制到 `_sources/`, 不进 `llms.txt`. 但它们在 git 里 (仓库是 private 的).

**`resources/` 里的文件永远不叫 `README.*`.** 文档发现脚本会把任何 `README.md` 当成一篇文档. 素材的文件名规则见 [05-resources.md](05-resources.md).

新建文档一律用 `blog_utils.py new-post`, 不要手动建: 它会生成 `doc_id`, 填好日期, 从 `assets/` 复制 `README.md` 和 `plan.md` 的骨架. `resources/`, `img/` 用到的时候再建.

---

## 3. 目录命名

- **英文 slug, 全小写, 用 `-` 连接**, 概括这篇讲的事. 正文不是英文时, slug 也必须是英文.
- **默认不加 `01-`, `02-` 序号前缀.** `kb-toctree` 按文件夹名排序, 不加前缀就按字母序. 只有作者要求固定顺序 (比如一组按步骤读的文档) 时, 才在同一个分类里统一加两位序号. 一个分类里要么都加, 要么都不加.
- **目录名不是身份.** 链接都走 `doc_id` (见 [07-readme-body.md](07-readme-body.md) 第 4 节), 改目录名或挪到别的分类不会断链. 所以起名按 "以后在文件树里一眼认出来" 来起, 写偏了可以改.
- slug 不放日期, 日期在 frontmatter 里.

```text
docs/source/<分类>/<主题>-<角度>/        # 比如 <tool>-setup, <tool>-vs-<tool>, <system>-troubleshooting
```

---

## 4. 写到一半也必须能构建

kb 没有草稿区, push 到 main 就部署 (见 [../01-strategy/01-positioning.md](../01-strategy/01-positioning.md) 第 4 节). 所以:

- `new-post` 要求建目录时就给 `--description`, 先写一个临时的两句话描述, 正文写完再改准.
- 每次改完都跑 `blog_utils.py check --path <文档目录>` 和 `mise run lint-doc`, 保证不会卡住站点构建.
- 作者不想让半成品上线, 就先别 commit, 或者在作者自己的分支上写. 这是作者的决定, 不要替作者做.
