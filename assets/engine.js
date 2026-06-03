/* Fontletr — shared Unicode style engine + app. Reads window.PAGE_CONFIG = {focusStyles:[ids], ...} */
(function(){
'use strict';
var A='ABCDEFGHIJKLMNOPQRSTUVWXYZ',a='abcdefghijklmnopqrstuvwxyz',D='0123456789';
function offsetMap(uS,lS,dS,exc){var m={},i,k;for(i=0;i<26;i++){if(uS!=null)m[A[i]]=String.fromCodePoint(uS+i);if(lS!=null)m[a[i]]=String.fromCodePoint(lS+i);}if(dS!=null)for(i=0;i<10;i++)m[D[i]]=String.fromCodePoint(dS+i);if(exc)for(k in exc)m[k]=exc[k];return m;}
/* Mathematical Alphanumeric Symbols has reserved holes — Unicode placed those letters in the Letterlike Symbols block instead. Patch them in or browsers render □. */
var EXC_ITALIC={h:'ℎ'};
var EXC_SCRIPT={B:'ℬ',E:'ℰ',F:'ℱ',H:'ℋ',I:'ℐ',L:'ℒ',M:'ℳ',R:'ℛ',e:'ℯ',g:'ℊ',o:'ℴ'};
var EXC_FRAKTUR={C:'ℭ',H:'ℌ',I:'ℑ',R:'ℜ',Z:'ℨ'};
var EXC_DSTRUCK={C:'ℂ',H:'ℍ',N:'ℕ',P:'ℙ',Q:'ℚ',R:'ℝ',Z:'ℤ'};
function pairMap(f,t){var tt=Array.from(t),m={},i;for(i=0;i<f.length;i++)m[f[i]]=tt[i];return m;}
function applyMap(s,m,c){var o='',ch,arr=Array.from(s),i;for(i=0;i<arr.length;i++){ch=arr[i];o+=(m[ch]!=null?m[ch]:ch);if(c)o+=c;}return o;}
function buildSimple(base){return (function(){var m={},i;for(i=0;i<26;i++){m[A[i]]=String.fromCodePoint(base+i);m[a[i]]=String.fromCodePoint(base+i);}return m;})();}
var smallCaps=pairMap(a,'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ');
var superscript=pairMap(a,'ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖqʳˢᵗᵘᵛʷˣʸᶻ');
var subscript=pairMap('aehijklmnoprstuvx','ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ');

var STYLES=[
  {id:'bold-sans',name:'Bold (sans)',cat:'bold',fn:function(s){return applyMap(s,offsetMap(0x1D5D4,0x1D5EE,0x1D7EC));}},
  {id:'bold-serif',name:'Bold (serif)',cat:'bold',fn:function(s){return applyMap(s,offsetMap(0x1D400,0x1D41A,0x1D7CE));}},
  {id:'italic',name:'Italic',cat:'bold',fn:function(s){return applyMap(s,offsetMap(0x1D434,0x1D44E,null,EXC_ITALIC));}},
  {id:'bold-italic',name:'Bold italic',cat:'bold',fn:function(s){return applyMap(s,offsetMap(0x1D468,0x1D482,null));}},
  {id:'sans-italic',name:'Sans italic',cat:'bold',fn:function(s){return applyMap(s,offsetMap(0x1D608,0x1D622,null));}},
  {id:'sans-serif',name:'Sans-serif',cat:'bold',fn:function(s){return applyMap(s,offsetMap(0x1D5A0,0x1D5BA,0x1D7E2));}},
  {id:'script-cursive',name:'Script · cursive',cat:'callig',fn:function(s){return applyMap(s,offsetMap(0x1D49C,0x1D4B6,null,EXC_SCRIPT));}},
  {id:'bold-script',name:'Bold script',cat:'callig',fn:function(s){return applyMap(s,offsetMap(0x1D4D0,0x1D4EA,null));}},
  {id:'fraktur',name:'Fraktur (Old English)',cat:'callig',fn:function(s){return applyMap(s,offsetMap(0x1D504,0x1D51E,null,EXC_FRAKTUR));}},
  {id:'bold-fraktur',name:'Bold fraktur',cat:'callig',fn:function(s){return applyMap(s,offsetMap(0x1D56C,0x1D586,null));}},
  {id:'small-caps',name:'Small caps',cat:'callig',fn:function(s){return applyMap(s.toLowerCase(),smallCaps);}},
  {id:'double-struck',name:'Double-struck',cat:'outline',fn:function(s){return applyMap(s,offsetMap(0x1D538,0x1D552,0x1D7D8,EXC_DSTRUCK));}},
  {id:'monospace',name:'Monospace',cat:'outline',fn:function(s){return applyMap(s,offsetMap(0x1D670,0x1D68A,0x1D7F6));}},
  {id:'full-width',name:'Full-width',cat:'deco',fn:function(s){return applyMap(s,(function(){var m={},i;for(i=0;i<26;i++){m[A[i]]=String.fromCodePoint(0xFF21+i);m[a[i]]=String.fromCodePoint(0xFF41+i);}for(i=0;i<10;i++)m[D[i]]=String.fromCodePoint(0xFF10+i);m[' ']='　';return m;})());}},
  {id:'circled',name:'Circled (bubble)',cat:'deco',fn:function(s){return applyMap(s,(function(){var m={},i;for(i=0;i<26;i++){m[A[i]]=String.fromCodePoint(0x24B6+i);m[a[i]]=String.fromCodePoint(0x24D0+i);}m['0']='⓪';for(i=1;i<=9;i++)m[D[i]]=String.fromCodePoint(0x2460+i-1);return m;})());}},
  {id:'circled-negative',name:'Circled (filled)',cat:'deco',fn:function(s){return applyMap(s,(function(){var m={},i;for(i=0;i<26;i++){m[A[i]]=String.fromCodePoint(0x1F150+i);m[a[i]]=String.fromCodePoint(0x1F150+i);}return m;})());}},
  {id:'squared',name:'Squared',cat:'deco',fn:function(s){return applyMap(s,(function(){var m={},i;for(i=0;i<26;i++){m[A[i]]=String.fromCodePoint(0x1F130+i);m[a[i]]=String.fromCodePoint(0x1F130+i);}return m;})());}},
  {id:'parenthesized',name:'Parenthesized',cat:'deco',fn:function(s){return applyMap(s,(function(){var m={},i;for(i=0;i<26;i++){m[a[i]]=String.fromCodePoint(0x249C+i);m[A[i]]=String.fromCodePoint(0x249C+i);}return m;})());}},
  {id:'bracketed',name:'Bracketed ⟦x⟧',cat:'deco',fn:function(s){return Array.from(s).map(function(c){return c===' '?' ':'⟦'+c+'⟧';}).join('');}},
  {id:'superscript',name:'Superscript',cat:'fun',fn:function(s){return applyMap(applyMap(s.toLowerCase(),superscript),smallCaps);}},
  {id:'subscript',name:'Subscript',cat:'fun',fn:function(s){return applyMap(applyMap(s.toLowerCase(),subscript),smallCaps);}},
  {id:'spaced',name:'Wide spaced',cat:'fun',fn:function(s){return Array.from(s).join(' ');}},
  {id:'dotted',name:'Dotted',cat:'fun',fn:function(s){return Array.from(s).join('·');}},
  {id:'upside-down',name:'Upside down',cat:'fun',fn:function(s){var f={'a':'ɐ','b':'q','c':'ɔ','d':'p','e':'ǝ','f':'ɟ','g':'ƃ','h':'ɥ','i':'ᴉ','j':'ɾ','k':'ʞ','l':'l','m':'ɯ','n':'u','o':'o','p':'d','q':'b','r':'ɹ','s':'s','t':'ʇ','u':'n','v':'ʌ','w':'ʍ','x':'x','y':'ʎ','z':'z','.':'˙',',':"'",'?':'¿','!':'¡',"'":',','"':',,','(':')',')':'('};return Array.from(s.toLowerCase()).reverse().map(function(c){return f[c]||c;}).join('');}},
  {id:'reversed',name:'Reversed (mirror)',cat:'fun',fn:function(s){return Array.from(s).reverse().join('');}},
  {id:'strikethrough',name:'Strikethrough',cat:'fx',fn:function(s){return applyMap(s,{},'̶');}},
  {id:'underline',name:'Underline',cat:'fx',fn:function(s){return applyMap(s,{},'̲');}},
  {id:'double-underline',name:'Double underline',cat:'fx',fn:function(s){return applyMap(s,{},'̳');}},
  {id:'slashed',name:'Slashed',cat:'fx',fn:function(s){return applyMap(s,{},'̸');}},
  {id:'zalgo',name:'Zalgo (glitch)',cat:'fx',fn:function(s){var u=['̍','̎','̄','̅','̿','̑','̆','̐','͒','͗'],o='',arr=Array.from(s),i,j,n,ch;for(i=0;i<arr.length;i++){ch=arr[i];o+=ch;n=ch.trim()?1+Math.floor(Math.random()*2):0;for(j=0;j<n;j++)o+=u[Math.floor(Math.random()*u.length)];}return o;}}
];
var CAT_LABEL={bold:'Weight',callig:'Calligraphic',outline:'Outline',deco:'Decorative',fx:'Effect',fun:'Misc'};
var byId={};STYLES.forEach(function(s){byId[s.id]=s;});

/* ---- app: two-panel "translator" — type left, see chosen style right ---- */
var cfg=window.PAGE_CONFIG||{focusStyles:[]};
var L=cfg.labels||{}, G=cfg.groups||{}, U=cfg.ui||{};
function styleName(st){return L[st.id]||st.name;}
function groupLabel(c){return G[c]||CAT_LABEL[c];}
function ui(k,d){return (U[k]!=null)?U[k]:d;}
var SAMPLE=ui('sample',SAMPLE);
var focus=(cfg.focusStyles||[]).map(function(id){return byId[id];}).filter(Boolean);
var selectable=focus.length?focus:STYLES;
var current=focus[0]||byId['script-cursive']||STYLES[0];

var input=document.getElementById('input'),
    styleSelect=document.getElementById('styleSelect'),
    bigOut=document.getElementById('bigOut'),
    bigCopy=document.getElementById('bigCopy'),
    results=document.getElementById('results'),
    counter=document.getElementById('counter'),
    styleCount=document.getElementById('styleCount');
var FAV_KEY='fontgen_favs';
var favs=new Set();try{favs=new Set(JSON.parse(localStorage.getItem(FAV_KEY)||'[]'));}catch(e){}
var favOnly=false;
function saveFavs(){try{localStorage.setItem(FAV_KEY,JSON.stringify(Array.from(favs)));}catch(e){}}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function escA(s){return String(s).replace(/"/g,'&quot;');}
function output(st,text){try{return st.fn(text);}catch(e){return text;}}

/* fill the right-panel <select> */
function populateSelect(){
  if(!styleSelect)return;
  var html='';
  if(selectable.length<=6){
    selectable.forEach(function(st){html+='<option value="'+escA(st.id)+'">'+esc(styleName(st))+'</option>';});
  }else{
    var byCat={};STYLES.forEach(function(st){(byCat[st.cat]=byCat[st.cat]||[]).push(st);});
    ['callig','bold','outline','deco','fx','fun'].forEach(function(c){
      if(!byCat[c])return;
      html+='<optgroup label="'+esc(groupLabel(c))+'">';
      byCat[c].forEach(function(st){html+='<option value="'+escA(st.id)+'">'+esc(styleName(st))+'</option>';});
      html+='</optgroup>';
    });
  }
  styleSelect.innerHTML=html;
  styleSelect.value=current.id;
}

function render(){
  var raw=input.value, isPh=raw.length===0, text=isPh?SAMPLE:raw;
  if(counter)counter.textContent=raw.length+' '+(raw.length===1?ui('charOne','character'):ui('charMany','characters'));

  /* right panel: the currently chosen style */
  if(bigOut){
    var out=output(current,text);
    bigOut.innerHTML=isPh?'<span class="ph">'+esc(out)+'</span>':esc(out);
  }

  /* the full list below (hub only — #results doesn't exist on spoke pages) */
  if(!results)return;
  var ordered=STYLES.slice().sort(function(x,y){return (favs.has(x.id)?0:1)-(favs.has(y.id)?0:1);});
  var list=favOnly?ordered.filter(function(s){return favs.has(s.id);}):ordered;
  if(styleCount)styleCount.textContent=list.length+' '+ui('styles','styles');
  if(list.length===0){results.innerHTML=ui('noFavs','No favorites yet — tap a star next to any style to pin it here.');return;}
  var html='',favHeaderDone=false,allHeaderDone=(favs.size===0||favOnly);
  list.forEach(function(st){
    if(favs.has(st.id)&&!favHeaderDone){html+='<div class="grouphead">'+ui('pinned','★ Pinned')+'</div>';favHeaderDone=true;}
    if(!favs.has(st.id)&&!allHeaderDone){html+='<div class="grouphead">'+ui('allStyles','All styles')+'</div>';allHeaderDone=true;}
    var o=output(st,text);
    var pv=isPh?'<span class="ph">'+esc(o)+'</span>':esc(o);
    html+='<div class="row'+(st.id===current.id?' active':'')+'" data-id="'+escA(st.id)+'">'
      +'<span class="name"><span class="dot d-'+st.cat+'"></span>'+esc(styleName(st))+'</span>'
      +'<span class="preview">'+pv+'</span>'
      +'<button class="star '+(favs.has(st.id)?'on':'')+'" data-act="star" title="'+escA(ui('pinTitle','Pin to top'))+'">'+(favs.has(st.id)?'★':'☆')+'</button>'
      +'<button class="copy" data-act="copy">'+esc(ui('copy','Copy'))+'</button></div>';
  });
  results.innerHTML=html;
}

function findStyle(el){var w=el.closest('[data-id]');return w?byId[w.dataset.id]:null;}
function flashBtn(btn){btn.textContent=ui('copied','✓ Copied');btn.classList.add('done');setTimeout(function(){btn.textContent=ui('copy','Copy');btn.classList.remove('done');},1400);}
function copyText(txt,btn,row){
  function ok(){if(btn)flashBtn(btn);if(row){row.classList.add('flash');setTimeout(function(){row.classList.remove('flash');},1400);}}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(ok,function(){fallbackCopy(txt);ok();});}
  else{fallbackCopy(txt);ok();}
}
function fallbackCopy(txt){var ta=document.createElement('textarea');ta.value=txt;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(ta);}
function curText(){return input.value.length?input.value:SAMPLE;}
function setCurrent(st){if(!st)return;current=st;if(styleSelect)styleSelect.value=st.id;render();}

/* right-panel copy */
if(bigCopy)bigCopy.addEventListener('click',function(){copyText(output(current,curText()),bigCopy,bigOut?bigOut.parentElement:null);});
/* style dropdown */
if(styleSelect)styleSelect.addEventListener('change',function(){setCurrent(byId[this.value]);});

/* list interactions (hub) */
if(results)results.addEventListener('click',function(e){
  var btn=e.target.closest('button');
  if(btn&&btn.dataset.act){
    var st=findStyle(btn);if(!st)return;
    var row=btn.closest('.row');
    if(btn.dataset.act==='copy')copyText(output(st,curText()),btn,row);
    else if(btn.dataset.act==='star'){favs.has(st.id)?favs.delete(st.id):favs.add(st.id);saveFavs();render();}
    return;
  }
  var rowEl=e.target.closest('.row');
  if(rowEl){var st2=byId[rowEl.dataset.id];setCurrent(st2);if(window.scrollY>0)window.scrollTo({top:0,behavior:'smooth'});}
});

function debounce(fn,ms){var t;return function(){var args=arguments;clearTimeout(t);t=setTimeout(function(){fn.apply(null,args);},ms);};}
input.addEventListener('input',debounce(render,40));
var clr=document.getElementById('clearBtn');if(clr)clr.addEventListener('click',function(){input.value='';render();input.focus();});
var fo=document.getElementById('favOnly');if(fo)fo.addEventListener('click',function(){favOnly=!favOnly;var st=document.getElementById('favState');if(st)st.textContent=favOnly?ui('on','On'):ui('off','Off');render();});

/* theme */
var themeBtn=document.getElementById('themeBtn');
function setTheme(t){document.documentElement.dataset.theme=t;try{localStorage.setItem('fontgen_theme',t);}catch(e){}if(themeBtn)themeBtn.textContent=ui('theme','Theme: ')+(t==='dark'?ui('dark','Dark'):ui('light','Light'))+' ▾';}
var savedTheme;try{savedTheme=localStorage.getItem('fontgen_theme');}catch(e){}
setTheme(savedTheme||'light');
if(themeBtn)themeBtn.addEventListener('click',function(){setTheme(document.documentElement.dataset.theme==='dark'?'light':'dark');});

/* generic copy-to-clipboard for any [data-copy] button (kaomoji library, etc.) */
document.addEventListener('click',function(e){
  var b=e.target.closest('[data-copy]');if(!b)return;
  var txt=b.getAttribute('data-copy');
  function flash(){b.classList.add('copied');setTimeout(function(){b.classList.remove('copied');},900);}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(flash,function(){fallbackCopy(txt);flash();});}
  else{fallbackCopy(txt);flash();}
});

populateSelect();
render();
})();
