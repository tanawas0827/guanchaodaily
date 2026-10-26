# 无需额外API密钥的自动更新

## 当前方案

ChatGPT的“更新观潮全部栏目”定时任务负责检索、生成、写入13个栏目数据，使用已有ChatGPT服务与GitHub连接，不调用额外模型API。
北京时间09:00更新，15:00、21:00检查缺更项重试；同日已完成、当周周报及当月书单跳过。任务受ChatGPT计划用量与应用审批约束，不能保证永远不需要人工处理批准。

GitHub Actions“Publish and Check Content”负责检查实际内容日期与发布，push数据后立即运行，另每日09:15/15:15/21:15检查。它不调用模型API、不重新生成文章，也不把过期内容换日期。data/update-status.json显示每个栏目的真实新鲜度，stale表示等待补更，不是已经更新。

## 验证与边界

2026-10-26定时触发的验证请求已成功创建data/automation-probe.json并回读，提交640d85674b84366f25b27ed0251882be5f8b4dc8。它验证单文件定时读写，不等于全栏目长文已成功生成。全任务运行后须逐项核对日期和提交记录。

如果任务暂停，查看Scheduled的待处理操作、GitHub连接与实际写入错误。不要在不知道具体原因时授予宽泛权限，不要把保存提示词当作同步成功。可在聊天明确要求立即补更。

## 可选备用实现

automation/update_content.py仍是未启用的API备用程序，本工作流不会执行它。OPENAI_API_KEY与AUTO_CONTENT_ENABLED都不是当前方案必需设置，也不需要为了当前方案添加密钥。栏目要求位于automation/content-jobs.json。
