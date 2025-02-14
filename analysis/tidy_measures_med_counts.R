library(here)
library(tidyverse)
library(readr)
library(gt)
library(purrr)

df_pf_medications_measures <- read_csv(
  here("output", "measures", "pf_medications_measures.csv"),
  col_types = cols(dmd_code = col_character())
)

df_consultation_med_counts_measures <- read_csv(
  here("output", "measures", "consultation_med_counts_measures.csv"),
  col_types = cols(dmd_code = col_character())
)

df_medications <- df_pf_medications_measures %>%
    filter(numerator != 0)

df_consultation_med_counts <- df_consultation_med_counts_measures %>%
    filter(numerator != 0)

readr::write_csv(
  df_medications,
  here::here("output", "measures", "pf_medications_measures_tidy.csv")
)

readr::write_csv(
  df_consultation_med_counts,
  here::here("output", "measures", "consultation_med_counts_measures_tidy.csv")
)