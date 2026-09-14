import os
import time
import datetime
import threading
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from src.tender_ai.config import DEFAULT_COMPANY_PROFILE
    from src.tender_ai.portal_scanner import PortalScanner
    from src.tender_ai.tender_finder import TenderFinder
    from src.tender_ai.notifier import TenderNotifier
    from src.tender_ai.db import DatabaseManager
except ImportError:
    from config import DEFAULT_COMPANY_PROFILE
    from portal_scanner import PortalScanner
    from tender_finder import TenderFinder
    from notifier import TenderNotifier
    from db import DatabaseManager

class TelegramAlertDaemon:
    """Continuous background worker that detects newly published UzEx lots 
    in real time and dispatches immediate Telegram alerts for relevant opportunities."""

    _running = False
    _thread = None
    _stats = {
        "status": "stopped",
        "last_poll_time": None,
        "total_checked": 0,
        "total_alerts_sent": 0,
        "last_message": "Bot to'xtatilgan"
    }

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        return {
            "is_running": cls._running,
            **cls._stats
        }

    @classmethod
    def poll_new_lots_once(
        cls,
        company_profile: Optional[Dict[str, Any]] = None,
        min_match_score: int = 65,
        keyword_filter: Optional[str] = None,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        profile = company_profile or DEFAULT_COMPANY_PROFILE
        token = (bot_token or os.getenv("TENDER_BOT_TOKEN", "")).strip()
        target_chat = (chat_id or os.getenv("TENDER_CHAT_ID", "") or os.getenv("TELEGRAM_CHAT_ID", "")).strip()

        # Fetch latest 40 lots from UzEx
        latest_lots = PortalScanner.fetch_uzex_live_lots(limit=40)
        
        new_lots_found = []
        alerts_sent = 0

        for lot in latest_lots:
            lot_id = str(lot.get("lot_id"))
            trade_url_id = lot.get("link", "").split("/")[-1]
            unique_key = f"UZEX-{trade_url_id or lot_id}"

            if not DatabaseManager.is_lot_seen(unique_key):
                # This is a brand new lot published on UzEx!
                eval_res = TenderFinder.calculate_relevance(lot, profile)
                lot.update(eval_res)
                new_lots_found.append(lot)

                # Keyword filtering if specified
                if keyword_filter and keyword_filter.strip():
                    kw = keyword_filter.lower().strip()
                    lot_text = f"{lot.get('title', '')} {lot.get('customer', '')} {lot.get('description', '')}".lower()
                    if kw not in lot_text:
                        DatabaseManager.mark_lot_seen(unique_key, portal="etender.uzex.uz", notified=False)
                        continue

                # Check if it matches company criteria
                if lot.get("match_score", 0) >= min_match_score:
                    if token and target_chat:
                        res = TenderNotifier.send_telegram_alert(lot, bot_token=token, chat_id=target_chat)
                        if res.get("success"):
                            alerts_sent += 1
                            DatabaseManager.mark_lot_seen(unique_key, portal="etender.uzex.uz", notified=True)
                            continue

                DatabaseManager.mark_lot_seen(unique_key, portal="etender.uzex.uz", notified=False)

        cls._stats["last_poll_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cls._stats["total_checked"] += len(latest_lots)
        cls._stats["total_alerts_sent"] += alerts_sent
        cls._stats["last_message"] = f"{len(latest_lots)} ta lot tekshirildi, {len(new_lots_found)} ta yangi, {alerts_sent} ta xabar yuborildi."

        return {
            "timestamp": cls._stats["last_poll_time"],
            "checked_lots": len(latest_lots),
            "brand_new_lots": len(new_lots_found),
            "alerts_sent": alerts_sent
        }

    @classmethod
    def start_daemon(
        cls, 
        interval_seconds: int = 90, 
        min_match_score: int = 65,
        keyword_filter: Optional[str] = None,
        company_profile: Optional[Dict[str, Any]] = None,
        bot_token: Optional[str] = None, 
        chat_id: Optional[str] = None
    ):
        """Starts real-time polling thread."""
        if cls._running:
            return "Telegram real-time bot xizmati allaqachon ishlab turibdi."

        cls._running = True
        cls._stats["status"] = "running"
        cls._stats["last_message"] = f"Faol (har {interval_seconds} soniyada tekshiradi)"

        def loop():
            print(f"[TelegramDaemon] Ishga tushdi. Har {interval_seconds} soniyada yangi e'lonlar tekshiriladi...")
            while cls._running:
                try:
                    res = cls.poll_new_lots_once(
                        company_profile=company_profile,
                        min_match_score=min_match_score,
                        keyword_filter=keyword_filter,
                        bot_token=bot_token, 
                        chat_id=chat_id
                    )
                    if res["alerts_sent"] > 0:
                        print(f"[TelegramDaemon] {res['alerts_sent']} ta yangi mos lot Telegram'ga yuborildi!")
                except Exception as e:
                    cls._stats["last_message"] = f"Xatolik: {e}"
                    print(f"[TelegramDaemon] Xatolik: {e}")
                time.sleep(interval_seconds)

        cls._thread = threading.Thread(target=loop, daemon=True)
        cls._thread.start()
        return f"🟢 Real-time Telegram xabarnomasi faol! (Har {interval_seconds} soniyada yangi lotlar tekshiriladi)"

    @classmethod
    def stop_daemon(cls):
        """Stops the real-time polling thread."""
        cls._running = False
        cls._stats["status"] = "stopped"
        cls._stats["last_message"] = "Bot to'xtatildi"
        return "Telegram bot xizmati to'xtatildi."

if __name__ == "__main__":
    print("TenderPro AI: Telegram Real-time Daemon ishga tushmoqda...")
    TelegramAlertDaemon.start_daemon(interval_seconds=60)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        TelegramAlertDaemon.stop_daemon()
        print("To'xtatildi.")
