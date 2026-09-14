import streamlit as st

def render_pricing_page():
    """Renders a clean, robust, modern B2B SaaS pricing page for Uzbekistan companies."""
    
    st.markdown("## 💎 Shaffof va Qulay B2B Tariflar")
    st.caption("O'zbekiston davlat xaridlari, Xalqaro NNT/BMT grantlari va Xususiy B2B tenderlarida g'olib bo'ling, yashirin xatarlardan himoyalaning.")

    # Billing Toggle
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        billing_mode = st.radio(
            "To'lov davrini tanlang:",
            ["🗓 Oylik To'lov", "🎁 Yillik To'lov (20% Chegirma bilan)"],
            horizontal=True
        )
    is_annual = "Yillik" in billing_mode

    p_starter = "312,000 UZS/oy" if is_annual else "390,000 UZS/oy"
    p_pro = "792,000 UZS/oy" if is_annual else "990,000 UZS/oy"
    p_ent = "2,320,000 UZS/oy" if is_annual else "2,900,000 UZS/oy"

    # 4 Pricing Cards using native Streamlit columns and containers
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        with st.container(border=True):
            st.markdown("### ⭐ Bepul")
            st.caption("Tizimni sinab ko'rish uchun")
            st.markdown("## 0 UZS")
            st.divider()
            st.markdown("""
            - **3 ta** to'liq AI audit
            - Barcha 3 ta sektor qidiruvi
            - Go / No-Go asosiy xulosasi
            - Namunaviy test tenderlari
            """)
            st.button("Hozir Sinash (Faol)", disabled=True, use_container_width=True, key="p_btn_free")

    with c2:
        with st.container(border=True):
            st.markdown("### 🚀 Starter")
            st.caption("Kichik korxonalar uchun")
            st.markdown(f"## {p_starter}")
            st.divider()
            st.markdown("""
            - **30 ta** oylik to'liq audit
            - **Word (.docx)** eksport
            - Rasmiy Texnik taklif & Kafolat xati
            - Optimal narx tavsiyasi
            - E-mail xabarnomalari
            """)
            st.link_button("Starter'ni Tanlash", "https://t.me/GPTify_uz_bot", use_container_width=True)

    with c3:
        with st.container(border=True):
            st.markdown("### 👑 Pro")
            st.caption("🔥 **Eng ommabop / Tavsiya**")
            st.markdown(f"## :blue[{p_pro}]")
            st.divider()
            st.markdown("""
            - **100 ta** oylik chuqur audit
            - **24/7 Real-Time Telegram Bot**
            - **Skanerlangan PDF OCR** (Gemini)
            - **Xalqaro NNT & Xususiy B2B** qamrovi
            - **O'zbek, Rus va Ingliz** tilida takliflar
            - Yashirin tuzoqlar & penya filtri
            - To'liq Word (.docx) paketlari
            """)
            st.link_button("👑 Pro'ni Faollashtirish", "https://t.me/GPTify_uz_bot", type="primary", use_container_width=True)

    with c4:
        with st.container(border=True):
            st.markdown("### 🏢 Enterprise")
            st.caption("Yirik korporatsiyalar & Xalqaro")
            st.markdown(f"## {p_ent}")
            st.divider()
            st.markdown("""
            - **Cheksiz** oylik auditlar
            - **BMT (UNGM), USAID & Banklar**
            - **Xalqaro Inglizcha RFP** generatsiyasi
            - **1C & Didox REST API** integratsiyasi
            - Jamoaviy kirish (5+ xodim)
            - Didox elektron hisob-faktura
            - Shaxsiy kurator & SLA
            """)
            st.link_button("Shartnoma Tuzish", "https://t.me/GPTify_uz_bot", use_container_width=True)

    # Interactive ROI Calculator using 100% Native Streamlit Metrics
    st.divider()
    st.subheader("🧮 Foyda va Investitsiya Qaytishi (ROI) Kalkulyatori")
    st.caption("TenderPro AI kompaniyangizni bitta tenderda diskvalifikatsiya yoki jarimalardan saqlab qolish hisobiga qanday o'zini oqlashini hisoblang:")

    r_col1, r_col2 = st.columns([1.3, 1])
    with r_col1:
        tender_val = st.slider(
            "💰 Kompaniyangiz qatnashadigan o'rtacha tender/lot summasi (mln so'm):",
            min_value=50,
            max_value=3000,
            value=650,
            step=50,
            key="roi_calc_slider"
        )
        zaklad_val = round(tender_val * 0.03, 1)
        penya_saved = round(tender_val * 0.05, 1)
        roi_times = int(round((tender_val * 1_000_000) / 990_000, 0))

    with r_col2:
        with st.container(border=True):
            m_c1, m_c2 = st.columns(2)
            with m_c1:
                st.metric(label="3% Zaklad Kafolati", value=f"{zaklad_val} mln so'm", help="Noto'g'ri topshirish oqibatida muzlash xavfi")
            with m_c2:
                st.metric(label="Penya va Xatarlardan Himoya", value=f"~{penya_saved} mln so'm")
            st.metric(label="📈 Pro Tarifining O'zini Oqlashi (ROI)", value=f"{roi_times} barobar!", delta="Tender qiymatiga nisbatan")

    # Feature Comparison Table
    st.divider()
    st.subheader("📊 Tariflarning Solishtirma Jadvali")
    st.markdown("""
    | Imkoniyat va Xususiyat | ⭐ Bepul | 🚀 Starter | 👑 Pro (Tavsiya) | 🏢 Enterprise |
    | :--- | :---: | :---: | :---: | :---: |
    | **Oylik To'liq Auditlar** | 3 ta | 30 ta | 100 ta | **Cheksiz** |
    | **Davlat Sektori (UzEx, Mc, Coop)** | ✅ | ✅ | ✅ | ✅ |
    | **Xalqaro NNT & BMT (UNGM, World Bank)** | Asosiy | Cheklangan | **✅ To'liq** | **✅ Cheksiz** |
    | **Xususiy B2B & Banklar (Ipak Yo'li, Telekom)** | Asosiy | Cheklangan | **✅ To'liq** | **✅ Cheksiz** |
    | **Taklif Tili (RFP Languages)** | Faqat O'zbek | O'zbek, Rus | **O'zbek, Rus, Ingliz** | **O'zbek, Rus, Ingliz** |
    | **Microsoft Word (.docx) Eksport** | ❌ | ✅ | ✅ | ✅ |
    | **24/7 Real-Time Telegram Alert Bot** | ❌ | ❌ | **✅ (Faol)** | **✅ (Maxsus)** |
    | **Skanerlangan PDF OCR (Gemini Multimodal)** | ❌ | Oddiy | **✅ Chuqur** | **✅ Kengaytirilgan** |
    | **Yashirin Tuzoqlar & Penya Detektori** | Asosiy | ✅ | ✅ | ✅ |
    | **Optimal Narx Strategiyasi Kalkulyatori** | ❌ | ✅ | ✅ | ✅ |
    | **Didox / 1C REST API Integratsiyasi** | ❌ | ❌ | ❌ | **✅ Mavjud** |
    | **Jamoaviy Kirish (Xodimlar soni)** | 1 | 1 | 3 tagacha | **5+ xodim** |
    | **Didox orqali Elektron Hisob-Faktura** | ❌ | ❌ | ✅ | ✅ |
    """)

    # FAQ Section
    st.divider()
    st.subheader("❓ Ko'p Beriladigan Savollar (FAQ)")

    with st.expander("🌍 Xalqaro NNT va BMT (UNGM) tenderlari qanday ishlaydi?"):
        st.write("""
        BMT (UNDP, UNICEF), Jahon Banki va xalqaro nodavlat fondlar O'zbekistondagi loyihalari uchun tenderlarni AQSh dollarida va qat'iy xalqaro standartlar asosida o'tkazadi.
        TenderPro AI ushbu lotlarni avtomatik aniqlaydi va xalqaro mezonlarga mos **ingliz tilidagi professional RFP taklifini** Word formatida shakllantiradi.
        """)

    with st.expander("🏢 Xususiy sektor va tijorat banklari xaridlari qamrab olinganmi?"):
        st.write("""
        Ha. Ipak Yo'li Banki, Kapitalbank, NBU, Beeline (Unitel), Korzinka va boshqa yirik xususiy korporatsiyalarning B2B xarid tanlovlari tizimimizga kiritilgan.
        Ular to'lovni tez va ishonchli amalga oshirishi bilan davlat xaridlaridan afzal hisoblanadi.
        """)

    with st.expander("💳 Didox orqali elektron hisob-faktura taqdim etiladimi?"):
        st.write("""
        Ha, albatta. Biz O'zbekistondagi barcha yuridik shaxslar (MCHJ, XK, AJ) uchun rasmiy ikki tomonlama shartnoma tuzamiz 
        va Didox yoki Soliq.uz orqali elektron hisob-faktura taqdim etamiz. To'lov 100% bank o'tkazmasi orqali qabul qilinadi.
        """)

    with st.expander("🔔 Real-Time Telegram bot yangi tenderlarni qanday topadi?"):
        st.write("""
        TenderPro AI orqa fonda UzEx jonli Oracle API va xalqaro manbalarni har 60-90 soniyada so'rov qiladi. 
        Yangi chiqqan lot bazada yo'qligi tekshirilib, kompaniyangiz profiliga mos kelgan zahoti 1-2 daqiqada Telegram guruhingizga to'g'ridan-to'g'ri havolasi bilan yetkaziladi.
        """)


