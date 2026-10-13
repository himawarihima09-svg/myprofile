/* sweet.js … ふわふわスイーツとタップのキラッを出すだけの小さな仕掛け */
(function () {
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // 背景のスイーツ（スマホは少なめにして軽く）
  var items = ['🍰', '🍬', '🍓', '🧁', '✨', '🍭', '💗', '🍪'];
  var count = window.innerWidth < 520 ? 6 : 11;
  var sky = document.createElement('div');
  sky.className = 'sweet-sky';
  sky.setAttribute('aria-hidden', 'true');
  for (var i = 0; i < count; i++) {
    var s = document.createElement('span');
    s.textContent = items[i % items.length];
    s.style.left = (Math.random() * 96) + '%';
    s.style.fontSize = (14 + Math.random() * 14) + 'px';
    s.style.animationDuration = (16 + Math.random() * 14) + 's';
    s.style.animationDelay = (-Math.random() * 30) + 's';
    sky.appendChild(s);
  }
  document.body.insertBefore(sky, document.body.firstChild);

  // タップ・クリックしたところに小さな星が5つはじける
  var marks = ['✦', '♡', '✧', '·', '✦'];
  var colors = ['#ff8cba', '#6fd6c2', '#ffc94d', '#ff8cba', '#b99cff'];
  document.addEventListener('pointerdown', function (e) {
    for (var k = 0; k < 5; k++) {
      var p = document.createElement('span');
      p.className = 'sweet-spark';
      p.textContent = marks[k];
      p.style.color = colors[k];
      p.style.left = e.clientX + 'px';
      p.style.top = e.clientY + 'px';
      var ang = (Math.PI * 2 / 5) * k + Math.random() * .6;
      p.style.setProperty('--dx', Math.cos(ang) * 26 + 'px');
      p.style.setProperty('--dy', Math.sin(ang) * 26 + 'px');
      document.body.appendChild(p);
      setTimeout(function (el) { el.remove(); }, 750, p);
    }
  }, { passive: true });
})();
