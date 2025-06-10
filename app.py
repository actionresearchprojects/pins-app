#!/usr/bin/env python3
"""
Enhanced CLI for generating a pins.json entry with robust validation.
Includes GDPR-masked coordinates and enriched climate zone selection.
"""

import json
import math
import random
import re

# Climate zones with labels and colours
CLIMATE_ZONES = {
    'Af': ('Tropical Rainforest', '#0000fe'),
    'Am': ('Tropical Monsoon', '#0078ff'),
    'Aw': ('Tropical Savannah', '#45aafa'),
    'BWh': ('Hot Desert', '#fe0000'),
    'BWk': ('Cold Desert', '#fe9695'),
    'BSh': ('Hot Steppe', '#f4a500'),
    'BSk': ('Cold Steppe', '#ffdc64'),
    'Csa': ('Hot-Summer Mediterranean', '#ffff00'),
    'Csb': ('Warm-Summer Mediterranean', '#c7c800'),
    'Csc': ('Cold-Summer Mediterranean', '#969600'),
    'Cwa': ('Humid Subtropical (dry winter, hot summer)', '#96ff96'),
    'Cwb': ('Subtropical Highland (dry winter)', '#64c865'),
    'Cwc': ('Cold Subtropical Highland', '#329633'),
    'Cfa': ('Humid Subtropical (no dry season)', '#c9ff51'),
    'Cfb': ('Oceanic', '#65ff51'),
    'Cfc': ('Subpolar Oceanic', '#31c800'),
    'Dsa': ('Hot-Summer Continental (dry summer)', '#ff00fe'),
    'Dsb': ('Warm-Summer Continental (dry summer)', '#c900c8'),
    'Dsc': ('Cold-Summer Continental (dry summer)', '#963295'),
    'Dsd': ('Extremely Cold-Summer Continental (dry summer)', '#963295'),
    'Dwa': ('Humid Continental (dry winter, hot summer)', '#aaafff'),
    'Dwb': ('Humid Continental (dry winter, warm summer)', '#5a77db'),
    'Dwc': ('Subarctic (dry winter, cold summer)', '#4b50b4'),
    'Dwd': ('Extremely Cold Subarctic (dry winter)', '#320087'),
    'Dfa': ('Humid Continental (no dry season, hot summer)', '#00ffff'),
    'Dfb': ('Humid Continental (no dry season, warm summer)', '#37c8ff'),
    'Dfc': ('Subarctic (no dry season, cold summer)', '#007e7d'),
    'Dfd': ('Extremely Cold Subarctic (no dry season)', '#00465f'),
    'ET': ('Tundra', '#b2b2b2'),
    'EF': ('Ice Cap', '#666666'),
}

HEX_COLOR_RE = re.compile(r'^#(?:[0-9A-Fa-f]{3}){1,2}$')
URL_RE = re.compile(
    r'^(https?:\/\/)'                              # http:// or https://
    r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6}'             # domain...
    r'|localhost'                                  # localhost...
    r'|\d{1,3}(?:\.\d{1,3}){3})'                    # ...or IPv4
    r'(?::\d+)?'                                    # optional port
    r'(?:\/\S*)?$'                                 # optional path
)

def is_valid_url(url):
    return bool(URL_RE.match(url))

def prompt_text(prompt_msg, required=True):
    while True:
        resp = input(prompt_msg).strip()
        if not resp and required:
            print("This field is required.")
        else:
            return resp

def prompt_choice(prompt_msg, choices):
    choices_lower = {c.lower(): c for c in choices}
    while True:
        resp = input(prompt_msg).strip().lower()
        if resp in choices_lower:
            return choices_lower[resp]
        print(f"Invalid choice. Valid options: {', '.join(choices)}")

def prompt_url(prompt_msg, required=True):
    while True:
        resp = input(prompt_msg).strip()
        if not resp and not required:
            return ''
        if is_valid_url(resp):
            return resp
        print("Invalid URL. Please enter a valid http:// or https:// URL.")

def prompt_hex_color(prompt_msg):
    while True:
        resp = input(prompt_msg).strip()
        if HEX_COLOR_RE.match(resp):
            return resp
        print("Invalid hex code. Enter in form #RRGGBB or #RGB.")

def prompt_float(prompt_msg, min_val=None, max_val=None):
    while True:
        resp = input(prompt_msg).strip()
        try:
            val = float(resp)
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"Value must be between {min_val} and {max_val}.")
            else:
                return val
        except ValueError:
            print("Invalid number. Please enter a numeric value.")

def generate_random_coordinate(lat, lon, radius_m=5000):
    lat_rad = math.radians(lat)
    R = 6371000
    d = random.uniform(0, radius_m)
    ang = random.uniform(0, 2 * math.pi)
    dLat = d * math.cos(ang) / R
    dLon = d * math.sin(ang) / (R * math.cos(lat_rad))

    new_lat = math.degrees(lat_rad + dLat)
    new_lon = lon + math.degrees(dLon)

    new_lat = max(min(new_lat, 90), -90)
    new_lon = ((new_lon + 180) % 360) - 180

    return new_lat, new_lon

def main():
    print("\n--- Generate a new pins.json entry ---\n")
    entry = {}
    entry['id'] = prompt_text("Enter a unique ID (e.g. 'site01'): ")
    entry['title'] = prompt_text("Title for popup (e.g. 'House 5'): ")
    entry['link'] = prompt_url("Link URL (http:// or https://, leave blank if none): ", required=False)
    entry['address'] = prompt_text("Address text: ")

    print("\nAvailable climate zones (input code like 'Aw'):")
    for code, (name, hexcol) in CLIMATE_ZONES.items():
        r, g, b = int(hexcol[1:3], 16), int(hexcol[3:5], 16), int(hexcol[5:7], 16)
        label = f"{name} ({code})"
        print(f"\x1b[38;2;{r};{g};{b}m{label}\x1b[0m")

    cz = prompt_choice("Enter climate zone code (e.g. Aw): ", CLIMATE_ZONES.keys())
    zone_name, hexcol = CLIMATE_ZONES[cz]
    entry['zoneText'] = f"{zone_name} ({cz})"
    entry['zoneColour'] = f"#{hexcol}"

    lat = prompt_float("Latitude (decimal degrees): ", -90, 90)
    lon = prompt_float("Longitude (decimal degrees): ", -180, 180)

    gdpr_resp = prompt_choice("GDPR geomasking required? (y/n): ", ['y', 'n', 'yes', 'no'])
    if gdpr_resp.lower() in ('y', 'yes'):
        mlat, mlon = generate_random_coordinate(lat, lon)
        entry['latitude'], entry['longitude'] = mlat, mlon
        entry['gdpr'] = True
        entry['radiusKm'] = 5
    else:
        entry['latitude'], entry['longitude'] = lat, lon
        entry['gdpr'] = False
        entry['radiusKm'] = 0

    entry['imageUrl'] = prompt_url("Image URL (http:// or https://, leave blank if none): ", required=False)
    entry['colour'] = prompt_hex_color("Marker colour hex (e.g. '#FF0000'): ")

    print("\nCopy and paste this JSON object into pins.json:\n")
    print(json.dumps(entry, indent=2))
    print("\n--- End of entry ---\n")

if __name__ == "__main__":
    main()
