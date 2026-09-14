import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Default company profile for GPTify (B2B AI workflow consultancy and systems builder)
DEFAULT_COMPANY_PROFILE = {
    "name": "GPTify (GPTify.co)",
    "founder": "GPTify Uzbekistan Jamoasi",
    "description": "Pragmatik B2B AI workflow konsalting, sun'iy intellekt tizimlari integratsiyasi va maxsus dasturiy ta'minot ishlab chiqaruvchisi.",
    "core_services": [
        "Sun'iy intellekt (AI) va LLM asosidagi avtomatlashtirilgan tizimlar",
        "B2B CRM, Didox, 1C va korporativ ma'lumotlar bazasi integratsiyalari",
        "Korporativ AI agentlar, Telegram bot va chat-bot ekotizimlari",
        "Axborot xavfsizligi, ma'lumotlarni tahlil qilish va intellektual dashboardlar",
        "Koll-markazlar va mijozlar bilan muloqotni avtomatlashtirish"
    ],
    "experience_years": "3+ yil",
    "qualification_highlights": [
        "Yirik tijorat va davlat sektoridagi korxonalar uchun AI audit va integratsiya tajribasi",
        "Soliq qonunchiligi, Didox, 1C va xavfsiz API protokollari bilan ishlash bo'yicha amaliy tajriba",
        "Yuqori malakali Fullstack, Data Science va AI injiniring jamoasi",
        "Loyihalarni texnik topshiriq va SLA shartlari asosida o'z vaqtida topshirish kafolati"
    ]
}

# Supported sectors and platforms in Uzbekistan
SECTORS = {
    "public": "Davlat sektori (Public / State)",
    "ngo": "Xalqaro NNT & BMT (International NGOs / UN)",
    "private": "Xususiy sektor & B2B (Commercial & Banks)"
}

SUPPORTED_PORTALS = {
    # 1. Davlat portallari (State Procurement)
    "etender.uzex.uz": {
        "name": "UZEX Elektron Tender Portali",
        "sector": "Davlat sektori",
        "description": "O'zbekiston Respublika tovar-xom ashyo birjasi elektron tender portali",
        "url": "https://etender.uzex.uz"
    },
    "xarid.uzex.uz": {
        "name": "Davlat Xaridlari Portali (UZEX)",
        "sector": "Davlat sektori",
        "description": "Budjet va korporativ buyurtmachilar maxsus axborot portali",
        "url": "https://xarid.uzex.uz"
    },
    "xarid.icppa.uz": {
        "name": "ICPPA Yangi Davlat Xaridlari Portali (2026)",
        "sector": "Davlat sektori",
        "description": "Budjet buyurtmachilarining elektron do'kon, milliy do'kon va reja-jadvallar portali",
        "url": "https://xarid.icppa.uz"
    },
    "tender.mc.uz": {
        "name": "Qurilish Vazirligi Tender Portali",
        "sector": "Davlat sektori",
        "description": "Shaharsozlik va qurilish obyektlari xaridlari",
        "url": "https://tender.mc.uz"
    },
    # 2. Xalqaro tashkilotlar va NNT (International NGOs & UN)
    "ungm.org": {
        "name": "UN Global Marketplace (BMT / UNGM)",
        "sector": "Xalqaro NNT & BMT",
        "description": "UNDP, UNICEF, WHO, UNFPA O'zbekistondagi xarid va grant loyihalari",
        "url": "https://www.ungm.org/Public/Notice"
    },
    "unicef.org": {
        "name": "UNICEF O'zbekiston Vakolatxonasi",
        "sector": "Xalqaro NNT & BMT",
        "description": "UNICEF O'zbekiston rasmiy xarid va dasturiy tanlovlari",
        "url": "https://www.unicef.org/uzbekistan/tenders"
    },
    "worldbank.org": {
        "name": "Jahon Banki (World Bank Group)",
        "sector": "Xalqaro NNT & BMT",
        "description": "Xalqaro taraqqiyot va axborot texnologiyalari loyihalari",
        "url": "https://projects.worldbank.org/en/projects-operations/procurement"
    },
    # 3. Xususiy va Tijorat B2B (Private Sector & Commercial Banks)
    "ipakyulibank.uz": {
        "name": "Ipak Yo'li Banki Xaridlari",
        "sector": "Xususiy sektor & B2B",
        "description": "Yirik xususiy tijorat banki IT va xizmat ko'rsatish tanlovlari",
        "url": "https://ipakyulibank.uz"
    },
    "beeline.uz": {
        "name": "Beeline Uzbekistan (Unitel MCHJ)",
        "sector": "Xususiy sektor & B2B",
        "description": "Telekom va axborot texnologiyalari bo'yicha korporativ xaridlar",
        "url": "https://beeline.uz"
    },
    "xt-xarid.uz": {
        "name": "XT-Xarid B2B Savdo Maydonchasi",
        "sector": "Xususiy sektor & B2B",
        "description": "Xususiy ishlab chiqarish va yirik korxonalar xaridlari",
        "url": "https://xt-xarid.uz"
    }
}

# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PRIMARY_MODEL = os.getenv("TENDER_AI_MODEL", "gemini-flash-latest")
FALLBACK_MODEL = "gpt-4o-mini"
