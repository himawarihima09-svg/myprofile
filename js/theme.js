/* theme.js … 夜のおやつモード（ダークモード）の切り替え
   ・最初は、見ている人の端末の設定（ダーク／ライト）に合わせる
   ・右下のまるいボタンで切り替えると、その好みをブラウザに覚えておく
   ・<head> の中で読み込むので、ページが表示される前に色が決まる（白く光るチラつきを防ぐ） */
(function () {
  var KEY = 'shintaya-theme';
  var root = document.documentElement;
  var mq = window.matchMedia ? matchMedia('(prefers-color-scheme: dark)') : null;

  function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function remember(t) { try { localStorage.setItem(KEY, t); } catch (e) {} }

  function apply(t) {
    root.setAttribute('data-theme', t);
    var btn = document.getElementById('theme-toggle');
    if (btn) {
      var dark = t === 'dark';
      btn.textContent = dark ? '☀️' : '🌙';
      btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
      btn.title = dark ? 'ひるのモードにする / Light mode' : 'よるのモードにする / Dark mode';
      btn.setAttribute('aria-label', btn.title);
    }
  }

  apply(saved() || (mq && mq.matches ? 'dark' : 'light'));

  // 自分で切り替えていない人は、端末の設定が変わったらそれに合わせる
  if (mq) {
    var follow = function (e) { if (!saved()) apply(e.matches ? 'dark' : 'light'); };
    if (mq.addEventListener) mq.addEventListener('change', follow); else if (mq.addListener) mq.addListener(follow);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.createElement('button');
    btn.id = 'theme-toggle';
    btn.type = 'button';
    btn.className = 'theme-toggle';
    document.body.appendChild(btn);
    apply(root.getAttribute('data-theme'));

    btn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      // 切り替えの瞬間だけ、色がふわっと変わるようにする
      root.classList.add('theme-anim');
      apply(next);
      remember(next);
      btn.classList.remove('pop'); void btn.offsetWidth; btn.classList.add('pop');
      setTimeout(function () { root.classList.remove('theme-anim'); }, 600);
    });
  });
})();
