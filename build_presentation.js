const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE'; // 13.333 x 7.5
pptx.author = 'BACKROW';
pptx.subject = 'YCWC 2026 Senior — BACKROW';
pptx.title = 'BACKROW — Can the last row still read it?';
pptx.company = 'YCWC 2026';
pptx.lang = 'en-US';
pptx.theme = {
  headFontFace: 'Inter', bodyFontFace: 'Inter', lang: 'en-US'
};
pptx.defineSlideMaster({
  title:'MASTER',
  background:{color:'F2F2ED'},
  objects:[
    {line:{x:0,y:0.48,w:13.333,h:0,line:{color:'0B0D0C',width:0.75}}},
    {text:{text:'BACKROW / YCWC 2026',options:{x:0.42,y:0.13,w:2.5,h:0.2,fontFace:'Inter',fontSize:8,bold:true,color:'0B0D0C',charSpacing:1.2,margin:0}}},
    {text:{text:'AUDIENCE-VIEW PRESENTATION QA',options:{x:10.55,y:0.13,w:2.35,h:0.2,fontFace:'Inter',fontSize:7,color:'68716B',charSpacing:1.1,align:'right',margin:0}}},
    {line:{x:0,y:7.15,w:13.333,h:0,line:{color:'0B0D0C',width:0.5}}},
    {text:{text:'Camera evidence is not a human-eyesight claim.',options:{x:8.2,y:7.22,w:4.7,h:0.15,fontFace:'Inter',fontSize:6.5,color:'68716B',align:'right',margin:0}}}
  ],
  slideNumber:{x:0.42,y:7.2,w:0.35,h:0.18,fontFace:'Inter',fontSize:7,color:'68716B',margin:0}
});
const C={bg:'F2F2ED',ink:'0B0D0C',green:'006B4F',red:'E23A2E',amber:'A97500',muted:'68716B',line:'ADB3AE',soft:'E5E6E1',dark:'101311',white:'FFFFFF'};
const R=__dirname;
function img(name){return path.join(R,name)}
function addTitle(slide,kicker,title,sub=''){
  slide.addText(kicker.toUpperCase(),{x:0.62,y:0.76,w:4.8,h:0.18,fontFace:'Inter',fontSize:8,bold:true,color:C.green,charSpacing:1.5,margin:0});
  slide.addText(title,{x:0.62,y:1.02,w:11.8,h:0.9,fontFace:'Inter',fontSize:30,bold:true,color:C.ink,breakLine:false,margin:0,fit:'shrink'});
  if(sub)slide.addText(sub,{x:0.64,y:1.94,w:11.5,h:0.47,fontFace:'Inter',fontSize:12,color:'454B47',margin:0,breakLine:false,fit:'shrink'});
}
function tag(slide,text,x,y,w,color=C.ink,fill=C.bg){slide.addText(text.toUpperCase(),{x,y,w,h:0.28,fontFace:'Inter',fontSize:7.5,bold:true,color,fill:{color:fill},line:{color,width:0.7},margin:0.05,align:'center',valign:'mid',charSpacing:0.8});}
function mono(slide,text,x,y,w,h,size=10,color=C.ink,opts={}){slide.addText(text,{x,y,w,h,fontFace:'Noto Sans Mono',fontSize:size,color,margin:0,breakLine:false,fit:'shrink',...opts});}
function label(slide,text,x,y,w){slide.addText(text.toUpperCase(),{x,y,w,h:0.2,fontFace:'Inter',fontSize:6.8,bold:true,color:C.muted,charSpacing:1.1,margin:0});}
function addImg(slide,file,x,y,w,h){slide.addImage({path:img(file),x,y,w,h});}
function rule(slide,x,y,w,color=C.line,width=.6){slide.addShape(pptx.ShapeType.line,{x,y,w,h:0,line:{color,width}})}
function bulletRows(slide,items,x,y,w){let yy=y;for(const it of items){slide.addText(it,{x:x+0.32,y:yy,w:w-0.32,h:0.36,fontFace:'Inter',fontSize:12,color:C.ink,margin:0,breakLine:false,fit:'shrink'});slide.addShape(pptx.ShapeType.rect,{x,y:yy+0.08,w:0.12,h:0.12,fill:{color:C.green},line:{color:C.green}});yy+=0.5}}

