# Function to create clinical pathways table

create_clinical_pathways_table <- function() {
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
      title = "Table 1. Pharmacy First population criteria"
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
