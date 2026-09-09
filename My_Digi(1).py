import json, re, threading, webbrowser, sys, socket, uuid, zipfile, xml.sax.saxutils as sx, os, time, shutil
from datetime import datetime, date
from pathlib import Path
from urllib.request import Request, urlopen, build_opener, ProxyHandler
from urllib.error import HTTPError, URLError
from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font as tkfont
import math, random

# Windows taskbar identity: set this before any GUI/webview window is created.
# This prevents Windows from treating the window as a generic host/browser app.
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Mabouth.MyDigi")
    except Exception:
        pass

try:
    from PIL import Image, ImageTk, ImageGrab
except ImportError:
    Image = ImageTk = ImageGrab = None

APP_VERSION = "2.0.9"
UPDATE_REPO = "miladasgharibehruz/My-Digi"  # Built-in fallback; release builds may override this via update_config.json.
UPDATE_API_BASE = "https://api.github.com"
APP_DIR = Path(os.environ.get("APPDATA") or Path.home()) / "My Digi"
DATA_FILE = APP_DIR / "products.json"
REFERENCE_FILE = APP_DIR / "reference.json"
MARKET_TREND_FILE = APP_DIR / "market_trend.json"
REMINDER_STATE_FILE = APP_DIR / "reminder_state.json"
ACCOUNTING_FILE = APP_DIR / "accounting.json"
ACCOUNTING_REPORTS_FILE = APP_DIR / "accounting_reports.json"
ACCOUNTING_MONTH_TRACK_FILE = APP_DIR / "accounting_month_track.json"
SETTINGS_FILE = APP_DIR / "settings.json"
MONTHLY_REPORTS_FILE = APP_DIR / "monthly_reports.json"
MONTH_TRACK_FILE = APP_DIR / "monthly_track.json"
APP_DIR.mkdir(exist_ok=True)

# Digi Calc is bundled directly into the Python application.  The calculator
# is extracted to the user's application data folder on first use, so the
# program does not depend on a separate "Digi Calc.html" file beside the EXE.
_CALCULATOR_B64_GZIP = "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"
_CALCULATOR_FILE = APP_DIR / "Digi Calc.html"


DEFAULT_SETTINGS = {
    "digikala": {
        "processing_percent": 7.0,
        "processing_min": 36000,
        "processing_max": 240000,
        "label_cost": 6000,
        "default_commission": 15.0,
    },
    "display": {
        "trend_days": 30,
        "accounting_records": 6,
    },
    "accounting": {
        "default_range": "month",
    },
}

def load_settings():
    try:
        raw=json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        raw={}
    out=json.loads(json.dumps(DEFAULT_SETTINGS))
    if isinstance(raw,dict):
        for section,values in raw.items():
            if isinstance(values,dict) and isinstance(out.get(section),dict):
                out[section].update(values)
    return out

def save_settings(data):
    out=json.loads(json.dumps(DEFAULT_SETTINGS))
    if isinstance(data,dict):
        for section,values in data.items():
            if isinstance(values,dict) and isinstance(out.get(section),dict):
                out[section].update(values)
    d=out["digikala"]
    d["processing_percent"]=max(0.0,float(d.get("processing_percent",7) or 0))
    d["processing_min"]=max(0,int(float(d.get("processing_min",36000) or 0)))
    d["processing_max"]=max(d["processing_min"],int(float(d.get("processing_max",240000) or 0)))
    d["label_cost"]=max(0,int(float(d.get("label_cost",6000) or 0)))
    d["default_commission"]=max(0.0,float(d.get("default_commission",15) or 0))
    v=out["display"]
    v["trend_days"]=int(v.get("trend_days",30) or 30) if int(v.get("trend_days",30) or 30) in (7,30,90,180,365) else 30
    ar=v.get("accounting_records",6)
    v["accounting_records"]=ar if str(ar) in ("6","10","20","all") else 6
    a=out["accounting"]
    a["default_range"]=a.get("default_range","month") if a.get("default_range","month") in ("all","day","week","month","quarter","30d","6m","year") else "month"
    SETTINGS_FILE.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    return out


def load_products():
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        changed = False
        for item in data:
            if not isinstance(item, dict):
                continue
            if not item.get("uuid"):
                item["uuid"] = str(uuid.uuid4())
                changed = True
        if changed:
            try:
                save_products(data)
            except Exception:
                pass
        return data
    except Exception:
        return []


def save_products(items):
    DATA_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def load_reference():
    if not REFERENCE_FILE.exists():
        return {"suppliers": []}
    try:
        data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {"suppliers": []}
        data.setdefault("suppliers", [])
        return data
    except Exception:
        return {"suppliers": []}

def save_reference(data):
    REFERENCE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_market_trend():
    try:
        if not MARKET_TREND_FILE.exists():
            return []
        data = json.loads(MARKET_TREND_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_market_trend(data):
    MARKET_TREND_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def record_market_trend(net_change, increase_total, decrease_total, checked_count):
    try:
        history = load_market_trend()
        history.append({
            "timestamp": datetime.now().isoformat(),
            "increase_total": int(increase_total),
            "decrease_total": int(decrease_total),
            "net_change": int(net_change),
            "checked_count": int(checked_count),
        })
        del history[:-60]
        save_market_trend(history)
    except Exception:
        pass

def load_reminder_state():
    try:
        if not REMINDER_STATE_FILE.exists():
            return {}
        data = json.loads(REMINDER_STATE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_reminder_state(data):
    REMINDER_STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# --- Accounting helpers ---
def load_accounting():
    default = {
        "categories": [
            {"id": "cat_transport", "name": "هزینه حمل و نقل", "color": "#8b5cf6"},
            {"id": "cat_packaging", "name": "هزینه بسته بندی", "color": "#4f46e5"},
        ],
        "expenses": [],
        "profits": [],
        "monthly_archive": []
    }
    if not ACCOUNTING_FILE.exists():
        return default
    try:
        data = json.loads(ACCOUNTING_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return default
        for k, v in default.items():
            data.setdefault(k, v.copy() if isinstance(v, list) else v)
        return data
    except Exception:
        return default


def save_accounting(data):
    ACCOUNTING_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_accounting_reports():
    try:
        if not ACCOUNTING_REPORTS_FILE.exists():
            return []
        data=json.loads(ACCOUNTING_REPORTS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data,list) else []
    except Exception:
        return []


def save_accounting_reports(data):
    ACCOUNTING_REPORTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_accounting_month_track():
    try:
        if not ACCOUNTING_MONTH_TRACK_FILE.exists():
            return {}
        data=json.loads(ACCOUNTING_MONTH_TRACK_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data,dict) else {}
    except Exception:
        return {}


def save_accounting_month_track(data):
    ACCOUNTING_MONTH_TRACK_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _record_jalali_month_key(rec):
    ts=str(rec.get("timestamp") or "").strip()
    if ts:
        try:
            dt=datetime.fromisoformat(ts.replace("Z","+00:00"))
            if dt.tzinfo:
                dt=dt.astimezone().replace(tzinfo=None)
            jy,jm,jd=gregorian_to_jalali(dt.year,dt.month,dt.day)
            return f"{jy:04d}/{jm:02d}"
        except Exception:
            pass
    raw=str(rec.get("date") or "").strip().replace("-","/")
    raw=_fa_to_en_digits(raw)
    m=re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})",raw)
    return f"{int(m.group(1)):04d}/{int(m.group(2)):02d}" if m else None


def ensure_accounting_monthly_reports():
    data=load_accounting()
    jy,jm=current_jalali_month()
    if jy is None:
        return None, load_accounting_reports()
    current_key=f"{jy:04d}/{jm:02d}"
    track=load_accounting_month_track()
    notice=None
    if not track.get("month"):
        track={"month":current_key}
    elif track.get("month")!=current_key:
        old_key=str(track.get("month"))
        reports=load_accounting_reports()
        expenses=[x for x in data.get("expenses",[]) if _record_jalali_month_key(x)==old_key]
        profits=[x for x in data.get("profits",[]) if _record_jalali_month_key(x)==old_key]
        total_exp=sum(int(x.get("amount",0) or 0) for x in expenses)
        total_profit=sum(int(x.get("total_profit",x.get("total",0)) or 0) for x in profits)
        qty=sum(int(x.get("qty",0) or 0) for x in profits)
        oy,om=map(int,old_key.split("/"))
        cat_map={str(c.get("id")):c for c in data.get("categories",[])}
        exp_break={}
        for e in expenses:
            name=e.get("category_name") or cat_map.get(str(e.get("category_id")),{}).get("name") or "بدون دسته"
            exp_break[name]=exp_break.get(name,0)+int(e.get("amount",0) or 0)
        prod={}
        for r in profits:
            name=r.get("product_name") or "محصول"
            rec=prod.setdefault(name,{"product_name":name,"qty":0,"profit":0})
            rec["qty"]+=int(r.get("qty",0) or 0); rec["profit"]+=int(r.get("total_profit",r.get("total",0)) or 0)
        report={"month":old_key,"title":_month_title(oy,om),"total_profit":total_profit,"total_expense":total_exp,"net_profit":total_profit-total_exp,"sales_qty":qty,"transaction_count":len(expenses)+len(profits),"expense_breakdown":[{"name":k,"amount":v} for k,v in sorted(exp_break.items())],"product_breakdown":list(prod.values())}
        reports=[r for r in reports if str(r.get("month"))!=old_key]
        reports.append(report); reports.sort(key=lambda r:str(r.get("month","")),reverse=True); save_accounting_reports(reports)
        notice=f"گزارش حسابداری {report['title']} ثبت شد"
        track={"month":current_key}
    track["month"]=current_key
    save_accounting_month_track(track)
    return notice, load_accounting_reports()


def _accounting_number(value):
    text = str(value or "").translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
    text = text.replace(",", "").replace("٬", "").replace(" ", "")
    return int(float(text))

def money_text(v):
    try:
        return f"{int(v):,}"
    except Exception:
        return "—"

# --- Persian/Jalali calendar helpers (dependency-free) ---
def _fa_to_en_digits(value):
    return str(value or "").translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))

def jalali_to_gregorian(jy, jm, jd):
    jy += 1595
    days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33 + 3) // 4) + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += (jm - 7) * 30 + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    while gd > month_days[gm - 1]:
        gd -= month_days[gm - 1]
        gm += 1
    return date(gy, gm, gd)

def gregorian_to_jalali(gy, gm, gd):
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gy -= 1600; gm -= 1; gd -= 1
    g_day_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    for i in range(gm):
        g_day_no += g_days_in_month[i]
    if gm > 1 and ((gy + 1600) % 4 == 0 and ((gy + 1600) % 100 != 0 or (gy + 1600) % 400 == 0)):
        g_day_no += 1
    g_day_no += gd
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        jm = 7 + (j_day_no - 186) // 30
        jd = 1 + (j_day_no - 186) % 30
    return jy, jm, jd

def today_jalali_text():
    jy, jm, jd = gregorian_to_jalali(date.today().year, date.today().month, date.today().day)
    return f"{jy:04d}/{jm:02d}/{jd:02d}"

def jalali_timestamp_text(dt=None):
    dt = dt or datetime.now()
    jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
    return f"{jy:04d}/{jm:02d}/{jd:02d} {dt:%H:%M}"

def today_text():
    # Historical records keep the original timestamp format for compatibility.
    return datetime.now().strftime("%Y-%m-%d")

def parse_reminder_date(value):
    raw = _fa_to_en_digits(str(value or "").strip()).replace("-", "/").replace(".", "/")
    m = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", raw)
    if not m:
        return None
    y, mo, d = map(int, m.groups())
    try:
        if y >= 1700:
            return date(y, mo, d)
        if not (1 <= mo <= 12 and 1 <= d <= 31):
            return None
        g = jalali_to_gregorian(y, mo, d)
        if gregorian_to_jalali(g.year, g.month, g.day) != (y, mo, d):
            return None
        return g
    except ValueError:
        return None

def normalize_reminder_for_edit(value):
    raw = _fa_to_en_digits(str(value or "").strip()).replace("-", "/").replace(".", "/")
    m = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", raw)
    if not m:
        return raw
    y, mo, d = map(int, m.groups())
    if y >= 1700:
        try:
            jy, jm, jd = gregorian_to_jalali(y, mo, d)
            return f"{jy:04d}/{jm:02d}/{jd:02d}"
        except ValueError:
            return raw
    return f"{y:04d}/{mo:02d}/{d:02d}"

def normalize_text(value):
    value = str(value or "").strip().lower()
    return value.translate(str.maketrans({"ي":"ی", "ى":"ی", "ك":"ک", "ۀ":"ه", "ة":"ه"}))

def parse_tiers(text):
    tiers = []
    for chunk in str(text or "").split(","):
        chunk = chunk.strip()
        if not chunk or ":" not in chunk:
            continue
        q, pr = chunk.split(":", 1)
        try:
            tiers.append({"qty": int(q.strip()), "price": int(pr.replace(",", "").strip())})
        except Exception:
            pass
    return sorted(tiers, key=lambda x: x["qty"])

def tiers_text(tiers):
    return ", ".join(f'{t.get("qty", 1)}:{money_text(t.get("price", 0))}' for t in (tiers or []))

def extract_id(url):
    cleaned = str(url).strip()
    m = re.search(r"(?:https?://)?(?:www\.)?digikala\.com/product/dkp-(\d+)", cleaned, re.I)
    if not m:
        m = re.search(r"dkp-(\d+)", cleaned, re.I)
    return m.group(1) if m else None


def first_image_url(obj):
    """Extract a real Digikala product image from the known image shapes.

    Digikala has used more than one image shape across product-detail
    responses.  Prefer product images only; never pick arbitrary UI/icon URLs.
    """
    if not isinstance(obj, dict):
        return None

    def url_from_value(value):
        if isinstance(value, str):
            value = value.strip()
            return value if value.startswith(("http://", "https://")) else None
        if isinstance(value, (list, tuple)):
            for v in value:
                found = url_from_value(v)
                if found:
                    return found
        if isinstance(value, dict):
            # Common image object forms.
            for k in ("url", "webp_url", "image_url", "imageUrl", "src", "source"):
                found = url_from_value(value.get(k))
                if found:
                    return found
        return None

    images = obj.get("images")
    if isinstance(images, dict):
        # Current/common product-detail shape.
        for key in ("main", "main_images", "images", "image"):
            found = url_from_value(images.get(key))
            if found:
                return found
        # Some responses put the URL directly under images.
        for key in ("url", "webp_url", "image_url", "imageUrl"):
            found = url_from_value(images.get(key))
            if found:
                return found
    else:
        found = url_from_value(images)
        if found:
            return found

    # Some Digikala wrappers expose the primary image directly.
    for key in ("image_url", "imageUrl", "main_image", "main_image_url", "primary_image_url"):
        found = url_from_value(obj.get(key))
        if found:
            return found

    return None


def fetch_product(product_id):
    api = f"https://api.digikala.com/v2/product/{product_id}/"
    req = Request(api, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
        "Referer": "https://www.digikala.com/",
    })
    try:
        with urlopen(req, timeout=20) as r:
            status_code = getattr(r, "status", 200)
            raw = r.read()
        if status_code >= 400:
            raise RuntimeError(f"خطای HTTP {status_code} در دریافت اطلاعات دیجی‌کالا.")
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("پاسخ دریافتی از دیجی‌کالا قابل خواندن نیست.") from exc
    except HTTPError as exc:
        if exc.code == 404:
            raise RuntimeError("محصول دیجی‌کالا پیدا نشد (404).") from exc
        if exc.code == 403:
            raise RuntimeError("دسترسی به اطلاعات دیجی‌کالا رد شد (403).") from exc
        if exc.code == 429:
            raise RuntimeError("درخواست‌های زیادی ارسال شده است (429). چند لحظه صبر کنید و دوباره امتحان کنید.") from exc
        raise RuntimeError(f"خطای HTTP {exc.code} هنگام دریافت محصول.") from exc
    except (URLError, socket.timeout, TimeoutError) as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(f"خطای اتصال به اینترنت/دیجی‌کالا: {reason}") from exc

    if not isinstance(data, dict):
        raise RuntimeError("ساختار پاسخ دیجی‌کالا معتبر نیست.")

    root = data.get("data", data)
    if not isinstance(root, dict):
        raise RuntimeError("بخش data پاسخ دیجی‌کالا معتبر نیست.")
    product = root.get("product", root)
    if not isinstance(product, dict):
        raise RuntimeError("اطلاعات محصول در پاسخ دیجی‌کالا پیدا نشد.")

    def first_text(*values):
        for value in values:
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    # Product title must come from the product-level metadata, not from a
    # seller/variant title.  Keep a few known fallback shapes for API changes.
    seo = product.get("seo") if isinstance(product.get("seo"), dict) else {}
    title = first_text(
        product.get("title_fa"), product.get("title"), product.get("name_fa"),
        product.get("name"), seo.get("title"), seo.get("title_fa")
    )
    if not title:
        raise RuntimeError("نام واقعی محصول در پاسخ دیجی‌کالا پیدا نشد.")

    image_url = first_image_url(product)

    def number_value(value):
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return int(value) if value > 0 else None
        if isinstance(value, str):
            trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
            text = value.translate(trans).replace(",", "").replace("٬", "").replace(" ", "")
            m = re.search(r"\d+", text)
            if m:
                n = int(m.group())
                return n if n > 0 else None
        return None

    def get_seller_info(obj):
        if isinstance(obj, str) and obj.strip():
            return obj.strip(), None
        if not isinstance(obj, dict):
            return None, None
        seller_id = obj.get("id") or obj.get("seller_id") or obj.get("sellerId")
        for key in ("title", "name", "title_fa", "name_fa", "seller_name", "sellerName"):
            value = obj.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip(), seller_id
        return None, seller_id

    def get_selling_price(obj):
        if not isinstance(obj, dict):
            return None
        candidates = []
        price_obj = obj.get("price")
        if isinstance(price_obj, dict):
            candidates.extend([
                price_obj.get("selling_price"), price_obj.get("sellingPrice"),
                price_obj.get("final_price"), price_obj.get("finalPrice"),
                price_obj.get("sale_price"), price_obj.get("salePrice"),
                price_obj.get("discounted_price"), price_obj.get("discountedPrice"),
            ])
        candidates.extend([
            obj.get("selling_price"), obj.get("sellingPrice"),
            obj.get("final_price"), obj.get("finalPrice"),
            obj.get("sale_price"), obj.get("salePrice"),
            obj.get("discounted_price"), obj.get("discountedPrice"),
        ])
        for value in candidates:
            if isinstance(value, dict):
                value = value.get("value") or value.get("amount") or value.get("price")
            n = number_value(value)
            if n is not None:
                return n
        return None

    # First use the documented/current product variant structure.  Product
    # detail wrappers expose seller + price on variants; this is much safer
    # than treating every nested {seller, price} pair as an independent offer.
    variants = product.get("variants")
    if isinstance(variants, dict):
        for key in ("items", "data", "variants", "results"):
            if isinstance(variants.get(key), list):
                variants = variants[key]
                break
    if not isinstance(variants, list):
        variants = []

    offers = []
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        seller_obj = variant.get("seller")
        seller, seller_id = get_seller_info(seller_obj)
        raw = get_selling_price(variant)
        if raw is not None and seller:
            offers.append((raw, seller, seller_id))

    # Fallback: recursively inspect only when the explicit variants structure
    # did not yield offers.  This keeps compatibility with older responses.
    if not offers:
        def collect_legacy(obj):
            if isinstance(obj, dict):
                seller, seller_id = get_seller_info(obj.get("seller"))
                raw = get_selling_price(obj)
                if raw is not None and seller:
                    offers.append((raw, seller, seller_id))
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        collect_legacy(value)
            elif isinstance(obj, list):
                for value in obj:
                    collect_legacy(value)
        collect_legacy(product)

    # Default variant is a valid fallback for the current price, but it must
    # not be interpreted as proof that the product has only one seller.
    if not offers:
        default_variant = product.get("default_variant")
        if isinstance(default_variant, dict):
            raw = get_selling_price(default_variant)
            seller, seller_id = get_seller_info(default_variant.get("seller"))
            if raw is not None:
                offers.append((raw, seller or "—", seller_id))

    # Deduplicate by seller ID/name and retain each seller's cheapest offer.
    best_by_seller = {}
    anonymous = []
    for raw, seller, seller_id in offers:
        if raw < 1000:
            continue
        if seller_id is not None:
            key = ("id", str(seller_id))
        else:
            key = ("name", normalize_text(seller))
        if key[1]:
            prev = best_by_seller.get(key)
            if prev is None or raw < prev[0]:
                best_by_seller[key] = (raw, seller)
        else:
            anonymous.append((raw, seller))

    unique = list(best_by_seller.values()) + anonymous
    ranked = sorted(unique, key=lambda x: x[0])

    # Determine availability independently from seller count.
    status = str(product.get("status") or "").lower()
    default_variant = product.get("default_variant") if isinstance(product.get("default_variant"), dict) else {}
    variant_status = str(default_variant.get("status") or "").lower()
    is_marketable = status in ("marketable", "available", "active") or variant_status in ("marketable", "available", "active")
    unavailable = not bool(ranked) and not is_marketable

    if not ranked:
        # Preserve the real title and image even when price/seller data is absent.
        return title, None, None, None, None, unavailable, image_url

    best_raw, best_seller = ranked[0]
    second_raw, second_seller = ranked[1] if len(ranked) > 1 else (None, None)
    price = best_raw // 10 if best_raw >= 10000 else best_raw
    second_price = second_raw // 10 if second_raw is not None and second_raw >= 10000 else second_raw

    return (
        title,
        int(price),
        best_seller or "—",
        int(second_price) if second_price is not None else None,
        second_seller or "—",
        False,
        image_url,
    )


def processing_cost(price):
    cfg=load_settings().get("digikala",{})
    pct=max(0.0,float(cfg.get("processing_percent",7) or 0))/100.0
    minimum=max(0,int(float(cfg.get("processing_min",36000) or 0)))
    maximum=max(minimum,int(float(cfg.get("processing_max",240000) or 0)))
    return min(maximum,max(minimum,round(price*pct)))


def my_price_inputs_ready(item):
    """Return True only when purchase, profit and commission have been entered.
    Ancillary cost is optional and defaults to zero.
    """
    purchase = item.get("purchase")
    profit = item.get("profit")
    commission = item.get("commission")
    if purchase in (None, "", 0) or profit in (None, "") or commission in (None, ""):
        return False
    try:
        return float(purchase) > 0 and float(profit) >= 0 and float(commission) >= 0
    except (TypeError, ValueError):
        return False


