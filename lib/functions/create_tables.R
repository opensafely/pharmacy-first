# Function to create clinical pathways table
create_clinical_pathways_table <- function(title) {
  data <- tibble(
    Condition = c(
      "Uncomplicated Urinary Tract Infection",
      "Shingles",
      "Impetigo",
      "Infected Insect Bites",
      "Acute Sore Throat",
      "Acute Sinusitis",
      "Acute Otitis Media"
    ),
    Age = c(
      "16 to 64 years",
      "18 years and over",
      "1 year and over",
      "1 year and over",
      "5 years and over",
      "12 years and over",
      "1 to 17 years"
    ),
    Sex = c(
      "Female",
      "Any",
      "Any",
      "Any",
      "Any",
      "Any",
      "Any"
    ),
    Exclusions = c(
      "Pregnant individuals, urinary catheter, recurrent UTI (2 episodes in last 6 months, or 3 episodes in last 12 months)",
      "Pregnant individuals",
      "Bullous impetigo, recurrent impetigo (2 or more episodes in the same year), pregnant individuals under 16 years",
      "Pregnant individuals under 16 years",
      "Pregnant individuals under 16 years",
      "Immunosuppressed individuals, chronic sinusitis (symptoms lasting more than 12 weeks), pregnant individuals under 16 years",
      "Recurrent acute otitis media (3 or more episodes in 6 months or four or more episodes in 12 months), pregnant individuals under 16 years"
    )
  )

  data %>%
    gt() %>%
    tab_header(
      title = title
      # subtitle = "Inclusion and exclusion criteria for clinical pathway/conditions"
    ) %>%
    cols_label(
      Condition = "Condition",
      Age = "Age Range",
      Sex = "Sex",
      Exclusions = "Exclusions"
    ) %>%
    tab_options(
      table.font.size = "medium",
      heading.title.font.size = "large",
      heading.subtitle.font.size = "small"
    ) %>%
    tab_style(
      style = cell_text(weight = "bold"),
      locations = cells_column_labels(columns = everything())
    )
}

# Function to create pharmacy first service codes table
create_pf_service_codes_table <- function(title) {
  data <- tibble(
    codelist = c(
      "Community Pharmacist (CP) Consultation Service for minor illness (procedure)",
      "Pharmacy First service (qualifier value)"
    ),
    code = c(
      "1577041000000109",
      "983341000000102"
    )
  )

  data %>%
    gt() %>%
    tab_header(
      title = title,
      # subtitle = "Codelist descriptions and their respective SNOMED codes"
    ) %>%
    cols_label(
      codelist = md("**Codelist Description**"),
      code = md("**SNOMED Code**")
    ) %>%
    tab_options(
      table.font.size = "medium",
      heading.title.font.size = "large",
      heading.subtitle.font.size = "small"
    )
}

create_clinical_conditions_codes_table <- function(title) {
  data <- tibble(
    condition = c(
      "Acute otitis media",
      "Herpes zoster",
      "Acute sinusitis",
      "Impetigo",
      "Infected insect bite",
      "Acute pharyngitis",
      "Uncomplicated urinary tract infection"
    ),
    code = c(
      "3110003",
      "4740000",
      "15805002",
      "48277006",
      "262550002",
      "363746003",
      "1090711000000102"
    )
  )
  data %>%
    gt() %>%
    tab_header(
      title = title
      # subtitle = "Clinical conditions and their corresponding SNOMED codes"
    ) %>%
    cols_label(
      condition = md("**Clinical Condition**"),
      code = md("**SNOMED Code**")
    ) %>%
    tab_options(
      table.font.size = "medium",
      heading.title.font.size = "large",
      heading.subtitle.font.size = "small"
    )
}

#  Create top 5 table grouped by pharmacy_first_med status
#  Data needs to have the following columns:
#  pharmacy_first_med
#  term
#  count
#  ratio_by_group
gt_top_meds <- function(data) {
  data |>
    gt(
      groupname_col = "pharmacy_first_med",
      rowname_col = "term"
    ) %>%
    tab_header(
      title = "Top 5 medications linked to Pharmacy First consultations",
      subtitle = "Timeframe: 1st Feb 2024 to 31st July 2024"
    ) %>%
    cols_label(
      term = md("**Medication**"),
      count = md("**Count**"),
      ratio_by_group = md("**%**")
    ) %>%
    fmt_number(
      columns = count,
      decimals = 0
    ) %>%
    fmt_percent(
      columns = ratio_by_group,
      decimals = 1
    ) %>%
    tab_style(
      style = cell_text(weight = "bold"),
      locations = cells_row_groups(groups = everything())
    ) %>%
    tab_stub_indent(
      rows = everything(),
      indent = 3
    )
}