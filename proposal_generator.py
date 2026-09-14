import requests
from typing import Dict, Any, Optional

try:
    from src.tender_ai.config import GEMINI_API_KEY, PRIMARY_MODEL, DEFAULT_COMPANY_PROFILE
except ImportError:
    from config import GEMINI_API_KEY, PRIMARY_MODEL, DEFAULT_COMPANY_PROFILE

class ProposalGenerator:
    """Generates formal Technical Proposals, Commercial Offers, and Compliance Checklists
    across State, International NGO/UN, and Private B2B sectors in Uzbek, Russian, and English."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or PRIMARY_MODEL

    def _call_gemini_text(self, system_instruction: str, user_prompt: str) -> str:
        """Calls Gemini API with automatic model fallback for high reliability."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY topilmadi.")

        candidate_models = [self.model_name, "gemini-flash-lite-latest", "gemini-3-flash-preview", "gemini-flash-latest"]
        candidate_models = list(dict.fromkeys(candidate_models))

        last_error = None
        for model in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_instruction}\n\n{user_prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 4096
                }
            }

            try:
                response = requests.post(url, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    last_error = f"Model {model} xatosi ({response.status_code}): {response.text[:200]}"
            except Exception as e:
                last_error = f"Model {model} ulanish xatosi: {str(e)}"

        raise RuntimeError(f"Barcha modellarda xatolik yuz berdi: {last_error}")

    def generate_technical_proposal(self, tender_data: Dict[str, Any], company_profile: Optional[Dict[str, Any]] = None, language: str = "uz") -> str:
        """Generates a formal, professional Technical Proposal (Texnik taklif / RFP) tailored to State, NGO, or B2B tenders."""
        profile = company_profile or DEFAULT_COMPANY_PROFILE

        if language == "en":
            lang_style = "English (International UNGM / World Bank Development Procurement Standard)"
            structure_prompt = """
Document Structure:
1. Executive Summary & Understanding of the Terms of Reference (TOR).
2. Bidder Qualifications, Corporate Profile & Track Record.
3. Clause-by-Clause Technical Compliance Matrix (Table: TOR Requirement | Proposed Technical Solution | Compliance Status [Fully Compliant]).
4. Work Breakdown Structure (WBS), Methodology, and Milestone Calendar.
5. Key Personnel, Staffing Plan & Relevant Certifications.
6. Quality Assurance, Data Privacy, Security Protocols & SLA Guarantees.
"""
        elif language == "ru":
            lang_style = "Rus tili (Ofitsialno-delovoy stil dlya gosudarstvennix i korporativnix zakupok)"
            structure_prompt = """
Hujjat tuzilishi:
1. Sarlavha va Buyurtmachiga rasmiy murojaat.
2. Ishtirokchi korxona to'g'risida ma'lumot (Guvohnoma, tajriba, muvofiqlik).
3. Texnik topshiriq (TT) talablarining bandma-band bajarilishi (Jadval: Talab | Bizning taklif | Muvofiqligi).
4. Ishni bajarish metodologiyasi, bosqichlari va Kalendar rejasi.
5. Jalb etiladigan mutaxassislar tarkibi va ularning malakasi.
6. Sifat kafolati, SLA va Texnik qo'llab-quvvatlash shartlari.
"""
        else:
            lang_style = "O'zbek tili (Rasmiy-idoraviy uslub O'RQ-684 qonuni va korporativ standartlar asosida)"
            structure_prompt = """
Hujjat tuzilishi:
1. Sarlavha va Buyurtmachiga rasmiy murojaat.
2. Ishtirokchi korxona to'g'risida ma'lumot (Guvohnoma, tajriba, muvofiqlik).
3. Texnik topshiriq (TT) talablarining bandma-band bajarilishi (Jadval: Talab | Bizning taklif | Muvofiqligi).
4. Ishni bajarish metodologiyasi, bosqichlari va Kalendar rejasi.
5. Jalb etiladigan mutaxassislar tarkibi va ularning malakasi.
6. Sifat kafolati, SLA va Texnik qo'llab-quvvatlash shartlari.
"""

        system_instruction = f"""
You are a senior enterprise procurement engineer specializing in winning government, international NGO (UN/World Bank), and corporate B2B tenders in Uzbekistan.
Your mission: Generate a compelling, rigorous, and fully compliant **TECHNICAL PROPOSAL / RFP RESPONSE**.
Language: {lang_style}.
{structure_prompt}
"""

        user_prompt = f"""
BUYURTMACHI VA TENDER MA'LUMOTLARI (PROCURING ENTITY & TENDER DETAILS):
- Tender/Lot nomi: {tender_data.get('tender_summary', {}).get('title')}
- Buyurtmachi: {tender_data.get('tender_summary', {}).get('customer')}
- Boshlang'ich narx: {tender_data.get('tender_summary', {}).get('starting_price')}
- Ijro muddati: {tender_data.get('tender_summary', {}).get('deadline_execution')}

ISHTIROKCHI KOMPANIYA (BIDDER PROFILE):
- Nomi: {profile.get('name')}
- Rahbari / Vakil: {profile.get('founder')}
- Faoliyat tavsifi: {profile.get('description')}
- Asosiy xizmatlar: {', '.join(profile.get('core_services', []))}
- Malaka yutuqlari: {', '.join(profile.get('qualification_highlights', []))}

TENDER TALABLARI VA XUSUSIYATLARI:
{tender_data.get('qualification_requirements', [])}

Iltimos, to'liq, mukammal va tender komissiyasiga topshirishga tayyor Texnik taklif / RFP loyihasini tuzib bering.
"""

        return self._call_gemini_text(system_instruction, user_prompt)

    def generate_guarantee_letter(self, tender_data: Dict[str, Any], company_profile: Optional[Dict[str, Any]] = None, language: str = "uz") -> str:
        """Generates formal Guarantee Letter / Bid Submission Letter."""
        profile = company_profile or DEFAULT_COMPANY_PROFILE
        customer = tender_data.get('tender_summary', {}).get('customer', "Xarid komissiyasiga")
        title = tender_data.get('tender_summary', {}).get('title', "Tender")

        if language == "en":
            return f"""# OFFICIAL BID SUBMISSION & GUARANTEE LETTER

**To:** Evaluation Committee of {customer}  
**From:** Management of "{profile.get('name')}"  
**Date:** [Current Date]  
**Subject:** Bid Submission & Formal Guarantee for "{title}"  

Dear Members of the Evaluation Committee,

Having examined the bidding documents and Terms of Reference (TOR) for the above-referenced tender, we, the undersigned, hereby formally submit our proposal and provide the following irrevocable guarantees:

1. **Full Compliance:** All works, deliverables, and services will be executed in strict adherence to the technical specifications and within the agreed timeline.
2. **Warranty & SLA:** We commit to providing a minimum of 12 (twelve) months comprehensive warranty and ongoing technical maintenance from the date of final acceptance.
3. **Bid Validity:** This proposal shall remain valid and binding upon us for a period of 60 (sixty) calendar days from the submission deadline.
4. **Ethics & Anti-Corruption:** We certify that our organization adheres to zero-tolerance policies regarding fraud, corruption, and conflict of interest, and has no outstanding tax liabilities.

Sincerely,

**Authorized Signatory for "{profile.get('name')}":**  
{profile.get('founder')}  
*(Signature and Corporate Stamp)* ____________________
"""
        elif language == "ru":
            return f"""# ГАРАНТИЙНОЕ ПИСЬМО

**Кому:** Закупочной комиссии {customer}  
**От кого:** Руководство "{profile.get('name')}"  
**Дата:** [Текущая дата]  
**Тема:** Гарантийные обязательства по лоту "{title}"  

Уважаемые члены Закупочной комиссии!

Настоящим письмом компания "{profile.get('name')}" выражает готовность принять участие в объявленном конкурсе и официально гарантирует следующее:

1. **Качество и сроки:** Все работы и услуги будут выполнены в полном соответствии с Техническим заданием (ТЗ) и в установленные сроки.
2. **Гарантийный срок:** На все выполненные работы предоставляется официальная бесплатная гарантия и техническая поддержка сроком не менее 12 (двенадцати) месяцев.
3. **Срок действия предложения:** Данное предложение сохраняет силу в течение 60 (шестидесяти) календарных дней с момента окончания приема заявок.
4. **Юридическая чистота:** Подтверждаем отсутствие задолженностей по налогам и сборам, а также соблюдение антикоррупционных стандартов законодательства.

**Руководитель "{profile.get('name')}":**  
{profile.get('founder')}  
*(Подпись и М.П.)* ____________________
"""
        else:
            return f"""# KAFOLAT XATI

**Kimgа:** {customer} Xarid komissiyasiga  
**Kimdаn:** "{profile.get('name')}" rahbariyati  
**Sana:** [Joriy sana]  
**Mavzu:** "{title}" bo'yicha kafolat majburiyatlari  

Hurmatli Xarid komissiyasi a'zolari!

Mazkur xat orqali "{profile.get('name')}" jamoasi e'lon qilingan mazkur tanlovda ishtirok etish niyatini bildiradi hamda quyidagilarni rasman kafolatlaydi:

1. **Sifat va Muddat:** Barcha xizmatlar/ishlar Texnik topshiriqda ko'rsatilgan talablarga 100% to'liq muvofiq ravishda va belgilangan muddatlarda amalga oshiriladi.
2. **Kafolat muddati:** Bajarilgan ishlarga rasmiy qabul qilish-topshirish dalolatnomasi imzolangan kundan boshlab kamida 12 (o'n ikki) oy davomida bepul kafolatli texnik xizmat ko'rsatiladi.
3. **Taklifning amal qilish muddati:** Ushbu tijorat va texnik taklif tanlov natijalari e'lon qilingan kundan boshlab 60 (oltmish) kalendar kuni davomida o'z kuchini saqlab qoladi.
4. **Qonuniy tozalik va Korrupsiyaga qarshi kafolat:** Korxonamiz O'zbekiston Respublikasi "Davlat xaridlari to'g'risida"gi Qonunining barcha talablariga rioya etishini, soliq va boshqa majburiy to'lovlar bo'yicha qarzdorlikka ega emasligini hamda manfaatlar to'qnashuvi yo'qligini tasdiqlaydi.

**"{profile.get('name')}" Rahbari:**  
{profile.get('founder')}  
*(Imzo va muhr o'rni)* ____________________
"""

    def generate_document_checklist(self, tender_data: Dict[str, Any], language: str = "uz") -> str:
        """Generates the comprehensive submission checklist across languages."""
        if language == "en":
            return """### Mandatory Document Submission Checklist (UN / International / B2B)

| № | Required Document | Issuing Authority / Format | Status |
|---|-------------------|----------------------------|--------|
| 1 | **Certificate of Incorporation / Legal Registration** | State Services / PDF with QR | [ ] Ready |
| 2 | **Tax Clearance Certificate** | my.soliq.uz official statement | [ ] Ready |
| 3 | **Audited Financial Statements (Balance Sheet & P&L)** | Past 1-2 fiscal years | [ ] Ready |
| 4 | **Track Record of Relevant Past Contracts** | Client completion certificates / copies | [ ] Ready |
| 5 | **Key Personnel CVs & Credentials** | Diplomas, certifications & signed CVs | [ ] Ready |
| 6 | **Technical Proposal (Generated by TenderPro AI)** | Signed and stamped official submission | [ ] Ready |
| 7 | **Commercial Financial Proposal / Price Schedule** | Cost breakdown within budget envelope | [ ] Ready |
| 8 | **Official Letter of Guarantee / Bid Securing Declaration**| On corporate letterhead with stamp | [ ] Ready |
| 9 | **Bid Security / Deposit (if applicable)** | 3% bank guarantee or deposit receipt | [ ] Ready |
| 10| **Digital Signature / Authorization Letter** | Authorized signatory Power of Attorney | [ ] Ready |
"""
        elif language == "ru":
            return """### Контрольный список обязательных документов для участия

| № | Наименование документа | Источник / Формат | Статус |
|---|------------------------|-------------------|--------|
| 1 | **Свидетельство о гос. регистрации (Гувохнома)** | ЕПИГУ (my.gov.uz) PDF с QR-кодом | [ ] Готово |
| 2 | **Справка об отсутствии задолженности по налогам** | my.soliq.uz официальная выписка | [ ] Готово |
| 3 | **Финансовая отчетность (Форма 1 Баланс, Форма 2 Отчет о фин. результатах)** | За последний отчетный период | [ ] Готово |
| 4 | **Опыт выполнения аналогичных договоров** | Копии контрактов и актов выполненных работ | [ ] Готово |
| 5 | **Квалификация ключевого персонала** | Дипломы, сертификаты и резюме | [ ] Готово |
| 6 | **Техническое предложение (TenderPro AI)** | Подписанное и скрепленное печатью | [ ] Готово |
| 7 | **Коммерческое (ценовое) предложение** | Обоснованная смета стоимости | [ ] Готово |
| 8 | **Гарантийное письмо** | На фирменном бланке организации | [ ] Готово |
| 9 | **Задаток / Банковская гарантия (3%)** | Подтверждение оплаты через портал | [ ] Готово |
| 10| **ЭЦП (Электронная цифровая подпись)** | Подписание всех файлов перед отправкой | [ ] Готово |
"""
        else:
            return """### Tenderga Ilova Qilinishi Shart Bo'lgan Hujjatlar Nazorat Ro'yxati (Checklist)

| № | Hujjat Nomi | Qayerdan olinadi / Tayyorlash shakli | Holati |
|---|-------------|---------------------------------------|--------|
| 1 | **Guvohnoma (Davlat ro'yxatidan o'tganlik to'g'risida)** | Yagona darcha (my.gov.uz) PDF | [ ] Tayyor |
| 2 | **Soliqdan qarz yo'qligi to'g'risida ma'lumotnoma** | my.soliq.uz shaxsiy kabinetidan olingan yangi QR-kodli spravka | [ ] Tayyor |
| 3 | **Moliyaviy hisobot (1-Forma Balans, 2-Forma Moliyaviy natijalar)** | Oxirgi hisobot davri uchun soliq qabul qilgan tasdiq belgisi bilan | [ ] Tayyor |
| 4 | **Bajarilgan shunga o'xshash loyihalar ro'yxati (Tajriba)** | Shartnomalar va akt-sverkalar / topshirish dalolatnomalari nusxasi | [ ] Tayyor |
| 5 | **Jalb etiladigan mutaxassislar malakasi** | Diplomlar, rezyumelar, buyruqlar yoki mehnat shartnomalari nusxasi | [ ] Tayyor |
| 6 | **Texnik taklif (TenderPro AI tomonidan tayyorlangan)** | Chop etilgan, har bir sahifasi imzolangan va muhrlangan | [ ] Tayyor |
| 7 | **Tijorat taklifi (Narxlar va to'lov grafigi)** | Boshlang'ich narxdan kamida 3-7% pastroq qilib rasmiylashtirilgan smeta | [ ] Tayyor |
| 8 | **Kafolat xati (Garantiynoe pismo)** | Korxona blankida rahbar imzosi bilan | [ ] Tayyor |
| 9 | **Zaklad / Bank kafolati (Agar talab qilingan bo'lsa)** | etender.uzex.uz shaxsiy hisobiga pul o'tkazish yoki bank kafolati | [ ] Tayyor |
| 10| **ERI (Elektron raqamli imzo)** | Portalga yuklashda barcha fayllarni E-imzo orqali tasdiqlash | [ ] Tayyor |
"""

    def generate_compliance_checklist(self, tender_data: Dict[str, Any], company_profile: Optional[Dict[str, Any]] = None, language: str = "uz") -> str:
        """Alias for generate_document_checklist to maintain backward compatibility."""
        return self.generate_document_checklist(tender_data, language=language)
