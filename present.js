const $=s=>document.querySelector(s);
const scenes=[...document.querySelectorAll('.scene')];
let lang='en',step=0,playing=false,utterance=null,narrationSerial=0;
const scripts={
 en:[
  `This slide says two point five percent. From the front, it looks obvious. But the person in the last row does not see the source file. They see what survives distance, projection, focus, light, and perspective. BACKROW tests that physical path.`,
  `Here, the source says two point five percent, while the audience-position capture recovers twenty-five percent. That is not just a style problem. The meaning changed.`,
  `Now I will show the product. BACKROW loads the deck once, then analyzes a capture from the audience position without being told the page number. It finds the slide, rectifies the perspective, maps evidence back to the source, and localizes the exact information that failed.`,
  `The technical roles are separated. AudienceNet is our custom learned model. Tesseract LSTM is third-party pretrained OCR. ORB, RANSAC, and homography are classical computer vision. A verified numeric contradiction always overrides model confidence.`,
  `Next, I repair the failing source region and rescan from the same audience position. The risk disappears. BACKROW is not a presentation score. It is a loop: find the information that failed, fix it, then prove the failure is gone.`,
  `There is one boundary I will not hide. A camera is not a human eye. The engineering pipeline is verified, but human readability needs real readers. BACKROW includes a blinded, timed, locked study so those results can be measured without leaking the source truth.`,
  `A presenter sees the source file. The audience sees the room. BACKROW tests the room. Please choose a slide.`
 ],
 id:[
  `Slide ini menulis dua koma lima persen. Dari depan, angkanya terlihat jelas. Tetapi orang di baris paling belakang tidak melihat file sumber. Mereka melihat apa yang bertahan setelah jarak, proyeksi, fokus, cahaya, dan perspektif. BACKROW menguji jalur fisik itu.`,
  `Di sini, sumber menulis dua koma lima persen, sedangkan tangkapan dari posisi penonton terbaca dua puluh lima persen. Ini bukan sekadar masalah tampilan. Maknanya berubah.`,
  `Sekarang saya tunjukkan produknya. BACKROW memuat deck satu kali, lalu menganalisis tangkapan dari posisi penonton tanpa diberi nomor halaman. Sistem mencari slide, meluruskan perspektif, memetakan bukti kembali ke sumber, dan menunjukkan informasi tepat yang gagal.`,
  `Peran teknisnya dipisahkan. AudienceNet adalah model learned kustom kami. Tesseract LSTM adalah OCR pretrained pihak ketiga. ORB, RANSAC, dan homography adalah computer vision klasik. Kontradiksi angka yang terverifikasi selalu mengalahkan confidence model.`,
  `Berikutnya, saya memperbaiki region sumber yang bermasalah lalu scan ulang dari posisi penonton yang sama. Risikonya hilang. BACKROW bukan skor presentasi. Ini loop: temukan informasi yang gagal, perbaiki, lalu buktikan kegagalannya sudah hilang.`,
  `Ada satu batas yang tidak saya sembunyikan. Kamera bukan mata manusia. Pipeline engineering sudah terverifikasi, tetapi keterbacaan manusia membutuhkan pembaca nyata. BACKROW sudah menyediakan studi blind, timed, dan locked agar hasil itu dapat diukur tanpa membocorkan jawaban sumber.`,
  `Presenter melihat file sumber. Penonton melihat ruangan. BACKROW menguji ruangan. Silakan pilih satu slide.`
 ]
};

