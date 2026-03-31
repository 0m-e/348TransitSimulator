data <- read.csv("streetcar_train_data.csv")

# Replace with your column name
col <- data$Code

# Proportions
prop <- prop.table(table(col))

# View results
print(prop)
str(prop)
write.csv(as.data.frame(prop), "streetcar_proportions.csv", row.names = FALSE)