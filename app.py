import streamlit as st
import json
import math
import random
import re

st.set_page_config(
    page_title="ARC People & Projects Map Entry Generator 🌍"
)

# Köppen climate zones with concise names and colours
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
    red_star = "<span style='color:#dc3545'>*</span>"

    # Step 1: Basic Details
    st.markdown(f"Unique ID {red_star} (e.g. 'house5')", unsafe_allow_html=True)
    entry['id'] = st.text_input("", key="id_input", label_visibility="collapsed")

    st.markdown(f"Title {red_star} (e.g. 'House 5')", unsafe_allow_html=True)
    entry['title'] = st.text_input("", key="title_input", label_visibility="collapsed")

    st.markdown("Link URL (optional, must start with http/https)", unsafe_allow_html=True)
    entry['link'] = st.text_input("", key="link_input", label_visibility="collapsed")
    if entry['link'] and not is_valid_url(entry['link']):
        st.error("Invalid URL format.")

    # Step 2: Location and Köppen Zones
    st.markdown("Address (for reference)", unsafe_allow_html=True)
    entry['address'] = st.text_input("", key="address_input", label_visibility="collapsed")

    zone_labels = [f"{name} ({code})" for code, (name, _) in CLIMATE_ZONES.items()]
    st.markdown(f"Select between 1 and 3 Köppen zones {red_star}", unsafe_allow_html=True)
    selected_zones = st.multiselect("", options=zone_labels, key="zones_select", label_visibility="collapsed")
    codes = [opt.split()[-1].strip('()') for opt in selected_zones]
    if len(codes) < 1 or len(codes) > 3:
        st.error("Please select between 1 and 3 zones.")
    else:
        entry['zones'] = [{
            'code': code,
            'text': f"{CLIMATE_ZONES[code][0]} ({code})",
            'colour': CLIMATE_ZONES[code][1]
        } for code in codes]

    # Step 3: Coordinates & GDPR Masking
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("Latitude (decimal degrees)", unsafe_allow_html=True)
        lat = st.number_input("", min_value=-90.0, max_value=90.0, format="%.6f", key="lat_input", label_visibility="collapsed")
    with col2:
        st.markdown("Longitude (decimal degrees)", unsafe_allow_html=True)
        lon = st.number_input("", min_value=-180.0, max_value=180.0, format="%.6f", key="lon_input", label_visibility="collapsed")

    st.markdown(f"GDPR geomasking required? {red_star}", unsafe_allow_html=True)
    gdpr = st.radio("", ["Yes", "No"], key="gdpr_radio", label_visibility="collapsed")
    if gdpr == "Yes":
        mlat, mlon = generate_random_coordinate(lat, lon)
        entry['latitude'], entry['longitude'], entry['gdpr'], entry['radiusKm'] = mlat, mlon, True, 5
    else:
        entry['latitude'], entry['longitude'], entry['gdpr'], entry['radiusKm'] = lat, lon, False, 0

    # Step 4: Image and Marker
    st.markdown(f"Marker colour hex {red_star} (e.g. '#FF0000')", unsafe_allow_html=True)
    entry['colour'] = st.text_input("", key="marker_colour_input", label_visibility="collapsed")
    if entry['colour'] and not HEX_COLOR_RE.match(entry['colour']):
        st.error("Invalid hex colour format.")

    # Output JSON
    st.markdown("### ✅ Output JSON")
    link_ok = (not entry['link']) or is_valid_url(entry['link'])
    mandatory = all([
        entry.get('id'), entry.get('title'), entry.get('zones'), gdpr in ["Yes", "No"], entry.get('colour')
    ])
    if mandatory and link_ok:
        json_output = json.dumps(entry, indent=2)
        st.code(json_output, language='json')
        # reCAPTCHA form
        form_html = f"""
        <form action="mailto:archwrth@gmail.com" method="post" enctype="text/plain">
          <input type="hidden" name="body" value='{json_output}' />
          <div class="g-recaptcha" data-sitekey="YOUR_SITE_KEY"></div>
          <br/>
          <input type="submit" value="Email your entry to Archie" />
        </form>
        <script src="https://www.google.com/recaptcha/api.js" async defer></script>
        """
        import streamlit.components.v1 as components
        components.html(form_html, height=200)
        st.markdown("Alternatively, copy and paste the JSON above into an email to archwrth@gmail.com.")
    else:
        st.info("Fill in all required fields (marked *) to generate JSON.")

if __name__ == "__main__":
