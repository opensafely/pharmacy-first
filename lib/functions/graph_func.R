plot_pharmacy_first_conditions <- function(data,
title = "Number of Consultations for each Pharmacy First Clinical Condition per month",
                                           x_label = "Date",
                                           y_label = "Number of Consultations",
                                           y_min = 0) {
  ggplot(data, 
  aes(x = interval_end,
  y = numerator,
  color = measure,
  group = measure)) +
    geom_line() +
    labs(title = title,
         x = x_label,
         y = y_label,
         color = "Condition") +
    ylim(y_min, NA) +  # Setting the minimum y-value
    theme_minimal()    # Applying the minimal theme
}
