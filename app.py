import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from weather_api import NER_LOCATIONS, fetch_live_weather

st.set_page_config(page_title="NER Landslide Early Warning System", layout="wide")

# Multi-Language Translation Dictionary
LANGUAGES = {
    "English": {
        "title": "🚨 AI-Based Early Warning & Landslide Risk Monitoring System (NER)",
        "sidebar_header": "⚙️ Data Source & Controls",
        "data_mode": "Data Input Mode",
        "mode_live": "Live API Feed",
        "mode_manual": "Manual Simulation Sliders",
        "preset_sectors": "Preset Sectors",
        "btn_focus": "Focus Selected Preset",
        "rainfall_label": "Current Rainfall (mm/hr)",
        "antecedent_label": "3-Day Antecedent Rainfall (mm)",
        "slope_label": "Terrain Slope (°)",
        "moisture_label": "Soil Moisture (%)",
        "score": "Calculated Risk Score",
        "status": "Threat Severity",
        "highway": "Key Highway Status",
        "low_risk": "LOW RISK",
        "med_risk": "MEDIUM RISK",
        "high_risk": "HIGH RISK / CRITICAL",
        "road_open": "🟢 Clear & Open",
        "road_caution": "🟡 Caution Advised",
        "road_closed": "🔴 Road Closure Warning",
        "alert_emergency": "EMERGENCY WARNING ISSUED FOR",
        "alert_desc": "⚠️ High probability of slope failure! Automated warning dispatched to local responders.",
        "btn_siren": "🔊 Replay Siren",
        "map_title": "🗺️ GIS Real-Time Map — Location:",
        "map_caption": "💡 Click anywhere on the map to place a pin and recalculate risk for that location.",
        "chart_title": "📊 24-Hour Rainfall Trend & Threshold Analytics",
        "infra_title": "🛣️ Infrastructure & Road Connectivity Status",
        "col_route": "Route Name",
        "col_risk": "Risk Level",
        "col_status": "Status",
        "sector_prefix": "Sector around",
        "dispatch_title": "📲 Disaster Management Alert Dispatcher",
        "dispatch_expander": "⚡ Dispatch Emergency SMS / Email Notification",
        "dispatch_desc": "Simulate sending instant operational alerts to local responders and District Disaster Management Authorities (DDMA).",
        "recipient_label": "Recipient Phone Number / Email",
        "channel_label": "Dispatch Channel",
        "btn_dispatch": "🚀 Dispatch Simulated Emergency Alert",
        "reporting_title": "📱 Citizen & Field Official Hazard Reporting",
        "input_location": "Incident Location / Route",
        "input_hazard": "Hazard Observed",
        "hazards": ["Slope Cracks", "Minor Rockfall", "Road Blockage", "Heavy Runoff"],
        "upload_photo": "Upload Field Photo",
        "btn_submit": "Submit Incident Report",
        "recent_reports": "📋 Recent Field Incident Reports",
        "no_reports": "No reports submitted yet during this session.",
        "flagged_status": "Flagged for Verification",
        "report_success": "Report recorded!",
        "ml_title": "🧠 Model Explainability & Feature Weights",
        "ml_expander": "🔍 View AI/ML Scoring Architecture",
        "export_title": "📄 Export Situational Report for Authorities",
        "btn_download": "📥 Download Situational Report (.TXT)"
    },
    "Hindi": {
        "title": "🚨 एआई-आधारित भूस्खलन पूर्व चेतावनी प्रणाली (NER)",
        "sidebar_header": "⚙️ डेटा स्रोत और नियंत्रण",
        "data_mode": "डेटा इनपुट मोड",
        "mode_live": "लाइव एपीआई फीड",
        "mode_manual": "मैनुअल सिमुलेशन स्लाइडर",
        "preset_sectors": "पूर्वनिर्धारित क्षेत्र",
        "btn_focus": "चयनित क्षेत्र पर ध्यान केंद्रित करें",
        "rainfall_label": "वर्तमान वर्षा (मिमी/घंटा)",
        "antecedent_label": "3-दिवसीय पूर्ववर्ती वर्षा (मिमी)",
        "slope_label": "ढलान (°)",
        "moisture_label": "मृदा नमी (%)",
        "score": "गणना किया गया जोखिम स्कोर",
        "status": "खतरे की गंभीरता",
        "highway": "प्रमुख राजमार्ग स्थिति",
        "low_risk": "कम जोखिम",
        "med_risk": "मध्यम जोखिम",
        "high_risk": "उच्च जोखिम / गंभीर",
        "road_open": "🟢 खुला और स्पष्ट",
        "road_caution": "🟡 सावधानी बरतें",
        "road_closed": "🔴 मार्ग बंद चेतावनी",
        "alert_emergency": "आपातकालीन चेतावनी जारी:",
        "alert_desc": "⚠️ भूस्खलन की अत्यधिक संभावना! स्थानीय उत्तरदाताओं को स्वचालित चेतावनी भेजी गई।",
        "btn_siren": "🔊 सायरन बजाएं",
        "map_title": "🗺️ जीआईएस वास्तविक समय मानचित्र — स्थान:",
        "map_caption": "💡 मानचित्र पर कहीं भी क्लिक करके पिन लगाएं और जोखिम की पुनः गणना करें।",
        "chart_title": "📊 24-घंटे का वर्षा रुझान और सीमा विश्लेषण",
        "infra_title": "🛣️ बुनियादी ढांचा और सड़क संपर्क स्थिति",
        "col_route": "मार्ग का नाम",
        "col_risk": "जोखिम स्तर",
        "col_status": "स्थिति",
        "sector_prefix": "क्षेत्र के आसपास",
        "dispatch_title": "📲 आपदा प्रबंधन अलर्ट प्रेषक",
        "dispatch_expander": "⚡ आपातकालीन एसएमएस / ईमेल अधिसूचना भेजें",
        "dispatch_desc": "स्थानीय प्रतिक्रियाकर्ताओं और जिला आपदा प्रबंधन प्राधिकरणों (डीडीएमए) को त्वरित अलर्ट भेजें।",
        "recipient_label": "प्राप्तकर्ता फोन नंबर / ईमेल",
        "channel_label": "चैनल",
        "btn_dispatch": "🚀 आपातकालीन अलर्ट भेजें",
        "reporting_title": "📱 नागरिक और क्षेत्र अधिकारी खतरा रिपोर्टिंग",
        "input_location": "घटना का स्थान / मार्ग",
        "input_hazard": "देखा गया खतरा",
        "hazards": ["ढलान में दरारें", "मामूली चट्टान गिरना", "सड़क अवरोध", "भारी जलभराव"],
        "upload_photo": "क्षेत्र की तस्वीर अपलोड करें",
        "btn_submit": "घटना रिपोर्ट जमा करें",
        "recent_reports": "📋 हालिया क्षेत्र घटना रिपोर्ट",
        "no_reports": "इस सत्र के दौरान अभी तक कोई रिपोर्ट दर्ज नहीं की गई है।",
        "flagged_status": "सत्यापन के लिए चिह्नित",
        "report_success": "रिपोर्ट दर्ज की गई!",
        "ml_title": "🧠 मॉडल स्पष्टीकरण और फीचर महत्व",
        "ml_expander": "🔍 एआई/एमएल स्कोरिंग आर्किटेक्चर देखें",
        "export_title": "📄 अधिकारियों के लिए स्थिति रिपोर्ट निर्यात करें",
        "btn_download": "📥 स्थिति रिपोर्ट डाउनलोड करें (.TXT)"
    },
    "Assamese": {
        "title": "🚨 এআই ভিত্তিক ভূমিস্খলন পূৰ্ব সতৰ্কবাৰ্তা ব্যৱস্থা (NER)",
        "sidebar_header": "⚙️ তথ্য উৎস আৰু নিয়ন্ত্ৰণ",
        "data_mode": "তথ্য ইনপুট ম'ড",
        "mode_live": "লাইভ API ফিড",
        "mode_manual": "মেনুৱেল ছিমিউলেশ্বন শ্লাইডাৰ",
        "preset_sectors": "পূৰ্বনিৰ্ধাৰিত অঞ্চল",
        "btn_focus": "নিৰ্বাচিত অঞ্চল ফ'কাছ কৰক",
        "rainfall_label": "বৰ্তমান বৰষুণ (মিঃমিঃ/ঘণ্টা)",
        "antecedent_label": "৩-দিনীয়া পূৰ্বৱৰ্তী বৰষুণ (মিঃমিঃ)",
        "slope_label": "ভূ-ভাগৰ হেলনীয়া মাত্ৰা (°)",
        "moisture_label": "মাটিৰ আৰ্দ্ৰতা (%)",
        "score": "ঝুঁকিৰ স্কোৰ",
        "status": "সংকটৰ মাত্ৰা",
        "highway": "ৰাষ্ট্ৰীয় ঘাইপথৰ অৱস্থা",
        "low_risk": "কম ঝুঁকি",
        "med_risk": "মাজৰীয় ঝুঁকি",
        "high_risk": "উচ্চ ঝুঁকি / সংকটজনক",
        "road_open": "🟢 খ খোলা আৰু পৰিষ্কাৰ",
        "road_caution": "🟡 সাৱধানতা অৱলম্বন কৰক",
        "road_closed": "🔴 পথ বন্ধৰ সতৰ্কবাৰ্তা",
        "alert_emergency": "জৰুৰীকালীন সতৰ্কবাৰ্তা জাৰি কৰা হৈছে:",
        "alert_desc": "⚠️ ভূমিস্খলনৰ তীব্ৰ সম্ভাৱনা! স্থানীয় প্ৰশাসনলৈ স্বয়ংক্ৰিয় বাৰ্তা প্ৰেৰণ কৰা হৈছে।",
        "btn_siren": "🔊 চাইৰেণ বজাওঁক",
        "map_title": "🗺️ GIS ৰিয়েল-টাইম মেপ — স্থান:",
        "map_caption": "💡 স্থান সলনি কৰিবলৈ আৰু ঝুঁকি পুনৰ গণনা কৰিবলৈ মেপৰ যিকোনো ঠাইত ক্লিক কৰক।",
        "chart_title": "📊 ২৪-ঘণ্টাৰ বৰষুণৰ ট্ৰেণ্ড আৰু বিশ্লেষণ",
        "infra_title": "🛣️ আন্তঃগাঁথনি আৰু পথ যোগাযোগৰ অৱস্থা",
        "col_route": "পথৰ নাম",
        "col_risk": "ঝুঁকিৰ মাত্ৰা",
        "col_status": "অৱস্থা",
        "sector_prefix": "আশে-পাশে অঞ্চল",
        "dispatch_title": "📲 দুৰ্যোগ প্ৰশমন সতৰ্কবাৰ্তা প্ৰেৰণ কৰ্তা",
        "dispatch_expander": "⚡ জৰুৰীকালীন SMS / Email প্ৰেৰণ কৰক",
        "dispatch_desc": "স্থানীয় প্ৰশাসন আৰু জিলা দুৰ্যোগ প্ৰশমন কৰ্তৃপক্ষলৈ তাৎক্ষণিক বাৰ্তা প্ৰেৰণ কৰক।",
        "recipient_label": "প্ৰাপকৰ ফোন নম্বৰ / ইমেইল",
        "channel_label": "প্ৰেৰণৰ মাধ্যম",
        "btn_dispatch": "🚀 সতৰ্কবাৰ্তা প্ৰেৰণ কৰক",
        "reporting_title": "📱 ৰাইজ আৰু ফিল্ড বিষয়াৰ দুৰ্যোগ প্ৰতিবেদন",
        "input_location": "দুৰ্যোগৰ স্থান / পথ",
        "input_hazard": "প্ৰত্যক্ষ কৰা বিপদ",
        "hazards": ["পাহাৰৰ ফাট", "শিলা খহি পৰা", "পথ অৱৰোধ", "তীব্ৰ পানীৰ সোঁত"],
        "upload_photo": "ঘটনাৰ ফটো আপলোড কৰক",
        "btn_submit": "প্ৰতিবেদন জমা দিয়ক",
        "recent_reports": "📋 শেহতীয়া ফিল্ড ৰিপৰ্টসমূহ",
        "no_reports": "এই চেছনত কোনো প্ৰতিবেদন জমা দিয়া হোৱা নাই।",
        "flagged_status": "পৰীক্ষাৰ বাবে প্ৰেৰণ কৰা হৈছে",
        "report_success": "প্ৰতিবেদন লিপিবদ্ধ কৰা হ'ল!",
        "ml_title": "🧠 AI/ML মডেলৰ ব্যাখ্যা আৰু বৈশিষ্ট্যসূচক বিশ্লেষণ",
        "ml_expander": "🔍 AI/ML স্ক'ৰিং আৰ্কিটেকচাৰ চাওক",
        "export_title": "📄 কৰ্তৃপক্ষৰ বাবে প্ৰতিবেদন সংগ্ৰহ কৰক",
        "btn_download": "📥 প্ৰতিবেদন ডাউনলোড কৰক (.TXT)"
    }
}

