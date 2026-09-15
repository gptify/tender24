import os
import json
import time
import datetime
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

try:
    from src.tender_ai.config import DEFAULT_COMPANY_PROFILE
    from src.tender_ai.notifier import TenderNotifier
except ImportError:
    from config import DEFAULT_COMPANY_PROFILE
    from notifier import TenderNotifier

CACHE_FILE = Path(__file__).resolve().parent / "data" / "tenders_live.json"

class PortalScanner:
    """Live web and portal scanner for Uzbekistan procurement portals across State, 
    International NGOs/UN, and Private B2B sectors."""

    PORTAL_URLS = {
        # State
        "etender.uzex.uz": "https://etender.uzex.uz",
        "xarid.uzex.uz": "https://xarid.uzex.uz",
        "xarid.icppa.uz": "https://xarid.icppa.uz",
        "tender.mc.uz": "https://tender.mc.uz",
        # International NGOs & UN
        "ungm.org": "https://www.ungm.org/Public/Notice",
        "unicef.org": "https://www.unicef.org/uzbekistan/tenders",
        "worldbank.org": "https://projects.worldbank.org/en/projects-operations/procurement",
        # Private Sector & Commercial B2B
        "ipakyulibank.uz": "https://ipakyulibank.uz",
        "beeline.uz": "https://beeline.uz",
        "xt-xarid.uz": "https://xt-xarid.uz"
    }

    _background_thread = None
    _scheduler_active = False

    @classmethod
    def load_cached_tenders(cls) -> List[Dict[str, Any]]:
        """Loads cached tender opportunities merged with all default curated multi-sector lots."""
        try:
            from src.tender_ai.tender_finder import TenderFinder
        except ImportError:
            from tender_finder import TenderFinder
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        existing_ids = {item.get("lot_id") for item in data}
                        merged = list(data)
                        for d in TenderFinder.DEFAULT_OPPORTUNITIES:
                            if d["lot_id"] not in existing_ids:
                                merged.append(d)
                        return merged
            except Exception:
                pass
        return TenderFinder.DEFAULT_OPPORTUNITIES

    @classmethod
    def save_cached_tenders(cls, tenders: List[Dict[str, Any]]):
        """Saves discovered tenders to local JSON cache."""
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(tenders, f, ensure_ascii=False, indent=2)

    @classmethod
    def ping_portals(cls) -> Dict[str, Dict[str, Any]]:
        """Checks live reachability and latency of all supported portals."""
        status_report = {}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        for portal, url in cls.PORTAL_URLS.items():
            start_t = time.time()
            try:
                res = requests.get(url, headers=headers, timeout=6)
                latency = round((time.time() - start_t) * 1000, 1)
                status_report[portal] = {
                    "online": res.status_code in [200, 301, 302, 403], # 403 on cloudflare still means reachable
                    "status_code": res.status_code,
                    "latency_ms": latency,
                    "url": url,
                    "last_checked": datetime.datetime.now().strftime("%H:%M:%S")
                }
            except Exception as e:
                status_report[portal] = {
                    "online": False,
                    "status_code": None,
                    "error": str(e)[:60],
                    "url": url,
                    "last_checked": datetime.datetime.now().strftime("%H:%M:%S")
                }
        return status_report

    @classmethod
    def fetch_uzex_live_lots(cls, limit: int = 40) -> List[Dict[str, Any]]:
        """Directly fetches live public and corporate procurement lots from UzEx API."""
        url = "https://apietender.uzex.uz/api/common/TradeList"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Content-Type": "application/json"}
        payload = {"From": 1, "To": limit}
        
        real_lots = []
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=12)
            if res.status_code == 200:
                raw_lots = res.json()
                for l in raw_lots:
                    trade_id = l.get("id")
                    if not trade_id:
                        continue
                    display_no = str(l.get("display_no") or f"LOT-{trade_id}")
                    raw_cost = float(l.get("cost") or 0)
                    name = l.get("name") or "Davlat xaridi"
                    seller = l.get("seller_name") or "Davlat buyurtmachisi"
                    end_date = (l.get("end_date") or "")[:10]
                    cat = l.get("category_name") or "Davlat xaridi"
                    
                    real_lots.append({
                        "lot_id": display_no,
                        "portal": "etender.uzex.uz",
                        "sector": "Davlat sektori",
                        "title": name,
                        "customer": seller,
                        "starting_price": f"{raw_cost:,.0f} UZS" if raw_cost else "Noma'lum",
                        "raw_price": int(raw_cost),
                        "deadline": end_date,
                        "category": cat,
                        "keywords": [w.lower() for w in name.split() if len(w) > 3][:6],
                        "description": f"{name}. Buyurtmachi: {seller}. Toifa: {cat}.",
                        "qualification_brief": "Texnik topshiriq va malaka talablari rasmiy portalda ko'rsatilgan.",
                        "link": f"https://etender.uzex.uz/lot/{trade_id}"
                    })
        except Exception as e:
            print(f"Error fetching live UzEx lots: {e}")
            
        return real_lots

    @classmethod
    def fetch_ungm_live_lots(cls, limit: int = 25) -> List[Dict[str, Any]]:
        """Directly fetches live international procurement notices for Uzbekistan from UNGM (UNDP, UNOPS, UNICEF, IOM, WHO)."""
        import re
        s = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'text/html, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }
        ungm_lots = []
        try:
            s.get('https://www.ungm.org/Public/Notice', headers=headers, timeout=8)
            payload = {
                'PageIndex': 0,
                'PageSize': limit,
                'Title': '',
                'Description': 'Uzbekistan',
                'Reference': '',
                'PublishedFrom': '',
                'PublishedTo': '',
                'DeadlineFrom': '',
                'DeadlineTo': '',
                'Countries': [],
                'Agencies': [],
                'UNSPSCs': [],
                'NoticeTypes': [],
                'SortField': 'Deadline',
                'SortAscending': True,
                'isPicker': False,
                'IsSustainable': False,
                'IsActive': True,
                'NoticeDisplayType': None,
                'NoticeSearchTotalLabelId': 'noticeSearchTotal',
                'TypeOfCompetitions': []
            }
            res = s.post('https://www.ungm.org/Public/Notice/Search', json=payload, headers=headers, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.find_all('div', class_='dataRow')
                for row in rows:
                    nid = row.get('data-noticeid')
                    cells = [c.get_text(' ', strip=True) for c in row.find_all('div', role='cell')]
                    if len(cells) >= 6:
                        raw_title = cells[1].replace('Open in a new window', '').strip()
                        deadline_raw = cells[2]
                        m = re.search(r'(\d{1,2}-[A-Za-z]{3}-\d{4})', deadline_raw)
                        deadline = m.group(1) if m else deadline_raw[:11]
                        agency = cells[4]
                        proc_type = cells[5]
                        ungm_lots.append({
                            'lot_id': f'UNGM-{nid}',
                            'portal': 'ungm.org',
                            'sector': 'Xalqaro NNT & BMT',
                            'title': raw_title,
                            'customer': f"{agency} (BMT / UNGM O'zbekiston)",
                            'starting_price': 'Grant / Valyuta (AQSh dollari)',
                            'raw_price': 1200000000,
                            'deadline': deadline,
                            'category': 'Xalqaro NNT / BMT Loyihalari',
                            'keywords': ['ungm', agency.lower(), 'grant', 'international', 'bmt'] + [w.lower() for w in raw_title.split() if len(w) > 3][:4],
                            'description': f"{raw_title}. Agentlik: {agency}. Xarid turi: {proc_type}. BMT / UNGM O'zbekiston loyihasi.",
                            'qualification_brief': "BMT xarid nizomlari bo'yicha xalqaro tajriba, moliyaviy barqarorlik va ingliz tilidagi hujjatlar talab etiladi.",
                            'link': f"https://www.ungm.org/Public/Notice/{nid}"
                        })
        except Exception as e:
            print(f"Error fetching live UNGM lots: {e}")
            
        return ungm_lots

    @classmethod
    def run_live_scan(
        cls,
        company_profile: Optional[Dict[str, Any]] = None,
        auto_notify: bool = False,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes a live multi-portal scan across UzEx and UNGM, parses real-time lots, 
        evaluates AI relevance, and caches for instant radar filtering."""
        try:
            from src.tender_ai.tender_finder import TenderFinder
        except ImportError:
            from tender_finder import TenderFinder
        profile = company_profile or DEFAULT_COMPANY_PROFILE

        # 1. Fetch real live state & corporate lots from UzEx Oracle API
        uzex_lots = cls.fetch_uzex_live_lots(limit=40)

        # 2. Fetch real live international NGO / UN notices from UNGM API
        ungm_lots = cls.fetch_ungm_live_lots(limit=25)

        live_lots = uzex_lots + ungm_lots

        # 3. If live APIs succeed, merge with curated benchmark lots
        if not live_lots:
            live_lots = cls.load_cached_tenders()
        else:
            cached_defaults = TenderFinder.DEFAULT_OPPORTUNITIES
            seen_ids = {l["lot_id"] for l in live_lots}
            for d in cached_defaults:
                if d["lot_id"] not in seen_ids and "UNGM-" not in d["lot_id"]:
                    live_lots.append(d)

        # Probe portals connectivity
        portal_status = cls.ping_portals()
        online_count = sum(1 for p in portal_status.values() if p["online"])

        # Timestamp for scanning
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Ingest, evaluate AI relevance and prepare notifications
        updated_list = []
        notified_count = 0

        for opp in live_lots:
            opp_copy = dict(opp)
            opp_copy["last_synced"] = now_str
            eval_res = TenderFinder.calculate_relevance(opp_copy, profile)
            opp_copy.update(eval_res)
            updated_list.append(opp_copy)

            if auto_notify and opp_copy.get("match_score", 0) >= 80:
                if bot_token and chat_id:
                    notif_res = TenderNotifier.send_telegram_alert(opp_copy, bot_token=bot_token, chat_id=chat_id)
                    if notif_res.get("success"):
                        notified_count += 1

        cls.save_cached_tenders(updated_list)

        return {
            "timestamp": now_str,
            "portals_checked": len(cls.PORTAL_URLS),
            "portals_online": online_count,
            "portal_status": portal_status,
            "total_lots": len(updated_list),
            "new_lots": len(live_lots),
            "notified_count": notified_count,
            "tenders": updated_list
        }

    @classmethod
    def start_background_scanner(cls, interval_hours: int = 4, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """Starts a recurring background daemon thread that scans 3-4 times a day."""
        if cls._scheduler_active:
            return "Avtomatik skanner allaqachon faol."

        cls._scheduler_active = True

        def worker():
            while cls._scheduler_active:
                try:
                    cls.run_live_scan(auto_notify=True, bot_token=bot_token, chat_id=chat_id)
                except Exception as e:
                    print(f"Background scan error: {e}")
                # Sleep interval in seconds
                time.sleep(max(1800, interval_hours * 3600))

        cls._background_thread = threading.Thread(target=worker, daemon=True)
        cls._background_thread.start()
        return f"Avtomatik skanner ishga tushdi (Har {interval_hours} soatda bir marta tekshiradi)."

    @classmethod
    def stop_background_scanner(cls):
        """Stops the recurring background scan."""
        cls._scheduler_active = False
        return "Avtomatik skanner to'xtatildi."
