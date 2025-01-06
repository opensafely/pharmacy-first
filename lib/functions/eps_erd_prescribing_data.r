library(tidyverse)
library(janitor)
library(here)
library(httr)

# Function to download and read the xlsx files
read_xlsx_from_url <- function(url_list, sheet = NULL, skip = NULL, ...) {
  temp_file <- tempfile(fileext = ".xlsx")
  GET(
    url_list,
    write_disk(temp_file, overwrite = TRUE)
  )
  readxl::read_xlsx(
    temp_file,
    col_names = TRUE,
    .name_repair = janitor::make_clean_names,
    sheet = sheet,
    skip = skip,
    ...
  )
}

df <- read_xlsx_from_url(
  "https://github.com/user-attachments/files/17774058/EPS.and.eRD.Prescribing.Dashboard.July.2024.xlsx",
  skip = 2,
  sheet = "Historical Data"
)

df_filtered <- df %>%
  select(month, region_code, practice_code, eps_items, erd_items) %>%
  filter(month %in% c(202402, 202403, 202404, 202405, 202406, 202407)) %>%
  mutate(month = ym(month))

df_filtered |> write_csv(
  here("lib", "validation", "data", "eps_erd_prescribing_2024-02-01_to_2024-07-01.csv")
)
