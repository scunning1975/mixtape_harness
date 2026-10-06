# 01_bite_national_trends.R — bite stage, brazil_caps.
# REQUIRES: data.table >= 1.14, ggplot2 >= 3.5
#
# Question: over 2002–2016, how did public-system psychiatric admissions move nationally,
# and did the schizophrenia subset (the deinstitutionalization margin Dias & Fontes tie to
# homicides) move with them? This is a DESCRIPTIVE national trend — not the ATT.
#
# National quantity = POPULATION-WEIGHTED rate. Each municipality's series is already an
# admissions-per-10,000 rate; weighting by population recovers the true national rate
# (total national admissions ÷ total national population × 10,000), rather than letting
# thousands of tiny municipalities vote equally with big ones. Choice recorded in findings.md.
#
# Figure philosophy (CLAUDE.md): the figure is the star. Title DESCRIBES what is plotted;
# it never states a conclusion. The story — the two series falling as CAPS spreads — is left
# for the reader to see in the lines themselves.

suppressPackageStartupMessages({ library(data.table); library(ggplot2) })
source("scripts/r/_theme_bite.R")

CLEAN <- "data/clean/brazil_bite_panel.rds"
stopifnot("run 00_bite_inspect.R first" = file.exists(CLEAN))
dt <- as.data.table(readRDS(CLEAN))

# guard: the figure must not silently plot the wrong thing
need <- c("ano", "pop_", "sih_tnet_F", "sih_tnet_F_esquizofrenia")
stopifnot("clean panel is missing expected columns" = all(need %in% names(dt)))

dt <- dt[complete.cases(dt[, ..need])]                 # drops the 13 all-NA municipality-years

nat <- dt[, .(
  `All mental disorders` = weighted.mean(sih_tnet_F,               pop_),
  `Schizophrenia`        = weighted.mean(sih_tnet_F_esquizofrenia, pop_)
), by = ano][order(ano)]

long <- melt(nat, id.vars = "ano", variable.name = "series", value.name = "rate")
long[, series := factor(series, levels = c("All mental disorders", "Schizophrenia"))]

ends  <- long[ano == max(ano)]                         # for direct end-of-line labels
cols  <- c(`All mental disorders` = bite_pal$teal, `Schizophrenia` = bite_pal$accent)

p <- ggplot(long, aes(ano, rate, colour = series)) +
  geom_line(linewidth = 1.5, lineend = "round") +
  geom_point(data = long[ano %in% range(ano)], size = 2.6) +
  geom_text(data = ends, aes(label = series), hjust = 0, nudge_x = 0.22,
            fontface = "bold", size = 4.2) +
  coord_cartesian(clip = "off") +
  scale_colour_manual(values = cols) +
  scale_x_continuous(breaks = seq(2002, 2016, 2),
                     limits = c(2002, 2021), expand = expansion(mult = c(0.01, 0))) +
  scale_y_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.06))) +
  labs(
    title    = "Psychiatric hospital admissions in Brazil, 2002–2016",
    subtitle = "Public-system admissions per 10,000 residents · population-weighted national rate",
    x = NULL, y = "Admissions per 10,000 residents",
    caption  = "Source: SIH/DATASUS, 5,476 municipalities. Dias & Fontes (2024) replication panel."
  ) +
  theme_bite()

ggsave("output/figures/brazil_caps_bite.png", p, width = 9.6, height = 5.6, dpi = 300, bg = "white")
ggsave("output/figures/brazil_caps_bite.pdf", p, width = 9.6, height = 5.6, bg = "white")

cat("National rate by year (population-weighted):\n"); print(nat)
cat("\nWrote output/figures/brazil_caps_bite.{png,pdf}\n")
