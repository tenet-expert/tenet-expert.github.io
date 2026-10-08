(function(){
  var s=document.createElement("script");
  s.src="https://raw.githubusercontent.com/tenet-expert/tenet-expert.github.io/45bab20b0f90da339214223260c7a2e4f3bab1b8/duty-overlay.js";
  document.head.appendChild(s);
})();
(function(){
  var SALES=[
    {when:"01.10.2026 12:00", who:"Демьянов", client:"Ахмеев", model:"T7"},
    {when:"02.10.2026 12:00", who:"Павлова", client:"А-Лизинг", model:"T7"},
    {when:"02.10.2026 12:01", who:"Тальков", client:"Базарова", model:"T4L"},
    {when:"04.10.2026 12:00", who:"Демьянов", client:"Мосольгин", model:"T7"},
    {when:"04.10.2026 12:01", who:"Лавров", client:"Антипов", model:"T4L"},
    {when:"05.10.2026 12:00", who:"Лавров", client:"Попов", model:"T8"},
    {when:"05.10.2026 12:01", who:"Спицын", client:"Ледкова", model:"T4L"},
    {when:"06.10.2026 12:00", who:"Спицын", client:"Антонов", model:"T8"},
    {when:"06.10.2026 12:01", who:"Спицын", client:"Шашков", model:"T4L"},
    {when:"07.10.2026 12:00", who:"Спицын", client:"Стрельников", model:"T7"}
  ];
  function apply(oct){
    if(!oct || oct.__sales) return;
    oct.forEach(function(r){ r.issue=0; });
    SALES.forEach(function(s){
      oct.push({when:s.when, who:s.who, client:s.client, model:s.model, visit:0, call:0, web:0, meet:0, service:0, td:0, contract:0, issue:1, note:"вкладка Продажи"});
    });
    oct.__sales=1;
  }
  function hook(){
    if(typeof boardEnsure!=="function" || boardEnsure.__sales) return;
    var orig=boardEnsure;
    var wrapped=async function(){
      var cache=await orig();
      if(cache && cache.oct) apply(cache.oct);
      return cache;
    };
    wrapped.__sales=1;
    try { boardEnsure=wrapped; } catch(e) {}
  }
  hook();
  var n=0;
  var t=setInterval(function(){ hook(); if(++n>40) clearInterval(t); }, 250);
  if(typeof boardLoad==="function") setTimeout(function(){ try{ boardLoad(); }catch(e){} }, 100);
})();
