import streamlit as st
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
    r'^(https?:\/\/)'
    r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6}'
    r'|localhost'
    r'|\d{1,3}(?:\.\d{1,3}){3})'
    r'(?::\d+)?'
    r'(?:\/\S*)?$'
)

def is_valid_url(url):
    return bool(URL_RE.match(url))

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
    st.title("ARC People & Projects Map Entry Generator 🌍")

    st.markdown("### Step 1: Basic Details")
    entry = {}
    entry['id'] = st.text_input("Unique ID (e.g. 'house5')", max_chars=50)
    entry['title'] = st.text_input("Title for popup (e.g. 'House 5')")
    entry['link'] = st.text_input("Link URL (optional, must start with http/https)", value="")

    st.markdown("### Step 2: Location and Climate Zone")
    entry['address'] = st.text_input("Address (for reference)", value="")

    st.markdown("#### Available Climate Zones")
    for code, (name, hexcol) in CLIMATE_ZONES.items():
        label = f"{name} ({code})"
        st.markdown(f"<span style='color:{hexcol}'>{label}</span>", unsafe_allow_html=True)

    selected_codes = st.multiselect(
        "Select between 1 and 3 climate zone codes",
        sorted(CLIMATE_ZONES.keys()),
        max_selections=3
    )
    if not 1 <= len(selected_codes) <= 3:
        st.error("Please select at least 1 and at most 3 climate zones.")
    else:
        entry['zones'] = []
        for code in selected_codes:
            name, hexcol = CLIMATE_ZONES[code]
            entry['zones'].append({
                'code': code,
                'text': f"{name} ({code})",
                'colour': hexcol
            })

    lat = st.number_input("Latitude (decimal degrees)", -90.0, 90.0, format="%.6f")
    lon = st.number_input("Longitude (decimal degrees)", -180.0, 180.0, format="%.6f")

    st.markdown("### Step 3: GDPR Masking")
    gdpr_mask = st.radio("GDPR geomasking required?", options=["Yes", "No"])
    if gdpr_mask == "Yes":
        mlat, mlon = generate_random_coordinate(lat, lon)
        entry['latitude'], entry['longitude'] = mlat, mlon
        entry['gdpr'] = True
        entry['radiusKm'] = 5
    else:
        entry['latitude'], entry['longitude'] = lat, lon
        entry['gdpr'] = False
        entry['radiusKm'] = 0

    st.markdown("### Step 4: Image and Marker")
    entry['imageUrl'] = st.text_input("Image URL (optional)", value="")
    marker_colour = st.text_input("Marker colour hex (e.g. '#FF0000')", value="#FF0000")
    if HEX_COLOR_RE.match(marker_colour):
        entry['colour'] = marker_colour
    else:
        st.error("Invalid hex colour format.")

    st.markdown("### ✅ Output JSON")
    if entry.get('id') and entry.get('title') and 'latitude' in entry and 'zones' in entry:
        st.code(json.dumps(entry, indent=2), language="json")
        st.caption(
            "Contact Archie at archwrth@gmail.com to add your entry to the map or refer to the official ARC SOP for adding pins to the map."
        )
    else:
        st.info("Fill in all required fields to generate JSON.")

if __name__ == "__main__":
    main()