# Language Selector Sidebar
selected_lang = st.sidebar.selectbox("🌐 Select Interface Language", list(LANGUAGES.keys()))
t = LANGUAGES[selected_lang]

# Dynamic Title Header
st.title(t["title"])
st.caption("Target Region: North Eastern Region (NER) | SIH PS ID: 26001")

# Helper function for reverse geocoding
@st.cache_data(ttl=3600)
def get_location_name(lat, lon):
    try:
        geolocator = Nominatim(user_agent="sih_landslide_app")
        location = geolocator.reverse((lat, lon), timeout=5, language="en")
        if location:
            address = location.raw.get("address", {})
            place = (
                address.get("city") 
                or address.get("town") 
                or address.get("village") 
                or address.get("state_district") 
                or address.get("county") 
                or "Unknown Location"
            )
            state = address.get("state", "")
            return f"{place}, {state}" if state else place
    except Exception:
        pass
    return f"Sector ({lat:.2f}, {lon:.2f})"

# Initialize Session States
if "selected_lat" not in st.session_state:
    st.session_state["selected_lat"] = 25.5788
    st.session_state["selected_lon"] = 91.8933
    st.session_state["location_name"] = "Shillong (Meghalaya)"

if "citizen_reports" not in st.session_state:
    st.session_state["citizen_reports"] = []

