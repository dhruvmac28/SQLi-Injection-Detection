import pandas as pd

# Read the first CSV file
df1 = pd.read_csv("SQLiDataset.csv")

# Read the second CSV file
df2 = pd.read_csv("SQLiDataset-02.csv")

# Concatenate the two dataframes vertically (along rows)
merged_df = pd.concat([df1, df2], ignore_index=True)

# Save the merged dataframe to a new CSV file
merged_df.to_csv("SQLi-Dataset.csv", index=False)

print("Merged dataset saved successfully.")