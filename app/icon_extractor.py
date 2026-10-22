import os
import ctypes
from ctypes import wintypes
import hashlib
from PIL import Image, ImageDraw, ImageFont

# Win32 API definitions
gdi32 = ctypes.windll.gdi32
user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

SHGFI_ICON = 0x000000100
SHGFI_LARGEICON = 0x000000000
SHGFI_SMALLICON = 0x000000001
SHGFI_USEFILEATTRIBUTES = 0x000000010

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD),
    ]

class ICONINFO(ctypes.Structure):
    _fields_ = [
        ('fIcon', wintypes.BOOL),
        ('xHotspot', wintypes.DWORD),
        ('yHotspot', wintypes.DWORD),
        ('hbmMask', wintypes.HBITMAP),
        ('hbmColor', wintypes.HBITMAP),
    ]

class SHFILEINFOW(ctypes.Structure):
    _fields_ = [
        ('hIcon', wintypes.HICON),
        ('iIcon', ctypes.c_int),
        ('dwAttributes', wintypes.DWORD),
        ('szDisplayName', wintypes.WCHAR * 260),
        ('szTypeName', wintypes.WCHAR * 80),
    ]

# Setup proper 64-bit argument types
gdi32.GetDIBits.argtypes = [
    wintypes.HDC,
    wintypes.HBITMAP,
    wintypes.UINT,
    wintypes.UINT,
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.UINT
]
gdi32.GetDIBits.restype = ctypes.c_int

user32.GetIconInfo.argtypes = [wintypes.HICON, ctypes.POINTER(ICONINFO)]
user32.GetIconInfo.restype = wintypes.BOOL

user32.DestroyIcon.argtypes = [wintypes.HICON]
user32.DestroyIcon.restype = wintypes.BOOL

PALETTE = [
    ("#6366f1", "#4f46e5"), # Indigo
    ("#06b6d4", "#0891b2"), # Cyan
    ("#10b981", "#059669"), # Emerald
    ("#f59e0b", "#d97706"), # Amber
    ("#ec4899", "#db2777"), # Pink
    ("#8b5cf6", "#7c3aed"), # Purple
    ("#3b82f6", "#2563eb"), # Blue
    ("#14b8a6", "#0d9488"), # Teal
]

def _hicon_to_image(hIcon, size=48):
    """Converts a Win32 HICON to a PIL RGBA Image."""
    if not hIcon:
        return None
    try:
        icon_info = ICONINFO()
        if not user32.GetIconInfo(hIcon, ctypes.byref(icon_info)):
            return None

        hdc = user32.GetDC(0)
        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = 32
        bmi.biHeight = -32 # top-down
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0

        buf = (ctypes.c_byte * (32 * 32 * 4))()
        gdi32.GetDIBits(hdc, icon_info.hbmColor, 0, 32, ctypes.byref(buf), ctypes.byref(bmi), 0)

        raw_data = bytes(buf)
        img = Image.frombytes('RGBA', (32, 32), raw_data, 'raw', 'BGRA')

        # Cleanup handles
        gdi32.DeleteObject(icon_info.hbmColor)
        gdi32.DeleteObject(icon_info.hbmMask)
        user32.ReleaseDC(0, hdc)

        # Check if alpha channel has information or is fully transparent
        alpha = img.split()[3]
        if alpha.getextrema() == (0, 0):
            # Fallback to mask alpha
            img = img.convert('RGB')
            img.putalpha(255)

        if img.size != (size, size):
            img = img.resize((size, size), Image.Resampling.LANCZOS)
        return img
    except Exception:
        return None

def generate_fallback_icon(name, size=48):
    """Generates a stylish fallback icon with the app initial letters and vibrant background."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Pick colors deterministically based on name
    hash_val = int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16)
    bg_color, border_color = PALETTE[hash_val % len(PALETTE)]

    padding = 2
    draw.rounded_rectangle(
        (padding, padding, size - padding, size - padding),
        radius=int(size * 0.28),
        fill=bg_color,
        outline=border_color,
        width=1
    )

    # Text / Initials
    letters = "".join([part[0].upper() for part in name.strip().split() if part])[:2]
    if not letters:
        letters = "APP"[:2]

    # Try standard Windows font, fallback to default
    font_size = int(size * 0.45)
    font = None
    font_names = ["segoeui.ttf", "arial.ttf", "calibri.ttf"]
    for fn in font_names:
        font_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", fn)
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letters, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) / 2 - bbox[0]
    y = (size - text_h) / 2 - bbox[1]

    draw.text((x, y), letters, fill="white", font=font)
    return img

def get_app_icon(file_path, app_name="", cache_dir=None, app_id="temp", size=48, custom_icon=None):
    """
    Extracts icon for the given file path or generates a modern fallback.
    If custom_icon is provided and valid, loads and scales that custom image.
    Caches icon to disk if cache_dir is provided.
    """
    # 1. Custom icon takes priority if specified
    if custom_icon:
        raw_icon = str(custom_icon).strip()
        if not os.path.isabs(raw_icon):
            from app.paths import get_user_data_dir, get_resource_path
            custom_icon_path = os.path.join(get_user_data_dir(), raw_icon)
            if not os.path.exists(custom_icon_path):
                custom_icon_path = get_resource_path(raw_icon)
        else:
            custom_icon_path = os.path.expandvars(raw_icon)

        if os.path.exists(custom_icon_path):
            try:
                img = Image.open(custom_icon_path)
                img.load()
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                if img.size != (size, size):
                    img = img.resize((size, size), Image.Resampling.LANCZOS)
                return img
            except Exception:
                pass

    # 2. Check disk cache
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        cached_file = os.path.join(cache_dir, f"{app_id}.png")
        if os.path.exists(cached_file):
            try:
                img = Image.open(cached_file)
                img.load()
                return img
            except Exception:
                pass

    extracted_img = None
    if file_path and os.path.exists(file_path):
        try:
            shinfo = SHFILEINFOW()
            res = shell32.SHGetFileInfoW(
                str(file_path),
                0,
                ctypes.byref(shinfo),
                ctypes.sizeof(shinfo),
                SHGFI_ICON | SHGFI_LARGEICON
            )
            if res and shinfo.hIcon:
                extracted_img = _hicon_to_image(shinfo.hIcon, size=size)
                user32.DestroyIcon(shinfo.hIcon)
        except Exception:
            extracted_img = None

    if extracted_img is None:
        fallback_name = app_name or (os.path.basename(file_path) if file_path else "App")
        extracted_img = generate_fallback_icon(fallback_name, size=size)

    if cache_dir and extracted_img:
        try:
            cached_file = os.path.join(cache_dir, f"{app_id}.png")
            extracted_img.save(cached_file, format="PNG")
        except Exception:
            pass

    return extracted_img
