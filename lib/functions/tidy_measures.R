# Define dictionaries with tidy names and mappings for measures
pf_measures_name_dict <- list(
  consultation_service = "Consultation Service",
  pharmacy_first_service = "Pharmacy First Consultation",
  combined_pf_service = "Pharmacy First Consultations (Combined)",
  acute_otitis_media = "Acute Otitis Media",
  herpes_zoster = "Herpes Zoster",
  acute_sinusitis = "Acute Sinusitis",
  impetigo = "Impetigo",
  infected_insect_bite = "Infected Insect Bite",
  acute_pharyngitis = "Acute Pharyngitis",
  uncomplicated_urinary_tract_infection = "UTI"
)

pf_measures_name_mapping <- list(
  consultation_service = "clinical_service",
  pharmacy_first_service = "clinical_service",
  combined_pf_service = "pharmacy_first_services",
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
    separate(measure, into = c("summary_stat_measure", "group_by"), sep = "_by_") %>%
    separate(summary_stat_measure, into = c("summary_stat", "measure"), sep = "_", extra = "merge")

  data_tmp <- data_tmp %>%
    mutate(
      measure_desc = recode(factor(measure), !!!pf_measures_name_mapping),
      measure = recode(factor(measure), !!!pf_measures_name_dict),
      group_by = recode(factor(group_by), !!!pf_measures_groupby_dict)
    )

  data_tmp
}
