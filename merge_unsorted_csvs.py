import os
import glob
import pandas as pd

source_dir = r"D:\user_2024_03_08\OneDrive\Desktop\Mails\Unsorted_mails"
target_file = r"c:\Users\SHAILESH YADAV\outreach_applier\outreach-service\processing_queue\all_mails.csv"

all_files = glob.glob(os.path.join(source_dir, "*.csv"))
df_list = []

def split_name(full_name):
    parts = str(full_name).strip().split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name

for f in all_files:
    try:
        try:
            df = pd.read_csv(f, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(f, encoding='latin1')
            
        df.columns = df.columns.str.strip()
        
        # We need Name, Company Name, Designation, Email Address
        if 'Email Address' in df.columns:
            df = df.dropna(subset=['Email Address'])
            if 'Name' in df.columns:
                df[['first_name', 'last_name']] = df['Name'].apply(lambda x: pd.Series(split_name(x)))
            else:
                df['first_name'] = ''
                df['last_name'] = ''
            
            # Map existing columns to desired ones
            rename_map = {}
            if 'Company Name' in df.columns:
                rename_map['Company Name'] = 'company'
            if 'Designation' in df.columns:
                rename_map['Designation'] = 'position'
            rename_map['Email Address'] = 'email'
            
            df = df.rename(columns=rename_map)
            
            # Ensure columns exist
            for col in ['first_name', 'last_name', 'company', 'position', 'email']:
                if col not in df.columns:
                    df[col] = ''
            
            df = df[['first_name', 'last_name', 'company', 'position', 'email']]
            df_list.append(df)
    except Exception as e:
        print(f"Error reading {f}: {e}")

if df_list:
    final_df = pd.concat(df_list, ignore_index=True)
    final_df['is_sent'] = False
    final_df['verdict'] = ''
    final_df['verdict_group'] = ''
    final_df['is_drafted'] = False
    
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    final_df.to_csv(target_file, index=False)
    print(f"Saved {len(final_df)} records to {target_file}")
else:
    print("No valid CSV files found.")