// 1
{
 let s=pptx.addSlide('MASTER');
 s.addText('01 / PHYSICAL FAILURE',{x:0.65,y:0.78,w:2.6,h:0.18,fontFace:'Noto Sans Mono',fontSize:7.5,color:C.muted,charSpacing:1.2,margin:0});
 s.addText('Can the last row\nstill read it?',{x:0.62,y:1.18,w:5.35,h:1.62,fontFace:'Inter',fontSize:38,bold:true,color:C.ink,margin:0,breakLine:false,fit:'shrink'});
 s.addText('The audience never sees the source file. They see what survives distance, projection, focus, lighting, and perspective.',{x:0.64,y:3.05,w:4.9,h:1.05,fontFace:'Inter',fontSize:15,color:'454B47',margin:0,breakLine:false,fit:'shrink'});
 tag(s,'SOURCE',0.65,4.55,1.0,C.ink,C.bg); tag(s,'BACK ROW',2.92,4.55,1.25,C.ink,C.bg);
 addImg(s,'assets/hero_source_detail.png',0.65,4.9,2.15,1.2);addImg(s,'assets/hero_audience_detail.png',2.92,4.9,2.15,1.2);
 s.addText('2.5%',{x:0.65,y:6.18,w:1.3,h:0.38,fontFace:'Inter',fontSize:20,bold:true,color:C.ink,margin:0});
 s.addText('→',{x:2.2,y:6.18,w:0.42,h:0.38,fontFace:'Inter',fontSize:20,bold:true,color:C.red,margin:0,align:'center'});
 s.addText('25%',{x:2.92,y:6.18,w:1.2,h:0.38,fontFace:'Inter',fontSize:20,bold:true,color:C.red,margin:0});
 s.addText('CRITICAL INFORMATION CHANGED',{x:4.12,y:6.27,w:1.35,h:0.22,fontFace:'Inter',fontSize:6.5,bold:true,color:C.red,charSpacing:0.8,margin:0});
 s.addShape(pptx.ShapeType.rect,{x:6.0,y:0.5,w:7.33,h:6.65,fill:{color:'DDE0DB'},line:{color:'DDE0DB'}});
 addImg(s,'assets/slide_2_view_risk.png',6.35,1.05,6.62,3.72);
 label(s,'AUDIENCE CAPTURE',6.36,4.92,2.0);
 s.addText('BACKROW',{x:6.35,y:5.28,w:2.15,h:0.48,fontFace:'Inter',fontSize:25,bold:true,color:C.ink,margin:0});
 s.addText('tests what the room delivered.',{x:8.4,y:5.34,w:4.2,h:0.4,fontFace:'Inter',fontSize:17,bold:false,color:C.ink,margin:0});
 s.addText('AI-integrated website · exact evidence · fix → rescan',{x:6.37,y:6.0,w:5.9,h:0.25,fontFace:'Noto Sans Mono',fontSize:8,color:C.green,margin:0});
}
// 2
{
 let s=pptx.addSlide('MASTER');addTitle(s,'02 / problem','The failure happens after the slide file.','A source-side checker can miss a problem introduced by the actual display path.');
 const y=2.75; const xs=[0.8,3.3,5.8,8.3,10.8]; const names=['SOURCE FILE','PROJECTOR','ROOM','AUDIENCE POSITION','RECEIVED INFO'];
 const sub=['perfect on laptop','focus / scale','light / washout','distance / angle','what survives'];
 xs.forEach((x,i)=>{s.addShape(pptx.ShapeType.rect,{x,y,w:1.72,h:1.15,fill:{color:i==4?'101311':'FFFFFF'},line:{color:C.ink,width:1}});s.addText(names[i],{x:x+0.1,y:y+0.18,w:1.52,h:0.25,fontFace:'Inter',fontSize:8,bold:true,color:i==4?C.white:C.ink,align:'center',margin:0});s.addText(sub[i],{x:x+0.12,y:y+0.55,w:1.48,h:0.26,fontFace:'Inter',fontSize:7.5,color:i==4?'D4D6D2':C.muted,align:'center',margin:0}); if(i<4)s.addText('→',{x:x+1.82,y:y+0.35,w:0.6,h:0.4,fontFace:'Inter',fontSize:18,color:C.green,align:'center',margin:0});});
 s.addText('Existing source checks answer: “Is the file designed well?”',{x:0.82,y:4.45,w:5.7,h:0.5,fontFace:'Inter',fontSize:15,bold:true,color:C.ink,margin:0});
 s.addText('BACKROW asks: “What exact information did this audience position actually receive?”',{x:0.82,y:5.18,w:10.8,h:0.64,fontFace:'Inter',fontSize:22,bold:true,color:C.green,margin:0,fit:'shrink'});
 mono(s,'SOURCE ≠ PHYSICAL DELIVERY',0.82,6.28,3.2,0.25,9,C.muted);
}
// 3
{
 let s=pptx.addSlide('MASTER');addTitle(s,'03 / product','One deck. One audience camera. Whole-deck evidence.');
 const steps=[['1','LOAD DECK','PDF / slide once'],['2','WATCH','camera stays at seat'],['3','MATCH','identify current page'],['4','RECTIFY','map back to source'],['5','PROVE','recover / lose exact info'],['6','RESCAN','verify the repair']];
 let x=0.62;for(let i=0;i<steps.length;i++){let [n,a,b]=steps[i];s.addText(n,{x,y:2.55,w:0.28,h:0.25,fontFace:'Noto Sans Mono',fontSize:7,bold:true,color:C.green,margin:0});s.addText(a,{x:x+0.32,y:2.48,w:1.45,h:0.25,fontFace:'Inter',fontSize:9,bold:true,color:C.ink,margin:0});s.addText(b,{x:x+0.32,y:2.82,w:1.45,h:0.4,fontFace:'Inter',fontSize:8,color:C.muted,margin:0,fit:'shrink'});if(i<steps.length-1)rule(s,x+1.9,2.72,0.28,C.green,1);x+=2.08}
 addImg(s,'preview/BACKROW_V5_RESULTS.png',0.65,3.55,7.7,3.12);
 s.addShape(pptx.ShapeType.rect,{x:8.72,y:3.55,w:3.92,h:3.12,fill:{color:C.dark},line:{color:C.dark}});
 s.addText('OUTPUT IS EVIDENCE,\nNOT A MAGIC SCORE.',{x:9.02,y:3.9,w:3.25,h:0.85,fontFace:'Inter',fontSize:19,bold:true,color:C.white,margin:0,fit:'shrink'});
 bulletRows(s,['source-localized region','exact audience decode','why it failed','repair + same-seat rescan'],9.0,5.05,3.1);
}
// 4
{
 let s=pptx.addSlide('MASTER');addTitle(s,'04 / live demo','The judge can change the input.');
 label(s,'SOURCE',0.72,2.42,1.0); label(s,'AUDIENCE VIEW',6.9,2.42,1.5);
 addImg(s,'assets/slide_2_source.png',0.72,2.75,5.55,3.12);addImg(s,'assets/slide_2_view_risk.png',6.9,2.75,5.55,3.12);
 s.addShape(pptx.ShapeType.rect,{x:0.72,y:6.1,w:11.73,h:0.62,fill:{color:C.dark},line:{color:C.dark}});
 s.addShape(pptx.ShapeType.rect,{x:0.72,y:6.1,w:1.2,h:0.62,fill:{color:C.red},line:{color:C.red}});
 s.addText('AT RISK',{x:0.82,y:6.3,w:1.0,h:0.18,fontFace:'Inter',fontSize:8,bold:true,color:C.white,margin:0,align:'center'});
 s.addText('2.5% → 25%',{x:2.18,y:6.22,w:2.0,h:0.28,fontFace:'Inter',fontSize:16,bold:true,color:C.white,margin:0});
 s.addText('exact critical value changed',{x:4.24,y:6.28,w:2.4,h:0.18,fontFace:'Inter',fontSize:8,color:'C9CCC9',margin:0});
 s.addText('NO PAGE INDEX GIVEN',{x:9.6,y:6.3,w:2.45,h:0.18,fontFace:'Noto Sans Mono',fontSize:7.2,color:'C9CCC9',align:'right',margin:0});
}
// 5
{
 let s=pptx.addSlide('MASTER');addTitle(s,'05 / architecture','What is AI — and what is not.','The project separates custom learning, pretrained AI, classical vision, and deterministic safety logic.');
 const rows=[
 ['CUSTOM AI','AudienceNet 2.0','48 → 24 MLP · 16 paired source/camera/room features',C.green],
 ['PRETRAINED AI','Tesseract 5 LSTM','exact text + numeric recovery · third-party', '355D92'],
 ['CLASSICAL CV','ORB + RANSAC + homography','page retrieval · geometric verification · rectification','5E615F'],
 ['DETERMINISTIC','numeric guard + evidence fusion','hard contradictions outrank learned uncertainty',C.red]
 ];
 let y=2.65;rows.forEach(r=>{s.addText(r[0],{x:0.72,y:y+0.08,w:1.35,h:0.2,fontFace:'Noto Sans Mono',fontSize:7.3,bold:true,color:r[3],margin:0});s.addText(r[1],{x:2.18,y,w:3.0,h:0.36,fontFace:'Inter',fontSize:17,bold:true,color:C.ink,margin:0});s.addText(r[2],{x:5.55,y:y+0.02,w:6.6,h:0.32,fontFace:'Inter',fontSize:10.5,color:'454B47',margin:0,fit:'shrink'});rule(s,0.72,y+0.58,11.72,'C6C9C5',0.6);y+=0.86});
 s.addText('The AI is core, but it is not allowed to erase direct evidence.',{x:0.72,y:6.35,w:10.8,h:0.35,fontFace:'Inter',fontSize:15,bold:true,color:C.green,margin:0});
}
//6
{
 let s=pptx.addSlide('MASTER');addTitle(s,'06 / fail-safe','Hard evidence outranks model confidence.');
 const levels=[['1','VERIFIED EXACT LOSS','source 2.5%  ≠  audience 25%',C.red],['2','STRONG OCR / REGION EVIDENCE','content recovered or missing',C.ink],['3','AUDIENCENET','learned survivability evidence',C.green],['4','WEAK HEURISTICS','blur / contrast / glare support',C.muted]];
 let y=2.45;levels.forEach((r,i)=>{s.addShape(pptx.ShapeType.rect,{x:0.8,y,w:0.55,h:0.55,fill:{color:r[3]},line:{color:r[3]}});s.addText(r[0],{x:0.8,y:y+0.14,w:0.55,h:0.18,fontFace:'Inter',fontSize:9,bold:true,color:i==3?C.white:C.white,align:'center',margin:0});s.addText(r[1],{x:1.65,y:y+0.03,w:3.25,h:0.24,fontFace:'Inter',fontSize:11,bold:true,color:C.ink,margin:0});mono(s,r[2],5.15,y+0.02,6.4,0.3,9,r[3]);if(i<3)s.addText('↓',{x:1.0,y:y+0.61,w:0.2,h:0.28,fontFace:'Inter',fontSize:12,color:C.line,align:'center',margin:0});y+=0.92});
 s.addShape(pptx.ShapeType.rect,{x:0.8,y:6.1,w:11.55,h:0.55,fill:{color:'E7E8E4'},line:{color:'C1C5C1'}});
 s.addText('If slide identity / geometry / evidence is insufficient → NOT ENOUGH EVIDENCE.',{x:1.0,y:6.27,w:10.9,h:0.22,fontFace:'Inter',fontSize:11,bold:true,color:C.ink,margin:0});
}
//7
{
 let s=pptx.addSlide('MASTER');addTitle(s,'07 / prior art','The claim is narrow on purpose.','Readability is not new. Projector-camera assessment is not new. The workflow integration is the contribution.');
 const entries=[
 ['2011','LECTURE-HALL LEGIBILITY','Cai · Kim · Green','geometry + text + lighting + observer acuity'],
 ['2017','PROJECTED-CONTENT QUALITY','Le · Marshall · Doan · Mai · Liu','original + camera capture + rectification + learned quality'],
 ['2026','SOURCE-FILE READABILITY','SlideSpeak','font size + contrast + density + language complexity'],
 ['BACKROW','AUDIENCE-PATH QA','this project','auto match + exact loss + repair/rescan + blinded field test']
 ];
 let y=2.62;entries.forEach((e,i)=>{s.addText(e[0],{x:0.75,y,w:1.1,h:0.28,fontFace:'Noto Sans Mono',fontSize:8,bold:true,color:i===3?C.green:C.muted,margin:0});s.addText(e[1],{x:1.9,y:y-0.02,w:3.2,h:0.3,fontFace:'Inter',fontSize:11,bold:true,color:C.ink,margin:0});s.addText(e[2],{x:5.2,y,w:2.6,h:0.25,fontFace:'Inter',fontSize:9.5,color:C.muted,margin:0});s.addText(e[3],{x:7.75,y:y-0.01,w:4.7,h:0.35,fontFace:'Inter',fontSize:9.5,color:C.ink,margin:0,fit:'shrink'});rule(s,0.75,y+0.48,11.7,'C5C8C4',0.5);y+=0.82});
 s.addText('DEFENSIBLE NOVELTY: N3–N4 APPLIED WORKFLOW',{x:0.75,y:6.2,w:5.2,h:0.24,fontFace:'Noto Sans Mono',fontSize:8.5,bold:true,color:C.green,margin:0});
 s.addText('No “world first” claim.',{x:9.75,y:6.18,w:2.7,h:0.3,fontFace:'Inter',fontSize:12,bold:true,color:C.red,align:'right',margin:0});
 s.addText('Sources: Cai et al. 2011 · Le et al. CRV 2017 · SlideSpeak current checker',{x:0.75,y:6.68,w:9.2,h:0.16,fontFace:'Inter',fontSize:6.5,color:C.muted,margin:0});
}
//8
{
 let s=pptx.addSlide('MASTER');addTitle(s,'08 / engineering evidence','The custom model beats simple baselines — on its stated procedural task.','These numbers are not human-readability accuracy.');
 const vals=[['signal rules',0.4056,C.muted],['geometry',0.4789,C.amber],['AudienceNet 2.0',0.9422,C.green]];
 const bx=1.1,by=3.0,bw=8.4;
 vals.forEach((r,i)=>{let y=by+i*0.88;s.addText(r[0],{x:bx,y:y+0.07,w:1.8,h:0.22,fontFace:'Inter',fontSize:10,bold:i==2,color:C.ink,margin:0});s.addShape(pptx.ShapeType.rect,{x:bx+2.0,y:y,w:bw*r[1],h:0.38,fill:{color:r[2]},line:{color:r[2]}});s.addText(r[1].toFixed(4),{x:bx+2.12+bw*r[1],y:y+0.05,w:0.82,h:0.22,fontFace:'Noto Sans Mono',fontSize:8,bold:true,color:C.ink,margin:0});});
 s.addText('1,440 samples · 48 template families · group-disjoint family split',{x:1.1,y:5.8,w:6.8,h:0.25,fontFace:'Noto Sans Mono',fontSize:8.5,color:C.muted,margin:0});
 s.addText('6/6',{x:9.75,y:2.86,w:1.1,h:0.55,fontFace:'Inter',fontSize:26,bold:true,color:C.ink,margin:0});s.addText('generated alignment cases',{x:9.75,y:3.46,w:2.0,h:0.25,fontFace:'Inter',fontSize:8,color:C.muted,margin:0});
 s.addText('3/3',{x:9.75,y:4.08,w:1.1,h:0.55,fontFace:'Inter',fontSize:26,bold:true,color:C.ink,margin:0});s.addText('bundled deck matches',{x:9.75,y:4.68,w:2.0,h:0.25,fontFace:'Inter',fontSize:8,color:C.muted,margin:0});
 s.addText('2 → 0',{x:9.75,y:5.3,w:1.4,h:0.55,fontFace:'Inter',fontSize:26,bold:true,color:C.green,margin:0});s.addText('risk regions after repair',{x:9.75,y:5.9,w:2.2,h:0.25,fontFace:'Inter',fontSize:8,color:C.muted,margin:0});
}
//9
{
 let s=pptx.addSlide('MASTER');addTitle(s,'09 / physical validation','The camera-human gap is measured, not hand-waved.');
 // timeline
 const tx=[0.8,3.15,5.5,7.85,10.2];const ts=[['1','RANDOMIZE'],['2','SHOW 6 s'],['3','HIDE'],['4','READER TYPES'],['5','LOCK RESPONSE']];
 ts.forEach((r,i)=>{s.addShape(pptx.ShapeType.ellipse,{x:tx[i],y:2.55,w:0.48,h:0.48,fill:{color:i==1?C.red:C.dark},line:{color:i==1?C.red:C.dark}});s.addText(r[0],{x:tx[i],y:2.68,w:0.48,h:0.14,fontFace:'Inter',fontSize:7,bold:true,color:C.white,align:'center',margin:0});s.addText(r[1],{x:tx[i]-0.15,y:3.15,w:1.2,h:0.22,fontFace:'Noto Sans Mono',fontSize:6.8,bold:true,color:C.ink,align:'center',margin:0});if(i<4)rule(s,tx[i]+0.53,2.79,1.75,C.line,1)});
 addImg(s,'preview/BACKROW_FIELD_STUDY_ADMIN.png',0.8,3.75,5.55,2.5);addImg(s,'preview/BACKROW_FIELD_STUDY_READER.png',6.82,3.75,5.55,2.5);
 label(s,'PRESENTER / TRUTH CONTROL',0.8,6.4,2.4);label(s,'BLINDED READER',6.82,6.4,1.7);
 s.addText('Source truth never appears in the participant payload before submission.',{x:7.95,y:6.39,w:4.38,h:0.24,fontFace:'Inter',fontSize:8.8,bold:true,color:C.green,margin:0,fit:'shrink'});
}
//10
{
 let s=pptx.addSlide('MASTER');addTitle(s,'10 / action','Find it. Fix it. Prove it.');
 label(s,'BEFORE',0.72,2.45,1.0); label(s,'AFTER',6.95,2.45,1.0);
 addImg(s,'assets/slide_2_view_risk.png',0.72,2.76,5.55,3.12);addImg(s,'assets/slide_2_view_fixed.png',6.95,2.76,5.55,3.12);
 s.addText('2 AT RISK',{x:0.72,y:6.1,w:1.75,h:0.35,fontFace:'Inter',fontSize:17,bold:true,color:C.red,margin:0});
 s.addText('→',{x:5.97,y:6.08,w:0.55,h:0.35,fontFace:'Inter',fontSize:18,bold:true,color:C.green,align:'center',margin:0});
 s.addText('0 AT RISK',{x:6.95,y:6.1,w:1.85,h:0.35,fontFace:'Inter',fontSize:17,bold:true,color:C.green,margin:0});
 s.addText('The product is not a score. It is a verified repair loop.',{x:8.75,y:6.09,w:3.74,h:0.42,fontFace:'Inter',fontSize:12,bold:true,color:C.ink,align:'right',margin:0,fit:'shrink'});
 s.addText('CHOOSE A SLIDE.',{x:0.72,y:6.62,w:3.0,h:0.28,fontFace:'Noto Sans Mono',fontSize:10,bold:true,color:C.ink,charSpacing:1.2,margin:0});
}

pptx.writeFile({fileName:path.join(R,'BACKROW_YCWC_2026_PRESENTATION.pptx')});
