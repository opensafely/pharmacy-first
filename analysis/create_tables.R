library(here)
library(tidyverse)
library(readr)
library(gt)
library(purrr)

# Dataset definition file path output/population/pf_population.csv.gz
df <- read_csv(here("output", "population", "pf_table1.csv.gz"))

df_demographics <- df %>%
  select(
    sex,
    age_band,
    region,
    imd,
    ethnicity,
    uti_numerator,
    uti_denominator,
    shingles_numerator,
    shingles_denominator,
    impetigo_numerator,
    impetigo_denominator,
    insectbite_numerator,
    insectbite_denominator,
    sorethroat_numerator,
    sorethroat_denominator,
    sinusitis_numerator,
    sinusitis_denominator,
    otitismedia_numerator,
    otitismedia_denominator
  ) %>%
  mutate(across(ends_with(("_numerator")) | ends_with(("_denominator")), as.character))

# map_dfr maps function to each elevent and combines result in single df
df_demographics_counts <- map_dfr(
  # Column names sex, age_band, region, imd, ethnicity are inputs (.x)
  names(df_demographics),
  ~ df_demographics %>%
    # Group by each column
    group_by(across(all_of(.x))) %>%
    # summarises df with a new column which counts occurences (n)
    summarise(n = n()) %>%
    mutate(category = .x) %>%
    rename(subcategory = 1) %>%
    # filter out all FALSES
    filter(across(everything(), ~ . != "FALSE")) %>%
    filter(n > 7) %>%
    mutate(n = round(n / 5) * 5)
)

readr::write_csv(
  df_demographics_counts,
  here::here("output", "population", "pf_demographics.csv")
)

# Demographics table with percentages
df_demographics_table <- head(df_demographics_counts, 39) %>%
  group_by(category) %>%
  mutate(pct = round(n / sum(n) * 100, digits = 1))

# Clinical pathways table with percentages
df_clinical_pathways_table <- tail(df_demographics_counts, 14) %>%
  separate(col=category, into=c("clinical_pathway", "metric"), sep = "_") %>%
  group_by(clinical_pathway) %>%
  mutate(pct = round(n / lead(n) * 100, digits = 1))

# View(df_clinical_pathways_table)
# View(df_demographics_table)

# gt_table <- df_demographics_table %>%
#   gt() %>%
#   tab_header(
#     title = "Demographics Table",
#     subtitle = "Counts of individuals by category and subcategory"
#   ) %>%
#   tab_row_group(
#     label = "sex",
#     rows = df_demographics_table$category == "sex",
#   ) %>%
#   tab_row_group(
#     label = "age_band",
#     rows = df_demographics_table$category == "age_band"
#   ) %>%
#   tab_row_group(
#     label = "region",
#     rows = df_demographics_table$category == "region"
#   ) %>%
#   tab_row_group(
#     label = "imd",
#     rows = df_demographics_table$category == "imd"
#   ) %>%
#   tab_row_group(
#     label = "ethnicity",
#     rows = df_demographics_table$category == "ethnicity"
#   ) %>%
#   tab_options(
#     heading.title.font.size = "medium",
#     heading.subtitle.font.size = "small",
#     table.font.size = "small"
#   ) %>%
#   tab_style(
#     style = cell_text(weight = "bold"),
#     locations = cells_row_groups(groups = everything())
#   )

# # Display the table
# gt_table


# output/population/pf_population.csv.gz
