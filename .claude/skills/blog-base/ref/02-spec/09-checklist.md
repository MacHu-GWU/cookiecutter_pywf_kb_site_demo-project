# Spec: 收工检查清单

> 每次写完或改完一篇, 逐项过一遍. 规则和理由都在前面的 spec 里, 后面标了出处. kb 没有定稿, 发布这两步, 过了这份清单就是写完了.

---

## 1. 目录

- [ ] 文档在作者指定的分类下, 目录名是英文 slug. ([01-repository-layout.md](01-repository-layout.md))
- [ ] `resources/` 里没有叫 `README.*` 的文件, 没有超过约 10 MB 的文件.
- [ ] 正文引用的图片都在 `img/` 下, 都压缩过, 没有没被引用的图片. ([08-images.md](08-images.md))

## 2. Metadata

- [ ] 五个字段齐全, 顺序正确. `description`, `created_at`, `updated_at` 是双引号. ([02-metadata.md](02-metadata.md))
- [ ] `description` 不再是建目录时的临时版本: 第一句讲具体讲了什么, 第二句讲是什么样的文档.
- [ ] 改了正文, `updated_at` 是今天.

## 3. 正文

- [ ] 一个 H1, 下面紧接开头段, 交代了问题和背景. 没有 "概述" H2. ([07-readme-body.md](07-readme-body.md))
- [ ] 源文件里没有手写 AI 伴读链接.
- [ ] 链接别的文档都用 doc_id, 中文小节用了 `(<doc_id>-<slug>)=` 标签.
- [ ] 每个代码块标了语言, 代码前后有说明, 没有编不过的代码.
- [ ] 没有满屏加粗, 没有 ✅ ❌ 列表, 没有编出来的耗时和数字, 没有客套结尾. ([04-tone.md](04-tone.md))
- [ ] 有结尾: 结论, 适用边界, 没解决的问题.
- [ ] 中文文档跑过 `c2ep`, 标点全部英文半角, MyST 语法没被改坏; 零感叹号. ([03-language-punctuation.md](03-language-punctuation.md))
- [ ] H1, H2 只读标题能串起全篇.

## 4. 素材

- [ ] `resources/*.md` 的 frontmatter 齐全, `intake_at` 有值. ([05-resources.md](05-resources.md))
- [ ] `plan.md` 里标了 "引用" 的素材, 正文注明了出处; 标了 "改写" 的原稿, 观点和事实没丢. ([06-plan.md](06-plan.md))

## 5. 机器校验

```bash
python3 .claude/skills/blog-base/scripts/blog_utils.py check --path <文档目录>
mise run lint-doc
```

- [ ] 两个都退出码 0. `check` 的 WARN 都看过, 该修的修了.
- [ ] 改动大 (新分类, 用了新的 MyST 写法, 加了图) 时, 跑 `mise run build-doc` 确认 Sphinx 没有 warning (构建用 `-W`, 任何 warning 都会失败), 需要的话 `mise run view-doc` 本地看一眼.
