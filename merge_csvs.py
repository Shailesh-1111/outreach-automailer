import os
import glob
import pandas as pd

source_dir = r"D:\user_2024_03_08\OneDrive\Desktop\Mails\Unsorted_mails\Processed_Companies"
target_file = r"c:\Users\SHAILESH YADAV\outreach_applier\outreach-service\processing_queue\merged_campaign.csv"

all_files = glob.glob(os.path.join(source_dir, "*.csv"))
df_list = []
for f in all_files:
    try:
        df = pd.read_csv(f)
        if not df.empty:
            df_list.append(df)
    except Exception as e:
        pass

if df_list:
    final_df = pd.concat(df_list, ignore_index=True)
    # create processing_queue if it doesn't exist
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    final_df.to_csv(target_file, index=False)
    print(f"Merged {len(df_list)} files. Total rows: {len(final_df)}. Saved to {target_file}")
else:
    print("No CSV files found or all were empty.")
