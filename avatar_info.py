import json
import re
import cloudscraper

# URLs of JavaScript files
urls = {
	"character": "https://homdgcat.wiki/gi/EN/avatar.js",
	"item": "https://homdgcat.wiki/gi/EN/item.js",
	"weapon": "https://homdgcat.wiki/gi/EN/avatar.js",
	"monster": "https://homdgcat.wiki/gi/EN/computer.js"
}

# Fetch JavaScript content
scraper = cloudscraper.create_scraper()  # This creates a session that can bypass CF
responses = {key: scraper.get(url) for key, url in urls.items()}
for key, response in responses.items():
	response.raise_for_status()

# Extract JSON data using regex
patterns = {
	"character": r'__AvatarInfoConfig\s*=\s*(\[\s*\{[\s\S]*?\}\s*\])(?=\s*var)',
	"item": r'_items\s*=\s*\[.*\].',
	"weapon": r'_WeaponConfig\s*=\s*(\[\s*\{.*?\}\s*\])',
	"monster": r'_Monsters\s*=\s*\{[\s\S]*?\}\s*(?=var\s)'
}

matches = {key: re.search(pattern, responses[key].text, re.DOTALL) for key, pattern in patterns.items()}
if any(match is None for match in matches.values()):
	raise ValueError(f"Could not find required JSON data in the {matches} JavaScript files.")

# Clean and convert data
item_data = matches["item"].group(0).replace("_items = [\n    [],\n    [\n", "[\n").replace("}\n    ]\n]", "}\n]").replace(
	"\n    ],\n    [", ",").replace("],\n    [", "")
monster_data = matches["monster"].group(0).replace("_Monsters = ", "")

# Parse JSON
data = {
	"character": json.loads(matches["character"].group(1)),
	"item": json.loads(item_data),
	"weapon": json.loads(matches["weapon"].group(1)),
	"monster": json.loads(monster_data)
}

# Save extracted data
for key, value in data.items():
	filename = f"exported_{key}_data.json"
	with open(filename, "w", encoding="utf-8") as f:
		json.dump(value, f, indent=4, ensure_ascii=False)
	print(f"Extracted data saved to {filename}.")

# Load the first JSON (monsters data)
with open('exported_monster_data.json', 'r', encoding='utf-8') as file:
	monsters_data = json.load(file)

# Load the second JSON (API data)
url = "https://api.hakush.in/gi/data/monster.json"
response = scraper.get(url)
api_data = response.json()

# Load the classes data from the API
url = "https://homdgcat.wiki/gi/EN/computer.js"
response = scraper.get(url)
classes_data = response.text

# Create a dictionary to map monster names from the API data to their icon names
name_to_icon_map = {}
for key, value in api_data.items():
	name_to_icon_map[value['EN']] = value['icon']

# Use regex to find the section that contains the Kingdoms data
regex_pattern = r"_Kingdoms = \[.*\](?<=]\n    }\n])"
match = re.search(regex_pattern, classes_data, re.DOTALL)

# If we found the match, proceed with parsing
if match:
	json_data = match.group(0)[len("_Kingdoms = "):]  # Remove the "var _Kingdoms = " part
	kingdoms_data = json.loads(json_data)

	# Create a dictionary for quick lookup of which class a monster belongs to
	monster_classes = {}

	# Populate the monster_classes dictionary
	for kingdom in kingdoms_data:
		for monster_class in kingdom['Classes']:
			for monster_id in monster_class['Monsters']:
				monster_classes[monster_id] = monster_class['Name']

	# Function to remove Chinese characters from a string
	def remove_chinese(text):
		return re.sub(r'[\u4e00-\u9fff/·]', '', text)

	# Mapping of old icon names to new values
	icon_conversion_map = {
		"gv": "UI_MonsterIcon_Drake_Rock",
		"pg": "UI_MonsterIcon_Drake_Primo_Rock",
		"pbv": "UI_MonsterIcon_Drake_Deepsea_Water",
		"rbv": "UI_MonsterIcon_Drake_Deepsea_Ice",
		"bbv": "UI_MonsterIcon_Drake_Deepsea_Electric",
		"ib": "UI_MonsterIcon_Invoker_Archdeacon",
		"thhp1": "UI_MonsterIcon_Thoarder_Male_Chemist_Water_01",
		"thep1": "UI_MonsterIcon_Thoarder_Male_Chemist_Electric_01",
		"thcp1": "UI_MonsterIcon_Thoarder_Male_Chemist_Ice_01",
		"thma1": "UI_MonsterIcon_Thoarder_Male_Hunter_01",
		"thpu1": "UI_MonsterIcon_Thoarder_MuscleMan_Boxer_01",
		"moxiang1": "UI_MonsterIcon_Golem_Centaur",
		"chi1": "UI_MonsterIcon_Tartaglia",
		"chi2": "UI_MonsterIcon_Tartaglia",
		"chi3": "UI_MonsterIcon_Tartaglia",
		"las2": "UI_MonsterIcon_LaSignora",
		"nad": "UI_MonsterIcon_Nada",
		"ap": "UI_MonsterIcon_Apep",
		"laopu": "UI_MonsterIcon_Nihil",
	}

	# Mapping for monsters to remove based on Icon values ("lg", "gf", "mot")
	icon_removal_map = ["keq", "lg", "gf", "mot"]

	# List to store monsters to be removed
	monsters_to_remove = []

	# Iterate over the monsters data and update the Icon field
	for monster_id, monster_info in monsters_data.items():
		_id = monster_info.get('_id')
		if _id in monster_classes:
			monster_info['Class'] = monster_classes[_id]

		# Add categories based on kingdoms
		for kingdom in kingdoms_data:
			for monster_class in kingdom['Classes']:
				if _id in monster_class['Monsters']:
					monster_info['Category'] = kingdom['Name']
					break

		# Remove Chinese characters from the Csx field
		if "Csx" in monster_info:
			monster_info["Csx"] = [remove_chinese(csx) for csx in monster_info["Csx"]]

		name = monster_info.get("Name")

		# Check if there's a matching name in the API data
		if name in name_to_icon_map:
			new_icon = name_to_icon_map[name]
			# Update the Icon field
			monster_info['Icon'] = [new_icon]

		# Convert icon names based on the mapping
		if "Icon" in monster_info:
			monster_info["Icon"] = [icon_conversion_map.get(icon, icon) for icon in monster_info["Icon"]]

		# Add to removal list if Icon matches any value in the icon_removal_map
		if "Icon" in monster_info and any(icon in monster_info["Icon"] for icon in icon_removal_map):
			monsters_to_remove.append(monster_id)

	# Remove the monsters that should be removed
	for monster_id in monsters_to_remove:
		del monsters_data[monster_id]

	# Save the updated data back to a JSON file
	with open('exported_monster_data.json', 'w', encoding='utf-8') as file:
		json.dump(monsters_data, file, ensure_ascii=False, indent=4)

	print("Classes and categories updated successfully.")
	print("Icon names updated successfully.")
else:
	print("No matching section found in the data.")
