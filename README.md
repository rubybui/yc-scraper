# YC Scraper

A multi-agent system for scraping, cleaning, and analyzing Y Combinator startup and founder data. This project aims to build a comprehensive dataset of YC companies and founders, with the ultimate goal of creating founder profiles that can help match engineers to startups based on fit.

## 🎯 Project Goals

**End Goal:** A multi-agent setup that can:
- Scrape YC's startup and founder directory based on English query
- Normalize the data (clean company and founder mapping)
- Crawl founders' public posts (mostly LinkedIn)
- Summarize their "founder profile": what they're proud of, how they think, and what kind of people they'd hire

**Current Phase:** Step 1 - Scraping and Cleaning

## 📋 Overview

YC's public API only returns 1,000 companies by default. To get the full dataset, this scraper:
- Tweaks parameters (offset, batch, filter by industry, etc.)
- Paginates through all available companies
- Queries both company and founder datasets (though they're loosely linked and relationships need to be reconstructed)

## 🏗️ Architecture

### Current Implementation

The scraper uses YC's Algolia search API to fetch company data:
- **Endpoint:** Algolia search API (`45bwzj1sgc-dsn.algolia.net`)
- **Indices:** `YCCompany_production` and `YCCompany_By_Launch_Date_production`
- **Pagination:** Automatically handles pagination to fetch all companies
- **Retry Logic:** Implements exponential backoff for transient failures (HTTP 429/5xx)

### Data Cleaning Strategy

Each company in the YC directory contains many fields. The cleaning process reduces the dataset to essential fields:

**Original Fields:**
```
id, objectID, name, slug, batch, industry, industries, subindustry, regions, 
all_locations, team_size, status, stage, isHiring, top_company, nonprofit, 
website, one_liner, long_description, small_logo_thumb_url, launched_at, 
tags, former_names, _highlightResult, app_answers, app_video_public, 
demo_day_video_public, question_answers, tags_highlighted
```

**Cleaned Fields:**
```
id, objectID, name, slug, batch, industry, industries, subindustry, regions, 
all_locations, team_size, status, stage, isHiring, top_company, nonprofit, 
website, long_description, former_names
```

**Cleaning Rules:**
- ✅ **Keep:** Structural identifiers and signal fields (slug, batch, industry, regions, stage, team_size, status, isHiring)
- ❌ **Drop:** Redundant or presentation-only fields (_highlightResult, tags_highlighted, etc.)
- 🔗 **Build:** Consistent key for linking founders and companies

## 🚀 Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd yc-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

Run the scraper:

```bash
python yc_scraper.py
```

The script will:
1. Fetch all YC companies from the Algolia API
2. Paginate through all available pages
3. Write the results to `yc_companies.csv`

### Output

The scraper generates a CSV file with all fetched company data. The CSV includes:
- Company identifiers (id, objectID, name, slug)
- Batch and industry information
- Location and team size data
- Company status and stage
- Hiring information
- Website and description

## 📊 Data Structure

### Company Fields

| Field | Description |
|-------|-------------|
| `id` | Unique company identifier |
| `objectID` | Algolia object ID |
| `name` | Company name |
| `slug` | URL-friendly company identifier |
| `batch` | YC batch (e.g., "S24", "W23") |
| `industry` | Primary industry |
| `industries` | List of industries |
| `subindustry` | Sub-industry classification |
| `regions` | Geographic regions |
| `all_locations` | All company locations |
| `team_size` | Current team size |
| `status` | Company status |
| `stage` | Funding stage |
| `isHiring` | Whether the company is currently hiring |
| `top_company` | Top company flag |
| `nonprofit` | Nonprofit status |
| `website` | Company website URL |
| `long_description` | Full company description |
| `former_names` | Previous company names |

## 🔮 Future Roadmap

### Phase 2: Founder Data
- Scrape founder directory
- Link founders to companies
- Normalize founder-company relationships

### Phase 3: Public Content Crawling
- Crawl founders' public posts (LinkedIn, Twitter, etc.)
- Extract patterns and insights

### Phase 4: Intelligence Layer
- Build agent to read founders' public content
- Extract patterns about what founders are proud of
- Understand how founders think
- Match engineers to startups based on founder profiles

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📝 Notes

- The scraper respects rate limits and implements retry logic
- Company and founder datasets are loosely linked - relationships need to be reconstructed
- The current implementation focuses on companies; founder scraping is planned for future phases

## 🔗 References

- [LinkedIn Post](https://www.linkedin.com/posts/rubybui99_building-a-yc-scraper-step-1-data-before-activity-7381764951389949953--W6e)
- Y Combinator Directory: https://www.ycombinator.com/companies

## 📄 License

[Add your license here]

