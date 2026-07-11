# 🔎 TrendWatch

An automated monitoring tool that tracks keyword mentions across web sources and reports new matches daily — no manual checking required.

**Live dashboard:** _add your GitHub Pages link here once enabled_

## What it does

TrendWatch checks configured sources (currently Hacker News) every day for stories matching a keyword list you control. New matches are saved to a growing history log and displayed on a live dashboard — fully automated via GitHub Actions.

This is built as a general-purpose monitoring service: adding a new source (a competitor's site, Reddit, a job board, etc.) only requires writing one small module — the rest of the pipeline, filtering, storage, and dashboard work unchanged.

## Features

- ✅ Whole-word keyword matching (no false positives from substrings)
- ✅ Runs automatically every day via GitHub Actions
- ✅ Keeps a full history (not just a snapshot) — enables trend tracking over time
- ✅ Live public dashboard, no server required
- ✅ Fully configurable via `config.yml` — change keywords or sources without touching code
- ✅ Modular source system — add a new site to monitor without rewriting existing logic

## Tech stack

- **Python:** `requests`, `beautifulsoup4`, `pandas`, `pyyaml`
- **Automation:** GitHub Actions (scheduled + manual triggers)
- **Dashboard:** Static HTML + PapaParse (reads CSV directly, no backend needed)

## Project structure