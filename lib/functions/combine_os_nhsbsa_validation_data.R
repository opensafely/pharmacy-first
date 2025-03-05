# Load NHS BSA validation data and summarise total count by:
# 1. pf_consultation
# 2. pf_medication
df_bsa_validation_total <- df_bsa_validation |>
  group_by(date, data_desc, count_method) |>
  mutate(count_total = sum(count, na.rm = TRUE)) |>
  select(-count_group, -count) |>
  distinct() %>%
  ungroup() %>%
  filter(count_method == "count_100pct")

# Transform OpenSAFLEY data into same format as NHS BSA validation data
# 1. pf_consultation from:
# 1.1. clinical condition (not every PF consult. has a linked clin. condition)
df_os_consultation_from_condition_validation <- df_measures %>%
  filter(measure_desc == "clinical_condition") %>%
  filter(is.na(group_by)) %>%
  select(
    date = interval_start,
    count_group = measure,
    count = numerator
  ) %>%
  mutate(
    data_source = "opensafely",
    data_desc = "pf_consultation",
    count_desc = "consultation_type",
    count_method = "opensafely_tpp",
  ) |>
  filter(date >= "2024-02-01") %>%
  relocate(
    date, data_source, data_desc,
    count_desc, count_group, count_method, count
  )

# 1.1. consultation id (better description of total PF consult. in OS)
df_os_consultation_from_id_validation <- df_pf_consultations_total |>
  mutate(
    data_source = "opensafely",
    data_desc = "pf_consultation",
    count_desc = "consultation_id",
    count_group = "consultation_id",
    count_method = "opensafely_tpp"
  ) |>
  select(
    date = interval_start,
    data_source, data_desc, count_desc, count_group, count_method,
    count = pf_consultation_total
  )

# 2. pf_medication from linked medication
df_os_medication_validation <- df_pfmed %>%
  rename(date = interval_start) %>%
  mutate(
    count = numerator,
    data_source = "opensafely",
    data_desc = "pf_medication",
    count_desc = "dmd_code",
    count_method = "opensafely_tpp",
    count_group = dmd_code,
  ) |>
  filter(date >= "2024-02-01") %>%
  select(
    date, data_source, data_desc,
    count_desc, count_group, count_method, count
  )

df_os_validation_total <- bind_rows(
  df_os_consultation_from_condition_validation,
  df_os_consultation_from_id_validation,
  df_os_medication_validation
) %>%
  group_by(date, data_desc, count_desc, count_method) |>
  mutate(count_total = sum(count, na.rm = TRUE)) |>
  select(-count_group, -count) |>
  distinct() %>%
  ungroup()

# Combine NHS BSA and OpenSAFELY data
pf_validation <- bind_rows(df_bsa_validation_total, df_os_validation_total)