def render_guide_page():
    """Renders an intuitive, clean product overview and feature guide."""

    st.markdown("## 🚀 TenderPro AI Imkoniyatlari va Qo'llanma")
    st.caption("O'zbekistonda davlat, xalqaro NNT/BMT va xususiy B2B xaridlarida ishtirok etuvchi kompaniyalar uchun intellektual yechim.")

    # 4 Pillars of Value
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        st.metric(label="Tayyorgarlik Tezligi", value="10x Tezroq", delta="2 kundan 5 daqiqaga")
    with v2:
        st.metric(label="Tuzoqlar Foshi", value="100% Audit", delta="Penya, avans, noxolis brendlar")
    with v3:
        st.metric(label="3 Katta Sektor", value="Davlat • NNT • B2B", delta="UzEx, UNGM, Banklar")
    with v4:
        st.metric(label="3 Tilda Takliflar", value="Word (.docx)", delta="O'zbek, Rus, Ingliz")

    st.divider()

    # 3 Sectors Breakdown
    st.subheader("🌐 3 Katta Xarid Sektori Qamrovi")
    s1, s2, s3 = st.columns(3)
    with s1:
        with st.container(border=True):
            st.markdown("#### 🏛 1. Davlat Xaridlari (State)")
            st.write("`etender.uzex.uz`, `xarid.uzex.uz`, `tender.mc.uz`, `cooperation.uz`.")
            st.caption("O'RQ-684 qonuniga mos: Byudjet tashkilotlari va davlat ulushi bor korxonalar tanlovlari.")
    with s2:
        with st.container(border=True):
            st.markdown("#### 💎 2. Xalqaro NNT & BMT (NGO & UN)")
            st.write("`ungm.org` (UNDP, UNICEF), Jahon Banki, USAID, Zamin Fondi.")
            st.caption("Kafolatlangan xalqaro to'lovlar, valyuta shartnomalari, qat'iy inglizcha RFP standartlari.")
    with s3:
        with st.container(border=True):
            st.markdown("#### 🏢 3. Xususiy Sektor & Banklar (B2B)")
            st.write("Tijorat banklari (Ipak Yo'li, Kapitalbank), Telekom (Beeline), Retail (Korzinka, Artel).")
            st.caption("Damping yo'q, sifat muhim, tez to'lov muddati (5-15 kun ichida).")

    st.divider()

    # Problems & Solutions Cards
    st.subheader("🎯 Tender Ishtirokchilarining 3 Katta Muammosi va Yechimi")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        with st.container(border=True):
            st.markdown("#### ❌ 1. Vaqt yetishmasligi")
            st.write("50-100 sahifalik murakkab texnik topshiriqlarni puxta o'qishga mutaxassislarning vaqti yetmaydi, muhim talablar qolib ketadi.")
            st.success("✅ **AI Yechim:** Gemini 2.5 butun matnni 10 soniyada o'qib, barcha malaka talablarini ajratib beradi.")

    with col_p2:
        with st.container(border=True):
            st.markdown("#### ❌ 2. Yashirin tuzoqlar va penya")
            st.write("Buyurtmachilar o'z tanishlariga moslab yashirin brend talablari, 0% avans va 90 kunlik to'lov kechikishlarini qo'shadi.")
            st.success("✅ **AI Yechim:** Xavflar filtri barcha shubhali bandlarni qizil va sariq bilan fosh qilib, xabardor qiladi.")

    with col_p3:
        with st.container(border=True):
            st.markdown("#### ❌ 3. Noto'g'ri narx strategiyasi")
            st.write("Qaysi narxni qo'yishni bilmay, juda qimmat taklif berib yutqazasiz yoki juda arzon narx qo'yib zararga ishlaysiz.")
            st.success("✅ **AI Yechim:** Tizim QQS (12%) va 3% zakladni hisoblab, yutish ehtimoli eng yuqori bo'lgan optimal narxni beradi.")


