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
    y_scale = NULL,
    scale_measure = NULL,
    add_vline = TRUE,
    date_breaks = "1 month",
    legend_position = "bottom",
    text_size = 14,
    point_size = 2.5) {
  plot_tmp <- ggplot(
    data,
    aes(
      x = {{ select_interval_date }},
      y = {{ select_value }},
      colour = {{ colour_var }},
      group = {{ colour_var }},
      shape = {{ colour_var }},
      fill = {{ colour_var }}
    )
  ) +
    geom_point(size = point_size) +
    geom_line(alpha = .3) +
    scale_x_date(
      date_breaks = {{ date_breaks }},
      labels = scales::label_date_short()
    ) +
    guides(
      color = guide_legend(nrow = guide_nrow),
      shape = guide_legend(nrow = guide_nrow)
    ) +
    labs(
      title = title,
      x = x_label,
      y = y_label,
      colour = guide_label,
      shape = NULL,
      fill = NULL
    ) +
    theme(
      legend.position = legend_position,
      plot.title = element_text(hjust = 0.5),
      text = element_text(size = text_size)
    )

  if (add_vline) {
    plot_tmp <- plot_tmp + geom_vline(
      xintercept = lubridate::as_date("2024-02-01"),
      linetype = "dotted",
      colour = "orange",
      linewidth = .7
    )
  }

  plot_tmp <- plot_tmp +
    scale_colour_viridis_d(end = .75, na.value = "gray40") +
    scale_fill_viridis_d(end = .75)

  # Automatically change y scale depending selected value
  scale_label <- rlang::as_label(enquo(scale_measure))
  if (is.null(scale_measure)) {
    plot_tmp <- plot_tmp + scale_y_continuous(
      limits = c(0, NA),
      labels = scales::label_number()
    )
  } else if (scale_measure == "rate") {
    plot_tmp <- plot_tmp + scale_y_continuous(
      limits = c(0, NA),
      labels = scales::label_number(scale = 1000)
    )
  } else if (scale_measure == "percent") {
    plot_tmp <- plot_tmp + scale_y_continuous(labels = scales::percent)
  } else {
    plot_tmp <- plot_tmp + scale_y_continuous(
      limits = c(0, NA),
      labels = scales::label_number()
    )
  }

  # Add facets if requested
  # Ideally we would want to check facet_var instead of having an additional argument facet_wrap
  # but for some unknown reason I cant get that to work
  if (facet_wrap) {
    plot_tmp <- plot_tmp +
      facet_wrap(vars({{ facet_var }}), ncol = 2)
  }
  # Add y_scale to add option for free_y
  if (!is.null(y_scale) && y_scale == "free_y") {
    plot_tmp <- plot_tmp +
      facet_wrap(~source, scales = "free_y")
  }

  plot_tmp
}

set_patchwork_theme <- function(patchwork_figure) {
  patchwork_figure +
    plot_annotation(tag_levels = "A") +
    plot_layout(guides = "collect", widths = c(2, 1)) &
    theme(
      legend.position = "bottom",
      text = element_text(size = 15),
      strip.background = element_rect(size = 0),
      strip.text.x = element_text(size = 13, face = "bold")
    )
}

save_figure <- function(figure, width = 10, height = 6) {
  # this uses the 'figure' argument as a string to later generate a filename
  figure_name <- deparse(substitute(figure))
  ggsave(
    filename = here("released_output", "results", "figures", paste(figure_name, "png", sep = ".")),
    figure,
    width = width, height = height
  )
}
