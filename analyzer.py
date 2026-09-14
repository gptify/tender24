import json
import re
import os
import requests
from typing import Dict, Any, Optional
try:
    from src.tender_ai.config import GEMINI_API_KEY, PRIMARY_MODEL, DEFAULT_COMPANY_PROFILE
except ImportError:
    from config import GEMINI_API_KEY, PRIMARY_MODEL, DEFAULT_COMPANY_PROFILE

class TenderAnalyzer:
    """Analyzes Uzbekistan tender documents, assesses risks, and evaluates company match."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name or PRIMARY_MODEL

    def _call_gemini_json(self, system_instruction: str, user_prompt: str, pdf_base64: Optional[str] = None) -> Dict[str, Any]:
        """Calls Gemini API with automatic model fallback and native PDF multimodal support."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY topilmadi. Iltimos, .env faylini tekshiring.")

        candidate_models = [self.model_name, "gemini-2.5-flash", "gemini-1.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]
        candidate_models = list(dict.fromkeys(candidate_models))
        
        last_error = None
        for model in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            
            parts = [
                {"text": f"TIZIM QOIDALARI VA YO'RIQNOMA:\n{system_instruction}\n\nFOYDALANUVCHI SO'ROVI:\n{user_prompt}"}
            ]
            if pdf_base64:
                # Insert inline PDF data for native multimodal parsing (scanned pages, stamps, tables)
                parts.insert(0, {
                    "inline_data": {
                        "mime_type": "application/pdf",
                        "data": pdf_base64
                    }
                })

            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }

            try:
                response = requests.post(url, json=payload, timeout=90)
                if response.status_code == 200:
                    data = response.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned_text = re.sub(r"^```json\s*", "", raw_text.strip())
                    cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
                    return json.loads(cleaned_text)
                else:
                    last_error = f"Model {model} xatosi ({response.status_code}): {response.text[:200]}"
            except Exception as e:
                last_error = f"Model {model} ulanish xatosi: {str(e)}"

        raise RuntimeError(f"Barcha modellarda xatolik yuz berdi: {last_error}")

    def analyze_tender(
        self,
        tender_text: str,
        company_profile: Optional[Dict[str, Any]] = None,
        pdf_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """Performs comprehensive multi-point analysis on tender specifications with native multimodal support."""
        profile = company_profile or DEFAULT_COMPANY_PROFILE

        system_instruction = """
Siz O'zbekiston davlat va korporativ xaridlari (etender.uzex.uz, xarid.uzex.uz, tender.mc.uz) bo'yicha yetakchi yuridik va texnik audit ekspertisiz.
Vazifangiz: Berilgan tender hujjatini (Texnik topshiriq / Lot tavsifi) sinchkovlik bilan tahlil qilish, yashirin risklar va tuzoqlarni fosh etish hamda kompaniya imkoniyatlariga mosligini baholash.

Siz FAQAT quyidagi JSON formatida javob qaytarishingiz shart:
{
  "tender_summary": {
    "lot_number": "string yoki Noma'lum",
    "title": "Tender / Lotning to'liq nomi",
    "customer": "Buyurtmachi tashkilot nomi",
    "starting_price": "Boshlang'ich narx (so'mda yoki Noma'lum)",
    "deadline_execution": "Ishni bajarish / yetkazib berish muddati",
    "submission_deadline": "Takliflarni topshirish oxirgi muddati",
    "guarantee_deposit": "Zaklad / Bank kafolati talabi (foiz yoki summa)"
  },
  "qualification_requirements": [
    {
      "category": "Tajriba / Moliya / Xodimlar / Litsenziya",
      "requirement": "Aniq talab matni",
      "criticality": "YUQORI / O'RTA / PAST"
    }
  ],
  "risks_and_traps": [
    {
      "risk_title": "Xavf / Tuzoq sarlavhasi (masalan: Kechiktirilgan to'lov, Asossiz monopol texnik shart, Katta penya)",
      "risk_level": "QIZIL (Yuqori xavf) / SARIQ (O'rta xavf) / YASHIL (E'tibor berish kerak)",
      "explanation": "Nima uchun bu xavfli va qanday oqibatga olib kelishi mumkin",
      "recommendation": "Tavsiya (masalan: Buyurtmachiga tushuntirish xati yozish, narxga risk foizini qo'shish)"
    }
  ],
  "pricing_strategy": {
    "recommended_discount_percent": "3-6%",
    "target_bid_amount": "Taxminiy g'olib narx (masalan: 455,000,000 UZS)",
    "pricing_rationale": "O'zbekiston tenderlarida g'olib bo'lish va foydani saqlab qolish bo'yicha narx tavsiyasi"
  },
  "match_evaluation": {
    "match_score": 85,
    "verdict": "GO (Qatnashish tavsiya etiladi) / GO_WITH_CAUTION (Shartli tavsiya etiladi) / NO_GO (Qatnashish tavsiya etilmaydi)",
    "strengths": [
      "Kompaniyaning ushbu tenderdagi ustunliklari"
    ],
    "weaknesses_or_missing": [
      "Yetishmayotgan hujjatlar, sertifikatlar yoki zaif nuqtalar"
    ],
    "verdict_reasoning": "Qarorning qisqacha asoslanishi"
  },
  "action_checklist": [
    "Qatnashish uchun keyingi aniq harakatlar ro'yxati (masalan: Guvohnoma va 1-forma tayyorlash, Bank kafolati olish va h.k.)"
  ]
}
"""

        company_context = f"""
KOMPANIYA PROFILI:
- Nomi: {profile.get('name')}
- Muassis/Rahbar: {profile.get('founder')}
- Faoliyat tavsifi: {profile.get('description')}
- Asosiy xizmatlar: {', '.join(profile.get('core_services', []))}
- Tajriba: {profile.get('experience_years')}
- Malaka afzalliklari: {', '.join(profile.get('qualification_highlights', []))}
"""

        user_prompt = f"""
{company_context}

QUYIDAGI TENDER MATNINI VA HUJJATLARINI TAHLIL QILING:
----------------------------------------
{tender_text[:120000]}
----------------------------------------
"""

        return self._call_gemini_json(system_instruction, user_prompt, pdf_base64=pdf_base64)
