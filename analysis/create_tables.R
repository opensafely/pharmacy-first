library(here)
library(tidyverse)
library(readr)
library(gt)
library(purrr)

# Dataset definition file path output/population/pf_population.csv.gz
df <- read_csv(here("output", "population", "pf_table1.csv.gz"))

df_demographics <- df %>%
  select(sex, age_band, region, imd, ethnicity)

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
    filter(n > 7) %>%
    mutate(n = (round(n / 5) * 5))
)

View(df_demographics_counts)

readr::write_csv(
  df_demographics_counts,
  here::here("output", "population", "pf_demographics.csv")
)

# gt_table <- df_demographics_counts[1:2] %>%
#   gt() %>%
#   tab_header(
#     title = "Demographics Table",
#     subtitle = "Counts of individuals by category and subcategory"
#   ) %>%
#   tab_row_group(
#     group = "sex",
#     rows = df_counts$Category == "sex"
#   ) %>%
#   tab_row_group(
#     group = "age_band",
#     rows = df_counts$Category == "age_band"
#   ) %>%
#   tab_row_group(
#     group = "region",
#     rows = df_counts$Category == "region"
#   ) %>%
#   tab_row_group(
#     group = "imd",
#     rows = df_counts$Category == "imd"
#   ) %>%
#   tab_row_group(
#     group = "ethnicity",
#     rows = df_counts$Category == "ethnicity"
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
