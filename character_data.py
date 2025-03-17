import json
import requests
import re

# Load character_data.json
with open("character_data.json", "r", encoding="utf-8") as f:
	original_data = json.load(f)

# Load data from exported_character_data.json
with open("exported_character_data.json", "r", encoding="utf-8") as f:
	character_data = json.load(f)

# Load image mapping data
with open("image_mapping_data.json", "r", encoding="utf-8-sig") as f:
	image_mapping = json.load(f)

# Load material mapping data
with open("material_mapping_data.json", "r", encoding="utf-8-sig") as f:
	material_mapping = json.load(f)

# Element mapping
element_mapping = {
	"Wind": "Anemo",
	"Ice": "Cryo",
	"Grass": "Dendro",
	"Elec": "Electro",
	"Rock": "Geo",
	"Water": "Hydro",
	"Fire": "Pyro"
}

# Weapon mapping
weapon_mapping = {
	"Pole": "Polearm"
}

# Gem mapping
gem_mapping = {
	"Anemo": "Vayuda Turquoise",
	"Cryo": "Shivada Jade",
	"Dendro": "Nagadus Emerald",
	"Electro": "Vajrada Amethyst",
	"Geo": "Prithiva Topaz",
	"Hydro": "Varunada Lazurite",
	"Pyro": "Agnidus Agate"
}

traveler_ascension_materials = {
	"enemyDrop": "Hilichurl Materials",
	"elementalGem": "Brilliant Diamond",
	"localSpecialty": "Windwheel Aster"
}

# Define materials for each Traveler element
traveler_materials = {
	"Anemo": {
		"materials": [
			{
				"ascension": [traveler_ascension_materials],
				"talents": [
					{
						"enemyDrop": "Samachurl Materials",
						"weeklyBossDrop": "Dvalin's Sigh",
						"travelertalentBooks": [
							{
								"teachings": "Freedom",
								"guide1": "Resistance",
								"guide2": "Ballad",
								"guide3": "Freedom",
								"philosophies1": "Ballad",
								"philosophies2": "Freedom",
								"philosophies3": "Resistance"
							}
						]
					}
				]
			}
		]
	},
	"Geo": {
		"materials": [
			{
				"ascension": [traveler_ascension_materials],
				"talents": [
					{
						"enemyDrop": "Samachurl Materials",
						"enemyDrop2": "Hilichurl Shooter Materials",
						"weeklyBossDrop": "Dvalin's Sigh",
						"weeklyBossDrop2": "Tail of Boreas",
						"travelertalentBooks": [
							{
								"teachings": "Freedom",
								"guide1": "Resistance",
								"guide2": "Ballad",
								"guide3": "Freedom",
								"philosophies1": "Ballad",
								"philosophies2": "Freedom",
								"philosophies3": "Resistance"
							}
						],
						"travelertalentBooks2": [
							{
								"teachings": "Prosperity",
								"guide1": "Diligence",
								"guide2": "Gold",
								"guide3": "Prosperity",
								"philosophies1": "Prosperity",
								"philosophies2": "Gold",
								"philosophies3": "Diligence"
							}
						]
					}
				]
			}
		]
	},
	"Electro": {
		"materials": [
			{
				"ascension": [traveler_ascension_materials],
				"talents": [
					{
						"enemyDrop": "Nobushi Materials",
						"weeklyBossDrop": "Dragon Lord's Crown",
						"travelertalentBooks": [
							{
								"teachings": "Transience",
								"guide1": "Elegance",
								"guide2": "Light",
								"guide3": "Transience",
								"philosophies1": "Light",
								"philosophies2": "Transience",
								"philosophies3": "Elegance"
							}
						]
					}
				]
			}
		]
	},
	"Dendro": {
		"materials": [
			{
				"ascension": [traveler_ascension_materials],
				"talents": [
					{
						"enemyDrop": "Fungus Materials",
						"weeklyBossDrop": "Mudra of the Malefic General",
						"travelertalentBooks": [
							{
								"teachings": "Admonition",
								"guide1": "Ingenuity",
								"guide2": "Praxis",
								"guide3": "Admonition",
								"philosophies1": "Praxis",
								"philosophies2": "Admonition",
								"philosophies3": "Ingenuity"
							}
						]
					}
				]
			}
		]
	},
	"Hydro": {
		"materials": [
			{
				"ascension": [traveler_ascension_materials],
				"talents": [
					{
						"enemyDrop": "Fontemer Aberrant Materials",
						"weeklyBossDrop": "Worldspan Fern",
						"travelertalentBooks": [
							{
								"teachings": "Equity",
								"guide1": "Justice",
								"guide2": "Order",
								"guide3": "Equity",
								"philosophies1": "Order",
								"philosophies2": "Equity",
								"philosophies3": "Justice"
							}
						]
					}
				]
			}
		]
	},
	"Pyro": {
		"materials": [
			{
				"ascension": [traveler_ascension_materials],
				"talents": [
					{
						"enemyDrop": "Sauroform Tribal Warrior Materials",
						"weeklyBossDrop": "The Cornerstone of Stars and Flames",
						"travelertalentBooks": [
							{
								"teachings": "Contention",
								"guide1": "Kindling",
								"guide2": "Conflict",
								"guide3": "Contention",
								"philosophies1": "Conflict",
								"philosophies2": "Contention",
								"philosophies3": "Kindling"
							}
						]
					}
				]
			}
		]
	}
}

