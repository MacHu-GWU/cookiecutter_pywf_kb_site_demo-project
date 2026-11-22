// Click to copy: any <button class="kb-copy" data-copy="..."> copies its
// data-copy value and shows data-copied ("Copied") next to it for 2 seconds.
// Used by the doc_id, permalink and raw link buttons (_templates/components/view-this-page.html).
(function () {
  "use strict";

  // sphinx-copybutton (the copy button on code blocks) picks its tooltips from
  // <html lang="zh-CN">: "复制" / "复制成功!" / "复制失败". Show the English ones
  // ("Copy" / "Copied!" / "Failed to copy") on every page instead. Its message
  // table is a global const of copybutton.js, which loads before this file,
  // and is read when the buttons are added and clicked, so editing it here
  // is enough.
  if (typeof messages === "object" && messages && messages.en) {
    for (const lang of Object.keys(messages)) messages[lang] = messages.en;
  }

  async function copyText(text) {
    // The Clipboard API needs a secure context (https or localhost).
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (e) {
        // fall through to the old way
      }
    }
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    let ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (e) {
      ok = false;
    }
    area.remove();
    return ok;
  }

  document.addEventListener("click", async (event) => {
    const button = event.target.closest("button.kb-copy[data-copy]");
    if (!button) return;
    event.preventDefault();
    if (!(await copyText(button.dataset.copy))) return;
    button.classList.add("kb-copied");
    clearTimeout(button._kbCopyTimer);
    button._kbCopyTimer = setTimeout(() => button.classList.remove("kb-copied"), 2000);
  });
})();
