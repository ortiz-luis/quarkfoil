from __future__ import annotations

import tempfile
import threading
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from scientific_slides.server import create_server

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "examples" / "pasqal-golden" / "deck.md"
OUT = ROOT / "artifacts" / "pasqal-visual"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    server = create_server(DECK, "127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    try:
        driver.set_window_size(1890, 1063)
        driver.get(f"http://127.0.0.1:{server.server_port}/")
        WebDriverWait(driver, 30).until(
            lambda d: d.find_element(By.ID, "save-state").text == "Saved"
        )
        WebDriverWait(driver, 30).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#slides section.scientific-slide")) > 0
        )

        count = len(driver.find_elements(By.CSS_SELECTOR, "#slides section.scientific-slide"))
        for index in range(count):
            driver.execute_script("window.Reveal.slide(arguments[0]);", index)
            WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.CSS_SELECTOR, "#slides section.present").get_attribute("data-slide-index") == str(index)
            )
            driver.execute_script(
                "document.querySelector('#toolbar').style.display='none';"
                "document.querySelector('#slide-sidebar').style.display='none';"
                "document.querySelector('#properties').style.display='none';"
                "document.querySelector('.notes-pane').style.display='none';"
                "document.querySelector('#notes-resizer').style.display='none';"
                "document.querySelector('#workspace').style.display='block';"
                "document.querySelector('#stage').style.position='fixed';"
                "document.querySelector('#stage').style.inset='0';"
                "document.querySelector('#stage').style.padding='0';"
                "document.body.style.margin='0';"
            )
            time.sleep(0.15)
            slide = driver.find_element(By.CSS_SELECTOR, "#slides section.present")
            slide.screenshot(str(OUT / f"page-{index + 1}.png"))

        print(f"PASQAL_VISUAL_SCREENSHOTS={count}")
        return 0
    finally:
        driver.quit()
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
