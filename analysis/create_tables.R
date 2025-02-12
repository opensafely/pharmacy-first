library(here)
library(tidyverse)
library(readr)
library(gt)
library(purrr)
library(scales)

# Dataset definition file path output/population/pf_population.csv.gz
df <- read_csv(here("output", "population", "pf_table1.csv.gz"))

df_demographics_table <- df %>%
  select(
    sex,
    age_band,
    region,
    imd,
    ethnicity
  )

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
  mutate(pct = percent(n / sum(n), accuracy = .1))

readr::write_csv(
  df_demographics_table_counts,
  here::here("output", "population", "pf_demographics.csv")
)