# 02_bite_maps.R — bite stage, brazil_caps. State choropleths of the within-municipality
# first difference in admissions around CAPS adoption.
# REQUIRES: data.table >= 1.14, sf >= 1.0, geobr >= 1.9, ggplot2 >= 3.5
#
# FIRST DIFFERENCE (per the authors' own cohort definition in load_brazil.R):
#   g  = first year the municipality has a CAPS  (first year ca == 1)
#   before = outcome at g-1            (the baseline year, just before treatment)
#   after  = mean(outcome | ano >= g)  (the entire post-treatment period)
#   fd     = after - before            (within-municipality change)
# Computed for every ever-treated municipality with an in-panel baseline (g in 2003..2016;
# the g = 2002 cohort is excluded — 2002 is the first panel year, so it has no g-1).
#
# WHY STATE-LEVEL: the teaching brazil.dta carries no municipality map key (cod is a 1..5476
# index; there is no IBGE code or name). `uf` IS the real IBGE state code, so the honest map we
# can draw is the 27 states — each municipality's fd population-weighted (baseline pop) to its
# state. A true 5,476-municipality map needs the geocoded replication file; see findings.md.
#
# Figure philosophy (CLAUDE.md): figure is the star. Titles DESCRIBE (what is mapped); the
# diverging color is a fact (how much each state changed), not a verdict.

suppressPackageStartupMessages({ library(data.table); library(sf); library(ggplot2) })
source("scripts/r/_theme_bite.R")

CLEAN <- "data/clean/brazil_bite_panel.rds"
stopifnot("run 00_bite_inspect.R first" = file.exists(CLEAN))
dt <- as.data.table(readRDS(CLEAN))
stopifnot(all(c("cod","uf","ano","pop_","ca","sih_tnet_F","sih_tnet_F_esquizofrenia") %in% names(dt)))

# --- cohort g per municipality (first treated year) --------------------------
dt[, g := { yrs <- ano[ca == 1]; if (length(yrs)) min(yrs) else NA_integer_ }, by = cod]

# --- per-municipality first difference for one outcome -----------------------
first_diff <- function(var) {
  d <- dt[!is.na(g) & g >= 2003 & g <= 2016]            # ever-treated, baseline in panel
  d[, .(
    uf      = uf[1L],
    before  = .SD[ano == g[1L] - 1L][[var]][1L],        # g-1 baseline
    after   = mean(.SD[ano >= g[1L]][[var]], na.rm = TRUE),
    pop_bl  = .SD[ano == g[1L] - 1L][["pop_"]][1L]       # baseline population (weight)
  ), by = cod][, fd := after - before][is.finite(fd) & is.finite(pop_bl)]
}

# --- aggregate municipal fd to state (population-weighted) --------------------
by_state <- function(var) {
  m <- first_diff(var)
  m[, .(fd = weighted.mean(fd, pop_bl), n_treated = .N), by = uf]
}

# --- geometry (27 states), cached locally, joined on IBGE state code ----------
GEO <- "data/derived/br_states.geojson"
if (!file.exists(GEO)) {
  options(timeout = 600)
  download.file("https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/brazil-states.geojson",
                GEO, mode = "wb", quiet = TRUE)
}
suppressMessages(sf::sf_use_s2(FALSE))                 # planar ops; the source has minor loop defects
states <- st_make_valid(st_read(GEO, quiet = TRUE))
states$uf <- as.integer(states$codigo_ibg)
states$abbrev_state <- states$sigla

make_map <- function(var, title, file) {
  agg <- by_state(var)
  g_sf <- merge(states, agg, by = "uf", all.x = TRUE)
  m <- max(abs(g_sf$fd), na.rm = TRUE)                  # symmetric scale around 0

  p <- ggplot(g_sf) +
    geom_sf(aes(fill = fd), colour = "white", linewidth = 0.25) +
    geom_sf_text(aes(label = abbrev_state), size = 2.6, colour = bite_pal$ink, fontface = "bold") +
    scale_fill_gradient2(
      low = bite_pal$teal, mid = "#F4F4F2", high = bite_pal$accent, midpoint = 0,
      limits = c(-m, m), name = "Change in admissions per 10,000 (after minus before)",
      guide = guide_colourbar(barwidth = 13, barheight = 0.5, title.position = "top")
    ) +
    labs(title = title,
         subtitle = "Mean of post-adoption years minus the year before adoption, population-weighted to each state",
         x = NULL, y = NULL,
         caption = "Source: SIH/DATASUS, ever-treated municipalities (CAPS cohorts 2003-2016). Dias & Fontes (2024) teaching panel.") +
    coord_sf(datum = NA) +
    theme_bite() +
    theme(plot.title = element_text(size = 15, face = "bold"),
          axis.text = element_blank(), axis.ticks = element_blank(),
          axis.title.x = element_blank(), axis.title.y = element_blank(),
          panel.grid = element_blank(), legend.position = "bottom",
          legend.title = element_text(size = 9, colour = bite_pal$muted, hjust = 0.5))

  ggsave(file, p, width = 8.2, height = 8.6, dpi = 300, bg = "white")
  ggsave(sub("\\.png$", ".pdf", file), p, width = 8.2, height = 8.6, bg = "white")
  cat("Wrote", file, "\n"); print(agg[order(fd)])
}

make_map("sih_tnet_F_esquizofrenia",
         "Schizophrenia admissions: change after CAPS adoption, by state",
         "output/figures/brazil_caps_firstdiff_schiz.png")

make_map("sih_tnet_F",
         "Mental-disorder admissions: change after CAPS adoption, by state",
         "output/figures/brazil_caps_firstdiff_allmh.png")
