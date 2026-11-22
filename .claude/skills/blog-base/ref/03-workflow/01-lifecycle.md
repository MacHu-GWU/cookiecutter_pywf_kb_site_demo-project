# Workflow: 一篇文档的生命周期

> 每个 `blog-*` invoker 负责哪一段, 上游给它什么, 它交给下游什么. 每个文件的格式见 `02-spec/`.

---

## 1. 全景

```text
种子 (做完的一件事, 一个想法, 一份 Confluence 旧稿)
  │
  ├─ blog-intake  收素材 ─→ resources/*.md     ┐ 顺序不固定, 可以来回跑,
  ├─ blog-plan    理想法 ─→ plan.md            ┘ 也可以只做其中一个
  │
  ├─ blog-write       写正文 ─→ README.md (从 plan 写, 或把粗稿改成规范稿)
  ├─ blog-add-images  配图   ─→ cover.jpeg, img/ (只在作者要求时; 生图只在 Antigravity)
  │
  └─ 收工检查 (09-checklist.md) ─→ 作者 commit, push 到 main 自动部署

捷径: 从 Confluence 迁移
  └─ blog-write-migrate-from-confluence ─→ 一次做完 intake (原稿) + plan (问背景) + write (改写)
```

kb 没有 `blog-ship`: 没有草稿区, 没有定稿挪目录, 没有回填地址. 写完, 过了检查清单, 作者 commit 就上线.

---

## 2. 每一段

| 段 | Invoker | 读 | 写 | 什么时候算完 |
| :--- | :--- | :--- | :--- | :--- |
| 建目录 | 第一个碰到这篇的 invoker | 作者说的分类 | 目录, `README.md` 骨架, `plan.md` 模板 | `new-post` 跑成功, `lint-doc` 通过 |
| 收素材 | `blog-intake` | 作者给的链接或文件 | `resources/*.md` | 每份素材 frontmatter 齐全 |
| 理想法 | `blog-plan` | `resources/`, `plan.md` | `plan.md` | `背景`, `核心观点`, `要讲的点` 有内容 |
| 写正文 | `blog-write` | `plan.md`, `resources/`, 已有的正文 | `README.md` 正文, `description`, `tags`, `updated_at` | 作者认可, 检查清单过了 |
| 迁移 | `blog-write-migrate-from-confluence` | Confluence 原稿, 作者的回答 | `resources/confluence-*.md`, `plan.md`, `README.md` | 同 "写正文" |
| 配图 | `blog-add-images` | `README.md` | 图片, sidecar, `README.md` 里的图片行 | 图都嵌好, 压缩过 |

---

## 3. 交接规则

- **建目录只用 `new-post`.** 第一个碰到这篇的 invoker 先跟作者确认分类和目录名, 再跑 `new-post`. 之后的 invoker 都用 `get` 找到它.
- **分类由作者定.** 作者没说放哪, 列出现有分类问作者. 作者要新分类, 用 `new-category` 建, 也要先确认名字和描述.
- **没有素材也能 plan, 没有 plan 也能 intake.**
- **`blog-write` 之前最好有 plan.** `背景` 或 `核心观点` 是空的, `blog-write` 先提醒作者; 作者坚持就直接写, 但开写前要把背景问出来.
- **写正文时冒出新想法**, 记进 `plan.md` 的 `随手记`, 不要只留在对话里.
- **配图是可选的**, 只在作者要求时做. 章节图跟着 H2 走, 正文写完再配.
- **每个 invoker 收工前都跑 `check` 和 `lint-doc`.** kb 没有草稿区, 一篇坏掉的文档会卡住整个站点的构建.
- **部署不是 invoker 的事.** push 到 main 由 GitHub Actions 部署; `mise run deploy-doc` 会改外部服务, 只在作者明确说要时才跑, 一次一问.
- **commit 由作者决定.** invoker 只写文件, 不 commit, 不 push, 除非作者要求.
