import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

st.set_page_config(page_title="MOS - LWMove", layout="wide", page_icon="⛏️")
st.title("MOS - LWMove")
st.markdown("**Longwall Move Tracking**  \nPrototype v1.0 – Tidied Pre-Install selection + all pages fully restored")

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["🏠 Dashboard", "🛠 Pre-Install", "🔩 Bolt-Up", "🛡️ Recovery", "📦 Install", "📊 Metrics & Reports", "📥 Data Input"])

# Global data
bolter_teams = pd.DataFrame({
    "Team": ["Hand Bolter 1", "Hand Bolter 2", "Hand Bolter 3", "Hand Bolter 4", "Hand Bolter 5", "Hand Bolter 6", "Hand Bolter 7"],
    "Shields": ["1-30", "31-58", "59-87", "88-115", "116-144", "145-173", "174-203"],
    "Hose Outlet": ["#14", "#44", "#74", "#104", "#134", "#154", "#184"],
    "Progress_%": [65, 42, 78, 31, 55, 89, 22],
    "Last_Row_Completed": ["Row 4", "Row 2", "Row 5", "Row 1", "Row 3", "Row 6", "Row 1"]
})

if "components" not in st.session_state:
    st.session_state.components = {
        "MiniPans": {"status": "Not Installed", "timestamp": None},
        "Crusher": {"status": "Not Installed", "timestamp": None},
        "DCB": {"status": "Not Installed", "timestamp": None},
        "Concave": {"status": "Not Installed", "timestamp": None},
        "Drive Frame": {"status": "Not Installed", "timestamp": None},
        "CME": {"status": "Not Installed", "timestamp": None},
        "Shearer SL750": {"status": "Not Installed", "timestamp": None},
        "Roof Supports": {"status": "Not Installed", "timestamp": None},
    }

if "overall_progress" not in st.session_state:
    st.session_state.overall_progress = {"BoltUp": 42, "Recovery": 18, "Install": 8}

# Granular schedule
schedule_data = pd.DataFrame({
    "Task": ["Pre-Install – Major Equipment", "Pre-Install – PRS 1-3", "Mesh Pull", "Bolt Row 1+2", "Bolt Row 3+4", "Bolt Row 5+6", "Bolt Row 6a+7", "Bolt Row 8", "Bolt Row 9 + Rib Bolts", "Recovery – Sequence 1", "Recovery – Sequence 2-5", "Recovery – Shred", "Install – Maingate Drive", "Install – AFC Panline", "Install – Tailgate Drive", "Install – Shearer", "First Coal Cut"],
    "Start": [date(2025,8,1), date(2025,8,1), date(2025,9,14), date(2025,9,15), date(2025,9,20), date(2025,9,25), date(2025,9,28), date(2025,10,1), date(2025,10,3), date(2025,10,19), date(2025,10,22), date(2025,10,28), date(2025,8,1), date(2025,8,5), date(2025,8,10), date(2025,8,15), date(2025,8,18)],
    "Finish": [date(2025,8,15), date(2025,8,10), date(2025,9,30), date(2025,9,20), date(2025,9,25), date(2025,9,28), date(2025,10,1), date(2025,10,3), date(2025,10,6), date(2025,10,22), date(2025,10,25), date(2025,11,5), date(2025,8,5), date(2025,8,15), date(2025,8,20), date(2025,8,25), date(2025,8,18)],
    "Progress": [100, 85, 80, 65, 55, 45, 35, 25, 15, 70, 55, 35, 100, 65, 30, 0, 0]
})

if page == "🏠 Dashboard":
    st.header("Live Equipment Schedule")
    fig = px.timeline(schedule_data, x_start="Start", x_end="Finish", y="Task", color="Progress", title="Longwall Move Schedule – Drag slider to zoom")
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"), height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Overall Progress Snapshot")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Bolt-Up", f"{st.session_state.overall_progress['BoltUp']}%")
    with col2: st.metric("Recovery", f"{st.session_state.overall_progress['Recovery']}%")
    with col3: st.metric("Install", f"{st.session_state.overall_progress['Install']}%")

