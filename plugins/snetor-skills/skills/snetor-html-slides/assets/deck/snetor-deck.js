const slides = Array.from(document.querySelectorAll('.slide'));
const progressBlocks = Array.from(document.querySelectorAll('.progress'));
const initialSlide = Number.parseInt(new URLSearchParams(window.location.search).get('slide') || '1', 10);
let current = Number.isFinite(initialSlide) ? initialSlide - 1 : 0;

function renderProgress() {
  progressBlocks.forEach((block) => {
    block.innerHTML = '';
    slides.forEach((_, index) => {
      const segment = document.createElement('span');
      if (index <= current) segment.classList.add('on');
      block.appendChild(segment);
    });
  });
}

function show(index) {
  current = Math.max(0, Math.min(slides.length - 1, index));
  slides.forEach((slide, i) => { slide.classList.toggle('active', i === current); });
  renderProgress();
  document.title = `${DECK_TITLE} - ${current + 1}/${slides.length}`;
}

document.getElementById('prev').addEventListener('click', () => show(current - 1));
document.getElementById('next').addEventListener('click', () => show(current + 1));

document.querySelectorAll('.check-card').forEach((card) => {
  card.addEventListener('click', () => {
    const isChecked = card.classList.toggle('checked');
    card.setAttribute('aria-pressed', String(isChecked));
  });
});

document.addEventListener('keydown', (event) => {
  if (event.target.closest && event.target.closest('.check-card')) return;
  if (['ArrowRight', 'PageDown', ' '].includes(event.key)) { event.preventDefault(); show(current + 1); }
  if (['ArrowLeft', 'PageUp'].includes(event.key)) { event.preventDefault(); show(current - 1); }
  if (event.key === 'Home') show(0);
  if (event.key === 'End') show(slides.length - 1);
});

show(current);
