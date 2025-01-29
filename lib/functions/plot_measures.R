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
    colour_palette = NULL,
    y_scale = NULL,
    scale_measure = NULL,
    shapes = NULL,
    add_vline = TRUE,
    date_breaks = "1 month",
    legend_position = "bottom",
    text_size = 14,
    point_size = 2.5) {
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

  # Change colour based on specified colour palette
  if (!is.null(colour_palette)) {
    if (length(colour_palette) == 1 && colour_palette == "plasma") {
      plot_tmp <- plot_tmp + scale_colour_viridis_d(option = "plasma", end = .75) +
        geom_line(size = 0.5) +
        geom_point(size = point_size)
    } else {
      plot_tmp <- plot_tmp + scale_colour_manual(values = colour_palette)
    }
  } else {
    plot_tmp <- plot_tmp + scale_colour_viridis_d(end = .75)
  }

  if (!is.null(shapes) && shapes == "condition_shapes") {
    plot_tmp <- plot_tmp + scale_shape_manual(values = condition_shapes)
  }

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

# Colour palettes
gradient_palette <- c("#001F4D", "#0056B3", "#007BFF", "#66B3E2", "#A4D8E1", "grey")
region_palette <- c("red", "navy", "#018701", "#ffa600ca", "purple", "brown", "#f4a5b2", "cyan", "green", "grey")
ethnicity_palette <- c("#42db0188", "#0056B3", "#ff0000c2", "#a52a2a5a", "purple", "grey")
sex_palette <- c("red", "blue")
dark2_palette <- RColorBrewer::brewer.pal(n = 8, name = "Dark2")

# Custom shapes
condition_shapes <- c(
  "Acute Sinusitis" = 15,
  "Infected Insect Bite" = 19,
  "UTI" = 4,
  "Acute Otitis Media" = 23,
  "Acute Pharyngitis" = 3,
  "Herpes Zoster" = 17,
  "Impetigo" = 8
)
