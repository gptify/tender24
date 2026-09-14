import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class TenderNotifier:
    """Handles real-time instant notifications via Telegram Bot and Email 
    whenever high-potential procurement opportunities are discovered."""

    @staticmethod
    def send_telegram_alert(
        tender: Dict[str, Any],
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sends a rich, actionable alert to a Telegram user or channel."""
        token = (bot_token or os.getenv("TENDER_BOT_TOKEN", "")).strip()
        target_chat = (chat_id or os.getenv("TENDER_CHAT_ID", "") or os.getenv("TELEGRAM_CHAT_ID", "")).strip()

        if not token or not target_chat:
            return {
                "success": False,
                "error": "Telegram Bot Token yoki Chat ID ko'rsatilmagan. Iltimos, sozlamalarni to'ldiring."
            }

        lot_id = tender.get("lot_id", "Noma'lum")
        portal = tender.get("portal", "etender.uzex.uz")
        title = tender.get("title", "")
        customer = tender.get("customer", "")
        price = tender.get("starting_price", "Noma'lum")
        deadline = tender.get("deadline", "Noma'lum")
        score = tender.get("match_score", 85)
        link = tender.get("link", f"https://{portal}")
        category = tender.get("category", "IT & Dasturiy ta'minot")

        web_url = (os.getenv("TENDER_WEB_URL") or "https://tenderpro24.streamlit.app").strip().rstrip("/")
        app_lot_link = f"{web_url}/?lot={lot_id}"

        message = (
            f"🎯 <b>YANGI MOS TENDER ANIQLANDI!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 <b>AI Moslik Bali:</b> <code>{score}%</code> ({category})\n"
            f"🏛 <b>Buyurtmachi:</b> {customer}\n"
            f"📋 <b>Lot:</b> <code>{lot_id}</code> ({portal})\n"
            f"📝 <b>Mavzu:</b> {title}\n"
            f"💰 <b>Boshlang'ich narx:</b> <b>{price}</b>\n"
            f"⏳ <b>Topshirish muddati:</b> <b>{deadline}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👉 <b><a href=\"{app_lot_link}\">TenderPro²⁴ Ilovasida Ko'rish va Tahlil Qilish ➔</a></b>\n"
            f"🔗 <a href=\"{link}\">Rasmiy Portaldagi Lot Sahifasi</a>"
        )

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": target_chat,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                return {"success": True, "data": res.json()}
            else:
                return {"success": False, "error": f"Telegram API xatosi ({res.status_code}): {res.text}"}
        except Exception as e:
            return {"success": False, "error": f"Telegramga ulanishda xatolik: {str(e)}"}

    @staticmethod
    def send_test_telegram(bot_token: str, chat_id: str) -> Dict[str, Any]:
        """Sends a test verification message to ensure credentials are valid."""
        test_tender = {
            "lot_id": "LOT-TEST-2026",
            "portal": "etender.uzex.uz",
            "title": "Sun'iy intellekt va CRM integratsiyasi (Sinov xabari)",
            "customer": "TenderPro AI Test Tizimi",
            "starting_price": "500,000,000 UZS",
            "deadline": "2026-10-01",
            "match_score": 95,
            "category": "Sun'iy Intellekt & LLM",
            "link": "https://etender.uzex.uz"
        }
        return TenderNotifier.send_telegram_alert(test_tender, bot_token=bot_token, chat_id=chat_id)

    @staticmethod
    def send_email_alert(
        tender: Dict[str, Any],
        recipient_email: str,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587
    ) -> Dict[str, Any]:
        """Sends an HTML formatted tender alert to the specified email."""
        user = smtp_user or os.getenv("SMTP_USER", "").strip()
        pwd = smtp_password or os.getenv("SMTP_PASSWORD", "").strip()

        if not user or not pwd or not recipient_email:
            return {"success": False, "error": "Email sozlamalari (SMTP_USER, SMTP_PASSWORD) to'liq emas."}

        lot_id = tender.get("lot_id", "Noma'lum")
        title = tender.get("title", "")
        customer = tender.get("customer", "")
        price = tender.get("starting_price", "Noma'lum")
        deadline = tender.get("deadline", "Noma'lum")
        score = tender.get("match_score", 85)
        link = tender.get("link", "#")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🎯 [TenderPro²⁴] Yangi Mos Tender: {lot_id} ({score}% moslik)"
        msg["From"] = user
        msg["To"] = recipient_email

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px;">
            <div style="background-color: #1E3A8A; color: white; padding: 12px 16px; border-radius: 6px;">
                <h2 style="margin: 0; font-size: 1.2rem;">🛡️ TenderPro²⁴: Yangi Mos Lot Topildi</h2>
            </div>
            <p style="font-size: 1.1rem; font-weight: bold; color: #16A34A; margin-top: 15px;">🔥 Moslik Darajasi: {score}%</p>
            <p><strong>Mavzu:</strong> {title}</p>
            <p><strong>Buyurtmachi:</strong> {customer}</p>
            <p><strong>Boshlang'ich narx:</strong> {price}</p>
            <p><strong>Topshirish muddati:</strong> {deadline}</p>
            <div style="margin-top: 20px;">
                <a href="{link}" style="background-color: #2563EB; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; font-weight: bold;">Portaldagi Tenderni Ko'rish</a>
            </div>
        </div>
        """
        msg.attach(MIMEText(html_body, "html"))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(user, pwd)
            server.sendmail(user, recipient_email, msg.as_string())
            server.quit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Email yuborishda xatolik: {str(e)}"}

    @staticmethod
    def send_lead_registration_alert(
        company_name: str,
        contact_person: str,
        phone: str,
        email: str,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sends an instant lead alert to the admin Telegram when a company registers with Phone or Gmail."""
        token = (bot_token or os.getenv("TENDER_BOT_TOKEN", "") or "8925436557:AAGHD3BK0LYoQPhUbgrdBwIQxvIqRGI9p-s").strip()
        target_chat = (chat_id or os.getenv("TENDER_CHAT_ID", "") or os.getenv("TELEGRAM_CHAT_ID", "") or "5077641672").strip()

        if not token or not target_chat:
            return {"success": False, "error": "Bot token or chat_id not set"}

        message = (
            f"🔔 <b>YANGI B2B LID / RO'YXATDAN O'TISH:</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🏢 <b>Tashkilot:</b> <b>{company_name}</b>\n"
            f"👤 <b>Mas'ul shaxs:</b> {contact_person or 'Kiritilmagan'}\n"
            f"📞 <b>Telefon:</b> <code>{phone or 'Kiritilmagan'}</code>\n"
            f"📧 <b>Gmail / Email:</b> <code>{email or 'Kiritilmagan'}</code>\n"
            f"🎁 <b>Status:</b> 3 ta bepul AI audit taqdim etildi\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ <i>TenderPro²⁴ B2B CRM bazasiga saqlandi</i>"
        )

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": target_chat,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        try:
            resp = requests.post(url, json=payload, timeout=8)
            return {"success": resp.status_code == 200, "status_code": resp.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}
