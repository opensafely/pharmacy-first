# Pharmacy First

## Overview

The COVID-19 pandemic has caused a significant backlog in hospital care, which has in turn contributed to an unprecedented increase in demand for GP appointments. In response, NHS England announced the [“Delivery plan for recovering access to primary care”](https://www.england.nhs.uk/publication/delivery-plan-for-recovering-access-to-primary-care/). A key element is the [Pharmacy First service](https://www.england.nhs.uk/primary-care/pharmacy/pharmacy-services/pharmacy-first/), which incorporates urgent supply of repeat medication, consultation for minor illnesses, and a clinical pathways service to assess for and manage seven common conditions, including supplying prescription-only medicines where appropriate. The plan also includes an expansion of the contraception and hypertension case-finding services. These services all aim to enable patients to access care in quicker and more convenient ways where otherwise this may have been more difficult or delayed due to the impacts of the pandemic.

We plan to investigate the information sent from community pharmacies to patients' GP records following a consultation under the above services to describe how the services are utilised. Our findings will help us understand how the new services are helping patients to access care, particularly in light of the increased strain on GP appointments caused by the pandemic.

We also plan to assess the possibility of linking additional datasets to OpenSAFELY to assess the potential impacts of the scheme on antimicrobial resistance (where bacteria develop ways to resist the drugs designed to kill them) and over the counter medicine sales (medicines available to buy without prescription).

[View on OpenSAFELY](https://jobs.opensafely.org/repo/https%253A%252F%252Fgithub.com%252Fopensafely%252Fpharmacy-first)

Details of the purpose and any published outputs from this project can be found at the link above.

The contents of this repository MUST NOT be considered an accurate or valid representation of the study or its purpose. 
This repository may reflect an incomplete or incorrect analysis with no further ongoing work.
The content has ONLY been made public to support the OpenSAFELY [open science and transparency principles](https://www.opensafely.org/about/#contributing-to-best-practice-around-open-science) and to support the sharing of re-usable code for other subsequent users.
No clinical, policy or safety conclusions must be drawn from the contents of this repository.

## Repository Structure

```
├── analysis/               # Study and measures definitions and analyses
├── codelists/              # Clinical code lists
├── docs/                   # Project-level documentation
├── dummy_data/             # Dummy data for local development and testing
├── dummy_tables/           # Dummy tables for local development and testing
├── lib/                    # Library with shared functions for data manipulations and plotting
├── logs/                   # Logs of actions, excluded via .gitignore
├── output/                 # Analysis outputs, excluded via .gitignore
├── renv/                   # R environment management, excluded via .gitignore
├── reports/                # RMarkdown scripts for tables/reports
├── project.yaml            # Study definition file for OpenSAFELY framework
```

## Overview of ehrQL and analysis scripts

- `analysis/codelists.py`: Loads relevant codelists from the `codelists/` folder and assigns labels to SNOMED codes.
- `analysis/config.py`: Contains centralised start dates and interval settings for dataset and measure scripts across the project.
- `analysis/create_tables.R`: Script which uses the output produced by `dataset_definition_tables.py` to generate a demographics table and clinical conditions tables (by sex and IMD).
- `analysis/dataset_definition_tables.py`: Defines the study population and variables to generate demographics of the population.
- `analysis/measures_definition_pf_breakdown.py`: Specifies OpenSAFELY measures for overall Pharmacy First consultation counts and Pharmacy First consultation counts by pharmacy first condition.
- `analysis/measures_definition_pf_condition_provider.py`: Tracks prescribing activity by provider (GP vs OpenSAFELY) and condition.
- `analysis/measures_definition_pf_descriptive_stats.py`: Generates descriptive statistics for the study population, including completeness of Pharmacy First consultations.
- `analysis/measures_definition_pf_med_counts.py`: Defines measures to calculate medication-specific prescribing counts under the Pharmacy First service.
- `analysis/pf_dataset.py`: Contains functions which are called in `dataset_definition_tables.py` that allows for variables such as IMD, ethnicity and age band to be retrieved.
- `analysis/pf_variables_library.py`: Contains reusable event selection and filtering functions to build variables dynamically in other scripts.
- `test_dataset_definition_tables.py`: Unit tests for checking table generation logic and structure.
- `analysis/tidy_measures_med_counts.R`: R script to process and tidy the output of `measures_definition_pf_med_counts.py` for reporting.
- For technical reasons the side by side comparison between OpenSAFELY-TPP and NHS BSA counts are available at https://github.com/bennettoxford/pharmacy-first-nhs-bsa-comparison

## Reusable functions for creating results

- `create_tables.R`: Contains functions to generate formatted tables for `create_results_manuscript.Rmd` and `pharmacy_first_report.Rmd`.
- `load_opensafely_outputs.R`: Loads and parses output files generated by OpenSAFELY for analysis, using outputs from either the `/output` directory or `/released_output` directory (both in .gitignore).
- `plot_measures.R`: Contains graphing function.
- `tidy_measures.R`: Cleans and standardises OpenSAFELY measure files to long format suitable for visualisation, and adds labels for measure names.

## RMarkdown reports

- `reports/pharmacy_first_report.Rmd`: R Markdown file to create Pharmacy First first year dashboard.
- `reports/pharmacy_first_monthly_report.Rmd`: R Markdown file to create Pharmacy First monthly dashboard.
- `reports/create_results_manuscript.Rmd`: Compiles main manuscript results in publication-ready format.


# About the OpenSAFELY framework

The OpenSAFELY framework is a Trusted Research Environment (TRE) for electronic
health records research in the NHS, with a focus on public accountability and
research quality.

Read more at [OpenSAFELY.org](https://opensafely.org).

# Licences
As standard, research projects have a MIT license. 

NHS BSA data of Pharmacy First consultations on a national and regional level is retrieved via their API ([link](https://www.nhsbsa.nhs.uk/prescription-data/dispensing-data/dispensing-contractors-data)), which is made available under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

