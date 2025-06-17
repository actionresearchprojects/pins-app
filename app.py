import streamlit as st
import json
import math
import random
import re

# Page configuration
st.set_page_config(page_title="ARC People & Projects Map Entry Generator 🌍")

# Inject custom CSS for Ubuntu font and sizing globally, disable link styling
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

# Generate jittered coordinate for masking
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
    st.markdown("<h1 style='font-family:Ubuntu; font-size:32px; font-weight:bold'>ARC People & Projects Map Entry Generator 🌍</h1>", unsafe_allow_html=True)
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
        "<h2 style='font-family:Ubuntu; font-size:24px; font-weight:bold'>Are you listing a Project or a Person?</h2>",
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
        st.info("Fill in all required fields (marked *) to generate JSON.")

if __name__ == "__main__":
    main()("Fill in all required fields (marked *) to generate JSON.")
        st.info("Fill in all required fields (marked *) to generate JSON.")

if __name__ == "__main__":
    main()
