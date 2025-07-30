import json
from collections import defaultdict
import re
import difflib

# Load item data
with open("exported_item_data.json", "r", encoding="utf-8") as f:
	item_data = json.load(f)

# Load image data
with open("image_mapping_data.json", "r", encoding="utf-8") as f:
	image_data = json.load(f)

material_mapping = {}

# Flatten enemy names from image_mapping_data.json
enemy_names = []
for category in image_data.get("Monsters", {}).values():
	enemy_names.extend(category.keys())

# Helper groupings
grouped_by_base_name = defaultdict(list)
gem_stars = {
	2: "star2",
	3: "star3",
	4: "star4",
	5: "star5"
}

# Go through all items
def strip_level(enemy_name):
	return re.sub(r"(Lv\.? ?30\+|70\+)\s*", "", enemy_name)

def singularize(name):
	# Avoid altering names ending in any of these suffixes
	blacklist_suffixes = ("Regisvines", "Drakes", "Matricis", "horses", "Statues")

	if name.endswith("es") and not name.endswith(blacklist_suffixes):
		return name[:-2] + "is"
	if name.endswith("s") and not name.endswith(("ss", "is")):
		return name[:-1]
	return name

manual_boss_overrides = {
	"Shouki no Kami, the Prodigal": "Shouki no Kami P1",
	"Wolf of the North": "Lupus Boreas, Dominator of Wolves",
	"Childe": "Childe P1",
	"Signora": "Crimson Witch of Embers",
	"Guardian of Eternity": "Magatsu Mitake Narukami no Mikoto",
	"Guardian of Apep's Oasis": "Warden of Oasis Prime",
	"Primo Geovishap": "Hydro Primo Geovishap",
	"Bathysmal Vishap Herd": "Coral Defenders",
	"Semi-Intransient Matrices": "Algorithm of Semi-Intransient Matrix of Overseer Network",
	"Iniquitous Baptist": "Iniquitous Baptist - Invoker of Flame, Frost, and Fulmination",
	"Legatus Golem": "\"Statue of Marble and Brass\"",
	"Tenebrous Papilla": "Tenebrous Papilla: Type I",
}

boss_items = []

for item in item_data:
	name = item["Name"]
	typ = item.get("Type")
	if typ is None:
		continue

	src = item.get("Src", [])
	rarity = item.get("R", 0)

	# Group talent books by base name
	if typ == "Character Talent Material":
		if "Teachings of" in name:
			base = name.replace("Teachings of ", "")
			mapping = material_mapping.setdefault(base, {})
			mapping["teachings"] = name
		elif "Guide to" in name:
			base = name.replace("Guide to ", "")
			mapping = material_mapping.setdefault(base, {})
			mapping["guide"] = name
		elif "Philosophies of" in name:
			base = name.replace("Philosophies of ", "")
			mapping = material_mapping.setdefault(base, {})
			mapping["philosophies"] = name

	# Group elemental gems
	elif typ == "Character Ascension Material" and ("Gemstone" in name or "Chunk" in name or "Fragment" in name or "Sliver" in name):
		base = name.replace(" Gemstone", "").replace(" Chunk", "").replace(" Fragment", "").replace(" Sliver", "")
		star_key = gem_stars.get(rarity)
		if not star_key:
			continue

		# Track each star tier seen for this base
		mapping = material_mapping.setdefault(base, {})
		mapping[star_key] = name

	# Group enhancement materials (enemy drop)
	elif typ == "Character and Weapon Enhancement Material":
		grouped_by_base_name[name.split(" ")[-1]].append(item)

	# Collect boss drop candidates for sorting
	elif typ == "Character Level-Up Material" and src and any("Dropped by" in s or "Challenge Reward" in s for s in src):
		boss_items.append((rarity, item))

# Process boss items sorted by R=4 first
for rarity in [4, 5]:
	for r, item in boss_items:
		if r != rarity:
			continue

		name = item["Name"]
		src = item.get("Src", [])

		# Special case: Artificed Spare Clockwork Component
		if "Artificed Spare Clockwork Component" in name:
			boss_name = name.replace("Artificed Spare Clockwork Component — ", "")
			name_map = {
				"Coppelius": "Nemesis of Coppelius",
				"Coppelia": "Dirge of Coppelia"
			}
			boss_name = name_map.get(boss_name, boss_name)
			material_mapping[name] = {
				"bossName": f"Icewind Suite: {boss_name}",
				"itemName": name
			}
			continue

		for s in src:
			if "Dropped by" in s or "Reward" in s:
				enemy_name = s.split("Dropped by Lv. 30+")[-1].strip()
				enemy_name = s.split("Dropped by")[1].strip() if "Dropped by" in s else enemy_name
				enemy_name = s.split("Challenge Reward")[-2].split("Lv.")[-1].strip() if "Challenge Reward" in s else enemy_name

				enemy_name = strip_level(enemy_name)
				enemy_name = singularize(enemy_name)

				# Manual override first
				if enemy_name in manual_boss_overrides:
					new_name = manual_boss_overrides[enemy_name]
					enemy_name = new_name

				# Only insert if not already mapped (R=4 wins)
				if name not in material_mapping:
					material_mapping[name] = {
						"bossName": enemy_name,
						"itemName": name
					}
				break

