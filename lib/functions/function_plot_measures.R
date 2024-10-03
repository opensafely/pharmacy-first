#' Plot Measures Over Time
#'
#' Creates a line plot of measures over time, with customisable labels and colours.
#'
#' @param data A dataframe containing output from the OpenSAFELY measures framework
#' @param select_interval_date Specify date variable interval_start or interval_end.
#' @param select_value The name of the column which contains the y-axis values: ratio, numerator, or denominator
#' @param title A string specifying the title of the plot.
#' @param x_label A string specifying the label for the x-axis.
#' @param y_label A string specifying the label for the y-axis.
#' @param colour_var Column name of the colour variable
#' @param legend_position Position of the guide/legend of the plot
#' @param guide_label A string specifying the label for the color/guide legend.
#' @param guide_nrow Number of rows for the colour/guide
#' @param facet_wrap Logical, specifying whether to include panels using facet_wrap
#' @param facet_var Variable name used for creating panels
#'
#' @return A ggplot object.

plot_measures <- function(
    data,
    select_interval_date,
    select_value,
    title = NULL,
    x_label = NULL,
    y_label = NULL,
    guide_label = NULL,
    guide_nrow = 2,
    facet_wrap = FALSE,
    facet_var = NULL,
    colour_var = NULL,
    legend_position = "bottom") {
  # Test if all columns expected in output from generate measures exist
  expected_names <- c("measure", "interval_start", "interval_end", "ratio", "numerator", "denominator")
  missing_columns <- setdiff(expected_names, colnames(data))

  if (length(missing_columns) > 0) {
    stop("Data does not have expected column(s): ", paste(missing_columns, collapse = ", "), call. = FALSE)
  }

  plot_tmp <- ggplot(
    data,
    aes(
      x = {{ select_interval_date }},
      y = {{ select_value }},
      colour = {{ colour_var }},
      group = {{ colour_var }}
    )
  ) +
    geom_point() +
    geom_line(alpha = .5) +
    geom_vline(
      xintercept = lubridate::as_date("2024-02-01"),
      linetype = "dotted",
      colour = "orange",
      linewidth = .7
    ) +
    scale_x_date(
      date_breaks = "1 month",
      labels = scales::label_date_short()
    ) +
    guides(
      color = guide_legend(nrow = guide_nrow)
    ) +
    labs(
      x = x_label,
      y = y_label,
      colour = guide_label,
    ) +
    theme(
      legend.position = legend_position
    )

  # Automatically change y scale depending selected value
  if (rlang::as_label(enquo(select_value)) %in% c("numerator", "denominator")) {
    plot_tmp <- plot_tmp + scale_y_continuous(
      limits = c(0, NA),
      labels = scales::label_number()
    )
  } else {
    plot_tmp <- plot_tmp + scale_y_continuous(
      limits = c(0, NA),
      labels = scales::label_percent()
    )
  }

  # Add facets if requested
  # Ideally we would want to check facet_var instead of having an additional argument facet_wrap
  # but for some unknown reason I cant get that to work
  if (facet_wrap) {
    plot_tmp <- plot_tmp +
      facet_wrap(vars({{ facet_var }}), ncol = 2)
  }

  plot_tmp
}
