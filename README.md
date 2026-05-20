# 科研实习工作记录

这是一个用于实习期间每日工作汇报、周报总结、阅读记录和阶段性进度留痕的自动化仓库。

每天可以手动新增 `.md` 日报文件；如果当天晚上 23:45 仍然没有对应日期的日报，自动化流程会创建一份空白日报模板，方便后续补充。首页优先展示当天日报；如果当天还没有记录，则自动展示最近一篇日报，并提示“今日暂无记录，当前展示最近一次工作记录”。

## 目录结构

```text
.
├── README.md
├── requirements.txt
├── reports/
│   └── 2026-05-21.md
├── weekly/
├── paper-notes/
├── milestones.md
├── scripts/
│   ├── ensure_today_report.py
│   └── generate_index.py
├── index.html
├── archive.html
├── weekly.html
├── papers.html
├── milestones.html
└── .github/
    └── workflows/
        ├── build-and-deploy.yml
        └── ensure-daily-report.yml
```

## 页面说明

- `index.html`：首页，展示今日工作汇报；当天日报不存在时展示最近一篇日报。
- `archive.html`：日报归档页，按时间倒序列出全部日报。
- `weekly.html`：周报页，展示最近一篇周报并列出历史周报。
- `papers.html`：阅读笔记页，列出 `paper-notes/` 下的阅读笔记。
- `milestones.html`：阶段性里程碑页，渲染 `milestones.md`。

## 日报使用方式

每天在 `reports/` 下创建日期命名的 `.md` 文件：

```text
reports/YYYY-MM-DD.md
```

示例：

```text
reports/2026-05-21.md
reports/2026-05-22.md
```

建议模板：

```markdown
# YYYY-MM-DD 工作汇报

## 今日目标

- 

## 今日完成

- 

## 遇到的问题

- 

## 明日计划

- 

## 思考与总结


```

## 自动补日报模板

仓库包含 `ensure-daily-report.yml` 自动化流程：

- 每天北京时间 23:45 检查 `reports/YYYY-MM-DD.md` 是否存在。
- 如果文件已经存在，不做任何修改。
- 如果文件不存在，自动创建一份空白日报模板并提交到仓库。
- 自动提交后，会触发页面重新生成与部署。

也可以手动运行：

```bash
python scripts/ensure_today_report.py
```

## 周报使用方式

在 `weekly/` 目录下新增周报 `.md` 文件，推荐使用周编号或周结束日期命名：

```text
weekly/2026-W21.md
weekly/2026-05-24.md
```

建议结构：

```markdown
# 2026-W21 周报

## 本周完成

- 

## 学习收获

- 

## 问题与风险

- 

## 下周计划

- 
```

`weekly.html` 会展示最近一篇周报，并保留历史周报入口。

## 阅读笔记使用方式

在 `paper-notes/` 目录下新增阅读笔记。文件名可以使用日期、资料简称或主题：

```text
paper-notes/2026-05-21-reading-note.md
paper-notes/topic-summary.md
```

建议结构：

```markdown
# 阅读笔记标题

## 基本信息

- 来源：
- 日期：
- 主题：

## 核心问题

- 

## 内容概述

- 

## 关键结论

- 

## 与当前工作的关系

- 
```

`papers.html` 会按时间或文件名倒序列出全部阅读笔记。

## 里程碑使用方式

阶段性成果记录在仓库根目录的 `milestones.md` 中。建议记录关键节点、阶段成果、实践进展、汇报材料和后续计划。

示例：

```markdown
# 阶段性里程碑

## 2026-05-21：建立工作留痕系统

- 完成日报、周报、阅读笔记和里程碑页面。
- 配置自动化部署流程。
```

## 本地预览

安装依赖并生成全部页面：

```bash
pip install -r requirements.txt
python scripts/generate_index.py
```

生成完成后，用浏览器打开仓库根目录下的 `index.html` 即可预览。脚本会同时生成：

```text
index.html
archive.html
weekly.html
papers.html
milestones.html
```

## 页面托管配置

第一次使用时，需要在仓库设置中启用静态页面托管：

1. 打开仓库的 `Settings`。
2. 进入 `Pages`。
3. 在 `Build and deployment` 中将 `Source` 选择为 `GitHub Actions`。
4. 保存后，后续 push、定时任务或手动触发都会自动部署页面。

## 自动化逻辑

- 页面构建：当 `main` 分支中的 `reports/**`、`weekly/**`、`paper-notes/**`、`scripts/**`、`milestones.md`、`requirements.txt` 或页面构建流程文件发生变化时自动构建部署。
- 每日构建：每天北京时间 06:00 自动生成并部署静态页面。
- 日报补全：每天北京时间 23:45 自动检查并补充当日空白日报模板。
- 手动触发：可以在仓库的自动化页面手动运行。

## 后续可扩展方向

- 生成月度汇总。
- 增加关键词统计。
- 增加阅读记录统计。
- 增加项目里程碑时间线。
- 增加汇报摘要页面。
