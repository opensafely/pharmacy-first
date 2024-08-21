# In this file we're trying out some code
library(tidyverse)
library(ggplot2)
library(gridExtra) # For arranging multiple plots

# Load data
df_measures <- readr::read_csv(
  here::here("output", "report", "conditions_measures.csv")
)

# Develop plotting function 
p <- ggplot(df_measures, aes(x = interval_end, y = numerator, color = measure, group = measure)) +
  geom_line() +
  labs(
    title = paste("Number of Consultations for each Pharmacy First Clinical Condition per month"),
    x = "Date",
    y = "Number of Consultations",
    color = "Condition"
  ) +
  ylim(0, NA)

source(here::here("lib", "functions", "graph_func.R"))
plot1_conditions <- plot_pharmacy_first_conditions(df_measures)
