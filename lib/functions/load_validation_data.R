library(readr)
library(tidyr)
library(dplyr)
library(here)

df_bsa_consultation_validation <- read_csv(
  here("lib", "validation", "data", "pf_consultation_validation_data.csv")
) %>%
  rename(count_100pct = count) |>
  mutate(count_40pct = round(as.numeric(count_100pct * .4), digits = 0)) %>%
  mutate(source = "nhs_bsa") |>
  pivot_longer(
    cols = c(count_100pct, count_40pct),
    names_to = "count_method",
    values_to = "count"
  )

df_bsa_consultation_validation <- df_bsa_consultation_validation %>%
  mutate(consultation_type = factor(consultation_type,
    levels = c(
      "sinusitis",
      "infected_insect_bites",
      "uncomplicated_uti",
      "acute_otitis_media",
      "acute_sore_throat",
      "shingles",
      "impetigo"
    ),
    labels = c(
      "Acute Sinusitis",
      "Infected Insect Bite",
      "UTI",
      "Acute Otitis Media",
      "Acute Pharyngitis",
      "Herpes Zoster",
      "Impetigo"
    )
  ))

df_bsa_medication_validation <- read_csv(
  here("lib", "validation", "data", "pf_medication_validation_data.csv")
)
