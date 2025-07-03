# Crawl-Pakistan-
# Pakistan Government Text Dataset Project

## Country Selected
Pakistan

## Objective
The objective of this project was to collect a minimum of 1 million words of clean, English language text data from official Pakistani government websites (specifically .gov domains) and produce a formatted dataset in a single .txt file with one paragraph per line. The data required to include policies, reports, educational materials, public announcements, or manuals, while excluding news articles from non-government sources, blogs, private sector websites, or copyrighted materials not in the public domain. This report details the data collection, cleaning processes (including binary noise removal), and the final dataset.

## Data Sources
The following official government websites were scraped for data collection:
1. **https://fabs.gov.pk/**  
   The Financial Accounting and Budgeting System (FABS) website provides financial and budgetary policies, public financial management reports, procedural manuals, and guidelines for fiscal operations, including annual financial statements and budget execution reports.
2. **https://www.finance.gov.pk/**  
   The Ministry of Finance’s official website serves as a repository for economic policies, fiscal announcements, annual budget reports, and public financial management guidelines, including economic surveys, budget speeches, and fiscal policy statements.
3. **http://www.pbs.gov.pk/**  
   The Pakistan Bureau of Statistics (PBS) website offers statistical reports, survey data, and educational materials on demographic, economic, and social indicators, including national census reports, labor force surveys, and statistical yearbooks.

## Subdomains and URLs Scraped
- **Pakistan Bureau of Statistics (PBS):**
  - http://www.pbs.gov.pk/node/1110: Policy and service descriptions.
  - http://www.pbs.gov.pk/content/field-services: Field service guidelines.
  - http://www.pbs.gov.pk/contacts: Contact information for statistical services.
  - http://www.pbs.gov.pk/contact/deputy-census-commissioner-g: Census commissioner details.
  - http://www.pbs.gov.pk/content/price-statistics: Price statistics reports.
  - http://www.pbs.gov.pk/content/foreign-training-workshop-seminar: Training and seminar details.
  - http://www.pbs.gov.pk/content/faqs: Frequently asked questions on statistics.
  - http://www.pbs.gov.pk/form/data-information-request-form: Data request forms.
  - http://www.pbs.gov.pk/content/national-health-accounts: Health accounts data.
- **Ministry of Finance:**
  - **Budget-related:** https://www.finance.gov.pk/budget/spf_gr2025_28032025.pdf, https://www.finance.gov.pk/budget/Budget_Call_Circular_2021_22.pdf, and others (budget circulars, fiscal policies, debt policies).
  - **Notifications:** https://www.finance.gov.pk/notifications/PF_5_799_11032025.pdf, https://www.finance.gov.pk/notifications/OO_24032025_1.pdf, and others (policy notifications, fiscal updates).
  - **Poverty:** https://www.finance.gov.pk/poverty/training_11012024_2.pdf, https://www.finance.gov.pk/poverty/training_30012025.pdf, and others (training materials for poverty alleviation).
  - **Surveys:** https://www.finance.gov.pk/survey/chapters_21/02-Agriculture.pdf, https://www.finance.gov.pk/survey/chapters_21/09-Public debt.pdf, and others (economic survey chapters).
  - **Economic Updates:** https://www.finance.gov.pk/economic/economic_update_July_2023.pdf, https://www.finance.gov.pk/economic/economic_update_March_2024.pdf, and others.
  - **Publications:** https://www.finance.gov.pk/publications/SOEs_Policy_Report_2023.pdf, https://www.finance.gov.pk/publications/Federal_Footprint_SOEs_Consolidated_Report_FY2020_22.pdf, and others.
- **Financial Accounting and Budgeting System (FABS):**
  - **Downloads:** https://fabs.gov.pk/downloads/User Manual-Online Billing Solution ver 2.0 November 2022.pdf, https://fabs.gov.pk/downloads/AGPR's User Manual-Punching of AAA Schedules.pdf, and others (user manuals, procurement plans, accounting guidelines).
  - **Other:** https://fabs.gov.pk/GOP.html (government financial policies).

## Data Collection
- Employed Python-based web crawler (BeautifulSoup) to extract English text from websites and PDFs.
- Targeted policies, reports, manuals, and statistical data; excluded news, blogs, and non-government content.
- Processed PDFs using PyPDF2 and OCR (Tesseract) for scanned documents.

## Data Cleaning
- **General Cleaning:** Removed duplicates, normalized text to UTF-8, filtered non-English content, and formatted one paragraph per line.
- **Binary Noise Cleaning:**
  - Input: pakistan_dataset_cleaned.txt (876 paragraphs, 1,101,298 words).
  - Removed: 4 binary paragraphs (9,513 words).
  - Output: pakistan_dataset_binary_cleaned.txt (872 paragraphs, 1,091,785 words).
- Ensured clean, readable text with minimal noise.

## Dataset Summary
- Word Count: 1,091,785
- Paragraphs: 872
- File: pakistan_dataset_binary_cleaned.txt (one paragraph per line, ~7-8 MB).
- Content: Financial policies, budget reports, statistical data, and training materials from government sources.

## Challenges and Solutions
- **Scanned PDFs:** Applied OCR for text extraction.
- **Duplicate text:** Used deduplication algorithms.
- **Binary noise:** Removed 9,513 words of corrupted data.
- **Formatting:** Scripted one-paragraph-per-line structure.

## Conclusion
The data collection and cleaning process successfully produced a high-quality dataset of 1,091,785 words across 872 paragraphs, sourced exclusively from official Pakistani government websites. The data set meets all project requirements, including source restrictions, content type, language, and formatting (one paragraph per line). The binary noise cleaning step effectively removed 9,513 words of corrupted data, ensuring the final .txt file (pakistan_dataset.txt) is clean, well-structured, and ready for further analysis or use in subsequent project phases.
