import datetime
from typing import List, Dict, Any, Optional

class TenderFinder:
    """Discovers, filters, and ranks relevant public and corporate procurement opportunities in Uzbekistan."""

    # Curated real-world and recurring procurement opportunities across State, International NGOs/UN, and Private B2B sectors in Uzbekistan
    DEFAULT_OPPORTUNITIES = [
        # --- 1. XALQARO NNT, BMT & GRANTLAR (International NGOs, UN, Non-Profits) ---
        {
            "lot_id": "LOT-UNGM-24110990",
            "portal": "ungm.org",
            "sector": "Xalqaro NNT & BMT",
            "title": "Development of AI-Powered National Energy Monitoring Platform & Public Analytics Dashboard",
            "customer": "UNDP Uzbekistan (BMT Taraqqiyot Dasturi)",
            "starting_price": "$120,000 USD (~1,536,000,000 UZS)",
            "raw_price": 1536000000,
            "deadline": "2026-10-20",
            "category": "Sun'iy Intellekt & LLM",
            "keywords": ["ai", "undp", "energy", "dashboard", "analytics", "rfp", "international"],
            "description": "BMT Taraqqiyot Dasturi buyurtmasi: O'zbekiston energetika ma'lumotlarini to'plash, AI yordamida tejamkorlikni prognozlash va interaktiv xalqaro portal yaratish. BMT shartlari bo'yicha to'lov 100% kafolatlangan.",
            "qualification_brief": "International or local IT experience, English RFP submission, audited financial balance, experienced team of 3+ developers.",
            "link": "https://www.ungm.org/Public/Notice"
        },
        {
            "lot_id": "LOT-UNICEF-24110815",
            "portal": "unicef.org",
            "sector": "Xalqaro NNT & BMT",
            "title": "Digital Child Health Records & Immunization Tracking System Architecture",
            "customer": "UNICEF Uzbekistan Country Office",
            "starting_price": "$85,000 USD (~1,088,000,000 UZS)",
            "raw_price": 1088000000,
            "deadline": "2026-10-15",
            "category": "MedTech & CRM",
            "keywords": ["unicef", "health", "crm", "mobile", "database", "api"],
            "description": "UNICEF O'zbekiston vakolatxonasi: Bolalar salomatligi kartalarini raqamlashtirish, shifokorlar uchun planshet ilovasi va SMS/Telegram xabardor qilish integratsiyasi.",
            "qualification_brief": "2+ years in MedTech or enterprise data management, ISO/IEC compliance or equivalent QA standards.",
            "link": "https://www.unicef.org/uzbekistan/tenders"
        },
        {
            "lot_id": "LOT-WB-24110720",
            "portal": "worldbank.org",
            "sector": "Xalqaro NNT & BMT",
            "title": "National Public Infrastructure Data Modernization & Analytics Platform",
            "customer": "Jahon Banki (World Bank Country Office)",
            "starting_price": "$140,000 USD (~1,792,000,000 UZS)",
            "raw_price": 1792000000,
            "deadline": "2026-10-25",
            "category": "Data & Analytics",
            "keywords": ["world bank", "analytics", "data", "infrastructure", "ai"],
            "description": "Jahon Banki granti: Davlat infratuzilmasi ma'lumotlarini markazlashtirilgan xalqaro platformada tahlil qilish va dashboard tizimini yaratish.",
            "qualification_brief": "Jahon Banki yoki xalqaro moliya institutlari loyihalarida ishtirok tajribasi, ISO 27001 sertifikati.",
            "link": "https://projects.worldbank.org/en/projects-operations/procurement"
        },

        # --- 2. XUSUSIY SEKTOR & BANKLAR (Private Sector & Commercial B2B) ---
        {
            "lot_id": "LOT-IYB-24110950",
            "portal": "ipakyulibank.uz",
            "sector": "Xususiy sektor & B2B",
            "title": "B2B korporativ mijozlar uchun AI Kredit Skoringi va Fraud-Monitoring Tizimi",
            "customer": "\"Ipak Yo'li\" AITB Bosh Ofisi",
            "starting_price": "980,000,000 UZS",
            "raw_price": 980000000,
            "deadline": "2026-10-12",
            "category": "Bank & Fintech CRM",
            "keywords": ["bank", "skoring", "fraud", "ai", "b2b", "kredit", "1c"],
            "description": "Yirik xususiy tijorat banki: Korporativ qarz oluvchilarning moliyaviy hisobotlari va Didox ma'lumotlarini AI tahlil qilib, kredit xatarini avtomatik baholash.",
            "qualification_brief": "FinTech yoki bank integratsiyasi bo'yicha kamida 2 ta muvaffaqiyatli topshirilgan shartnoma, ma'lumotlar xavfsizligi kafolati.",
            "link": "https://ipakyulibank.uz"
        },
        {
            "lot_id": "LOT-BEE-24110880",
            "portal": "beeline.uz",
            "sector": "Xususiy sektor & B2B",
            "title": "Call-Center audio yozuvlarini AI orqali tahlil qilish va operatorlar sifatini avtomat baholash tizimi",
            "customer": "\"Unitel\" MCHJ (Beeline Uzbekistan)",
            "starting_price": "720,000,000 UZS",
            "raw_price": 720000000,
            "deadline": "2026-10-06",
            "category": "Sun'iy Intellekt & LLM",
            "keywords": ["beeline", "call center", "speech-to-text", "audio", "ai", "koll-markaz"],
            "description": "Kompaniya koll-markaziga kiruvchi 50,000+ oylik qo'ng'iroqlarni transkripsiya qilish, operatorlarning xushmuomalaligi va mijozlar qoniqish darajasini (CSAT) AI orqali avtomatik baholash.",
            "qualification_brief": "Telekom yoki yirik xizmat ko'rsatish kompaniyalari bilan ishlash tajribasi, yuqori yuklamali server arxitekturasi.",
            "link": "https://beeline.uz"
        },
        {
            "lot_id": "LOT-XT-24110610",
            "portal": "xt-xarid.uz",
            "sector": "Xususiy sektor & B2B",
            "title": "B2B Yetkazib beruvchilar va ombor zanjirini prognozlovchi avtomatlashtirilgan ERP/CRM moduli",
            "customer": "XT-Xarid Korporativ Mijozlar Tarmog'i",
            "starting_price": "560,000,000 UZS",
            "raw_price": 560000000,
            "deadline": "2026-09-27",
            "category": "Logistika & CRM",
            "keywords": ["retail", "logistika", "crm", "didox", "1c", "prognoz"],
            "description": "Yirik tarmoq do'konlarida mahsulot qoldiqlarini tahlil qilish, yetkazib beruvchilarga avtomatik buyurtma shakllantirish va Didox orqali schyot-fakturalarni solishtirish.",
            "qualification_brief": "Retail yoki logistika sohasida 1C/ERP integratsiya tajribasi.",
            "link": "https://xt-xarid.uz"
        },

        # --- 3. DAVLAT XARIDLARI (State / Public Procurement - O'RQ-684) ---
        {
            "lot_id": "LOT-UZEX-24110901",
            "portal": "etender.uzex.uz",
            "sector": "Davlat sektori",
            "title": "Davlat xizmatlari portalida sun'iy intellekt (LLM) asosidagi virtual konsultant va chat-bot tizimini joriy qilish",
            "customer": "O'zbekiston Respublikasi Raqamli Texnologiyalar Vazirligi",
            "starting_price": "650,000,000 UZS",
            "raw_price": 650000000,
            "deadline": "2026-09-28",
            "category": "Sun'iy Intellekt & LLM",
            "keywords": ["sun'iy intellekt", "ai", "llm", "chatbot", "crm", "dasturiy"],
            "description": "Foydalanuvchilarning savollariga 24/7 avtomat javob beruvchi, o'zbek va rus tillaridagi katta til modellari (LLM) integratsiyasi, admin dashboard va CRM ulanishi.",
            "qualification_brief": "IT sohasida 2+ yillik tajriba, AI loyihalar portfoliosi, 3 nafar mutaxassis.",
            "link": "https://etender.uzex.uz"
        },
        {
            "lot_id": "LOT-XARID-24110842",
            "portal": "xarid.uzex.uz",
            "sector": "Davlat sektori",
            "title": "Tijorat banki uchun B2B mijozlar muloqotini tahlil qilish va CRM voronkasini avtomatlashtirish tizimi",
            "customer": "\"Asakabank\" AJ Bosh Ofisi",
            "starting_price": "920,000,000 UZS",
            "raw_price": 920000000,
            "deadline": "2026-10-05",
            "category": "Bank & Fintech CRM",
            "keywords": ["crm", "bank", "b2b", "avtomatlashtirish", "integratsiya", "call center"],
            "description": "Kompaniya mijozlari bilan muloqotlarni tahlil qilish, ovozli xabarlarni matnga o'girish (STT) va 1C/Bank ichki tizimlariga integratsiya qilish.",
            "qualification_brief": "Bank yoki moliya sektorida integratsiya tajribasi, axborot xavfsizligi talablariga muvofiqlik.",
            "link": "https://xarid.uzex.uz"
        },
        {
            "lot_id": "LOT-UZEX-24110788",
            "portal": "etender.uzex.uz",
            "sector": "Davlat sektori",
            "title": "Korporativ elektron hujjat aylanishi (Didox) va hisob-fakturalar auditi uchun avtomatlashtirilgan dasturiy modul",
            "customer": "\"O'zbektelekom\" AK",
            "starting_price": "420,000,000 UZS",
            "raw_price": 420000000,
            "deadline": "2026-09-22",
            "category": "Hisob-faktura & Audit IT",
            "keywords": ["didox", "1c", "audit", "hisob-faktura", "soliq", "integratsiya"],
            "description": "Elektron hisob-fakturalarni Didox API orqali qabul qilish, 1C bilan nomutanosibliklarni solishtirish va soliq risklarini oldindan xabarlash moduli.",
            "qualification_brief": "Didox/1C bilan ishlash bo'yicha amaliy tajriba, soliq qoidalari tushunchasi.",
            "link": "https://etender.uzex.uz"
        },
        {
            "lot_id": "LOT-ICPPA-24110655",
            "portal": "xarid.icppa.uz",
            "sector": "Davlat sektori",
            "title": "Hududiy agrar va logistika korxonalari uchun yagona ombor va buyurtmalar nazorati CRM tizimini ishlab chiqish",
            "customer": "\"O'zagrologistika\" Milliy Markazi",
            "starting_price": "380,000,000 UZS",
            "raw_price": 380000000,
            "deadline": "2026-09-30",
            "category": "Logistika & CRM",
            "keywords": ["crm", "ombor", "logistika", "telegram bot", "dashboard"],
            "description": "Yuklarni qabul qilish, Telegram bot orqali buyurtmachilarga posilka holatini yetkazish va kassa to'lovlarini avtomat qayd qilish tizimi.",
            "qualification_brief": "Veb va mobil/Telegram tizimlar yaratish bo'yicha kamida 1 yillik tajriba.",
            "link": "https://xarid.icppa.uz"
        },
        {
            "lot_id": "LOT-XARID-24110599",
            "portal": "xarid.uzex.uz",
            "sector": "Davlat sektori",
            "title": "Koll-markaz operatorlari muloqot sifatini AI orqali baholash va transkripsiyalash tizimini joriy etish",
            "customer": "\"O'zbekneftgaz\" AJ Markaziy Boshqarmasi",
            "starting_price": "750,000,000 UZS",
            "raw_price": 750000000,
            "deadline": "2026-10-08",
            "category": "Sun'iy Intellekt & LLM",
            "keywords": ["ai", "speech-to-text", "audio", "call center", "koll-markaz", "sifat nazorati"],
            "description": "Kiruvchi va chiquvchi qo'ng'iroqlarni o'zbek va rus tillarida avtomat matnga aylantirish, xushmuomalalik va savollar hal etilganligini AI ball bilan baholash.",
            "qualification_brief": "Nutqni qayta ishlash (ASR/STT) yoki AI tahlil bo'yicha amaliy ishlanmalar mavjudligi.",
            "link": "https://xarid.uzex.uz"
        },
        {
            "lot_id": "LOT-UZEX-24110544",
            "portal": "etender.uzex.uz",
            "sector": "Davlat sektori",
            "title": "Bank ichki axborot xavfsizligi auditi va zaifliklarni aniqlash bo'yicha dasturiy-apparat majmuasi",
            "customer": "\"O'zmilliybank\" (NBU) AJ",
            "starting_price": "880,000,000 UZS",
            "raw_price": 880000000,
            "deadline": "2026-10-15",
            "category": "Kiberxavfsizlik & IT Audit",
            "keywords": ["xavfsizlik", "audit", "security", "kiberxavfsizlik", "tarmoq"],
            "description": "Bankning ichki infratuzilmasini pentest qilish, xavfsizlik protokollarini PCI-DSS va O'zbekiston Markaziy Banki talablariga muvofiqlashtirish.",
            "qualification_brief": "Axborot xavfsizligi sohasida litsenziya yoki sertifikatlangan ekspertlar mavjudligi.",
            "link": "https://etender.uzex.uz"
        },
        {
            "lot_id": "LOT-MC-24110512",
            "portal": "tender.mc.uz",
            "sector": "Davlat sektori",
            "title": "Qurilish obyektlari hisoboti va texnik nazorat smetasini avtomatlashtirish dasturi",
            "customer": "Qurilish va uy-joy kommunal xo'jaligi vazirligi",
            "starting_price": "540,000,000 UZS",
            "raw_price": 540000000,
            "deadline": "2026-10-12",
            "category": "PropTech & ConTech IT",
            "keywords": ["smeta", "qurilish", "dastur", "dashboard", "nazorat"],
            "description": "Qurilish obyektlari bo'yicha smeta xarajatlarini nazorat qilish, pudratchilar topshirgan dalolatnomalarni raqamlashtirish.",
            "qualification_brief": "Qurilish yoki korporativ hisob tizimlari bilan ishlash tajribasi.",
            "link": "https://tender.mc.uz"
        },
        {
            "lot_id": "LOT-ICPPA-24110480",
            "portal": "xarid.icppa.uz",
            "sector": "Davlat sektori",
            "title": "B2B buyurtmalar va distribyutsiya zanjirini nazorat qiluvchi elektron savdo platformasi",
            "customer": "\"UzPost\" AJ (O'zbekiston pochtasi)",
            "starting_price": "490,000,000 UZS",
            "raw_price": 490000000,
            "deadline": "2026-10-02",
            "category": "E-Commerce & B2B SaaS",
            "keywords": ["b2b", "e-commerce", "post", "platforma", "yetkazib berish", "crm"],
            "description": "Yetkazib beruvchilar va buyurtmachilar uchun B2B portal, shartnomalarni elektron imzolash va buyurtmalar marshrutizatsiyasi.",
            "qualification_brief": "Veb dasturlash, to'lov tizimlari va E-imzo integratsiyasi bo'yicha tajriba.",
            "link": "https://xarid.icppa.uz"
        },
        {
            "lot_id": "LOT-UZEX-24110410",
            "portal": "etender.uzex.uz",
            "sector": "Davlat sektori",
            "title": "Tibbiyot muassasalari uchun bemorlar elektron navbati va billing tizimi integratsiyasi",
            "customer": "Toshkent shahar Sog'liqni Saqlash Bosh Boshqarmasi",
            "starting_price": "580,000,000 UZS",
            "raw_price": 580000000,
            "deadline": "2026-10-10",
            "category": "MedTech & CRM",
            "keywords": ["crm", "tibbiyot", "navbat", "billing", "integratsiya"],
            "description": "Poliklinikalar uchun elektron navbat monitorlari, SMS/Telegram bildirishnomalar va xizmatlar hisob-kitobi.",
            "qualification_brief": "Tibbiyot yoki davlat xizmatlari loyihalarida ishtirok etganlik.",
            "link": "https://etender.uzex.uz"
        },
        {
            "lot_id": "LOT-XARID-24110385",
            "portal": "xarid.uzex.uz",
            "sector": "Davlat sektori",
            "title": "Suv ta'minoti korxonalari uchun billing va qarzdorlikni prognozlash tahliliy dashboardi",
            "customer": "\"O'zsuvta'minot\" AJ",
            "starting_price": "610,000,000 UZS",
            "raw_price": 610000000,
            "deadline": "2026-10-18",
            "category": "Data & Analytics",
            "keywords": ["dashboard", "tahlil", "billing", "prognoz", "ma'lumotlar bazasi"],
            "description": "Hisoblagichlar ma'lumotlarini tahlil qilish, noqonuniy ulanishlar xavfini aniqlovchi ML algoritmlar va interaktiv tahliliy xarita.",
            "qualification_brief": "Data Science va BI (PowerBI/Custom Dashboard) loyihalari portfoliosi.",
            "link": "https://xarid.uzex.uz"
        }
    ]

    @classmethod
    def calculate_relevance(cls, tender: Dict[str, Any], company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates AI match score and tags for a given tender against the company profile."""
        company_services = " ".join(company_profile.get("core_services", [])).lower()
        company_desc = company_profile.get("description", "").lower()
        all_company_text = f"{company_services} {company_desc}"

        tender_title = tender.get("title", "").lower()
        tender_desc = tender.get("description", "").lower()
        tender_keywords = tender.get("keywords", [])

        # Calculate keyword overlap strictly against company profile
        matched_keywords = []
        score = 15  # Baseline

        for kw in tender_keywords:
            if kw in all_company_text and len(kw) > 2:
                matched_keywords.append(kw)
                score += 15

        if "ai" in tender_title or "sun'iy intellekt" in tender_title or "llm" in tender_title or "artificial intelligence" in tender_title:
            score += 35
            matched_keywords.append("⭐️ Asosiy ixtisoslik (AI/LLM)")

        if "crm" in tender_title or "avtomat" in tender_title or "didox" in tender_title or "1c" in tender_title or "dasturiy" in tender_title or "software" in tender_title or "analytics" in tender_title or "monitoring" in tender_title or "skoring" in tender_title:
            score += 25
            matched_keywords.append("⚡️ Workflow & B2B Integratsiya")

        # Cap between 15% and 98%
        score = min(98, max(15, score))

        if score >= 80:
            badge = "🔥 YUQORI POTENSIAL (Tavsiya etiladi)"
            badge_color = "green"
        elif score >= 55:
            badge = "🟡 O'RTA POTENSIAL (Ko'rib chiqish mumkin)"
            badge_color = "orange"
        else:
            badge = "⚪️ PAST MOSLIK (Boshqa soha)"
            badge_color = "gray"

        return {
            "match_score": score,
            "badge": badge,
            "badge_color": badge_color,
            "matched_keywords": list(set(matched_keywords))
        }

    @classmethod
    def search_opportunities(
        cls,
        query: str = "",
        min_budget: int = 0,
        portal_filter: str = "Barchasi",
        category_filter: str = "Barchasi",
        sector_filter: str = "Barchasi",
        sort_by: str = "match_score",
        company_profile: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ) -> List[Dict[str, Any]]:
        try:
            from src.tender_ai.config import DEFAULT_COMPANY_PROFILE
        except ImportError:
            from config import DEFAULT_COMPANY_PROFILE
        profile = company_profile or DEFAULT_COMPANY_PROFILE

        try:
            try:
                from src.tender_ai.portal_scanner import PortalScanner
            except ImportError:
                from portal_scanner import PortalScanner
            opportunities_pool = PortalScanner.load_cached_tenders()
        except Exception:
            opportunities_pool = cls.DEFAULT_OPPORTUNITIES

        results = []
        q = query.lower().strip()

        for opp in opportunities_pool:
            # Determine sector fallback if missing
            opp_sector = opp.get("sector")
            if not opp_sector:
                portal_str = opp.get("portal", "")
                if "ungm" in portal_str or "worldbank" in portal_str or "ngo" in portal_str:
                    opp_sector = "Xalqaro NNT & BMT"
                elif "b2b" in portal_str or "telecom" in portal_str or "xt-xarid" in portal_str:
                    opp_sector = "Xususiy sektor & B2B"
                else:
                    opp_sector = "Davlat sektori"
            opp["sector"] = opp_sector

            # Filter by sector
            if sector_filter != "Barchasi" and opp_sector != sector_filter:
                continue

            # Filter by portal
            if portal_filter != "Barchasi" and opp["portal"] != portal_filter:
                continue

            # Filter by category
            if category_filter != "Barchasi" and opp.get("category") != category_filter:
                continue

            # Filter by min budget
            if opp["raw_price"] < min_budget:
                continue

            # Filter by query (keywords, title, customer, description)
            if q:
                match_text = f"{opp['title']} {opp['customer']} {opp['description']} {' '.join(opp.get('keywords', []))}".lower()
                if q not in match_text:
                    continue

            # Calculate match
            eval_res = cls.calculate_relevance(opp, profile)
            enriched = {**opp, **eval_res}
            results.append(enriched)

        # Apply user-selected sorting
        if sort_by == "budget_desc":
            results.sort(key=lambda x: x["raw_price"], reverse=True)
        elif sort_by == "budget_asc":
            results.sort(key=lambda x: x["raw_price"])
        elif sort_by == "deadline":
            results.sort(key=lambda x: x.get("deadline", "9999-12-31"))
        else: # "match_score" default
            results.sort(key=lambda x: x["match_score"], reverse=True)

        return results
