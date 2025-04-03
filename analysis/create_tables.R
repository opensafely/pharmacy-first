library(here)
library(tidyverse)
library(readr)
library(purrr)
library(scales)

# Dataset definition file path output/population/pf_population.csv.gz
df_pf_tab <- read_csv(here("output", "population", "pf_tables.csv.gz"))

df_demographics_table <- df_pf_tab %>%
  select(
    has_pf_consultation,
    sex,
    age_band,
    region,
    imd,
    ethnicity
  )

df_pf_pathways_tab <- df_pf_tab %>%
  filter(has_pf_consultation == TRUE) %>%
  select(
    -has_pf_consultation,
    sex,
    region,
    imd,
    uti_numerator,
    shingles_numerator,
    impetigo_numerator,
    insectbite_numerator,
    sorethroat_numerator,
    sinusitis_numerator,
    otitismedia_numerator,
  )

df_pf_pathways_breakdown_variables <- c(
  "sex",
  "region",
  "imd"
)

df_pf_pathways_num_den_variables <- c(
  "uti_numerator",
  "shingles_numerator",
  "impetigo_numerator",
  "insectbite_numerator",
  "sorethroat_numerator",
  "sinusitis_numerator",
  "otitismedia_numerator"
)

# Define function to calculate demographics table counts
# Count subcategories (e.g. female/male) for each variable/categories (e.g. sex)
# Var names, referred to as .x in code: sex, age_band, region, imd, ethnicity
get_demographics_table <- function(df) {
  map_dfr(
    names(df),
    ~ df %>%
      group_by(across(all_of(.x))) %>%
      summarise(n = n()) %>%
      mutate(category = .x) %>%
      rename(subcategory = 1)
  ) %>%
    filter(n > 7) %>%
    mutate(n = round(n / 5) * 5) %>%
    select(category, subcategory, n) %>%
    replace_na(list(subcategory = "Missing")) %>%
    group_by(category) %>%
    mutate(
      pct = round(n / sum(n), 4),
      table = "tab_demographics"
    ) %>%
    ungroup() %>%
    pivot_longer(
      cols = c(n, pct),
      names_to = "metric"
    ) %>%
    relocate(table)
}

# Table 1: Demographics table
df_demo_tab_counts_pf <- df_demographics_table %>%
  filter(has_pf_consultation == TRUE) %>%
  select(-has_pf_consultation) %>%
  get_demographics_table() %>%
  mutate(population = "pharmacy_first") %>%
  relocate(table, population)

df_demo_tab_counts_tpp <- df_demographics_table %>%
  select(-has_pf_consultation) %>%
  get_demographics_table() %>%
  mutate(population = "tpp") %>%
  relocate(table, population)

# Table 2: Clinical pathways
df_pf_pathways_tab_long <- df_pf_pathways_tab %>%
  pivot_longer(
    cols = all_of(df_pf_pathways_num_den_variables),
    names_to = "pf_pathway_count"
  ) %>%
  filter(value == TRUE)

df_pf_pathways_tab_counts_by_sex <- df_pf_pathways_tab_long %>%
  group_by(sex, pf_pathway_count) %>%
  count(value) %>%
  ungroup() %>%
  select(category = sex, subcategory = pf_pathway_count, n) %>%
  filter(n > 7) %>%
  mutate(n = round(n / 5) * 5) %>%
  select(category, subcategory, n) %>%
  separate(
    col = subcategory,
    into = c("subcategory", "metric"),
    sep = "_"
  ) %>%
  pivot_wider(
    id_cols = c("category", "subcategory"),
    names_from = metric,
    values_from = n
  ) %>%
  mutate(
    table = "tab_pf_pathways_by_sex"
  ) %>%
  pivot_longer(
    cols = numerator,
    names_to = "metric"
  ) %>%
  mutate(population = "pharmacy_first") %>%
  relocate(table, population)

df_pf_pathways_tab_counts_by_imd <- df_pf_pathways_tab_long %>%
  group_by(imd, pf_pathway_count) %>%
  count(value) %>%
  ungroup() %>%
  select(category = imd, subcategory = pf_pathway_count, n) %>%
  filter(n > 7) %>%
  mutate(n = round(n / 5) * 5) %>%
  select(category, subcategory, n) %>%
  separate(
    col = subcategory,
    into = c("subcategory", "metric"),
    sep = "_"
  ) %>%
  pivot_wider(
    id_cols = c("category", "subcategory"),
    names_from = metric,
    values_from = n
  ) %>%
  mutate(
    table = "tab_pf_pathways_by_imd"
  ) %>%
  pivot_longer(
    cols = numerator,
    names_to = "metric"
  ) %>%
  mutate(population = "pharmacy_first") %>%
  relocate(table, population)

# Combine tables
df_tabs_combined <- bind_rows(
  df_demo_tab_counts_pf,
  df_demo_tab_counts_tpp,
  df_pf_pathways_tab_counts_by_sex,
  df_pf_pathways_tab_counts_by_imd
)

readr::write_csv(
  df_tabs_combined,
  here::here("output", "population", "pf_tables.csv")
)
