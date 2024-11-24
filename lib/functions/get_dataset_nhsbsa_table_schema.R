library("httr")
library("jsonlite")
library("crul")
library("here")
library("rvest")
library("dplyr")
library("lubridate")
library("tidyverse")
library("readr")

source(here("lib/functions/get_pf_medication_validation_data.R"))

# This may be useful for writing SQL queries but reading the schema from
# JSON in the metadata seems more tricky and maybe there's another way
get_dataset_table_schema <- function(dataset_id) {
  base_endpoint <- "https://opendata.nhsbsa.net/api/3/action/"
  package_show_method <- "package_show?id="

  available_datasets <- get_available_datasets()

  if (!dataset_id %in% available_datasets) {
    stop("The provided 'dataset_id' is not available. Run 'get_available_datasets()' to see all available datasets.", call. = FALSE)
  }

  metadata_response <- GET(paste0(base_endpoint, package_show_method, dataset_id))
  resources <- content(metadata_response)$result$resources

  schema_raw <- resources[[1]]$schema

  # There seems to be a lot of odd strings in the JSON
  # that needs to be fixed before we can read it
  schema_fixed <- schema_raw
  schema_fixed <- gsub("u\'", '"', schema_fixed)
  schema_fixed <- gsub("u\"", '"', schema_fixed)
  schema_fixed <- gsub("':", '":', schema_fixed)
  schema_fixed <- gsub("',", '",', schema_fixed)
  schema_fixed <- gsub("'}", '"}', schema_fixed)
  schema_fixed <- gsub("']", '"]', schema_fixed)
  schema_fixed <- gsub("-", "", schema_fixed)
  schema_fixed <- gsub("-", "", schema_fixed)

  schema_list <- fromJSON(schema_fixed, flatten = TRUE)

  tibble(schema_list$fields) |>
    select(name, title, type, description)
}

nhsbsa_table_schemas <- map(
  set_names(get_available_datasets()),
  safely(get_dataset_table_schema)
)

nhsbsa_table_schemas_results <- map(nhsbsa_table_schemas, "result")
nhsbsa_table_schemas_errors <- map(nhsbsa_table_schemas, "error")