# Create a dictionary of reruns from the original file for easy lookup
reruns_dict = {char["name"]: char["reruns"] for char in original_data}


# Function to get material section based on item name
def get_material_section(item_name):
	for section, data in material_mapping.items():
		if item_name in [data["itemName1"], data["itemName2"], data["itemName3"]]:
			return section
	return item_name  # Return the original name if no match is found


# Function to format the birthday as "MM-DD"
def format_birthday(birthday):
	month, day = birthday.split("/")
	return f"{int(month):02d}-{int(day):02d}"


# Identify travelers (e.g., based on a specific ID or other criteria)
travelers = [char for char in character_data if char["Name"] == "Traveler"]
other_characters = [char for char in character_data if char["Name"] != "Traveler"]

# Set Keqing's version to 1.0
for char in other_characters:
	if char["Name"] == "Keqing":
		char["Version"] = "1.0"
	if "Version" in char:
		char["Version"] = re.sub(r"v\d+$", "", char["Version"])

# Sort the characters by their ID
travelers.sort(key=lambda x: x["_id"])
other_characters.sort(key=lambda x: (x["Version"], x["_id"]))

# Merge the travelers at the top and sorted characters below
final_data = travelers + other_characters

# Create the character data with Paimon added to the top
paimon_data = {
	"name": "Paimon",
	"birthday": "06-01",
	"reruns": []
}


# Function to get the key from the value in the dictionary
def get_item_name(item_id):
	# Loop through all categories and items to find the name associated with the given ID
	for category, items in image_mapping["Items"].items():
		for item_name, _id in items.items():
			if _id == item_id:
				return item_name
	return None  # Return None if the item ID is not found


# Get all subcategories under "Items"
enemy_drop_materials = image_mapping["Items"]["Character and Weapon Enhancement Material"]

# Extract required fields
filtered_data = (
		[
			paimon_data  # Add Paimon data to the top
		] +
		[
			{
				"id": char["_id"],
				"name": char["Name"],
				**({"male_name": "Aether"} if char["Name"] == "Traveler" else {}),
				**({"female_name": "Lumine"} if char["Name"] == "Traveler" else {}),
				**({"constellation": char["Constellation"]} if char["Name"] != "Traveler" else {}),
				**({"male_constellation": "Viator"} if char["Name"] == "Traveler" else {}),
				**({"female_constellation": "Viatrix"} if char["Name"] == "Traveler" else {}),
				"version": char["Version"],
				"star": char["Grade"],
				"nation": char["Nation"],
				"element": element_mapping.get(char["Element"], char["Element"]),  # Replace if in mapping
				"weapon": weapon_mapping.get(char["Weapon"], char["Weapon"]),  # Replace if in mapping
				**({"birthday": format_birthday(char["Birthday"])} if char["Name"] != "Traveler" else {}),
				"title": char["Title"],
				"description": char["Desc"],
				"reruns": reruns_dict.get(char["Name"], []),  # Add reruns data if available
				**({"materials": [
					{
						"ascension": [
							{
								"enemyDrop": get_material_section(get_item_name(char["CommonMatt"])),
								"elementalGem": gem_mapping.get(element_mapping.get(char["Element"], char["Element"]), char["Element"]),
								"normalBossDrop": get_item_name(char["AscMat"]),
								"localSpecialty": get_item_name(char["SpecialityMat"])
							}
						],
						"talents": [
							{
								"enemyDrop": get_material_section(get_item_name(char["CommonMatt"])),
								"weeklyBossDrop": get_item_name(char["WeekMat"]),
								"talentBooks": get_item_name(char["TalentMatt"]).split(" ")[-1] ,
								# "talentBooks": [next((key.split(" ")[-1] for key, value in category.items() if value == str(char["TalentMatt"])), char["TalentMatt"]) for category in items_categories.values()]
							}
						]
					}
				]} if char["Name"] != "Traveler" else traveler_materials.get(element_mapping.get(char["Element"], char["Element"]), {}))
			}
			for char in final_data if char["Constellation"].lower() != "viator"
		]
)

# Save to character_data.json
with open("character_data.json", "w", encoding="utf-8") as f:
	json.dump(filtered_data, f, indent=4, ensure_ascii=False)

print("Filtered data saved to character_data.json.")
