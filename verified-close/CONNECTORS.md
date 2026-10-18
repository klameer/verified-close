# Connectors

> **Modified file** (Apache-2.0 §4(b)). Changed for verified-close, October 2026, from [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) @ `33eeda1`, `finance/CONNECTORS.md`: added "The close folder (this plugin's default)". Everything from "How tool references work" down is the upstream text, unchanged. This plugin ships no `.mcp.json`: the upstream one pre-configured data warehouse, chat and email servers the close does not need.

## The close folder (this plugin's default)

The gated close needs no connector. It runs on files in a **close folder** described by `close.toml`: the ERP's exports (bank statement, cashbook, trial balance), the budget workbook, the pack template and last month's signed reconciliation. See `examples/caldergate/` in the repository.

An `~~erp` connector can replace the exports folder: pull the same three datasets, save them where `close.toml` says the exports live, and the scripts run unchanged. Keep the connector read-only. The plugin never writes to a ledger.

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user connects in that category. For example, `~~data warehouse` might mean Snowflake, BigQuery, or any other warehouse with an MCP server.

Plugins are **tool-agnostic** — they describe workflows in terms of categories (data warehouse, chat, project tracker, etc.) rather than specific products. The `.mcp.json` pre-configures specific MCP servers, but any MCP server in that category works.

## Connectors for this plugin

| Category | Placeholder | Included servers | Other options |
|----------|-------------|-----------------|---------------|
| Data warehouse | `~~data warehouse` | Snowflake\*, Databricks\*, BigQuery | Redshift, PostgreSQL |
| Email | `~~email` | Microsoft 365 | — |
| Office suite | `~~office suite` | Microsoft 365 | — |
| Chat | `~~chat` | Slack | Microsoft Teams |
| ERP / Accounting | `~~erp` | — (no supported MCP servers yet) | NetSuite, SAP, QuickBooks, Xero |
| Analytics / BI | `~~analytics` | — (no supported MCP servers yet) | Tableau, Looker, Power BI |

\* Placeholder — MCP URL not yet configured
