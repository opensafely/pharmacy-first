# Define dictionaries with tidy names and mappings for measures
pf_measures_name_dict <- list(
  pf_consultation_cp_minorillness = "Consultation Service",
  pf_consultation_service = "Pharmacy First Consultation",
  pf_consultation_cp_service = "Community Pharmacy First Service",
  pf_consultation_services_combined = "Pharmacy First Consultations (Combined)",
  acute_otitis_media = "Acute Otitis Media",
  herpes_zoster = "Herpes Zoster",
  acute_sinusitis = "Acute Sinusitis",
  impetigo = "Impetigo",
  infected_insect_bite = "Infected Insect Bite",
  acute_pharyngitis = "Acute Pharyngitis",
  uncomplicated_urinary_tract_infection = "UTI"
)

pf_measures_name_mapping <- list(
  pf_consultation_cp_minorillness = "clinical_service",
  pf_consultation_service = "clinical_service",
  pf_consultation_cp_service = "clinical_service",
  pf_consultation_services_combined = "pharmacy_first_services",
  acute_otitis_media = "clinical_condition",
  herpes_zoster = "clinical_condition",
  acute_sinusitis = "clinical_condition",
  impetigo = "clinical_condition",
  infected_insect_bite = "clinical_condition",
  acute_pharyngitis = "clinical_condition",
  uncomplicated_urinary_tract_infection = "clinical_condition"
)

pf_measures_groupby_dict <- list(
  age_band = "Age band",
  sex = "Sex",
  imd = "IMD",
  region = "Region",
  ethnicity = "Ethnicity"
)

pf_measures_ethnicity_list <- list(
  "White",
  "Mixed",
  "Asian or Asian British",
  "Black or Black British",
  "Chinese or Other Ethnic Groups",
  "Missing"
)

pf_measures_age_list <- list(
  "0-19",
  "20-39",
  "40-59",
  "60-79",
  "80+",
  "Missing"
)

pf_measures_region_list <- list(
    "East",
    "East Midlands",
    "London",
    "North East",
    "North West",
    "South East",
    "South West",
    "West Midlands",
    "Yorkshire and The Humber",
    "Missing"
)

#' Tidy measures data
#'
#' Creates a tidier dataframe of measures data.
#' The measures must be named in a spedific way for this function to work properly.
#'
#' @param data A dataframe containing output from the OpenSAFELY measures framework
#' @param pf_measures_name_dict List, specifying the dict of measure names.
#' This information will be pulled from the original measure name.
#' @param pf_measures_name_mapping List, specifying the mapping of measures to groups.
#' This information will be pulled from the original measure name.
#' @param pf_measures_groupby_dict List, specifying the dict of groupby/breakdown names.
#' This information will be pulled from the original measure name.
#'
#' @return A dataframe
tidy_measures <- function(data, pf_measures_name_dict, pf_measures_name_mapping, pf_measures_groupby_dict) {
  data_tmp <- data %>%
  # Separate 'measure' column into 'summary_stat_measure' and 'group_by'
  # Separate 'summary_stat_measure' into 'summary_stat' and 'measure'
    separate(measure, into = c("summary_stat_measure", "group_by"), sep = "_by_") %>%
    separate(summary_stat_measure, into = c("summary_stat", "measure"), sep = "_", extra = "merge")

  # Modify columns based on recoding and factor levels
  data_tmp <- data_tmp %>%
    mutate(
      # Recode 'measure' to be more readable
      measure_desc = recode(factor(measure), !!!pf_measures_name_mapping),
      measure = recode(factor(measure), !!!pf_measures_name_dict),
      group_by = recode(factor(group_by), !!!pf_measures_groupby_dict),
      ethnicity = factor(ethnicity, levels = pf_measures_ethnicity_list, labels = pf_measures_ethnicity_list),
      age_band = factor(age_band, levels = pf_measures_age_list, labels = pf_measures_age_list),
      region = factor(region, levels = pf_measures_region_list, labels = pf_measures_region_list),
      sex = factor(sex, levels = c("female", "male"), labels = c("Female", "Male"))
    )

  data_tmp
}
