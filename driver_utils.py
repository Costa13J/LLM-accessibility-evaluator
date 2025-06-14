from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_webdriver():
    """Configures and launches a headless Chrome browser."""
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Run without UI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())  
    return webdriver.Chrome(service=service, options=chrome_options)

def inject_cookie_dismiss_script(driver):
    js = """
    const selectors = [
        'button[id*="cookie"]',
        'button[class*="cookie"]',
        'button[name*="cookie"]',
        '[id*="cookie"] button',
        '[class*="cookie"] button',
        '[id*="consent"] button',
        '[class*="consent"] button',
        '[aria-label*="cookie"]',
        '[data-testid*="cookie"]'
    ];

    selectors.forEach(sel => {
        const btns = document.querySelectorAll(sel);
        btns.forEach(btn => {
            if (btn && btn.offsetParent !== null) {
                try { btn.click(); } catch (e) {}
            }
        });
    });
    """
    driver.execute_script(js)