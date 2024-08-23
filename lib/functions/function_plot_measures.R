#' Plot Measures Over Time
#' 
#' Creates a line plot of measures over time, with customisable labels and colours.
#' 
#' @param data A dataframe containing the data to plot.
#' @param measure_names Strings specifiying the names of measure columns to be plotted.
#' @param title A string specifying the title of the plot. Default is NULL. 
#' @param x_label A string specifying the label for the x-axis. Default is NULL.
#' @param y_label A string specifying the label for the y-axis. Default is NULL. 
#' @param color_label A string specifying the label for the color legend. Default is NULL.
#' @param value_col The name of the dataframe column which contains the y-axis values. Default is "numerator".
#' @param measure_col The name of the dataframe column which contains the categorical variable. Default is "measure".
#' 
#' 
#' @return A ggplot object.

# Define the function
plot_measures <- function(
    data,
    measure_names,
    date_col = "interval_end",
    value_col = "numerator",
    measure_col = "measure",
    title = NULL,
    x_label = NULL,
    y_label = NULL,
    color_label = NULL,
    axis_x_text_size = 7) {

  # Check if the necessary columns exist in the data
  if (date_col %in% names(data) == FALSE) {
    stop("Data does not have a column with the name '", date_col, "'")
  } else if (value_col %in% names(data) == FALSE) {
    stop("Data does not have a column with the name '", value_col, "'")
  } else if (measure_col %in% names(data) == FALSE) {
    stop("Data does not have a column with the name '", measure_col, "'")
  }

  # Convert column names to symbols
  date_sym <- sym(date_col)
  value_sym <- sym(value_col)
  measure_sym <- sym(measure_col)

  # Ensure the date column is of Date type
  data <- data %>%
    mutate(!!date_sym := as.Date(!!date_sym))

  # Filter measures column for user-specified measure names
  data <- data %>%
    filter(!!measure_sym %in% measure_names)

  # Create plot
  plot1 <- ggplot(
    data,
    aes(
      x = !!date_sym,
      y = !!value_sym,
      color = !!measure_sym,
      group = !!measure_sym
    )
  ) +
    geom_line() +
    labs(
      title = title,
      x = x_label,
      y = y_label,
      color = color_label
    ) +
    scale_y_continuous(
      limits = c(0, NA),
    ) +
    theme_minimal() +
    theme(axis.text.x = element_text(size = axis_x_text_size), 
    legend.position="bottom",
    legend.key.size = unit(0.5, "cm"),
    legend.text = element_text(size = 6),
    legend.title = element_text(size = 8)) +
    guides(
    color = guide_legend(nrow = 2)  # Adjust number of rows in the legend
) +
    geom_vline(
      xintercept = lubridate::as_date("2024-02-01"),
      linetype = "dotted",
      colour = "orange",
      linewidth = .7) +
    scale_x_date(
      date_breaks = "1 month",  
      date_labels = "%b %Y"
    )

  
  plot1
}