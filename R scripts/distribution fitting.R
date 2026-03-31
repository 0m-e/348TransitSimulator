# ================================
# Discrete Distribution Fitting by Delay Code
# ================================

  install.packages("fitdistrplus")  # if needed
library(fitdistrplus)
library(dplyr)

# Load data
data <- read.csv("bus_train_data.csv")

# Column names (EDIT THESE)
delay_col <- "Min.Delay"
code_col  <- "Code"

# ----------------
# Clean data
# ----------------
data <- data %>%
  filter(!is.na(.data[[delay_col]]),
         !is.na(.data[[code_col]]))

# Ensure discrete (integer delays)
data[[delay_col]] <- round(data[[delay_col]])

# ----------------
# Split by delay code
# ----------------
split_data <- split(data[[delay_col]], data[[code_col]])

results <- list()

# ----------------
# Fit distributions
# ----------------
for (code in names(split_data)) {
  
  x <- split_data[[code]]
  
  if (length(x) < 20) next
  
  fits <- list()
  
  fits$pois <- try(fitdist(x, "pois"), silent = TRUE)
  fits$nb   <- try(fitdist(x, "nbinom"), silent = TRUE)
  fits$geom <- try(fitdist(x, "geom"), silent = TRUE)
  
  # AIC comparison
  aics <- sapply(fits, function(f) {
    if (class(f)[1] == "try-error") return(Inf)
    f$aic
  })
  
  best_name <- names(which.min(aics))
  best_fit  <- fits[[best_name]]
  
  # ----------------
  # Create PMF function
  # ----------------
  pmf <- function(k) {
    if (best_name == "pois") {
      return(dpois(k, lambda = best_fit$estimate["lambda"]))
    } else if (best_name == "nbinom") {
      return(dnbinom(k,
                     size = best_fit$estimate["size"],
                     mu   = best_fit$estimate["mu"]))
    } else if (best_name == "geom") {
      return(dgeom(k, prob = best_fit$estimate["prob"]))
    }
  }
  
  results[[code]] <- list(
    best_model = best_name,
    parameters = best_fit$estimate,
    AICs = aics,
    pmf = pmf
  )
}
# Initialize empty list to store rows
rows <- list()

for (code in names(results)) {
  
  res <- results[[code]]
  
  model <- res$best_model
  params <- res$parameters
  aics <- res$AICs
  
  # Initialize all possible fields as NA
  lambda <- NA
  size   <- NA
  mu     <- NA
  prob   <- NA
  
  # Fill depending on model
  if (model == "pois") {
    lambda <- params["lambda"]
  } else if (model == "nb") {
    size <- params["size"]
    mu   <- params["mu"]
  } else if (model == "geom") {
    prob <- params["prob"]
  }
  
  # Create consistent row
  row <- data.frame(
    delay_code = code,
    best_model = model,
    lambda = lambda,
    size = size,
    mu = mu,
    prob = prob,
    AIC_pois = aics["pois"],
    AIC_nb   = aics["nbinom"],
    AIC_geom = aics["geom"],
    row.names = NULL
  )
  
  rows[[code]] <- row
}

# Now this WILL work
results_df <- do.call(rbind, rows)

# Save
write.csv(results_df, "bus_delay_model_results.csv", row.names = FALSE)