library(httr)
library(here)
library(rvest)
library(dplyr)
library(lubridate)
library(tidyverse)
library(readr)
library(jsonlite)

#' Get ICB code to region lookup data
get_icb_region_lookup <- function() {
  query_url <- "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/SICBL22_ICB22_NHSER22_EN_LU/FeatureServer/0/query"

  query_params <- list(
    where = "1=1",
    outFields = "NHSER22NM,ICB22CDH",
    outSR = "4326",
    f = "json"
  )

  response <- GET(query_url, query = query_params)

  json_text <- content(response, as = "text", encoding = "UTF-8")

  fromJSON(json_text, flatten = TRUE)$features |>
    bind_rows() |>
    as_tibble() |>
    rename(region = attributes.NHSER22NM, icb_code = attributes.ICB22CDH) |>
    distinct()
}

#' Extract dates from dispensing data URL
#'
#' @param urls List of URLs
#' @return String, of date in YYYY-MM-DD format if date can be found, otherwise NA.
extract_dates <- function(urls) {
  urls %>%
    map(~ {
      match <- str_match(.x, ".*Dispensing%20Data%20(\\w+)%20(\\d{2})")[, 2:3]

      if (all(!is.na(match))) {
        month <- match[1]
        year <- paste0("20", match[2])

        parsed_date <- parse_date_time(
          paste("1", month, year),
          orders = "dmy",
          quiet = TRUE
        )
        if (!is.na(parsed_date)) {
          return(format(parsed_date, "%Y-%m-%d"))
        }
      }
      return(NA)
    })
}

get_dispensing_urls <- function(start_date = NULL, end_date = NULL) {
  # This is the URL where the data is linked from
  url <- "https://www.nhsbsa.nhs.uk/prescription-data/dispensing-data/dispensing-contractors-data"

  # The URL to the data we are interested in follows this URL structure
  # https://www.nhsbsa.nhs.uk/sites/default/files/2024-05/Dispensing%20Data%20Jan%2024%20-%20CSV.csv
  base_url <- "https://www.nhsbsa.nhs.uk"

  response <- GET(url)
  html_content <- content(response, "text", encoding = "UTF-8")

  csv_links <- read_html(html_content) %>%
    html_nodes("a") %>%
    html_attr("href") %>%
    .[grepl("Dispensing%20Data.*\\.csv", .)]

  df <- tibble(
    date = as.Date(extract_dates(csv_links) |> unlist()),
    url = paste0(base_url, csv_links)
  )

  if (is.null(start_date)) {
    start_date <- as.Date(min(df$date))
  }

  if (is.null(end_date)) {
    end_date <- as.Date(max(df$date))
  }

  df <- df |>
    filter(between(date, as.Date(start_date), as.Date(end_date)))

  setNames(as.list(df$url), as.character(df$date))
}

get_dispensing_data <- function(start_date = NULL, end_date = NULL) {
  dispensing_urls <- get_dispensing_urls(start_date = start_date, end_date = end_date)

  icb_var_list <- c(
    "ICBCode",
    "ICB"
  )

  pf_var_list <- c(
    "NumberofPharmacyFirstClinicalPathwaysConsultations-AcuteOtitisMedia",
    "NumberofPharmacyFirstClinicalPathwaysConsultations-AcuteSoreThroat",
    "NumberofPharmacyFirstClinicalPathwaysConsultations-Impetigo",
    "NumberofPharmacyFirstClinicalPathwaysConsultations-InfectedInsectBites",
    "NumberofPharmacyFirstClinicalPathwaysConsultations-Shingles",
    "NumberofPharmacyFirstClinicalPathwaysConsultations-Sinusitis",
    "NumberofPharmacyFirstClinicalPathwaysConsultations-UncomplicatedUTI",
    "NumberofPharmacyFirstUrgentMedicineSupplyConsultations",
    "NumberofPharmacyFirstMinorIllnessReferralConsultations"
  )

  df <- dispensing_urls |>
    map(read_csv,
      name_repair = janitor::make_clean_names
    ) |>
    bind_rows(.id = "date") |>
    select(date, all_of(janitor::make_clean_names(c(icb_var_list, pf_var_list))))

  df |>
    rename_with(~ str_replace(., "^numberof_pharmacy_first", "n_pf")) |>
    rename_with(~ str_replace(., "clinical_pathways_consultations", "consultation"))
}

