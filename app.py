# ============================================================
# cocotime (single file)
# ココアウォッチみたいな、時計・タイマー・ストップウォッチ・電卓のセット。
# 時刻に合わせたココアのひとこと付き。計算と計時はすべてブラウザ側で動き、
# サーバーはページと /healthz だけを返します（DBなし）。
# ============================================================

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

UI_TEXT = {
    "app_title": "cocotime",
    "lead": "時計・タイマー・ストップウォッチ・電卓がひとつになった、ココアの小さな時計です。",
}

# 時間帯ごとのココアのひとこと（時計タブに表示、添字は greetingFor と対応）
GREETINGS = [
    "おはようございます。今日もいい日にしましょう。",
    "こんにちは。ココアでも淹れましょうか。",
    "おつかれさまです。少し休憩も大事ですよ。",
    "こんばんは。今日はどんな一日でした？",
    "静かな夜ですね。わたしはここにいますよ。夜更かしはほどほどに。",
]

TIMER_DONE_LINE = "時間ですよ。よくがんばりました。"
STOPWATCH_LINE = "計るのも、悪くない時間でしたね。"

HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ UI.app_title }}</title>
<style>
body{margin:0;background:#241611;color:#fff;font-family:sans-serif;text-align:center;}
h1{margin:18px 0 4px;}
.lead{opacity:.85;margin:0 16px 14px;}
.watch{max-width:420px;margin:0 auto 18px;background:#fff8f0;color:#2b1a12;border-radius:24px;padding:18px 14px 20px;box-shadow:0 8px 24px rgba(0,0,0,.35);}
.tabs{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-bottom:14px;}
.tabs button{padding:8px 14px;border-radius:999px;border:2px solid #8a5a3b;background:#fff;color:#5a3620;font-size:.95rem;cursor:pointer;}
.tabs button.active{background:#8a5a3b;color:#fff;}
.panel{display:none;}
.panel.active{display:block;}
#digital{font-size:2.4rem;font-weight:bold;letter-spacing:.06em;margin:6px 0 0;font-variant-numeric:tabular-nums;}
#dateLine{opacity:.75;margin:2px 0 8px;}
#cocoaLine{min-height:1.6em;background:#f3e2cf;border-radius:12px;padding:8px 10px;margin:10px 4px 0;white-space:pre-wrap;}
.bigtime{font-size:2.6rem;font-weight:bold;font-variant-numeric:tabular-nums;margin:8px 0;}
input[type=number]{width:4.2em;padding:8px;font-size:1.1rem;text-align:center;border-radius:8px;border:1px solid #c9a37e;}
button.act{padding:10px 18px;font-size:1rem;border-radius:10px;border:none;background:#8a5a3b;color:#fff;cursor:pointer;margin:3px;}
button.sub{background:#d9b98f;color:#4a2c14;}
.presets button{padding:6px 10px;margin:2px;border-radius:999px;border:1px solid #c9a37e;background:#fff;cursor:pointer;}
#calcDisplay{background:#2b1a12;color:#ffe9c9;font-size:1.8rem;text-align:right;padding:12px;border-radius:10px;min-height:1.4em;word-break:break-all;font-variant-numeric:tabular-nums;}
.calcgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:8px;}
.calcgrid button{padding:14px 0;font-size:1.15rem;border-radius:10px;border:1px solid #c9a37e;background:#fff;cursor:pointer;}
.calcgrid button.op{background:#f3e2cf;}
.calcgrid button.eq{background:#8a5a3b;color:#fff;}
footer{opacity:.6;font-size:.85rem;padding:0 0 18px;}
</style>
</head>
<body>

<h1>🕰️ {{ UI.app_title }}</h1>
<p class="lead">{{ UI.lead }}</p>

<div class="watch">
  <div class="tabs">
    <button data-tab="clock" class="active">時計</button>
    <button data-tab="timer">タイマー</button>
    <button data-tab="stopwatch">ストップウォッチ</button>
    <button data-tab="calc">電卓</button>
  </div>

  <div class="panel active" id="panel-clock">
    <svg id="analog" width="180" height="180" viewBox="0 0 100 100" aria-label="アナログ時計">
      <circle cx="50" cy="50" r="48" fill="#fff" stroke="#8a5a3b" stroke-width="2"/>
      <g id="ticks"></g>
      <line id="hourHand" x1="50" y1="50" x2="50" y2="28" stroke="#2b1a12" stroke-width="4" stroke-linecap="round"/>
      <line id="minHand" x1="50" y1="50" x2="50" y2="18" stroke="#5a3620" stroke-width="2.6" stroke-linecap="round"/>
      <line id="secHand" x1="50" y1="56" x2="50" y2="14" stroke="#c0392b" stroke-width="1.2" stroke-linecap="round"/>
      <circle cx="50" cy="50" r="3" fill="#8a5a3b"/>
    </svg>
    <div id="digital">--:--:--</div>
    <p id="dateLine"></p>
    <p id="cocoaLine"></p>
  </div>

  <div class="panel" id="panel-timer">
    <div class="bigtime" id="timerDisplay">05:00</div>
    <p>
      <input type="number" id="timerMin" min="0" max="999" value="5"> 分
      <input type="number" id="timerSec" min="0" max="59" value="0"> 秒
    </p>
    <p class="presets">
      <button data-preset="180">3分</button>
      <button data-preset="300">5分</button>
      <button data-preset="600">10分</button>
      <button data-preset="1500">25分</button>
    </p>
    <p>
      <button class="act" id="timerStart">スタート</button>
      <button class="act sub" id="timerReset">リセット</button>
    </p>
    <p id="timerLine"></p>
    <p>タイマー完了：<span id="timerCount">0</span> 回</p>
  </div>

  <div class="panel" id="panel-stopwatch">
    <div class="bigtime" id="swDisplay">00:00.0</div>
    <p>
      <button class="act" id="swStart">スタート</button>
      <button class="act sub" id="swReset">リセット</button>
    </p>
    <p id="swLine"></p>
  </div>

  <div class="panel" id="panel-calc">
    <div id="calcDisplay">0</div>
    <div class="calcgrid" id="calcGrid">
      <button data-k="C" class="op">C</button>
      <button data-k="±" class="op">±</button>
      <button data-k="%" class="op">%</button>
      <button data-k="÷" class="op">÷</button>
      <button data-k="7">7</button><button data-k="8">8</button><button data-k="9">9</button>
      <button data-k="×" class="op">×</button>
      <button data-k="4">4</button><button data-k="5">5</button><button data-k="6">6</button>
      <button data-k="−" class="op">−</button>
      <button data-k="1">1</button><button data-k="2">2</button><button data-k="3">3</button>
      <button data-k="+" class="op">+</button>
      <button data-k="0">0</button><button data-k="00">00</button><button data-k=".">.</button>
      <button data-k="=" class="eq">=</button>
    </div>
  </div>
</div>

<footer>cocotime — cocoa series</footer>

<script>
const greetings={{ greetings|tojson }};
const TIMER_DONE_LINE={{ timer_done|tojson }};
const STOPWATCH_LINE={{ sw_line|tojson }};

// ---- tabs ----
document.querySelectorAll(".tabs button").forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll(".tabs button").forEach(x=>x.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(x=>x.classList.remove("active"));
    b.classList.add("active");
    document.getElementById("panel-"+b.dataset.tab).classList.add("active");
  };
});

// ---- clock ----
(function(){
  const ticks=document.getElementById("ticks");
  let s="";
  for(let i=0;i<12;i++){
    const a=i*Math.PI/6, x1=50+42*Math.sin(a), y1=50-42*Math.cos(a), x2=50+46*Math.sin(a), y2=50-46*Math.cos(a);
    s+='<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="#8a5a3b" stroke-width="'+(i%3===0?2:1)+'"/>';
  }
  ticks.innerHTML=s;
})();
function greetingFor(h){
  if(h>=5&&h<11)return greetings[0];
  if(h>=11&&h<17)return greetings[1];
  if(h>=17&&h<22)return greetings[2];
  if(h>=22)return greetings[3];
  return greetings[4];
}
function setHand(id,deg){document.getElementById(id).setAttribute("transform","rotate("+deg+" 50 50)");}
function tickClock(){
  const now=new Date();
  const h=now.getHours(),m=now.getMinutes(),sec=now.getSeconds();
  document.getElementById("digital").textContent=
    String(h).padStart(2,"0")+":"+String(m).padStart(2,"0")+":"+String(sec).padStart(2,"0");
  const days=["日","月","火","水","木","金","土"];
  document.getElementById("dateLine").textContent=
    now.getFullYear()+"年"+(now.getMonth()+1)+"月"+now.getDate()+"日（"+days[now.getDay()]+"）";
  document.getElementById("cocoaLine").textContent="ココア："+greetingFor(h);
  setHand("hourHand",(h%12)*30+m*0.5);
  setHand("minHand",m*6+sec*0.1);
  setHand("secHand",sec*6);
}
tickClock();setInterval(tickClock,1000);

// ---- timer ----
let timerLeft=300,timerId=null,timerDoneCount=0;
function fmtTimer(s){return String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0");}
function showTimer(){document.getElementById("timerDisplay").textContent=fmtTimer(timerLeft);}
function readTimerInput(){
  let m=parseInt(document.getElementById("timerMin").value||"0",10);
  let s=parseInt(document.getElementById("timerSec").value||"0",10);
  if(isNaN(m)||m<0)m=0; if(isNaN(s)||s<0)s=0; if(s>59)s=59; if(m>999)m=999;
  return m*60+s;
}
function beep(){
  try{
    const ctx=new (window.AudioContext||window.webkitAudioContext)();
    [0,0.25,0.5].forEach(off=>{
      const o=ctx.createOscillator(),g=ctx.createGain();
      o.connect(g);g.connect(ctx.destination);o.frequency.value=880;
      g.gain.setValueAtTime(0.15,ctx.currentTime+off);
      o.start(ctx.currentTime+off);o.stop(ctx.currentTime+off+0.18);
    });
  }catch(e){}
}
function stopTimer(){if(timerId){clearInterval(timerId);timerId=null;}document.getElementById("timerStart").textContent="スタート";}
document.getElementById("timerStart").onclick=()=>{
  if(timerId){stopTimer();return;}
  if(timerLeft<=0)timerLeft=readTimerInput();
  if(timerLeft<=0)return;
  document.getElementById("timerLine").textContent="";
  document.getElementById("timerStart").textContent="一時停止";
  timerId=setInterval(()=>{
    timerLeft--;showTimer();
    if(timerLeft<=0){
      stopTimer();beep();timerDoneCount++;
      document.getElementById("timerCount").textContent=timerDoneCount;
      document.getElementById("timerLine").textContent="ココア："+TIMER_DONE_LINE;
    }
  },1000);
};
document.getElementById("timerReset").onclick=()=>{stopTimer();timerLeft=readTimerInput();showTimer();document.getElementById("timerLine").textContent="";};
document.querySelectorAll("[data-preset]").forEach(b=>{
  b.onclick=()=>{stopTimer();timerLeft=parseInt(b.dataset.preset,10);
    document.getElementById("timerMin").value=Math.floor(timerLeft/60);
    document.getElementById("timerSec").value=timerLeft%60;showTimer();};
});
showTimer();

// ---- stopwatch ----
let swStartAt=null,swElapsed=0,swId=null;
function fmtSw(ms){
  const t=Math.floor(ms/100),s=Math.floor(t/10),ds=t%10;
  return String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0")+"."+ds;
}
function showSw(){document.getElementById("swDisplay").textContent=fmtSw(swElapsed+(swStartAt?Date.now()-swStartAt:0));}
document.getElementById("swStart").onclick=()=>{
  if(swId){clearInterval(swId);swId=null;swElapsed+=Date.now()-swStartAt;swStartAt=null;
    document.getElementById("swStart").textContent="スタート";
    document.getElementById("swLine").textContent="ココア："+STOPWATCH_LINE;showSw();return;}
  swStartAt=Date.now();document.getElementById("swLine").textContent="";
  document.getElementById("swStart").textContent="ストップ";
  swId=setInterval(showSw,100);
};
document.getElementById("swReset").onclick=()=>{
  if(swId){clearInterval(swId);swId=null;}swStartAt=null;swElapsed=0;
  document.getElementById("swStart").textContent="スタート";showSw();
};
showSw();

// ---- calculator (state machine, no eval) ----
let calcCur="0",calcPrev=null,calcOp=null,calcFresh=true;
function calcShow(){document.getElementById("calcDisplay").textContent=calcCur;}
function calcApply(a,b,op){
  if(op==="+")return a+b; if(op==="−")return a-b;
  if(op==="×")return a*b; if(op==="÷")return b===0?NaN:a/b;
  return b;
}
function calcNum(v){const n=parseFloat(v);return isNaN(n)?0:n;}
function calcFormat(v){
  if(typeof v!=="number"||isNaN(v)||!isFinite(v))return "エラー";
  return String(Math.round(v*1e10)/1e10);
}
function calcKey(k){
  if(k==="C"){calcCur="0";calcPrev=null;calcOp=null;calcFresh=true;}
  else if(k==="±"){if(calcCur!=="0")calcCur=calcCur.startsWith("-")?calcCur.slice(1):"-"+calcCur;}
  else if(k==="%"){calcCur=calcFormat(calcNum(calcCur)/100);calcFresh=true;}
  else if(k==="="){
    if(calcOp!==null&&calcPrev!==null){
      calcCur=calcFormat(calcApply(calcPrev,calcNum(calcCur),calcOp));
      calcPrev=null;calcOp=null;calcFresh=true;
    }
  }
  else if(["+","−","×","÷"].indexOf(k)>=0){
    if(calcOp!==null&&calcPrev!==null&&!calcFresh){
      calcCur=calcFormat(calcApply(calcPrev,calcNum(calcCur),calcOp));
    }
    calcPrev=calcNum(calcCur);calcOp=k;calcFresh=true;
  }
  else{ // digits and dot
    if(calcFresh||calcCur==="0"||calcCur==="エラー"){
      if(k==="."){calcCur="0.";}else if(k==="00"){calcCur="0";}else{calcCur=k;}
      calcFresh=false;
    }else{
      if(k==="."&&calcCur.indexOf(".")>=0)return;
      if(calcCur.replace("-","").replace(".","").length>=12)return;
      calcCur+=k;
    }
  }
  calcShow();
}
document.querySelectorAll("#calcGrid button").forEach(b=>{b.onclick=()=>calcKey(b.dataset.k);});
calcShow();
</script>

</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(
        HTML,
        UI=UI_TEXT,
        greetings=GREETINGS,
        timer_done=TIMER_DONE_LINE,
        sw_line=STOPWATCH_LINE,
    )


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "app": "cocotime"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
