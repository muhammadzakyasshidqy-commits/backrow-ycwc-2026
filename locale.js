(function(){
  const q=new URLSearchParams(location.search);
  const requested=q.get('lang');
  let stored=null;try{stored=localStorage.getItem('backrow-lang')}catch{}
  let lang=(requested==='id'||requested==='en')?requested:(stored==='id'||stored==='en'?stored:(navigator.language||'en').toLowerCase().startsWith('id')?'id':'en');
  function setLang(next){lang=next==='id'?'id':'en';try{localStorage.setItem('backrow-lang',lang)}catch{}document.documentElement.lang=lang;const u=new URL(location.href);u.searchParams.set('lang',lang);history.replaceState(null,'',u);window.dispatchEvent(new CustomEvent('backrow:lang',{detail:{lang}}));}
  function toggle(){setLang(lang==='en'?'id':'en')}
  function get(){return lang}
  function withLang(url){const u=new URL(url,location.href);u.searchParams.set('lang',lang);return u.pathname+u.search+u.hash}
  window.BACKROW_LOCALE={get,set:setLang,toggle,withLang};
  document.documentElement.lang=lang;
})();
