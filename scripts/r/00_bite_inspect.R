# 00_bite_inspect.R — LOOK at brazil.dta with our own eyes before building anything.
# REQUIRES: haven >= 2.5, data.table >= 1.14
#
# Stage: 02_bite (analyses/brazil_caps). This script does NOT make the figure.
# Its only job is the Gawande pause for the data: load the real panel, print its
# shape, confirm the two bite variables exist and are what we think they are
# (psychiatric admissions, schizophrenia admissions), find the treatment and
# population columns, and write a slim clean panel for the figure script to read.
#
# Nothing downstream should assume a column exists until this script has confirmed it.

suppressPackageStartupMessages({
  library(haven); library(data.table)
})

RAW   <- "data/raw/brazil.dta"
CLEAN <- "data/clean/brazil_bite_panel.rds"

stopifnot("brazil.dta not found at data/raw/ — intake it first" = file.exists(RAW))

cat("Reading", RAW, "...\n")
dt <- as.data.table(haven::read_dta(RAW))

cat("\n================ SHAPE ================\n")
cat(sprintf("rows: %s   cols: %s\n", format(nrow(dt), big.mark=","), ncol(dt)))

# --- locate the columns we care about ---------------------------------------
hit <- function(pat) grep(pat, names(dt), ignore.case = TRUE, value = TRUE)
cat("\n--- candidate admission vars (sih_tnet*) ---\n"); print(hit("sih_tnet"))
cat("\n--- candidate treatment vars (caps / numcaps / ano_caps) ---\n"); print(hit("caps"))
cat("\n--- candidate id / year vars ---\n"); print(hit("^(ano|year|munic|codmun|ibge|id)"))
cat("\n--- candidate population vars ---\n"); print(hit("(pop|populac)"))

# --- eyeball the two bite series --------------------------------------------
for (v in c("sih_tnet_F", "sih_tnet_F_esquizofrenia")) {
  if (v %in% names(dt)) {
    cat(sprintf("\n--- summary(%s) ---\n", v)); print(summary(dt[[v]]))
    lbl <- attr(dt[[v]], "label"); if (!is.null(lbl)) cat("  label:", lbl, "\n")
  } else cat(sprintf("\n!! %s NOT in data — reconcile against the paper before proceeding\n", v))
}

cat("\nTop-level: inspect the above, then (if structure matches) uncomment the write below.\n")

# --- write a slim clean panel (only columns confirmed present) --------------
# Edit this vector to the REAL names printed above before enabling the write.
want <- c("cod", "uf", "ano", "pop_", "ca", "caps", "sih_tnet_F", "sih_tnet_F_esquizofrenia")
have <- intersect(want, names(dt))
missing <- setdiff(want, names(dt))
if (length(missing)) cat("\nNOTE missing from `want`:", paste(missing, collapse=", "), "\n")

if (length(have) >= 4) {
  slim <- dt[, ..have]
  saveRDS(slim, CLEAN)
  cat("\nWrote", CLEAN, "with cols:", paste(have, collapse=", "), "\n")
} else {
  cat("\nDid NOT write clean panel — adjust `want` to the printed column names first.\n")
}
