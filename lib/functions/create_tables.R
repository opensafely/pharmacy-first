# Create a formatted demographics dataset for Table 1.
# Checks for expected row count, reshapes the data, standardises labels,
# and applies a custom ordering.
generate_demographics_dataset <- function(population_table) {
  if (nrow(population_table) < 216) {
    print("Table 1 cannot be generated with current dummy data")
    return(NULL)
  } else if (nrow(population_table) == 216) {
    population_table_demo <- population_table %>% 
      pivot_wider(names_from = "population", values_from = "value")

    df_demographics_table <- population_table_demo %>%
      filter(table == "tab_demographics") %>%
      pivot_wider(names_from = metric, values_from = c(pharmacy_first, tpp)) %>%
      select(-table) %>%
      mutate(category = factor(category,
        levels = c("sex", "age_band", "ethnicity", "imd", "region"),
        labels = c("Sex", "Age Band", "Ethnicity", "IMD", "Region")
      )) %>%
      mutate(
        subcategory = recode(subcategory,
          "female" = "Female",
          "male" = "Male",
          "Other South Asian" = "Any other Asian background",
          "Other Black" = "Any other Black background",
          "Other Mixed" = "Any other mixed background",
          "All other ethnic groups" = "Any other ethnic group",
          "Other White" = "Any other White background"
        )
      ) %>%
      mutate(order = c(1:23, 28, 36, 24, 29, 35, 25, 40, 30, 34, 27, 39, 26, 37, 38, 32, 31, 33)) %>%
      arrange(order) %>%
      select(-order)

    return(df_demographics_table)
  } else {
    print("Unexpected number of rows in population_table")
    return(NULL)
  }
}

