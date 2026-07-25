---
name: autonomous-learning-engine
description: 提供在獨立主機 (如 N100) 上部署與維護 Hermes Agent 自主學習引擎（含自動節流與遙測防護）的完整架構指南與試誤記錄。
---

# Autonomous Learning Engine (自主學習引擎)

本技能總結了將 Hermes Agent 轉化為「無人值守自主進化實體」的部署架構、試誤過程與防護欄設計。

## 1. 核心架構 (The Architecture)

自主學習引擎包含三個核心組件：
1. **心跳觸發器 (Heartbeat Cron)**: 部署於邊緣節點 (N100) 的定時排程，負責定期喚醒 Agent。
2. **自動節流閥 (Auto-Throttle)**: 每次喚醒前，強制攔截並檢查 API Token 餘額（如 Minimax API `token_plan/remains`），避免爆量計費。
3. **跨節點遙測 (Cross-Node Telemetry)**: Agent 節點每日輸出學習軌跡日誌，由架構師節點 (Antigravity) 每日定時拉取並摘要。

## 2. 試誤與修正過程 (Trial and Error Learnings)

- **[錯誤 1] 直接呼叫 CLI 的阻塞問題**
  - **嘗試**: 直接將 `hermes chat` 寫入 cron。
  - **結果**: Cron 任務卡死，產生殭屍進程 (Zombie Processes)。
  - **修正**: 改用語法 `nohup hermes chat -q "..." >> log 2>&1 &` 將任務推入背景，並加上 `pgrep` 鎖定機制 (`is_learning_in_progress()`) 避免重複啟動。

- **[錯誤 2] 額度耗盡導致任務崩潰**
  - **嘗試**: 設定高頻率 (每 10 分鐘) 盲目學習。
  - **結果**: 若無防護，當模型 API 額度用盡時，Agent 會陷入報錯迴圈，甚至破壞本機配置檔。
  - **修正**: 撰寫 `smart_heartbeat.py`。透過 `urllib.request` 在觸發前向 `https://api.minimax.io/v1/token_plan/remains` 查詢 `current_interval_remaining_percent`。若低於 15%，強制 `sys.exit(0)` 保留緊急額度供手動任務使用。

- **[錯誤 3] GitHub Secret Scanning 封鎖**
  - **嘗試**: 將 N100 上的 Cron 目錄備份推送到 GitHub，其中包含含有 Token 的 `jobs.json`。
  - **結果**: `git push` 被遠端拒絕，備份鏈中斷。
  - **修正**: 移除敏感金鑰並利用 `rm -rf .git && git init && git push -f` 抹除備份倉庫的污染歷史。未來設定 Autonomous Cron 時，Token 應獨立存放於 `.env`，避免寫入 `jobs.json` 提示詞中。

## 3. 部署 SOP (Deployment Protocol)

當需要在新環境部署自主學習引擎時，請遵循以下步驟：
1. **檢查依賴**: 確保 Agent CLI (如 `hermes`) 與 API 金鑰 (`.env`) 已就緒。
2. **部署 Smart Heartbeat**: 撰寫包含 Token 檢查與進程鎖 (Process Lock) 的 python 腳本。
3. **註冊排程**: `(crontab -l 2>/dev/null; echo '*/10 * * * * python3 /path/to/smart_heartbeat.py') | crontab -`
4. **部署遙測**: 撰寫 `generate_telemetry.py` (每晚 23:50) 與對應的架構師端 (Antigravity) 喚醒排程 (每日 08:00)。

> [!CAUTION]
> 永遠不要在沒有實作 Auto-Throttle (自動節流) 的情況下設定高頻心跳，這將導致毀滅性的帳單或額度枯竭。

## ?? �[�c�t�i�GVercel Serverless Gist Bridge �P Excalidraw UI
1. **��Ʋ�_ (Decoupled Data)**�G�N N100 �Ѩ��� JSON �z�L GitHub Repo (�� Gist) �o���� Public Raw ���}�A���e�ݵL���A������C
2. **UI ���� (Excalidraw Style)**�G�ϥ� ECharts (�ί� CSS) �f�t Virgil �r���B��ø��� (border-radius: 255px 15px 225px 15px/15px 225px 15px 255px) ������~����A�ä䴩�L/�`��Ҧ��C
3. **�h�y���`�I**�GPrompt �W�w LLM ��X�y���� (English)�z�榡�A�A�ѫe�ݰʺA�����ƪ��C
4. **�����W�W�Ҧ�**�G�T�� Hermes �ϥ� clarify �u��A�j���H�����D�æۥD Debug �쩳�C�ëإ����V�^�X���� (review_queue.md & architect_feedback.md)�C