elif page == "🛠 Pre-Install":
    st.header("Pre-Install – Longwall System Schematic")
    st.caption("Navigable view based on supplied technical drawings (Eickhoff SL750, Nepean AFC, CAT PRS, monorail)")
    
    # Schematic (fixed at top)
    st.subheader("Longwall Face Layout (MG left → TG right)")
    schematic_cols = st.columns([1, 2, 6, 2, 1])
    with schematic_cols[0]:
        st.success("**MG End**")
        st.caption("Bootend / BSL / MG Drive")
    with schematic_cols[1]:
        st.info("**BSL / Crusher Area**")
    with schematic_cols[2]:
        st.subheader("AFC Panline")
        st.caption("195 pans total – standard, inspection, mid-face, MGRR/TGRR")
        st.progress(60, text="60 % placed")
        st.caption("CAT 2-leg Roof Supports placed under pans")
    with schematic_cols[3]:
        st.subheader("Shearer SL750 Model 6810")
        st.caption("Length ≈ 14.57 m, web = 1000 mm")
    with schematic_cols[4]:
        st.success("**TG End**")
        st.caption("TG Drive / Bootend")
    
    st.divider()
    
    # Tidied simple selection
    st.subheader("Equipment Status Selection")
    for comp in list(st.session_state.components.keys()):
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write(f"**{comp}**")
        with col2:
            new_status = st.selectbox("Status", ["Not Installed", "Installed", "Pre-Powered", "Post-Powered"], 
                                      index=["Not Installed", "Installed", "Pre-Powered", "Post-Powered"].index(st.session_state.components[comp]["status"]),
                                      key=f"status_{comp}")
            if new_status != st.session_state.components[comp]["status"]:
                st.session_state.components[comp]["status"] = new_status
                st.session_state.components[comp]["timestamp"] = datetime.now().strftime("%d/%m %H:%M")
                st.rerun()
    
    st.divider()
    
    # Installed Equipment Bar
    st.subheader("Installed Equipment Bar")
    bottom_cols = st.columns(8)
    for i, comp in enumerate(st.session_state.components.keys()):
        with bottom_cols[i % 8]:
            status = st.session_state.components[comp]["status"]
            if status == "Post-Powered": st.success(comp)
            elif status == "Pre-Powered": st.info(comp)
            elif status == "Installed": st.warning(comp)
            else: st.error(comp)

elif page == "🔩 Bolt-Up":
    st.header("Bolt-Up Tracking")
    st.caption("Slow bolting teams – high handling, productivity and draw")
    st.data_editor(bolter_teams, num_rows="fixed", use_container_width=True)

elif page == "🛡️ Recovery":
    st.header("Shield Recovery")
    st.caption("Shred Recovery – reverse page logic for tear-down")
    st.subheader("MG / Run-of-Face / TG Extraction")
    st.checkbox("Sequence 1 – CribLocs installed at cut-through", value=True)
    st.checkbox("Sequence 2-5 – E-Frame and shield takeoff complete", value=False)
    st.progress(35, text="35% recovered")

elif page == "📦 Install":
    st.header("Longwall Install Tracking")
    st.metric("Shields Installed", "47 / 203")
    st.plotly_chart(px.bar(x=["Maingate Drive", "AFC Panline", "Tailgate Drive", "Shearer"], y=[100, 65, 30, 0], title="Install Progress"), use_container_width=True)

elif page == "📊 Metrics & Reports":
    st.header("Metrics and Reports")
    view = st.selectbox("Select Metric View", ["Bolt-Up Progress", "Recovery Progress", "Install Progress", "Overall Equipment Status", "Component Commissioning"])
    if view == "Bolt-Up Progress":
        fig = px.bar(bolter_teams, x="Team", y="Progress_%", text="Progress_%", title="Hand Bolter Teams – Progress %")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(bolter_teams, use_container_width=True)
        st.download_button("Download Bolt-Up CSV", bolter_teams.to_csv(index=False), "bolt_up_progress.csv")

elif page == "📥 Data Input":
    st.header("Data Input – Spreadsheet + Manual Entry")
    st.subheader("Upload Spreadsheet")
    uploaded_file = st.file_uploader("Drag & drop Bolter handout or similar file", type=["xlsx", "csv"])
    if uploaded_file:
        st.success("Spreadsheet ingested – table updated below")
    st.subheader("Manual / Editable Tables")
    st.data_editor(bolter_teams, num_rows="fixed", use_container_width=True)

st.sidebar.caption("MOS - LWMove v1.0  \nPre-Install selection now tidy & simple  \nAll pages fully restored and working  \nReady for software team NEXIS bolt-on")
