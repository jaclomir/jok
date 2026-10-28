
(function(){
 var b=document.getElementById('motyw'),n=document.getElementById('motywNapis'),h=document.documentElement;
 var mq=window.matchMedia?window.matchMedia('(prefers-color-scheme: dark)'):null;
 function teraz(){var t=h.getAttribute('data-theme');return t||(mq&&mq.matches?'dark':'light');}
 function napis(){n.textContent=teraz()==='dark'?'Jasny':'Ciemny';}
 b.addEventListener('click',function(){var nowy=teraz()==='dark'?'light':'dark';h.setAttribute('data-theme',nowy);try{localStorage.setItem('domowydrukarz-motyw',nowy)}catch(e){}napis();});
 if(mq&&mq.addEventListener)mq.addEventListener('change',napis);
 napis();
})();
