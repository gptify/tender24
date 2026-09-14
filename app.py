import sys
import time
from pathlib import Path

# Add project root to sys.path so 'src' is always discoverable
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import json

try:
    from src.tender_ai.config import DEFAULT_COMPANY_PROFILE, SUPPORTED_PORTALS
    from src.tender_ai.document_parser import DocumentParser
    from src.tender_ai.analyzer import TenderAnalyzer
    from src.tender_ai.proposal_generator import ProposalGenerator
    from src.tender_ai.tender_finder import TenderFinder
    from src.tender_ai.docx_exporter import DocxExporter
    from src.tender_ai.portal_scanner import PortalScanner
    from src.tender_ai.notifier import TenderNotifier
    from src.tender_ai.db import DatabaseManager
    from src.tender_ai.telegram_bot_daemon import TelegramAlertDaemon
    from src.tender_ai.pages_content import render_pricing_page, render_guide_page, render_footer
except ImportError:
    from config import DEFAULT_COMPANY_PROFILE, SUPPORTED_PORTALS
    from document_parser import DocumentParser
    from analyzer import TenderAnalyzer
    from proposal_generator import ProposalGenerator
    from tender_finder import TenderFinder
    from docx_exporter import DocxExporter
    from portal_scanner import PortalScanner
    from notifier import TenderNotifier
    from db import DatabaseManager
    from telegram_bot_daemon import TelegramAlertDaemon
    from pages_content import render_pricing_page, render_guide_page, render_footer

