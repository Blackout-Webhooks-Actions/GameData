import os
import json

# Check if image_mapping_data.json exists
if os.path.exists('image_mapping_data.json'):
	# Load the existing image mapping data
	with open('image_mapping_data.json', 'r', encoding='utf-8') as file:
		image_mapping_data = json.load(file)
else:
	# If the file doesn't exist, create an empty dictionary
	image_mapping_data = {}

# Load the character data from the exported JSON file
with open('exported_character_data.json', 'r', encoding='utf-8') as file:
	character_data = json.load(file)

# Load the item data from the exported JSON file
with open('exported_item_data.json', 'r', encoding='utf-8') as file:
	item_data = json.load(file)

# Load the weapon data from the exported JSON file
with open('exported_weapon_data.json', 'r', encoding='utf-8') as file:
	weapon_data = json.load(file)

# Load the monster data from the exported JSON file
with open('exported_monster_data.json', 'r', encoding='utf-8') as file:
	monster_data = json.load(file)

# Initialize the Characters dictionary
Characters = {}

# Iterate through the character data and check for mismatched names
for character in character_data:
	name = character.get("Name")
	_name = character.get("_name")

	# Skip if the name is "Traveler"
	if name == "Traveler" or _name == "Keqing2":
		continue

	# Check if Name and _name are different
	if name != _name:
		# Add the character to the Characters dictionary
		Characters[name] = _name

# Add the Characters dictionary inside the image_mapping_data object
image_mapping_data['Characters'] = Characters

# Initialize the Items dictionary
Items = {}

# Iterate through the item data and update the Name field
for item in item_data:
	name = item.get("Name")
	_id = item.get("_id")
	_type = item.get("Type")

	# Skip if the name is empty
	if name == "":
		continue

	if _type:
		# Check if _type starts with "Local Specialty"
		if _type.startswith("Local Specialty"):
			item_type = "Local Specialty"
		else:
			item_type = _type
	elif _id.__str__().startswith("2100") | _id.__str__().startswith("2101") | _id.__str__().startswith("2102"):
		item_type = "Namecards"
	elif _id.__str__().startswith("100244") | _id.__str__().startswith("1003") | _id.__str__().startswith("1012") | _id.__str__().startswith("1080") | _id.__str__().startswith("1081") | _id.__str__().startswith("1082") | _id.__str__().startswith("1083") | _id.__str__().startswith("1084") | _id.__str__().startswith("1085") | _id.__str__().startswith("1086") | _id.__str__().startswith("1087") | _id.__str__().startswith("1088") | _id.__str__().startswith("1110"):
		item_type = "Food"
	elif _id.__str__().startswith("2150"):
		item_type = "Envisaged Echoes"
	elif _id.__str__().startswith("1000") | _id.__str__().startswith("1001") | _id.__str__().startswith("1002"):
		item_type = "Profile Pictures"
	else:
		item_type = "Miscellaneous"

	# Initialize the list for this item type if it doesn't exist
	if item_type not in Items:
		Items[item_type] = {}

	# Add the item to the Items dictionary
	Items[item_type][name] = _id


# Add the Items dictionary inside the image_mapping_data object
image_mapping_data['Items'] = Items

# Initialize the Weapons dictionary
Weapons = {}

# Iterate through the weapon data and update the Name field
for weapon in weapon_data:
	name = weapon.get("Name")
	icons = weapon.get("Icons")

	if icons:
		# Get the first icon and remove the "UI_EquipIcon_" prefix
		new_name = icons.replace("UI_EquipIcon_", "")

		# Extract weapon type (first part of the new_name)
		weapon_type = new_name.split('_')[0]

		# Special case for "Pole" to map to "polearm"
		if weapon_type == "Pole":
			weapon_type = "Polearm"

		# Initialize the list for this weapon type if it doesn't exist
		if weapon_type not in Weapons:
			Weapons[weapon_type] = {}

		# Add the weapon to the appropriate weapon type array
		Weapons[weapon_type][name] = new_name

# Add the Weapons dictionary inside the image_mapping_data object
image_mapping_data['Weapons'] = Weapons

# Initialize the Monster dictionary
Monsters = {}

# Iterate through the monster data and update the Name field
for monster in monster_data.items():
	name = monster[1].get("Name")
	icon = monster[1].get("Icon")[0]
	_category = monster[1].get("Category")

	# Skip if the name is empty
	if name == "":
		continue

	if _category:
		monster_category = _category

		# Initialize the list for this monster category if it doesn't exist
		if monster_category not in Monsters:
			Monsters[monster_category] = {}

		# Add the monster to the appropriate weapon type array
		Monsters[monster_category][name] = icon
	else:
		if "Miscellaneous" not in Monsters:
			Monsters["Miscellaneous"] = {}
		Monsters["Miscellaneous"][name] = icon

# Manually add Oceanid to Elemental Lifeforms
if "Elemental Lifeforms" in Monsters:
	Monsters["Elemental Lifeforms"]["Oceanid"] = "UI_MonsterIcon_Oceanid"
else:
	Monsters["Elemental Lifeforms"] = {
		"Oceanid": "UI_MonsterIcon_Oceanid"
	}

# Add the Monsters dictionary inside the image_mapping_data object
image_mapping_data['Monsters'] = Monsters

# Save the updated image mapping data back to the JSON file
with open('image_mapping_data.json', 'w', encoding='utf-8') as file:
	json.dump(image_mapping_data, file, ensure_ascii=False, indent=4)

print("File updated successfully.")
