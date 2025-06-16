import streamlit as st
import json
import math
import random
import re

st.set_page_config(
    page_title="ARC People & Projects Map Entry Generator 🌍"
)

# Climate zones with concise official Köppen names and colours
CLIMATE_ZONES = {
    'Af': ('Tropical rainforest climate', '#0000fe'),
    'Am': ('Tropical monsoon climate', '#0078ff'),
    'Aw': ('Tropical savanna climate', '#45aafa'),
    'BWh': ('Hot desert climate', '#fe0000'),
    'BWk': ('Cold desert climate', '#fe9695'),
    'BSh': ('Hot semi-arid climate', '#f4a500'),
    'BSk': ('Cold semi-arid climate', '#ffdc64'),
    'Csa': ('Hot-summer Mediterranean climate', '#ffff00'),
    'Csb': ('Warm-summer Mediterranean climate', '#c7c800'),
    'Csc': ('Cold-summer Mediterranean climate', '#969600'),
    'Cwa': ('Monsoon-influenced humid subtropical climate', '#96ff96'),
    'Cwb': ('Subtropical highland climate (dry winter)', '#64c865'),
    'Cwc': ('Subtropical highland climate (cold)', '#329633'),
    'Cfa': ('Humid subtropical climate', '#c9ff51'),
    'Cfb': ('Oceanic climate', '#65ff51'),
    'Cfc': ('Subpolar oceanic climate', '#31c800'),
    'Dsa': ('Hot-summer humid continental climate', '#ff00fe'),
    'Dsb': ('Warm-summer humid continental climate', '#c900c8'),
    'Dsc': ('Cold-summer humid continental climate', '#963295'),
    'Dsd': ('Extremely cold-summer humid continental climate', '#963295'),
    'Dwa': ('Monsoon-influenced humid continental climate', '#aaafff'),
    'Dwb': ('Monsoon-influenced warm-summer humid continental', '#5a77db'),
    'Dwc': ('Monsoon-influenced subarctic climate', '#4b50b4'),
    'Dwd': ('Monsoon-influenced extremely cold subarctic climate', '#320087'),
    'Dfa': ('Hot-summer humid continental climate', '#00ffff'),
    'Dfb': ('Warm-summer humid continental climate', '#37c8ff'),
    'Dfc': ('Subarctic climate', '#007e7d'),
    'Dfd': ('Extremely cold subarctic climate', '#00465f'),
    'ET': ('Tundra climate', '#b2b2b2'),
    'EF': ('Ice cap climate', '#666666'),
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

# Great-circle offset for GDPR geomasking
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
    st.title("ARC People & Projects Map Entry Generator 🌍")
    entry = {}

    # Step 1: Basic Details
    entry['id'] = st.text_input(
        label="Unique ID * (e.g. 'house5')",
        max_chars=50,
        key="id_input"
    )
    entry['title'] = st.text_input(
        label="Title * (e.g. 'House 5')",
        key="title_input"
    )
    entry['link'] = st.text_input(
        label="Link URL (optional, must start with http/https)",
        key="link_input"
    )
    if entry['link'] and not is_valid_url(entry['link']):
        st.error("Invalid URL format.")

    # Step 2: Location and Climate Zones
    entry['address'] = st.text_input(
        label="Address (for reference)",
        key="address_input"
    )
    zone_options = [f"{label} ({code})" for code, (label, _) in CLIMATE_ZONES.items()]
    selected_zones = st.multiselect(
        label="Select between 1 and 3 climate zone codes *",
        options=[f"{name} ({code})" for code, (name, _) in CLIMATE_ZONES.items()],
        key="zones_select"
    )
    codes = [opt.split()[-1].strip('()') for opt in selected_zones]
    if len(codes) < 1 or len(codes) > 3:
        st.error("Please select between 1 and 3 climate zones.")
    else:
        entry['zones'] = [
            {
                'code': code,
                'text': f"{CLIMATE_ZONES[code][0]} ({code})",
                'colour': CLIMATE_ZONES[code][1]
            }
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
            key="lat_input"
        )
    with col2:
        lon = st.number_input(
            label="Longitude (decimal degrees)",
            min_value=-180.0,
            max_value=180.0,
            format="%.6f",
            key="lon_input"
        )
    gdpr = st.radio(
        label="GDPR geomasking required? *",
        options=["Yes", "No"],
        key="gdpr_radio"
    )
    if gdpr == "Yes":
        mlat, mlon = generate_random_coordinate(lat, lon)
        entry['latitude'], entry['longitude'], entry['gdpr'], entry['radiusKm'] = mlat, mlon, True, 5
    else:
        entry['latitude'], entry['longitude'], entry['gdpr'], entry['radiusKm'] = lat, lon, False, 0

    # Step 4: Image and Marker
    entry['colour'] = st.text_input(
        label="Marker colour hex * (e.g. '#FF0000')",
        key="marker_colour_input"
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
            "<small>For inclusion on the public map, please email Archie at archwrth@gmail.com or see the ARC SOP for adding new entries.</small>",
            unsafe_allow_html=True
        )
    else:
        st.info("Fill in all required fields (marked *) to generate JSON.")

if __name__ == "__main__":
    main()
