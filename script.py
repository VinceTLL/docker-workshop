import os
import re 
from pathlib import Path

current_dir = Path.cwd()
current_file = Path(__file__).name

# file_list = os.listdir()
# for file in file_list:
#   if re.search("txt",file):
#     with open( file,"r") as f:
#       print(f.read())



for filepath in current_dir.iterdir():
  if filepath.name == current_file:
    continue

  print(f" - {filepath.name}")

  if filepath.is_file():
    content = filepath.read_text(encoding = "utf-8")
    print(f" Content: {content}")









#   print_file_content(os.listdir())
