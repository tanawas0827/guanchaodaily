# 网站全栏目自动更新

覆盖首页新闻、风景、常识、荤素菜单、酒吧饮品、食尚、时尚与男女妆教、行业、中国各地、人物，另有两份周报及月度文青，共13项。

## 一次性启用

1. 仓库 Settings → Secrets and variables → Actions → Secrets：新增 OPENAI_API_KEY。只能在 GitHub 的密钥界面填写，不发到聊天、不写进源码。需使用具有 Responses API 与 web_search 权限且有可用额度的 OpenAI API 项目密钥。
2. Actions → Variables：新增 AUTO_CONTENT_ENABLED，值为 true。这一步是显式启用付费API调用。ChatGPT订阅不等于API额度，模型与搜索按API用量计费；先在API项目设置预算和告警。
3. 可选 OPENAI_MODEL，默认 gpt-5-mini；所选模型必须支持Responses API、web_search与结构化输出。
4. Actions → Update All Content → Run workflow。检查各栏目生成、data/update-status.json、Publish website步骤。缺失凭据时任务明确失败并保留旧内容，不伪造更新。

## 时间与恢复

每天北京时间09:00首次检查，15:00、21:00补漏；GitHub可能延迟排队，不保证准点。当天已生成不再付费生成，失败项下次重试。周报每周首次运行按周一周期生成，文青每月首次运行生成。历史专题保留；同日不重复；已有本月书单不覆盖选书ID。网页本地选书只保存在浏览器。

## 验证边界

本地测试验证调度、历史合并、缺密钥保留旧文、拒绝不合格内容和无来源链接。没有API密钥时不能验证真实模型调用或声明无人值守已修复。检索来源可追溯不等于内容绝无错误，保留原始来源供阅读者核验。

## 管理

编辑 automation/content-jobs.json 中的栏目要求。单项调试：python automation/update_content.py --only daily-knowledge。不要手动给旧文换日期。需要暂停生成，将AUTO_CONTENT_ENABLED改为false；不要删除旧数据。

GitHub Actions直接发布dist中的index.html与data，不依赖机器人提交再次触发Pages，因此能验证从生成到上线的一条流程。不要向日志或网页输出密钥。