# Sidebar Controls
st.sidebar.header(t["sidebar_header"])
data_mode_choice = st.sidebar.radio(t["data_mode"], [t["mode_live"], t["mode_manual"]])

if data_mode_choice == t["mode_live"]:
    selected_city = st.sidebar.selectbox(t["preset_sectors"], list(NER_LOCATIONS.keys()))
    
    if st.sidebar.button(t["btn_focus"]):
        st.session_state["selected_lat"] = NER_LOCATIONS[selected_city]["lat"]
        st.session_state["selected_lon"] = NER_LOCATIONS[selected_city]["lon"]
        st.session_state["location_name"] = selected_city

    weather = fetch_live_weather(st.session_state["selected_lat"], st.session_state["selected_lon"])
    rainfall = weather["current_rainfall_mm"]
    antecedent = weather["antecedent_3day_mm"]
    
    st.sidebar.info(f"API Status: {weather['status']}")
    st.sidebar.metric(t["rainfall_label"], f"{rainfall} mm/hr")
    st.sidebar.metric(t["antecedent_label"], f"{antecedent} mm")
    
    slope = st.sidebar.slider(t["slope_label"], 0.0, 60.0, 38.0)
    soil_moisture = st.sidebar.slider(t["moisture_label"], 0.0, 100.0, 75.0)
