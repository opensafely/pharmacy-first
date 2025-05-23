library("httr")
library("jsonlite")
library("crul")
library("here")
library("rvest")
library("dplyr")
library("lubridate")
library("tidyverse")
library("readr")
library("retry")

base_endpoint <- "https://opendata.nhsbsa.net/api/3/action/"
package_list_method <- "package_list"
package_show_method <- "package_show?id="
action_method <- "datastore_search_sql?"

get_available_datasets <- function() {
  base_endpoint <- "https://opendata.nhsbsa.net/api/3/action/"
  package_list_method <- "package_list"

  datasets_response <- fromJSON(paste0(
    base_endpoint,
    package_list_method
  ))$result

  # Remove datasets with FOI and starting with a number
  # There does not seem to be any data that we can query from these tables
  datasets_response <- datasets_response[!grepl("foi", datasets_response)]
  datasets_response <- datasets_response[!grepl("^[0-9]", datasets_response)]

  datasets_response
}

get_available_datasets()

get_dataset_table_names <- function(dataset_id, start_date = NULL, end_date = NULL) {
  available_datasets <- get_available_datasets()

  if (!dataset_id %in% available_datasets) {
    stop("The provided 'dataset_id' is not available. Run 'get_available_datasets()' to see all available datasets.", call. = FALSE)
  }

  base_endpoint <- "https://opendata.nhsbsa.net/api/3/action/"
  package_show_method <- "package_show?id="

  metadata_response <- GET(paste0(base_endpoint, package_show_method, dataset_id))
  resources_table <- content(metadata_response)$result$resources

  dataset_tables <- tibble(
    table_name = map_chr(
      resources_table,
      "bq_table_name",
      .default = NA_character_
    ),
    date = ym(str_extract(table_name, "\\d{6}"))
  ) |>
    relocate(date)

  if (is.null(start_date)) {
    start_date <- as.Date(min(dataset_tables$date))
  }

  if (is.null(end_date)) {
    end_date <- as.Date(max(dataset_tables$date))
  }

  dataset_tables <- dataset_tables |>
    filter(between(date, as.Date(start_date), as.Date(end_date)))

  dataset_tables
}

get_dataset_table_names("prescription-cost-analysis-pca-monthly-data", "2024-01-01")

construct_sql_query <- function(table_name, sql_query) {
  gsub("{FROM_TABLE}", sprintf("FROM `%s`", table_name), sql_query, fixed = TRUE)
}

get_nhsbsa_data <- function(dataset_id, sql, start_date = NULL, end_date = NULL) {
  base_endpoint <- "https://opendata.nhsbsa.net/api/3/action/"
  action_method <- "datastore_search_sql?"

  # Retrieve table names for specified dataset and data range
  table_names <- get_dataset_table_names(dataset_id, start_date, end_date)$table_name

  # Construct URLs for querying the API, one URL per table, modifying each table with table_name
  async_api_calls <- paste0(
    base_endpoint,
    action_method,
    "resource_id=", table_names,
    "&sql=", URLencode(map_chr(table_names, construct_sql_query, sql))
  )

  # Initialise an empty list to store API responses
  responses <- list()

  # Loop over each API call URL, by:
  # 1) getting URL for current table, 
  # 2) initialise retry counter, 
  # 3) set max number of retry attempts, 
  # 4) flag to track if request was successful
  for (i in seq_along(async_api_calls)) {
    url <- async_api_calls[i]
    attempt <- 1
    max_attempts <- 5
    success <- FALSE

    # Retry logic: keep trying until request is successful or max attempts reached
    while (attempt <= max_attempts && !success) {
      response <- tryCatch({
        crul::HttpClient$new(url)$get()
      }, error = function(e) {
        NULL
      })

      if (!is.null(response) && response$status_code == 200) {
        # If response is valid and status code = 200, mark as successful
        success <- TRUE
        responses[[i]] <- response
      } else {
        message(sprintf("Attempt %d failed for URL: %s", attempt, url))
        Sys.sleep(2 ^ attempt)
        attempt <- attempt + 1
      }
    }

    if (!success) {
      stop(sprintf("Failed to fetch data from URL: %s after %d attempts", url, max_attempts))
    }
  }
  # Parse the successful responses to extract the data
  results <- map(responses, ~ {
    content_raw <- .x$parse("UTF-8")
    fromJSON(readLines(textConnection(content_raw), warn = FALSE))$result$result$records
  })

  df_tmp <- bind_rows(map(results, ~ as_tibble(.x, .default = tibble())))

  df_tmp |>
    janitor::clean_names() |>
    mutate(year_month = ym(year_month)) |>
    select(date = year_month, everything())
}

sql <- ("
  SELECT *
  {FROM_TABLE}
  WHERE PHARMACY_ADVANCED_SERVICE = 'Pharmacy First Clinical Pathways'
  ")

df_validate <- get_nhsbsa_data("prescription-cost-analysis-pca-monthly-data", sql, start_date = "2024-02-01")

names(df_validate)
unique(df_validate$pharmacy_advanced_service)
range(df_validate$date)

pf_medication_validation_data <- df_validate |>
  select(date, snomed_code, pharmacy_advanced_service, bnf_section, bnf_paragraph, items) |>
  group_by(date, pharmacy_advanced_service, bnf_paragraph) |>
  summarise(count = sum(items, na.rm = TRUE)) |>
  ungroup()

write_csv(pf_medication_validation_data, here("lib", "validation", "data", "pf_medication_validation_data.csv"))
