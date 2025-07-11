import streamlit as st
import json
import math
import random
import re

st.set_page_config(page_title="ARC People & Projects Map Entry Generator 🌍")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu&display=swap');
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
    r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,6}|localhost|\d{1,3}(?:\.\d{1,3}){3})'
    r'(?::\d+)?(/\S*)?$'
)

def is_valid_url(url):
    return bool(URL_RE.match(url))

# Enforce minimum displacement of 1 km from true location
def generate_random_coordinate(lat, lon, radius_m=5000, min_radius_m=1000):
    R = 6371000  # Earth’s radius in metres
    lat_rad = math.radians(lat)
    d = random.uniform(min_radius_m, radius_m)
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
    st.markdown(
        "<h1 style='font-family:Ubuntu; font-size:32px; font-weight:bold;'>"
        "ARC People & Projects Map Entry Generator 🌍</h1>",
        unsafe_allow_html=True
    )

    entry = {}
    red_star = "<span style='color:#dc3545'>*</span>"

    st.markdown(
        f"Please provide a unique ID for admin purposes only. No caps or spaces. {red_star} (e.g. 'house5')",
        unsafe_allow_html=True
    )
    entry['id'] = st.text_input("", key="id_input", label_visibility="collapsed")
    valid_id = bool(entry['id']) and re.match(r'^[a-z0-9_-]+$', entry['id'])
    if entry['id'] and not valid_id:
        st.error("ID must use only lowercase letters, numbers, hyphens or underscores.")

    st.markdown(
        "<h2 style='font-family:Ubuntu; font-size:24px; font-weight:bold;'>"
        "Are you listing a Project or a Person?</h2>",
        unsafe_allow_html=True
    )
    listing_type = st.radio("", ["Project", "Person"], index=0, key="listing_type", label_visibility="collapsed")
    entry['type'] = listing_type

    st.markdown(
        f"{'Please enter a title to display publicly as your project title' if listing_type == 'Project' else 'Please enter your full name to be displayed publicly.'} {red_star}",
        unsafe_allow_html=True
    )
    title = st.text_input("", key="title_input", label_visibility="collapsed")
    entry['title'] = title

    st.markdown(
        "Link to further information you'd like to share (optional, must start with https://)" if listing_type == "Project"
        else "", unsafe_allow_html=True
    )
    link_val = st.text_input("", key="link_input", label_visibility="collapsed") if listing_type == "Project" else ""
    entry['link'] = link_val if link_val.startswith("https://") else ("https://actionresearchprojects.framer.website/people" if listing_type == "Person" else "")

    st.markdown(
        "Address/description of location (optional, will be displayed publicly)", unsafe_allow_html=True
    )
    entry['address'] = st.text_input("", key="address_input", label_visibility="collapsed")

    st.markdown(f"Select a climate zone {red_star}", unsafe_allow_html=True)
    zone_labels = [f"{name} ({code})" for code, (name, _) in CLIMATE_ZONES.items()]
    selected = st.selectbox("", options=[""] + zone_labels, key="zone_select", label_visibility="collapsed")
    if selected:
        code = selected.split()[-1].strip("()")
        entry['zones'] = [{
            'code': code,
            'text': f"{CLIMATE_ZONES[code][0]} ({code})",
            'colour': CLIMATE_ZONES[code][1]
        }]
    else:
        entry['zones'] = []

    st.markdown(
        "<h2 style='font-family:Ubuntu; font-size:24px; font-weight:bold;'>Precise location coordinates</h2>",
        unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude (decimal degrees)", -90.0, 90.0, format="%.6f", key="lat_input")
    with col2:
        lon = st.number_input("Longitude (decimal degrees)", -180.0, 180.0, format="%.6f", key="lon_input")

    st.markdown(
        f"You may opt to randomise your coordinates within a chosen radius for privacy. {red_star}",
        unsafe_allow_html=True
    )
    mask_choice = st.radio("", ["Yes", "No"], key="mask_radio", label_visibility="collapsed")
    if mask_choice == "Yes":
        st.markdown(f"Select mask radius in km (we advise a 5km radius for privacy) {red_star}", unsafe_allow_html=True)
        radius_km = st.slider("", 2, 10, 5, key="mask_radius")
        mlat, mlon = generate_random_coordinate(lat, lon, radius_m=radius_km * 1000, min_radius_m=1000)
        entry.update(latitude=mlat, longitude=mlon, radiusKm=radius_km, gdpr=True)
    else:
        entry.update(latitude=lat, longitude=lon, radiusKm=0, gdpr=False)

    st.markdown(
        """
        Image URL (optional, will appear publicly, must start with https://)<br>
        If your image isn't already hosted online, you can upload it via
        <a href="https://postimages.org/" target="_blank" rel="noopener noreferrer">postimages.org</a>.<br>
        Just drag and drop your image, then copy the link labelled <strong>Direct Link</strong> and paste it here.
        """,
        unsafe_allow_html=True
    )
    img_val = st.text_input("", key="image_input", label_visibility="collapsed")
    entry['imageUrl'] = img_val if img_val.startswith("http") else ""

    entry['colour'] = "#006400" if listing_type == "Project" else "#add8e6"

    st.markdown("### ✅ Output JSON")
    valid_link = (listing_type == "Person") or entry['link'].startswith("https://") or entry['link'] == ""
    valid_image = entry['imageUrl'] == "" or entry['imageUrl'].startswith("http")
    mandatory = all([entry['id'], entry['title'], entry['zones'], mask_choice in ["Yes", "No"], valid_link, valid_image])
    if not valid_link:
        st.error("Link must start with https:// or be left blank.")
    if entry['imageUrl'] and not valid_image:
        st.error("Image URL must start with https://")
    if mandatory:
        st.code(json.dumps(entry, indent=2), language="json")
        st.markdown(
            "<small>For inclusion on the public map, please click the button in the top right corner of the box to copy the text, and email it archwrth@gmail.com.</small>",
            unsafe_allow_html=True
        )
    else:
        st.info("Fill in all required fields (marked *) to generate JSON.")

if __name__ == "__main__":
    main()