else:
    rainfall = st.sidebar.slider(t["rainfall_label"], 0.0, 100.0, 65.0)
    antecedent = st.sidebar.slider(t["antecedent_label"], 0.0, 400.0, 180.0)
    slope = st.sidebar.slider(t["slope_label"], 0.0, 60.0, 45.0)
    soil_moisture = st.sidebar.slider(t["moisture_label"], 0.0, 100.0, 85.0)

# Calculate Risk Index
risk_score = min(100.0, (rainfall * 0.35) + (antecedent * 0.15) + (slope * 0.30) + (soil_moisture * 0.20))

if risk_score < 35:
    status, color = t["low_risk"], "green"
    road_status = t["road_open"]
elif risk_score < 65:
    status, color = t["med_risk"], "orange"
    road_status = t["road_caution"]
else:
    status, color = t["high_risk"], "red"
    road_status = t["road_closed"]

# Emergency Siren Alert
if risk_score >= 65:
    st.error(f"🚨 **{t['alert_emergency']} {st.session_state['location_name'].upper()}**")
    st.warning(t["alert_desc"])
    
    st.components.v1.html(f"""
        <div style="margin-top: 10px;">
            <button onclick="playSiren()" 
                    style="background-color: #ff4b4b; color: white; border: none; padding: 10px 18px; 
                           font-size: 14px; font-weight: bold; border-radius: 8px; cursor: pointer;">
                {t["btn_siren"]}
            </button>
            <script>
                function playSiren() {{
                    try {{
                        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        const osc = audioCtx.createOscillator();
                        const gain = audioCtx.createGain();
                        
                        osc.type = 'sawtooth';
                        osc.frequency.setValueAtTime(800, audioCtx.currentTime);
                        osc.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime + 0.7);
                        
                        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.7);
                        
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        
                        osc.start();
                        osc.stop(audioCtx.currentTime + 0.7);
                    }} catch (e) {{
                        console.log("Autoplay context pending interaction", e);
                    }}
                }}
                window.onload = function() {{
                    playSiren();
                }};
            </script>
        </div>
    """, height=60)

