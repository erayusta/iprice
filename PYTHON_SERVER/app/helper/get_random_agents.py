import random
from datetime import datetime, timedelta


def get_random_user_agent():
    """Dinamik olarak rastgele bir user-agent string oluşturur"""

    # Tarayıcı türünü seç
    browser_type = random.choice(['chrome', 'firefox', 'safari', 'edge'])

    if browser_type == 'chrome':
        return generate_chrome_user_agent()
    elif browser_type == 'firefox':
        return generate_firefox_user_agent()
    elif browser_type == 'safari':
        return generate_safari_user_agent()
    elif browser_type == 'edge':
        return generate_edge_user_agent()


def generate_chrome_user_agent():
    """Chrome user-agent dinamik olarak oluşturur"""
    # Chrome versiyonu (115-125 arası)
    major_version = random.randint(115, 125)
    minor_version = random.randint(0, 5)
    build_version = random.randint(0, 9999)
    patch_version = random.randint(0, 999)

    chrome_version = f"{major_version}.{minor_version}.{build_version}.{patch_version}"

    # WebKit versiyonu
    webkit_version = "537.36"

    # İşletim sistemi seç
    os_info = random.choice([
        generate_windows_os(),
        generate_macos_os(),
        generate_linux_os()
    ])

    return f"Mozilla/5.0 ({os_info}) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}"


def generate_firefox_user_agent():
    """Firefox user-agent dinamik olarak oluşturur"""
    # Firefox versiyonu (100-125 arası)
    version = random.randint(100, 125)

    # İşletim sistemi seç
    os_info = random.choice([
        generate_windows_os(),
        generate_macos_firefox_os(),
        generate_linux_firefox_os()
    ])

    return f"Mozilla/5.0 ({os_info}; rv:{version}.0) Gecko/20100101 Firefox/{version}.0"


def generate_safari_user_agent():
    """Safari user-agent dinamik olarak oluşturur"""
    # Safari versiyonu
    safari_major = random.randint(16, 17)
    safari_minor = random.randint(0, 6)

    # WebKit versiyonu
    webkit_major = random.randint(605, 615)
    webkit_minor = random.randint(1, 15)
    webkit_patch = random.randint(1, 99)

    webkit_version = f"{webkit_major}.{webkit_minor}.{webkit_patch}"
    safari_version = f"{safari_major}.{safari_minor}"

    # macOS bilgisi
    macos = generate_macos_os()

    return f"Mozilla/5.0 ({macos}) AppleWebKit/{webkit_version} (KHTML, like Gecko) Version/{safari_version} Safari/{webkit_version}"


def generate_edge_user_agent():
    """Edge user-agent dinamik olarak oluşturur"""
    # Edge Chromium tabanlı, Chrome versiyonu kullan
    major_version = random.randint(115, 125)
    minor_version = random.randint(0, 5)
    build_version = random.randint(0, 9999)
    patch_version = random.randint(0, 999)

    chrome_version = f"{major_version}.{minor_version}.{build_version}.{patch_version}"
    edge_version = f"{major_version}.{minor_version}.{build_version}.{patch_version}"

    # Windows OS (Edge sadece Windows'ta)
    os_info = generate_windows_os()

    return f"Mozilla/5.0 ({os_info}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36 Edg/{edge_version}"


def generate_windows_os():
    """Windows işletim sistemi bilgisi oluşturur"""
    # Windows versiyonları
    windows_versions = [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 10.0; WOW64",
        "Windows NT 11.0; Win64; x64"
    ]
    return random.choice(windows_versions)


def generate_macos_os():
    """macOS işletim sistemi bilgisi oluşturur"""
    # macOS versiyonları
    major_version = random.randint(10, 14)

    if major_version == 10:
        minor_version = random.randint(15, 15)  # macOS 10.15 Catalina
        patch_version = random.randint(0, 7)
    else:
        minor_version = random.randint(0, 6)
        patch_version = random.randint(0, 9)

    # Intel veya Apple Silicon
    processor = random.choice([
        "Intel Mac OS X",
        "PPC Mac OS X"  # Eski sistemler için
    ])

    return f"Macintosh; {processor} {major_version}_{minor_version}_{patch_version}"


def generate_macos_firefox_os():
    """Firefox için macOS bilgisi"""
    major_version = random.randint(10, 14)
    minor_version = random.randint(0, 15)

    return f"Macintosh; Intel Mac OS X {major_version}.{minor_version}"


def generate_linux_os():
    """Linux işletim sistemi bilgisi oluşturur"""
    # Linux dağıtımları
    distros = [
        "X11; Linux x86_64",
        "X11; Ubuntu; Linux x86_64",
        "X11; Linux i686",
        "X11; Fedora; Linux x86_64",
        "X11; CentOS; Linux x86_64"
    ]
    return random.choice(distros)


def generate_linux_firefox_os():
    """Firefox için Linux bilgisi"""
    return random.choice([
        "X11; Linux x86_64",
        "X11; Ubuntu; Linux x86_64",
        "X11; Linux i686"
    ])