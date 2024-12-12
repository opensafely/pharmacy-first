# Load data based on execution environment
if (Sys.getenv("OPENSAFELY_BACKEND") != "") {
  # Load data from generate_pf_measures action
  df_measures <- readr::read_csv(
    here("output", "measures", "pf_codes_conditions_measures.csv")
  )
  df_descriptive_stats <- read_csv(
    here("output", "measures", "pf_descriptive_stats_measures.csv")
  )
  df_pfmed <- read_csv(
    here("output", "measures", "pf_medications_measures.csv")
  )
  df_condition_provider <- read_csv(
    here("output", "measures", "pf_condition_provider_measures.csv")
  )
} else {
  # Load data from released_output directory
  df_measures <- readr::read_csv(
    here("released_output", "measures", "pf_codes_conditions_measures.csv")
  )
  df_descriptive_stats <- read_csv(
    here("released_output", "measures", "pf_descriptive_stats_measures.csv")
  )
  df_pfmed <- read_csv(
    here("released_output", "measures", "pf_medications_measures.csv")
  )
  df_condition_provider <- read_csv(
    here("released_output", "measures", "pf_condition_provider_measures.csv")
  )
}

df_measures <- tidy_measures(
  data = df_measures,
  pf_measures_name_dict = pf_measures_name_dict,
  pf_measures_name_mapping = pf_measures_name_mapping,
  pf_measures_groupby_dict = pf_measures_groupby_dict
)

# str(df_measures$ethnicity)
# str(df_measures$age_band)
# str(df_measures$region)
# str(df_measures$sex)

df_measures$age_band[is.na(df_measures$age_band)] <- "Missing"
