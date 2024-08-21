plot_measures <- function(
    data,
    title = NULL,
    x_label = NULL,
    y_label = NULL) {

  # Create plot
  plot <- ggplot(
    data,
    aes(
      x = interval_end,
      y = numerator,
      color = measure,
      group = measure
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
    ylim(y_min, NA) +
    # Applying the minimal theme
    theme_minimal()

  # Return plot
  plot
}