# Calculate summary of counts
df_dispensing_data <- get_dispensing_data(start_date = "2023-11-01")

df_dispensing_data_summary <- df_dispensing_data |>
  group_by(date) |>
  summarise(
    n_pf_consultation_acute_otitis_media = sum(n_pf_consultation_acute_otitis_media, na.rm = TRUE),
    n_pf_consultation_acute_sore_throat = sum(n_pf_consultation_acute_sore_throat, na.rm = TRUE),
    n_pf_consultation_impetigo = sum(n_pf_consultation_impetigo, na.rm = TRUE),
    n_pf_consultation_infected_insect_bites = sum(n_pf_consultation_infected_insect_bites, na.rm = TRUE),
    n_pf_consultation_shingles = sum(n_pf_consultation_shingles, na.rm = TRUE),
    n_pf_consultation_sinusitis = sum(n_pf_consultation_sinusitis, na.rm = TRUE),
    n_pf_consultation_uncomplicated_uti = sum(n_pf_consultation_uncomplicated_uti, na.rm = TRUE),
    # n_pf_urgent_medicine_supply_consultations = sum(n_pf_urgent_medicine_supply_consultations, na.rm = TRUE),
    # n_pf_minor_illness_referral_consultations = sum(n_pf_minor_illness_referral_consultations, na.rm = TRUE)
  ) |>
  pivot_longer(
    cols = c(
      n_pf_consultation_acute_otitis_media,
      n_pf_consultation_acute_sore_throat,
      n_pf_consultation_impetigo,
      n_pf_consultation_infected_insect_bites,
      n_pf_consultation_shingles,
      n_pf_consultation_sinusitis,
      n_pf_consultation_uncomplicated_uti,
      # n_pf_urgent_medicine_supply_consultations,
      # n_pf_minor_illness_referral_consultations
    ),
    names_to = "consultation_type",
    values_to = "count"
  ) |>
  mutate(consultation_type = str_replace(consultation_type, "^n_pf_consultation_", ""))

write_csv(df_dispensing_data_summary, here("lib", "validation", "data", "pf_consultation_validation_data.csv"))

# Get counts by region
icb_region_lookup <- get_icb_region_lookup()

df_dispensing_data_by_region <- df_dispensing_data |>
  left_join(icb_region_lookup, by = "icb_code")

df_dispensing_data_summary_by_region <- df_dispensing_data_by_region |>
  group_by(date, region) |>
  summarise(
    n_pf_consultation_acute_otitis_media = sum(n_pf_consultation_acute_otitis_media, na.rm = TRUE),
    n_pf_consultation_acute_sore_throat = sum(n_pf_consultation_acute_sore_throat, na.rm = TRUE),
    n_pf_consultation_impetigo = sum(n_pf_consultation_impetigo, na.rm = TRUE),
    n_pf_consultation_infected_insect_bites = sum(n_pf_consultation_infected_insect_bites, na.rm = TRUE),
    n_pf_consultation_shingles = sum(n_pf_consultation_shingles, na.rm = TRUE),
    n_pf_consultation_sinusitis = sum(n_pf_consultation_sinusitis, na.rm = TRUE),
    n_pf_consultation_uncomplicated_uti = sum(n_pf_consultation_uncomplicated_uti, na.rm = TRUE),
    # n_pf_urgent_medicine_supply_consultations = sum(n_pf_urgent_medicine_supply_consultations, na.rm = TRUE),
    # n_pf_minor_illness_referral_consultations = sum(n_pf_minor_illness_referral_consultations, na.rm = TRUE)
  ) |>
  pivot_longer(
    cols = c(
      n_pf_consultation_acute_otitis_media,
      n_pf_consultation_acute_sore_throat,
      n_pf_consultation_impetigo,
      n_pf_consultation_infected_insect_bites,
      n_pf_consultation_shingles,
      n_pf_consultation_sinusitis,
      n_pf_consultation_uncomplicated_uti,
      # n_pf_urgent_medicine_supply_consultations,
      # n_pf_minor_illness_referral_consultations
    ),
    names_to = "consultation_type",
    values_to = "count"
  ) |>
  mutate(consultation_type = str_replace(consultation_type, "^n_pf_consultation_", ""))
  
write_csv(df_dispensing_data_summary_by_region, here("lib", "validation", "data", "pf_consultation_validation_data_by_region.csv"))
