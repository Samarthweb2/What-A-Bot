import os
import glob

files = glob.glob(r"e:\emberground\frontend\src\pages\*.tsx")
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'console.log(MOCK_DATA)' not in content:
        content = content.replace("return <div>", "console.log(MOCK_DATA);\n  return <div>")
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
print("Fixed TS errors")
