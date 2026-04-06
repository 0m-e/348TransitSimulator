# -----------------------------
# LOAD DATA
# -----------------------------
test_data <- read.csv("line_32_data.csv", stringsAsFactors = FALSE)
sim_data  <- read.csv("simulation_log2.csv", header = FALSE, stringsAsFactors = FALSE)

# Keep only relevant columns
test <- data.frame(
  Code = test_data$Code,
  Min.Delay = test_data$Min.Delay
)

sim <- data.frame(
  Code = sim_data[[2]],
  Min.Delay = sim_data[[3]]
)

# Clean missing values
test <- test[!is.na(test$Code) & !is.na(test$Min.Delay), ]
sim  <- sim[!is.na(sim$Code) & !is.na(sim$Min.Delay), ]

# Make sure types are appropriate
test$Code <- as.character(test$Code)
sim$Code  <- as.character(sim$Code)

test$Min.Delay <- as.numeric(test$Min.Delay)
sim$Min.Delay  <- as.numeric(sim$Min.Delay)

# -----------------------------
# CODE FREQUENCY COMPARISON
# -----------------------------
all_codes <- union(unique(test$Code), unique(sim$Code))

test_counts <- table(factor(test$Code, levels = all_codes))
sim_counts  <- table(factor(sim$Code, levels = all_codes))

code_table <- rbind(
  Test = as.numeric(test_counts),
  Simulated = as.numeric(sim_counts)
)
colnames(code_table) <- all_codes

print(code_table)

# Chi-square test of homogeneity
chisq_result <- chisq.test(code_table)
print(chisq_result)

# Compare proportions
test_props <- prop.table(test_counts)
sim_props  <- prop.table(sim_counts)

prop_comparison <- data.frame(
  Code = all_codes,
  Test_Proportion = as.numeric(test_props),
  Sim_Proportion = as.numeric(sim_props),
  Abs_Diff = abs(as.numeric(test_props) - as.numeric(sim_props))
)

print(prop_comparison[order(-prop_comparison$Abs_Diff), ])

# -----------------------------
# OVERALL DELAY DISTRIBUTION
# -----------------------------
# Summary statistics
summary_test <- c(
  Mean = mean(test$Min.Delay),
  SD = sd(test$Min.Delay),
  Median = median(test$Min.Delay),
  Q90 = quantile(test$Min.Delay, 0.90),
  Q95 = quantile(test$Min.Delay, 0.95),
  Max = max(test$Min.Delay)
)

summary_sim <- c(
  Mean = mean(sim$Min.Delay),
  SD = sd(sim$Min.Delay),
  Median = median(sim$Min.Delay),
  Q90 = quantile(sim$Min.Delay, 0.90),
  Q95 = quantile(sim$Min.Delay, 0.95),
  Max = max(sim$Min.Delay)
)

summary_comparison <- data.frame(
  Statistic = names(summary_test),
  Test = as.numeric(summary_test),
  Simulated = as.numeric(summary_sim),
  Abs_Diff = abs(as.numeric(summary_test) - as.numeric(summary_sim))
)

print(summary_comparison)

# Kolmogorov-Smirnov test
ks_result <- ks.test(test$Min.Delay, sim$Min.Delay)
print(ks_result)

# Wilcoxon rank-sum test
wilcox_result <- wilcox.test(test$Min.Delay, sim$Min.Delay)
print(wilcox_result)

# t-test for means (optional)
ttest_result <- t.test(test$Min.Delay, sim$Min.Delay)
print(ttest_result)

# -----------------------------
# PER-CODE DISTRIBUTION TESTS
# -----------------------------
min_n <- 20   # minimum observations required in BOTH sets for testing
results_by_code <- data.frame()

for (code in all_codes) {
  test_sub <- test$Min.Delay[test$Code == code]
  sim_sub  <- sim$Min.Delay[sim$Code == code]
  
  n_test <- length(test_sub)
  n_sim  <- length(sim_sub)
  
  if (n_test >= min_n && n_sim >= min_n) {
    ks_p <- tryCatch(ks.test(test_sub, sim_sub)$p.value, error = function(e) NA)
    wil_p <- tryCatch(wilcox.test(test_sub, sim_sub)$p.value, error = function(e) NA)
    
    row <- data.frame(
      Code = code,
      N_Test = n_test,
      N_Sim = n_sim,
      Mean_Test = mean(test_sub),
      Mean_Sim = mean(sim_sub),
      Median_Test = median(test_sub),
      Median_Sim = median(sim_sub),
      SD_Test = sd(test_sub),
      SD_Sim = sd(sim_sub),
      KS_p_value = ks_p,
      Wilcox_p_value = wil_p
    )
    
    results_by_code <- rbind(results_by_code, row)
  }
}

