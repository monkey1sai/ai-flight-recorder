# Codex 可執行專案總規格
## AI / Agent / LLM Observability Platform（Flight Recorder + Provenance Graph + Why Engine）

版本：v1.0  
日期：2026-04-17  
用途：這份文件是 **人類與 Codex 共用的專案系統說明書**。它的目的不是只描述產品概念，而是讓 Codex 能夠依照一致的契約完成以下工作：

1. 理解專案目標與邊界  
2. 搜尋並整理外部資料  
3. 設計與實作程式碼  
4. 執行測試、驗證與回報  
5. 持續更新知識文件與執行計畫  

---

## 0. 使用方式

### 給人類
你應該把這份文件視為：
- 專案的總設計說明
- 對 Codex 的工作約束
- 決定是否放行 PR / release 的共同標準

### 給 Codex
你應該把這份文件視為：
- 架構與產品的系統紀錄
- 任何非 trivial 任務的背景知識
- 撰寫與執行 ExecPlan 的上位規格

### 讀取順序
對 Codex 而言，建議的讀取順序固定如下：

1. `AGENTS.md`
2. 本文件 `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
3. `.agent/PLANS.md`
4. `plans/active/` 內最新且相關的計畫
5. `docs/` 內補充文件

---

## 1. 專案定位

### 1.1 一句話定義
打造一套讓人類理解 AI / Agent / LLM 行為的觀測平台，核心能力是：

- 記錄它做了什麼
- 顯示它看到了什麼
- 顯示狀態如何變化
- 追蹤哪些證據影響了哪些輸出
- 以可驗證的方式回答「為什麼它會這樣輸出」

### 1.2 產品名稱（工作名）
- AI Flight Recorder
- Agent Observability Studio
- Reasoning Provenance Workbench

### 1.3 核心價值
本產品不是要聲稱讀出模型真正的隱藏內心獨白，而是要建立一套 **可審計、可回放、可驗證** 的證據系統，讓人類能看懂：

- session / run / task 的過程
- observation / tool / retrieval / memory / state 的變化
- 最終輸出與來源證據的連結
- 模型自述、後設推論、可驗證事實之間的差異

---

## 2. 問題定義

### 2.1 我們要解決的痛點
目前大多數 AI 產品只給使用者最終答案，但缺少以下能力：

- 任務流程回放
- 工具與文件來源追蹤
- 狀態與計畫變更紀錄
- 哪個證據支持哪段輸出
- 為什麼最後選了 A 而不是 B
- 哪些解釋只是模型自述，哪些是真正可驗證的依據

### 2.2 本產品的回答方式
我們用四層證據等級處理所有 explanation：

- `observed`：來自 trace、tool result、retrieval、DB、system event 的硬證據
- `self_reported`：模型自己的敘述或 reasoning summary
- `inferred`：由 replay、shadow analysis、 post-hoc 分析推得
- `verified`：經 counterfactual / ablation / replay 支持的因果性說明

**非協商原則：**
> 任何 UI 或 API 都不得把 `self_reported` 假裝成 `verified`。

---

## 3. 目標使用者

### 3.1 主要角色
1. **AI 產品開發者**  
   需要知道 agent 在哪一層失敗，怎麼修。

2. **研究與評估人員**  
   需要把輸出拆成 claim，對應 evidence chain，分析 faithfulness 與 provenance。

3. **營運與風控角色**  
   需要 session 級別的 audit trail、資料來源追蹤、風險事件檢查。

4. **最終使用者 / 客戶成功角色**  
   需要簡單看懂「系統為何做出這個回答」。

### 3.2 典型問題
- 這個 agent 為什麼回錯？
- 它忽略了哪份文件？
- 哪段輸出沒有證據支持？
- 是哪個 tool result 改變了決策方向？
- 這次改版後，哪些 trace 品質下降？
- 哪些 explanation 只是 post-hoc 合理化？

---

## 4. 產品範圍

### 4.1 In scope（MVP 內）
- session / trace / step ingestion
- 可查詢的 canonical schema
- timeline / run detail UI
- state diff viewer
- evidence graph
- why panel（第一代）
- replay / validation hooks
- Google Drive 研究資料連接器
- arXiv metadata 研究資料連接器
- Codex-friendly repo contract（AGENTS / PLANS / skills / validation）

### 4.2 Out of scope（至少第一階段不做）
- 聲稱讀出隱藏 chain-of-thought
- 自動大規模儲存與重新分發受版權保護的論文 PDF
- 未經同意的 production full-access agent 自動執行
- 以 graph DB 為前提的重型基礎設施（MVP 先不用）
- 多租戶企業治理的完整商業化層（可後補）

---

## 5. 核心設計原則

### 5.1 Repository knowledge 是系統紀錄
文件不是附屬品；文件、計畫、驗證報告、品質規則都要跟程式碼一起版本化。

### 5.2 人類定義意圖，Codex 負責執行
人類負責：
- 設定方向
- 審核架構
- 給憑證與權限
- 做最後風險判斷

Codex 負責：
- 掃描專案
- 研究資料
- 撰寫計畫
- 實作程式碼
- 執行測試
- 更新文件
- 產出驗證報告

### 5.3 觀測資料必須 append-only
不要只存當前狀態。每一步的意圖、觀察、推論、操作、回應、風險判斷都應可追溯。

### 5.4 解釋必須分級
UI 與 API 不得把不同可信度的 explanation 混在一起。

### 5.5 預設最小權限
設計上採用 read-only / workspace-write / live research 的分層模式；高風險權限必須被明確區隔。

### 5.6 先有可驗證最小垂直切片，再擴充
Codex 在每個 milestone 先交出最小可跑的 slice，再擴到更完整功能。

---

## 6. 技術策略（具體決策）

> 這一節不是理論選項比較，而是本專案的預設決策。Codex 除非有明確理由，否則不應偏離。

### 6.1 專案型態
採 **monorepo**。

### 6.2 建議技術棧
- **Web UI**：Next.js + TypeScript + React + Tailwind
- **API / workers**：Python + FastAPI
- **DB**：PostgreSQL（canonical store）
- **Queue / cache**：Redis
- **Blob store**：S3-compatible object storage
- **Telemetry**：OpenTelemetry
- **Testing**：
  - Python：pytest
  - Web：Vitest / Playwright
  - API contract：schema + fixture tests
- **Developer contract**：Makefile 為統一入口

### 6.3 為何這樣選
1. Web 前端與操作台需要快速組裝與良好元件化。
2. Python 適合資料處理、連接器、worker、schema 驗證與研究流程。
3. PostgreSQL 足夠支援：
   - session / trace / step 的正規化表
   - JSONB payload metadata
   - edge table 形式的 provenance graph
4. MVP 不使用獨立 graph DB，以降低基礎設施複雜度。
5. Makefile 讓 Codex 有統一、穩定、可腳本化的執行入口。

---

## 7. 建議 repo 佈局

```text
repo-root/
├─ AGENTS.md
├─ COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md
├─ Makefile
├─ .codex/
│  └─ config.toml
├─ .agent/
│  └─ PLANS.md
├─ .agents/
│  └─ skills/
│     ├─ research-evidence/
│     ├─ implement-execplan/
│     └─ validate-release/
├─ apps/
│  ├─ web/
│  └─ api/
├─ workers/
│  ├─ ingest/
│  ├─ drive_sync/
│  ├─ arxiv_sync/
│  └─ replay/
├─ packages/
│  ├─ schema/
│  ├─ ui/
│  └─ testkit/
├─ docs/
│  ├─ architecture/
│  ├─ research/
│  ├─ TASK_SEEDS.md
│  ├─ SOURCES_AND_LIMITS.md
│  └─ ACCEPTANCE_CHECKLIST.md
├─ plans/
│  ├─ active/
│  └─ done/
├─ reports/
│  └─ validation/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ smoke/
│  └─ fixtures/
└─ infra/
   ├─ docker/
   └─ compose/
