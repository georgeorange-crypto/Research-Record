# 陶鼎文组实习工作汇报

这是一个用于中国科学院计算技术研究所高性能计算机研究中心陶鼎文课题组实习期间每日工作汇报、周报总结、论文阅读记录和阶段性进度留痕的自动化仓库。

每天只需要新增 Markdown 文件，GitHub Actions 会自动生成静态页面并部署到 GitHub Pages。首页优先展示当天日报；如果当天还没有记录，则自动展示最近一篇日报，并提示“今日暂无记录，当前展示最近一次工作记录”。

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
│   └── generate_index.py
├── index.html
├── archive.html
├── weekly.html
├── papers.html
├── milestones.html
└── .github/
    └── workflows/
        └── build-and-deploy.yml
```

## 页面说明

- `index.html`：首页，展示今日工作汇报；当天日报不存在时展示最近一篇日报。
- `archive.html`：日报归档页，按时间倒序列出全部日报。
- `weekly.html`：周报页，展示最近一篇周报并列出历史周报。
- `papers.html`：论文笔记页，列出 `paper-notes/` 下的论文阅读笔记。
- `milestones.html`：阶段性里程碑页，渲染 `milestones.md`。

## 日报使用方式

每天在 `reports/` 下创建日期命名的 Markdown 文件：

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

## 周报使用方式

在 `weekly/` 目录下新增周报 Markdown 文件，推荐使用周编号或周结束日期命名：

```text
weekly/2026-W21.md
weekly/2026-05-24.md
```

建议结构：

```markdown
# 2026-W21 周报

## 本周完成

- 

## 技术收获

- 

## 问题与风险

- 

## 下周计划

- 
```

`weekly.html` 会展示最近一篇周报，并保留历史周报入口。

## 论文笔记使用方式

在 `paper-notes/` 目录下新增论文阅读笔记。文件名可以使用日期、论文简称或主题：

```text
paper-notes/2026-05-21-ai-infra-survey.md
paper-notes/flashattention.md
```

建议结构：

```markdown
# 论文标题

## 基本信息

- 作者：
- 会议/期刊：
- 年份：

## 核心问题

- 

## 方法概述

- 

## 关键结论

- 

## 与当前工作的关系

- 
```

`papers.html` 会按时间或文件名倒序列出全部论文笔记。

## 里程碑使用方式

阶段性成果记录在仓库根目录的 `milestones.md` 中。建议记录关键节点、阶段成果、实验进展、汇报材料和后续计划。

示例：

```markdown
# 阶段性里程碑

## 2026-05-21：建立实习工作留痕系统

- 完成日报、周报、论文笔记和里程碑页面。
- 配置 GitHub Actions 自动部署。
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

## GitHub Pages 配置

第一次使用时，需要在 GitHub 仓库中启用 GitHub Pages：

1. 打开仓库的 `Settings`。
2. 进入 `Pages`。
3. 在 `Build and deployment` 中将 `Source` 选择为 `GitHub Actions`。
4. 保存后，后续 push、定时任务或手动触发都会自动部署页面。

## 自动化逻辑

- `push` 触发：当 `main` 分支中的 `reports/**`、`weekly/**`、`paper-notes/**`、`scripts/**`、`milestones.md`、`requirements.txt` 或 workflow 文件发生变化时自动构建部署。
- 定时触发：每天北京时间 06:00 自动运行。GitHub Actions cron 使用 UTC，因此 workflow 中配置为 `0 22 * * *`。
- 手动触发：可以在 GitHub Actions 页面通过 `workflow_dispatch` 手动运行。

## 后续可扩展方向

- 生成月报。
- 增加技术关键词统计。
- 增加论文阅读统计。
- 增加项目里程碑时间线。
- 增加导师汇报版摘要。
