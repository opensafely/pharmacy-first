# Check if the script is running in the OpenSAFELY backend environment
# If yes, opensafely data will be loaded from output directory
if (Sys.getenv("OPENSAFELY_BACKEND") != "") {
  # Load data from output directory
  df_measures <- read_csv(
    here("output", "measures", "pf_breakdown_measures.csv")
  )
  df_descriptive_stats <- read_csv(
    here("output", "measures", "pf_descriptive_stats_measures.csv")
  )
  df_pfmed <- read_csv(
    here("output", "measures", "pf_medications_measures_tidy.csv"),
    col_types = list(
      measure = col_character(),
      interval_start = col_date(),
      interval_end = col_date(),
      ratio = col_double(),
      numerator = col_double(),
      denominator = col_double(),
      dmd_code = col_character(),
      pharmacy_first_med = col_logical()
    )
  )
  df_consultation_med_counts <- read_csv(
    here("output", "measures", "pf_medications_measures_tidy.csv"),
    col_types = cols(
      measure = col_character(),
      interval_start = col_date(),
      interval_end = col_date(),
      ratio = col_double(),
      numerator = col_double(),
      denominator = col_double(),
      dmd_code = col_character()
    )
  )
  population_table <- read_csv(here("output", "population", "pf_tables.csv"))

} else {
  # Else (locally), opensafely data will be loaded from released_output directory
  df_measures <- read_csv(
    here("released_output", "measures", "pf_breakdown_measures.csv")
  )
  df_descriptive_stats <- read_csv(
    here("released_output", "measures", "pf_descriptive_stats_measures.csv")
  )
  df_pfmed <- read_csv(
    here("released_output", "measures", "pf_medications_measures_tidy.csv"),
    col_types = list(dmd_code = col_character())
  )
  df_consultation_med_counts <- read_csv(
    here("released_output", "measures", "pf_medications_measures_tidy.csv"),
    col_types = cols(dmd_code = col_character())
  )
  population_table <- read_csv(here("released_output", "population", "pf_tables.csv"))
}

# Clean and standardise the measures dataset:
# - Splits the 'measure' column into summary statistic, measure type, and group
# - Applies human-readable labels from dictionaries
# - Factors key breakdown variables (e.g. age, sex, ethnicity, region) with defined order
df_measures <- tidy_measures(
  data = df_measures,
  pf_measures_name_dict = pf_measures_name_dict,
  pf_measures_name_mapping = pf_measures_name_mapping,
  pf_measures_groupby_dict = pf_measures_groupby_dict
)
