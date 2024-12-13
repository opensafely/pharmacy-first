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
    shape_var = NULL,
    save_path = NULL,
    colour_palette = NULL,
    legend_position = "bottom") {
  # Test if all columns expected in output from generate measures exist
  # expected_names <- c("measure", "interval_start", "interval_end", "ratio", "numerator", "denominator")
  # missing_columns <- setdiff(expected_names, colnames(data))

  # if (length(missing_columns) > 0) {
  #   stop("Data does not have expected column(s): ", paste(missing_columns, collapse = ", "), call. = FALSE)
  # }

  plot_tmp <- ggplot(
    data,
    aes(
      x = {{ select_interval_date }},
      y = {{ select_value }},
      colour = {{ colour_var }},
      group = {{ colour_var }},
      shape = {{ colour_var }}
    )
  ) +
    geom_point(size = 2) +
    geom_line(alpha = .3) +
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
      color = guide_legend(nrow = guide_nrow),
      shape = guide_legend(nrow = guide_nrow)
    ) +
    labs(
      title = title,
      x = x_label,
      y = y_label,
      colour = guide_label,
      shape = guide_label
    ) +
    theme(
      legend.position = legend_position,
      plot.title = element_text(hjust = 0.5),
      text = element_text(size = 14)
    ) 

  if(!is.null(colour_palette)) {
    plot_tmp <- plot_tmp + scale_colour_manual(values = colour_palette)
  } else {
    plot_tmp <- plot_tmp + scale_colour_viridis_d(end = .75)
  }

  # Automatically change y scale depending selected value
  if (rlang::as_label(enquo(select_value)) == "ratio") {
    plot_tmp <- plot_tmp + scale_y_continuous(
      limits = c(0, NA),
      # scale = 1000 to calculate rate per 1000 people
      labels = scales::label_number(scale = 1000)
    )
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

  if (!is.null(save_path)) {
    ggsave(
      filename = here("released_output", "results", "figures", save_path),
      plot = plot_tmp,
      width = 10,
      height = 6
    )
  } 

  plot_tmp
}

# Colour palettes
gradient_palette <- c("#001F4D", "#0056B3", "#007BFF", "#66B3E2", "#A4D8E1", "grey")
region_palette <- c("red", "navy", "#018701", "#ffa600ca", "purple", "brown", "#f4a5b2", "cyan", "green", "grey")
ethnicity_palette <- c("#42db0188", "#0056B3", "#ff0000c2", "#a52a2a5a", "purple", "grey")
sex_palette <- c("red", "blue")
