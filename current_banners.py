import json
import requests

# Load local character data
with open("character_data.json", "r", encoding="utf-8") as f:
	character_data = json.load(f)

# Fetch the event calendar JSON
url = "https://raw.githubusercontent.com/Blackout-Webhooks-Actions/GameData/refs/heads/main/gamestats/genshin_event_calendar.json"
response = requests.get(url)
event_calendar = response.json()

# Track whether we processed any banners
processed_any = False

# Helper: Normalize character name comparison
def find_character_entry(name):
	for entry in character_data["characters"]:
		if "name" not in entry:
			continue
		if entry["name"] == name:
			return entry
	return None

# Helper: Check if rerun exists
def has_rerun(entry, start, end, version, wish_type):
	for rerun in entry.get("reruns", []):
		if (
			rerun["startDate"] == start
			and rerun["endDate"] == end
			and rerun["version"] == version
			and rerun["wishType"] == wish_type
		):
			return True
	return False

# Format ISO date to YYYY-MM-DD
def format_date(iso):
	return iso.split("T")[0]

# Generalized banner processor
def process_banners(banners, wish_type):
	global processed_any
	if not banners:
		print("Currently No Banners")
		return

	for banner in banners:
		start = format_date(banner["start_time"])
		end = format_date(banner["end_time"])
		version = banner["version"]

		for char in banner["characters"]:
			entry = find_character_entry(char["name"])
			if entry:
				# Remove any "upcoming" banner reruns if we add a real rerun now
				original_reruns = entry.get("reruns", [])
				entry["reruns"] = [
					r for r in original_reruns if r.get("banner") != "upcoming"
				]

				if not has_rerun(entry, start, end, version, wish_type):
					entry.setdefault("reruns", []).append({
						"startDate": start,
						"endDate": end,
						"version": version,
						"wishType": wish_type
					})
					processed_any = True
			else:
				print(f"⚠️ Character {char['name']} (ID: {char['id']}) not found in character_data.json")


# Collect banners
character_banners = event_calendar.get("character_banners", [])
chronicled_banners = event_calendar.get("chronicled_banners", [])

# Process banners
process_banners(character_banners, "event")
if chronicled_banners:
	process_banners(chronicled_banners, "chronicled")

# Save the updated data
with open("character_data.json", "w", encoding="utf-8") as f:
	json.dump(character_data, f, indent=4, ensure_ascii=False)

if processed_any:
	print("✅ character_data.json has been updated.")