# Generate a gt table of Pharmacy First and TPP demographics.
# Applies groupings, labels, formatting, and styling to the dataset
# prepared by generate_demographics_dataset().
gt_demographics <- function(data, title = NULL, subtitle = NULL) {
  data |>
    gt(
      groupname_col = "category",
      rowname_col = "subcategory"
    ) %>%
    tab_header(
      title = title,
      subtitle = subtitle
    ) %>%
    cols_label(
      subcategory = md("**Medication**"),
      pharmacy_first_n = md("**Count**"),
      pharmacy_first_pct = md("**%**"),
      tpp_n = md("**Count**"),
      tpp_pct = md("**%**")
    ) %>%
    tab_spanner(
      label = md("**Pharmacy First**"),
      columns = c(pharmacy_first_n, pharmacy_first_pct)
    ) %>%
    tab_spanner(
      label = md("**OpenSAFELY-TPP**"),
      columns = c(tpp_n, tpp_pct)
    ) %>%
    fmt_number(
      columns = c(pharmacy_first_n, tpp_n),
      decimals = 0
    ) %>%
    fmt_percent(
      columns = c(pharmacy_first_pct, tpp_pct),
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

# Create a labelled dataset with counts for three different Pharmacy First
# consultation codes, along with their total.
# Outputs both the individual breakdowns and combined total, reshaped for plotting.
generate_pf_consultation_counts <- function(df_measures) {
  df_pf_consultations <- df_measures |>
    filter(measure_desc == "clinical_service") |>
    filter(is.na(group_by)) |>
    select(measure, interval_start, numerator) |>
    mutate(measure = factor(measure,
      levels = c(
        "Consultation Service",
        "Pharmacy First Consultation",
        "Community Pharmacy First Service"
      ),
      labels = c(
        "CP Consultation Service for minor illness (1577041000000109)",
        "Pharmacy First service (983341000000102)",
        "CP Pharmacy First Service (2129921000000100)"
      )
    )) |>
    group_by(interval_start) |>
    mutate(
      pf_consultation_total = sum(numerator, na.rm = TRUE),
      data_desc = "Pharmacy First Consultation"
    ) |>
    rename(pf_code = measure) |>
    filter(interval_start >= "2024-02-01") |>
    ungroup() |>
    pivot_longer(
      cols = c(numerator, pf_consultation_total),
      names_to = "measure"
    ) |>
    mutate(
      measure = case_when(
        measure == "pf_consultation_total" ~ "Pharmacy First Service Total",
        measure == "numerator" ~ pf_code
      ),
      data_desc = case_when(
        measure == "Pharmacy First Service Total" ~ "total",
        measure %in% c(
          "CP Consultation Service for minor illness (1577041000000109)",
          "Pharmacy First service (983341000000102)",
          "CP Pharmacy First Service (2129921000000100)"
        ) ~ "breakdown"
      ),
      measure = factor(measure,
        levels = c(
          "Pharmacy First Service Total",
          "CP Consultation Service for minor illness (1577041000000109)",
          "Pharmacy First service (983341000000102)",
          "CP Pharmacy First Service (2129921000000100)"
        )
      ),
      data_desc = factor(data_desc,
        levels = c("total", "breakdown"),
        labels = c("Total", "Breakdown")
      )
    ) |>
    select(measure, interval_start, data_desc, value)

  return(df_pf_consultations)
}

# Create a labelled dataset with counts for three different Pharmacy First
# consultation codes, along with their total.
# Outputs both the individual breakdowns and combined total, reshaped for plotting.
generate_pf_consultation_counts_extended <- function(df_measures, report_date) {
  df_pf_consultations <- df_measures |>
    filter(measure_desc == "clinical_service") |>
    filter(is.na(group_by)) |>
    select(measure, interval_start, numerator) |>
    mutate(measure = factor(measure,
      levels = c(
        "Consultation Service",
        "Pharmacy First Consultation",
        "Community Pharmacy First Service"
      ),
      labels = c(
        "CP Consultation Service for minor illness (1577041000000109)",
        "Pharmacy First service (983341000000102)",
        "CP Pharmacy First Service (2129921000000100)"
      )
    )) |>
    group_by(interval_start) |>
    mutate(
      pf_consultation_total = sum(numerator, na.rm = TRUE),
      data_desc = "Pharmacy First Consultation"
    ) |>
    rename(pf_code = measure) |>
    filter(interval_start <= report_date) |>
    ungroup() |>
    pivot_longer(
      cols = c(numerator, pf_consultation_total),
      names_to = "measure"
    ) |>
    mutate(
      measure = case_when(
        measure == "pf_consultation_total" ~ "Pharmacy First Service Total",
        measure == "numerator" ~ pf_code
      ),
      data_desc = case_when(
        measure == "Pharmacy First Service Total" ~ "total",
        measure %in% c(
          "CP Consultation Service for minor illness (1577041000000109)",
          "Pharmacy First service (983341000000102)",
          "CP Pharmacy First Service (2129921000000100)"
        ) ~ "breakdown"
      ),
      measure = factor(measure,
        levels = c(
          "Pharmacy First Service Total",
          "CP Consultation Service for minor illness (1577041000000109)",
          "Pharmacy First service (983341000000102)",
          "CP Pharmacy First Service (2129921000000100)"
        )
      ),
      data_desc = factor(data_desc,
        levels = c("total", "breakdown"),
        labels = c("Total", "Breakdown")
      )
    ) |>
    select(measure, interval_start, data_desc, value)

  return(df_pf_consultations)
}

# Create a dataset for plotting Figure 3 showing linkage between consultations and
# medications, conditions, or both.
# Joins total consultations, calculates exclusive linkage ratios, and
# positions label data for plotting stacked bar chart proportions.
generate_linkage_dataset <- function(df_descriptive_stats, df_pf_consultations, report_date=as.Date("2025-01-31")) {
  df_pf_descriptive_stats <- df_descriptive_stats %>%
    filter(measure %in% c("pfmed_with_pfid", "pfcondition_with_pfid", "pfmed_and_pfcondition_with_pfid")) %>%
    mutate(
      measure = factor(measure,
        levels = c(
          "pfmed_with_pfid",
          "pfcondition_with_pfid",
          "pfmed_and_pfcondition_with_pfid"
        ),
        labels = c(
          "Medication",
          "Clinical condition",
          "Both"
        )
      )
    ) 
    df_pf_consultation_total <- df_pf_consultations %>% 
      filter(data_desc == "Total") %>% 
      distinct() %>% 
      select(-measure)

    df_pf_descriptive_stats <- df_pf_descriptive_stats %>%
    left_join(df_pf_consultation_total,
      by = c("interval_start")
    )

  # Set positions in graph for figure 3 percentage labels
  df_pf_descriptive_stats <- df_pf_descriptive_stats %>%
    filter(between(interval_start, as.Date("2024-02-01"), report_date)) %>%
    group_by(interval_start) %>%
    mutate(measure = factor(measure, levels = c("Both", "Clinical condition", "Medication"))) |>
    arrange(desc(measure), .by_group = TRUE) |>
    mutate(
      ratio_exclusive = numerator / value,
      cumulative_ratio_exclusive = case_when(interval_start == max(df_pf_descriptive_stats$interval_start) ~ cumsum(ratio_exclusive), TRUE ~ NA)
    )

  return(df_pf_descriptive_stats)
}

# Produce a dataset showing the sex breakdown for each clinical condition
# for use in a conditions summary table (table 2)
# Only runs if the population table contains the expected 216 rows.
generate_clinical_conditions_dataset <- function(population_table) {
  if (nrow(population_table) < 216) {
    print("Table cannot be generated with current dummy data")
    return(NULL)
  } else if (nrow(population_table) == 216) {
    population_table <- population_table %>%
    filter(population == "pharmacy_first")
    df_clinical_pathways_by_sex <- population_table %>%
    filter(table == "tab_pf_pathways_by_sex") %>%
    pivot_wider(names_from = metric, values_from = value) %>%
    select(-table) %>%
    pivot_wider(names_from = category, values_from = numerator) %>%
    group_by(subcategory) %>%
    mutate(total = female + male) %>%
    ungroup() %>%
    mutate(
      pct = total / sum(total),
      subcategory = factor(subcategory,
        levels = c(
          "otitismedia",
          "impetigo",
          "insectbite",
          "shingles",
          "sinusitis",
          "sorethroat",
          "uti"
        ),
        labels = c(
          "Acute otitis media",
          "Impetigo",
          "Infected insect bites",
          "Herpes zoster",
          "Acute sinusitis",
          "Acute pharyngitis",
          "Uncomplicated UTI"
        )
      )
    ) %>% 
    arrange(subcategory) %>% 
    select(-population)

    return(df_clinical_pathways_by_sex)
  } else {
    print("Unexpected number of rows in population_table")
    return(NULL)
  }
}

# Create a formatted gt table of clinical condition pathways by sex.
# Uses data prepared by generate_clinical_conditions_dataset().
gt_pathways <- function(data, title = NULL, subtitle = NULL) {
  data |>
    gt(
      rowname_col = "subcategory"
    ) %>%
    tab_header(
      title = NULL,
      subtitle = NULL
    ) %>%
    cols_label(
      subcategory = md("**Medication**"),
      female = md("Female"),
      male = md("Male"),
      total = md("**Total**"),
      pct = md("**%**")
    ) %>%
    fmt_number(
      columns = female,
      decimals = 0
    ) %>%
    fmt_number(
      columns = male,
      decimals = 0
    ) %>%
    fmt_number(
      columns = total,
      decimals = 0
    ) %>%
    fmt_percent(
      columns = pct,
      decimals = 1
    ) %>%
    tab_style(
      style = cell_text(weight = "bold"),
      locations = cells_row_groups(groups = everything())
    ) %>%
  tab_spanner(
    label = "Sex",
    columns = c(female, male)
  ) %>%
  cols_align(align = "left", columns = subcategory)
}

# Create a top 10 medications dataset, grouped by whether medications
# are included in the Pharmacy First codelist or not.
# Joins to a VMP/VTM lookup.
generate_meds_dataset <- function(df_consultation_med_counts, report_date=as.Date("2025-01-31")) {
  vmp_lookup <- read_csv(
    here("lib", "reference", "vmp_vtm_lookup.csv"),
    col_types = cols(id = col_character())
  ) %>%
    rename(code = id)

  df_pf_med_counts <- df_consultation_med_counts |>
    filter(interval_start <= report_date) |>
    select(numerator, code = dmd_code, pharmacy_first_med) |>
    left_join(vmp_lookup, by = "code") |>
    filter(numerator > 0) |>
    select(-code) %>%
    group_by(pharmacy_first_med, vmp_nm) |>
    summarise(count = sum(numerator, na.rm = TRUE)) |>
    filter(!is.na(vmp_nm)) %>%
    ungroup() |>
    group_by(pharmacy_first_med) |>
    mutate(ratio_by_group = count / sum(count, na.na.rm = TRUE)) |>
    slice_max(order_by = ratio_by_group, n = 10) |>
    ungroup()

  df_pf_and_non_pf_med_counts <- df_pf_med_counts %>%
    arrange(!pharmacy_first_med) %>%
    mutate(pharmacy_first_med = factor(pharmacy_first_med,
      levels = c(FALSE, TRUE),
      labels = c(("Medication not included in codelists"), "Medication included in codelists")
    )) %>%
    group_by(pharmacy_first_med) %>% 
    filter(pharmacy_first_med == "Medication included in codelists")

  return(df_pf_and_non_pf_med_counts)
}

#  Create top 10 table grouped by pharmacy_first_med status
#  Data needs to have the following columns:
#  pharmacy_first_med
#  term
#  count
#  ratio_by_group
gt_top_meds <- function(data) {
  data |>
    gt(
      groupname_col = "pharmacy_first_med",
      rowname_col = "vmp_nm"
    ) %>%
    cols_label(
      vmp_nm = md("**Medication**"),
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