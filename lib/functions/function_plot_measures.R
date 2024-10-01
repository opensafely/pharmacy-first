#' Plot Measures Over Time
#'
#' Creates a line plot of measures over time, with customisable labels and colours.
#'
#' @param data A dataframe containing the data to plot.
#' @param measure_names Strings specifiying the names of measure columns to be plotted.
#' @param custom_labels Strings specifying the names of legend labels.
#' @param title A string specifying the title of the plot. Default is NULL.
#' @param x_label A string specifying the label for the x-axis. Default is NULL.
#' @param y_label A string specifying the label for the y-axis. Default is NULL.
#' @param color_label A string specifying the label for the color legend. Default is NULL.
#' @param value_col The name of the dataframe column which contains the y-axis values. Default is "numerator".
#' @param measure_col The name of the dataframe column which contains the categorical variable. Default is "measure".
#'
#' @return A ggplot object.

plot_measures <- function(
    data,
    measure_names,
    custom_labels = NULL,
    date_col = "interval_end",
    value_col = "numerator",
    measure_col = "measure",
    title = NULL,
    x_label = NULL,
    y_label = NULL,
    facet_var = NULL,
    color_label = NULL,
    rotate_x_labels = FALSE,
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

  # Apply custom labels if provided
  if (!is.null(custom_labels)) {
    data <- data %>%
      mutate(!!measure_sym := factor(!!measure_sym, levels = measure_names, labels = custom_labels))
  }

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
    geom_point() +
    geom_line(alpha = .5) +
    scale_y_continuous(
      limits = c(0, NA),
    ) +
    theme_minimal() +
    theme(
      axis.text.x = element_text(size = axis_x_text_size),
      legend.position = "bottom",
      legend.key.size = unit(0.5, "cm"),
      legend.text = element_text(size = 8),
      legend.title = element_text(size = 8)
    ) +
    # Adjust number of rows in the legend
    guides(
      color = guide_legend(nrow = 2)
    ) +
    geom_vline(
      xintercept = lubridate::as_date("2024-02-01"),
      linetype = "dotted",
      colour = "orange",
      linewidth = .7
    ) +
    scale_x_date(
      date_breaks = "1 month",
      date_labels = "%b %Y"
    )

    if (!is.null(facet_var)) {
    facet_sym <- sym(facet_var)
    plot1 <- plot1 + facet_wrap(vars(!!facet_sym), scales = "free_x")

  }

# Conditionally apply x-axis label rotation if rotate_x_labels is TRUE
  if (rotate_x_labels) {
    plot1 <- plot1 + theme(axis.text.x = element_text(angle = 45, hjust = 1))
  }

  plot1
}