const copy={
 en:{introTitle:'The audience sees the room, not your source file.',introBody:'BACKROW tests what survives the path from slide → projector → room → audience position.',evTitle:'The information changed.',evNote:'Not a style score. The critical value itself was recovered differently.',liveTitle:'BACKROW finds the slide and localizes the failure.',archTitle:'One learned component. Several deterministic safeguards.',repairTitle:'The result is a repair loop, not a score.',valEyebrow:'SCIENTIFIC BOUNDARY',valTitle:'Camera evidence is not human eyesight.',valLead:'BACKROW separates what is already verified from what still requires real readers in real rooms.',valAFlag:'VERIFIED ENGINEERING',valATitle:'Physical capture pipeline',valABody:'slide retrieval · rectification · exact OCR evidence · numeric guard · fix/rescan',valBFlag:'LOCKED HUMAN STUDY',valBTitle:'Naïve readers, hidden truth',valBBody:'frozen order · timed exposure · immutable responses · confidence intervals · kill gates',valCFlag:'CLAIM DISCIPLINE',valCTitle:'No fake human-accuracy number',valCBody:'procedural model metrics stay labeled as engineering evidence until physical validation is complete',closeTitle:'Presenter sees the source. Audience sees the room.',closeBody:'BACKROW tests the room.',start:'START PRESENTATION'},
 id:{introTitle:'Penonton melihat ruangan, bukan file sumbermu.',introBody:'BACKROW menguji apa yang bertahan dari slide → proyektor → ruangan → posisi penonton.',evTitle:'Informasinya berubah.',evNote:'Bukan skor gaya. Nilai kritisnya sendiri dipulihkan secara berbeda.',liveTitle:'BACKROW mengenali slide dan melokalisasi kegagalan.',archTitle:'Satu komponen learned. Beberapa safeguard deterministik.',repairTitle:'Hasil akhirnya adalah loop perbaikan, bukan skor.',valEyebrow:'BATAS ILMIAH',valTitle:'Bukti kamera bukan penglihatan manusia.',valLead:'BACKROW memisahkan hal yang sudah terverifikasi dari hal yang masih membutuhkan pembaca nyata di ruangan nyata.',valAFlag:'ENGINEERING TERVERIFIKASI',valATitle:'Pipeline tangkapan fisik',valABody:'retrieval slide · rectification · bukti OCR eksak · numeric guard · fix/rescan',valBFlag:'STUDI MANUSIA TERKUNCI',valBTitle:'Pembaca naïf, jawaban disembunyikan',valBBody:'urutan dibekukan · paparan bertimer · respons immutable · confidence interval · kill gate',valCFlag:'DISIPLIN KLAIM',valCTitle:'Tidak ada angka akurasi manusia palsu',valCBody:'metrik model prosedural tetap dilabeli sebagai bukti engineering sampai validasi fisik selesai',closeTitle:'Presenter melihat file sumber. Penonton melihat ruangan.',closeBody:'BACKROW menguji ruangan.',start:'MULAI PRESENTASI'}
};
function voiceScore(v){
 const name=(v.name||'').toLowerCase(),loc=(v.lang||'').toLowerCase();
 const target=lang==='id'?'id':'en';
 let s=loc.startsWith(target)?50:0;
 if(/natural|neural|online/.test(name))s+=40;
 if(lang==='id'&&/ardi|gadis|indones/.test(name))s+=30;
 if(lang==='en'&&/aria|jenny|guy|ava|andrew|emma|brian|sonia|google us english/.test(name))s+=30;
 if(/desktop|legacy|compact/.test(name))s-=10;
 return s;
}
function chooseVoice(){const voices=speechSynthesis.getVoices();return [...voices].sort((a,b)=>voiceScore(b)-voiceScore(a))[0]||null}
function updateCopy(){
 const c=copy[lang];
 for(const [id,key] of [['#introTitle','introTitle'],['#introBody','introBody'],['#evTitle','evTitle'],['#evNote','evNote'],['#liveTitle','liveTitle'],['#archTitle','archTitle'],['#repairTitle','repairTitle'],['#valEyebrow','valEyebrow'],['#valTitle','valTitle'],['#valLead','valLead'],['#valAFlag','valAFlag'],['#valATitle','valATitle'],['#valABody','valABody'],['#valBFlag','valBFlag'],['#valBTitle','valBTitle'],['#valBBody','valBBody'],['#valCFlag','valCFlag'],['#valCTitle','valCTitle'],['#valCBody','valCBody'],['#closeTitle','closeTitle'],['#closeBody','closeBody']]){const el=$(id);if(el)el.textContent=c[key]}
 $('#playBtn').textContent=playing?'PAUSE':c.start;$('#enBtn').classList.toggle('active',lang==='en');$('#idBtn').classList.toggle('active',lang==='id');const frame=$('#productFrame');if(frame&&frame.tagName==='IFRAME')frame.src='/?lang='+lang
}
function showStep(n){step=Math.max(0,Math.min(scenes.length-1,n));scenes.forEach((s,i)=>s.classList.toggle('active',i===step));$('#stepCount').textContent=String(step+1).padStart(2,'0')+' / '+String(scenes.length).padStart(2,'0');if(step===2)prepareLiveRisk();if(step===4)prepareLiveFix()}
async function frameReady(){const f=$('#productFrame');if(!f||!f.contentWindow)return;for(let i=0;i<70;i++){if(typeof f.contentWindow.loadJudgeDemo==='function')return;await new Promise(r=>setTimeout(r,100))}}
async function prepareLiveRisk(){const f=$('#productFrame');await frameReady();try{await f.contentWindow.loadJudgeDemo(true);setTimeout(()=>{const el=f.contentDocument.querySelector('#results');el&&el.scrollIntoView({behavior:'smooth',block:'start'})},500)}catch(e){console.warn('Live risk scene unavailable',e)}}
async function prepareLiveFix(){const f=$('#productFrame');await frameReady();try{await f.contentWindow.loadJudgeDemo(true);await new Promise(r=>setTimeout(r,1200));await f.contentWindow.runFixRescanDemo();setTimeout(()=>{const el=f.contentDocument.querySelector('#beforeAfter');el&&el.scrollIntoView({behavior:'smooth',block:'center'})},500)}catch(e){console.warn('Live fix scene unavailable',e)}}
function stopNarration(){narrationSerial++;speechSynthesis.cancel()}
function finishNarration(serial){if(serial!==narrationSerial||!playing)return;if(step<scenes.length-1){showStep(step+1);setTimeout(()=>{if(serial===narrationSerial&&playing)speakCurrent()},500)}else{playing=false;$('#playBtn').textContent=copy[lang].start}}
function speakLocal(text,serial){utterance=new SpeechSynthesisUtterance(text);const v=chooseVoice();if(v)utterance.voice=v;utterance.rate=lang==='id'?0.98:0.96;utterance.pitch=1;utterance.volume=1;$('#voiceStatus').textContent=v?('LOCAL VOICE · '+v.name.toUpperCase()):'LOCAL VOICE · SYSTEM DEFAULT';utterance.onend=()=>finishNarration(serial);utterance.onerror=()=>{$('#voiceStatus').textContent='VOICE FALLBACK';finishNarration(serial)};speechSynthesis.speak(utterance)}
function speakCurrent(){stopNarration();const serial=narrationSerial,text=scripts[lang][step]||'';$('#caption').textContent=text;$('#caption').classList.add('show');speakLocal(text,serial)}
function togglePlay(){playing=!playing;if(playing){$('#playBtn').textContent='PAUSE';speakCurrent()}else{stopNarration();$('#playBtn').textContent=copy[lang].start;$('#caption').classList.remove('show')}}
$('#playBtn').onclick=togglePlay;$('#prevBtn').onclick=()=>{playing=false;stopNarration();showStep(step-1);$('#caption').classList.remove('show')};$('#nextBtn').onclick=()=>{playing=false;stopNarration();showStep(step+1);$('#caption').classList.remove('show')};$('#enBtn').onclick=()=>{lang='en';playing=false;stopNarration();updateCopy()};$('#idBtn').onclick=()=>{lang='id';playing=false;stopNarration();updateCopy()};
window.addEventListener('keydown',e=>{if(e.code==='Space'){e.preventDefault();togglePlay()}if(e.key==='ArrowRight')$('#nextBtn').click();if(e.key==='ArrowLeft')$('#prevBtn').click()});
speechSynthesis.onvoiceschanged=()=>{if(!playing)$('#voiceStatus').textContent='VOICE READY'};
showStep(0);updateCopy();
