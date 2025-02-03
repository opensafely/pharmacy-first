library(here)
library(tidyverse)
library(readr)
library(gt)
library(purrr)

df <- read_csv(here("released_output", "measures", "pf_medications_measures.csv"))
df1 <- read_csv(here("released_output", "measures", "consultation_med_counts_measures.csv"))

df_medications <- df %>%
    filter(numerator != 0)

df_consultation_med_counts <- df1 %>%
    filter(numerator != 0)

readr::write_csv(
  df_medications,
  here::here("output", "measures", "pf_medications_measures_updated.csv")
)

readr::write_csv(
  df_consultation_med_counts,
  here::here("output", "measures", "consultation_med_counts_measures_updated.csv")
)