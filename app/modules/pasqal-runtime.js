export function applyPasqalRuntime(root = document) {
  const slides = [...root.querySelectorAll('.scientific-slide[data-slide-id^="pasqal-"]')];

  slides.forEach(slide => {
    if (!slide.querySelector(':scope > .pasqal-logo')) {
      const logo = document.createElement('img');
      logo.className = 'pasqal-logo';
      logo.alt = 'Pasqal';
      logo.src = './assets/pasqal-logo-light.svg';
      logo.setAttribute('aria-hidden', 'true');
      slide.appendChild(logo);
    }
  });

  const numbered = slides.filter(slide => {
    const id = slide.dataset.slideId || '';
    return id !== 'pasqal-front' && id !== 'pasqal-closing' && !id.startsWith('pasqal-section-');
  });
  const total = String(numbered.length);
  numbered.forEach((slide, index) => {
    slide.dataset.pasqalPage = String(index + 1);
    slide.dataset.pasqalTotal = total;
    const footer = slide.querySelector('.slide-footer');
    if (footer) {
      footer.dataset.pasqalPage = String(index + 1);
      footer.dataset.pasqalTotal = total;
    }
  });
  slides.filter(slide => !numbered.includes(slide)).forEach(slide => {
    slide.dataset.pasqalPage = '';
    slide.dataset.pasqalTotal = total;
  });
}