# Metric Summary Cards
col1, col2, col3 = st.columns(3)
col1.metric(t["score"], f"{risk_score:.1f} / 100")
col2.metric(t["status"], status)
col3.metric(t["highway"], road_status)

st.markdown("---")

# GIS Real-Time Map
current_place = st.session_state["location_name"]
st.subheader(f"{t['map_title']} {current_place}")
st.caption(t["map_caption"])

m = folium.Map(
    location=[st.session_state["selected_lat"], st.session_state["selected_lon"]], 
    zoom_start=10
)

folium.Marker(
    location=[st.session_state["selected_lat"], st.session_state["selected_lon"]],
    popup=f"<b>Location:</b> {current_place}<br><b>Risk:</b> {risk_score:.1f}<br><b>Status:</b> {status}",
    icon=folium.Icon(color=color, icon="info-sign")
).add_to(m)

map_data = st_folium(m, width=1100, height=450)

if map_data and map_data.get("last_clicked"):
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lon = map_data["last_clicked"]["lng"]
    
    if (clicked_lat != st.session_state["selected_lat"]) or (clicked_lon != st.session_state["selected_lon"]):
        st.session_state["selected_lat"] = clicked_lat
        st.session_state["selected_lon"] = clicked_lon
        st.session_state["location_name"] = get_location_name(clicked_lat, clicked_lon)
        st.rerun()

# 24-Hour Rainfall Analytics Chart
st.subheader(t["chart_title"])
hours = [f"-{i}h" for i in range(24, 0, -1)]
simulated_rainfall = np.clip(np.random.normal(loc=rainfall * 0.8, scale=4.0, size=24), 0, 100)
simulated_rainfall[-1] = rainfall

