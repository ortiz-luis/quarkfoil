from __future__ import annotations

import json
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
    diagnostics = []
    try:
        driver.set_window_size(1280, 720)
        driver.get(f"http://127.0.0.1:{server.server_port}/print.html?preview")
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.documentElement.dataset.previewReady === 'true'")
        )
        WebDriverWait(driver, 30).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#slides section.scientific-slide")) > 0
        )

        sections = driver.find_elements(By.CSS_SELECTOR, "#slides section.scientific-slide")
        count = len(sections)
        driver.execute_script(
            "document.querySelector('.reveal').style.width='1280px';"
            "document.querySelector('.reveal').style.height='720px';"
            "document.querySelector('.slides').style.width='1280px';"
            "document.querySelector('.slides').style.height='720px';"
            "document.querySelector('.slides').style.transform='none';"
            "document.body.style.margin='0';"
            "document.body.style.overflow='hidden';"
        )

        for index in range(count):
            driver.execute_script(
                "const sections=[...document.querySelectorAll('#slides section.scientific-slide')];"
                "sections.forEach((s,i)=>{"
                "s.hidden=false;"
                "s.classList.remove('present','past','future');"
                "s.style.display=i===arguments[0]?'block':'none';"
                "s.style.position='absolute';s.style.inset='0';"
                "s.style.width='1280px';s.style.height='720px';"
                "s.style.margin='0';s.style.transform='none';s.style.opacity='1';"
                "});",
                index,
            )
            time.sleep(0.1)
            slide = driver.find_elements(By.CSS_SELECTOR, "#slides section.scientific-slide")[index]
            diag = driver.execute_script(
                "const s=arguments[0];"
                "const pick=(sel)=>{const e=s.querySelector(sel);if(!e)return null;const r=e.getBoundingClientRect();const c=getComputedStyle(e);return {sel,x:r.x,y:r.y,w:r.width,h:r.height,position:c.position,left:c.left,top:c.top,fontSize:c.fontSize,fontFamily:c.fontFamily,lineHeight:c.lineHeight,display:c.display,transform:c.transform};};"
                "const sr=s.getBoundingClientRect();"
                "return {id:s.dataset.slideId,slide:{x:sr.x,y:sr.y,w:sr.width,h:sr.height},title:pick('.slide-title'),titleHeading:pick('.slide-title h1,.slide-title h2,.slide-title h3'),core:pick('.slide-core'),cell:pick('.slide-cell'),footer:pick('.slide-footer'),frame:pick('.slide-frame')};",
                slide,
            )
            diagnostics.append(diag)
            slide.screenshot(str(OUT / f"page-{index + 1}.png"))

        (OUT / "layout-diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
        print(json.dumps(diagnostics, indent=2))
        print(f"PASQAL_VISUAL_SCREENSHOTS={count}")
        return 0
    finally:
        driver.quit()
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
