# Local Business Radar – Corren RSS → Telegram

## Overview

This project is an **automated local business radar** that monitors regional news coverage for newly created companies and sends real-time notifications to Telegram.

It continuously scans RSS feeds from *Corren* (Östgöta Correspondenten) for articles about **new business establishments**, filters out duplicates, and alerts you as soon as a new company is detected.

The system is designed to be:

* **Fully automated** (cron-friendly)
* **Idempotent** (no duplicate notifications)
* **Low-maintenance** (RSS-based, no scraping)
* **Well suited for lead discovery and local prospecting**

---

## What the script does

1. **Reads multiple local RSS feeds** from Corren (Mjölby, Motala, Boxholm, Vadstena)
2. **Filters articles** to only include business establishment news

   * Matches URLs starting with:

     ```
     https://www.corren.se/naringsliv/nyetableringar/
     ```
3. **Detects new companies** by comparing article GUIDs against previously processed entries
4. **Prevents duplicates** by persisting seen GUIDs to disk
5. **Extracts key information** from each article:

   * Municipality (based on RSS source)
   * Article title
   * Registration sentence (e.g. “Den 23 januari registrerades det nya bolaget … hos Bolagsverket.”)
   * Clickable link to the full article
6. **Sends a formatted Telegram notification** for each newly discovered company

---

## Duplicate protection

The script guarantees that **each company/article is only processed once**.

* Every RSS item has a unique `GUID`
* All processed GUIDs are stored in:

  ```
  seen_guids.txt
  ```
* On subsequent runs:

  * If the GUID already exists → the article is skipped
  * If the GUID is new → the article is processed and stored

This makes the script safe to run:

* multiple times per day
* daily via cron
* long-term without manual cleanup

---

## Output

### Telegram notification

Each new company triggers a Telegram message containing:

* New establishment indicator
* Municipality
* Article title
* Official registration sentence
* Clickable link to the article

This enables **instant awareness of new local businesses**.

---

## Typical use cases

* Local B2B lead discovery
* Early outreach to newly formed companies
* Monitoring entrepreneurial activity in a specific region
* Sales, consulting, accounting, IT, or agency prospecting


---

## Requirements

* Python 3
* `feedparser`
* `requests`
* Telegram Bot Token + Chat ID


---

