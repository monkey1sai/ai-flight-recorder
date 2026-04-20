# Definition Of Done

一個變更只有在以下條件滿足時，才算完成。

## Required

- [ ] 變更範圍與原始需求一致，沒有偷渡額外 concern
- [ ] relevant docs 已同步更新
- [ ] 非 trivial 任務的 active plan 已更新
- [ ] 已執行可用驗證命令，並保存結果
- [ ] 若有失敗，已記錄失敗原因、影響範圍與後續處置
- [ ] 沒有提交 secrets、local credentials、generated dirs、cache artifacts
- [ ] PR 可由 reviewer 在不依賴口頭背景的情況下理解

## For Major Work

- [ ] 有報告或 validation note
- [ ] 有風險與 blocker 說明
- [ ] 有清楚的 follow-up 清單

## Not Done If

- 沒有驗證證據
- 只有「應該可行」但沒有實際執行命令
- 文檔與程式碼不同步
- 工作樹混入 unrelated changes 卻未說明