print(results_by_code)

# -----------------------------
# EXTREME DELAY RATES
# -----------------------------
thresholds <- c(5, 10, 20, 30, 60)

tail_results <- data.frame()

for (thr in thresholds) {
  row <- data.frame(
    Threshold = thr,
    Test_Prob = mean(test$Min.Delay >= thr),
    Sim_Prob = mean(sim$Min.Delay >= thr)
  )
  row$Abs_Diff <- abs(row$Test_Prob - row$Sim_Prob)
  tail_results <- rbind(tail_results, row)
}

print(tail_results)

# -----------------------------
# HISTOGRAMS / DENSITIES
# -----------------------------
par(mfrow = c(1, 2))

hist(test$Min.Delay, breaks = 30, main = "Testing Data Delays",
     xlab = "Delay (minutes)", col = "lightblue", border = "white")

hist(sim$Min.Delay, breaks = 30, main = "Simulated Data Delays",
     xlab = "Delay (minutes)", col = "salmon", border = "white")

# Overlay density curves
par(mfrow = c(1,1))
plot(density(test$Min.Delay, na.rm = TRUE), lwd = 2,
     main = "Delay Density: Test vs Simulated", xlab = "Delay (minutes)")
lines(density(sim$Min.Delay, na.rm = TRUE), lwd = 2, lty = 2)
legend("topright", legend = c("Test", "Simulated"), lwd = 2, lty = c(1,2))

# -----------------------------
# CODE PROPORTION BARPLOT
# -----------------------------
barplot(
  rbind(as.numeric(prop.table(test_counts)),
        as.numeric(prop.table(sim_counts))),
  beside = TRUE,
  names.arg = all_codes,
  las = 2,
  col = c("lightblue", "salmon"),
  main = "Code Proportions: Test vs Simulated",
  ylab = "Proportion"
)
legend("topright", legend = c("Test", "Simulated"),
       fill = c("lightblue", "salmon"))


# -----------------------------
# VALIDATION SCORECARD
# -----------------------------
validation_scorecard <- data.frame(
  Metric = c(
    "Mean delay",
    "Median delay",
    "SD delay",
    "90th percentile",
    "95th percentile",
    "P(delay >= 10)",
    "P(delay >= 20)",
    "P(delay >= 30)"
  ),
  Test = c(
    mean(test$Min.Delay),
    median(test$Min.Delay),
    sd(test$Min.Delay),
    quantile(test$Min.Delay, 0.90),
    quantile(test$Min.Delay, 0.95),
    mean(test$Min.Delay >= 10),
    mean(test$Min.Delay >= 20),
    mean(test$Min.Delay >= 30)
  ),
  Simulated = c(
    mean(sim$Min.Delay),
    median(sim$Min.Delay),
    sd(sim$Min.Delay),
    quantile(sim$Min.Delay, 0.90),
    quantile(sim$Min.Delay, 0.95),
    mean(sim$Min.Delay >= 10),
    mean(sim$Min.Delay >= 20),
    mean(sim$Min.Delay >= 30)
  )
)

validation_scorecard$Abs_Diff <- abs(validation_scorecard$Test - validation_scorecard$Simulated)

print(validation_scorecard)


common_breaks <- seq(0, 100, by = 5)

par(mfrow = c(1, 2))

hist(test$Min.Delay,
     breaks = common_breaks,
     main = "Testing Data Delays",
     xlab = "Delay (minutes)",
     col = "lightblue",
     border = "white",
     xlim = c(0, 100))

hist(sim$Min.Delay,
     breaks = common_breaks,
     main = "Simulated Data Delays",
     xlab = "Delay (minutes)",
     col = "salmon",
     border = "white",
     xlim = c(0, 100))