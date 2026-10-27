"""MediMind AI - Next-Gen Multilingual Health & Emergency Resource Portal.
Run: python -m streamlit run app.py
"""
import hashlib
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import streamlit as st

from medimind import facilities, knowledge, llm, pharmacies, safety, voice

# Page configuration for a full-width modern healthcare web app
st.set_page_config(
    page_title="MediMind AI • Smart Health & Emergency Network",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load API credentials
try:
    if "OPENROUTER_API_KEY" in st.secrets:
        os.environ.setdefault("OPENROUTER_API_KEY", st.secrets["OPENROUTER_API_KEY"])
    elif "ANTHROPIC_API_KEY" in st.secrets:
        os.environ.setdefault("OPENROUTER_API_KEY", st.secrets["ANTHROPIC_API_KEY"])
    if "MEDIMIND_MODEL" in st.secrets:
        os.environ.setdefault("MEDIMIND_MODEL", st.secrets["MEDIMIND_MODEL"])
except Exception:
    pass

# Session state initialization
ss = st.session_state
for k, v in {
    "msgs": [],
    "last_hash": None,
    "play": None,
    "replay": None,
    "flags": [],
    "err": None,
    "live_loc": None,
}.items():
    ss.setdefault(k, v)

# Modern Responsive Styling & Typography Injection
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Container Spacing */
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1280px;
    }

    /* Top Navbar / Header */
    .medimind-navbar {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        color: white;
    }

    .medimind-title {
        font-family: 'Outfit', sans-serif;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .medimind-tagline {
        font-size: 13px;
        color: #94a3b8;
        margin: 0;
    }

    .emergency-badge {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        color: #fca5a5;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Tabs Bar Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px;
        font-weight: 600;
        color: #475569;
        padding: 0 16px;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0284c7 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    /* Card Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
        background: #ffffff !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.06);
    }

    /* Metrics Styling */
    [data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 16px;
    }

    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #64748b;
        font-size: 13px;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif;
        color: #0f172a;
        font-weight: 700;
    }

    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Top Web Navigation Header
st.markdown(
    """
    <div class="medimind-navbar">
        <div style="display:flex; align-items:center; gap:14px;">
            <div style="font-size:32px;">🩺</div>
            <div>
                <h1 class="medimind-title">MediMind AI</h1>
                <p class="medimind-tagline">Multilingual Health Voice Assistant • Emergency Beds • Blood Banks • Medicine Finder</p>
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
            <div class="emergency-badge">
                <span>🚨 Emergency:</span>
                <a href="tel:112" style="color:#fca5a5; text-decoration:none; font-weight:700;">112</a> |
                <a href="tel:108" style="color:#fca5a5; text-decoration:none; font-weight:700;">108 (Ambulance)</a>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Global Language Selector
top_col1, top_col2 = st.columns([1, 3])
with top_col1:
    lang_label = st.selectbox("🌐 भाषा / Language", list(voice.LANGUAGES), index=0)
    sr_code, tts_code = voice.LANGUAGES[lang_label]

with top_col2:
    if ss.flags:
        st.error(
            "🚨 **CRITICAL EMERGENCY SIGNS DETECTED: " + ", ".join(ss.flags) + "**\n\n"
            "### [📞 Call 112](tel:112)    [🚑 Call 108 (Ambulance)](tel:108)\n"
            "Please call right now or proceed immediately to the nearest hospital trauma centre."
        )


def handle(text: str):
    """Process user query: safety checks -> OpenRouter LLM -> spoken response."""
    ss.msgs.append({"role": "user", "content": text})
    ss.flags = safety.detect(text)
    answer, _ = llm.reply(llm.clean(ss.msgs), sr_code, ss.flags)
    ss.msgs.append({"role": "assistant", "content": answer})
    audio = voice.speak(answer, tts_code)
    ss.play = ss.replay = audio


# Five Core Modules / Tabs
tab_voice, tab_meds, tab_beds, tab_sym, tab_vit = st.tabs([
    "🎤 Voice Assistant",
    "💊 Find Medicines & Stores",
    "🏥 Beds & Blood Vacancies",
    "🤒 Symptom Checker",
    "❤️ Vitals & First Aid",
])

# ==============================================================================
# TAB 1: VOICE HEALTH ASSISTANT
# ==============================================================================
with tab_voice:
    st.markdown("### 🎙️ Speak or Type Your Health Concern")
    st.caption("Designed for patients and families. You can speak naturally in 10 Indian languages.")

    # Quick Conversation Prompt Chips
    st.write("**Quick examples to ask:**")
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        if st.button("🌡️ High fever & chills", use_container_width=True):
            handle("I have high fever and severe shivering for 2 days.")
            st.rerun()
    with qc2:
        if st.button("🤕 Severe headache", use_container_width=True):
            handle("I have throbbing headache on one side and nausea.")
            st.rerun()
    with qc3:
        if st.button("🤢 Stomach pain & vomiting", use_container_width=True):
            handle("Severe stomach pain and loose motion since morning.")
            st.rerun()
    with qc4:
        if st.button("🫁 Breathlessness / Cough", use_container_width=True):
            handle("Difficulty breathing and dry cough for 3 days.")
            st.rerun()

    st.markdown("---")

    v_col1, v_col2 = st.columns([1, 1])
    with v_col1:
        if st.button("🔊 Hear instructions in " + lang_label, use_container_width=True):
            ss.play = voice.speak(voice.GREETING.get(tts_code, voice.GREETING["en"]), tts_code)

        st.markdown("#### 1️⃣ Tap 🎤   2️⃣ Speak   3️⃣ Tap ⏹ stop")
        rec = st.audio_input("Speak here", label_visibility="collapsed")

        if rec is not None:
            data = rec.getvalue()
            h = hashlib.md5(data).hexdigest()
            if h != ss.last_hash:
                ss.last_hash, ss.err = h, None
                with st.spinner("👂 Listening… 💭 Consulting MediMind AI…"):
                    try:
                        text = voice.transcribe(data, sr_code)
                    except voice.VoiceError:
                        text = None
                        ss.err = "No internet connection for speech recognition. Please type below."
                    if text:
                        handle(text)
                    elif not ss.err:
                        ss.play = voice.speak(voice.NOT_HEARD.get(tts_code, voice.NOT_HEARD["en"]), tts_code)

        if ss.err:
            st.error(ss.err)
        if ss.play:
            st.audio(ss.play, format="audio/mp3", autoplay=True)
            ss.play = None
        elif ss.replay:
            if st.button("🔁 Hear the answer again", use_container_width=True):
                st.audio(ss.replay, format="audio/mp3", autoplay=True)

        with st.form("typed", clear_on_submit=True):
            typed = st.text_input("⌨️ Or type your health question here:")
            if st.form_submit_button("Send Question") and typed.strip():
                handle(typed.strip())
                st.rerun()

    with v_col2:
        st.markdown("#### 💬 Conversation History")
        if not ss.msgs:
            st.info("No messages yet. Speak or type to begin.")
        for m in ss.msgs[-6:]:
            with st.chat_message(
                "user" if m["role"] == "user" else "assistant",
                avatar="🧑" if m["role"] == "user" else "🩺",
            ):
                st.write(m["content"])
        if ss.msgs and st.button("🗑 Clear Conversation"):
            ss.msgs, ss.flags, ss.replay, ss.last_hash = [], [], None, None
            st.rerun()

# ==============================================================================
# TAB 2: FIND MEDICINES & MEDICAL STORES (NEW FEATURE)
# ==============================================================================
with tab_meds:
    st.markdown("### 💊 Nearest Medical Stores & Live Medicine Availability")
    st.caption("Check real-time stock at local pharmacies, 24/7 stores, and Jan Aushadhi Kendras (save up to 80% on generics).")

    # Live Location Detector Bar
    loc_bar1, loc_bar2 = st.columns([1, 1])
    with loc_bar1:
        if st.button("📍 Detect Live Location (Instant)", key="detect_loc_meds", use_container_width=True):
            live = facilities.detect_live_location()
            if live:
                ss.live_loc = live
                st.rerun()
            else:
                st.error("Could not automatically pinpoint location. Please select your city below.")
    with loc_bar2:
        if ss.get("live_loc"):
            llat, llon, llabel = ss.live_loc
            st.success(f"🎯 **Location Active**: {llabel}")
            if st.button("✖ Reset Location", key="reset_med_loc"):
                ss.live_loc = None
                st.rerun()

    # Search and Filter Bars
    m_col1, m_col2 = st.columns([2, 1])
    with m_col1:
        med_options = ["All Medicines"] + [m["name"] for m in pharmacies.COMMON_MEDICINES]
        selected_med_name = st.selectbox("🔍 Select or Search Medicine Needed:", med_options, index=1)
    with m_col2:
        city_names = list(facilities.CITIES.keys())
        selected_med_city = st.selectbox("🏙️ Or Select City Area:", city_names, index=0)

    # Determine Coordinates for Pharmacy search
    if ss.get("live_loc"):
        m_lat, m_lon = ss.live_loc[0], ss.live_loc[1]
    else:
        m_lat = facilities.CITIES[selected_med_city]["lat"]
        m_lon = facilities.CITIES[selected_med_city]["lon"]

    # Show Selected Medicine Details & Savings Info
    selected_med_info = next((m for m in pharmacies.COMMON_MEDICINES if m["name"] == selected_med_name), None)
    if selected_med_info:
        with st.container(border=True):
            d1, d2, d3 = st.columns([2, 1, 1])
            with d1:
                st.markdown(f"#### 💊 {selected_med_info['name']}")
                st.write(f"**Generic Composition:** `{selected_med_info['generic']}`")
                st.caption(f"**Common Uses:** {selected_med_info['usage']}  •  Category: {selected_med_info['category']}")
            with d2:
                st.metric("Jan Aushadhi Generic Price", selected_med_info['generic_price'], delta="Best Value", delta_color="normal")
            with d3:
                st.metric("Branded MRP", selected_med_info['brand_price'])
                if selected_med_info.get("prescription_needed"):
                    st.warning("⚠️ Prescription required")

    # Pharmacy Filter Controls
    with st.expander("⚙️ Filter Stores & Pharmacy Options", expanded=True):
        pf1, pf2, pf3 = st.columns(3)
        with pf1:
            only_jan = st.checkbox("🏛️ Jan Aushadhi Kendras Only (Govt Generics)", value=False)
        with pf2:
            only_24 = st.checkbox("🕒 24/7 Open Stores Only", value=False)
        with pf3:
            p_dist = st.slider("Search Radius (km)", 5, 100, 35, 5, key="pharm_dist_slider")

    # Fetch matching pharmacies
    matched_pharmacies = pharmacies.search_pharmacies(
        medicine_name=selected_med_name,
        center_lat=m_lat,
        center_lon=m_lon,
        max_dist_km=float(p_dist),
        only_24_7=only_24,
        only_jan_aushadhi=only_jan,
    )

    st.markdown(f"#### 📋 Nearest Stores with Availability ({len(matched_pharmacies)} Found)")

    if not matched_pharmacies:
        st.info("No stores found matching these specific filters. Try increasing the search radius or unticking 24/7 filter.")

    for p in matched_pharmacies:
        with st.container(border=True):
            head_col, dist_col = st.columns([3, 1])
            with head_col:
                badge = "🏛️" if "Jan Aushadhi" in p["type"] else "🏥"
                st.markdown(f"### {badge} {p['name']}")
                st.caption(f"📍 {p['address']}  •  🕒 {p['timings']}")
            with dist_col:
                st.markdown(f"**📍 {p['distance_km']} km away**")
                is_24_tag = "🕒 24/7 Open" if p["is_24_7"] else "Standard Hours"
                st.caption(is_24_tag)

            # Medicine stock status in this store
            sc1, sc2, sc3 = st.columns(3)
            stock_status = p.get("medicine_stock", "In Stock")
            status_color = "#16a34a" if stock_status == "In Stock" else "#f59e0b"
            with sc1:
                st.markdown(f"**Stock Status:** <span style='color:{status_color}; font-weight:700;'>● {stock_status}</span>", unsafe_allow_html=True)
            with sc2:
                st.write(f"**Quantity Available:** `{p.get('medicine_qty', 0)} units`")
            with sc3:
                st.write(f"**Price at this Store:** `{p.get('medicine_price', 'MRP')}`")

            # Actions
            b_call, b_map = st.columns(2)
            with b_call:
                clean_phone = p['phone'].replace(" ", "").replace("-", "")
                st.link_button(f"📞 Call Store: {p['phone']}", f"tel:{clean_phone}", use_container_width=True)
            with b_map:
                map_dest = f"https://www.google.com/maps/dir/?api=1&destination={p['lat']},{p['lon']}"
                st.link_button("🗺️ Get Directions in Google Maps", map_dest, use_container_width=True)

# ==============================================================================
# TAB 3: HOSPITAL BEDS & BLOOD BANK VACANCIES
# ==============================================================================
with tab_beds:
    st.markdown("### 🏥 Nearest Hospitals & Blood Banks with Live Vacancy")
    st.caption("Interactive real-time map with verified ICU beds, oxygen beds, general wards, and blood bank stock.")

    # Live Location Detector Bar
    loc_b1, loc_b2 = st.columns([1, 1])
    with loc_b1:
        if st.button("📍 Detect Live Location (Instant)", key="detect_loc_beds", use_container_width=True):
            live = facilities.detect_live_location()
            if live:
                ss.live_loc = live
                st.rerun()
            else:
                st.error("Could not automatically detect network location. Please pick your city below.")
    with loc_b2:
        if ss.get("live_loc"):
            llat, llon, llabel = ss.live_loc
            st.success(f"🎯 **Location Active**: {llabel} (`{llat:.4f}, {llon:.4f}`)")
            if st.button("✖ Reset Location", key="reset_bed_loc"):
                ss.live_loc = None
                st.rerun()

    # Manual Selection Fallback
    col_city, col_search = st.columns([1, 2])
    with col_city:
        city_names = list(facilities.CITIES.keys())
        selected_city = st.selectbox("🏙️ Or Select Metro City", city_names, index=0)
    with col_search:
        search_place = st.text_input(
            "🔍 Or Search Any Area / Pincode / Landmark:",
            placeholder="e.g. Connaught Place, Whitefield, Bandra, 110001...",
        )

    # Determine center location
    if ss.get("live_loc"):
        center_lat, center_lon, location_label = ss.live_loc
    elif search_place.strip():
        geo = facilities.geocode_place(search_place.strip())
        if geo:
            center_lat, center_lon, location_label = geo
            st.success(f"📍 Pinpointed: **{location_label}** ({center_lat:.4f}, {center_lon:.4f})")
        else:
            center_coords = facilities.CITIES[selected_city]
            center_lat, center_lon = center_coords["lat"], center_coords["lon"]
            location_label = selected_city
            st.warning(f"Could not pinpoint '{search_place}'. Showing default {selected_city} area.")
    else:
        center_coords = facilities.CITIES[selected_city]
        center_lat, center_lon = center_coords["lat"], center_coords["lon"]
        location_label = selected_city

    # Filters
    with st.expander("⚙️ Filter Vacancies & Medical Needs", expanded=True):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            facility_type = st.selectbox("Facility Type", ["All", "Hospital", "Blood Bank"])
            max_dist = st.slider("Search Radius (km)", min_value=5, max_value=150, value=50, step=5)
        with fcol2:
            req_blood = st.selectbox("Required Blood Group", ["Any", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", "Platelets"])
            filter_text = st.text_input("Filter by facility name", placeholder="e.g. AIIMS, Red Cross...")
        with fcol3:
            st.write("**Bed Requirements:**")
            req_icu = st.checkbox("🚨 ICU Beds Required")
            req_oxygen = st.checkbox("💨 Oxygen Beds Required")

    # Fetch matching facilities
    matched = facilities.search_facilities(
        center_lat=center_lat,
        center_lon=center_lon,
        facility_type=facility_type,
        req_blood=req_blood if req_blood != "Any" else None,
        req_icu=req_icu,
        req_oxygen=req_oxygen,
        max_distance_km=float(max_dist),
        search_query=filter_text,
    )

    # KPI Summary Cards
    total_beds = sum(f.get("beds_available", 0) for f in matched if f["type"] == "Hospital")
    total_icu = sum(f.get("icu_available", 0) for f in matched if f["type"] == "Hospital")
    total_oxygen = sum(f.get("oxygen_available", 0) for f in matched if f["type"] == "Hospital")
    total_blood_units = sum(
        f.get("blood_stock", {}).get(req_blood, sum(f.get("blood_stock", {}).values()))
        if req_blood != "Any"
        else sum(f.get("blood_stock", {}).values())
        for f in matched
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏥 Facilities Found", f"{len(matched)}")
    m2.metric("🛏️ Available Beds", f"{total_beds}", f"{total_icu} ICU")
    m3.metric("💨 Oxygen Beds", f"{total_oxygen}")
    m4.metric("🩸 Blood Units", f"{total_blood_units}", "Units Available" if req_blood == "Any" else f"{req_blood} units")

    # Map visualization
    if matched:
        import pandas as pd
        import pydeck as pdk

        map_data = []

        # Add user's location marker if live
        if ss.get("live_loc"):
            map_data.append({
                "name": "🎯 Your Current Location",
                "lat": center_lat,
                "lon": center_lon,
                "type": "Your Location",
                "status": "You are here",
                "distance": "0.0 km",
                "phone": "",
                "summary": f"Your Location: {location_label}",
                "color": [59, 130, 246, 255],
                "radius": 550,
            })

        for f in matched:
            if f["type"] == "Blood Bank":
                color = [220, 38, 38, 200]
                summary = f"Blood Bank • Total Units: {sum(f.get('blood_stock', {}).values())}"
            elif f.get("beds_available", 0) > 15:
                color = [34, 197, 94, 200]
                summary = f"Hospital • Beds: {f.get('beds_available')} (ICU: {f.get('icu_available')}, O₂: {f.get('oxygen_available')})"
            else:
                color = [245, 158, 11, 200]
                summary = f"Hospital (Limited) • Beds: {f.get('beds_available')} (ICU: {f.get('icu_available')})"

            map_data.append({
                "name": f["name"],
                "lat": f["lat"],
                "lon": f["lon"],
                "type": f["type"],
                "status": f.get("status", ""),
                "distance": f"{f['distance_km']} km",
                "phone": f.get("phone", ""),
                "summary": summary,
                "color": color,
                "radius": 500 if f["type"] == "Hospital" else 350,
            })

        df_map = pd.DataFrame(map_data)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius="radius",
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
        )

        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={
                    "html": "<b>{name}</b><br/>{summary}<br/>📍 Distance: {distance}<br/>📞 {phone}",
                    "style": {"color": "white", "backgroundColor": "#1e293b", "padding": "8px", "borderRadius": "4px"},
                },
                map_style="light",
            )
        )
        st.caption("🎯 Blue: Your Live Location  |  🟢 Green: Hospital with Beds  |  🟠 Amber: Limited Beds  |  🔴 Red: Blood Bank")
    else:
        st.info("No facilities found matching your specific filters. Try increasing the search radius or clearing filters.")

    # Facility Details Cards
    st.markdown("### 📋 Facility Vacancy Details (Sorted by Proximity)")
    for f in matched:
        with st.container(border=True):
            head_col, dist_col = st.columns([3, 1])
            icon = "🏥" if f["type"] == "Hospital" else "🩸"
            with head_col:
                st.markdown(f"#### {icon} {f['name']}")
                st.caption(f"📍 {f['address']}  •  🕒 Live Update: {f.get('last_updated', 'Just now')}")
            with dist_col:
                st.markdown(f"**📍 {f['distance_km']} km away**")
                st.markdown(f"<span style='color:{f.get('status_color')}; font-weight:bold;'>● {f.get('status')}</span>", unsafe_allow_html=True)

            if f["type"] == "Hospital":
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Available Beds", f"{f['beds_available']} / {f['beds_total']}")
                c2.metric("ICU Beds", f"{f['icu_available']}")
                c3.metric("Oxygen Beds", f"{f['oxygen_available']}")
                c4.metric("Ventilators", f"{f['ventilators_available']}")

            blood_stock = f.get("blood_stock", {})
            if blood_stock:
                st.markdown("**🩸 Available Blood Stock:**")
                b_cols = st.columns(len(blood_stock))
                for idx, (grp, units) in enumerate(blood_stock.items()):
                    with b_cols[idx]:
                        highlight = "bold" if grp == req_blood else "normal"
                        color_code = "#dc2626" if units < 5 else "#16a34a"
                        st.markdown(
                            f"<div style='text-align:center; border:1px solid #cbd5e1; border-radius:6px; padding:4px; margin-bottom:8px;'>"
                            f"<b>{grp}</b><br/><span style='color:{color_code}; font-weight:{highlight};'>{units} units</span></div>",
                            unsafe_allow_html=True,
                        )

            act_col1, act_col2 = st.columns(2)
            with act_col1:
                st.link_button(f"📞 Call: {f['phone']}", f"tel:{f['phone'].replace(' ', '')}", use_container_width=True)
            with act_col2:
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={f['lat']},{f['lon']}"
                st.link_button("🗺️ Open in Google Maps", maps_url, use_container_width=True)

# ==============================================================================
# TAB 4: SYMPTOMS CHECKER
# ==============================================================================
with tab_sym:
    st.markdown("### 🤒 Intelligent Symptom Assessment")
    st.caption("Select your symptoms for instant preliminary screening and danger sign detection.")

    sel = st.multiselect("Select your symptoms", knowledge.SYMPTOMS)
    days = st.select_slider("For how many days have you had these symptoms?", options=[1, 2, 3, 5, 7, 14], value=1)
    extra = st.text_input("Anything else? (checked for danger signs)", placeholder="e.g. feeling dizzy, pain spreading to arm...")

    if sel or extra:
        res = knowledge.match(sel, days)
        danger = safety.detect(extra + " " + " ".join(sel))
        if res["urgent"] or danger:
            st.error("🚨 **Seek emergency care now: call 112 or 108 immediately.**")
        elif res["see_doctor"]:
            st.warning("⚠️ Symptoms lasting this long should be clinically checked by a physician.")
        else:
            st.success("✅ No urgent emergency red flags detected from your selected symptoms.")

        st.markdown("#### 🔬 Potential Health Matches")
        for c in res["matches"]:
            with st.container(border=True):
                st.markdown(f"**{c['name']}**  ·  *Symptom overlap: {int(c['overlap'] * 100)}%*")
                st.write(c["advice"])
        st.caption("Overlap indicates symptom match only, not a formal medical diagnosis.")
    else:
        st.info("Pick at least one symptom from the list above to begin assessment.")

# ==============================================================================
# TAB 5: VITALS, BMI & FIRST AID
# ==============================================================================
with tab_vit:
    st.markdown("### ❤️ Vital Signs Evaluator & Emergency First Aid")

    v_left, v_right = st.columns([1, 1])

    with v_left:
        st.markdown("#### 🩺 Record Vital Signs")
        c1, c2 = st.columns(2)
        sys_ = c1.number_input("Systolic BP (mmHg)", 0, 300, 0)
        dia = c2.number_input("Diastolic BP (mmHg)", 0, 200, 0)
        hr = c1.number_input("Pulse Rate (bpm)", 0, 250, 0)
        temp = c2.number_input("Temperature (°C)", 0.0, 45.0, 0.0, 0.1)
        spo2 = c1.number_input("SpO₂ Oxygen (%)", 0, 100, 0)
        sugar = c2.number_input("Fasting Blood Sugar (mg/dL)", 0, 600, 0)

        out = knowledge.vitals({"sys": sys_, "dia": dia, "hr": hr, "temp": temp, "spo2": spo2, "sugar": sugar})
        show = {"ok": st.success, "warn": st.warning, "bad": st.error}
        for r in out:
            show[r["level"]](f"**{r['label']}: {r['value']}** — {r['note']}")
        if not out:
            st.info("Enter any vital values above to see clinical evaluations.")

        st.divider()
        st.markdown("#### ⚖️ BMI Calculator (Asian Standard)")
        b1, b2 = st.columns(2)
        h_cm = b1.number_input("Height (cm)", 0, 250, 0)
        w_kg = b2.number_input("Weight (kg)", 0, 300, 0)
        if h_cm and w_kg:
            b = w_kg / (h_cm / 100) ** 2
            label = (
                "Underweight"
                if b < 18.5
                else "Healthy"
                if b < 23
                else "Overweight (Asian cut-off)"
                if b < 25
                else "Overweight"
                if b < 30
                else "Obese range"
            )
            st.metric("Body Mass Index (BMI)", f"{b:.1f}", label, delta_color="off")

    with v_right:
        st.markdown("#### 🩹 Emergency First Aid Protocol Guides")
        st.caption("Call 108 or 112 first for emergencies, then follow these verified steps.")
        for title, steps in knowledge.AID.items():
            with st.expander(title):
                for i, s in enumerate(steps, 1):
                    st.markdown(f"**{i}.** {s}")

# Website Footer
st.markdown("---")
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("**🚑 National Emergency Numbers**")
    st.caption("• **112**: All-in-One National Emergency\n• **108**: 24/7 Ambulance & Trauma\n• **102**: Mother & Child Ambulance\n• **104**: State Health Advice")
with f2:
    st.markdown("**🧠 Mental Health & Wellness**")
    st.caption("• **Tele-MANAS**: 14416 (Toll-Free 24/7)\n• **KIRAN Helpline**: 1800-599-0019\n• Consult your nearest PHC or ASHA worker.")
with f3:
    st.markdown("**ℹ️ MediMind Disclaimer**")
    st.caption("MediMind AI provides informational screening only. It does not replace professional clinical evaluation, medical diagnosis, or emergency dispatch.")
