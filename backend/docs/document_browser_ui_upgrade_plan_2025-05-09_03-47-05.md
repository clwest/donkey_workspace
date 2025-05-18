
# 🧠 Document Browser + Detail UI Upgrade Plan

We're cleaning up the document UI and adding useful features piece-by-piece. Here's our checklist of upgrades:

---

## ✅ 1. Filter out duplicate chunks in Document Browser
- Only show documents where `metadata.chunk_index === 0` (already done)

---

## ⏭️ 2. Update the Document Card UI
- [ ] Title as `Link` to detail view
- [ ] Show **domain only** (like `wikipedia.org`) instead of full URL
- [ ] Improve summary truncation logic
- [ ] Add source type tag (e.g. `🔗 URL`, `📄 PDF`, `📺 YouTube`)

---

## 🔄 3. Expandable Smart Chunk Viewer
- [ ] Make accordion fully expandable
- [ ] Include `chunk.text` inside
- [ ] Add token count display
- [ ] Add optional “Copy” button on hover

---

## 📊 4. Add Full Document Stats
- [ ] Token total
- [ ] Chunk count
- [ ] Average and max tokens per chunk

---

## 🏷️ 5. Show Document Tags
- [ ] Display any `document.tags.all()` under the title

---

## 📎 6. Extra Utilities (Optional)
- [ ] "Copy All Text"
- [ ] "Download as .txt"
- [ ] "Send to Zeno" button (hooked into memory/project)

---

## 🧠 Future: Link Document to Memory
- [ ] Allow linking to `MemoryContext` or `AssistantProject`
- [ ] Show “Used In” panel (future memory trace feature)