def render_footer():
    """Renders the official Legal Disclaimer & Terms of Service footer."""
    st.divider()
    st.markdown("""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px 20px; font-size: 0.84rem; color: #475569; line-height: 1.5;">
        <div style="font-weight: 700; color: #1E293B; font-size: 0.92rem; margin-bottom: 6px;">
            ⚖️ Yuridik Ogohlantirish & Ommaviy Oferta (Legal Disclaimer & Terms of Use)
        </div>
        <p style="margin-bottom: 6px;">
            <strong>1. Xizmatning maqomi:</strong> "TenderPro AI" davlat, xalqaro nodavlat (NNT/BMT) va korporativ xaridlar ishtirokchilari uchun axborot-tahliliy vosita hisoblanadi. Mazkur tizim davlat xaridlari organi yoki tender komissiyasi hisoblanmaydi.
        </p>
        <p style="margin-bottom: 6px;">
            <strong>2. Tahlillar xarakteri:</strong> Sun'iy intellekt tomonidan berilgan tahlillar, xavflar va generatsiya qilingan hujjat loyihalari tavsiyaviy xarakterga ega bo'lib, tenderda qatnashish va taklif yuborish bo'yicha yakuniy javobgarlik ishtirokchi zimmasida.
        </p>
        <p style="margin: 0;">
            <strong>3. Qonuniylik:</strong> Barcha jarayonlar O'zbekiston Respublikasining "Davlat xaridlari to'g'risida"gi Qonuni (O'RQ-684) hamda xalqaro xarid standartlariga muvofiq olib boriladi.
        </p>
        <div style="border-top: 1px solid #CBD5E1; margin-top: 10px; padding-top: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                © 2026 <strong>GPTify (GPTify.co)</strong> — B2B AI ish oqimlari va tizimlari konsaltingi. <strong>GPTify Uzbekistan Jamoasi</strong> tomonidan ishlab chiqilgan.
            </div>
            <div>
                Aloqa: <a href="https://t.me/GPTify_uz_bot" target="_blank" style="color: #2563EB; text-decoration: none; font-weight: 600;">@GPTify_uz_bot</a> | contact@gptify.co
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