def extract_enemy_name(src_entry):
	match = re.search(r"Dropped by(?: Lv\. \d+\+)? ([\w\s\-\':]+)", src_entry)
	if match:
		name = match.group(1).strip()
		if name.startswith("The "):
			name = name[4:]  # manually remove "The "
		return name
	return None

# Finalize enemy drops into triplets
enhancement_groups = defaultdict(list)
for item in item_data:
	if item.get("Type") != "Character and Weapon Enhancement Material":
		continue

	name = item["Name"]
	if not name:
		continue

	for src_entry in item.get("Src", []):
		enemy = extract_enemy_name(src_entry)
		if enemy:
			group_key = f"{enemy} Materials"
			enhancement_groups[group_key].append(name)

# Fix capitalization of keys in enhancement_groups
fixed_enhancement_groups = defaultdict(list)

for group, names in enhancement_groups.items():
	base_name = group.replace(" Materials", "")
	fixed_base_name = base_name.title()
	fixed_key = f"{fixed_base_name} Materials"
	fixed_enhancement_groups[fixed_key].extend(names)

enhancement_groups = fixed_enhancement_groups

# Manual group name merges
enhancement_group_merges = {
	"Vishap Materials": [
		"Geovishap Hatchlings Materials",
		"Geovishaps Materials",
		"Bathysmal Vishaps Materials"
	],
	"Ruin Guards Materials": [
		"Ruin Guards Materials",
		"Ruin Hunters Materials"
	],
	"Mitachurls Materials": [
		"Mitachurls Materials",
		"Lawachurls Materials"
	]
}

# Apply merges
for merged_name, source_groups in enhancement_group_merges.items():
	merged_items = set()
	for group in source_groups:
		merged_items.update(enhancement_groups.get(group, []))
		enhancement_groups.pop(group, None)  # remove originals
	enhancement_groups[merged_name] = sorted(merged_items)

manual_closest_enemy_overrides = {
	"Fatui Oprichniki Materials": "Oprichniki Fireblade Shock Trooper",
	"Mitachurls Materials": "Wooden Shieldwall Mitachurl",
	"Vishap Materials": "Hydro Geovishap",
	"Ruin Drakes Materials": "Ruin Drake: Skywatch",
	"Riftwolves Materials": "Rockfond Rifthound Whelp",
	"Clockwork Meka Materials": "Annihilation Specialist Mek - Ousia",
	"Fontemer Aberrants Materials": "Sternshield Crab",
	"Sauroform Tribal Warriors Materials": "Yumkasaurus Warrior: Flowing Skyfire",
	"Natlan Saurians Materials": "Iktomisaurus",
	"Wasteland Wild Hunt Materials": "Wilderness Hunter",
	"Fungi Materials": "Floating Dendro Fungus"
}

# Fuzzy match function to find closest enemy name from image data
def get_closest_enemy_name(name):
	# Manual override first
	if name in manual_closest_enemy_overrides:
		new_name = manual_closest_enemy_overrides[name]
		return new_name

	# Remove " Materials" suffix if present
	clean_name = name.replace(" Materials", "").strip()

	# Priority 1: Exact or partial containment match
	containment_matches = [enemy for enemy in enemy_names if clean_name.lower() in enemy.lower()]
	if containment_matches:
		# Prefer the longest match (most specific)
		return max(containment_matches, key=len)

	# Priority 2: Fuzzy fallback
	matches = difflib.get_close_matches(clean_name, enemy_names, n=1, cutoff=0.6)
	return matches[0] if matches else clean_name

# Create rarity lookup once
item_rarity_lookup = {item["Name"]: item.get("R", 0) for item in item_data}

# Finalize enhancement triplets
for group, names in enhancement_groups.items():
	if len(names) >= 3:
		# If more than 3, take the last 3 only
		relevant_names = names[-3:] if len(names) > 3 else names
		sorted_items = sorted(relevant_names, key=lambda n: (item_rarity_lookup.get(n, 0), n.lower()))
		closest_enemy = get_closest_enemy_name(group)
		material_mapping[group] = {
			"enemyName": closest_enemy,
			"itemName1": sorted_items[0],
			"itemName2": sorted_items[1],
			"itemName3": sorted_items[2]
		}

# Save the output JSON
with open("material_mapping_data.json", "w", encoding="utf-8") as f:
	json.dump(material_mapping, f, indent=4, ensure_ascii=False)

print("✅ material_mapping_data.json generated.")
