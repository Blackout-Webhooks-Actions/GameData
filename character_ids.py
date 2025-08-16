import json
import requests

# URLs
avatar_url = "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/ExcelBinOutput/AvatarExcelConfigData.json"
textmap_url = "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/TextMap/TextMapEN.json"

# Download JSON files
avatar_data = requests.get(avatar_url).json()
textmap_data = requests.get(textmap_url).json()

# Result mapping: {id: name}
result = {}

for entry in avatar_data:
	avatar_id = entry.get("id")
	name_hash = str(entry.get("nameTextMapHash"))  # keys in TextMap are strings
	name_value = textmap_data.get(name_hash, None)

	if avatar_id and name_value:
		result[avatar_id] = name_value

# Save to JSON file
with open("avatar_names.json", "w", encoding="utf-8") as f:
	json.dump(result, f, ensure_ascii=False, indent=2)

print("Saved avatar_names.json with", len(result), "entries.")