def digikala_my_price(purchase, profit, commission_percent, ancillary=0):
    """Find the smallest listing price whose net payout covers purchase+profit+ancillary.
    Commission and VAT are percentages of the listing price; processing is capped/floored.
    """
    target = max(0, purchase + profit + ancillary)
    rate = max(0.0, float(commission_percent or 0)) / 100.0

    def net(price):
        commission = price * rate
        processing = processing_cost(price)
        vat = (commission + processing) * 0.10
        label = max(0,int(float(load_settings().get("digikala",{}).get("label_cost",6000) or 0)))
        return price - commission - processing - vat - label

    # Monotonic in the relevant range; binary-search to the nearest تومان.
    lo, hi = 0, max(1_000_000, int(target * 2 + 500_000))
    while net(hi) < target:
        hi *= 2
        if hi > 10_000_000_000:
            return None
    while lo < hi:
        mid = (lo + hi) // 2
        if net(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


# --- Portable XLSX export helper (no Microsoft Excel dependency) ---
def _xlsx_col_letter(n):
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def _xlsx_cell(ref, value, style=None):
    if value is None:
        return ""
    if isinstance(value, bool):
        return f'<c r="{ref}" t="b"><v>{1 if value else 0}</v></c>'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"><v>{value}</v></c>'
    s = sx.escape(str(value))
    st = f' s="{style}"' if style is not None else ''
    return f'<c r="{ref}" t="inlineStr"{st}><is><t xml:space="preserve">{s}</t></is></c>'


def write_products_xlsx(items, filepath, best_supplier_resolver=None, all_supplier_resolver=None):
    headers = ["ردیف","نام کالا","شناسه محصول دیجی‌کالا","لینک دیجی‌کالا","کمترین قیمت دیجی‌کالا","فروشنده کمترین قیمت","دومین قیمت","فروشنده دوم","تغییر وضعیت","آخرین بررسی","قیمت خرید","سود","هزینه جانبی","کمیسیون٪","قیمت من","قیمت دیجی‌کالای من","بهترین تأمین‌کننده","قیمت بهترین تأمین‌کننده","همه تأمین‌کنندگان مرتبط","وضعیت محصول","UUID داخلی"]
    rows=[headers]
    for idx,item in enumerate(items,1):
        purchase=item.get("purchase"); profit=item.get("profit"); ancillary=item.get("ancillary",0) or 0; commission=item.get("commission")
        mine=digikala_my_price(purchase,profit,commission,ancillary) if my_price_inputs_ready(item) else None
        best=best_supplier_resolver(item) if best_supplier_resolver else None
        names=[]
        if all_supplier_resolver:
            try: names=[x[1] for x in all_supplier_resolver(item)]
            except Exception: pass
        rows.append([idx,item.get("custom_title") or item.get("title",""),item.get("id") or item.get("product_id") or "",item.get("url",""),item.get("price"),item.get("seller",""),item.get("second_price"),item.get("second_seller",""),item.get("status",""),item.get("checked",""),purchase,profit,ancillary,commission,(purchase+profit if purchase is not None and profit is not None else None),mine,best[1] if best else "",best[0] if best else None,"، ".join(dict.fromkeys(names)),item.get("status",""),item.get("uuid","")])
    xml_rows=[]
    for r,row in enumerate(rows,1):
        xml_rows.append(f'<row r="{r}">' + ''.join(_xlsx_cell(f"{_xlsx_col_letter(c)}{r}",v,1 if r==1 else None) for c,v in enumerate(row,1)) + '</row>')
    widths=[8,34,18,48,18,24,18,24,20,20,16,16,16,12,16,20,24,22,34,22,38]
    cols=''.join(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>' for i,w in enumerate(widths,1))
    maxc=len(headers); maxr=len(rows)
    sheet_xml='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0" rightToLeft="1"><pane xSplit="0" ySplit="1" topLeftCell="A2" activePane="bottomRight" state="frozen"/><selection pane="bottomRight" activeCell="A2" sqref="A2"/></sheetView></sheetViews><cols>COLS</cols><sheetData>ROWS</sheetData><autoFilter ref="A1:ENDCOLENDROW"/></worksheet>'''.replace('COLS',cols).replace('ROWS',''.join(xml_rows)).replace('ENDCOL',_xlsx_col_letter(maxc)).replace('ENDROW',str(maxr))
    styles='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Segoe UI"/></font><font><b/><sz val="11"/><name val="Segoe UI"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" applyFont="1"/></cellXfs></styleSheet>'''
    workbook='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="محصولات مانیتور" sheetId="1" r:id="rId1"/></sheets></workbook>'''
    rels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    rootrels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'''
    types='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>'''
    filepath=Path(filepath); filepath.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(filepath,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',types); z.writestr('_rels/.rels',rootrels); z.writestr('xl/workbook.xml',workbook); z.writestr('xl/_rels/workbook.xml.rels',rels); z.writestr('xl/styles.xml',styles); z.writestr('xl/worksheets/sheet1.xml',sheet_xml)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("My Digi")
        self.root.geometry("1500x880")
        self.root.minsize(1180, 720)
        self.items = load_products()
        for _item in self.items:
            _item.setdefault("selected", False)
        self._migrate_reference_monitor_links()
        self.running = True
        self.row_images = {}
        self.image_cache = {}
        self.page_size = 10
        self.current_page = 1
        self.total_pages = 1
        self._pending_save = None
        self.unsaved_changes = False
        self.dark_mode = True
        self.selected_index = None
        self.reference_window = None
        self._ambient_phase = 0
        self._ambient_nodes = []

        self.root.bind_all("<KeyPress>", self._handle_edit_shortcut, add="+")
        self.root.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self._on_mousewheel_linux, add="+")
        self.root.bind_all("<Button-5>", self._on_mousewheel_linux, add="+")

        families = set(tkfont.families(self.root))
        self.ui_family = "Vazirmatn" if "Vazirmatn" in families else "Segoe UI"
        self.root.option_add("*Font", f"{{{self.ui_family}}} 9")
        self._modern_palette = {
            "bg":"#050A15", "panel":"#0B1426", "panel2":"#101C31", "panel3":"#0A1222",
            "border":"#203959", "text":"#EAF2FF", "muted":"#8299B6", "cyan":"#25D7FF",
            "blue":"#4D7CFF", "purple":"#A45CFF", "green":"#19D69A", "red":"#FF4C78",
            "gold":"#FFC857", "teal":"#2BD9C1"
        }
        self._light_palette = {
            "bg":"#EEF3FA", "panel":"#FFFFFF", "panel2":"#F4F7FC", "panel3":"#E9EEF7",
            "border":"#D3DDEC", "text":"#132033", "muted":"#62728A", "cyan":"#108CC8",
            "blue":"#466BEA", "purple":"#7F4CEB", "green":"#0A9A76", "red":"#D93664",
            "gold":"#C58A13", "teal":"#159E8C"
        }
        self._build_modern_ui()
        self.refresh()
        self.root.after(450, self.check_reference_reminders)
        self.root.after(80, self._animate_ambient)

    def _build_modern_ui(self):
        c=self._modern_palette if self.dark_mode else self._light_palette
        self.root.configure(bg=c["bg"])
        self.style = ttk.Style(self.root)
        try: self.style.theme_use("clam")
        except Exception: pass
        self.style.configure("Modern.TButton", font=(self.ui_family,9,"bold"), padding=(10,6), background=c["panel2"], foreground=c["text"], borderwidth=0)
        self.style.map("Modern.TButton", background=[("active",c["blue"])], foreground=[("active","white")])
        self.style.configure("Modern.TLabel", background=c["bg"], foreground=c["text"], font=(self.ui_family,9))
        self.style.configure("Modern.Treeview", background=c["panel"], fieldbackground=c["panel"], foreground=c["text"], rowheight=30)

        # ambient canvas behind the interface; side/background surfaces show subtle motion
        self.ambient = tk.Canvas(self.root, bg=c["bg"], highlightthickness=0, bd=0)
        self.ambient.place(relx=0,rely=0,relwidth=1,relheight=1)
        random.seed(7)
        self._ambient_nodes=[]
        for _ in range(28):
            self._ambient_nodes.append({
                "x":random.random(), "y":random.random(), "r":random.randint(10,34),
                "vx":random.uniform(-0.00035,0.00035), "vy":random.uniform(-0.00025,0.00025),
                "kind":random.choice(("cyan","purple","blue"))
            })

        root_frame=tk.Frame(self.root,bg=c["bg"],highlightthickness=0)
        root_frame.place(relx=0,rely=0,relwidth=1,relheight=1)

        # TOP BAR
        top=tk.Frame(root_frame,bg=c["panel3"],height=54,highlightthickness=1,highlightbackground=c["border"])
        top.pack(fill="x",padx=12,pady=(10,6)); top.pack_propagate(False)
        brand=tk.Frame(top,bg=c["panel3"]); brand.pack(side="left",fill="y",padx=12)
        tk.Label(brand,text="✦",font=(self.ui_family,20,"bold"),bg=c["panel3"],fg=c["cyan"]).pack(side="left",padx=(0,8))
        tk.Label(brand,text="My Digi",font=(self.ui_family,15,"bold"),bg=c["panel3"],fg=c["text"]).pack(side="left")
        tk.Label(brand,text=APP_VERSION,font=(self.ui_family,9,"bold"),bg=c["panel3"],fg=c["blue"]).pack(side="left",padx=6)
        self.top_hint=tk.Label(top,text="مدیریت هوشمند کسب‌وکار و پایش قیمت",font=(self.ui_family,9),bg=c["panel3"],fg=c["muted"])
        self.top_hint.pack(side="left",padx=15)

        actions=tk.Frame(top,bg=c["panel3"]); actions.pack(side="right",fill="y",padx=8)
        self.search_var=tk.StringVar()
        self.search_entry=tk.Entry(actions,textvariable=self.search_var,justify="right",font=(self.ui_family,9),
                                   bg=c["panel"],fg=c["text"],insertbackground=c["text"],relief="flat",highlightthickness=1,
                                   highlightbackground=c["border"],highlightcolor=c["cyan"])
        self.search_entry.pack(side="right",fill="y",ipady=7,padx=(8,4),pady=7)
        self.search_entry.configure(width=34)
        self.search_entry.insert(0,"")
        self.search_entry.bind("<KeyRelease>",self._on_search); self.search_entry.bind("<Escape>",self._clear_search)
        tk.Label(actions,text="⌕",bg=c["panel3"],fg=c["cyan"],font=(self.ui_family,16)).pack(side="right")
        for txt,cmd,fg in (("🔔",lambda:self.open_today_dashboard,c["gold"]),("▣",self.open_accounting,c["purple"]),("↻",self.check_all,c["cyan"])):
            b=tk.Button(actions,text=txt,command=cmd,bd=0,relief="flat",bg=c["panel2"],fg=fg,activebackground=c["blue"],activeforeground="white",font=(self.ui_family,12,"bold"),width=3,cursor="hand2")
            b.pack(side="right",padx=3,pady=7)

        # KPI cards — real monitor data
        kpi_row=tk.Frame(root_frame,bg=c["bg"]); kpi_row.pack(fill="x",padx=12,pady=(0,8))
        self.kpi_vars={}
        kpis=[("قیمت کل مانیتور","market",c["cyan"]),("کالاهای مانیتور","count",c["blue"]),("کاهش قیمت","down",c["green"]),("افزایش قیمت","up",c["red"]),("کالاهای جدید","new",c["gold"])]
        for title,key,accent in kpis:
            card=tk.Frame(kpi_row,bg=c["panel"],highlightthickness=1,highlightbackground=c["border"],height=78)
            card.pack(side="right",fill="both",expand=True,padx=4); card.pack_propagate(False)
            tk.Frame(card,bg=accent,height=2).pack(fill="x")
            topc=tk.Frame(card,bg=c["panel"]); topc.pack(fill="x",padx=10,pady=(8,0))
            tk.Label(topc,text=title,bg=c["panel"],fg=c["muted"],font=(self.ui_family,8,"bold")).pack(side="right")
            var=tk.StringVar(value="0"); self.kpi_vars[key]=var
            tk.Label(card,textvariable=var,bg=c["panel"],fg=accent,font=(self.ui_family,15,"bold"),anchor="e").pack(fill="x",padx=10,pady=(5,0))

        # MAIN BODY
        body=tk.Frame(root_frame,bg=c["bg"]); body.pack(fill="both",expand=True,padx=12,pady=(0,6))

        # LEFT SIDEBAR
        left=tk.Frame(body,bg=c["panel3"],width=248,highlightthickness=1,highlightbackground=c["border"])
        left.pack(side="left",fill="y",padx=(0,7)); left.pack_propagate(False)
        self._side_nav(left,c)
        self._side_filters(left,c)

        # RIGHT ANALYTICS
        right=tk.Frame(body,bg=c["panel3"],width=315,highlightthickness=1,highlightbackground=c["border"])
        right.pack(side="right",fill="y",padx=(7,0)); right.pack_propagate(False)
        self._analytics_sidebar(right,c)

        # CENTER MONITOR
        center=tk.Frame(body,bg=c["panel3"],highlightthickness=1,highlightbackground=c["border"])
        center.pack(side="left",fill="both",expand=True)

        monitor_head=tk.Frame(center,bg=c["panel3"],height=68); monitor_head.pack(fill="x",padx=10,pady=8); monitor_head.pack_propagate(False)
        icon_box=tk.Frame(monitor_head,bg=c["blue"],width=48,height=48); icon_box.pack(side="right",padx=(0,10),pady=8); icon_box.pack_propagate(False)
        tk.Label(icon_box,text="▣",bg=c["blue"],fg="white",font=(self.ui_family,20,"bold")).pack(expand=True)
        info=tk.Frame(monitor_head,bg=c["panel3"]); info.pack(side="right",fill="both",expand=True)
        tk.Label(info,text="مانیتور محصولات دیجی‌کالا",bg=c["panel3"],fg=c["text"],font=(self.ui_family,13,"bold"),anchor="e").pack(fill="x")
        tk.Label(info,text="مشاهده، مقایسه و مدیریت قیمت و وضعیت کالاهای شما",bg=c["panel3"],fg=c["muted"],font=(self.ui_family,8),anchor="e").pack(fill="x",pady=(3,0))
        # controls: add product, paste, calculator, supplier
        ctl=tk.Frame(monitor_head,bg=c["panel3"]); ctl.pack(side="left",fill="y")
        for text,cmd,accent in (("افزودن کالا",self.add,c["blue"]),("چسباندن",self.paste_from_clipboard,c["cyan"]),("مرجع من",self.open_reference,c["purple"]),("ماشین حساب",self.open_calculator,c["teal"]),("حسابداری",self.open_accounting,c["gold"])):
            b=tk.Button(ctl,text=text,command=cmd,bd=0,relief="flat",bg=accent,fg="white",activebackground=c["text"],activeforeground=c["bg"],font=(self.ui_family,8,"bold"),cursor="hand2")
            b.pack(side="left",padx=3,pady=15,ipadx=5)

        # add/search row: actual URL field kept because add() uses it
        addrow=tk.Frame(center,bg=c["panel2"],height=46,highlightthickness=1,highlightbackground=c["border"])
        addrow.pack(fill="x",padx=10); addrow.pack_propagate(False)
        tk.Label(addrow,text="لینک محصول",bg=c["panel2"],fg=c["muted"],font=(self.ui_family,8,"bold")).pack(side="right",padx=8)
        self.url=tk.Entry(addrow,justify="left",font=(self.ui_family,9),bg=c["panel"],fg=c["text"],insertbackground=c["text"],relief="flat",highlightthickness=1,highlightbackground=c["border"])
        self.url.pack(side="right",fill="x",expand=True,ipady=5,padx=4,pady=6)
        self.url.bind("<Shift-Insert>",self._paste_event); self.url.bind("<Return>",lambda e:self.add())
        self.paste_btn=tk.Button(addrow,text="📋",command=self.paste_from_clipboard,bd=0,bg=c["panel2"],fg=c["cyan"],font=(self.ui_family,12),activebackground=c["panel2"]); self.paste_btn.pack(side="left",padx=8)
        self.add_btn=tk.Button(addrow,text="➕ افزودن",command=self.add,bd=0,bg=c["blue"],fg="white",font=(self.ui_family,8,"bold"),activebackground=c["cyan"],activeforeground=c["bg"],cursor="hand2"); self.add_btn.pack(side="left",padx=5,ipadx=7)

        toolbar=tk.Frame(center,bg=c["panel3"],height=42); toolbar.pack(fill="x",padx=10,pady=(6,4)); toolbar.pack_propagate(False)
        tk.Label(toolbar,text="فهرست محصولات",bg=c["panel3"],fg=c["text"],font=(self.ui_family,9,"bold")).pack(side="right",padx=6)
        self.dark_btn=tk.Button(toolbar,text="☀ حالت روشن",command=self.toggle_dark_mode,bd=0,bg=c["panel2"],fg=c["gold"],font=(self.ui_family,8,"bold"),activebackground=c["panel2"]); self.dark_btn.pack(side="left",padx=3)
        for text,cmd in (("💾 ذخیره",self.save_now),("🗑 حذف انتخاب‌شده",self.remove_selected)):
            tk.Button(toolbar,text=text,command=cmd,bd=0,bg=c["panel2"],fg=c["muted"],font=(self.ui_family,8,"bold"),activebackground=c["blue"],activeforeground="white").pack(side="left",padx=3)
        self.info=tk.Label(toolbar,text="آماده",bg=c["panel3"],fg=c["muted"],font=(self.ui_family,8)); self.info.pack(side="left",padx=10)

        # Scrollable custom table, preserving the real implementation
        table=tk.Frame(center,bg=c["panel3"]); table.pack(fill="both",expand=True,padx=10,pady=(0,7))
        self.canvas=tk.Canvas(table,background=c["panel"],highlightthickness=0,bd=0)
        self.vbar=ttk.Scrollbar(table,orient="vertical",command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)
        self.vbar.pack(side="left",fill="y")
        self.canvas.pack(side="right",fill="both",expand=True)
        self.rows_frame=ttk.Frame(self.canvas)
        self.canvas_window=self.canvas.create_window((0,0),window=self.rows_frame,anchor="nw")
        self.rows_frame.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",self._resize_table)

        # BOTTOM: pager + online + monitoring + version only
        bottom=tk.Frame(root_frame,bg=c["panel3"],height=38,highlightthickness=1,highlightbackground=c["border"]); bottom.pack(fill="x",padx=12,pady=(0,10)); bottom.pack_propagate(False)
        self.version_label=tk.Label(bottom,text=f"My Digi {APP_VERSION}",bg=c["panel3"],fg=c["muted"],font=(self.ui_family,8,"bold")); self.version_label.pack(side="left",padx=10)
        statusf=tk.Frame(bottom,bg=c["panel3"]); statusf.pack(side="left",fill="y")
        tk.Label(statusf,text="●",bg=c["panel3"],fg=c["green"],font=(self.ui_family,9)).pack(side="left",padx=(8,2))
        tk.Label(statusf,text="متصل به سیستم",bg=c["panel3"],fg=c["muted"],font=(self.ui_family,8)).pack(side="left")
        self.progress_label=tk.Label(bottom,text="پایش: 0 / 0",bg=c["panel3"],fg=c["muted"],font=(self.ui_family,8)); self.progress_label.pack(side="right",padx=12)
        self.prev_page_btn=tk.Button(bottom,text="‹",command=self._prev_page,bd=0,bg=c["panel2"],fg=c["text"],font=(self.ui_family,10,"bold"),width=3); self.prev_page_btn.pack(side="right",padx=2)
        self.page_label=tk.Label(bottom,text="1 / 1",bg=c["panel3"],fg=c["text"],font=(self.ui_family,8,"bold")); self.page_label.pack(side="right",padx=6)
        self.next_page_btn=tk.Button(bottom,text="›",command=self._next_page,bd=0,bg=c["panel2"],fg=c["text"],font=(self.ui_family,10,"bold"),width=3); self.next_page_btn.pack(side="right",padx=2)

    def _side_nav(self,parent,c):
        brand=tk.Frame(parent,bg=c["panel3"],height=92); brand.pack(fill="x",padx=8,pady=8); brand.pack_propagate(False)
        tk.Label(brand,text="My Digi",bg=c["panel3"],fg=c["text"],font=(self.ui_family,13,"bold")).pack(anchor="e",padx=10,pady=(10,0))
        tk.Label(brand,text="دستیار هوشمند فروش آنلاین",bg=c["panel3"],fg=c["muted"],font=(self.ui_family,7)).pack(anchor="e",padx=10,pady=(2,0))
        nav=[("⌂", "خانه", lambda:None),("▣","محصولات",lambda:None),("▤","مانیتور",lambda:None),("◈","مرجع من",self.open_reference),("◫","کارهای امروز",self.open_today_dashboard),("⌘","حسابداری",self.open_accounting),("▥","گزارش‌ها",lambda:None),("⚙","تنظیمات",lambda:None)]
        for icon,title,cmd in nav:
            active=(title=="مانیتور")
            b=tk.Button(parent,text=f"{icon}   {title}",command=cmd,anchor="e",bd=0,relief="flat",bg=c["blue"] if active else c["panel3"],fg="white" if active else c["text"],activebackground=c["purple"],activeforeground="white",font=(self.ui_family,9,"bold"),cursor="hand2")
            b.pack(fill="x",padx=8,pady=2,ipady=7)
        sep=tk.Frame(parent,bg=c["border"],height=1); sep.pack(fill="x",padx=14,pady=10)

    def _side_filters(self,parent,c):
        box=tk.Frame(parent,bg=c["panel"],highlightthickness=1,highlightbackground=c["border"]); box.pack(fill="x",padx=9,pady=(0,8))
        tk.Label(box,text="فیلترها و جستجو",bg=c["panel"],fg=c["text"],font=(self.ui_family,10,"bold")).pack(anchor="e",padx=10,pady=(10,7))
        for text in ("همه دسته‌ها","همه وضعیت‌ها","بدون محدودیت قیمت"):
            tk.Button(box,text=text+"  ˅",bd=0,bg=c["panel2"],fg=c["muted"],activebackground=c["border"],font=(self.ui_family,8),anchor="e").pack(fill="x",padx=10,pady=4,ipady=5)
        tk.Button(box,text="اعمال فیلتر",bd=0,bg=c["purple"],fg="white",activebackground=c["blue"],font=(self.ui_family,8,"bold")).pack(fill="x",padx=10,pady=(8,10),ipady=7)
        sel=tk.Frame(parent,bg=c["panel"],highlightthickness=1,highlightbackground=c["border"]); sel.pack(fill="both",expand=True,padx=9,pady=0)
        tk.Label(sel,text="محصولات منتخب",bg=c["panel"],fg=c["text"],font=(self.ui_family,10,"bold")).pack(anchor="e",padx=10,pady=10)
        self.selected_list=sel
        self.today_side=tk.Frame(parent,bg=c["panel2"],highlightthickness=1,highlightbackground=c["border"],height=76); self.today_side.pack(fill="x",padx=9,pady=9); self.today_side.pack_propagate(False)
        tk.Label(self.today_side,text="☀ بهترین فرصت‌های امروز",bg=c["panel2"],fg=c["gold"],font=(self.ui_family,9,"bold"),anchor="e").pack(fill="x",padx=10,pady=(10,2))
        tk.Label(self.today_side,text="کالاهایی با بیشترین کاهش قیمت",bg=c["panel2"],fg=c["muted"],font=(self.ui_family,7),anchor="e").pack(fill="x",padx=10)

    def _analytics_sidebar(self,parent,c):
        # Status donut
        self.status_canvas=tk.Canvas(parent,bg=c["panel3"],highlightthickness=0,height=184)
        self.status_canvas.pack(fill="x",padx=8,pady=(8,5)); self.status_canvas.bind("<Configure>",lambda e:self._update_dashboard_stats())
        # Trend
        trendbox=tk.Frame(parent,bg=c["panel"],highlightthickness=1,highlightbackground=c["border"],height=190); trendbox.pack(fill="x",padx=8,pady=5); trendbox.pack_propagate(False)
        tk.Label(trendbox,text="روند تغییرات قیمت (۳۰ روز اخیر)",bg=c["panel"],fg=c["text"],font=(self.ui_family,9,"bold"),anchor="e").pack(fill="x",padx=10,pady=(10,3))
        self.trend_canvas=tk.Canvas(trendbox,bg=c["panel"],highlightthickness=0); self.trend_canvas.pack(fill="both",expand=True,padx=8,pady=6)
        keybox=tk.Frame(parent,bg=c["panel"],highlightthickness=1,highlightbackground=c["border"],height=160); keybox.pack(fill="x",padx=8,pady=5); keybox.pack_propagate(False)
        tk.Label(keybox,text="تغییرات کلیدی",bg=c["panel"],fg=c["text"],font=(self.ui_family,9,"bold"),anchor="e").pack(fill="x",padx=10,pady=8)
        self.key_changes=keybox
        statusbox=tk.Frame(parent,bg=c["panel"],highlightthickness=1,highlightbackground=c["border"]); statusbox.pack(fill="both",expand=True,padx=8,pady=(5,8))
        tk.Label(statusbox,text="وضعیت کلی مانیتور",bg=c["panel"],fg=c["text"],font=(self.ui_family,9,"bold"),anchor="e").pack(fill="x",padx=10,pady=8)
        self.overall_canvas=tk.Canvas(statusbox,bg=c["panel"],highlightthickness=0,height=160); self.overall_canvas.pack(fill="both",expand=True)

    def _update_dashboard_stats(self):
        if not hasattr(self,"kpi_vars"): return
        items=self.items
        total=sum(int(x.get("price") or 0) for x in items)
        ups=sum("افزایش" in str(x.get("status","")) for x in items)
        downs=sum("کاهش" in str(x.get("status","")) for x in items)
        news=sum("موجود شد" in str(x.get("status","")) for x in items)
        active=sum("فعال" in str(x.get("status","")) or "بدون تغییر" in str(x.get("status","")) for x in items)
        self.kpi_vars["market"].set(f"{total:,} تومان")
        self.kpi_vars["count"].set(str(len(items)))
        self.kpi_vars["down"].set(str(downs))
        self.kpi_vars["up"].set(str(ups))
        self.kpi_vars["new"].set(str(news))
        if hasattr(self,"progress_label"): self.progress_label.config(text=f"پایش: {len(items)} / {len(items)}")
        if hasattr(self,"page_label"): self.page_label.config(text=f"{self.current_page} / {max(1,self.total_pages)}")

        # selected cards
        if hasattr(self,"selected_list"):
            for ch in self.selected_list.winfo_children()[1:]: ch.destroy()
            picks=[]
            for x in items:
                if x.get("selected"): picks.append(x)
            if not picks: picks=sorted(items,key=lambda q:int(q.get("price") or 0),reverse=True)[:4]
            for x in picks[:4]:
                line=tk.Frame(self.selected_list,bg=self._modern_palette["panel"])
                line.pack(fill="x",padx=8,pady=3)
                title=(x.get("custom_title") or x.get("title") or "محصول")[:23]
                tk.Label(line,text=title,bg=self._modern_palette["panel"],fg=self._modern_palette["text"],font=(self.ui_family,7),anchor="e").pack(side="right",fill="x",expand=True)
                clr=self._modern_palette["green"] if "کاهش" in str(x.get("status")) else self._modern_palette["red"] if "افزایش" in str(x.get("status")) else self._modern_palette["muted"]
                tk.Label(line,text=money_text(x.get("price")),bg=self._modern_palette["panel"],fg=clr,font=(self.ui_family,7,"bold")).pack(side="left")

        # donut price-status
        if hasattr(self,"status_canvas"):
            self._draw_donut(self.status_canvas, ups, downs, max(0,len(items)-ups-downs), "وضعیت قیمت", [self._modern_palette["red"],self._modern_palette["green"],self._modern_palette["blue"]])
        if hasattr(self,"trend_canvas"):
            vals=[int(x.get("price") or 0) for x in items]
            if not vals: vals=[0]
            self._draw_line(self.trend_canvas, vals, self._modern_palette["purple"])
        if hasattr(self,"overall_canvas"):
            active=active; inactive=max(0,len(items)-active)
            self._draw_donut(self.overall_canvas, active,inactive,0,"فعال",[self._modern_palette["teal"],self._modern_palette["muted"]])
        if hasattr(self,"key_changes"):
            for ch in self.key_changes.winfo_children()[1:]: ch.destroy()
            for label,count,accent in (("کالاهای با کاهش قیمت",downs,self._modern_palette["green"]),("کالاهای با افزایش قیمت",ups,self._modern_palette["red"]),("کالاهای بدون تغییر",max(0,len(items)-ups-downs),self._modern_palette["blue"])):
                row=tk.Frame(self.key_changes,bg=self._modern_palette["panel"]); row.pack(fill="x",padx=10,pady=3)
                tk.Label(row,text=label,bg=self._modern_palette["panel"],fg=self._modern_palette["muted"],font=(self.ui_family,7),anchor="e").pack(side="right",fill="x",expand=True)
                tk.Label(row,text=str(count),bg=self._modern_palette["panel"],fg=accent,font=(self.ui_family,8,"bold")).pack(side="left")

    def _draw_donut(self,canvas,a,b,d,title,colors):
        try: canvas.delete("all")
        except Exception: return
        w=max(120,canvas.winfo_width()); h=max(130,canvas.winfo_height()); cx=w*0.72; cy=h*0.55; r=min(h*0.33,w*0.24)
        total=max(1,a+b+d); vals=[a,b,d]; start=0
        for v,col in zip(vals,colors):
            extent=360*v/total if total else 0
            canvas.create_arc(cx-r,cy-r,cx+r,cy+r,start=start,extent=-extent,style="arc",width=max(10,int(r*0.22)),outline=col)
            start-=extent
        canvas.create_oval(cx-r*0.63,cy-r*0.63,cx+r*0.63,cy+r*0.63,fill=(self._modern_palette["panel"] if canvas is getattr(self,'status_canvas',None) else self._modern_palette["panel"]),outline="")
        canvas.create_text(cx,cy-8,text=str(a+b+d),fill=self._modern_palette["text"],font=(self.ui_family,16,"bold"))
        canvas.create_text(cx,cy+16,text=title,fill=self._modern_palette["muted"],font=(self.ui_family,7))
        extra = colors[2] if len(colors) > 2 else colors[-1]
        labels=[("اول",a,colors[0]),("دوم",b,colors[1] if len(colors)>1 else colors[0]),("سایر",d,extra)]
        y=18
        for lab,v,col in labels:
            if v==0 and lab=="سایر": continue
            canvas.create_oval(10,y,18,y+8,fill=col,outline="")
            canvas.create_text(25,y+4,text=f"{lab}  {v}",anchor="w",fill=self._modern_palette["muted"],font=(self.ui_family,7))
            y+=20

    def _draw_line(self,canvas,vals,color):
        canvas.delete("all")
        w=max(180,canvas.winfo_width()); h=max(110,canvas.winfo_height())
        pad=18; n=len(vals); lo=min(vals); hi=max(vals); span=max(1,hi-lo)
        for i in range(1,4):
            y=pad+(h-2*pad)*i/4
            canvas.create_line(pad,y,w-pad,y,fill=self._modern_palette["border"],dash=(2,4))
        pts=[]
        for i,v in enumerate(vals):
            x=pad+(w-2*pad)*(i/(max(1,n-1)))
            y=h-pad-(h-2*pad)*(v-lo)/span
            pts.append((x,y))
        if len(pts)>1: canvas.create_line(*[p for pt in pts for p in pt],fill=color,width=2,smooth=True)
        for x,y in pts[-min(8,len(pts)):]: canvas.create_oval(x-2,y-2,x+2,y+2,fill=color,outline="")

    def _animate_ambient(self):
        if not hasattr(self,"ambient"):
            return
        try:
            self.ambient.delete("all")
            w=max(1,self.ambient.winfo_width()); h=max(1,self.ambient.winfo_height())
            colors={"cyan":"#0C4450","purple":"#25133B","blue":"#10264F"}
            for n in self._ambient_nodes:
                n["x"]=(n["x"]+n["vx"])%1.0; n["y"]=(n["y"]+n["vy"])%1.0
                x=n["x"]*w; y=n["y"]*h; r=n["r"]
                self.ambient.create_oval(x-r,y-r,x+r,y+r,fill=colors[n["kind"]],outline="")
            self._ambient_phase=(self._ambient_phase+1)%1000
        except Exception:
            pass
        self.root.after(110,self._animate_ambient)

    def _migrate_reference_monitor_links(self):
        try:
            data = load_reference()
            changed = False
            by_id = {str(item.get("id")): item for item in self.items if item.get("id") is not None}
            for supplier in data.get("suppliers", []):
                for product in supplier.get("products", []):
                    if product.get("monitor_product_uuid"):
                        continue
                    legacy = product.get("monitor_product_id")
                    target = by_id.get(str(legacy)) if legacy not in (None, "") else None
                    if target is None and isinstance(legacy, int) and 0 <= legacy < len(self.items):
                        target = self.items[legacy]
                    if target is not None and target.get("uuid"):
                        product["monitor_product_uuid"] = target["uuid"]
                        product["monitor_product_id"] = target.get("id")
                        changed = True
            if changed:
                save_reference(data)
        except Exception:
            pass

    def _editable_focus(self):
        widget = self.root.focus_get()
        if widget is None:
            return None
        try:
            cls = str(widget.winfo_class())
        except Exception:
            cls = ""
        if cls in ("Entry", "TEntry", "Text"):
            return widget
        return None

    def _handle_edit_shortcut(self, event=None):
        if event is None:
            return None
        widget = self._editable_focus()
        if widget is None:
            return None
        # Ctrl mask is 0x0004 on Tk/Windows. Physical keycodes are used so
        # Persian layout does not turn Ctrl+V/C/X/A into another keysym.
        if not (event.state & 0x0004):
            return None
        keycode_map = {65: "a", 67: "c", 86: "v", 88: "x"}
        key = keycode_map.get(getattr(event, "keycode", -1))
        if key is None:
            key = str(getattr(event, "keysym", "")).lower()
        try:
            if key == "v":
                text = self.root.clipboard_get()
                if hasattr(widget, "selection_present") and widget.selection_present():
                    widget.delete("sel.first", "sel.last")
                elif str(widget.winfo_class()) == "Text":
                    try:
                        widget.delete("sel.first", "sel.last")
                    except tk.TclError:
                        pass
                widget.insert("insert", text)
                return "break"
            if key == "c":
                if str(widget.winfo_class()) == "Text":
                    text = widget.get("sel.first", "sel.last")
                else:
                    text = widget.selection_get()
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                self.root.update()
                return "break"
            if key == "x":
                if str(widget.winfo_class()) == "Text":
                    text = widget.get("sel.first", "sel.last")
                    widget.delete("sel.first", "sel.last")
                else:
                    text = widget.selection_get()
                    widget.delete("sel.first", "sel.last")
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                self.root.update()
                return "break"
            if key == "a":
                if str(widget.winfo_class()) == "Text":
                    widget.tag_add("sel", "1.0", "end-1c")
                else:
                    widget.select_range(0, "end")
                widget.icursor("end")
                return "break"
        except tk.TclError:
            return "break"
        except Exception:
            return "break"
        return None

    def _paste_any_input(self, event=None):
        # Backward-compatible alias for older code paths.
        return self._handle_edit_shortcut(event)

    def _schedule_products_save(self, delay=1000):
        self.unsaved_changes = True
        if self._pending_save is not None:
            try:
                self.root.after_cancel(self._pending_save)
            except Exception:
                pass
        self._pending_save = self.root.after(delay, self._flush_products_save)

    def _flush_products_save(self):
        self._pending_save = None
        try:
            save_products(self.items)
            self.unsaved_changes = False
        except Exception:
            pass

    def save_now(self):
        try:
            if self._pending_save is not None:
                self.root.after_cancel(self._pending_save)
                self._pending_save = None
            save_products(self.items)
            self.unsaved_changes = False
            self.info.config(text="تغییرات ذخیره شد")
        except Exception as exc:
            messagebox.showerror("خطا در ذخیره", str(exc), parent=self.root)

    def _downloads_dir(self):
        path = Path.home() / "Downloads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def toggle_dark_mode(self):
        # Rebuild the visual shell while preserving all product/reference data.
        self.dark_mode = not self.dark_mode
        for child in list(self.root.winfo_children()):
            try: child.destroy()
            except Exception: pass
        self.row_images.clear(); self.image_cache.clear()
        self._build_modern_ui()
        self.refresh()
        self.root.after(80,self._animate_ambient)

    def _apply_widget_theme(self,parent,dark):
        # Legacy recursive hook retained for compatibility; modern UI is rebuilt by toggle_dark_mode().
        return

    def screenshot_monitor(self):
        if ImageGrab is None:
            messagebox.showerror("اسکرین‌شات", "کتابخانه Pillow برای اسکرین‌شات در دسترس نیست.", parent=self.root)
            return
        self.root.update_idletasks()
        visible_rows=max(0,len(self.rows_frame.winfo_children())-1)
        if visible_rows<1:
            messagebox.showwarning("اسکرین‌شات", "در صفحه فعلی حداقل یک کالا برای تصویربرداری وجود ندارد.", parent=self.root)
            return
        try:
            x=self.canvas.winfo_rootx(); y=self.canvas.winfo_rooty(); w=self.canvas.winfo_width(); h=self.canvas.winfo_height()
            img=ImageGrab.grab(bbox=(x,y,x+w,y+h))
            out=self._downloads_dir()/f"My_Digi_Monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(out,"PNG")
            messagebox.showinfo("اسکرین‌شات", f"اسکرین‌شات مانیتور ذخیره شد:\n\n{out}", parent=self.root)
        except Exception as exc:
            messagebox.showerror("اسکرین‌شات", f"گرفتن اسکرین‌شات انجام نشد:\n{exc}", parent=self.root)

    def export_excel(self):
        try:
            out=self._downloads_dir()/f"My_Digi_Products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            write_products_xlsx(self.items,out,best_supplier_resolver=lambda item:self._best_supplier_for_monitor(item),all_supplier_resolver=lambda item:self._best_supplier_for_monitor(item,all_suppliers=True))
            messagebox.showinfo("دانلود اکسل", f"فایل اکسل همه کالاها ذخیره شد:\n\n{out}", parent=self.root)
        except Exception as exc:
            messagebox.showerror("دانلود اکسل", f"ساخت فایل اکسل انجام نشد:\n{exc}", parent=self.root)

    def _close_app(self):
        if not self.unsaved_changes:
            self.root.destroy()
            return
        ans=messagebox.askyesnocancel("خروج از My Digi", "تغییرات فعلی ذخیره نشده‌اند.\n\nآیا می‌خواهید قبل از خروج ذخیره شوند؟", parent=self.root)
        if ans is None:
            return
        if ans:
            if self._pending_save is not None:
                try: self.root.after_cancel(self._pending_save)
                except Exception: pass
                self._pending_save=None
            try:
                save_products(self.items)
                self.unsaved_changes=False
            except Exception as exc:
                messagebox.showerror("خطا در ذخیره", str(exc), parent=self.root)
                return
        self.root.destroy()

    def check_reference_reminders(self):
        try:
            data = load_reference()
            due = []
            today = date.today()
            for supplier in data.get("suppliers", []):
                raw = supplier.get("next_check", "")
                due_date = parse_reminder_date(raw)
                if due_date and due_date <= today:
                    label = self._supplier_label(supplier)
                    jy, jm, jd = gregorian_to_jalali(due_date.year, due_date.month, due_date.day)
                    jtxt = f"{jy:04d}/{jm:02d}/{jd:02d}"
                    if due_date < today:
                        days = (today - due_date).days
                        state = f"{days} روز گذشته"
                    else:
                        state = "امروز"
                    due.append(f"• {label} — {jtxt} ({state})")
            if due:
                messagebox.showwarning(
                    "🔔 یادآوری مرجع من",
                    "موعد تماس/استعلام تأمین‌کننده‌های زیر رسیده است:\n\n" + "\n".join(due),
                    parent=self.root,
                )
        except Exception:
            # Reminder checking must never prevent the monitor from starting.
            pass

    def _find_monitor_matches(self, ref_product):
        """Find the monitored item for a reference product.

        Matching priority is deliberately based on identity, not display name:
        1) stored internal monitor UUID (if already linked)
        2) Digikala product ID extracted from the reference URL
        3) exact normalized URL (legacy/fallback)
        4) normalized title similarity (last-resort fallback)
        """
        # 1) Existing UUID is the strongest internal link.
        ref_uuid = str(ref_product.get("monitor_product_uuid") or "").strip()
        if ref_uuid:
            for idx, item in enumerate(self.items):
                if str(item.get("uuid") or "").strip() == ref_uuid:
                    return [idx]

        # 2) The Digikala product ID is the canonical identity of the product.
        #    This works even when the reference-library name differs from the
        #    name shown in the monitor.
        ref_url = str(ref_product.get("digikala_url", "") or "").strip()
        ref_pid = extract_id(ref_url)
        if ref_pid:
            ref_pid = str(ref_pid).strip()
            matches = []
            for idx, item in enumerate(self.items):
                item_pid = item.get("id") or item.get("product_id")
                if item_pid is None:
                    item_pid = extract_id(item.get("url", ""))
                if item_pid is not None and str(item_pid).strip() == ref_pid:
                    matches.append(idx)
            if matches:
                return matches

        # 3) Exact URL fallback for older/imported data.
        durl = normalize_text(ref_url)
        if durl:
            matches = []
            for idx, item in enumerate(self.items):
                item_url = normalize_text(item.get("url", ""))
                if item_url and item_url == durl:
                    matches.append(idx)
            if matches:
                return matches

        # 4) Name match is only a last resort.
        name = normalize_text(ref_product.get("name", ""))
        if name:
            out = []
            for idx, item in enumerate(self.items):
                title = normalize_text(item.get("custom_title") or item.get("title", ""))
                if title and (name in title or title in name):
                    out.append(idx)
            return out
        return []

    def _sync_ref_price_to_monitor(self, supplier, ref_product, monitor_index, ask=True):
        if not (0 <= monitor_index < len(self.items)):
            return
        item = self.items[monitor_index]
        new_price = ref_product.get("price")
        if new_price not in (None, ""):
            try:
                new_price = int(new_price)
            except Exception:
                new_price = None
        old_price = item.get("purchase")
        if ask and new_price is not None and old_price not in (None, new_price):
            ok = messagebox.askyesno("به‌روزرسانی قیمت خرید", f"قیمت خرید فعلی: {money_text(old_price)} تومان\nقیمت مرجع من: {money_text(new_price)} تومان\n\nقیمت خرید کالا در مانیتور به‌روزرسانی شود؟", parent=self.root)
            if not ok:
                return
        if new_price is not None:
            item["purchase"] = new_price
        if ref_product.get("my_profit") not in (None, ""):
            try: item["profit"] = int(ref_product.get("my_profit"))
            except Exception: pass
        item["reference_supplier_ids"] = list(dict.fromkeys((item.get("reference_supplier_ids") or []) + [supplier.get("id")]))
        save_products(self.items)
        self.refresh()

    def _supplier_label(self, supplier):
        name = (str(supplier.get("first_name", "")) + " " + str(supplier.get("last_name", ""))).strip()
        return name or supplier.get("company", "بدون نام")

    def _reference_product_alert(self, supplier, product):
        alerts = []
        if product.get("price_history"):
            hist = product["price_history"]
            if len(hist) >= 2:
                a, b = hist[-2], hist[-1]
                if a.get("price") != b.get("price"):
                    alerts.append("تغییر قیمت")
        if product.get("stock_reliable") in (False, 0, "0"):
            alerts.append("موجودی غیرقابل اتکا")
        return "، ".join(alerts)

    def _record_reference_change(self, product, price, stock, note=""):
        product.setdefault("price_history", [])
        product.setdefault("stock_history", [])
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            price = int(str(price).replace(",", "").strip()) if price not in (None, "") else None
        except Exception:
            price = None
        try:
            stock = int(str(stock).replace(",", "").strip()) if stock not in (None, "") else None
        except Exception:
            stock = None
        if price is not None:
            last = product["price_history"][-1].get("price") if product["price_history"] else None
            if last != price:
                product["price_history"].append({"date": stamp, "price": price})
        if stock is not None:
            last = product["stock_history"][-1].get("stock") if product["stock_history"] else None
            if last != stock:
                product["stock_history"].append({"date": stamp, "stock": stock})
        product["last_quote"] = stamp
        if note:
            product.setdefault("history_notes", []).append({"date": stamp, "note": note})

    def _reference_products_for_monitor(self, item):
        """Return all reference-library products that represent this monitor item."""
        pid = str(item.get("id") or item.get("product_id") or "").strip()
        uid = str(item.get("uuid") or "").strip()
        url = normalize_text(item.get("url", ""))
        out = []
        try:
            data = load_reference()
            for supplier in data.get("suppliers", []):
                for rp in supplier.get("products", []):
                    rpid = str(rp.get("monitor_product_id") or "").strip()
                    ruid = str(rp.get("monitor_product_uuid") or "").strip()
                    rurl = normalize_text(rp.get("digikala_url", ""))
                    ref_pid = extract_id(rp.get("digikala_url", ""))
                    matched = ((uid and ruid == uid) or
                               (pid and (rpid == pid or str(ref_pid or "") == pid)) or
                               (url and rurl == url))
                    if matched:
                        out.append((supplier, rp))
        except Exception:
            pass
        return out

    def _best_supplier_for_monitor(self, item, all_suppliers=False):
        """Find the cheapest currently recorded reference supplier for a monitor item."""
        candidates = []
        for supplier, rp in self._reference_products_for_monitor(item):
            try:
                price = int(str(rp.get("price", "")).replace(",", "").strip())
            except Exception:
                continue
            if price > 0:
                candidates.append((price, self._supplier_label(supplier), supplier, rp))
        if not candidates:
            return [] if all_suppliers else None
        candidates.sort(key=lambda x: x[0])
        return candidates if all_suppliers else candidates[0]

    def _purchase_impact(self, item, new_purchase):
        """Return the required Digikala listing price under a new purchase price."""
        try:
            profit = float(item.get("profit"))
            commission = float(item.get("commission"))
            ancillary = float(item.get("ancillary", 0) or 0)
            purchase = float(new_purchase)
            return digikala_my_price(purchase, profit, commission, ancillary)
        except Exception:
            return None

    def open_today_dashboard(self):
        data = load_reference()
        suppliers = data.get("suppliers", [])
        reminders = []
        price_changes = []
        low_stock = []
        profit_review = []
        today = date.today()
        for supplier in suppliers:
            sname = self._supplier_label(supplier)
            raw_rem = supplier.get("next_check", "")
            rd = parse_reminder_date(raw_rem)
            if rd is not None and rd <= today:
                days = (today - rd).days
                reminders.append(f"{sname} — " + ("امروز" if days == 0 else f"{days} روز گذشته"))
            for rp in supplier.get("products", []):
                hist = rp.get("price_history", []) or []
                if len(hist) >= 2 and hist[-1].get("price") != hist[-2].get("price"):
                    try:
                        oldp = int(hist[-2].get("price")); newp = int(hist[-1].get("price"))
                    except Exception:
                        continue
                    direction = "افزایش" if newp > oldp else "کاهش"
                    price_changes.append((rp.get("name", "کالا"), sname, oldp, newp, direction, rp))
                    m_uuid = str(rp.get("monitor_product_uuid") or "").strip()
                    m = next((x for x in self.items if str(x.get("uuid") or "").strip() == m_uuid), None)
                    if m is None and rp.get("monitor_product_id") not in (None, ""):
                        m = next((x for x in self.items if str(x.get("id") or x.get("product_id") or "") == str(rp.get("monitor_product_id"))), None)
                    if m is not None and newp > oldp:
                        old_required = self._purchase_impact(m, oldp)
                        new_required = self._purchase_impact(m, newp)
                        if old_required and new_required and new_required > old_required:
                            diff = new_required - old_required
                            profit_review.append(f"{rp.get('name','کالا')} — قیمت خرید {money_text(newp)}؛ قیمت لازم دیجی‌کالا برای حفظ سود حدود {money_text(new_required)} تومان است (+{money_text(diff)} نسبت به قبل)")
                try:
                    stock = int(rp.get("stock", 0) or 0)
                    if stock <= 3:
                        low_stock.append(f"{rp.get('name','کالا')} — {sname}: موجودی {stock}")
                except Exception:
                    pass

        win = tk.Toplevel(self.root)
        win.title("📌 کارهای امروز")
        win.geometry("800x650")
        win.transient(self.root)
        outer = ttk.Frame(win, padding=14); outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="📌 کارهای امروز", font=(self.ui_family, 16, "bold"), anchor="e").pack(fill="x", pady=(0,8))
        summary = f"یادآوری: {len(reminders)}   |   تغییر قیمت خرید: {len(price_changes)}   |   موجودی پایین: {len(low_stock)}   |   نیاز به بررسی قیمت فروش: {len(profit_review)}"
        ttk.Label(outer, text=summary, anchor="e").pack(fill="x", pady=(0,10))
        notebook = ttk.Notebook(outer); notebook.pack(fill="both", expand=True)
        sections = [
            ("🔔 یادآوری‌ها", reminders, "item"),
            ("💰 تغییر قیمت خرید", [f"{n} — {sn}: {money_text(o)} → {money_text(nn)} تومان ({d})" for n,sn,o,nn,d,_ in price_changes], "item"),
            ("⚠ موجودی پایین", low_stock, "item"),
            ("📈 اثر روی قیمت فروش", profit_review, "item"),
        ]
        for title, lines, _ in sections:
            tab=ttk.Frame(notebook,padding=8); notebook.add(tab,text=title)
            txt=tk.Text(tab, wrap="word", height=20, font=(self.ui_family,10), state="normal")
            txt.pack(fill="both",expand=True)
            if lines:
                txt.insert("1.0", "\n".join(f"• {x}" for x in lines))
            else:
                txt.insert("1.0", "موردی برای امروز وجود ندارد.")
            txt.configure(state="disabled")
        ttk.Button(outer, text="بستن", command=win.destroy).pack(anchor="e", pady=(10,0))

    def open_reference(self):
        if self.reference_window is not None and self.reference_window.winfo_exists():
            self.reference_window.lift()
            self.reference_window.focus_force()
            return
        self.reference_window = tk.Toplevel(self.root)
        win = self.reference_window
        win.title("📚 مرجع من — کتابخانه تأمین‌کنندگان")
        win.geometry("1200x720")
        win.minsize(980, 620)

        data = load_reference()
        suppliers = data.setdefault("suppliers", [])
        search_var = tk.StringVar()
        selected_sid = {"value": None}
        selected_pid = {"value": None}

        main = ttk.Frame(win, padding=10)
        main.pack(fill="both", expand=True)
        head = ttk.Frame(main)
        head.pack(fill="x", pady=(0, 8))
        ttk.Label(head, text="📚 مرجع من", font=(self.ui_family, 14, "bold")).pack(side="right")
        ttk.Label(head, text="دفتر تأمین‌کننده، قیمت خرید، موجودی و سوابق", font=(self.ui_family, 10)).pack(side="right", padx=15)
        ttk.Button(head, text="➕ تأمین‌کننده جدید", command=lambda: add_supplier()).pack(side="left")
        ttk.Label(head, text="جستجو:").pack(side="left", padx=(15, 3))
        search = tk.Entry(head, textvariable=search_var, justify="right", width=28)
        search.pack(side="left")

        paned = ttk.Panedwindow(main, orient="horizontal")
        paned.pack(fill="both", expand=True)
        left = ttk.Frame(paned, padding=6)
        right = ttk.Frame(paned, padding=6)
        paned.add(left, weight=1)
        paned.add(right, weight=5)

        supplier_tree = ttk.Treeview(left, columns=("name", "status"), show="headings", height=22)
        supplier_tree.heading("name", text="تأمین‌کننده")
        supplier_tree.heading("status", text="وضعیت")
        supplier_tree.column("name", width=180, anchor="e")
        supplier_tree.column("status", width=105, anchor="center")
        supplier_tree.pack(fill="both", expand=True)
        lbtn = ttk.Frame(left); lbtn.pack(fill="x", pady=(6,0))

        ttk.Button(lbtn, text="ویرایش", command=lambda: edit_supplier()).pack(side="right", padx=2)
        ttk.Button(lbtn, text="حذف", command=lambda: delete_supplier()).pack(side="right", padx=2)

        top_right = ttk.Frame(right); top_right.pack(fill="x")
        supplier_title = ttk.Label(top_right, text="یک تأمین‌کننده را انتخاب کنید", font=(self.ui_family, 12, "bold"), anchor="e")
        supplier_title.pack(side="right", fill="x", expand=True)
        edit_info_btn = ttk.Button(top_right, text="ویرایش اطلاعات", command=lambda: edit_supplier()); edit_info_btn.pack(side="left")

        notebook = ttk.Notebook(right)
        notebook.pack(fill="both", expand=True, pady=(8,0))
        ptab = ttk.Frame(notebook, padding=6); ctab = ttk.Frame(notebook, padding=6); ntab = ttk.Frame(notebook, padding=6); htab = ttk.Frame(notebook, padding=6)
        notebook.add(ptab, text="کالاهای تأمین‌کننده")
        notebook.add(ctab, text="تماس و استعلام")
        notebook.add(ntab, text="یادداشت")
        notebook.add(htab, text="سوابق قیمت و موجودی")

        ptop=ttk.Frame(ptab); ptop.pack(fill="x")
        ttk.Button(ptop, text="➕ کالای جدید", command=lambda: add_ref_product()).pack(side="right", padx=2)
        ttk.Button(ptop, text="✏ ویرایش کالا", command=lambda: edit_ref_product()).pack(side="right", padx=2)
        ttk.Button(ptop, text="🗑 حذف کالا", command=lambda: delete_ref_product()).pack(side="right", padx=2)
        ttk.Button(ptop, text="🔗 اتصال به مانیتور", command=lambda: link_to_monitor()).pack(side="right", padx=2)
        ttk.Button(ptop, text="➕ افزودن به مانیتور", command=lambda: add_to_monitor()).pack(side="right", padx=2)
        ttk.Button(ptop, text="🏆 بهترین تأمین‌کننده", command=lambda: best_supplier()).pack(side="left", padx=2)
        ttk.Button(ptop, text="🔄 ثبت استعلام جدید", command=lambda: quote_product()).pack(side="left", padx=2)

        product_tree = ttk.Treeview(ptab, columns=("name","price","stock","reliable","monitor","alert"), show="headings", height=16)
        for col, title, width in [("name","کالا",260),("price","قیمت خرید",120),("stock","موجودی",90),("reliable","موجودی قابل اتکا",120),("monitor","مانیتور",120),("alert","هشدار",160)]:
            product_tree.heading(col, text=title); product_tree.column(col, width=width, anchor="center" if col!="name" else "e")
        product_tree.pack(fill="both", expand=True, pady=(6,0))

        quote_tree=ttk.Treeview(ctab, columns=("date","subject","price","stock","notes"), show="headings", height=15)
        for col,title,w in [("date","تاریخ",130),("subject","موضوع",170),("price","قیمت",110),("stock","موجودی",90),("notes","یادداشت",360)]:
            quote_tree.heading(col,text=title); quote_tree.column(col,width=w,anchor="center" if col!="notes" else "e")
        quote_tree.pack(fill="both", expand=True)

        notes_text=tk.Text(ntab, height=15, wrap="word")
        notes_text.pack(fill="both", expand=True)
        ttk.Button(ntab,text="💾 ذخیره یادداشت",command=lambda: save_notes()).pack(anchor="e",pady=(6,0))

        history_tree=ttk.Treeview(htab, columns=("date","price","stock","note"), show="headings")
        for col,title,w in [("date","تاریخ",150),("price","قیمت",130),("stock","موجودی",100),("note","توضیح",500)]:
            history_tree.heading(col,text=title); history_tree.column(col,width=w,anchor="center" if col!="note" else "e")
        history_tree.pack(fill="both",expand=True)

        def current_supplier():
            sid=selected_sid["value"]
            return next((s for s in suppliers if s.get("id")==sid), None)
        def current_product():
            s=current_supplier(); pid=selected_pid["value"] if selected_pid else None
            if not s: return None
            return next((p for p in s.get("products",[]) if p.get("id")==pid), None)
        def refresh_suppliers():
            supplier_tree.delete(*supplier_tree.get_children())
            q=normalize_text(search_var.get())
            for s in suppliers:
                label=self._supplier_label(s); status=s.get("status","فعال")
                products_count=len(s.get("products",[]))
                if q and q not in normalize_text(label) and q not in normalize_text(s.get("mobile","")) and q not in normalize_text(s.get("tags","")):
                    continue
                iid=str(s.get("id")); supplier_tree.insert("", "end", iid=iid, values=(label, f"{status} | {products_count} کالا"))
            if selected_sid["value"] and supplier_tree.exists(str(selected_sid["value"])):
                supplier_tree.selection_set(str(selected_sid["value"]))
        def refresh_details():
            s=current_supplier()
            selected_pid["value"]=None
            product_tree.delete(*product_tree.get_children()); quote_tree.delete(*quote_tree.get_children()); history_tree.delete(*history_tree.get_children()); notes_text.delete("1.0","end")
            if not s:
                supplier_title.config(text="یک تأمین‌کننده را انتخاب کنید"); return
            supplier_title.config(text=f"{self._supplier_label(s)}  |  {s.get('mobile','') or 'بدون موبایل'}  |  وضعیت: {s.get('status','فعال')}")
            notes_text.insert("1.0", s.get("notes", ""))
            for p in s.get("products",[]):
                iid=str(p.get("id")); mon="متصل" if (p.get("monitor_product_uuid") or p.get("monitor_product_id")) else "مستقل"
                alert=self._reference_product_alert(s,p)
                reliable="بله" if p.get("stock_reliable", True) else "خیر"
                product_tree.insert("", "end", iid=iid, values=(p.get("name",""), money_text(p.get("price")), p.get("stock",0), reliable, mon, alert))
            for q in s.get("quotes",[]):
                quote_tree.insert("", "end", values=(q.get("date",""),q.get("subject","استعلام"),money_text(q.get("price")),q.get("stock",""),q.get("notes","")))
        def refresh_history():
            history_tree.delete(*history_tree.get_children())
            p=current_product()
            if not p:return
            ph=p.get("price_history",[]); sh=p.get("stock_history",[])
            dates=sorted(set([x.get("date") for x in ph]+[x.get("date") for x in sh]), reverse=True)
            notes={x.get("date"):x.get("note","") for x in p.get("history_notes",[])}
            for d in dates:
                pr=next((x.get("price") for x in ph if x.get("date")==d), None); st=next((x.get("stock") for x in sh if x.get("date")==d), None)
                history_tree.insert("", "end", values=(d,money_text(pr),st if st is not None else "—",notes.get(d,"")))
        def add_supplier():
            form_supplier(None)
        def edit_supplier():
            s=current_supplier()
            if s: form_supplier(s)
            else: messagebox.showinfo("مرجع من","یک تأمین‌کننده را انتخاب کنید.",parent=win)
        def form_supplier(existing):
            dlg=tk.Toplevel(win); dlg.title("تأمین‌کننده"); dlg.transient(win); dlg.grab_set(); dlg.geometry("520x560")
            frm=ttk.Frame(dlg,padding=12); frm.pack(fill="both",expand=True)
            fields=[("نام","first_name"),("نام خانوادگی","last_name"),("موبایل","mobile"),("آدرس","address"),("برچسب‌ها","tags"),("یادآوری بعدی (شمسی: ۱۴۰۵/۰۶/۲۰)","next_check")]
            vars={}
            for label,key in fields:
                ttk.Label(frm,text=label).pack(anchor="e")
                initial = normalize_reminder_for_edit((existing or {}).get(key,"")) if key == "next_check" else (existing or {}).get(key,"")
                v=tk.StringVar(value=initial); vars[key]=v; tk.Entry(frm,textvariable=v,justify="right").pack(fill="x", pady=(0,6))
            ttk.Label(frm,text="وضعیت تأمین‌کننده").pack(anchor="e")
            status=tk.StringVar(value=(existing or {}).get("status","فعال")); ttk.Combobox(frm,textvariable=status,values=["فعال","موقتاً غیرفعال","ناموجود","دیگر همکاری ندارد"],state="readonly",justify="right").pack(fill="x",pady=(0,6))
            ttk.Label(frm,text="یادداشت آزاد").pack(anchor="e"); nt=tk.Text(frm,height=7); nt.pack(fill="both",expand=True); nt.insert("1.0",(existing or {}).get("notes",""))
            def save_it():
                vals={k:v.get().strip() for k,v in vars.items()}
                vals["next_check"] = normalize_reminder_for_edit(vals["next_check"])
                if vals["next_check"] and not parse_reminder_date(vals["next_check"]):
                    messagebox.showwarning("مرجع من","تاریخ یادآوری را به‌صورت شمسی و به شکل ۱۴۰۵/۰۶/۲۰ وارد کنید.",parent=dlg); return
                vals["status"]=status.get(); vals["notes"]=nt.get("1.0","end").strip()
                if not vals["first_name"] and not vals["last_name"]: messagebox.showwarning("مرجع من","حداقل نام تأمین‌کننده را وارد کنید.",parent=dlg); return
                if existing: existing.update(vals)
                else:
                    vals.update({"id": f"sup-{int(datetime.now().timestamp()*1000)}", "products":[], "quotes":[]}); suppliers.append(vals)
                save_reference(data); dlg.destroy(); refresh_suppliers(); refresh_details()
            ttk.Button(frm,text="ذخیره",command=save_it).pack(anchor="e",pady=6)
        def delete_supplier():
            s=current_supplier()
            if not s:return
            if messagebox.askyesno("حذف تأمین‌کننده",f"«{self._supplier_label(s)}» حذف شود؟",parent=win):
                suppliers.remove(s); selected_sid["value"]=None; save_reference(data); refresh_suppliers(); refresh_details()
        def add_ref_product(): form_product(None)
        def edit_ref_product():
            p=current_product()
            if p: form_product(p)
            else: messagebox.showinfo("مرجع من","یک کالا را انتخاب کنید.",parent=win)
        def form_product(existing):
            s=current_supplier()
            if not s:return
            dlg=tk.Toplevel(win); dlg.title("کالای تأمین‌کننده"); dlg.transient(win); dlg.grab_set(); dlg.geometry("620x700")
            frm=ttk.Frame(dlg,padding=12); frm.pack(fill="both",expand=True)
            fields=[("نام کالا","name"),("دسته‌بندی","category"),("قیمت خرید تأمین‌کننده","price"),("سود من","my_profit"),("موجودی اعلامی","stock"),("لینک دیجی‌کالا (اختیاری)","digikala_url"),("تاریخ آخرین استعلام","last_quote")]
            vars={}
            for label,key in fields:
                ttk.Label(frm,text=label).pack(anchor="e"); v=tk.StringVar(value=str((existing or {}).get(key,""))); vars[key]=v; tk.Entry(frm,textvariable=v,justify="right").pack(fill="x",pady=(0,6))
            rel=tk.BooleanVar(value=bool((existing or {}).get("stock_reliable",True)))
            tk.Checkbutton(frm,text="این موجودی قابل اتکاست",variable=rel).pack(anchor="e",pady=4)
            ttk.Label(frm,text="قیمت پلکانی بر اساس تعداد — مثال: 1:550000, 5:530000, 10:510000").pack(anchor="e")
            tier=tk.StringVar(value=tiers_text((existing or {}).get("price_tiers",[]))); tk.Entry(frm,textvariable=tier,justify="right").pack(fill="x",pady=(0,6))
            ttk.Label(frm,text="یادداشت کالا").pack(anchor="e"); nt=tk.Text(frm,height=8); nt.pack(fill="both",expand=True); nt.insert("1.0",(existing or {}).get("notes",""))
            def save_it():
                try: price=int(str(vars["price"].get()).replace(",","")) if vars["price"].get().strip() else None
                except: price=None
                try: stock=int(str(vars["stock"].get()).replace(",","")) if vars["stock"].get().strip() else 0
                except: stock=0
                try: my_profit=int(str(vars["my_profit"].get()).replace(",","")) if vars["my_profit"].get().strip() else None
                except: my_profit=None
                if not vars["name"].get().strip(): messagebox.showwarning("مرجع من","نام کالا الزامی است.",parent=dlg); return
                vals={k:v.get().strip() for k,v in vars.items()}; vals["price"]=price; vals["my_profit"]=my_profit; vals["stock"]=stock; vals["stock_reliable"]=bool(rel.get()); vals["price_tiers"]=parse_tiers(tier.get()); vals["notes"]=nt.get("1.0","end").strip()
                if existing:
                    old=existing.get("price")
                    existing.update(vals); self._record_reference_change(existing, price, stock, "ویرایش کالا")
                    if old not in (None,price):
                        existing.setdefault("alerts",[]).append({"date":today_text(),"type":"price_change","from":old,"to":price})
                else:
                    vals.update({"id":f"prd-{int(datetime.now().timestamp()*1000)}","monitor_product_id":None,"monitor_product_uuid":None,"price_history":[],"stock_history":[],"history_notes":[],"alerts":[]}); self._record_reference_change(vals, price, stock, "ثبت اولیه"); s.setdefault("products",[]).append(vals); selected_pid["value"]=vals["id"]
                save_reference(data); dlg.destroy(); refresh_details(); refresh_history()
            ttk.Button(frm,text="ذخیره",command=save_it).pack(anchor="e",pady=6)
        def delete_ref_product():
            s=current_supplier(); p=current_product()
            if s and p and messagebox.askyesno("حذف کالا","این کالا از مرجع این تأمین‌کننده حذف شود؟",parent=win):
                s.get("products",[]).remove(p); selected_pid["value"]=None; save_reference(data); refresh_details(); refresh_history()
        def link_to_monitor():
            s=current_supplier(); p=current_product()
            if not s or not p:return
            matches=self._find_monitor_matches(p)
            if not matches:
                messagebox.showinfo("اتصال به مانیتور","کالای مشابهی در مانیتور اصلی پیدا نشد. از «افزودن به مانیتور» استفاده کنید.",parent=win); return
            idx=matches[0]; p["monitor_product_uuid"] = self.items[idx].get("uuid")
            p["monitor_product_id"] = self.items[idx].get("id") or self.items[idx].get("product_id")
            self._sync_ref_price_to_monitor(s,p,idx,ask=True); save_reference(data); refresh_details()
        def add_to_monitor():
            s=current_supplier(); p=current_product()
            if not p:return
            url=p.get("digikala_url","")
            if not url: messagebox.showinfo("مرجع من","برای این کالا لینک دیجی‌کالا ثبت نشده است.",parent=win); return
            self.url.delete(0,"end"); self.url.insert(0,url); self.add(); p["monitor_product_id"]=None; save_reference(data); refresh_details()
        def quote_product():
            s=current_supplier(); p=current_product()
            if not s or not p:return
            dlg=tk.Toplevel(win); dlg.title("ثبت استعلام جدید"); dlg.transient(win); dlg.grab_set(); dlg.geometry("500x380")
            frm=ttk.Frame(dlg,padding=12); frm.pack(fill="both",expand=True)
            vsub=tk.StringVar(value="تماس و استعلام قیمت/موجودی"); vp=tk.StringVar(value="" if p.get("price") is None else str(p.get("price"))); vs=tk.StringVar(value=str(p.get("stock",0))); vn=tk.StringVar()
            for lab,v in [("موضوع",vsub),("قیمت جدید",vp),("موجودی جدید",vs)]:
                ttk.Label(frm,text=lab).pack(anchor="e"); tk.Entry(frm,textvariable=v,justify="right").pack(fill="x",pady=(0,7))
            ttk.Label(frm,text="یادداشت").pack(anchor="e"); txt=tk.Text(frm,height=7); txt.pack(fill="both",expand=True)
            def save_q():
                try: price=int(vp.get().replace(",",""))
                except: price=p.get("price")
                try: stock=int(vs.get().replace(",",""))
                except: stock=p.get("stock",0)
                old=p.get("price"); p["price"]=price; p["stock"]=stock; self._record_reference_change(p,price,stock,txt.get("1.0","end").strip())
                if old not in (None,price):
                    p.setdefault("alerts",[]).append({"date":today_text(),"type":"price_change","from":old,"to":price})
                    try:
                        linked_uuid = str(p.get("monitor_product_uuid") or "").strip()
                        linked = next((m for m in self.items if str(m.get("uuid") or "").strip()==linked_uuid), None)
                        if linked is not None and int(price) > int(old):
                            linked["reference_price_alert"] = {"date":today_text(),"supplier":self._supplier_label(s),"old":int(old),"new":int(price),"impact_price":self._purchase_impact(linked, price)}
                            self._schedule_products_save()
                    except Exception:
                        pass
                s.setdefault("quotes",[]).append({"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"subject":vsub.get(),"price":price,"stock":stock,"notes":txt.get("1.0","end").strip()})
                save_reference(data); dlg.destroy(); refresh_details(); refresh_history()
            ttk.Button(frm,text="ذخیره استعلام",command=save_q).pack(anchor="e",pady=6)
        def best_supplier():
            p=current_product()
            if not p:return
            target=normalize_text(p.get("name"))
            candidates=[]
            for s in suppliers:
                for q in s.get("products",[]):
                    if target and (target in normalize_text(q.get("name")) or normalize_text(q.get("name")) in target) and q.get("price") not in (None,""):
                        candidates.append((int(q.get("price")),self._supplier_label(s),q.get("stock",0),s))
            if not candidates:
                messagebox.showinfo("بهترین تأمین‌کننده","برای کالای انتخاب‌شده، تأمین‌کننده دیگری با قیمت ثبت‌شده پیدا نشد.",parent=win); return
            candidates.sort(key=lambda x:x[0])
            lines=[f"{i+1}. {name} — {money_text(price)} تومان — موجودی: {stock}" for i,(price,name,stock,_) in enumerate(candidates[:10])]
            messagebox.showinfo("بهترین تأمین‌کننده برای این کالا","\n".join(lines),parent=win)
        def save_notes():
            s=current_supplier()
            if not s:return
            s["notes"]=notes_text.get("1.0","end").strip(); save_reference(data); messagebox.showinfo("مرجع من","یادداشت ذخیره شد.",parent=win)
        def on_supplier_select(event=None):
            sel=supplier_tree.selection(); selected_sid["value"]=sel[0] if sel else None; refresh_details()
        def on_product_select(event=None):
            sel=product_tree.selection(); selected_pid["value"]=sel[0] if sel else None; refresh_history()
        search_var.trace_add("write",lambda *a: refresh_suppliers())
        supplier_tree.bind("<<TreeviewSelect>>",on_supplier_select)
        product_tree.bind("<<TreeviewSelect>>",on_product_select)
        refresh_suppliers()
        if suppliers:
            selected_sid["value"]=suppliers[0].get("id"); refresh_suppliers(); supplier_tree.selection_set(str(selected_sid["value"])); refresh_details()
        win.protocol("WM_DELETE_WINDOW",lambda: (setattr(self,"reference_window",None),win.destroy()))

    def open_accounting(self):
        data = load_accounting()
        win = tk.Toplevel(self.root)
        win.title("🧾 حسابداری | My Digi")
        win.geometry("1120x760")
        win.minsize(980, 650)
        win.transient(self.root)

        # ---------- helpers ----------
        def fmt(v):
            try:
                return f"{int(v):,}"
            except Exception:
                return "0"

        def save_and_refresh():
            save_accounting(data)
            refresh_summary()
            refresh_expenses()
            refresh_profits()
            refresh_archive()

        def current_month_key():
            jy, jm, _ = gregorian_to_jalali(date.today().year, date.today().month, date.today().day)
            return f"{jy:04d}/{jm:02d}"

        def month_key_from_date(text):
            raw = _fa_to_en_digits(str(text or "").strip()).replace("-", "/")
            m = re.fullmatch(r"(\\d{4})/(\\d{1,2})/(\\d{1,2})", raw)
            if not m:
                return None
            y, mo, _ = map(int, m.groups())
            if y >= 1700:
                jy, jm, _ = gregorian_to_jalali(y, mo, 1)
                return f"{jy:04d}/{jm:02d}"
            return f"{y:04d}/{mo:02d}"

        def selected_product():
            iid = profit_product_var.get().strip()
            return next((x for x in self.items if str(x.get("uuid", "")) == iid), None)

        # ---------- header summary ----------
        header = ttk.Frame(win, padding=12)
        header.pack(fill="x")
        title = ttk.Label(header, text="🧾 حسابداری My Digi", font=(self.ui_family, 16, "bold"))
        title.pack(side="right")

        summary = ttk.Frame(win, padding=(12, 0, 12, 8))
        summary.pack(fill="x")
        summary_vars = {k: tk.StringVar(value="0 تومان") for k in ("profits", "expenses", "net")}
        for key, label in (("profits", "سود این ماه"), ("expenses", "هزینه این ماه"), ("net", "سود / زیان خالص")):
            card = ttk.LabelFrame(summary, text=label, padding=10)
            card.pack(side="right", fill="both", expand=True, padx=5)
            ttk.Label(card, textvariable=summary_vars[key], font=(self.ui_family, 13, "bold"), anchor="center").pack(fill="x")

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=12, pady=5)
        exp_tab = ttk.Frame(notebook, padding=10)
        profit_tab = ttk.Frame(notebook, padding=10)
        archive_tab = ttk.Frame(notebook, padding=10)
        notebook.add(exp_tab, text="هزینه‌ها")
        notebook.add(profit_tab, text="سودها")
        notebook.add(archive_tab, text="آرشیو ماه‌ها")

        # ---------- expenses ----------
        exp_top = ttk.Frame(exp_tab)
        exp_top.pack(fill="x", pady=(0, 8))
        ttk.Button(exp_top, text="➕ افزودن هزینه", command=lambda: add_expense()).pack(side="right", padx=3)
        ttk.Button(exp_top, text="🎨 تعریف نوع هزینه", command=lambda: manage_categories()).pack(side="right", padx=3)

        exp_tree = ttk.Treeview(exp_tab, columns=("date", "title", "cat", "amount"), show="headings", height=15)
        exp_tree.heading("date", text="تاریخ")
        exp_tree.heading("title", text="شرح")
        exp_tree.heading("cat", text="نوع هزینه")
        exp_tree.heading("amount", text="مبلغ")
        exp_tree.column("date", width=120, anchor="center")
        exp_tree.column("title", width=380, anchor="e")
        exp_tree.column("cat", width=220, anchor="e")
        exp_tree.column("amount", width=180, anchor="center")
        exp_tree.pack(fill="both", expand=True)

        # ---------- profits ----------
        ptop = ttk.Frame(profit_tab)
        ptop.pack(fill="x", pady=(0, 8))
        ttk.Button(ptop, text="➕ ثبت فروش / سود", command=lambda: add_profit()).pack(side="right", padx=3)
        ttk.Button(ptop, text="✏ ویرایش انتخاب‌شده", command=lambda: edit_profit()).pack(side="right", padx=3)
        ttk.Button(ptop, text="🗑 حذف انتخاب‌شده", command=lambda: delete_profit()).pack(side="right", padx=3)

        profit_tree = ttk.Treeview(profit_tab, columns=("date", "product", "qty", "unit", "total", "mode"), show="headings", height=15)
        for col, txt, width, anchor in (
            ("date", "تاریخ فروش", 120, "center"),
            ("product", "کالا", 360, "e"),
            ("qty", "تعداد", 80, "center"),
            ("unit", "سود واحد", 150, "center"),
            ("total", "سود کل", 170, "center"),
            ("mode", "منبع سود", 120, "center"),
        ):
            profit_tree.heading(col, text=txt)
            profit_tree.column(col, width=width, anchor=anchor)
        profit_tree.pack(fill="both", expand=True)

        # ---------- archive ----------
        at = ttk.Frame(archive_tab)
        at.pack(fill="both", expand=True)
        archive_tree = ttk.Treeview(at, columns=("month", "profits", "expenses", "net"), show="headings", height=14)
        for col, txt, width in (("month", "ماه", 160), ("profits", "مجموع سود", 220), ("expenses", "مجموع هزینه", 220), ("net", "سود / زیان خالص", 240)):
            archive_tree.heading(col, text=txt)
            archive_tree.column(col, width=width, anchor="center")
        archive_tree.pack(fill="both", expand=True)
        ttk.Label(archive_tab, text="هر بار باز شدن حسابداری، آرشیو ماه‌های بسته‌شده از روی ثبت‌های همان ماه به‌روزرسانی می‌شود.").pack(anchor="e", pady=(8,0))

        def refresh_summary():
            key = current_month_key()
            p = sum(int(x.get("total", 0) or 0) for x in data.get("profits", []) if month_key_from_date(x.get("date")) == key)
            e = sum(int(x.get("amount", 0) or 0) for x in data.get("expenses", []) if month_key_from_date(x.get("date")) == key)
            summary_vars["profits"].set(fmt(p) + " تومان")
            summary_vars["expenses"].set(fmt(e) + " تومان")
            summary_vars["net"].set(fmt(p - e) + " تومان")

        def refresh_expenses():
            exp_tree.delete(*exp_tree.get_children())
            cats = {str(c.get("id")): c for c in data.get("categories", [])}
            for i, x in enumerate(data.get("expenses", [])):
                c = cats.get(str(x.get("category_id")), {})
                iid = f"e{i}"
                exp_tree.insert("", "end", iid=iid, values=(x.get("date", ""), x.get("title", ""), c.get("name", "بدون دسته"), fmt(x.get("amount", 0))))
                color = c.get("color")
                if color:
                    tag = f"cat_{x.get('category_id')}"
                    try:
                        exp_tree.tag_configure(tag, foreground=color)
                        exp_tree.item(iid, tags=(tag,))
                    except Exception:
                        pass

        def refresh_profits():
            profit_tree.delete(*profit_tree.get_children())
            for i, x in enumerate(data.get("profits", [])):
                name = x.get("product_name", "کالای دستی")
                mode = "دستی" if x.get("manual") else "از مانیتور"
                profit_tree.insert("", "end", iid=f"p{i}", values=(x.get("date", ""), name, x.get("qty", 1), fmt(x.get("unit_profit", 0)), fmt(x.get("total", 0)), mode))

        def refresh_archive():
            archive_tree.delete(*archive_tree.get_children())
            months = {}
            for x in data.get("profits", []):
                k = month_key_from_date(x.get("date"))
                if k:
                    months.setdefault(k, {"profits": 0, "expenses": 0})["profits"] += int(x.get("total", 0) or 0)
            for x in data.get("expenses", []):
                k = month_key_from_date(x.get("date"))
                if k:
                    months.setdefault(k, {"profits": 0, "expenses": 0})["expenses"] += int(x.get("amount", 0) or 0)
            for k in sorted(months.keys(), reverse=True):
                prof = months[k]["profits"]; exp = months[k]["expenses"]
                archive_tree.insert("", "end", values=(k, fmt(prof), fmt(exp), fmt(prof-exp)))

        def expense_dialog(existing=None, edit_index=None):
            dlg = tk.Toplevel(win)
            dlg.title("هزینه")
            dlg.geometry("520x300")
            dlg.transient(win); dlg.grab_set()
            frm = ttk.Frame(dlg, padding=15); frm.pack(fill="both", expand=True)
            ttk.Label(frm, text="تاریخ (شمسی)").grid(row=0,column=0,sticky="e",pady=7)
            dvar = tk.StringVar(value=(existing or {}).get("date", today_jalali_text()))
            ttk.Entry(frm, textvariable=dvar, justify="center").grid(row=0,column=1,sticky="ew",pady=7)
            ttk.Label(frm, text="شرح هزینه").grid(row=1,column=0,sticky="e",pady=7)
            tvar = tk.StringVar(value=(existing or {}).get("title", ""))
            ttk.Entry(frm, textvariable=tvar).grid(row=1,column=1,sticky="ew",pady=7)
            ttk.Label(frm, text="دسته").grid(row=2,column=0,sticky="e",pady=7)
            cats = data.get("categories", [])
            cmap = {c.get("name"): c.get("id") for c in cats}
            cvar = tk.StringVar(value=next((c.get("name") for c in cats if c.get("id") == (existing or {}).get("category_id")), cats[0].get("name") if cats else ""))
            ttk.Combobox(frm, textvariable=cvar, values=list(cmap.keys()), state="readonly", justify="center").grid(row=2,column=1,sticky="ew",pady=7)
            ttk.Label(frm, text="مبلغ (تومان)").grid(row=3,column=0,sticky="e",pady=7)
            avar = tk.StringVar(value=fmt((existing or {}).get("amount", "")) if existing else "")
            ttk.Entry(frm, textvariable=avar, justify="center").grid(row=3,column=1,sticky="ew",pady=7)
            frm.columnconfigure(1, weight=1)
            def save_it():
                try:
                    amount = _accounting_number(avar.get())
                    if amount <= 0 or not tvar.get().strip(): raise ValueError()
                    rec = {"date": normalize_reminder_for_edit(dvar.get()), "title": tvar.get().strip(), "category_id": cmap.get(cvar.get()), "amount": amount}
                    if edit_index is None: data.setdefault("expenses", []).append(rec)
                    else: data["expenses"][edit_index] = rec
                    save_and_refresh(); dlg.destroy()
                except Exception:
                    messagebox.showerror("خطا", "شرح و مبلغ معتبر وارد کنید.", parent=dlg)
            ttk.Button(frm, text="ذخیره", command=save_it).grid(row=4,column=1,sticky="e",pady=12)

        def add_expense(): expense_dialog()

        def manage_categories():
            dlg=tk.Toplevel(win); dlg.title("انواع هزینه"); dlg.geometry("560x420"); dlg.transient(win); dlg.grab_set()
            frm=ttk.Frame(dlg,padding=12); frm.pack(fill="both",expand=True)
            tree=ttk.Treeview(frm,columns=("name","color"),show="headings",height=10)
            tree.heading("name",text="نوع هزینه"); tree.heading("color",text="رنگ")
            tree.column("name",width=300,anchor="e"); tree.column("color",width=150,anchor="center")
            tree.pack(fill="both",expand=True)
            def repop():
                tree.delete(*tree.get_children())
                for c in data.get("categories",[]): tree.insert("", "end", iid=str(c.get("id")), values=(c.get("name"), c.get("color")))
            def add_cat():
                name = simpledialog.askstring("نوع هزینه", "نام نوع هزینه:", parent=dlg)
                if not name: return
                from tkinter import colorchooser
                picked = colorchooser.askcolor(title="رنگ دسته")[1] or "#8b5cf6"
                data.setdefault("categories", []).append({"id":"cat_"+uuid.uuid4().hex[:10],"name":name.strip(),"color":picked})
                save_and_refresh(); repop()
            ttk.Button(frm,text="➕ افزودن نوع هزینه",command=add_cat).pack(anchor="e",pady=8)
            repop()

        def profit_dialog(existing=None, edit_index=None):
            dlg=tk.Toplevel(win); dlg.title("ثبت سود فروش"); dlg.geometry("620x440"); dlg.transient(win); dlg.grab_set()
            frm=ttk.Frame(dlg,padding=15); frm.pack(fill="both",expand=True)
            ttk.Label(frm,text="محصول مانیتور").grid(row=0,column=0,sticky="e",pady=8)
            products = [(str(x.get("uuid","")), x.get("custom_title") or x.get("title") or "بدون نام") for x in self.items]
            pmap = {name: uid for uid, name in products}
            pre_uid = (existing or {}).get("product_uuid")
            pre_name = next((n for uid,n in products if uid == pre_uid), (existing or {}).get("product_name", "کالای دستی"))
            pvar=tk.StringVar(value=pre_name)
            cb=ttk.Combobox(frm,textvariable=pvar,values=list(pmap.keys()),state="normal")
            cb.grid(row=0,column=1,sticky="ew",pady=8)
            ttk.Label(frm,text="تاریخ فروش (شمسی)").grid(row=1,column=0,sticky="e",pady=8)
            dvar=tk.StringVar(value=(existing or {}).get("date",today_jalali_text())); ttk.Entry(frm,textvariable=dvar,justify="center").grid(row=1,column=1,sticky="ew",pady=8)
            ttk.Label(frm,text="تعداد").grid(row=2,column=0,sticky="e",pady=8)
            qvar=tk.StringVar(value=str((existing or {}).get("qty",1))); ttk.Entry(frm,textvariable=qvar,justify="center").grid(row=2,column=1,sticky="ew",pady=8)
            ttk.Label(frm,text="سود واحد (تومان)").grid(row=3,column=0,sticky="e",pady=8)
            uvar=tk.StringVar(value=fmt((existing or {}).get("unit_profit", "")) if existing else ""); ue=ttk.Entry(frm,textvariable=uvar,justify="center"); ue.grid(row=3,column=1,sticky="ew",pady=8)
            manual_var=tk.BooleanVar(value=bool((existing or {}).get("manual",False)))
            ttk.Checkbutton(frm,text="سود را دستی ثبت/ویرایش می‌کنم",variable=manual_var).grid(row=4,column=1,sticky="e",pady=5)
            info=tk.StringVar(value="")
            ttk.Label(frm,textvariable=info,foreground="gray").grid(row=5,column=1,sticky="e",pady=5)
            frm.columnconfigure(1,weight=1)
            def load_from_monitor(event=None):
                prod=next((x for x in self.items if str(x.get("uuid",""))==pmap.get(pvar.get())),None)
                if prod:
                    profit=prod.get("profit")
                    if profit not in (None,"") and not manual_var.get():
                        uvar.set(fmt(profit)); info.set("سود واحد از مانیتور خوانده شد")
                    elif profit not in (None,""):
                        info.set("سود مانیتور موجود است؛ امکان ویرایش دستی دارید")
            cb.bind("<<ComboboxSelected>>",load_from_monitor); load_from_monitor()
            def save_it():
                try:
                    name=pvar.get().strip() or "کالای دستی"
                    uid=pmap.get(name)
                    qty=max(1,_accounting_number(qvar.get()))
                    unit=_accounting_number(uvar.get())
                    if unit < 0: raise ValueError()
                    rec={"date":normalize_reminder_for_edit(dvar.get()),"product_uuid":uid,"product_name":name,"qty":qty,"unit_profit":unit,"total":unit*qty,"manual":bool(manual_var.get())}
                    if edit_index is None: data.setdefault("profits",[]).append(rec)
                    else: data["profits"][edit_index]=rec
                    save_and_refresh(); dlg.destroy()
                except Exception:
                    messagebox.showerror("خطا","تاریخ، تعداد و سود واحد را معتبر وارد کنید.",parent=dlg)
            ttk.Button(frm,text="ذخیره فروش",command=save_it).grid(row=6,column=1,sticky="e",pady=15)

        def add_profit(): profit_dialog()
        def edit_profit():
            sel=profit_tree.selection()
            if not sel: return messagebox.showinfo("حسابداری","یک رکورد را انتخاب کنید.",parent=win)
            idx=int(sel[0][1:]); profit_dialog(data.get("profits",[])[idx],idx)
        def delete_profit():
            sel=profit_tree.selection()
            if not sel: return
            idx=int(sel[0][1:])
            if messagebox.askyesno("حذف سود","این رکورد حذف شود؟",parent=win):
                data["profits"].pop(idx); save_and_refresh()

        refresh_summary(); refresh_expenses(); refresh_profits(); refresh_archive()

    def open_calculator(self):
        """Legacy Tk entry: launch the calculator in its own native window process."""
        try:
            _subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--calculator"], cwd=str(Path(__file__).resolve().parent))
        except Exception as exc:
            messagebox.showerror("ماشین حساب", f"باز کردن ماشین حساب انجام نشد:\n{exc}", parent=self.root)

    def _resize_table(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def _mouse_over_table(self, event):
        try:
            x = event.x_root - self.canvas.winfo_rootx()
            y = event.y_root - self.canvas.winfo_rooty()
            return 0 <= x < self.canvas.winfo_width() and 0 <= y < self.canvas.winfo_height()
        except Exception:
            return False

    def _on_mousewheel(self, event):
        if not self._mouse_over_table(event):
            return
        delta = int(event.delta)
        if delta:
            self.canvas.yview_scroll(-1 if delta > 0 else 1, "units")
            return "break"

    def _on_mousewheel_linux(self, event):
        if not self._mouse_over_table(event):
            return
        self.canvas.yview_scroll(-1 if event.num == 4 else 1, "units")
        return "break"

    def paste_from_clipboard(self):
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showwarning("کپی انجام نشده", "لینک را ابتدا در ویندوز Copy کنید.")
            return
        text = str(text).strip()
        for ch in ("\u200c", "\u200d", "\u200e", "\u200f", "\ufeff", "\r", "\n", "\t"):
            text = text.replace(ch, "")
        self.url.delete(0, "end")
        self.url.insert(0, text)
        self.url.icursor("end")
        self.url.focus_set()

    def _paste_event(self, event=None):
        self.paste_from_clipboard()
        return "break"

    @staticmethod
    def _normalize_search_text(text):
        text = str(text or "").strip().lower()
        replacements = {
            "ي": "ی", "ى": "ی", "ئ": "ی",
            "ك": "ک", "ۀ": "ه", "ة": "ه",
            "ؤ": "و", "إ": "ا", "أ": "ا", "آ": "ا",
            "\u200c": " ", "\u200d": " ", "\u200e": " ", "\u200f": " ",
            "\ufeff": " ",
        }
        for a, b in replacements.items():
            text = text.replace(a, b)
        return text

    @classmethod
    def _matches_search(cls, title, query):
        query = cls._normalize_search_text(query)
        if not query:
            return True
        title = cls._normalize_search_text(title)
        # Only the beginning of each word is searchable.
        words = re.findall(r"[A-Za-z0-9_\u0600-\u06ff]+", title, flags=re.UNICODE)
        return any(word.startswith(query) for word in words)

    def _on_search(self, event=None):
        self.refresh()

    def _clear_search(self, event=None):
        self.search_var.set("")
        self.refresh()
        self.search_entry.focus_set()
        return "break"

    def refresh(self):
        for child in self.rows_frame.winfo_children():
            child.destroy()
        self.row_images.clear()

        # Sort ALL products first. Pagination only changes what is displayed.
        def sort_key(pair):
            _, item = pair
            market = item.get("price")
            mine = (digikala_my_price(
                        item.get("purchase", 0),
                        item.get("profit", 0),
                        item.get("commission", 0),
                        item.get("ancillary", 0))
                    if my_price_inputs_ready(item) else None)
            if market is None or mine is None:
                return (3, 0)
            if mine > market:
                return (0, -(mine - market))
            if mine == market:
                return (1, 0)
            return (2, -mine)

        ordered = sorted(list(enumerate(self.items)), key=sort_key)

        # Search works on the complete product list, before pagination.
        query = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        if query:
            ordered = [
                pair for pair in ordered
                if self._matches_search(
                    pair[1].get("custom_title") or pair[1].get("title", ""),
                    query
                )
            ]

        # Ten products per page. All operations/data remain based on self.items.
        self.total_pages = max(1, (len(ordered) + self.page_size - 1) // self.page_size)
        self.current_page = max(1, min(self.current_page, self.total_pages))
        start_idx = (self.current_page - 1) * self.page_size
        visible = ordered[start_idx:start_idx + self.page_size]

        # Visual order from RIGHT to LEFT.
        specs = [
            ("row", "ردیف", 1),
            ("image", "عکس", 1),
            ("title", "نام کالا", 5),
            ("best", "فروشنده با کمترین قیمت", 2),
            ("second", "دومین قیمت کم دیجیکالا", 2),
            ("change_status", "تغییر وضعیت", 2),
            ("myprice", "قیمت من", 3),
            ("mydigikala", "قیمت دیجیکالای من", 2),
            ("checked", "آخرین بررسی", 2),
        ]
        header = ttk.Frame(self.rows_frame, relief="ridge", borderwidth=1)
        header.pack(fill="x")
        for key, text, weight in reversed(specs):
            lbl = ttk.Label(header, text=text, anchor="center", relief="ridge", padding=5)
            lbl.pack(side="left", fill="both", expand=(weight > 1))
            if key in ("image", "row"):
                lbl.configure(width=8)

        # Keep original row numbering, not page-local numbering.
        for offset, (original_index, item) in enumerate(visible):
            display_number = start_idx + offset + 1
            self._make_row(display_number, item, original_index)

        self._load_visible_images()

        if hasattr(self, "page_label"):
            self.page_label.configure(
                text=f"صفحه {self.current_page} از {self.total_pages}   |   تعداد کل کالاها: {len(self.items)}"
            )
        if hasattr(self, "prev_page_btn"):
            self.prev_page_btn.configure(state=("normal" if self.current_page > 1 else "disabled"))
        if hasattr(self, "next_page_btn"):
            self.next_page_btn.configure(
                state=("normal" if self.current_page < self.total_pages else "disabled")
            )

        try:
            self._update_dashboard_stats()
        except Exception:
            pass

    def _set_page(self, page):
        self.current_page = max(1, min(int(page), self.total_pages))
        self.refresh()

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh()

    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh()

    def _edit_product_name(self, original_index):
        if not (0 <= original_index < len(self.items)):
            return
        item = self.items[original_index]
        current = item.get("custom_title") or item.get("title", "")

        win = tk.Toplevel(self.root)
        win.title("ویرایش نام کالا")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="نام کالا:").pack(anchor="e", pady=(0, 5))

        var = tk.StringVar(value=current)
        entry = tk.Entry(frame, textvariable=var, justify="right", width=70)
        entry.pack(fill="x")
        entry.focus_set()
        entry.select_range(0, "end")

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(10, 0))

        def save_name():
            value = var.get().strip()
            if value:
                item["custom_title"] = value
            else:
                item.pop("custom_title", None)
            save_products(self.items)
            win.destroy()
            self.refresh()

        ttk.Button(buttons, text="ذخیره", command=save_name).pack(side="right", padx=4)
        ttk.Button(buttons, text="انصراف", command=win.destroy).pack(side="right", padx=4)
        entry.bind("<Return>", lambda e: save_name())
        entry.bind("<Escape>", lambda e: win.destroy())

    def _make_row(self, number, item, original_index):
        row = ttk.Frame(self.rows_frame, relief="ridge", borderwidth=1)
        row.pack(fill="x")

        mine = (digikala_my_price(item.get("purchase", 0), item.get("profit", 0),
                                  item.get("commission", 0), item.get("ancillary", 0))
                if my_price_inputs_ready(item) else None)
        market = item.get("price")
        if mine is None or market is None:
            mine_color = None
        elif mine <= market:
            mine_color = "green"
        else:
            mine_color = "red"

        # Build cells from RIGHT to LEFT in the exact requested order.
        def cell(text, expand=True):
            x = ttk.Label(row, text=text, anchor="center", relief="ridge", padding=6)
            x.pack(side="right", fill="both", expand=expand)
            return x

        # 1) Row number + checkbox UNDER the number.
        row_cell = tk.Frame(row, relief="ridge", bd=1)
        row_cell.pack(side="right", fill="y")
        tk.Label(row_cell, text=str(number), anchor="center", cursor="hand2").pack(fill="x", padx=4, pady=(3, 0))
        selected_var = tk.BooleanVar(value=bool(item.get("selected", False)))

        def on_selected():
            item["selected"] = bool(selected_var.get())
            save_products(self.items)

        cb = tk.Checkbutton(row_cell, variable=selected_var, command=on_selected,
                            relief="flat", bd=0, highlightthickness=0)
        cb.pack(anchor="center", pady=(0, 3))
        row_cell.bind("<Button-1>", lambda e, idx=original_index: self.open_product(idx))
        # Keep the number clickable for opening the product.
        for w in row_cell.winfo_children():
            if isinstance(w, tk.Label):
                w.bind("<Button-1>", lambda e, idx=original_index: self.open_product(idx))

        # 2) Image
        img = ttk.Label(row, text="در حال بارگذاری…", anchor="center", relief="ridge", width=12)
        img.pack(side="right", fill="y")
        img.bind("<Button-1>", lambda e, idx=original_index: self.show_product_image(idx))
        self.row_images[original_index] = img

        # 3) Product name + pencil for a user-defined display name.
        name_frame = ttk.Frame(row, relief="ridge", borderwidth=1)
        name_frame.pack(side="right", fill="both", expand=True)

        displayed_title = item.get("custom_title") or item.get("title", "")
        pencil = ttk.Button(
            name_frame, text="✏", width=3,
            command=lambda idx=original_index: self._edit_product_name(idx)
        )
        pencil.pack(side="right", padx=4, pady=4)

        c = ttk.Label(
            name_frame, text=displayed_title, anchor="e",
            padding=6, cursor="hand2"
        )
        c.pack(side="right", fill="both", expand=True)
        c.bind("<Button-1>", lambda e, idx=original_index: self.select_row(idx))

        # 4) Cheapest offer: price, then seller directly underneath.
        seller = item.get("seller", "—") or "—"
        best_text = f'{market:,} تومان\n{seller}' if market is not None else f'ناموجود\n{seller if seller != "—" else ""}'
        cell(best_text)

        # 5) Second-cheapest offer: price, then seller. Single offer => تک قیمت.
        sp = item.get("second_price")
        ss = item.get("second_seller", "—") or "—"
        if sp is None:
            second_text = "تک قیمت"
        else:
            second_text = f"{sp:,} تومان\n{ss}"
        cell(second_text)

        # 6) Combined change/status column: one colored lamp + amount/status.
        old_change = str(item.get("change", "—") or "—")
        status = str(item.get("status", "") or "")
        lamp_color = "#808080"
        display_change = "—"

        # Prefer the numeric change recorded in `change`; derive color from status.
        if old_change not in ("—", "-") and old_change:
            display_change = old_change
        if "افزایش" in status:
            lamp_color = "red"
            if not display_change.startswith("+") and old_change not in ("—", "-"):
                # Existing V9 stores ↑; replace with explicit increase amount.
                m = re.search(r'[\d,]+', old_change)
                display_change = f"+{m.group(0)}" if m else old_change
        elif "کاهش" in status:
            lamp_color = "blue"
            if old_change not in ("—", "-"):
                m = re.search(r'[\d,]+', old_change)
                display_change = f"-{m.group(0)}" if m else old_change
        elif "ناموجود" in status or "خطا" in status:
            lamp_color = "#808080"
            display_change = "—"
        else:
            lamp_color = "#808080"
            display_change = "—"

        cs = tk.Frame(row, relief="ridge", bd=1)
        cs.pack(side="right", fill="both", expand=True)
        tk.Label(cs, text="●", fg=lamp_color, font=(self.ui_family, 13), anchor="center").pack(pady=(3, 0))
        tk.Label(cs, text=display_change, anchor="center").pack(pady=(0, 3))

        # 7) My price: two small editable fields above the computed total.
        mp = ttk.Frame(row, relief="ridge", borderwidth=1)
        mp.pack(side="right", fill="both", expand=True)
        top = ttk.Frame(mp)
        top.pack(fill="x")

        purchase_var = tk.StringVar(value="" if item.get("purchase") is None else str(item.get("purchase")))
        profit_var = tk.StringVar(value="" if item.get("profit") is None else str(item.get("profit")))
        ancillary_var = tk.StringVar(value=str(item.get("ancillary", 0)))
        commission_var = tk.StringVar(value="" if item.get("commission") is None else str(item.get("commission")))

        def num_value(v):
            try:
                return int(str(v).replace(",", "").strip() or 0)
            except Exception:
                return 0

        def recalc(*_):
            pv = purchase_var.get().strip()
            fv = profit_var.get().strip()
            av = ancillary_var.get().strip()
            cv = commission_var.get().strip()
            item["purchase"] = num_value(pv) if pv else None
            item["profit"] = num_value(fv) if fv else None
            item["ancillary"] = num_value(av) if av else 0
            try:
                item["commission"] = max(0, float(str(cv).replace(",", ".").strip())) if cv else None
            except Exception:
                item["commission"] = None
            if item["purchase"] is not None and item["profit"] is not None:
                total = item["purchase"] + item["profit"]
                total_lbl.configure(text=f"قیمت من\n{total:,} تومان")
            else:
                total_lbl.configure(text="قیمت من\nمحاسبه نشده")
            self._schedule_products_save()
            self.refresh()

        def small(parent, label, var):
            f = ttk.Frame(parent)
            f.pack(side="right", fill="x", expand=True)
            ttk.Label(f, text=label, anchor="center").pack()
            e = tk.Entry(f, textvariable=var, justify="center", width=10)
            e.pack(fill="x", padx=2, pady=1)
            e.bind("<FocusOut>", recalc)
            e.bind("<Return>", recalc)

        small(top, "خرید", purchase_var)
        small(top, "سود", profit_var)
        if item.get("purchase") is not None and item.get("profit") is not None:
            total_text = f"قیمت من\n{item.get('purchase', 0) + item.get('profit', 0):,} تومان"
        else:
            total_text = "قیمت من\nمحاسبه نشده"
        total_lbl = ttk.Label(mp, text=total_text, anchor="center", padding=4)
        total_lbl.pack(fill="both", expand=True)

        settings = ttk.Frame(mp)
        settings.pack(fill="x")
        ttk.Label(settings, text="جانبی").pack(side="right")
        ae = tk.Entry(settings, textvariable=ancillary_var, width=8, justify="center")
        ae.pack(side="right", padx=2)
        ae.bind("<FocusOut>", recalc)
        ae.bind("<Return>", recalc)
        ttk.Label(settings, text="کمیسیون٪").pack(side="right")
        ce = tk.Entry(settings, textvariable=commission_var, width=6, justify="center")
        ce.pack(side="right", padx=2)
        ce.bind("<FocusOut>", recalc)
        ce.bind("<Return>", recalc)

        # 8) My Digikala price
        best_supplier = self._best_supplier_for_monitor(item)
        if mine is not None:
            mine_text = f"{mine:,} تومان"
            if best_supplier:
                mine_text += f"\n{best_supplier[1]}"
        else:
            mine_text = "محاسبه نشده"
            if best_supplier:
                mine_text += f"\n{best_supplier[1]}"
        mine_lbl = ttk.Label(row, text=mine_text, anchor="center", relief="ridge", padding=6)
        if mine_color == "green":
            mine_lbl.configure(foreground="green")
        elif mine_color == "red":
            mine_lbl.configure(foreground="red")
        mine_lbl.pack(side="right", fill="both", expand=True)

        # 9) Last checked: this is the LEFTMOST column.
        cell(item.get("checked", "—"))

    def _refresh_my_price_column(self):
        # Rebuild the table so sorting and colors reflect edited values.
        save_products(self.items)
        self.refresh()

    def select_row(self, idx):
        # Row clicks no longer display the confusing "ردیف ... انتخاب شد"
        # message. Keep the index internally for existing interactions.
        self.selected_index = idx

    def _load_visible_images(self):
        if Image is None:
            for item in self.items:
                cell = self.row_images.get(self.items.index(item))
                if cell:
                    cell.configure(text="Pillow نصب نیست")
            return
        visible_indices = set()
        query = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        for idx, item in enumerate(self.items):
            if not query or self._matches_search(item.get("custom_title") or item.get("title", ""), query):
                visible_indices.add(idx)

        for idx in visible_indices:
            item = self.items[idx]
            url = item.get("image_url")
            if url:
                threading.Thread(target=self._download_thumbnail, args=(idx, url), daemon=True).start()

    def _download_thumbnail(self, idx, url):
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=20) as r:
                raw = r.read()
            image = Image.open(BytesIO(raw)).convert("RGB")
            original_size = image.size
            thumb = image.copy()
            thumb.thumbnail((85, 85), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(thumb)
            self.root.after(0, lambda: self._set_thumbnail(idx, photo, original_size))
        except Exception:
            self.root.after(0, lambda: self._set_thumbnail_error(idx))

    def _set_thumbnail(self, idx, photo, original_size):
        if idx >= len(self.items):
            return
        self.image_cache[idx] = photo
        cell = self.row_images.get(idx)
        if cell and cell.winfo_exists():
            cell.configure(image=photo, text="", width=90)
            cell.image = photo
        self.items[idx]["image_size"] = list(original_size)

    def _set_thumbnail_error(self, idx):
        if idx < len(self.items):
            cell = self.row_images.get(idx)
            if cell and cell.winfo_exists():
                cell.configure(text="بدون عکس")

    def open_product(self, idx):
        if 0 <= idx < len(self.items):
            webbrowser.open(self.items[idx].get("url", ""))

    def show_product_image(self, idx):
        if not (0 <= idx < len(self.items)):
            return
        if Image is None:
            messagebox.showerror("خطا", "برای نمایش عکس باید Pillow نصب باشد.")
            return
        item = self.items[idx]
        url = item.get("image_url")
        if not url:
            messagebox.showinfo("عکس محصول", "آدرس عکس این محصول در اطلاعات دیجی‌کالا پیدا نشد.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"عکس محصول - ردیف {idx+1}")
        win.geometry("1000x750")
        win.minsize(500, 400)

        canvas = tk.Canvas(win, background="white")
        xbar = ttk.Scrollbar(win, orient="horizontal", command=canvas.xview)
        ybar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)
        xbar.pack(side="bottom", fill="x")
        ybar.pack(side="left", fill="y")
        canvas.pack(side="right", fill="both", expand=True)

        holder = {"photo": None}
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=20) as r:
                raw = r.read()
            image = Image.open(BytesIO(raw)).convert("RGB")
            # IMPORTANT: no resize here. The image is displayed at its native pixel dimensions.
            holder["photo"] = ImageTk.PhotoImage(image)
            canvas.create_image(0, 0, image=holder["photo"], anchor="nw")
            canvas.configure(scrollregion=(0, 0, image.width, image.height))
            win.title(f"عکس محصول - {image.width} × {image.height} پیکسل")
        except Exception as e:
            win.destroy()
            messagebox.showerror("خطا در نمایش عکس", str(e))

    def add(self):
        url = self.url.get().strip().replace("\u200c", "").replace("\n", "").replace("\r", "").replace("\u200f", "").replace("\u200e", "")
        pid = extract_id(url)
        if not pid:
            messagebox.showerror("خطا", "لینک معتبر محصول دیجی‌کالا وارد کنید.")
            return
        existing_ids = {str(p.get("id", "")).strip() for p in self.items}
        if str(pid).strip() in existing_ids:
            messagebox.showinfo("محصول تکراری", f"این محصول قبلاً اضافه شده است.\n\nشناسه محصول: {pid}")
            return
        self.info.config(text="در حال دریافت اطلاعات محصول…")

        def work():
            try:
                try:
                    title, price, seller, second_price, second_seller, unavailable, image_url = fetch_product(pid)
                    pending=False
                except Exception:
                    title=f"محصول DKP-{pid}"; price=None; seller="—"; second_price=None; second_seller="—"; unavailable=False; image_url=None; pending=True
                item = {"uuid": str(uuid.uuid4()), "id": pid, "url": url, "title": title, "price": price,
                        "seller": seller or "—", "second_price": second_price,
                        "second_seller": second_seller or "—", "change": "—",
                        "purchase": None, "profit": None, "ancillary": 0, "commission": None,
                        "status": "⚠ نیاز به بررسی" if pending else ("⚪ ناموجود" if unavailable else "🟢 فعال"),
                        "checked": datetime.now().strftime("%Y/%m/%d %H:%M"),
                        "image_url": image_url, "selected": False}
                self.items.append(item)
                save_products(self.items)
                self.root.after(0, self.refresh)
                self.root.after(0, lambda: self.url.delete(0, "end"))
                self.root.after(0, lambda: self.info.config(text="محصول اضافه شد"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("خطا", str(e)))
                self.root.after(0, lambda: self.info.config(text="خطا در بررسی"))
        threading.Thread(target=work, daemon=True).start()

    def remove_selected(self):
        selected = [p for p in self.items if p.get("selected", False)]
        if not selected:
            messagebox.showinfo("حذف", "ابتدا مربع کنار ردیف کالاهای موردنظر را تیک بزنید.")
            return
        if not messagebox.askyesno("حذف انتخاب‌شده", f"{len(selected)} کالا حذف شود؟"):
            return
        self.items = [p for p in self.items if not p.get("selected", False)]
        save_products(self.items)
        self.selected_index = None
        self.refresh()

    def check_all(self):
        threading.Thread(target=self._check_all, daemon=True).start()

    def _check_all(self):
        self.root.after(0, lambda: self.info.config(text="در حال بررسی قیمت‌ها…"))
        changed = []
        for p in self.items:
            try:
                title, new, seller, second_price, second_seller, unavailable, image_url = fetch_product(p["id"])
                old = p.get("price")
                old_seller = p.get("seller") or "—"
                new_seller = seller or "—"
                old_unavailable = old is None
                p["title"] = title
                # Seller is recalculated on EVERY check. The cheapest seller
                # today may be different from the seller saved previously.
                p["seller"] = new_seller
                p["price"] = new
                p["second_price"] = second_price
                p["second_seller"] = second_seller or "—"
                if image_url:
                    p["image_url"] = image_url
                p["checked"] = datetime.now().strftime("%Y/%m/%d %H:%M")

                if unavailable:
                    p["change"] = "—" if old_unavailable else "ناموجود شد"
                    p["status"] = "⚪ ناموجود"
                    if not old_unavailable:
                        changed.append((title, old, None, "ناموجود"))
                elif old_unavailable:
                    p["change"] = f"↑ {new:,}"
                    p["status"] = "🟢 دوباره موجود شد"
                    changed.append((title, None, new, "موجود شد"))
                elif new < old:
                    p["change"] = f"↓ {old-new:,}"
                    p["status"] = "🔻 کاهش قیمت"
                    changed.append((title, old, new, "کاهش"))
                elif new > old:
                    p["change"] = f"↑ {new-old:,}"
                    p["status"] = "🔺 افزایش قیمت"
                    changed.append((title, old, new, "افزایش"))
                else:
                    p["change"] = "—"
                    p["status"] = "🟢 بدون تغییر"

                # Even when the price is identical, a different seller can
                # become the cheapest offer. Record that change separately.
                if (not unavailable and old is not None and
                        old_seller != "—" and new_seller != "—" and
                        old_seller != new_seller):
                    p["status"] = "🔄 تغییر فروشنده" if new == old else p["status"]
                    changed.append((title, old_seller, new_seller, "فروشنده"))
            except HTTPError as exc:
                p["status"] = f"⚠ HTTP {exc.code}"
                p["checked"] = datetime.now().strftime("%Y/%m/%d %H:%M")
            except (URLError, socket.timeout, TimeoutError) as exc:
                p["status"] = "⚠ خطای شبکه"
                p["checked"] = datetime.now().strftime("%Y/%m/%d %H:%M")
            except Exception as exc:
                p["status"] = "⚠ خطا در بررسی"
                p["checked"] = datetime.now().strftime("%Y/%m/%d %H:%M")
        save_products(self.items)
        self.root.after(0, self.refresh)
        if changed:
            text = "\n\n".join(
                f"{t}\n{('ناموجود شد' if typ == 'ناموجود' else 'دوباره موجود شد' if typ == 'موجود شد' else f'فروشنده: {old} → {new}' if typ == 'فروشنده' else f'{typ}: {old:,} → {new:,} تومان')}"
                for t, old, new, typ in changed
            )
            self.root.after(0, lambda: messagebox.showinfo("🔔 تغییر قیمت", text))
        self.root.after(0, lambda: self.info.config(text="آخرین بررسی انجام شد"))




# ---------------------- My Digi graphical web edition ----------------------
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote
import threading as _web_threading
import webbrowser as _webbrowser
import subprocess as _subprocess

WEB_PORT = 0

WEB_CHECK_LOCK = threading.Lock()
WEB_CHECK_PROGRESS = {"running": False, "completed": 0, "total": 0, "failed": 0, "current": "", "finished": False, "finished_at": None, "state": None, "error": None, "engine_error": None, "last_item_error": ""}



def _best_supplier_for_web(item, all_suppliers=False):
    ref = load_reference()
    matches=[]
    pid=str(item.get("id") or item.get("product_id") or "").strip()
    puuid=str(item.get("uuid") or "").strip()
    for supplier in ref.get("suppliers", []):
        label=((str(supplier.get("first_name", "")) + " " + str(supplier.get("last_name", ""))).strip() or supplier.get("company") or "بدون نام")
        for prod in supplier.get("products", []):
            link=str(prod.get("digikala_url") or "").strip()
            mpid=extract_id(link)
            linked=str(prod.get("monitor_product_uuid") or "").strip()==puuid if puuid else False
            linked = linked or (pid and mpid and str(mpid)==pid)
            if linked and prod.get("price") not in (None, ""):
                try: matches.append((int(prod.get("price")), label, supplier.get("id"), prod.get("name") or ""))
                except Exception: pass
    matches.sort(key=lambda x:x[0])
    return matches if all_suppliers else (matches[0] if matches else None)



def load_monthly_reports():
    try:
        if not MONTHLY_REPORTS_FILE.exists():
            return []
        data=json.loads(MONTHLY_REPORTS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data,list) else []
    except Exception:
        return []


def save_monthly_reports(data):
    MONTHLY_REPORTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_month_track():
    try:
        if not MONTH_TRACK_FILE.exists():
            return {}
        data=json.loads(MONTH_TRACK_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data,dict) else {}
    except Exception:
        return {}


def save_month_track(data):
    MONTH_TRACK_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def current_jalali_month():
    stamp=today_jalali_text()
    parts=stamp.split("/")
    return (int(parts[0]), int(parts[1])) if len(parts)==3 else (None,None)


def current_jalali_full():
    return today_jalali_text()


def _month_title(jy, jm):
    names={1:"فروردین",2:"اردیبهشت",3:"خرداد",4:"تیر",5:"مرداد",6:"شهریور",7:"مهر",8:"آبان",9:"آذر",10:"دی",11:"بهمن",12:"اسفند"}
    return f"{names.get(int(jm), jm)} {jy}"


def ensure_monthly_tracking(items):
    """Archive the completed Jalali month once the first check of a new month starts."""
    jy,jm=current_jalali_month()
    if jy is None:
        return None
    track=load_month_track()
    current_key=f"{jy:04d}/{jm:02d}"
    month_notice=None
    if not track.get("month"):
        track={"month":current_key,"start_date":current_jalali_full(),"products":{}}
    elif track.get("month") != current_key:
        old_key=str(track.get("month"))
        old_products=track.get("products") or {}
        reports=load_monthly_reports()
        if old_products:
            oy,om=map(int,old_key.split("/"))
            report={
                "month":old_key,
                "title":_month_title(oy,om),
                "start_date":track.get("start_date") or old_key+"/01",
                "end_date":track.get("last_date") or old_key+"/31",
                "products":list(old_products.values()),
            }
            # replace same month rather than duplicate
            reports=[r for r in reports if str(r.get("month"))!=old_key]
            reports.append(report)
            reports.sort(key=lambda r:str(r.get("month","")))
            save_monthly_reports(reports)
            month_notice=report["title"]
        track={"month":current_key,"start_date":current_jalali_full(),"products":{}}
    track["last_date"]=current_jalali_full()
    save_month_track(track)
    return month_notice


def record_monthly_price_event(item, old, new, direction):
    jy,jm=current_jalali_month()
    if jy is None or old is None or new is None or old==new:
        return
    track=load_month_track()
    key=f"{jy:04d}/{jm:02d}"
    if track.get("month") != key:
        return
    products=track.setdefault("products",{})
    uid=str(item.get("uuid") or item.get("id") or item.get("title") or "")
    rec=products.get(uid)
    today=current_jalali_full()
    title=item.get("custom_title") or item.get("title") or "محصول"
    if rec is None:
        rec={"uuid":item.get("uuid"),"product_id":item.get("id"),"title":title,"first_price":int(old),"last_price":int(new),"increase_count":0,"decrease_count":0,"events":[]}
    rec["title"]=title
    rec["last_price"]=int(new)
    rec["events"].append({"date":today,"from":int(old),"to":int(new),"direction":direction})
    if direction=="increase": rec["increase_count"]=int(rec.get("increase_count",0))+1
    if direction=="decrease": rec["decrease_count"]=int(rec.get("decrease_count",0))+1
    products[uid]=rec
    track["last_date"]=today
    save_month_track(track)


def monthly_report_payload():
    jy,jm=current_jalali_month()
    current_key=f"{jy:04d}/{jm:02d}" if jy is not None else ""
    reports=load_monthly_reports()
    # Show archived months plus the currently active month as a live report.
    track=load_month_track()
    out=list(reports)
    if track.get("month")==current_key:
        out.append({"month":current_key,"title":_month_title(jy,jm),"start_date":track.get("start_date"),"end_date":track.get("last_date"),"products":list((track.get("products") or {}).values()),"active":True})
    out.sort(key=lambda r:str(r.get("month","")), reverse=True)
    return out



def _change_is_fresh(item, now=None):
    ts=item.get("change_at")
    if not ts:
        return False
    try:
        stamp=datetime.fromisoformat(str(ts))
    except Exception:
        return False
    now=now or datetime.now()
    return (now-stamp).total_seconds() < 7*24*60*60


def _visible_change_fields(item):
    if not _change_is_fresh(item):
        return "—", "muted", ""
    direction=item.get("change_direction")
    amount=item.get("change_amount")
    if direction=="increase":
        return (f"↑ {int(amount):,}" if amount else "↑", "red", "increase")
    if direction=="decrease":
        return (f"↓ {int(amount):,}" if amount else "↓", "green", "decrease")
    return "—", "muted", ""


def current_month_summary(items=None):
    if items is None:
        items=load_products()
    jy,jm=current_jalali_month()
    key=f"{jy:04d}/{jm:02d}" if jy is not None else ""
    track=load_month_track()
    if track.get("month")!=key:
        return {"month":key,"increase_products":0,"decrease_products":0,"increase_events":0,"decrease_events":0}
    products=list((track.get("products") or {}).values())
    increase_products=sum(int(r.get("increase_count",0))>0 for r in products)
    decrease_products=sum(int(r.get("decrease_count",0))>0 for r in products)
    increase_events=sum(int(r.get("increase_count",0)) for r in products)
    decrease_events=sum(int(r.get("decrease_count",0)) for r in products)
    # For the pie/donut distribution, each monitored product occupies exactly
    # one segment based on its latest price-change direction in the current
    # Jalali month; products with no event this month are "fixed".
    distribution_increase=0
    distribution_decrease=0
    for r in products:
        events=r.get("events") or []
        last_direction=(events[-1].get("direction") if events and isinstance(events[-1],dict) else None)
        if last_direction=="increase":
            distribution_increase += 1
        elif last_direction=="decrease":
            distribution_decrease += 1
    return {
        "month":key,
        "increase_products":increase_products,
        "decrease_products":decrease_products,
        "increase_events":increase_events,
        "decrease_events":decrease_events,
        "distribution_increase_products":distribution_increase,
        "distribution_decrease_products":distribution_decrease,
        "distribution_fixed_products":max(0,len(items)-distribution_increase-distribution_decrease),
        "month_name":_month_title(jy,jm).rsplit(" ",1)[0],
    }


def _web_state():
    accounting_notice, accounting_reports = ensure_accounting_monthly_reports()
    items=load_products()
    reminders=[]
    try:
        today=date.today()
        ref=load_reference()
        reminder_state=load_reminder_state()
        for supplier in ref.get("suppliers", []):
            label=_ref_supplier_label(supplier)
            # Legacy supplier-level reminder remains supported.
            raw=str(supplier.get("next_check") or "").strip()
            due=parse_reminder_date(raw)
            if due is not None and due <= today:
                jy,jm,jd=gregorian_to_jalali(due.year,due.month,due.day); jdate=f"{jy:04d}/{jm:02d}/{jd:02d}"
                state="امروز" if due==today else f"{(today-due).days} روز گذشته"
                rid=f"{supplier.get('id') or label}|{jdate}"
                reminders.append({"id":rid,"supplier":label,"product":"","date":jdate,"state":state,"read":bool(reminder_state.get(rid, False))})
            # Product-specific scheduled inquiries. They stay until completed.
            for q in supplier.get("quotes",[]) or []:
                if not isinstance(q,dict) or q.get("completed"): continue
                rawq=str(q.get("due_date") or q.get("date") or "").strip(); qdue=parse_reminder_date(rawq)
                if qdue is None or qdue > today: continue
                jy,jm,jd=gregorian_to_jalali(qdue.year,qdue.month,qdue.day); jdate=f"{jy:04d}/{jm:02d}/{jd:02d}"
                state="امروز" if qdue==today else f"{(today-qdue).days} روز گذشته"
                rid=f"refquote|{q.get('id')}"
                reminders.append({"id":rid,"supplier":label,"product":q.get("product_name") or "کالا","date":jdate,"state":state,"read":bool(reminder_state.get(rid, False))})
        reminders.sort(key=lambda x:x.get("date", ""))
    except Exception:
        reminders=[]
    month_summary=current_month_summary(items)
    # Keep the existing chart semantics for `ups`/`downs`; the header KPIs use
    # the separate monthly_summary values.
    ups=sum((x.get("change_direction")=="increase" and _change_is_fresh(x)) for x in items)
    downs=sum((x.get("change_direction")=="decrease" and _change_is_fresh(x)) for x in items)
    new=sum("موجود شد" in str(x.get("status","")) for x in items)
    active=sum(x.get("price") is not None for x in items)
    rows=[]
    for x in items:
        purchase=x.get("purchase"); profit=x.get("profit"); commission=x.get("commission"); ancillary=x.get("ancillary",0) or 0
        effective_commission=commission if commission not in (None,"") else load_settings().get("digikala",{}).get("default_commission",15.0)
        calc_item=dict(x)
        if commission in (None,""): calc_item["commission"]=effective_commission
        mine=digikala_my_price(purchase,profit,effective_commission,ancillary) if my_price_inputs_ready(calc_item) else None
        best=_best_supplier_for_web(x)
        status=str(x.get("status",""))
        change, change_color, change_direction = _visible_change_fields(x)
        rows.append({
            "uuid":x.get("uuid"),"id":x.get("id") or x.get("product_id"),"title":x.get("custom_title") or x.get("title") or "محصول",
            "image":x.get("image_url"),"market":x.get("price"),"seller":x.get("seller") or "—","second":x.get("second_price"),
            "second_seller":x.get("second_seller") or "—","change":change,"change_color":change_color,"change_direction":change_direction,"status":status,
            "checked":x.get("checked") or "—","purchase":purchase,"profit":profit,"ancillary":ancillary,"commission":commission,"commission_effective":effective_commission,
            "mine":mine,"best_supplier":best[1] if best else None,"best_supplier_price":best[0] if best else None,"selected":bool(x.get("selected")),"price_history":list(x.get("price_history") or [])[-365:],"change_at":x.get("change_at")
        })
    return {"version":APP_VERSION,"items":rows,"stats":{"count":len(items),"ups":ups,"downs":downs,"new":new,"active":active},"reminders":reminders,"market_trend":load_market_trend(),"reference":load_reference(),"accounting":load_accounting(),"accounting_reports":accounting_reports,"accounting_report_notice":accounting_notice,"monthly_reports":monthly_report_payload(),"monthly_summary":month_summary,"settings":load_settings()}


def _record_monitor_price(item, price):
    """Store one monitor price point per Persian calendar day.

    Repeated checks on the same day update today's point instead of creating
    multiple samples. This history feeds the selected-product 30-day chart.
    """
    try:
        price = int(price) if price is not None else None
    except Exception:
        price = None
    if price is None or price <= 0:
        return
    today = today_jalali_text()
    hist = item.setdefault("price_history", [])
    by_day = {}
    for rec in hist:
        if not isinstance(rec, dict):
            continue
        try:
            pr = int(str(rec.get("price")).replace(",", "").strip())
        except Exception:
            continue
        raw = str(rec.get("date") or "").strip()[:10].replace("-", "/")
        day = raw
        try:
            parts = day.split("/")
            if len(parts) == 3:
                y, m, d = map(int, parts)
                if y >= 1700:
                    jy, jm, jd = gregorian_to_jalali(y, m, d)
                    day = f"{jy:04d}/{jm:02d}/{jd:02d}"
        except Exception:
            pass
        if re.fullmatch(r"1[34-5]\d{2}/\d{2}/\d{2}", day):
            by_day[day] = pr
    by_day[today] = price
    dates = sorted(by_day.keys())[-365:]
    item["price_history"] = [{"date": d, "price": by_day[d]} for d in dates]


def _accounting_state():
    data=load_accounting()
    return data


def _reference_state():
    """JSON-safe reference library for the graphical UI, including monitor links."""
    data = load_reference()
    products = load_products()
    monitor = []
    for item in products:
        monitor.append({
            "uuid": item.get("uuid"), "id": item.get("id") or item.get("product_id"),
            "title": item.get("custom_title") or item.get("title") or "محصول",
            "purchase": item.get("purchase"), "profit": item.get("profit"),
            "stock": item.get("stock"), "url": item.get("url", ""),
            "reference_supplier_ids": item.get("reference_supplier_ids") or [],
            "reference_price_alert": item.get("reference_price_alert"),
        })
    return {"ok": True, "data": data, "monitor": monitor}


def _ref_supplier_label(supplier):
    parts = [str(supplier.get("first_name", "") or "").strip(), str(supplier.get("last_name", "") or "").strip()]
    name = " ".join(x for x in parts if x).strip()
    return name or str(supplier.get("company") or supplier.get("name") or supplier.get("full_name") or "بدون نام").strip()


def _ref_find_monitor_matches(ref_product, items):
    ref_uuid = str(ref_product.get("monitor_product_uuid") or "").strip()
    if ref_uuid:
        for idx, item in enumerate(items):
            if str(item.get("uuid") or "").strip() == ref_uuid:
                return [idx]
    ref_url = str(ref_product.get("digikala_url", "") or "").strip()
    ref_pid = extract_id(ref_url)
    if ref_pid:
        ref_pid = str(ref_pid).strip()
        matches = []
        for idx, item in enumerate(items):
            item_pid = item.get("id") or item.get("product_id") or extract_id(item.get("url", ""))
            if item_pid is not None and str(item_pid).strip() == ref_pid:
                matches.append(idx)
        if matches:
            return matches
    durl = normalize_text(ref_url)
    if durl:
        matches = [idx for idx,item in enumerate(items) if normalize_text(item.get("url", "")) == durl]
        if matches:
            return matches
    name = normalize_text(ref_product.get("name", ""))
    if name:
        return [idx for idx,item in enumerate(items) if (lambda title: bool(title and (name in title or title in name)))(normalize_text(item.get("custom_title") or item.get("title", "")))]
    return []


def _reference_supplier_notes(supplier):
    """Return normalized supplier-scoped note records, migrating the legacy single note."""
    notes=supplier.get("notes_list")
    if not isinstance(notes,list): notes=[]
    notes=[dict(x) for x in notes if isinstance(x,dict)]
    legacy=str(supplier.get("notes") or "").strip()
    if legacy and not any(str(x.get("text") or "").strip()==legacy for x in notes):
        notes.insert(0,{"id":f"note-legacy-{supplier.get('id')}","text":legacy,"date":datetime.now().strftime("%Y-%m-%d %H:%M")})
    return notes

def _reference_mark_product_quotes_done(supplier, product_id, reason=""):
    """Complete pending supplier-specific inquiry reminders for one product."""
    changed=False
    for q in supplier.setdefault("quotes",[]):
        if str(q.get("product_id") or "") == str(product_id) and not q.get("completed"):
            q["completed"]=True; q["completed_at"]=datetime.now().strftime("%Y-%m-%d %H:%M"); q["completion_reason"]=reason or "انجام شد"; changed=True
    return changed

def _reference_record_snapshot(product, reason=""):
    """Keep a dated price+profit snapshot for the supplier/product history."""
    try: price=int(str(product.get("price")).replace(",","").replace("٬","")) if product.get("price") not in (None,"") else None
    except Exception: price=None
    try: profit=int(str(product.get("my_profit")).replace(",","").replace("٬","")) if product.get("my_profit") not in (None,"") else None
    except Exception: profit=None
    hist=product.setdefault("value_history",[])
    now=jalali_timestamp_text()
    last=hist[-1] if hist else None
    if last and last.get("price")==price and last.get("profit")==profit:
        return False
    hist.append({"date":now,"price":price,"profit":profit,"reason":reason or "تغییر اطلاعات"})
    return True

def _reference_history_rows(product):
    """Build contiguous validity ranges from stored snapshots."""
    hist=list(product.get("value_history") or [])
    if not hist:
        price_hist=list(product.get("price_history") or [])
        if price_hist:
            return [{"from":x.get("date",""),"to":"اکنون","price":x.get("price"),"profit":product.get("my_profit")} for x in price_hist]
        return []
    rows=[]
    for i,x in enumerate(hist):
        rows.append({"from":x.get("date",""),"to":hist[i+1].get("date","") if i+1<len(hist) else "اکنون","price":x.get("price"),"profit":x.get("profit")})
    return rows


def _reference_api_action(payload):
    """Perform a graphical reference-library mutation without opening a Tk window."""
    action = str(payload.get("action") or "").strip()
    data = load_reference()
    suppliers = data.setdefault("suppliers", [])
    if action == "save":
        incoming = payload.get("data")
        if not isinstance(incoming, dict):
            raise ValueError("اطلاعات مرجع من معتبر نیست.")
        incoming.setdefault("suppliers", [])
        save_reference(incoming)
        return {"ok": True}
    if action == "save_supplier":
        sid = str(payload.get("id") or "").strip()
        vals = payload.get("supplier") or {}
        if not str(vals.get("company") or vals.get("first_name") or vals.get("last_name") or "").strip():
            raise ValueError("نام یا شرکت تأمین‌کننده الزامی است.")
        vals = dict(vals)
        if sid:
            s = next((x for x in suppliers if str(x.get("id")) == sid), None)
            if not s: raise ValueError("تأمین‌کننده پیدا نشد.")
            vals.setdefault("id", sid); vals.setdefault("products", s.get("products", [])); vals.setdefault("quotes", s.get("quotes", [])); s.update(vals)
            # The supplier-form note remains supplier-scoped and is also visible in the notes panel.
            legacy=str(vals.get("notes") or "").strip()
            notes=s.setdefault("notes_list", [])
            legacy_note=next((n for n in notes if str(n.get("id") or "").startswith("note-legacy-")), None)
            if legacy:
                if legacy_note: legacy_note["text"]=legacy
                else: notes.insert(0,{"id":f"note-legacy-{sid}","text":legacy,"date":datetime.now().strftime("%Y-%m-%d %H:%M")})
            elif legacy_note:
                notes[:]=[n for n in notes if n is not legacy_note]
        else:
            vals["id"] = f"sup-{int(datetime.now().timestamp()*1000)}"
            vals.setdefault("products", []); vals.setdefault("quotes", [])
            vals.setdefault("notes_list", [])
            if str(vals.get("notes") or "").strip():
                vals["notes_list"].append({"id":f"note-legacy-{vals['id']}","text":str(vals.get("notes") or "").strip(),"date":datetime.now().strftime("%Y-%m-%d %H:%M")})
            suppliers.append(vals)
        save_reference(data); return {"ok": True, "id": vals["id"]}
    if action == "delete_supplier":
        sid = str(payload.get("id") or "").strip()
        suppliers[:] = [x for x in suppliers if str(x.get("id")) != sid]
        save_reference(data); return {"ok": True}
    sid = str(payload.get("supplier_id") or "").strip()
    supplier = next((x for x in suppliers if str(x.get("id")) == sid), None)
    if not supplier: raise ValueError("تأمین‌کننده پیدا نشد.")
    products = supplier.setdefault("products", [])
    if action == "save_product":
        pid = str(payload.get("id") or "").strip()
        vals = dict(payload.get("product") or {})
        vals["name"] = str(vals.get("name") or "").strip()
        if not vals["name"]: raise ValueError("نام کالا الزامی است.")
        for key in ("price", "stock", "my_profit"):
            v = vals.get(key)
            if v in (None, ""): vals[key] = None if key in ("price", "my_profit") else 0
            else:
                try: vals[key] = int(str(v).replace(",", "").replace("٬", ""))
                except Exception: vals[key] = None if key in ("price", "my_profit") else 0
        cv = vals.get("commission")
        if cv in (None, ""):
            vals["commission"] = None
        else:
            try:
                vals["commission"] = float(str(cv).replace(",", ".").replace("٪", "").replace("%", "").strip())
            except Exception:
                vals["commission"] = None
        vals["stock_reliable"] = bool(vals.get("stock_reliable", True))
        vals.setdefault("price_tiers", []); vals.setdefault("notes", ""); vals.setdefault("last_quote", "")
        if pid:
            q = next((x for x in products if str(x.get("id")) == pid), None)
            if not q: raise ValueError("کالا پیدا نشد.")
            old_price=q.get("price"); old_profit=q.get("my_profit"); old_commission=q.get("commission")
            q.update(vals); q["id"] = pid
            price_changed=old_price != q.get("price"); profit_changed=old_profit != q.get("my_profit"); commission_changed=old_commission != q.get("commission")
            if price_changed:
                q.setdefault("alerts", []).append({"date": today_text(), "type":"price_change", "from":old_price, "to":q.get("price")})
            if price_changed or profit_changed or commission_changed:
                _reference_record_snapshot(q, "ویرایش کالا")
                _reference_mark_product_quotes_done(supplier, pid, "تغییر قیمت، سود یا کمیسیون")
                # Keep the linked monitor product in sync with explicit reference edits.
                items=load_products(); linked=next((m for m in items if str(m.get("uuid") or "")==str(q.get("monitor_product_uuid") or "")),None)
                if linked is not None:
                    if q.get("price") not in (None,""): linked["purchase"]=int(q["price"])
                    if q.get("my_profit") not in (None,""): linked["profit"]=int(q["my_profit"])
                    linked["commission"]=q.get("commission")
                    save_products(items)
        else:
            vals["id"] = f"prd-{int(datetime.now().timestamp()*1000)}"
            vals.update({"monitor_product_id":None,"monitor_product_uuid":None,"price_history":[],"stock_history":[],"history_notes":[],"alerts":[],"value_history":[]})
            products.append(vals); pid=vals["id"]; _reference_record_snapshot(vals, "ثبت اولیه")
        save_reference(data); return {"ok":True,"id":pid}
    if action == "delete_product":
        pid=str(payload.get("id") or "").strip(); supplier["products"]=[x for x in products if str(x.get("id")) != pid]; save_reference(data); return {"ok":True}
    if action == "save_supplier_notes":
        supplier["notes"] = str(payload.get("notes") or ""); save_reference(data); return {"ok":True}
    if action == "add_supplier_note":
        text=str(payload.get("text") or "").strip()
        if not text: raise ValueError("متن یادداشت را وارد کنید.")
        supplier.setdefault("notes_list",[]).append({"id":f"note-{int(datetime.now().timestamp()*1000)}","text":text,"date":datetime.now().strftime("%Y-%m-%d %H:%M")})
        save_reference(data); return {"ok":True}
    if action == "edit_supplier_note":
        nid=str(payload.get("note_id") or "")
        text=str(payload.get("text") or "").strip()
        note=next((x for x in _reference_supplier_notes(supplier) if str(x.get("id"))==nid),None)
        if not note or not text: raise ValueError("یادداشت پیدا نشد.")
        note["text"]=text
        supplier["notes_list"]=[x for x in _reference_supplier_notes(supplier) if str(x.get("id"))!=nid]+[note]
        save_reference(data); return {"ok":True}
    if action == "delete_supplier_note":
        nid=str(payload.get("note_id") or "")
        notes=[x for x in _reference_supplier_notes(supplier) if str(x.get("id"))!=nid]
        supplier["notes_list"]=notes
        if nid.startswith("note-legacy-"): supplier["notes"]=""
        save_reference(data); return {"ok":True}
    if action == "schedule_quote":
        pid=str(payload.get("id") or "").strip(); p=next((x for x in products if str(x.get("id"))==pid),None)
        if not p: raise ValueError("کالا پیدا نشد.")
        due=str(payload.get("due_date") or "").strip()
        if not due or not parse_reminder_date(due): raise ValueError("تاریخ استعلام معتبر نیست.")
        q={"id":f"quote-{int(datetime.now().timestamp()*1000)}","product_id":pid,"product_name":p.get("name","کالا"),"date":due,"due_date":due,"subject":str(payload.get("subject") or "استعلام قیمت و سود"),"notes":str(payload.get("notes") or ""),"completed":False,"price":p.get("price"),"profit":p.get("my_profit"),"stock":p.get("stock",0)}
        supplier.setdefault("quotes",[]).append(q); save_reference(data); return {"ok":True,"id":q["id"]}
    if action == "quote_product":
        pid=str(payload.get("id") or "").strip(); p=next((x for x in products if str(x.get("id"))==pid),None)
        if not p: raise ValueError("کالا پیدا نشد.")
        old=p.get("price"); old_profit=p.get("my_profit"); price=payload.get("price",p.get("price")); profit=payload.get("profit",p.get("my_profit")); stock=payload.get("stock",p.get("stock",0))
        try: price=int(str(price).replace(",","").replace("٬","")) if price not in (None,"") else None
        except Exception: price=p.get("price")
        try: profit=int(str(profit).replace(",","").replace("٬","")) if profit not in (None,"") else None
        except Exception: profit=p.get("my_profit")
        try: stock=int(str(stock).replace(",","").replace("٬",""))
        except Exception: stock=p.get("stock",0)
        p["price"]=price; p["my_profit"]=profit; p["stock"]=stock
        _reference_record_snapshot(p, "ثبت استعلام")
        p.setdefault("price_history",[])
        if old not in (None,price): p["price_history"].append({"date":today_text(),"price":price})
        p.setdefault("stock_history",[]).append({"date":today_text(),"stock":stock})
        p.setdefault("alerts",[])
        if old not in (None,price) or old_profit != profit:
            p["alerts"].append({"date":jalali_timestamp_text(),"type":"value_change","price_from":old,"price_to":price,"profit_from":old_profit,"profit_to":profit})
        qid=str(payload.get("quote_id") or "")
        qmatch=next((q for q in supplier.setdefault("quotes",[]) if str(q.get("id") or "")==qid),None) if qid else None
        qrec={"id":qid or f"quote-{int(datetime.now().timestamp()*1000)}","product_id":p.get("id"),"product_name":p.get("name","کالا"),"date":datetime.now().strftime("%Y-%m-%d %H:%M"),"subject":str(payload.get("subject") or "تماس و استعلام قیمت/سود"),"price":price,"profit":profit,"stock":stock,"notes":str(payload.get("notes") or ""),"completed":True,"completed_at":datetime.now().strftime("%Y-%m-%d %H:%M"),"completion_reason":"ثبت استعلام"}
        if qmatch: qmatch.update(qrec)
        else: supplier.setdefault("quotes",[]).append(qrec)
        _reference_mark_product_quotes_done(supplier, p.get("id"), "ثبت استعلام")
        items=load_products(); linked_uuid=str(p.get("monitor_product_uuid") or "").strip()
        linked=next((m for m in items if str(m.get("uuid") or "").strip()==linked_uuid),None)
        if linked is not None:
            if old not in (None,price) and price is not None and old is not None and int(price)>int(old):
                linked["reference_price_alert"]={"date":today_text(),"supplier":_ref_supplier_label(supplier),"old":int(old),"new":int(price),"impact_price":_purchase_impact_value(linked, price)}
            if price is not None: linked["purchase"]=int(price)
            if profit is not None: linked["profit"]=int(profit)
            save_products(items)
        save_reference(data); return {"ok":True}
    if action == "link_product":
        pid=str(payload.get("id") or "").strip(); p=next((x for x in products if str(x.get("id"))==pid),None)
        if not p: raise ValueError("کالا پیدا نشد.")
        items=load_products(); matches=_ref_find_monitor_matches(p,items)
        if not matches: return {"ok":False,"matched":False,"message":"کالای مشابهی در مانیتور اصلی پیدا نشد. از «افزودن به مانیتور» استفاده کنید."}
        idx=matches[0]; item=items[idx]
        p["monitor_product_uuid"]=item.get("uuid"); p["monitor_product_id"]=item.get("id") or item.get("product_id")
        if p.get("price") not in (None,""): item["purchase"]=int(p["price"])
        if p.get("my_profit") not in (None,""): item["profit"]=int(p["my_profit"])
        item["commission"]=p.get("commission")
        item["reference_supplier_ids"]=list(dict.fromkeys((item.get("reference_supplier_ids") or [])+[supplier.get("id")]))
        save_products(items); save_reference(data)
        return {"ok":True,"matched":True,"monitor_uuid":item.get("uuid"),"purchase":item.get("purchase"),"profit":item.get("profit")}
    if action == "add_to_monitor":
        pid=str(payload.get("id") or "").strip(); p=next((x for x in products if str(x.get("id"))==pid),None)
        if not p: raise ValueError("کالا پیدا نشد.")
        url=str(p.get("digikala_url") or "").strip()
        if not url: raise ValueError("برای این کالا لینک دیجی‌کالا ثبت نشده است.")
        items=load_products(); product_id=extract_id(url)
        if not product_id: raise ValueError("لینک دیجی‌کالا معتبر نیست.")
        if any(str(x.get("id"))==str(product_id) for x in items): return {"ok":False,"message":"این کالا قبلاً در مانیتور وجود دارد."}
        try: title,price,seller,second_price,second_seller,unavailable,image_url=fetch_product(product_id); pending=False
        except Exception: title=f"محصول DKP-{product_id}"; price=None; seller="—"; second_price=None; second_seller="—"; unavailable=False; image_url=None; pending=True
        item={"uuid":str(uuid.uuid4()),"id":product_id,"url":url,"title":title,"price":price,"seller":seller or "—","second_price":second_price,"second_seller":second_seller or "—","change":"—","change_direction":None,"change_amount":None,"change_at":None,"purchase":p.get("price"),"profit":p.get("my_profit"),"ancillary":0,"commission":p.get("commission"),"status":"⚠ نیاز به بررسی" if pending else ("⚪ ناموجود" if unavailable else "🟢 فعال"),"checked":datetime.now().strftime("%Y/%m/%d %H:%M"),"image_url":image_url,"selected":False,"price_history":([{"date":today_jalali_text(),"price":price}] if price is not None else []),"reference_supplier_ids":[supplier.get("id")]}
        items.append(item); p["monitor_product_uuid"]=item["uuid"]; p["monitor_product_id"]=product_id; save_products(items); save_reference(data); return {"ok":True,"uuid":item["uuid"],"pending":pending}
    raise ValueError("عملیات مرجع من شناخته نشد.")


def _purchase_impact_value(item, new_purchase):
    try:
        return digikala_my_price(int(new_purchase), float(item.get("profit") or 0), float(item.get("commission") or 0), int(item.get("ancillary") or 0))
    except Exception:
        return None



def _web_downloads_dir():
    path=Path.home()/"Downloads"
    path.mkdir(parents=True,exist_ok=True)
    return path


def _capture_my_digi_window():
    """Capture the visible My Digi app window on Windows without touching app state."""
    if ImageGrab is None:
        raise RuntimeError("کتابخانه Pillow برای اسکرین‌شات در دسترس نیست.")
    if os.name != "nt":
        return ImageGrab.grab()
    try:
        import ctypes
        from ctypes import wintypes
        user32=ctypes.windll.user32
        candidates=[]
        WNDENUMPROC=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
        def cb(hwnd,lparam):
            if not user32.IsWindowVisible(hwnd): return True
            n=user32.GetWindowTextLengthW(hwnd)
            if n<=0: return True
            buf=ctypes.create_unicode_buffer(n+1); user32.GetWindowTextW(hwnd,buf,n+1)
            title=buf.value.strip()
            if title and "My Digi" in title:
                rect=wintypes.RECT()
                if user32.GetWindowRect(hwnd,ctypes.byref(rect)):
                    candidates.append((hwnd,title,(rect.left,rect.top,rect.right,rect.bottom)))
            return True
        user32.EnumWindows(WNDENUMPROC(cb),0)
        if candidates:
            hwnd,title,(l,t,r,b)=max(candidates,key=lambda x:max(0,x[2][2]-x[2][0])*max(0,x[2][3]-x[2][1]))
            if r>l and b>t:
                return ImageGrab.grab(bbox=(l,t,r,b),all_screens=True)
    except Exception:
        pass
    return ImageGrab.grab(all_screens=True)



def _is_frozen_app():
    return bool(getattr(sys, "frozen", False))


def _install_dir():
    return Path(sys.executable if _is_frozen_app() else __file__).resolve().parent


def _updater_executable():
    # Run the helper from writable AppData, not Program Files, so the helper can
    # safely replace the installed application while it is still running.
    bundled = _install_dir() / "My Digi Updater.exe"
    target_dir = APP_DIR / "Updater"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "My Digi Updater.exe"
    if bundled.exists():
        try:
            if (not target.exists()) or bundled.stat().st_size != target.stat().st_size or bundled.stat().st_mtime > target.stat().st_mtime:
                shutil.copy2(bundled, target)
        except Exception:
            pass
    if target.exists():
        return target
    # Development/source fallback.
    p2 = Path(__file__).with_name("mydigi_updater.py")
    return p2 if p2.exists() else bundled


def _github_repo():
    repo = str(UPDATE_REPO or "").strip().strip("/")
    try:
        cfg = _install_dir() / "update_config.json"
        if cfg.exists():
            data = json.loads(cfg.read_text(encoding="utf-8"))
            configured_repo = str(data.get("repo") or "").strip().strip("/")
            if configured_repo:
                repo = configured_repo
    except Exception:
        pass
    return repo


def _urlopen_resilient(request, timeout=20):
    """Try Windows/system networking first, then bypass a broken proxy."""
    first_error = None
    try:
        return urlopen(request, timeout=timeout)
    except Exception as exc:
        first_error = exc
    try:
        return build_opener(ProxyHandler({})).open(request, timeout=timeout)
    except Exception as direct_error:
        raise RuntimeError(f"اتصال معمول: {first_error} | اتصال مستقیم: {direct_error}") from direct_error


def _github_latest_release():
    repo = _github_repo()
    if not repo or "/" not in repo:
        return None, "انتشار آنلاین GitHub هنوز برای این نسخه تنظیم نشده است."
    headers={
        "User-Agent":"My-Digi-Updater/2.1",
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28",
    }
    api_url = f"{UPDATE_API_BASE}/repos/{repo}/releases/latest"
    req = Request(api_url, headers=headers)
    try:
        with _urlopen_resilient(req, timeout=20) as r:
            release = json.loads(r.read().decode("utf-8-sig"))
    except Exception as api_error:
        # Some networks block api.github.com while github.com itself works.
        latest_req = Request(
            f"https://github.com/{repo}/releases/latest",
            headers={"User-Agent":"My-Digi-Updater/2.1"},
        )
        try:
            with _urlopen_resilient(latest_req, timeout=20) as r:
                final_url = r.geturl()
                html = r.read().decode("utf-8", "replace")
        except Exception as page_error:
            raise RuntimeError(f"GitHub API: {api_error} | GitHub Releases: {page_error}") from page_error
        match = re.search(r"/releases/tag/([^\"?#/]+)", final_url)
        if not match:
            match = re.search(r"/releases/tag/([^\"?#/]+)", html)
        if not match:
            return None, "هنوز Release منتشرشده‌ای در GitHub پیدا نشد."
        tag_raw = unquote(match.group(1))
        base = f"https://github.com/{repo}/releases/download/{tag_raw}"
        installer_url = f"{base}/My-Digi-Setup.exe"
        checksum = ""
        try:
            checksum_req = Request(f"{base}/My-Digi-Setup.exe.sha256", headers={"User-Agent":"My-Digi-Updater/2.1"})
            with _urlopen_resilient(checksum_req, timeout=15) as r:
                checksum_text = r.read(4096).decode("ascii", "ignore")
            checksum_match = re.search(r"\b[0-9a-fA-F]{64}\b", checksum_text)
            if checksum_match:
                checksum = checksum_match.group(0).lower()
        except Exception:
            pass
        return {
            "version": tag_raw.lstrip("vV"),
            "body": "",
            "html_url": f"https://github.com/{repo}/releases/tag/{tag_raw}",
            "installer": {"name":"My-Digi-Setup.exe", "url":installer_url, "size":None, "sha256":checksum},
            "published_at": None,
        }, None

    tag_raw = str(release.get("tag_name") or "").strip()
    if not tag_raw:
        return None, "آخرین Release گیت‌هاب شماره نسخه ندارد."

    assets = release.get("assets") or []
    installer_asset = next(
        (a for a in assets if str(a.get("name") or "").lower() == "my-digi-setup.exe"),
        None,
    )
    if not installer_asset:
        installer_asset = next(
            (a for a in assets if str(a.get("name") or "").lower().endswith(".exe")),
            None,
        )
    if not installer_asset:
        return None, "فایل نصب EXE در آخرین Release پیدا نشد."

    checksum = ""
    checksum_asset = next(
        (a for a in assets if str(a.get("name") or "").lower() == "my-digi-setup.exe.sha256"),
        None,
    )
    if checksum_asset and checksum_asset.get("browser_download_url"):
        try:
            checksum_req = Request(checksum_asset["browser_download_url"], headers={"User-Agent":"My-Digi-Updater/2.1"})
            with _urlopen_resilient(checksum_req, timeout=15) as r:
                checksum_text = r.read(4096).decode("ascii", "ignore")
            match = re.search(r"\b[0-9a-fA-F]{64}\b", checksum_text)
            if match:
                checksum = match.group(0).lower()
        except Exception:
            pass

    installer = {
        "name": str(installer_asset.get("name") or "My-Digi-Setup.exe"),
        "url": installer_asset.get("browser_download_url"),
        "size": installer_asset.get("size"),
        "sha256": checksum,
    }
    return {
        "version": tag_raw.lstrip("vV"),
        "body": str(release.get("body") or ""),
        "html_url": release.get("html_url"),
        "installer": installer,
        "published_at": release.get("published_at"),
    }, None


def _version_tuple(v):
    parts = re.findall(r"\d+", str(v or ""))
    return tuple(int(x) for x in parts[:4]) or (0,)


def _launch_updater(mode, extra=None):
    extra = extra or []
    exe = _updater_executable()
    args = [str(exe), f"--{mode}", "--pid", str(os.getpid()), "--install-dir", str(_install_dir()), "--data-dir", str(APP_DIR), "--current-version", str(APP_VERSION)] + [str(x) for x in extra]
    if not exe.exists():
        raise RuntimeError("فایل به‌روزرسان برنامه پیدا نشد.")
    if _is_frozen_app() and os.name == "nt":
        _subprocess.Popen(args, cwd=str(_install_dir()), creationflags=getattr(_subprocess, "CREATE_NO_WINDOW", 0))
    else:
        _subprocess.Popen([sys.executable] + args[1:], cwd=str(_install_dir()))


def _update_state():
    versions = APP_DIR / "versions"
    backups=[]
    if versions.exists():
        for p in versions.iterdir():
            if p.is_dir(): backups.append(p.name)
    backups.sort(reverse=True)
    last_update={}
    try:
        last_update=json.loads((APP_DIR/"update-state.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"current": APP_VERSION, "backups": backups[:3], "can_rollback": bool(backups), "last_update":last_update}


MANUAL_BACKUP_DIR = APP_DIR / "backups"
BACKUP_EXCLUDES = {"versions", "backups", "Updater", "update.log", "installer.log", "startup-error.log", "update-state.json"}


def _safe_backup_name(prefix="manual"):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = f"{prefix}__{stamp}"
    candidate = base
    counter = 1
    while (MANUAL_BACKUP_DIR / candidate).exists():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


def _snapshot_user_data(prefix="manual"):
    MANUAL_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    name = _safe_backup_name(prefix)
    root = MANUAL_BACKUP_DIR / name
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=False)
    copied = 0
    try:
        for item in APP_DIR.iterdir():
            if item.name in BACKUP_EXCLUDES:
                continue
            target = data_dir / item.name
            if item.is_dir():
                shutil.copytree(item, target)
                copied += sum(1 for p in target.rglob("*") if p.is_file())
            elif item.is_file():
                shutil.copy2(item, target)
                copied += 1
        manifest = {
            "type": prefix,
            "app_version": APP_VERSION,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "files": copied,
        }
        (root / "backup.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return root
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise


def _backup_entries():
    result = []
    sources = [("manual", MANUAL_BACKUP_DIR), ("update", APP_DIR / "versions")]
    for kind, parent in sources:
        if not parent.exists():
            continue
        for root in parent.iterdir():
            data_dir = root / "data"
            if not root.is_dir() or not data_dir.is_dir():
                continue
            manifest = {}
            try:
                manifest = json.loads((root / "backup.json").read_text(encoding="utf-8"))
            except Exception:
                pass
            files = sum(1 for p in data_dir.rglob("*") if p.is_file())
            size = sum(p.stat().st_size for p in data_dir.rglob("*") if p.is_file())
            created = manifest.get("created_at") or datetime.fromtimestamp(root.stat().st_mtime).isoformat(timespec="seconds")
            result.append({
                "id": f"{kind}:{root.name}",
                "kind": kind,
                "name": root.name,
                "version": manifest.get("app_version") or manifest.get("version") or "—",
                "created_at": created,
                "files": files,
                "size": size,
            })
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return result


HEALTH_DATA_FILES = {
    DATA_FILE: list,
    REFERENCE_FILE: dict,
    MARKET_TREND_FILE: list,
    REMINDER_STATE_FILE: dict,
    ACCOUNTING_FILE: dict,
    ACCOUNTING_REPORTS_FILE: (dict, list),
    ACCOUNTING_MONTH_TRACK_FILE: dict,
    SETTINGS_FILE: dict,
    MONTHLY_REPORTS_FILE: (dict, list),
    MONTH_TRACK_FILE: dict,
}


def _health_item(key, title, status, value, detail, action=None):
    return {"key": key, "title": title, "status": status, "value": value, "detail": detail, "action": action}


def _health_diagnostics():
    """Run bounded, read-only checks used by the in-app health center."""
    checks = []
    checked_at = datetime.now().isoformat(timespec="seconds")

    # General connectivity is intentionally independent from GitHub so a blocked
    # update service does not make the whole internet look offline.
    try:
        sock = socket.create_connection(("www.digikala.com", 443), timeout=4)
        sock.close()
        checks.append(_health_item("internet", "اتصال اینترنت", "ok", "متصل", "ارتباط عمومی شبکه برقرار است."))
    except Exception as exc:
        checks.append(_health_item("internet", "اتصال اینترنت", "error", "قطع یا محدود", f"اتصال شبکه برقرار نشد: {exc}", "retry"))

    try:
        req = Request("https://api.digikala.com/v2/", headers={"User-Agent": "My-Digi-Health/1.0", "Accept": "application/json"})
        with urlopen(req, timeout=8) as response:
            response.read(256)
        checks.append(_health_item("digikala", "ارتباط با دیجی‌کالا", "ok", "سالم", "API دیجی‌کالا پاسخ معتبر داد."))
    except HTTPError as exc:
        # Any HTTP response proves the host/TLS path is reachable; 4xx on the
        # generic root endpoint is not an outage.
        status = "ok" if 400 <= exc.code < 500 else "warning"
        checks.append(_health_item("digikala", "ارتباط با دیجی‌کالا", status, f"HTTP {exc.code}", "سرور دیجی‌کالا در دسترس است." if status == "ok" else "پاسخ سرویس موقتاً غیرعادی است.", "retry" if status != "ok" else None))
    except Exception as exc:
        checks.append(_health_item("digikala", "ارتباط با دیجی‌کالا", "error", "ناموفق", f"ارتباط با دیجی‌کالا برقرار نشد: {exc}", "retry"))

    try:
        release, release_error = _github_latest_release()
        if release_error:
            checks.append(_health_item("github", "ارتباط با GitHub", "warning", "نیازمند توجه", release_error, "retry"))
        else:
            latest = str((release or {}).get("version") or "نامشخص")
            checks.append(_health_item("github", "ارتباط با GitHub", "ok", "سالم", f"سرویس آپدیت در دسترس است؛ آخرین انتشار: {latest}."))
    except Exception as exc:
        checks.append(_health_item("github", "ارتباط با GitHub", "error", "ناموفق", f"بررسی GitHub انجام نشد: {exc}", "retry"))

    invalid = []
    existing = 0
    for path, expected in HEALTH_DATA_FILES.items():
        if not path.exists():
            continue
        existing += 1
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, expected):
                invalid.append(path.name)
        except Exception:
            invalid.append(path.name)
    if invalid:
        checks.append(_health_item("database", "اطلاعات برنامه", "error", f"{len(invalid)} فایل ناسالم", "فایل‌های نیازمند تعمیر: " + "، ".join(invalid), "repair"))
    else:
        checks.append(_health_item("database", "اطلاعات برنامه", "ok", "سالم", f"ساختار {existing} فایل اطلاعاتی بررسی و تأیید شد."))

    backups = _backup_entries()
    if backups:
        latest = backups[0]
        try:
            age_days = max(0, (datetime.now() - datetime.fromisoformat(str(latest.get("created_at")))).days)
        except Exception:
            age_days = 0
        status = "warning" if age_days >= 14 else "ok"
        detail = f"آخرین بکاپ {age_days} روز قبل ساخته شده است." if age_days else "یک بکاپ جدید در دسترس است."
        checks.append(_health_item("backup", "سیستم بکاپ", status, f"{len(backups)} بکاپ", detail, "backup" if status == "warning" else None))
    else:
        checks.append(_health_item("backup", "سیستم بکاپ", "warning", "بدون بکاپ", "هنوز هیچ نسخه پشتیبانی ساخته نشده است.", "backup"))

    update = _update_state()
    last_update = update.get("last_update") or {}
    if last_update.get("status") == "failed":
        checks.append(_health_item("update", "سیستم به‌روزرسانی", "error", f"نسخه {APP_VERSION}", "آخرین نصب ناموفق بود: " + str(last_update.get("error") or "خطای نامشخص"), "settings"))
    elif last_update.get("status") == "success":
        checks.append(_health_item("update", "سیستم به‌روزرسانی", "ok", f"نسخه {APP_VERSION}", "آخرین به‌روزرسانی با موفقیت نصب شده است."))
    else:
        checks.append(_health_item("update", "سیستم به‌روزرسانی", "ok", f"نسخه {APP_VERSION}", "سامانه به‌روزرسانی آماده بررسی است."))

    try:
        free = shutil.disk_usage(APP_DIR).free
        free_gb = free / (1024 ** 3)
        disk_status = "error" if free < 500 * 1024 ** 2 else "warning" if free < 2 * 1024 ** 3 else "ok"
        disk_detail = "فضای بسیار کمی باقی مانده است." if disk_status == "error" else "برای آپدیت و بکاپ بهتر است فضا آزاد شود." if disk_status == "warning" else "فضای کافی برای اطلاعات و به‌روزرسانی وجود دارد."
        checks.append(_health_item("disk", "فضای ذخیره‌سازی", disk_status, f"{free_gb:.1f} GB آزاد", disk_detail, "data_folder" if disk_status != "ok" else None))
    except Exception as exc:
        checks.append(_health_item("disk", "فضای ذخیره‌سازی", "warning", "نامشخص", f"فضای دیسک خوانده نشد: {exc}"))

    products = load_products()
    checked_values = [str(item.get("checked") or "").strip() for item in products if str(item.get("checked") or "").strip()]
    last_checked = max(checked_values) if checked_values else "—"
    monitor_status = "ok" if checked_values else "warning"
    checks.append(_health_item("monitor", "آخرین بررسی محصولات", monitor_status, last_checked, f"{len(products)} کالا در مانیتور ثبت شده است." if products else "هنوز کالایی در مانیتور ثبت نشده است."))

    recent_errors = []
    for log_name in ("update.log", "installer.log", "startup-error.log"):
        log_path = APP_DIR / log_name
        if not log_path.exists():
            continue
        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-200:]
            recent_errors.extend(f"{log_name}: {line.strip()}" for line in lines if "error" in line.lower() or "traceback" in line.lower())
        except Exception:
            pass
    error_count = len(recent_errors)
    checks.append(_health_item("errors", "خطاهای اخیر", "warning" if error_count else "ok", f"{error_count} خطا", recent_errors[-1] if recent_errors else "خطای ثبت‌شده‌ای در گزارش‌های اخیر پیدا نشد.", "report" if error_count else None))

    counts = {"ok": 0, "warning": 0, "error": 0}
    for item in checks:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    overall = "error" if counts["error"] else "warning" if counts["warning"] else "ok"
    return {"ok": True, "checked_at": checked_at, "overall": overall, "counts": counts, "checks": checks, "recent_errors": recent_errors[-10:], "version": APP_VERSION}


def _health_report_text(report):
    labels = {"ok": "سالم", "warning": "نیازمند توجه", "error": "دارای مشکل"}
    lines = ["گزارش سلامت My Digi", f"نسخه: V{APP_VERSION}", f"زمان بررسی: {report.get('checked_at', '—')}", ""]
    for item in report.get("checks", []):
        lines.append(f"[{labels.get(item.get('status'), item.get('status'))}] {item.get('title')}: {item.get('value')}")
        lines.append(f"  {item.get('detail')}")
    errors = report.get("recent_errors") or []
    if errors:
        lines.extend(["", "آخرین خطاها:", *[f"- {x}" for x in errors]])
    return "\n".join(lines)


def _repair_health_data():
    """Archive malformed JSON files and recreate only their safe empty shape."""
    safety = _snapshot_user_data("repair-safety")
    repaired = []
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for path, expected in HEALTH_DATA_FILES.items():
        if not path.exists():
            continue
        valid = True
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            valid = isinstance(value, expected)
        except Exception:
            valid = False
        if valid:
            continue
        archive = path.with_name(f"{path.name}.corrupt-{stamp}")
        shutil.copy2(path, archive)
        default = [] if expected is list else {}
        path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")
        repaired.append(path.name)
    return safety, repaired


def _resolve_data_backup(backup_id):
    kind, separator, name = str(backup_id or "").partition(":")
    if separator != ":" or kind not in {"manual", "update"} or not re.fullmatch(r"[A-Za-z0-9._-]+", name):
        raise ValueError("شناسه پشتیبان معتبر نیست.")
    parent = MANUAL_BACKUP_DIR if kind == "manual" else APP_DIR / "versions"
    root = parent / name
    data_dir = root / "data"
    if not root.is_dir() or not data_dir.is_dir():
        raise FileNotFoundError("نسخه پشتیبان اطلاعات پیدا نشد.")
    return root, data_dir


def _restore_user_data(backup_id):
    _, source = _resolve_data_backup(backup_id)
    safety = _snapshot_user_data("before-restore")
    restored = 0
    for item in source.iterdir():
        target = APP_DIR / item.name
        if item.is_dir():
            temp = APP_DIR / f".{item.name}.restore-{uuid.uuid4().hex}"
            shutil.copytree(item, temp)
            if target.exists():
                shutil.rmtree(target)
            temp.rename(target)
            restored += sum(1 for p in target.rglob("*") if p.is_file())
        elif item.is_file():
            temp = APP_DIR / f".{item.name}.restore-{uuid.uuid4().hex}"
            shutil.copy2(item, temp)
            os.replace(temp, target)
            restored += 1
    return safety, restored


def _delete_data_backup(backup_id):
    root, _ = _resolve_data_backup(backup_id)
    shutil.rmtree(root)

def _regular_python_executable():
    """Return a normal GIL-enabled CPython executable for the native calculator."""
    if os.name != "nt" or _is_frozen_app():
        return sys.executable

    def is_regular(candidate):
        if not candidate:
            return False
        try:
            candidate = str(Path(candidate).resolve())
        except Exception:
            candidate = str(candidate).strip()
        if not Path(candidate).exists() or candidate.lower().endswith("t.exe"):
            return False
        try:
            probe = _subprocess.run(
                [candidate, "-c", "import sys; print(getattr(sys, '_is_gil_enabled', lambda: True)())"],
                capture_output=True, text=True, timeout=8
            )
            return probe.returncode == 0 and probe.stdout.strip().lower() == "true"
        except Exception:
            return False

    # Prefer the currently running interpreter when it is already regular.
    if is_regular(sys.executable):
        return sys.executable

    # Prefer the regular Python version installed alongside Python 3.14t.
    for ver in ("3.14", "3.13", "3.12", "3.11", "3.10"):
        try:
            probe = _subprocess.run(
                ["py", f"-{ver}", "-c", "import sys; print(sys.executable)"],
                capture_output=True, text=True, timeout=8
            )
            candidate = probe.stdout.strip().splitlines()[-1] if probe.returncode == 0 and probe.stdout.strip() else ""
            if is_regular(candidate):
                return candidate
        except Exception:
            pass

    raise RuntimeError("برای باز کردن ماشین‌حساب، Python معمولی (غیر آزاد از GIL) روی ویندوز لازم است. نسخه‌های نصب‌شده بررسی شدند اما نسخهٔ معمولی مناسب پیدا نشد.")

def _launch_native_calculator():
    import base64,gzip
    raw=gzip.decompress(base64.b64decode(_CALCULATOR_B64_GZIP))
    _CALCULATOR_FILE.write_bytes(raw)

    # Packaged My Digi is built with regular CPython, so the same EXE can open the calculator mode.
    if _is_frozen_app():
        _subprocess.Popen([sys.executable, "--calculator"], cwd=str(_install_dir()))
        return

    # If the main app is running under a free-threaded Python, relaunch only the calculator
    # under regular CPython. This keeps the main My Digi UI untouched.
    pyexe = _regular_python_executable()
    if os.path.normcase(os.path.abspath(pyexe)) != os.path.normcase(os.path.abspath(sys.executable)):
        script = str(Path(__file__).resolve())
        _subprocess.check_call([pyexe, "-m", "pip", "install", "--user", "pywebview==6.2.1"])
        _subprocess.Popen([pyexe, script, "--calculator"], cwd=str(Path(__file__).resolve().parent))
        return

    try:
        import webview
    except Exception:
        try:
            _subprocess.check_call([pyexe, "-m", "pip", "install", "--user", "pywebview==6.2.1"])
            import importlib
            webview = importlib.import_module("webview")
        except Exception as exc:
            raise RuntimeError("کتابخانه pywebview نصب نشد. ماشین‌حساب در این نسخه به Python معمولی 3.13 نیاز دارد؛ Python 3.14t برای pywebview/pythonnet مناسب نیست.") from exc

    window=webview.create_window("My Digi — ماشین حساب", url=_CALCULATOR_FILE.resolve().as_uri(), width=1180, height=820, min_size=(900,650), background_color="#050b17", text_select=True)
    webview.start(gui="edgechromium")


class _MyDigiHandler(BaseHTTPRequestHandler):
    server_version="MyDigi/1.10"
    def _json(self, code, payload):
        raw=json.dumps(payload,ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers(); self.wfile.write(raw)
    def _body(self):
        n=int(self.headers.get("Content-Length","0") or 0)
        raw=self.rfile.read(n) if n else b"{}"
        try: return json.loads(raw.decode("utf-8"))
        except Exception: return {}
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ("/","/index.html"):
            html=(Path(__file__).with_name("mydigi_graphic.html")).read_text(encoding="utf-8").replace("__APP_VERSION__",APP_VERSION)
            raw=html.encode("utf-8")
            self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if path=="/calculator":
            # Serve the bundled calculator from the same local My Digi web app.
            # It is opened by Edge/Chrome in app mode, so no second My Digi/Python
            # process is needed and the calculator appears as a native app window.
            import base64, gzip
            raw=gzip.decompress(base64.b64decode(_CALCULATOR_B64_GZIP))
            html=raw.decode("utf-8").replace("__APP_VERSION__",APP_VERSION)
            raw=html.encode("utf-8")
            self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if path=="/api/state": self._json(200,_web_state()); return
        if path=="/api/accounting": self._json(200,_accounting_state()); return
        if path=="/api/settings": self._json(200,{"ok":True,"settings":load_settings()}); return
        if path=="/api/update-state": self._json(200,{"ok":True,**_update_state()}); return
        if path=="/api/backups": self._json(200,{"ok":True,"backups":_backup_entries()}); return
        if path=="/api/health":
            try: return self._json(200,_health_diagnostics())
            except Exception as exc: return self._json(500,{"ok":False,"error":f"اجرای بررسی سلامت ناموفق بود: {exc}"})
        if path=="/api/check-update":
            try:
                rel, err = _github_latest_release()
                if err: return self._json(200,{"ok":True,"configured":False,"message":err,**_update_state()})
                available = bool(rel and _version_tuple(rel.get("version")) > _version_tuple(APP_VERSION) and rel.get("installer"))
                return self._json(200,{"ok":True,"configured":True,"available":available,"current":APP_VERSION,"release":rel,**_update_state()})
            except HTTPError as exc:
                detail = "مخزن یا Release پیدا نشد." if exc.code == 404 else "دسترسی گیت‌هاب محدود شده یا تعداد درخواست‌ها بیش از حد است." if exc.code == 403 else f"HTTP {exc.code}"
                return self._json(502,{"ok":False,"error":f"بررسی نسخه جدید انجام نشد: {detail}"})
            except Exception as exc:
                return self._json(502,{"ok":False,"error":f"بررسی نسخه جدید انجام نشد: {exc}"})
        if path=="/api/reference": self._json(200,_reference_state()); return
        if path=="/api/internet-status":
            online=False
            detail=""
            try:
                sock=socket.create_connection(("api.digikala.com",443),timeout=3)
                sock.close(); online=True
            except Exception as exc:
                detail=str(exc)
            return self._json(200,{"ok":True,"online":online,"detail":detail,"checked_at":datetime.now().isoformat()})
        if path=="/api/check-all-progress":
            with WEB_CHECK_LOCK:
                snap=dict(WEB_CHECK_PROGRESS)
            payload={"ok":True,**{k:snap.get(k) for k in ("running","completed","total","failed","current","finished","finished_at","error","engine_error")}}
            if snap.get("finished") and snap.get("state") is not None:
                payload["state"]=snap.get("state")
            return self._json(200,payload)
        if path=="/api/reminders":
            state=_web_state()
            reminders=state.get("reminders",[])
            read_count=sum(1 for x in reminders if x.get("read"))
            unread_count=len(reminders)-read_count
            return self._json(200,{"ok":True,"reminders":reminders,"read_count":read_count,"unread_count":unread_count})
        if path.startswith("/api/product-image-url/"):
            parts=path.split("/")
            uid=unquote(parts[-1]).strip() if len(parts)>3 else ""
            if not uid:
                return self._json(400,{"ok":False,"error":"شناسه تصویر معتبر نیست."})
            items=load_products()
            item=next((x for x in items if str(x.get("uuid") or "").strip()==uid),None)
            if not item:
                return self._json(404,{"ok":False,"error":"محصول پیدا نشد."})
            product_id=str(item.get("id") or "").strip()
            if not product_id:
                return self._json(404,{"ok":False,"error":"شناسه محصول دیجی‌کالا ثبت نشده است."})
            try:
                api=f"https://api.digikala.com/v2/product/{product_id}/"
                req=Request(api,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36","Accept":"application/json","Referer":"https://www.digikala.com/"})
                with urlopen(req,timeout=20) as r:
                    raw=r.read(6*1024*1024)
                data=json.loads(raw.decode("utf-8"))
                root=data.get("data",{}) if isinstance(data,dict) else {}
                product=root.get("product",root) if isinstance(root,dict) else {}
                image_url=first_image_url(product)
            except Exception as exc:
                return self._json(502,{"ok":False,"error":f"دریافت اطلاعات تصویر از دیجی‌کالا انجام نشد: {exc}"})
            if not image_url:
                return self._json(404,{"ok":False,"error":"اولین تصویر واقعی کالا در اطلاعات دیجی‌کالا پیدا نشد."})
            if item.get("image_url") != image_url:
                item["image_url"]=image_url
                try: save_products(items)
                except Exception: pass
            return self._json(200,{"ok":True,"url":image_url,"product_id":product_id})
        if path.startswith("/api/product-image/"):
            parts=path.split("/")
            uid=unquote(parts[-1]).strip() if len(parts)>3 else ""
            if not uid:
                return self._json(400,{"ok":False,"error":"شناسه تصویر معتبر نیست."})
            items=load_products()
            item=next((x for x in items if str(x.get("uuid") or "").strip()==uid),None)
            if not item:
                return self._json(404,{"ok":False,"error":"محصول پیدا نشد."})
            product_id=str(item.get("id") or "").strip()
            if not product_id:
                return self._json(404,{"ok":False,"error":"شناسه محصول دیجی‌کالا ثبت نشده است."})
            try:
                image_url=item.get("image_url")
                if not image_url:
                    api=f"https://api.digikala.com/v2/product/{product_id}/"
                    req=Request(api,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36","Accept":"application/json","Referer":"https://www.digikala.com/"})
                    with urlopen(req,timeout=20) as r:
                        raw=r.read(6*1024*1024)
                    data=json.loads(raw.decode("utf-8"))
                    root=data.get("data",{}) if isinstance(data,dict) else {}
                    product=root.get("product",root) if isinstance(root,dict) else {}
                    image_url=first_image_url(product)
                    if image_url:
                        item["image_url"]=image_url
                        try: save_products(items)
                        except Exception: pass
                if not image_url:
                    return self._json(404,{"ok":False,"error":"آدرس تصویر کالا پیدا نشد."})
                req=Request(image_url,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36","Referer":"https://www.digikala.com/"})
                with urlopen(req,timeout=30) as r:
                    image_raw=r.read(12*1024*1024)
                    content_type=r.headers.get("Content-Type") or "image/jpeg"
                if not content_type.startswith("image/"):
                    content_type="image/jpeg"
                self.send_response(200)
                self.send_header("Content-Type",content_type)
                self.send_header("Cache-Control","public, max-age=3600")
                self.send_header("Content-Length",str(len(image_raw)))
                self.end_headers()
                self.wfile.write(image_raw)
                return
            except Exception as exc:
                return self._json(502,{"ok":False,"error":f"دریافت تصویر کالا انجام نشد: {exc}"})
        self._json(404,{"error":"Not found"})
    def do_POST(self):
        global WEB_CHECK_PROGRESS
        path=urlparse(self.path).path; data=self._body()
        try:
            if path=="/api/reference":
                result=_reference_api_action(data)
                return self._json(200,result)
            if path=="/api/health/report":
                report=_health_diagnostics()
                out=_web_downloads_dir()/f"My_Digi_Health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                out.write_text(_health_report_text(report),encoding="utf-8-sig")
                return self._json(200,{"ok":True,"name":out.name,"folder":str(out.parent)})
            if path=="/api/health/repair":
                safety,repaired=_repair_health_data()
                return self._json(200,{"ok":True,"repaired":repaired,"safety_backup":safety.name,"health":_health_diagnostics()})
            if path=="/api/health/open-data":
                if os.name=="nt": os.startfile(str(APP_DIR))
                else: _subprocess.Popen(["xdg-open",str(APP_DIR)])
                return self._json(200,{"ok":True})
            if path=="/api/start-update":
                rel = data.get("release") or {}
                inst = (rel.get("installer") or {}).get("url")
                ver = str(rel.get("version") or "").strip()
                if not inst or not ver: return self._json(400,{"ok":False,"error":"اطلاعات نسخه جدید ناقص است."})
                sha = str((rel.get("installer") or {}).get("sha256") or "")
                _launch_updater("update", ["--url", inst, "--version", ver, "--sha256", sha])
                threading.Timer(1.5, lambda: os._exit(0)).start()
                return self._json(200,{"ok":True,"message":"به‌روزرسانی در حال آماده‌سازی است."})
            if path=="/api/rollback":
                version = str(data.get("version") or "").strip()
                if not version: return self._json(400,{"ok":False,"error":"نسخه بازگشت مشخص نشده است."})
                backup = APP_DIR / "versions" / version
                if not backup.exists(): return self._json(404,{"ok":False,"error":"نسخه پشتیبان پیدا نشد."})
                _launch_updater("rollback", ["--backup", str(backup)])
                threading.Timer(1.5, lambda: os._exit(0)).start()
                return self._json(200,{"ok":True,"message":"بازگشت به نسخه قبلی در حال انجام است."})
            if path=="/api/backups/create":
                backup = _snapshot_user_data("manual")
                return self._json(200,{"ok":True,"message":"پشتیبان اطلاعات ساخته شد.","backup":backup.name,"backups":_backup_entries()})
            if path=="/api/backups/restore":
                backup_id = str(data.get("id") or "")
                safety, restored = _restore_user_data(backup_id)
                return self._json(200,{"ok":True,"message":"اطلاعات با موفقیت بازیابی شد.","restored":restored,"safety_backup":safety.name})
            if path=="/api/backups/delete":
                backup_id = str(data.get("id") or "")
                _delete_data_backup(backup_id)
                return self._json(200,{"ok":True,"message":"نسخه پشتیبان حذف شد.","backups":_backup_entries()})
            if path=="/api/backups/open-folder":
                MANUAL_BACKUP_DIR.mkdir(parents=True,exist_ok=True)
                if os.name == "nt": os.startfile(str(MANUAL_BACKUP_DIR))
                else: _subprocess.Popen(["xdg-open",str(MANUAL_BACKUP_DIR)])
                return self._json(200,{"ok":True})
            if path=="/api/settings-save":
                return self._json(200,{"ok":True,"settings":save_settings(data.get("settings") if isinstance(data,dict) else {})})
            if path=="/api/reminders/mark-read":
                ids=data.get("ids") or []
                if not isinstance(ids,list):
                    ids=[ids]
                state=load_reminder_state()
                for rid in ids:
                    rid=str(rid or "").strip()
                    if not rid: continue
                    state[rid]=True
                    if rid.startswith("refquote|"):
                        qid=rid.split("|",1)[1]
                        ref=load_reference(); changed=False
                        for sup in ref.get("suppliers",[]):
                            for q in sup.get("quotes",[]) or []:
                                if str(q.get("id") or "")==qid and not q.get("completed"):
                                    q["completed"]=True; q["completed_at"]=datetime.now().strftime("%Y-%m-%d %H:%M"); q["completion_reason"]="تیک انجام شد"; changed=True
                        if changed: save_reference(ref)
                save_reminder_state(state)
                st=_web_state()
                reminders=st.get("reminders",[])
                return self._json(200,{"ok":True,"reminders":reminders,"read_count":sum(1 for x in reminders if x.get("read")),"unread_count":sum(1 for x in reminders if not x.get("read"))})
            if path=="/api/save-product":
                items=load_products(); uid=str(data.get("uuid") or ""); item=next((x for x in items if str(x.get("uuid"))==uid),None)
                if not item: return self._json(404,{"ok":False,"error":"محصول پیدا نشد"})
                if "selected" in data:
                    item["selected"]=bool(data.get("selected"))
                if "custom_title" in data:
                    item["custom_title"]=str(data.get("custom_title") or "").strip() or item.get("title")
                for key in ("purchase","profit","ancillary"):
                    if key in data:
                        v=data.get(key); item[key]=None if v in (None,"") else int(str(v).replace(",",""))
                if "commission" in data:
                    v=data.get("commission"); item["commission"]=None if v in (None,"") else float(str(v).replace(",","."))

                # Keep commission in sync with linked "مرجع من" products.
                if "commission" in data:
                    try:
                        ref_data=load_reference()
                        changed=False
                        target_uuid=str(item.get("uuid") or "")
                        for supplier in (ref_data.get("suppliers") or []):
                            for rp in (supplier.get("products") or []):
                                if str(rp.get("monitor_product_uuid") or "")==target_uuid:
                                    rp["commission"]=item.get("commission")
                                    changed=True
                        if changed:
                            save_reference(ref_data)
                    except Exception:
                        pass

                save_products(items); return self._json(200,{"ok":True})
            if path=="/api/add":
                url=str(data.get("url") or "").strip(); pid=extract_id(url)
                if not pid: return self._json(400,{"ok":False,"error":"لینک معتبر محصول دیجی‌کالا وارد کنید."})
                items=load_products()
                if any(str(x.get("id"))==str(pid) for x in items): return self._json(409,{"ok":False,"error":"این محصول قبلاً اضافه شده است."})
                try:
                    title,price,seller,second_price,second_seller,unavailable,image_url=fetch_product(pid)
                    pending=False
                except Exception:
                    # Do not block saving a valid Digikala URL just because the live API is temporarily unreachable.
                    title=f"محصول DKP-{pid}"; price=None; seller="—"; second_price=None; second_seller="—"; unavailable=False; image_url=None; pending=True
                stamp=datetime.now().strftime("%Y/%m/%d %H:%M")
                items.append({"uuid":str(uuid.uuid4()),"id":pid,"url":url,"title":title,"price":price,"seller":seller or "—","second_price":second_price,"second_seller":second_seller or "—","change":"—","change_direction":None,"change_amount":None,"change_at":None,"purchase":None,"profit":None,"ancillary":0,"commission":None,"status":"⚠ نیاز به بررسی" if pending else ("⚪ ناموجود" if unavailable else "🟢 فعال"),"checked":stamp,"image_url":image_url,"selected":False,"price_history":([{"date":today_jalali_text(),"price":price}] if price is not None else [])})
                save_products(items); return self._json(200,{"ok":True,"pending":pending})
            if path=="/api/remove":
                items=load_products(); uids={str(x) for x in (data.get("uuids") or [])}; items=[x for x in items if str(x.get("uuid")) not in uids]; save_products(items); return self._json(200,{"ok":True})
            if path=="/api/check-all/start":
                with WEB_CHECK_LOCK:
                    if WEB_CHECK_PROGRESS.get("running"):
                        return self._json(200,{"ok":True,"already_running":True,"total":WEB_CHECK_PROGRESS.get("total",0)})
                    items=load_products()
                    WEB_CHECK_PROGRESS={"running":True,"completed":0,"total":len(items),"failed":0,"current":"","finished":False,"finished_at":None,"state":None,"error":None,"engine_error":None,"last_item_error":""}
                def run_check_all():
                    global WEB_CHECK_PROGRESS
                    items=load_products()
                    failed=0
                    month_notice=None
                    try:
                        month_notice=ensure_monthly_tracking(items)
                        increase_total=0
                        decrease_total=0
                        for idx,p in enumerate(items,1):
                            with WEB_CHECK_LOCK:
                                WEB_CHECK_PROGRESS["current"]=str(p.get("title") or f"کالا {idx}")
                            ok=False
                            last_error=""
                            for attempt in range(3):
                                try:
                                    title,new,seller,second_price,second_seller,unavailable,image_url=fetch_product(p["id"]); old=p.get("price")
                                    p["title"]=title; p["seller"]=seller or "—"; p["price"]=new; p["second_price"]=second_price; p["second_seller"]=second_seller or "—"; p["checked"]=datetime.now().strftime("%Y/%m/%d %H:%M")
                                    if image_url: p["image_url"]=image_url
                                    if not unavailable and new is not None: _record_monitor_price(p,new)
                                    if unavailable:
                                        p["change"]="—"; p["change_direction"]=None; p["change_amount"]=None; p["status"]="⚪ ناموجود"
                                    elif old is None and new is not None:
                                        p["change"]="—"; p["change_direction"]=None; p["change_amount"]=None; p["status"]="🟢 دوباره موجود شد"
                                    elif new is not None and old is not None and new<old:
                                        delta=old-new; decrease_total += delta
                                        p["change"]=f"↓ {delta:,}"; p["change_direction"]="decrease"; p["change_amount"]=int(delta); p["change_at"]=datetime.now().isoformat(); p["status"]="🔻 کاهش قیمت"
                                        record_monthly_price_event(p,old,new,"decrease")
                                    elif new is not None and old is not None and new>old:
                                        delta=new-old; increase_total += delta
                                        p["change"]=f"↑ {delta:,}"; p["change_direction"]="increase"; p["change_amount"]=int(delta); p["change_at"]=datetime.now().isoformat(); p["status"]="🔺 افزایش قیمت"
                                        record_monthly_price_event(p,old,new,"increase")
                                    else: p["change"]="—"; p["status"]="🟢 بدون تغییر"
                                    ok=True
                                    break
                                except Exception as exc:
                                    last_error=str(exc)
                                    if attempt < 2: time.sleep(0.45)
                            if not ok:
                                failed += 1
                                p["status"]="⚠ خطای بررسی"
                                p["checked"]=datetime.now().strftime("%Y/%m/%d %H:%M")
                            with WEB_CHECK_LOCK:
                                WEB_CHECK_PROGRESS["completed"]=idx
                                WEB_CHECK_PROGRESS["failed"]=failed
                                WEB_CHECK_PROGRESS["last_item_error"]=last_error if not ok else ""
                        record_market_trend(increase_total-decrease_total, increase_total, decrease_total, len(items)-failed)
                        save_products(items)
                        state=_web_state()
                        state["month_notice"]=month_notice
                        with WEB_CHECK_LOCK:
                            WEB_CHECK_PROGRESS["running"]=False; WEB_CHECK_PROGRESS["current"]=""; WEB_CHECK_PROGRESS["finished"]=True; WEB_CHECK_PROGRESS["finished_at"]=datetime.now().isoformat(); WEB_CHECK_PROGRESS["state"]=state; WEB_CHECK_PROGRESS["error"]=None; WEB_CHECK_PROGRESS["engine_error"]=None
                    except Exception as exc:
                        with WEB_CHECK_LOCK:
                            WEB_CHECK_PROGRESS["running"]=False; WEB_CHECK_PROGRESS["current"]=""; WEB_CHECK_PROGRESS["finished"]=True; WEB_CHECK_PROGRESS["finished_at"]=datetime.now().isoformat(); WEB_CHECK_PROGRESS["error"]=None; WEB_CHECK_PROGRESS["engine_error"]=str(exc); WEB_CHECK_PROGRESS["state"]=_web_state()
                threading.Thread(target=run_check_all,daemon=True).start()
                return self._json(202,{"ok":True,"already_running":False,"total":len(items)})
            if path=="/api/check-all-progress":
                with WEB_CHECK_LOCK:
                    snap=dict(WEB_CHECK_PROGRESS)
                payload={"ok":True,**{k:snap.get(k) for k in ("running","completed","total","failed","current","finished","finished_at","error","engine_error")}}
                if snap.get("finished") and snap.get("state") is not None:
                    payload["state"]=snap.get("state")
                    if snap.get("error"):
                        payload["error"]=snap.get("error")
                return self._json(200,payload)
            if path=="/api/check-all":
                # Compatibility: preserve the legacy endpoint while using the same asynchronous progress engine.
                with WEB_CHECK_LOCK:
                    running=bool(WEB_CHECK_PROGRESS.get("running"))
                if running:
                    return self._json(200,{"ok":True,"state":_web_state(),"already_running":True})
                return self._json(409,{"ok":False,"error":"بررسی همه باید از مسیر /api/check-all/start اجرا شود."})
            if path=="/api/screenshot-monitor":
                try:
                    out=_web_downloads_dir()/f"My_Digi_Monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    img=_capture_my_digi_window()
                    img.save(out,"PNG")
                    return self._json(200,{"ok":True,"name":out.name,"folder":str(out.parent)})
                except Exception as exc:
                    return self._json(500,{"ok":False,"error":f"گرفتن اسکرین‌شات انجام نشد: {exc}"})
            if path=="/api/export-excel":
                try:
                    items=load_products()
                    out=_web_downloads_dir()/f"My_Digi_Products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    write_products_xlsx(items,out,best_supplier_resolver=lambda item:_best_supplier_for_web(item),all_supplier_resolver=lambda item:_best_supplier_for_web(item,all_suppliers=True))
                    return self._json(200,{"ok":True,"name":out.name,"folder":str(out.parent),"count":len(items)})
                except Exception as exc:
                    return self._json(500,{"ok":False,"error":f"ساخت فایل اکسل انجام نشد: {exc}"})
            if path=="/api/open-path":
                try:
                    kind=str(data.get("kind") or "file")
                    name=str(data.get("name") or "").strip()
                    folder=_web_downloads_dir()
                    target=folder if kind=="folder" else folder/name
                    target=target.resolve()
                    if target.parent.resolve()!=folder.resolve() and target.resolve()!=folder.resolve():
                        return self._json(400,{"ok":False,"error":"مسیر فایل معتبر نیست."})
                    if not target.exists():
                        return self._json(404,{"ok":False,"error":"فایل پیدا نشد."})
                    if os.name=="nt":
                        if kind=="folder": os.startfile(str(target))
                        else: os.startfile(str(target))
                    else:
                        _subprocess.Popen(["xdg-open",str(target)])
                    return self._json(200,{"ok":True})
                except Exception as exc:
                    return self._json(500,{"ok":False,"error":f"باز کردن مسیر انجام نشد: {exc}"})
            if path=="/api/open-calculator":
                try:
                    # Open the calculator as a second My Digi app window using the
                    # same local HTTP server as the main UI. This keeps the calculator
                    # inside the My Digi app experience and avoids launching another
                    # copy of the My Digi executable.
                    port=self.server.server_address[1]
                    url=f"http://127.0.0.1:{port}/calculator"
                    candidates=[
                        Path(os.environ.get("PROGRAMFILES",""))/"Microsoft/Edge/Application/msedge.exe",
                        Path(os.environ.get("PROGRAMFILES(X86)",""))/"Microsoft/Edge/Application/msedge.exe",
                        Path(os.environ.get("LOCALAPPDATA",""))/"Microsoft/Edge/Application/msedge.exe",
                        Path(os.environ.get("LOCALAPPDATA",""))/"Google/Chrome/Application/chrome.exe",
                        Path(os.environ.get("PROGRAMFILES",""))/"Google/Chrome/Application/chrome.exe",
                        Path(os.environ.get("PROGRAMFILES(X86)",""))/"Google/Chrome/Application/chrome.exe",
                    ]
                    launched=False
                    if os.name=="nt":
                        for exe in candidates:
                            try:
                                if exe.exists():
                                    _subprocess.Popen([str(exe),f"--app={url}"], cwd=str(_install_dir()), creationflags=getattr(_subprocess,"CREATE_NO_WINDOW",0))
                                    launched=True
                                    break
                            except Exception:
                                pass
                    if not launched:
                        _webbrowser.open_new(url)
                    return self._json(200,{"ok":True,"url":url})
                except Exception as exc:
                    return self._json(500,{"ok":False,"error":f"باز کردن ماشین حساب انجام نشد: {exc}"})
            if path=="/api/open-reference":
                try:
                    _subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--classic-reference"], cwd=str(Path(__file__).resolve().parent))
                    return self._json(200,{"ok":True,"message":"پنجره مرجع من باز شد."})
                except Exception as exc:
                    return self._json(500,{"ok":False,"error":f"باز کردن مرجع من انجام نشد: {exc}"})
            if path=="/api/accounting-save":
                save_accounting(data); return self._json(200,{"ok":True})
            if path=="/api/accounting-report-check":
                notice, reports = ensure_accounting_monthly_reports(); return self._json(200,{"ok":True,"notice":notice,"reports":reports})
            self._json(404,{"ok":False,"error":"Not found"})
        except Exception as exc:
            self._json(500,{"ok":False,"error":str(exc)})
    def log_message(self, format, *args): return


def _apply_windows_window_icon():
    """Apply the installed ICO to My Digi's native top-level window."""
    if os.name != "nt":
        return
    try:
        import ctypes as ct
        from ctypes import wintypes as wt
        user32 = ct.windll.user32
        icon_path = _install_dir() / "My Digi.ico"
        if not icon_path.exists() and getattr(sys, "_MEIPASS", None):
            icon_path = Path(sys._MEIPASS) / "My Digi.ico"
        if not icon_path.exists():
            return
        load_image = user32.LoadImageW
        load_image.restype = wt.HANDLE
        big = load_image(None, str(icon_path), 1, 32, 32, 0x10)
        small = load_image(None, str(icon_path), 1, 16, 16, 0x10)
        current_pid = os.getpid()

        @ct.WINFUNCTYPE(ct.c_bool, wt.HWND, wt.LPARAM)
        def callback(hwnd, _):
            pid = wt.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ct.byref(pid))
            if pid.value == current_pid and user32.IsWindowVisible(hwnd):
                if big:
                    user32.SendMessageW(hwnd, 0x0080, 1, big)
                if small:
                    user32.SendMessageW(hwnd, 0x0080, 0, small)
            return True

        for _ in range(20):
            user32.EnumWindows(callback, 0)
            time.sleep(0.15)
    except Exception as icon_exc:
        try:
            (APP_DIR / "startup-error.log").write_text(
                f"{datetime.now().isoformat()} | taskbar icon: {icon_exc}\n",
                encoding="utf-8",
            )
        except Exception:
            pass


def launch_graphic_web():
    html_path=Path(__file__).with_name("mydigi_graphic.html")
    if not html_path.exists():
        print("فایل رابط گرافیکی mydigi_graphic.html کنار برنامه پیدا نشد.")
        return
    httpd=ThreadingHTTPServer(("127.0.0.1",WEB_PORT),_MyDigiHandler)
    actual_port=httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever,daemon=True).start()
    url=f"http://127.0.0.1:{actual_port}/"
    print(f"My Digi {APP_VERSION} graphical UI: {url}")

    # Host the main HTML inside pywebview instead of an external Edge/Chrome
    # app window.  This keeps the same HTML/CSS/JS UI but makes the top-level
    # window belong to My Digi itself, so Windows can use the EXE icon in the
    # taskbar instead of the browser's globe icon.
    webview_error = "unknown error"
    try:
        import webview
        # On Windows the application icon is taken from the bundled executable.
        # Do not attach a fragile native before_show hook here: if that hook fails,
        # the old code fell through to Edge --app and Windows showed the browser icon.
        webview.create_window(
            f"My Digi {APP_VERSION}",
            url=url,
            width=1500,
            height=900,
            min_size=(1100,700),
            background_color="#050b17",
            text_select=True,
        )
        webview.start(_apply_windows_window_icon, gui="edgechromium")
        return
    except Exception as exc:
        webview_error = str(exc)
        print(f"pywebview main window failed: {exc}")

    # Never launch the main UI as an Edge/Chrome app. A browser-owned window
    # is grouped under Edge in the Windows taskbar and cannot reliably inherit
    # My Digi's application identity or pinned shortcut.
    httpd.shutdown()
    error_log = APP_DIR / "startup-error.log"
    try:
        error_log.write_text(
            f"{datetime.now().isoformat()} | pywebview: {webview_error}\n",
            encoding="utf-8",
        )
    except Exception:
        pass
    try:
        messagebox.showerror(
            "My Digi",
            "پنجره برنامه اجرا نشد. لطفاً Microsoft Edge WebView2 Runtime را نصب یا تعمیر کنید.\n\n"
            f"جزئیات خطا در این فایل ذخیره شد:\n{error_log}",
        )
    except Exception:
        pass

# The graphical edition is the default launcher. Use --classic for the legacy Tk window.
if __name__ == "__main__":
    if "--calculator" in sys.argv:
        try:
            _launch_native_calculator()
        except Exception as exc:
            print(f"ماشین حساب: {exc}")
            try: messagebox.showerror("ماشین حساب", str(exc))
            except Exception: pass
    elif "--classic-reference" in sys.argv:
        root = tk.Tk()
        root.withdraw()
        app = App(root)
        app.open_reference()
        root.protocol("WM_DELETE_WINDOW", app._close_app)
        root.mainloop()
    elif "--classic" in sys.argv:
        root = tk.Tk()
        app = App(root)
        root.protocol("WM_DELETE_WINDOW", app._close_app)
        root.mainloop()
    else:
        launch_graphic_web()
