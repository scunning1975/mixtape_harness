# _theme_bite.R — shared, reusable figure styling for the brazil_caps bite stage
# REQUIRES: ggplot2 >= 3.5
#
# Philosophy (CLAUDE.md figure standard): the figure is the star. Titles DESCRIBE
# what is plotted; they never tell the reader what to conclude. No evaluative words
# baked into the plot. The styling exists to make someone want to put the phone down
# and look — clean type, generous whitespace, a restrained cool palette, one accent.

suppressPackageStartupMessages(library(ggplot2))

# --- palette -----------------------------------------------------------------
# Cool base (deep slate/teal) with a single warm accent reserved for the series
# we most want the eye to land on (schizophrenia admissions — the mechanism).
bite_pal <- list(
  ink     = "#1A2E35",  # near-black slate, for text
  muted   = "#6B7B82",  # subtitle / caption grey
  grid    = "#E3E8EA",  # whisper-faint gridlines
  teal    = "#2A7F8E",  # psychiatric admissions (all)
  accent  = "#C8553D",  # schizophrenia admissions — the one we want stared at
  paper   = "#FFFFFF"
)

theme_bite <- function(base_size = 13, base_family = "Helvetica") {
  theme_minimal(base_size = base_size, base_family = base_family) +
    theme(
      plot.background   = element_rect(fill = bite_pal$paper, colour = NA),
      panel.background  = element_rect(fill = bite_pal$paper, colour = NA),
      panel.grid.major  = element_line(colour = bite_pal$grid, linewidth = 0.4),
      panel.grid.minor  = element_blank(),
      axis.ticks        = element_blank(),
      axis.text         = element_text(colour = bite_pal$muted, size = base_size - 2),
      axis.title        = element_text(colour = bite_pal$ink, size = base_size - 1),
      axis.title.x      = element_text(margin = margin(t = 8)),
      axis.title.y      = element_text(margin = margin(r = 8)),
      plot.title        = element_text(colour = bite_pal$ink, size = base_size + 5,
                                       face = "bold", margin = margin(b = 2)),
      plot.subtitle     = element_text(colour = bite_pal$muted, size = base_size - 1,
                                       margin = margin(b = 14), lineheight = 1.1),
      plot.caption      = element_text(colour = bite_pal$muted, size = base_size - 4,
                                       hjust = 0, margin = margin(t = 14)),
      plot.title.position   = "plot",
      plot.caption.position = "plot",
      legend.position   = "none",       # label the lines directly, not in a legend
      plot.margin       = margin(22, 26, 18, 22)
    )
}