chart_data = pd.DataFrame({
    "Observed Rainfall (mm/hr)": simulated_rainfall,
    "Critical Threshold (50 mm/hr)": [50.0] * 24
}, index=hours)

st.line_chart(chart_data)

# Infrastructure Table
st.subheader(t["infra_title"])
route_data = pd.DataFrame([
    {t["col_route"]: f"{t['sector_prefix']} {current_place}", t["col_risk"]: status, t["col_status"]: road_status},
    {t["col_route"]: "NH-10 (Siliguri - Gangtok Corridor)", t["col_risk"]: status, t["col_status"]: road_status},
    {t["col_route"]: "NH-27 (Guwahati Corridor)", t["col_risk"]: t["low_risk"], t["col_status"]: t["road_open"]}
])
st.table(route_data)

# Disaster Management Alert Dispatcher
st.subheader(t["dispatch_title"])
with st.expander(t["dispatch_expander"]):
    st.write(t["dispatch_desc"])
    col_recipient, col_channel = st.columns([2, 1])
    with col_recipient:
        recipient = st.text_input(t["recipient_label"], "+91 98765 43210")
    with col_channel:
        channel = st.selectbox(t["channel_label"], ["SMS (Twilio API)", "WhatsApp Gateway", "Email"])
        
    if st.button(t["btn_dispatch"]):
        if risk_score >= 65:
            st.success(f"✅ CRITICAL ALERT dispatched to {recipient} via {channel}! Status: Delivered.")
        else:
            st.info(f"ℹ️ Advisory report dispatched to {recipient} via {channel}. Risk level currently normal.")

# Citizen Reporting Section
st.subheader(t["reporting_title"])
col_form, col_logs = st.columns([1, 1])

with col_form:
    with st.form("citizen_report_form"):
        report_loc = st.text_input(t["input_location"], current_place)
        hazard = st.selectbox(t["input_hazard"], t["hazards"])
        photo = st.file_uploader(t["upload_photo"], type=["jpg", "png"])
        submit = st.form_submit_button(t["btn_submit"])
        
        if submit:
            st.session_state["citizen_reports"].append({
                t["col_route"]: report_loc,
                t["input_hazard"]: hazard,
                t["col_status"]: t["flagged_status"]
            })
            st.success(f"{t['report_success']} ({hazard})")

with col_logs:
    st.markdown(f"**{t['recent_reports']}**")
    if st.session_state["citizen_reports"]:
        st.dataframe(pd.DataFrame(st.session_state["citizen_reports"]), use_container_width=True)
    else:
        st.info(t["no_reports"])

# ML Model Explainability & Feature Weights
st.subheader(t["ml_title"])
with st.expander(t["ml_expander"]):
    weights_df = pd.DataFrame({
        "Feature Parameter": ["Current Rainfall", "Terrain Slope", "Soil Moisture", "3-Day Antecedent Rainfall"],
        "Weight Share": ["35%", "30%", "20%", "15%"],
        "Current Value": [f"{rainfall} mm/hr", f"{slope}°", f"{soil_moisture}%", f"{antecedent} mm"]
    })
    st.table(weights_df)

st.markdown("---")

# Situational Report Exporter
st.subheader(t["export_title"])

report_content = f"""
==================================================
LANDSLIDE RISK & INFRASTRUCTURE REPORT
Generated via SIH Early Warning System
==================================================
Location Monitored: {current_place}
Calculated Risk Index: {risk_score:.1f} / 100
Threat Level: {status}
Highway Condition: {road_status}
--------------------------------------------------
Weather Parameters:
- Live Hourly Rainfall: {rainfall} mm/hr
- 3-Day Antecedent Rainfall: {antecedent} mm
- Terrain Slope: {slope}°
- Soil Moisture: {soil_moisture}%
==================================================
"""

st.download_button(
    label=t["btn_download"],
    data=report_content,
    file_name=f"landslide_report_{current_place.replace(' ', '_')}.txt",
    mime="text/plain"
)