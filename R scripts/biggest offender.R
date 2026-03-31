data <- read.csv("bus_test_data.csv")

# Replace with your column name
col <- data$Line

# Proportions
prop <- prop.table(table(col))
# Find the line with the highest proportion
max_line <- names(prop)[which.max(prop)]
max_value <- max(prop)

# Print result
cat("Most common line:", max_line, "\n")
cat("Proportion:", max_value, "\n")
#write.csv(as.data.frame(prop), "bus_line_proportions.csv", row.names = FALSE)