# Page Configuration
st.set_page_config(
    page_title="TenderPro²⁴ — O'zbekiston Davlat va B2B Tenderlari Auditi",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling: Clean Modern B2B SaaS Theme (High-Contrast & Light Theme Safe)
st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    /* Widget Labels & Text */
    label[data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] span {
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    /* Input fields and Selectboxes */
    .stTextInput input,
    .stNumberInput input,
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: #EFF6FF !important;
        border-color: #3B82F6 !important;
        color: #1D4ED8 !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25) !important;
    }

    /* Stepper & Onboarding */
    .onboarding-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .step-badge {
        background-color: #EFF6FF;
        color: #1D4ED8;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        border: 1px solid #BFDBFE;
    }

    /* Risk boxes */
    .risk-red {
        background-color: #FFFFFF;
        border: 1px solid #FEE2E2;
        border-left: 5px solid #EF4444;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .risk-yellow {
        background-color: #FFFFFF;
        border: 1px solid #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .risk-green {
        background-color: #FFFFFF;
        border: 1px solid #DCFCE7;
        border-left: 5px solid #10B981;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Sample tender technical specification for instant 1-click test
SAMPLE_TENDER_TEXT = """
O'ZBEKISTON RESPUBLIKASI RAQAMLI TEXNOLOGIYALAR VAZIRLIGI HUZURIDAGI "ELEKTRON HUKUMAT" MARKAZI
LOT № 24110012398745
TEXNIK TOPSHIRIQ (ТЗ)
Mavzu: "Davlat organlari uchun yagona avtomatlashtirilgan sun'iy intellekt CRM va muloqot tizimini joriy qilish"

1. UMUMIY QOIDALAR VA MAQSAD:
1.1. Mazkur xaridning boshlang'ich narxi: 480,000,000 (To'rt yuz sakson million) so'm QQS bilan.
1.2. Ishlarni bajarish muddati: Shartnoma imzolangan kundan boshlab 45 (qirq besh) kalendar kuni.
1.3. Zaklad to'lovi (Bank kafolati): Boshlang'ich narxning 3% miqdorida portal hisobiga kiritilishi shart.

2. ISHTIROKCHILARGA QO'YILADIGAN MALAKA TALABLARI:
2.1. Ishtirokchi axborot texnologiyalari va dasturiy ta'minot sohasida kamida 2 (ikki) yillik tajribaga ega bo'lishi shart.
2.2. O'xshash yo'nalishdagi (AI botlar, integratsiyalar yoki CRM) kamida 2 ta muvaffaqiyatli topshirilgan loyiha dalolatnomalari taqdim etilishi lozim.
2.3. Korxona shtatida kamida 3 nafar oliy ma'lumotli IT mutaxassisi (diplom nusxalari bilan) mavjud bo'lishi shart.
2.4. Oxirgi 1 yillik moliyaviy aylanma mablag' kamida 300,000,000 so'mni tashkil etishi va soliq qarzdorligi bo'lmasligi lozim.

3. TEXNIK TALABLAR VA ISH HAJMI:
3.1. Tizim Telegram Bot va Web Dashboard orqali davlat xizmatlariga oid so'rovlarni avtomat qabul qilishi va LLM orqali tahlil qilishi kerak.
3.2. Didox va 1C tizimlari bilan xavfsiz REST API orqali ikki tomonlama integratsiya bo'lishi shart.
3.3. Tizim O'zbekistondagi serverlarda (O'zbektelekom yoki Uzinfocom ma'lumotlar markazida) joylashtirilishi shart.
3.4. Bajarilgan ishlarga 12 oylik kafolatli texnik ko'mak (SLA 99.5%) berilishi shart.

4. TO'LOV VA JAVOBGARLIK SHARTLARI (DIQQAT):
4.1. To'lov sharti: 0% avans. 100% to'lov barcha ishlar qabul qilinib, dalolatnoma imzolangandan so'ng 90 (to'qson) bank kuni ichida amalga oshiriladi.
4.2. Jarima shartlari: Muddat har bir kechiktirilgan kun uchun jami shartnoma summasining 0.5% miqdorida penya hisoblanadi (cheklanmagan).
4.3. Ishtirokchi server uskunalari faqat "Brand-X Server Model-9000" rusumli bo'lishi shart deb ko'rsatilgan.
"""

# Sidebar Configuration: User Authentication & Company Profile
with st.sidebar:
    st.header("👤 Foydalanuvchi & Profil")
    
    # Initialize or refresh session user from DB
    if "auth_user" not in st.session_state:
        user_rec = DatabaseManager.get_user("demo")
        if user_rec:
            st.session_state["auth_user"] = user_rec
        else:
            st.session_state["auth_user"] = {
                "username": "demo",
                "company_name": DEFAULT_COMPANY_PROFILE["name"],
                "tier": "pro",
                "credits_left": 999
            }
    else:
        refreshed = DatabaseManager.get_user(st.session_state["auth_user"]["username"])
        if refreshed:
            st.session_state["auth_user"] = refreshed

    current_user = st.session_state["auth_user"]
    tier_badge = "👑 PRO (Cheksiz)" if current_user["tier"] == "pro" else f"⭐ Bepul ({current_user['credits_left']} ta qoldi)"
    
    st.markdown(f"""
    <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="font-weight: 700; color: #1E3A8A; font-size: 1rem;">{current_user['company_name']}</div>
        <div style="font-size: 0.84rem; color: #64748B;">Login: <strong>@{current_user['username']}</strong></div>
        <div style="font-size: 0.86rem; color: #16A34A; font-weight: 700; margin-top: 4px;">Tarif: {tier_badge}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔑 Hisobni almashtirish"):
        tab_login, tab_reg = st.tabs(["Kirish", "Ro'yxatdan o'tish"])
        with tab_login:
            login_u = st.text_input("Login", value="demo", key="sb_login_u")
            login_p = st.text_input("Parol", value="demo123", type="password", key="sb_login_p")
            if st.button("Tizimga kirish", key="btn_login", use_container_width=True):
                user_record = DatabaseManager.authenticate_user(login_u, login_p)
                if user_record:
                    st.session_state["auth_user"] = user_record
                    st.success("Muvaffaqiyatli kirdingiz!")
                    st.rerun()
                else:
                    st.error("Login yoki parol noto'g'ri.")
        with tab_reg:
            reg_u = st.text_input("Yangi login", key="sb_reg_u")
            reg_p = st.text_input("Yangi parol", type="password", key="sb_reg_p")
            reg_comp = st.text_input("Kompaniya nomi", key="sb_reg_c")
            if st.button("3 ta bepul audit bilan ro'yxatdan o'tish", key="btn_reg", use_container_width=True):
                reg_res = DatabaseManager.register_user(reg_u, reg_p, reg_comp)
                if reg_res.get("success"):
                    st.success("Hisob yaratildi! Endi kirishingiz mumkin.")
                else:
                    st.error(reg_res.get("error"))

    st.divider()
    st.subheader("🏢 Kompaniya Rekvizitlari")
    comp_name = st.text_input("Kompaniya nomi", value=current_user["company_name"])
    comp_founder = st.text_input("Mas'ul shaxs", value=DEFAULT_COMPANY_PROFILE["founder"])
    comp_desc = st.text_area("Faoliyat sohasi", value=DEFAULT_COMPANY_PROFILE["description"], height=60)
    comp_exp = st.text_input("Tajriba davri", value=DEFAULT_COMPANY_PROFILE["experience_years"])
    
    st.divider()
    st.markdown("🌐 **Ulangan Portallar & Sektorlar:**")
    for portal, info in SUPPORTED_PORTALS.items():
        desc_text = info.get("name", "") if isinstance(info, dict) else str(info)
        sec_text = f"({info.get('sector', '')})" if isinstance(info, dict) and info.get("sector") else ""
        st.caption(f"• **{portal}** — {desc_text}")

company_profile = {
    "name": comp_name,
    "founder": comp_founder,
    "description": comp_desc,
    "experience_years": comp_exp,
    "core_services": DEFAULT_COMPANY_PROFILE["core_services"],
    "qualification_highlights": DEFAULT_COMPANY_PROFILE["qualification_highlights"]
}

# Top SaaS Header Bar
st.markdown("""
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 20px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="background: #2563EB; color: white; width: 38px; height: 38px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">
            ⚖️
        </div>
        <div>
            <div style="font-size: 1.35rem; font-weight: 900; color: #0F172A; line-height: 1.1; letter-spacing: -0.02em;">
                TenderPro<span style="color: #2563EB;">²⁴</span> <span style="font-size: 0.72rem; background-color: #0F172A; color: #38BDF8; font-weight: 700; padding: 2px 8px; border-radius: 8px; border: 1px solid #1E293B; vertical-align: middle;">AI SUITE</span>
            </div>
            <div style="font-size: 0.82rem; color: #64748B;">O'zbekiston Davlat, BMT va B2B Xaridlar Intellekti • GPTify.co</div>
        </div>
    </div>
    <div>
        <span style="background: #F8FAFC; color: #334155; font-size: 0.8rem; font-weight: 600; padding: 4px 10px; border-radius: 6px; border: 1px solid #E2E8F0;">
            Qamrov: Davlat xaridlari • Xalqaro NNT & BMT • Xususiy B2B & Banklar
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Clean, Native Streamlit Tabs
tab_radar, tab_audit, tab_docs, tab_telegram, tab_pricing, tab_guide = st.tabs([
    "🎯 1. Tenderlar Radari",
    "🔍 2. AI Audit & Tuzoqlar",
    "📝 3. Takliflar & Word (.docx)",
    "🔔 4. 24/7 Telegram Bot",
    "💎 5. Tariflar & Obuna",
    "🚀 6. Qo'llanma & Yechimlar"
])

# ---------------------------------------------------------
# ---------------------------------------------------------
# TAB 1: TENDERLAR RADARI (Live Multi-Sector Scanner & Radar)
# ---------------------------------------------------------
with tab_radar:
    # 1. Clear Guide Banner
    st.markdown("""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 20px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-weight: 700; color: #1E293B; font-size: 0.95rem;">💡 Qanday ishlatiladi?</span>
                <span style="color: #64748B; font-size: 0.88rem; margin-left: 8px;">
                    1. Kerakli xarid sektorini tanlang ➔ 2. Lot kartasidagi <strong>"⚡️ Audit Qilish"</strong> tugmasini bosing ➔ 3. <strong>"📝 3. Takliflar"</strong> tabida Word taklifini oling.
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Check if a lot or search query parameter was passed from Telegram link
    query_lot = st.query_params.get("lot") or st.query_params.get("search")
    if query_lot and "param_loaded" not in st.session_state:
        st.session_state["radar_kw"] = query_lot
        st.session_state["param_loaded"] = True
        current_kw = query_lot
    else:
        current_kw = st.session_state.get("radar_kw", "")
    
    with st.container(border=True):
        f_c1, f_c2, f_c3, f_c4 = st.columns([2.2, 1.2, 1.2, 1.0])
        with f_c1:
            search_query = st.text_input("🔍 Qidiruv:", value=current_kw, placeholder="Masalan: AI, CRM, BMT, Kredit skoringi, Didox...", label_visibility="collapsed")
        with f_c2:
            sort_choice = st.selectbox(
                "Saralash:",
                [
                    "🏆 AI Moslik (Eng yuqori)",
                    "💰 Byudjet (Eng qimmat)",
                    "💵 Byudjet (Eng arzon)",
                    "⏳ Topshirish muddati"
                ],
                label_visibility="collapsed"
            )
            sort_map = {
                "🏆 AI Moslik (Eng yuqori)": "match_score",
                "💰 Byudjet (Eng qimmat)": "budget_desc",
                "💵 Byudjet (Eng arzon)": "budget_asc",
                "⏳ Topshirish muddati": "deadline"
            }
            active_sort = sort_map[sort_choice]
        with f_c3:
            cat_choice = st.selectbox("Soha:", [
                "Barchasi", "Sun'iy Intellekt & LLM", "Bank & Fintech CRM", "Hisob-faktura & Audit IT",
                "Logistika & CRM", "Kiberxavfsizlik & IT Audit", "PropTech & ConTech IT", "E-Commerce & B2B SaaS",
                "MedTech & CRM", "Data & Analytics"
            ], label_visibility="collapsed")
        with f_c4:
            if st.button("🔄 Yangilash", use_container_width=True, help="Portallarni qayta tekshirish"):
                import os
                tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
                tg_chat = os.getenv("TELEGRAM_CHAT_ID", "")
                with st.spinner("Portallar tekshirilmoqda..."):
                    scan_res = PortalScanner.run_live_scan(
                        company_profile=company_profile,
                        auto_notify=bool(tg_token and tg_chat),
                        bot_token=tg_token,
                        chat_id=tg_chat
                    )
                    st.session_state["last_scan_res"] = scan_res
                    st.success(f"✅ {scan_res['total_lots']} ta lot yangilandi!")
                    st.rerun()

        # Quick keyword chips
        kw_col1, kw_col2, kw_col3, kw_col4, kw_col5, kw_col6 = st.columns(6)
        if kw_col1.button("🔥 AI / LLM", use_container_width=True):
            st.session_state["radar_kw"] = "AI"
            st.rerun()
        if kw_col2.button("⚡️ CRM & B2B", use_container_width=True):
            st.session_state["radar_kw"] = "CRM"
            st.rerun()
        if kw_col3.button("💎 BMT / NNT", use_container_width=True):
            st.session_state["radar_kw"] = "UNDP"
            st.rerun()
        if kw_col4.button("🏦 Bank & Skoring", use_container_width=True):
            st.session_state["radar_kw"] = "Bank"
            st.rerun()
        if kw_col5.button("📊 1C & Didox", use_container_width=True):
            st.session_state["radar_kw"] = "Didox"
            st.rerun()
        if kw_col6.button("🔄 Tozalash", use_container_width=True):
            st.session_state["radar_kw"] = ""
            st.rerun()

    # 3. Helper function to render lot cards
    def render_lot_card_list(sector_name: str):
        lots = TenderFinder.search_opportunities(
            query=search_query,
            min_budget=0,
            portal_filter="Barchasi",
            category_filter=cat_choice,
            sector_filter=sector_name,
            sort_by=active_sort,
            company_profile=company_profile
        )

        st.caption(f"Topilgan imkoniyatlar soni: **{len(lots)} ta lot**")

        if len(lots) == 0:
            st.info("Ushbu filtrlar bo'yicha lot topilmadi. Yuqoridagi qidiruv so'zini tozalab ko'ring.")
            return

        for opp in lots:
            score = opp.get("match_score", 50)
            badge_bg = "#DCFCE7" if score >= 80 else ("#FEF3C7" if score >= 55 else "#F1F5F9")
            badge_color = "#15803D" if score >= 80 else ("#B45309" if score >= 55 else "#475569")
            
            opp_sec = opp.get("sector", "Davlat sektori")
            sec_badge_color = "#1D4ED8" if opp_sec == "Davlat sektori" else ("#7C3AED" if "NNT" in opp_sec else "#047857")
            sec_badge_bg = "#EFF6FF" if opp_sec == "Davlat sektori" else ("#F5F3FF" if "NNT" in opp_sec else "#ECFDF5")
            sec_icon = "🏛" if opp_sec == "Davlat sektori" else ("💎" if "NNT" in opp_sec else "🏢")

            with st.container(border=True):
                o_h1, o_h2 = st.columns([3, 1.2])
                with o_h1:
                    st.markdown(f"#### {opp['title']}")
                    st.markdown(f"""
                    <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 6px;">
                        <span style="background-color: {sec_badge_bg}; color: {sec_badge_color}; font-weight: 700; padding: 2px 8px; border-radius: 8px; font-size: 0.78rem; border: 1px solid {sec_badge_color}30;">
                            {sec_icon} {opp_sec}
                        </span>
                        <span style="background-color: #F1F5F9; color: #334155; font-weight: 600; padding: 2px 8px; border-radius: 8px; font-size: 0.78rem;">
                            🌐 {opp['portal']}
                        </span>
                        <span style="color: #64748B; font-size: 0.78rem;">
                            ID: {opp['lot_id']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"🏛 **Buyurtmachi:** {opp['customer']}")
                with o_h2:
                    st.markdown(f"""
                    <div style="text-align: right;">
                        <span style="background-color: {badge_bg}; color: {badge_color}; font-weight: 700; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem;">
                            Moslik: {score}%
                        </span>
                        <div style="font-size: 1.15rem; font-weight: 800; color: #1E3A8A; margin-top: 4px;">{opp['starting_price']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.write(opp.get("description", ""))
                
                c_btn1, c_btn2, c_btn3 = st.columns([1.5, 1.5, 2])
                with c_btn1:
                    lot_btn_key = f"audit_lot_{sector_name}_{opp['lot_id']}"
                    if st.button("⚡️ Audit Qilish", key=lot_btn_key, type="primary", use_container_width=True):
                        full_text = f"TENDER / LOT: {opp['lot_id']}\nBUYURTMACHI: {opp['customer']}\nMAVZU: {opp['title']}\nPORTAL: {opp['portal']}\nSEKTOR: {opp_sec}\nBOSHLANG'ICH NARX: {opp['starting_price']}\nMUDDAT: {opp.get('deadline', 'Noma\'lum')}\n\nTAVSIF VA TALABLAR:\n{opp['description']}\n\nMALAKA TALABLARI:\n{opp.get('qualification_brief', 'Standart malaka talablari')}"
                        st.session_state["tender_text"] = full_text
                        st.session_state["current_tender_link"] = opp.get("link", "")
                        st.session_state["selected_lot_title"] = opp['title']
                        st.session_state["trigger_auto_analysis"] = True
                        st.success(f"✅ Tanlandi! Yuqoridagi **'🔍 2. AI Audit & Tuzoqlar'** tabiga o'ting.")

                with c_btn2:
                    if opp.get("link"):
                        st.link_button("Portaldagi Sahifa ↗", opp["link"], use_container_width=True)
                with c_btn3:
                    st.caption(f"⏳ Topshirish muddati: **{opp.get('deadline', 'Noma\'lum')}**")

    # 4. Native Sector Tabs for Instant, Reliable Switching
    sec_tab_all, sec_tab_ngo, sec_tab_b2b, sec_tab_state = st.tabs([
        "🌐 Barcha Sektorlar",
        "💎 Xalqaro NNT & BMT (UN / Grants)",
        "🏢 Xususiy B2B & Banklar",
        "🏛 Davlat Xaridlari (UzEx)"
    ])

    with sec_tab_all:
        render_lot_card_list("Barchasi")

    with sec_tab_ngo:
        st.info("💡 **Xalqaro NNT va BMT (UNDP, UNICEF, Jahon Banki):** To'lovlar 100% kafolatlangan, valyutada (AQSh dollarida). Hujjatlar ingliz tilida talab qilinadi.")
        render_lot_card_list("Xalqaro NNT & BMT")

    with sec_tab_b2b:
        st.info("💡 **Xususiy Sektor & Tijorat Banklari:** To'lovlar tez (5-15 kun), byurokratiyasiz va sifatga asoslangan.")
        render_lot_card_list("Xususiy sektor & B2B")

    with sec_tab_state:
        st.info("💡 **O'zbekiston Davlat Xaridlari:** O'RQ-684 qonuniga mos davlat buyurtmachilari tenderlari.")
        render_lot_card_list("Davlat sektori")

# ---------------------------------------------------------
# TAB 2: AI AUDIT & YASHIRIN TUZOQLAR (Deep Audit Workspace)
# ---------------------------------------------------------
with tab_audit:
    st.markdown("### 🔍 Tender Hujjatlari va Texnik Topshiriq Auditi")
    st.caption("AI Gemini 2.5 butun hujjatni chuqur tahlil qilib, yashirin tuzoqlar, noxolis talablar va g'oliblik narxini hisoblaydi.")

    tender_raw_text = ""

    if st.session_state.get("selected_lot_title"):
        st.info(f"📌 **Radardan tanlangan lot:** {st.session_state['selected_lot_title']}")

    c_inp1, c_inp2 = st.columns([2, 1])
    with c_inp1:
        input_choice = st.radio(
            "Tender manbasini tanlang:",
            ["📁 Hujjat yuklash (PDF / DOCX / TXT)", "✍️ Matn nusxasini qo'yish (Paste text)"],
            horizontal=True
        )

        if input_choice == "📁 Hujjat yuklash (PDF / DOCX / TXT)":
            uploaded_file = st.file_uploader("Texnik topshiriq yoki tender xarid hujjatini yuklang:", type=["pdf", "docx", "txt"])
            if uploaded_file is not None:
                with st.spinner("Hujjat o'qilmoqda..."):
                    parsed = DocumentParser.parse_document(uploaded_file.name, uploaded_file.read())
                    tender_raw_text = parsed["text"]
                    if parsed.get("is_scanned"):
                        st.warning("⚠️ **DIQQAT:** Yuklangan PDF skanerlangan (rasmli) formatda! AI Gemini Multimodal orqali rasmlar va jadvallarni to'g'ridan-to'g'ri tahlil qiladi.")
                        st.session_state["pdf_base64"] = parsed.get("pdf_base64", "")
                    else:
                        st.session_state["pdf_base64"] = ""
                        st.success(f"Fayl muvaffaqiyatli o'qildi: **{uploaded_file.name}** ({parsed['word_count']} so'z)")
        else:
            default_val = st.session_state.get("tender_text", "")
            tender_raw_text = st.text_area("Tender yoki lot matni:", value=default_val, height=180, placeholder="Texnik topshiriq matnini kiriting...")

    with c_inp2:
        with st.container(border=True):
            st.markdown("💡 **Namunaviy Sinov:**")
            st.caption("O'zbekistondagi haqiqiy IT davlat tenderi texnik topshirig'ini 1-clickda sinab ko'ring:")
            if st.button("🚀 Namunaviy IT Tenderini Yuklash", use_container_width=True):
                st.session_state["tender_text"] = SAMPLE_TENDER_TEXT
                st.session_state["pdf_base64"] = ""
                st.session_state["selected_lot_title"] = "LOT № 24110012398745 (Elektron Hukumat IT Tizimi)"
                tender_raw_text = SAMPLE_TENDER_TEXT
                st.rerun()

    if "tender_text" in st.session_state and not tender_raw_text:
        tender_raw_text = st.session_state["tender_text"]

    st.divider()

    # Trigger Audit Button
    col_run1, col_run2 = st.columns([2.5, 1])
    with col_run1:
        start_analysis = st.button("🔍 Ushbu Tenderni Chuqur Audit Qilish (AI Audit)", type="primary", use_container_width=True)

    auto_trigger = st.session_state.pop("trigger_auto_analysis", False)

    if start_analysis or auto_trigger:
        if not tender_raw_text.strip():
            st.warning("Iltimos, avval tender faylini yuklang yoki Radardan biror lotni tanlang!")
        else:
            # Credit validation
            credit_available = DatabaseManager.use_audit_credit(current_user["username"])
            if not credit_available:
                st.error("🚫 **Audit limitlaringiz tugadi!** Bepul tarifingizdagi barcha kreditlar sarflangan.")
                st.info("Yangi tenderlarni audit qilish va rasmiy Word hujjatlarini olish uchun '💎 5. Tariflar & Obuna' tabida qulay tarifni tanlang.")
            else:
                st.session_state["auth_user"] = DatabaseManager.get_user(current_user["username"])
                with st.status("🔍 AI audit va tahlil boshlanmoqda...", expanded=True) as status_box:
                    try:
                        st.write("📄 1/3: Texnik topshiriq va malaka talablari o'qilmoqda...")
                        time.sleep(0.3)
                        st.write("🚨 2/3: Yashirin tuzoqlar, penya, to'lov shartlari va qonuniy normalar tekshirilmoqda...")
                        pdf_b64 = st.session_state.get("pdf_base64", None)
                        analyzer = TenderAnalyzer()
                        analysis_results = analyzer.analyze_tender(tender_raw_text, company_profile, pdf_base64=pdf_b64)
                        st.write("⚖️ 3/3: Go / No-Go qarori va optimal narx strategiyasi shakllantirildi.")
                        st.session_state["analysis_results"] = analysis_results
                        st.session_state["current_tender_text"] = tender_raw_text
                        
                        DatabaseManager.log_audit(
                            current_user["username"],
                            analysis_results.get("tender_summary", {}),
                            analysis_results.get("match_evaluation", {})
                        )
                        status_box.update(label="✅ Tahlil muvaffaqiyatli yakunlandi!", state="complete", expanded=False)
                        st.success("Tahlil yakunlandi! Natijalar bilan quyida tanishing.")
                    except Exception as e:
                        status_box.update(label="❌ Tahlilda xatolik yuz berdi", state="error")
                        st.error(f"Xatolik: {str(e)}")

    # Render Audit Results if Available
    if "analysis_results" in st.session_state:
        data = st.session_state["analysis_results"]
        summary = data.get("tender_summary", {})
        match = data.get("match_evaluation", {})
        risks = data.get("risks_and_traps", [])
        qual = data.get("qualification_requirements", [])

        st.divider()
        st.markdown("### 📊 Asosiy Audit Ko'rsatkichlari")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Boshlang'ich Narx", value=summary.get("starting_price", "Noma'lum"))
        with m2:
            st.metric(label="Ijro Muddati", value=summary.get("deadline_execution", "Noma'lum"))
        with m3:
            st.metric(label="Kompaniya Moslik Bali", value=f"{match.get('match_score', 0)}%")
        with m4:
            verdict = match.get("verdict", "")
            if "GO" in verdict and "CAUTION" not in verdict:
                st.success(f"Qaror: {verdict}")
            elif "CAUTION" in verdict:
                st.warning(f"Qaror: {verdict}")
            else:
                st.error(f"Qaror: {verdict}")

        # Optimal Pricing Recommendation Card
        pricing = data.get("pricing_strategy", {})
        if pricing:
            with st.container(border=True):
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 1.05rem; font-weight: 700; color: #166534;">💰 G'oliblik Ehtimolini Oshiruvchi Narx Strategiyasi</span>
                    <span style="background-color: #DCFCE7; color: #15803D; font-weight: 700; padding: 2px 10px; border-radius: 12px; font-size: 0.85rem;">
                        Tavsiya chegirma: {pricing.get('recommended_discount_percent', '3-7%')}
                    </span>
                </div>
                <div style="margin: 8px 0;">
                    <span style="color: #4B5563; font-size: 0.88rem;">Tavsiya etilayotgan taklif summasi:</span>
                    <strong style="color: #15803D; font-size: 1.15rem; margin-left: 8px;">{pricing.get('target_bid_amount', 'Hisoblanmagan')}</strong>
                </div>
                <p style="margin: 0; font-size: 0.9rem; color: #374151;"><strong>Mantiqiy asos:</strong> {pricing.get('pricing_rationale', '')}</p>
                """, unsafe_allow_html=True)

        # Sub-tabs for detailed audit review
        sub_pass, sub_risks, sub_qual = st.tabs([
            "📋 Tender Pasporti & Talablar",
            "🚨 Yashirin Xavflar va Tuzoqlar",
            "🎯 Malaka Talablari Auditi"
        ])

        with sub_pass:
            p_c1, p_c2 = st.columns(2)
            with p_c1:
                st.write(f"**Lot raqami:** {summary.get('lot_number')}")
                st.write(f"**Mavzu:** {summary.get('title')}")
                st.write(f"**Buyurtmachi:** {summary.get('customer')}")
            with p_c2:
                st.write(f"**Topshirish muddati:** {summary.get('submission_deadline', 'Noma\'lum')}")
                st.write(f"**Zaklad ta'minoti:** {summary.get('guarantee_deposit', 'Talab qilinmagan')}")
                curr_link = st.session_state.get("current_tender_link", "")
                if curr_link:
                    st.markdown(f"[Portaldagi rasmiy lot sahifasini ochish ↗]({curr_link})")

        with sub_risks:
            st.write("Quyida shartnomadagi potentsial jarimalar, diskvalifikatsiya xavflari va noxolis talablar ko'rsatilgan:")
            for r in risks:
                r_type = r.get("type", "warning")
                css_cls = "risk-red" if r_type == "danger" else ("risk-yellow" if r_type == "warning" else "risk-green")
                icon = "🚨" if r_type == "danger" else ("⚠️" if r_type == "warning" else "✅")
                
                st.markdown(f"""
                <div class="{css_cls}">
                    <div style="font-weight: 700; color: #1E293B; font-size: 0.95rem; margin-bottom: 4px;">
                        {icon} {r.get('title')}
                    </div>
                    <div style="font-size: 0.9rem; color: #475569; margin-bottom: 6px;">
                        {r.get('description')}
                    </div>
                    <div style="font-size: 0.85rem; color: #1D4ED8; font-weight: 600;">
                        💡 Tavsiya: {r.get('recommendation')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with sub_qual:
            for q in qual:
                status_icon = "✅" if q.get("status") == "met" else ("⚠️" if q.get("status") == "partial" else "❌")
                with st.container(border=True):
                    st.markdown(f"**{status_icon} {q.get('category')}:** {q.get('requirement')}")
                    st.caption(f"Ishtirokchi holati: {q.get('our_match')}")

# ---------------------------------------------------------
# TAB 3: RASMIY TAKLIFLAR & WORD (.DOCX) GENERATORI
# ---------------------------------------------------------
with tab_docs:
    st.markdown("### 📝 Rasmiy Hujjatlar va Microsoft Word (.docx) Generatori")
    st.caption("O'zbekiston davlat standartlariga mos rasmiy korxona blankasi, talablar solishtirma jadvali va imzo bloklari bilan tayyor Word hujjatlari.")

    if "analysis_results" not in st.session_state:
        st.info("ℹ️ Rasmiy takliflarni shakllantirish uchun avval **'🔍 2. AI Audit & Tuzoqlar'** tabida biror tenderni tahlil qiling.")
    else:
        data = st.session_state["analysis_results"]
        summary = data.get("tender_summary", {})
        lot_tag = str(summary.get('lot_number', 'Lot')).replace('/', '_').replace(' ', '_')

        c_l1, c_l2 = st.columns([1.5, 1])
        with c_l1:
            doc_lang_choice = st.radio(
                "🌐 Taklif tili (Proposal Language):",
                ["🇺🇿 O'zbek tili (Davlat & Mahalliy B2B)", "🇷🇺 Rus tili (Davlat & Korporativ)", "🇬🇧 English (UN / International NGO / World Bank)"],
                horizontal=True
            )
            lang_code = "en" if "English" in doc_lang_choice else ("ru" if "Rus" in doc_lang_choice else "uz")
        with c_l2:
            st.caption("Xalqaro NNT (BMT, UNICEF) uchun **Ingliz tili**, mahalliy davlat tenderlari uchun **O'zbek** yoki **Rus tili** tavsiya etiladi.")

        if st.button("🚀 Barcha Rasmiy Hujjatlarni Generatsiya Qilish (Word .docx)", type="primary", use_container_width=True):
            with st.spinner(f"Microsoft Word (.docx) va matnli takliflar tayyorlanmoqda ({doc_lang_choice})..."):
                gen = ProposalGenerator()
                tech_prop = gen.generate_technical_proposal(data, company_profile, language=lang_code)
                guarantee_let = gen.generate_guarantee_letter(data, company_profile, language=lang_code)
                checklist_table = gen.generate_compliance_checklist(data, company_profile, language=lang_code)

                docx_tech = DocxExporter.create_technical_proposal_docx(
                    tender_summary=summary,
                    proposal_text=tech_prop,
                    company_profile=company_profile,
                    qualifications=data.get("qualification_requirements", []),
                    language=lang_code
                )
                docx_guarantee = DocxExporter.create_guarantee_letter_docx(
                    tender_summary=summary,
                    guarantee_text=guarantee_let,
                    company_profile=company_profile,
                    language=lang_code
                )
                docx_checklist = DocxExporter.create_checklist_docx(
                    tender_summary=summary,
                    company_profile=company_profile,
                    language=lang_code
                )

                st.session_state["tech_proposal"] = tech_prop
                st.session_state["guarantee_letter"] = guarantee_let
                st.session_state["doc_checklist"] = checklist_table
                st.session_state["docx_tech"] = docx_tech
                st.session_state["docx_guarantee"] = docx_guarantee
                st.session_state["docx_checklist"] = docx_checklist
                st.success("✅ Barcha hujjatlar va Microsoft Word (.docx) fayllari muvaffaqiyatli tayyorlandi!")

        if "tech_proposal" in st.session_state:
            d_tab1, d_tab2, d_tab3 = st.tabs(["📄 Texnik Taklif", "🛡 Kafolat Xati", "📑 Hujjatlar Cheklisti"])
            
            with d_tab1:
                c_d1, c_d2 = st.columns([1, 1])
                with c_d1:
                    if "docx_tech" in st.session_state:
                        st.download_button(
                            label="📥 Texnik Taklifni Yuklab Olish (.DOCX Word)",
                            data=st.session_state["docx_tech"],
                            file_name=f"Texnik_Taklif_{lot_tag}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                            use_container_width=True
                        )
                with c_d2:
                    st.download_button(
                        label="💾 Markdown nusxasi (.MD)",
                        data=st.session_state["tech_proposal"],
                        file_name=f"Texnik_Taklif_{lot_tag}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                st.divider()
                st.markdown(st.session_state["tech_proposal"])

            with d_tab2:
                c_g1, c_g2 = st.columns([1, 1])
                with c_g1:
                    if "docx_guarantee" in st.session_state:
                        st.download_button(
                            label="📥 Kafolat Xatini Yuklab Olish (.DOCX Word)",
                            data=st.session_state["docx_guarantee"],
                            file_name=f"Kafolat_Xati_{lot_tag}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                            use_container_width=True
                        )
                with c_g2:
                    st.download_button(
                        label="💾 Markdown nusxasi (.MD)",
                        data=st.session_state["guarantee_letter"],
                        file_name=f"Kafolat_Xati_{lot_tag}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                st.divider()
                st.markdown(st.session_state["guarantee_letter"])

            with d_tab3:
                if "docx_checklist" in st.session_state:
                    st.download_button(
                        label="📥 Hujjatlar Cheklistini Yuklab Olish (.DOCX Word)",
                        data=st.session_state["docx_checklist"],
                        file_name=f"Hujjatlar_Cheklisti_{lot_tag}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary"
                    )
                st.divider()
                st.markdown(st.session_state["doc_checklist"])

# ---------------------------------------------------------
# TAB 4: 24/7 TELEGRAM ALERT BOT (Real-Time Background Daemon)
# ---------------------------------------------------------
with tab_telegram:
    st.markdown("### 🔔 24/7 Real-Time Telegram Alert Bot")
    st.caption("UzEx va boshqa portallarda yangi mos tender e'lon qilingan zahoti Telegram guruhingizga 1-2 daqiqada xabar yetkazish:")

    import os
    tg_col1, tg_col2 = st.columns(2)
    with tg_col1:
        tg_token_val = st.text_input("Telegram Bot Token", value=os.getenv("TELEGRAM_BOT_TOKEN", ""), type="password", placeholder="123456:ABC-DEF...")
        tg_min_score_val = st.slider("Minimal moslik darajasi (%)", min_value=50, max_value=90, value=65, step=5)
    with tg_col2:
        tg_chat_val = st.text_input("Telegram Chat / Kanal ID", value=os.getenv("TELEGRAM_CHAT_ID", ""), placeholder="-100123456789 yoki @chat_id")
        tg_kw_val = st.text_input("Filtrlovchi kalit so'z (ixtiyoriy)", placeholder="AI, CRM, kiberxavfsizlik...")

    daemon_status = TelegramAlertDaemon.get_status()
    is_running = daemon_status.get("is_running", False)

    # Telemetry Status Card
    if is_running:
        st.success(f"🟢 **Bot Faol:** Har 90 soniyada portallar tekshirilmoqda. Oxirgi tekshiruv: {daemon_status.get('last_poll_time') or 'Hozirgina'} | Ko'rilgan: {daemon_status.get('total_checked', 0)} | Yuborilgan: {daemon_status.get('total_alerts_sent', 0)}")
    else:
        st.info("⚪️ **Holati:** Bot to'xtatilgan.")

    t_b1, t_b2 = st.columns(2)
    with t_b1:
        if st.button("🧪 Test Xabar Yuborish", use_container_width=True):
            if not tg_token_val or not tg_chat_val:
                st.warning("Iltimos, Bot Token va Chat ID ni kiriting!")
            else:
                with st.spinner("Telegramga test yuborilmoqda..."):
                    t_res = TenderNotifier.send_test_telegram(tg_token_val, tg_chat_val)
                    if t_res.get("success"):
                        st.success("✅ Test xabari Telegram'ga muvaffaqiyatli bordi!")
                    else:
                        st.error(f"Xatolik: {t_res.get('error')}")

    with t_b2:
        if not is_running:
            if st.button("▶️ Botni Ishga Tushirish", type="primary", use_container_width=True):
                if not tg_token_val or not tg_chat_val:
                    st.warning("Token va Chat ID kiriting!")
                else:
                    TelegramAlertDaemon.start_daemon(
                        interval_seconds=90,
                        min_match_score=tg_min_score_val,
                        keyword_filter=tg_kw_val,
                        company_profile=company_profile,
                        bot_token=tg_token_val,
                        chat_id=tg_chat_val
                    )
                    st.success("🟢 Bot ishga tushirildi!")
                    st.rerun()
        else:
            if st.button("⏹ Botni To'xtatish", use_container_width=True):
                TelegramAlertDaemon.stop_daemon()
                st.info("⚪️ Bot to'xtatildi.")
                st.rerun()

# ---------------------------------------------------------
# TAB 5: TARIFLAR & OBUNA (Dedicated Pricing Page)
# ---------------------------------------------------------
with tab_pricing:
    render_pricing_page()

# ---------------------------------------------------------
# TAB 6: QO'LLANMA & YECHIMLAR (Product Overview & Guide)
# ---------------------------------------------------------
with tab_guide:
    render_guide_page()

# Footer: Official Legal Disclaimer & Terms of Service across all tabs
render_footer()
