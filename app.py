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
    r'^(https?://)'               # http:// or https://
    r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6}'
    r'|localhost'
    r'|\d{1,3}(?:\.\d{1,3}){3})'
    r'(?::\d+)?'
    r'(/\S*)?$'
)


def is_valid_url(url):
    return bool(URL_RE.match(url))

# Great-circle offset to avoid large jumps
def generate_random_coordinate(lat, lon, radius_m=5000):
    R = 6371000
    lat_rad = math.radians(lat)
    d = random.uniform(0, radius_m)
    theta = random.uniform(0, 2 * math.pi)
    ang = d / R
    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(ang) +
        math.cos(lat_rad) * math.sin(ang) * math.cos(theta)
    )
    new_lon_rad = math.radians(lon) + math.atan2(
        math.sin(theta) * math.sin(ang) * math.cos(lat_rad),
        math.cos(ang) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )
    new_lat = math.degrees(new_lat_rad)
    new_lon = math.degrees(new_lon_rad)
    new_lat = max(min(new_lat, 90), -90)
    new_lon = ((new_lon + 180) % 360) - 180
    return new_lat, new_lon


def main():
    st.title("📍 pins.json Entry Generator")
    entry = {}

    # Step 1: Basic Details
    entry['id'] = st.text_input(
        label="Unique ID * (e.g. 'house5')",
        max_chars=50,
        key="id_input",
        label_visibility="visible"
    )
    entry['title'] = st.text_input(
        label="Title * (e.g. 'House 5')",
        key="title_input",
        label_visibility="visible"
    )
    entry['link'] = st.text_input(
        label="Link URL (optional, must start with http/https)",
        key="link_input",
        label_visibility="visible"
    )
    if entry['link'] and not is_valid_url(entry['link']):
        st.error("Invalid URL format.")

    # Step 2: Location and Climate Zones
    entry['address'] = st.text_input(
        label="Address (for reference)",
        key="address_input",
        label_visibility="visible"
    )
    zone_options = [f"{name} ({code})" for code, (name, _) in CLIMATE_ZONES.items()]
    selected_zones = st.multiselect(
        label="Select between 1 and 3 climate zone codes *",
        options=zone_options,
        key="zones_select",
        label_visibility="visible"
    )
    codes = [opt.split()[-1].strip('()') for opt in selected_zones]
    if len(codes) < 1 or len(codes) > 3:
        st.error("Please select between 1 and 3 climate zones.")
    else:
        entry['zones'] = [
            {'code': code,
             'text': f"{CLIMATE_ZONES[code][0]} ({code})",
             'colour': CLIMATE_ZONES[code][1]}
            for code in codes
        ]

    # Step 3: Coordinates & GDPR Masking
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input(
            label="Latitude (decimal degrees)",
            min_value=-90.0,
            max_value=90.0,
            format="%.6f",
            key="lat_input",
            label_visibility="visible"
        )
    with col2:
        lon = st.number_input(
            label="Longitude (decimal degrees)",
            min_value=-180.0,
            max_value=180.0,
            format="%.6f",
            key="lon_input",
            label_visibility="visible"
        )
    gdpr = st.radio(
        label="GDPR geomasking required? *",
        options=["Yes", "No"],
        key="gdpr_radio",
        label_visibility="visible"
    )
    if gdpr == "Yes":
        mlat, mlon = generate_random_coordinate(lat, lon)
        entry['latitude'], entry['longitude'], entry['gdpr'], entry['radiusKm'] = mlat, mlon, True, 5
    else:
        entry['latitude'], entry['longitude'], entry['gdpr'], entry['radiusKm'] = lat, lon, False, 0

    # Step 4: Image and Marker
    entry['colour'] = st.text_input(
        label="Marker colour hex * (e.g. '#FF0000')",
        key="marker_colour_input",
        label_visibility="visible"
    )
    if entry['colour'] and not HEX_COLOR_RE.match(entry['colour']):
        st.error("Invalid hex colour format.")

    # Output JSON
    st.markdown("### ✅ Output JSON")
    link_ok = (not entry['link']) or is_valid_url(entry['link'])
    mandatory = all([
        entry.get('id'),
        entry.get('title'),
        entry.get('zones'),
        gdpr in ["Yes", "No"],
        entry.get('colour')
    ])
    if mandatory and link_ok:
        st.code(json.dumps(entry, indent=2), language='json')
        st.markdown(
            "<small>Contact Archie at archwrth@gmail.com for him to add your entry to the map or refer to the official ARC SOP for adding pins to the map.</small>",
            unsafe_allow_html=True
        )
    else:
        st.info("Fill in all required fields (marked *) to generate JSON.")

if __name__ == "__main__":
    main()
