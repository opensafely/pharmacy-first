#' Plot Measures Over Time
#' 
#' Creates a line plot of measures over time, with customisable labels and colours.
#' 
#' @param data A dataframe containing the data to plot.
#' @param title A string specifying the title of the plot. Default is NULL. 
#' @param x_label A string specifying the label for the x-axis. Default is NULL.
#' @param y_label A string specifying the label for the y-axis. Default is NULL. 
#' @param color_label A string specifying the label for the color legend. Default is NULL.
#' @param value_col The name of the dataframe column which contains the y-axis values. Default is "numerator".
#' @param measure_col The name of the dataframe column which contains the categorical variable. Default is "measure".
#' 
#' 
#' @return A ggplot object.

plot_measures <- function(
    data,
    date_col = "interval_end",
    value_col = "numerator",
    measure_col = "measure",
    title = NULL,
    x_label = NULL,
    y_label = NULL,
    color_label = NULL) {

  # Create plot
  plot1 <- ggplot(
    data,
    aes(
      x = {{date_col}},
      y = {{value_col}},
      color = {{measure_col}},
      group = {{measure_col}}
    )
  ) +
    geom_line() +
    labs(
      title = title,
      x = x_label,
      y = y_label,
      color = "Condition"
    ) +
    # Setting the minimum y-value
    ylim(0, NA) +
    # Applying the minimal theme
    theme_minimal() +
    scale_x_date(
    date_breaks = "1 month",  
    date_labels = "%b %Y",    
    )

  # Return plot
  plot1
}
