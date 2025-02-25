library(here)
library(tidyverse)
library(readr)
library(purrr)
library(scales)

# Dataset definition file path output/population/pf_population.csv.gz
df_pf_tables <- read_csv(here("output", "population", "pf_tables_dataset.csv.gz"))

df_demographics_table <- df_pf_tables %>%
  select(
    sex,
    age_band,
    region,
    imd,
    ethnicity
  )

df_pf_pathways_table <- df_pf_tables %>%
  select(
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

# Table 1: Demographics
# Count subcategories (e.g. female/male) for each variable/categories (e.g. sex)
# Var names, referred to as .x in code: sex, age_band, region, imd, ethnicity
df_demographics_table_counts <- map_dfr(
  names(df_demographics_table),
  ~ df_demographics_table %>%
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

# Table 2: Clinical pathways
df_pf_pathways_table_long <- df_pf_pathways_table %>%
  pivot_longer(
    cols = all_of(df_pf_pathways_num_den_variables),
    names_to = "pf_pathway_count"
  ) %>%
  filter(value == TRUE)

df_pf_pathways_table_counts_by_sex <- df_pf_pathways_table_long %>%
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
  relocate(table)

df_pf_pathways_table_counts_by_imd <- df_pf_pathways_table_long %>%
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
  relocate(table)

# Combine tables
df_tables_combined <- bind_rows(
  df_demographics_table_counts,
  df_pf_pathways_table_counts_by_sex,
  df_pf_pathways_table_counts_by_imd
)

readr::write_csv(
  df_tables_combined,
  here::here("output", "population", "pf_tables.csv")
)
