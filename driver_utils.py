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
    const buttonSelectors = [
        '[id*="onetrust"] button',
        '[class*="onetrust"] button',
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

    let clicked = false;

    // First: Try all known/selective button selectors
    buttonSelectors.forEach(sel => {
        const btns = document.querySelectorAll(sel);
        btns.forEach(btn => {
            if (btn && btn.offsetParent !== null && !clicked) {
                try {
                    const text = btn.innerText.toLowerCase();
                    if (text.includes("accept") || text.includes("yes")) {
                        btn.click();
                        clicked = true;
                        console.log("Clicked button:", sel);
                    }
                } catch (e) {}
            }
        });
    });

    // Second: If no buttons matched, try containers with aria-label and click buttons inside
    if (!clicked) {
        const containers = document.querySelectorAll('[aria-label*="cookie"], [aria-label*="consent"]');
        containers.forEach(container => {
            const buttons = container.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn && btn.offsetParent !== null && !clicked) {
                    try {
                        const text = btn.innerText.toLowerCase();
                        if (text.includes("accept") || text.includes("yes") || text.includes("agree")) {
                            btn.click();
                            clicked = true;
                            console.log("Clicked fallback button inside container:", text);
                        }
                    } catch (e) {}
                }
            });
        });
    }
    """
    driver.execute_script(js)
