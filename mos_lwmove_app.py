import streamlit as st
from datetime import datetime

st.set_page_config(page_title="MOS - LWMove", layout="wide", page_icon="⛏️")
st.title("MOS - LWMove")
st.markdown("**Longwall Move Tracking**  \nPrototype v1.2 – Pictorial Webflow-style drag-and-drop longwall system builder")

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["🖼️ Longwall System Layout (Drag & Drop)", "🏠 Dashboard (Placeholder)", "🛠 Pre-Install (Placeholder)", "🔩 Bolt-Up (Placeholder)", "🛡️ Recovery (Placeholder)", "📦 Install (Placeholder)", "📊 Metrics & Reports (Placeholder)", "📥 Data Input (Placeholder)"])

# Session state for placed components
if "placed_components" not in st.session_state:
    st.session_state.placed_components = {}  # zone -> list of components

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

if page == "🖼️ Longwall System Layout (Drag & Drop)":
    st.header("Longwall System Layout – Visual Drag & Drop Builder")
    st.caption("Webflow-style canvas: click a component from the palette, then click a zone to place it. Built from Eickhoff SL750, Nepean AFC, CAT PRS and monorail drawings.")

    # Left palette
    st.sidebar.subheader("Component Palette")
    picked = None
    for comp in st.session_state.components.keys():
        if st.sidebar.button(f"📦 {comp}", key=f"pick_{comp}"):
            picked = comp
            st.session_state["currently_picked"] = comp
            st.rerun()

    # Central canvas – visual longwall layout
    st.subheader("Full Longwall Face (MG left → TG right)")
    canvas_cols = st.columns([1.5, 1.5, 5, 1.5, 1.5])

    # MG End zone
    with canvas_cols[0]:
        st.success("**MG End**  \nBootend / MG Drive  \n(approx. 3.5 m)")
        if st.button("Drop here", key="drop_mg"):
            if "currently_picked" in st.session_state:
                comp = st.session_state["currently_picked"]
                st.session_state.placed_components.setdefault("MG End", []).append(comp)
                st.session_state.components[comp]["status"] = "Installed"
                st.session_state.components[comp]["timestamp"] = datetime.now().strftime("%d/%m %H:%M")
                st.success(f"{comp} placed")
                st.rerun()

    # BSL / Crusher zone
    with canvas_cols[1]:
        st.info("**BSL & Crusher Area**")
        if st.button("Drop here", key="drop_bsl"):
            if "currently_picked" in st.session_state:
                comp = st.session_state["currently_picked"]
                st.session_state.placed_components.setdefault("BSL Area", []).append(comp)
                st.session_state.components[comp]["status"] = "Installed"
                st.session_state.components[comp]["timestamp"] = datetime.now().strftime("%d/%m %H:%M")
                st.success(f"{comp} placed")
                st.rerun()

    # Central AFC Panline + Roof Supports + Shearer zone (wide)
    with canvas_cols[2]:
        st.subheader("AFC Panline (195 pans total)")
        st.caption("Standard • Inspection • Mid-face • MGRR/TGRR (Nepean BOM)")
        st.progress(60, text="60 % placed along face")
        st.caption("CAT 2-leg Roof Supports (1400/2750-1040T) placed under pans")
        
        # Shearer position
        st.subheader("Shearer SL750 Model 6810")
        st.caption("Length ≈ 14.57 m • Web = 1000 mm (Eickhoff P0100056)")
        if st.button("Drop Shearer here", key="drop_shearer"):
            if "currently_picked" in st.session_state:
                comp = st.session_state["currently_picked"]
                st.session_state.placed_components.setdefault("Shearer Position", []).append(comp)
                st.session_state.components[comp]["status"] = "Installed"
                st.session_state.components[comp]["timestamp"] = datetime.now().strftime("%d/%m %H:%M")
                st.success(f"{comp} placed")
                st.rerun()

    # TG End zone
    with canvas_cols[4]:
        st.success("**TG End**  \nTG Drive / Bootend  \n(approx. 3.5 m)")
        if st.button("Drop here", key="drop_tg"):
            if "currently_picked" in st.session_state:
                comp = st.session_state["currently_picked"]
                st.session_state.placed_components.setdefault("TG End", []).append(comp)
                st.session_state.components[comp]["status"] = "Installed"
                st.session_state.components[comp]["timestamp"] = datetime.now().strftime("%d/%m %H:%M")
                st.success(f"{comp} placed")
                st.rerun()

    # Show placed items with remove option
    st.divider()
    st.subheader("Currently Placed on Face")
    for zone, items in st.session_state.placed_components.items():
        st.write(f"**{zone}**")
        for item in items[:]:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.caption(f"📍 {item}")
            with col2:
                if st.button("Remove", key=f"remove_{zone}_{item}"):
                    items.remove(item)
                    st.rerun()

else:
    st.header(f"{page} – On Hold")
    st.caption("Placeholder – the pictorial drag-and-drop builder is now the main focus")

st.sidebar.caption("MOS - LWMove v1.2  \nWebflow-style pictorial drag-and-drop longwall builder now live  \nOther pages paused as placeholders  \nReady for software team NEXIS bolt-on")