```

---

## 8. 必要的 automation contract

所有 repo 最終都應提供這些入口；若還沒有，Codex 的第一個 bootstrap 任務就是建立它們。

### 8.1 Makefile target 契約
- `make setup`
- `make lint`
- `make typecheck`
- `make unit`
- `make integration`
- `make smoke`
- `make test`
- `make validate`

### 8.2 各 target 語意
- `setup`：安裝依賴與本地工具
- `lint`：風格與靜態檢查
- `typecheck`：型別 / schema 檢查
- `unit`：快速 deterministic tests
- `integration`：資料庫、連接器、API、worker 整合測試
- `smoke`：最小端到端檢查
- `test`：聚合式本地測試
- `validate`：lint + typecheck + test + smoke + 必要報告

---

## 9. 核心資料模型（canonical schema）

這是產品的靈魂。Codex 在建立 DB schema、API contract、fixture 與 UI 時必須以這組概念為中心。

### 9.1 實體

#### Session
一個長任務或多輪互動的容器。

建議欄位：
- `id`
- `source`
- `user_id`
- `started_at`
- `ended_at`
- `status`
- `metadata_json`

#### Trace
一次 request / run / cloud task / local task。

建議欄位：
- `id`
- `session_id`
- `parent_trace_id`
- `task_id`
- `model_name`
- `started_at`
- `ended_at`
- `status`
- `config_ref`

#### Step
單一步驟，例如：
- model call
- tool call
- retrieval
- memory read
- memory write
- approval
- validation
- replay

建議欄位：
- `id`
- `trace_id`
- `parent_step_id`
- `step_type`
- `actor`
- `started_at`
- `ended_at`
- `status`
- `summary`

#### Observation
此步驟實際看到的東西。

- `id`
- `step_id`
- `kind`
- `content_ref`
- `confidence`
- `source_artifact_id`

#### StateDelta
狀態變更，至少支援：
- goal state
- plan state
- belief state
- memory state
- risk state
- environment state

- `id`
- `step_id`
- `facet`
- `before_json`
- `after_json`

#### Artifact
原始資料或可追溯物件，例如：
- prompt
- message
- doc chunk
- tool result
- Drive file
- arXiv record
- screenshot
- test log

- `id`
- `source_type`
- `source_uri`
- `mime_type`
- `checksum`
- `storage_ref`
- `metadata_json`

#### EvidenceEdge
把 claim、artifact、step、output 等串起來的邊。

- `id`
- `from_kind`
- `from_id`
- `to_kind`
- `to_id`
- `relation`
- `weight`
- `metadata_json`

#### OutputClaim
把最終輸出拆成可驗證 claim。

- `id`
- `trace_id`
- `claim_text`
- `claim_type`
- `confidence`
- `position_index`

#### ExplanationRecord
某個 claim 的 explanation 物件。

- `id`
- `claim_id`
- `grade`  
  (`observed | self_reported | inferred | verified`)
- `method`
- `summary`
- `supporting_edge_ids`
- `confidence`

#### Evaluation
測試或審查結果。

- `id`
- `trace_id`
- `suite_name`
- `metric_name`
- `score`
- `verdict`
- `details_json`

#### Intervention
任何 guardrail / fallback / override。

- `id`
- `trace_id`
- `step_id`
- `intervention_type`
- `reason`
- `actor`
- `result`

### 9.2 設計規則
1. **raw payload 與 normalized metadata 分開存**
2. **大內容走 object store，DB 只留 reference**
3. **evidence graph 先用 relation table，不先上 graph DB**
4. **每個 explanation 必須標示 grade**
5. **沒有 evidence 的 claim 必須可標成 unsupported**

---

## 10. 產品畫面（MVP 到 V1）

### 10.1 Live Timeline
顯示：
- user input
- plan
- model step
- tool call
- retrieval
- memory op
- validation
- final output

### 10.2 State Diff Viewer
每個 step 前後：
- goal
- plan
- belief
- risk
- memory
- pending actions

### 10.3 Evidence Graph
從 output claim 追到：
- artifact
- retrieval chunk
- tool result
- prior step
- memory item
- config

### 10.4 Why Panel
對單一輸出片段顯示：
- supporting evidence
- explanation grade
- alternative explanation
- unsupported flag
- confidence

### 10.5 After-Action Review
讓使用者問：
- 在某時間點它知道什麼？
- 為何忽略某份文件？
- 哪個 tool result 改變了判斷？

---

## 11. 為什麼輸出引擎（Why Engine）第一代規格

### 11.1 基本流程
1. 將輸出拆成 atomic claims
2. 對每個 claim 連 evidence edges
3. 標示 support 狀態
4. 加上 explanation grade
5. 提供 UI 查詢與 API 查詢

### 11.2 claim 狀態
- `supported`
- `partially_supported`
- `unsupported`
- `model_prior_only`
- `conflicted`

### 11.3 explanation method
- `direct_trace_link`
- `tool_result_link`
- `retrieval_link`
- `self_report`
- `counterfactual_check`
- `shadow_analysis`
- `human_annotation`

### 11.4 第一代不做的事
- 完整機制化因果推論
- 大規模 shadow-model infra
- 自動 truth adjudication across all claims

---

## 12. 研究資料流：Web / Google Drive / arXiv

這個專案不只是工程工具，也是一個研究工作台。Codex 必須能夠「找資料 → 轉成 evidence → 實作」。

### 12.1 統一原則
對每個外部來源，都要保留：

- `source_type`
- `source_id`
- `source_uri`
- `retrieved_at`
- `license_or_terms_note`
- `ingest_job_id`
- `checksum`（若適用）
- `content_ref`
- `metadata_json`

---

### 12.2 Web research workflow

#### 目標
讓 Codex 在需要 current info 時，不依賴過期記憶。

#### 規則
1. 先官方文件，再 primary sources，再高品質二手來源
2. 研究結果要落地成 repo 內文件，不只在對話裡
3. 每個研究結論都要說明「對實作有何影響」
4. Web result 一律視為 untrusted input，要做來源分級

#### 產出格式
建議記錄在 `docs/research/YYYYMMDD-topic.md`：

- Question
- Why this matters
- Source table
- Key facts
- Implementation consequences
- Open questions
- Next safe action

---

### 12.3 Google Drive 連接器規格

#### 目標
用於搜尋私人研究資料庫、筆記、論文 PDF、Google Docs 與版本/活動歷史。

#### MVP 功能
1. 檔案搜尋
2. metadata 擷取
3. Google Docs export（若適用）
4. 增量變更同步
5. 活動紀錄 enrich
6. provenance 保存

#### 讀取模式
先做 **read-only connector**，不要一開始就支援寫入。

#### 建議工具面
若你有 MCP / internal tools，建議至少暴露：
- `drive.search_files`
- `drive.get_file_metadata`
- `drive.export_doc`
- `drive.list_changes`
- `drive.get_activity`

#### 搜尋策略
支援：
- title/name query
- fullText phrase query
- mimeType filter
- shared drive / my drive scope
- modified time filter
- trashed=false
- tags / custom properties（若企業環境有）

#### 實作規則
- 搜尋結果與匯出結果都要建立 `Artifact`
- 儘量保存 `file_id`, `revision-like info`, `modifiedTime`, `owners`, `mimeType`
- 若檔案太大無法 export，至少保存 metadata 與失敗原因
- 任何同步 worker 都要有 resumable cursor / token

#### 必留 provenance
- Drive file id
- source query
- retrieval timestamp
- change token
- activity actor / action / target（若有）
- exported mime type
- export status

---

### 12.4 arXiv 連接器規格

#### 目標
建立公開研究文獻的 metadata feed 與 topic watchlist。

#### MVP 功能
1. 關鍵字搜尋
2. category filter
3. 作者 / title / abstract 搜尋
4. metadata 落庫
5. daily 更新模式抽象
6. 與 internal research notes 的 cross-link

#### 建議工具面
- `arxiv.search`
- `arxiv.get_paper`
- `arxiv.harvest_metadata`
- `arxiv.track_topics`

#### Topic watchlist 初始集合
- `agent observability`
- `reasoning provenance`
- `faithful explanations`
- `chain-of-thought faithfulness`
- `agent monitoring`
- `MCP telemetry`
- `tool-use provenance`
- `AI audit trail`

#### 必留欄位
- arXiv id
- title
- authors
- abstract
- categories
- published date
- updated date
- primary category
- abstract page URL
- PDF URL（只作 reference，不預設再分發）
- ingestion timestamp
- query that found the paper

---

## 13. 推薦的連接器實作順序

1. `workers/arxiv_sync/`  
   因為公開、易測、低憑證成本。

2. `workers/drive_sync/`  
   第二階段接 read-only OAuth / service integration。

3. `workers/replay/`  
   把 trace 回放與 validation 接起來。

---

## 14. Codex 的工作模式

這一節是整個文件最重要的部分：它定義了 Codex 如何從理解專案走到自動執行專案。

### 14.1 標準作業流程

#### Phase A：理解
1. 讀 `AGENTS.md`
2. 讀本文件
3. 讀 `.agent/PLANS.md`
4. 讀現有 active plan
5. 掃描 repo tree
6. 列出已存在的 command contract 與缺口

#### Phase B：規劃
若任務非 trivial，建立或更新 plan：
- scope
- assumptions
- milestones
- success criteria
- validation plan

#### Phase C：研究
若需要 current or external info：
- 用 `$research-evidence`
- 官方文件優先
- 研究結果寫回 repo

#### Phase D：實作
- 一次只做一個 milestone 的最小可驗證 slice
- 先建立 schema / fixtures / API contract，再堆 UI
- 先讓測試可執行，再增加功能

#### Phase E：驗證
- 跑最小 relevant tests
- 再跑 broader gates
- 產出 validation report

#### Phase F：更新知識
- 更新 active plan
- 更新 docs
- 記錄決策與發現
- 若 milestone 完成，把計畫移到 `plans/done/`

---

## 15. Codex 何時要用哪些 repo 能力

### 15.1 何時必須建立 plan
符合以下任一條件都要建：
- 多檔案
- 多子系統
- 外部研究
- schema / API / infra 變更
- 估計 > 30 分鐘
- 需要 staged validation

### 15.2 何時要用 research skill
- 需要 current docs
- Google Drive / arXiv / OTel / Codex 配置疑問
- 任何可能已變動的 API / policy / limit

### 15.3 何時要用 validate skill
- milestone 完成
- 準備 merge
- 大改版後
- connector / worker / schema 變更後
- 說明「這真的能用嗎」的時候

### 15.4 何時可用 subagents
只有在使用者或 plan 明確要求時，才平行拆成獨立子任務，例如：
- frontend shell
- backend schema
- research ingestion
- validation audit

**不要為了看起來聰明而無限制拆子代理。**

---

## 16. 建議的 Codex 執行指令模式

### 16.1 只看 repo，不修改
```bash
codex --sandbox read-only --ask-for-approval never "Summarize this repository and list the active instruction files."
```

### 16.2 本地低摩擦實作
```bash
codex exec --json --full-auto "Read AGENTS.md and the active ExecPlan, implement the current milestone, run the narrowest relevant checks, and update the plan."
```

### 16.3 需要最新網路資訊的研究
```bash
codex --profile research_live --search "Use the $research-evidence skill and produce a reusable note for this repository."
```

### 16.4 只做 read-only 驗證
```bash
codex exec --json --sandbox read-only --ask-for-approval never "Use the $validate-release skill to audit this branch against docs/ACCEPTANCE_CHECKLIST.md."
```

### 16.5 雲端背景任務（可選）
若你使用 Codex cloud / app，可把長任務交給 cloud environment，但仍要遵循本 repo 的 AGENTS / plan / validation 契約。

---

## 17. 安全與權限設計

### 17.1 預設原則
- 預設最小權限
- 預設 read-only 或 workspace-write
- 需要 live research 才開網路
- 危險模式只在隔離 runner 中使用

### 17.2 本 repo 的權限層級建議
1. `readonly_quiet`
2. `build_local`
3. `research_live`
4. `dangerous_full_access`（原則上不預設提供）

### 17.3 設定與秘密
- `.codex/config.toml` 視為較穩定的控制面
- 真正 secrets 不應硬編碼
- 任何連接器都應支援 mock / fixture 模式
- 雲端 setup script 可取得 secrets，但 agent phase 應假設不可依賴 setup script 的 export 狀態持續存在

### 17.4 shell environment policy
應該採 include-only 最小白名單，而不是把整個 shell 環境全部暴露給 agent。

---

## 18. Telemetry 與 OTel 策略

### 18.1 內部 canonical schema 優先
OTel 是輸出與對接層，不是產品內部唯一真實 schema。

### 18.2 分層
- **Canonical schema**：產品內部的長期穩定資料模型
- **OTel mapping layer**：對外或對標準化工具導出的相容層
- **Blob store refs**：原始大內容
- **Query / analytics layer**：給 UI 與 replay 使用

### 18.3 原始內容處理
prompt / output / tool payload 可能很大、也可能含敏感資訊，所以：
- trace metadata 與 raw content 分離
- raw content 用 reference
- 預設 redaction
- 使用者可控地開啟更詳細記錄

---

## 19. 測試策略

### 19.1 測試層次
1. **Unit**
   - schema validation
   - claim extraction
   - evidence linking
   - connector parser
   - policy helpers

2. **Integration**
   - DB migrations
   - ingest API
   - Drive connector with fixtures
   - arXiv connector with fixtures
   - object storage ref flow

3. **Smoke**
   - sample trace ingest
   - sample run detail render
   - sample why panel render
   - sample research note generation

4. **Eval / Audit**
   - Codex skill trigger behavior
   - plan adherence
   - unsupported claim marking
   - provenance completeness

### 19.2 測試原則
- external connectors 先用 fixtures / mocks
- live credentials 只做 opt-in testing
- every milestone 至少有一個 smoke path
- validation report 是 deliverable，不是可有可無

### 19.3 驗證報告格式
建議 `reports/validation/YYYYMMDD-topic.md`

內容至少包含：
- Scope
- Commands run
- Pass / fail summary
- Known issues
- Risk assessment
- Recommendation

---

## 20. Evals 與 deterministic graders

因為這個 repo 是給 Codex 長期工作用，所以不只要測程式，也要測 agent workflow。

### 20.1 最小 eval 類型
- skill 會不會正確觸發
- 會不會亂觸發
- 在 plan 存在時會不會先更新 plan
- 驗證任務會不會真的寫 report
- research 任務會不會生成可重用 evidence note

### 20.2 基本做法
- 使用 `codex exec --json`
- 保存 JSONL trace
- 對輸出事件做 deterministic checks
- 將 prompt set 存在 `evals/`

---

## 21. 里程碑規劃

### Milestone 0：Repo bootstrap
交付：
- monorepo skeleton
- Makefile contract
- lint / typecheck / test wiring
- AGENTS / PLANS / skills / reports dir
- first bootstrap validation report

### Milestone 1：Canonical schema + fixtures
交付：
- DB models / migrations
- seed fixtures
- API contracts
- schema tests

### Milestone 2：Ingestion API + run detail
交付：
- ingest endpoint
- artifact refs
- run detail API
- minimal timeline UI

### Milestone 3：State diff + evidence graph
交付：
- state delta persistence
- evidence_edge linking
- graph API
- graph UI prototype

### Milestone 4：Research connectors
交付：
- arXiv metadata connector
- Google Drive read-only connector
- source provenance fields
- integration tests with fixtures

### Milestone 5：Why Engine v1
交付：
- claim extraction
- support classification
- explanation grade UI
- unsupported claim handling
- validation cases

### Milestone 6：Replay + evals + hardening
交付：
- replay worker
- milestone evals
- OTel export mapping
- retention / redaction policies
- release checklist automation

---

## 22. 初始 backlog（建議 Codex 依序完成）

1. bootstrap repo
2. define schema
3. implement migrations
4. implement ingest API
5. create fixture trace
6. build run detail page
7. build timeline
8. build state diff API
9. build evidence graph API
10. build why panel API + UI shell
11. implement arXiv connector
12. implement Google Drive connector
13. add validation reports
14. add smoke tests
15. add OTel mapping export

---

## 23. 第一批你應該要求 Codex 產出的文件

除了程式碼之外，Codex 第一輪就應該補齊：

- `plans/active/<bootstrap>.md`
- `docs/architecture/overview.md`
- `docs/research/source-policy.md`
- `reports/validation/<bootstrap>.md`

這會讓後續長期運作的可靠性大幅提高。

---

## 24. 非協商品質規則（Golden Principles）

1. **Docs 與 code 一起變更**
2. **沒有 plan 的大任務視為未準備好**
3. **沒有 validation report 的 milestone 視為未完成**
4. **沒有 source metadata 的外部資料視為低可信度**
5. **不得把模型自述當作已驗證原因**
6. **不得把 unsupported claim 偽裝成 supported**
7. **不得讓 repo 依賴手動口頭知識才能運作**
8. **不得在正常 feature 任務中隨意修改 `.codex/` 或 `.agents/` 基礎設施**
9. **不得留下只有人類記得、repo 裡不存在的關鍵規則**
10. **一切以可重跑、可審計、可交接為目標**

---

## 25. 給 Codex 的執行準則（精簡版）

你在這個 repo 內工作時，必須假設：

- 你需要先讀 instruction chain
- 重大任務必須建立或更新 ExecPlan
- 研究結果必須落地到 repo
- 實作要採最小可驗證 slice
- 每個安全停點都要更新 plan
- 完成前要有 tests + docs + validation evidence
- 你不是在寫一次性的 demo，而是在建立可持續被 agent 維護的系統

---

## 26. Source basis（給人類用）

本文件的操作設計，建立在下列類型來源之上：

### A. Codex 官方操作模型
- AGENTS.md discovery
- sandbox / approvals
- CLI exec / JSON output
- profiles / config layering
- cloud setup / internet access / secrets
- skills / repo skill paths
- web search modes
- OTel export options

### B. Google Drive 官方 API 能力
- files.list search
- query operators
- files.export
- changes.getStartPageToken / list / watch
- Drive Activity API

### C. arXiv 官方 API / policy
- API search
- start / max_results paging
- rate limits
- OAI-PMH for metadata harvesting
- attribution and redistribution constraints

### D. OpenTelemetry 官方規格
- GenAI semantic conventions
- agent spans
- MCP spans
- development / evolving status

### E. 研究論文方向
- reasoning provenance
- agent observability
- unfaithful chain-of-thought
- explanation faithfulness
- provenance graph for agent workflows

---

## 27. 最後結論

這個專案的真正產品，不只是觀測平台本身；也是一套 **讓 Codex 能夠持續理解、研究、實作、測試、驗證、演進這個平台的工程作業系統**。

因此，本文件的核心要求只有一句：

> **把知識、計畫、程式、測試、驗證、來源證據全部收斂到 repo 內，讓下一次的 Codex 可以從 repo 本身重新啟動工作。**
