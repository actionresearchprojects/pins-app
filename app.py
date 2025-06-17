import streamlit as st
import json
import math
import random
import re

# Page configuration
st.set_page_config(page_title="ARC People & Projects Map Entry Generator 🌍")

# Inject custom CSS for Ubuntu font and sizing globally
st.markdown(
    """
    <style>
    * {
        font-family: 'Ubuntu', sans-serif !important;
        font-size: 18px !important;
    }
    a {
        color: inherit !important;
        text-decoration: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Köppen zones with concise names
CLIMATE_ZONES = {
    'Af': ('Tropical rainforest', '#0000fe'),
    'Am': ('Tropical monsoon', '#0078ff'),
    'Aw': ('Tropical savanna', '#45aafa'),
    'BWh': ('Hot desert', '#fe0000'),
    'BWk': ('Cold desert', '#fe9695'),
    'BSh': ('Hot semi-arid', '#f4a500'),
    'BSk': ('Cold semi-arid', '#ffdc64'),
    'Csa': ('Hot-summer Mediterranean', '#ffff00'),
    'Csb': ('Warm-summer Mediterranean', '#c7c800'),
    'Csc': ('Cold-summer Mediterranean', '#969600'),
    'Cwa': ('Monsoon-influenced humid subtropical', '#96ff96'),
    'Cwb': ('Subtropical highland (dry winter)', '#64c865'),
    'Cwc': ('Subtropical highland (cold)', '#329633'),
    'Cfa': ('Humid subtropical', '#c9ff51'),
    'Cfb': ('Oceanic', '#65ff51'),
    'Cfc': ('Subpolar oceanic', '#31c800'),
    'Dsa': ('Hot-summer humid continental', '#ff00fe'),
    'Dsb': ('Warm-summer humid continental', '#c900c8'),
    'Dsc': ('Cold-summer humid continental', '#963295'),
    'Dsd': ('Extremely cold-summer humid continental', '#963295'),
    'Dwa': ('Monsoon-influenced humid continental', '#aaafff'),
    'Dwb': ('Monsoon-influenced warm-summer humid continental', '#5a77db'),
    'Dwc': ('Monsoon-influenced subarctic', '#4b50b4'),
    'Dwd': ('Monsoon-influenced extremely cold subarctic', '#320087'),
    'Dfa': ('Hot-summer humid continental', '#00ffff'),
    'Dfb': ('Warm-summer humid continental', '#37c8ff'),
    'Dfc': ('Subarctic', '#007e7d'),
    'Dfd': ('Extremely cold subarctic', '#00465f'),
    'ET': ('Tundra', '#b2b2b2'),
    'EF': ('Ice cap', '#666666'),
}

HEX_COLOR_RE = re.compile(r'^#(?:[0-9A-Fa-f]{3}){1,2}$')
URL_RE = re.compile(
    r'^(https?://)'
    r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6}'
    r'|localhost'
    r'|\d{1,3}(?:\.\d{1,3}){3})'
    r'(?::\d+)?'
    r'(/\S*)?$'
)

def is_valid_url(url):
    return bool(URL_RE.match(url))

# Generate jittered coordinate
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
    red_star = "<span style='color:#dc3545'>*</span>"

    # Unique ID
    st.markdown(
        f"Please provide a unique ID for admin purposes only. No caps or spaces. {red_star} (e.g. 'house5')",
        unsafe_allow_html=True
    )
    entry['id'] = st.text_input("", key="id_input", label_visibility="collapsed")

    # Listing type (default Project)
    st.markdown(
        f"<p style='font-size:20px; font-weight:bold'>Are you listing a Project or a Person?</p>",
        unsafe_allow_html=True
    )
    listing_type = st.radio(
        "", ["Project", "Person"], index=0, key="listing_type", label_visibility="collapsed"
    )
    entry['type'] = listing_type

    # Title
    if listing_type == "Project":
        st.markdown(
            f"Please enter a title to display publicly as your project title. {red_star} (e.g. 'House 5')",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"Please enter your full name to be displayed publicly. {red_star}",
            unsafe_allow_html=True
        )
    entry['title'] = st.text_input("", key="title_input", label_visibility="collapsed")

    # Link (optional)
    if listing_type == "Project":
        st.markdown(
            "Link to further information you'd like to share (optional, must start with `https://`, e.g. `https://google.com`)"
        )
        entry['link'] = st.text_input("", key="link_input", label_visibility="collapsed")
        if entry['link'] and not entry['link'].startswith("https://"):
            st.error("Link must start with https://")
    else:
        entry['link'] = "https://actionresearchprojects.framer.website/people"

    # Address/Description
    st.markdown(
        "Address/description of location (optional, will be displayed publicly). e.g. iHelp Eco Village, Mkuranga, Tanzania",
        unsafe_allow_html=True
    )
    entry['address'] = st.text_input("", key="address_input", label_visibility="collapsed")

    # Climate zones
    zone_labels = [f"{name} ({code})" for code, (name, _) in CLIMATE_ZONES.items()]
    st.markdown(f"Select up to 3 climate zones {red_star}", unsafe_allow_html=True)
    selected = st.multiselect("", options=zone_labels, key="zones_select", label_visibility="collapsed")
    codes = [opt.split()[-1].strip('()') for opt in selected]
    if len(codes) > 3:
        st.error("Please select at most 3 climate zones.")
    entry['zones'] = [{
        'code': code,
        'text': f"{CLIMATE_ZONES[code][0]} ({code})",
        'colour': CLIMATE_ZONES[code][1]
    } for code in codes]

    # Coordinates
    st.markdown("**Precise location coordinates**", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input(
            "Latitude (decimal degrees)",
            -90.0,
            90.0,
            format="%.6f",
            key="lat_input"
        )
    with col2:
        lon = st.number_input(
            "Longitude (decimal degrees)",
            -180.0,
            180.0,
            format="%.6f",
            key="lon_input"
        )

    # Privacy masking
    st.markdown(
        f"You may opt to randomise your coordinates within a chosen radius for privacy. {red_star}",
        unsafe_allow_html=True
    )
    mask_choice = st.radio("", ["Yes", "No"], key="mask_radio", label_visibility="collapsed")
    if mask_choice == "Yes":
        radius_km = st.slider("Select mask radius (km) *", 2, 10, 5, key="radius_slider")
        mlat, mlon = generate_random_coordinate(lat, lon, radius_m=radius_km * 1000)
        entry['latitude'], entry['longitude'] = mlat, mlon
        entry['radiusKm'] = radius_km
        entry['mask'] = True
    else:
        entry['latitude'], entry['longitude'] = lat, lon
        entry['radiusKm'] = 0
        entry['mask'] = False

    # Marker colour by type
    entry['colour'] = "#ffff00" if listing_type == "Project" else "#add8e6"

    # Output
    st.markdown("### ✅ Output JSON")
    link_ok = listing_type == "Person" or entry['link'] == "" or entry['link'].startswith("https://")
    mandatory_fields = all([
        entry.get('id'),
        entry.get('title'),
        entry.get('zones'),
        mask_choice in ["Yes", "No"]
    ])
    if mandatory_fields and link_ok:
        st.code(json.dumps(entry, indent=2), language='json')
        st.markdown(
            "<small>For inclusion on the public map, please click the button in the top right corner of the box to copy the text, and email it archwrth@gmail.com.</small>",
            unsafe_allow_html=True
        )
    else:
        st.info("Fill in all required fields (marked *) to generate JSON.")

if __name__ == "__main__":
    main()
