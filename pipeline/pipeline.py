import sys
import pandas as pd



###########################
#### Simple pipeline######
###########################


print('arguments', sys.argv)
month = int(sys.argv[1])
print(f"hello pipeline month = {month}")


df = pd.DataFrame({"A":[1,2],"B":[3,4] })
df["month"] = month
 
df.to_parquet(f"output_{month}.parquet")  
print(df.head())
 