# ================================
# Train-Test Split (80-20)
# ================================

# 1. Load dataset
data <- read.csv("TTC Bus Delay Data since 2025.csv")

# 2. Set seed for reproducibility
set.seed(123)

# 3. Get number of rows
n <- nrow(data)

# 4. Create random indices for training set (80%)
train_indices <- sample(1:n, size = 0.8 * n)

# 5. Split the data
train_data <- data[train_indices, ]
test_data  <- data[-train_indices, ]

# 6. (Optional) Check sizes
cat("Training rows:", nrow(train_data), "\n")
cat("Testing rows:", nrow(test_data), "\n")

# 7. (Optional) Save to CSV
write.csv(train_data, "bus_train_data.csv", row.names = FALSE)
write.csv(test_data, "bus_test_data.csv", row.names = FALSE)

