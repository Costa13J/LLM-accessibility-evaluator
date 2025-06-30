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
    function tryClick(selector) {
        const el = document.querySelector(selector);
        if (el && typeof el.click === 'function') {
            el.click();
            console.log('Clicked:', selector);
            return true;
        }
        return false;
    }

    const tried = [
        '#onetrust-accept-btn-handler', // OneTrust
        '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll', // Cookiebot
        '#accept-cookies',              // Generic
        '#cookie-accept-button',
    ];

    let clicked = false;
    for (const sel of tried) {
        if (tryClick(sel)) {
            clicked = true;
            break;
        }
    }

    if (!clicked) {
        const buttonSelectors = [
            '[id*="onetrust"] button',
            '[class*="onetrust"] button',
            '[id*="CybotCookiebot"] button',
            '[class*="CybotCookiebot"] button',
            'button[aria-label*="cookie"]',
            'button[aria-label*="consent"]',
            'button[id*="cookie"]',
            'button[class*="cookie"]',
            'button[name*="cookie"]',
            '[id*="cookie"] button',
            '[class*="cookie"] button',
            '[id*="consent"] button',
            '[class*="consent"] button'
        ];

        buttonSelectors.forEach(sel => {
            if (clicked) return;
            const btns = document.querySelectorAll(sel);
            btns.forEach(btn => {
                if (btn && typeof btn.click === 'function' && !clicked) {
                    const text = btn.innerText?.toLowerCase() || '';
                    if (text.includes('accept') || text.includes('agree') || text.includes('yes')) {
                        btn.click();
                        console.log('Clicked generic selector:', sel, 'with text:', text);
                        clicked = true;
                    }
                }
            });
        });
    }

    if (!clicked) {
        const containers = document.querySelectorAll('[aria-label*="cookie"], [aria-label*="consent"]');
        containers.forEach(container => {
            if (clicked) return;
            const buttons = container.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn && typeof btn.click === 'function') {
                    const text = btn.innerText?.toLowerCase() || '';
                    if (text.includes('accept') || text.includes('agree') || text.includes('yes')) {
                        btn.click();
                        console.log('Clicked container fallback:', text);
                        clicked = true;
                    }
                }
            });
        });
    }
    """
    driver.execute_script(js)


