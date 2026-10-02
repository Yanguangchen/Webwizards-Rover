import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';

const outDir=path.dirname(fileURLToPath(import.meta.url));
const workspaceDir=outDir;
const buildDir=path.join(outDir,'build');
const SKILL_DIR=process.env.PRESENTATION_SKILL_DIR;
if (!SKILL_DIR) throw new Error('Set PRESENTATION_SKILL_DIR to the installed presentations skill directory.');
const RUNTIME_PYTHON=process.env.RUNTIME_PYTHON || 'python3';
const {resolvePresentationFont,finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')).href);
const family=resolvePresentationFont({fontFamily:'Aptos'});
const C={ink:'#132D2A',green:'#26715E',muted:'#536763',light:'#D9EBE3',white:'#FFFFFF',soft:'#F2F6F3',dark:'#132D2A',accent:'#A9DDC1'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
const slides=[];
const text=(s,value,x,y,w,h,size=28,color=C.ink,bold=false,align='left')=>{
  const t=s.shapes.add({geometry:'textbox',name:value.slice(0,56).replaceAll('\n',' '),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  t.text=value;
  t.text.style={typeface:family,fontSize:size,color,bold,alignment:align,verticalAlignment:'top',autoFit:'none',wrap:'none',insets:{top:0,right:0,bottom:0,left:0}};
  return t;
};
const sourceNote='Source: user-provided prototype photos IMG_8361–IMG_8364, 21 September 2026, and the documented rover setup and diagnostic sessions on 19–20 September 2026. Product name Rover is a working name. Photos use AI-assisted background replacement and exposure cleanup. Original hardware photographs remain the authoritative engineering record.';
function slide(title,{dark=false,notes=''}={}){
  const s=p.slides.add();s.background.fill=dark?C.dark:C.white;slides.push(s);
  if(title)text(s,title,64,52,1152,125,52,dark?C.white:C.ink,true);
  text(s,String(slides.length).padStart(2,'0'),1190,664,34,26,17,dark?'#A6BDB6':'#84928D',false,'right');
  s.speakerNotes.textFrame.setText(`${notes}\n\n${sourceNote}`);
  return s;
}
async function photo(s,file,x,y,w,h,alt){
  s.images.add({blob:new Uint8Array(await fs.readFile(path.join(outDir,'photos',file))),contentType:'image/png',position:{left:x,top:y,width:w,height:h},fit:'contain',alt});
}

// 1. Minimal product cover with the cleaned front view.
{
 const s=slide('',{notes:'Opening pitch: Rover is a Raspberry Pi camera prototype mounted on a wheeled chassis, with StampNote as the web viewing layer. Present remote driving as a product direction until the motor-control integration is demonstrated.'});
 await photo(s,'rover-front-white.png',514,88,748,544,'Retouched front three-quarter photograph of the actual Rover prototype');
 text(s,'ROVER',64,184,460,136,108,C.ink,true);
 text(s,'A robot platform\nfor remote vision',68,330,510,124,42,C.green);
 text(s,'Prototype pitch\nSeptember 2026',68,568,420,74,23,C.muted);
}

// 2. Problem framing without unsupported market numbers.
{
 const s=slide('Remote checks need\na useful viewpoint',{dark:true,notes:'Problem hypothesis for discovery interviews. The deck does not claim measured demand or quantified time savings. Ask potential users which remote checks they cannot complete with existing equipment.'});
 text(s,'A live feed helps only when it shows the thing you need to check.',66,215,1110,56,30,C.light);
 text(s,'Fixed viewpoints',66,348,500,58,38,C.white,true);
 text(s,'A room camera can leave the relevant\nobject or corner outside its view.',66,425,530,96,29,C.light);
 text(s,'Someone has to go and look',664,348,552,58,38,C.white,true);
 text(s,'A closer inspection can still depend on\na person being available on site.',664,425,552,96,29,C.light);
 text(s,'Product opportunity: a camera platform that can change its viewpoint.',66,602,1120,38,25,C.accent);
}

// 3. Actual hardware rather than a speculative production render.
{
 const s=slide('The Rover prototype',{notes:'The photos show a black wheeled chassis, USB webcam, Raspberry Pi board and exposed connections. Raspberry Pi 4 identification comes from the setup history. No speed, battery life, range, payload, weather resistance or motor-control performance has been measured in the supplied material.'});
 await photo(s,'rover-side-white.png',568,190,685,457,'Retouched side three-quarter photograph of the actual Rover prototype');
 text(s,'USB webcam',66,212,450,46,34,C.green,true);
 text(s,'A live view from the robot’s position.',66,266,486,74,26,C.muted);
 text(s,'Raspberry Pi 4',66,352,470,46,34,C.green,true);
 text(s,'Runs the operating system and\nStampNote in Chromium.',66,406,484,78,26,C.muted);
 text(s,'Wheeled chassis',66,514,470,46,34,C.green,true);
 text(s,'A physical base for the next stage\nof remote movement development.',66,568,484,78,26,C.muted);
}

// 4. Explicit boundary between evidence and the remaining hardware work.
{
 const s=slide('A working camera foundation',{notes:'720p capture was verified in Chromium with the C270 during earlier setup sessions: videoWidth 1280, videoHeight 720, paused false and a live camera track. The boot service and direct /robotic-control launch passed a reboot test. The Google sign-in and live camera page status were verified. The later replacement webcam was not detected by Linux at the last check, so this is historical prototype evidence rather than a claim that the new camera is already validated. Automatic startStream() is now present in deployed page code, but capture depends on a detected compatible camera.'});
 text(s,'720p',66,211,492,126,102,C.green,true);
 text(s,'Live capture demonstrated',70,352,500,45,32,C.ink,true);
 text(s,'1280 × 720 video in Chromium\nwith the earlier C270 webcam.',70,414,500,88,28,C.muted);
 text(s,'Automatic browser startup',664,220,550,48,33,C.ink,true);
 text(s,'The Pi opens robotic-control after boot.',664,277,548,77,27,C.muted);
 text(s,'Signed-in camera sharing',664,389,550,48,33,C.ink,true);
 text(s,'StampNote links the camera session\nto its Live tunnel viewing flow.',664,446,548,85,27,C.muted);
 text(s,'Next validation: replacement webcam detection and automatic capture after boot.',66,607,1145,48,24,C.green);
}

// 5. Viewing workflow, editable explanatory text and a unique detail photograph.
{
 const s=slide('StampNote is the viewing layer',{notes:'Operational flow based on the implemented Linux boot launcher, site camera code and Firebase sign-in. The page is https://stampnote-omega.vercel.app/robotic-control. Boot opening is verified. Page-level automatic camera activation is implemented in the deployed JavaScript as of 20 September 2026 and still needs end-to-end validation with the replacement webcam. The Live tunnel transport and access behaviour should be validated in the pilot; no recording retention or compliance capability is claimed.'});
 text(s,'The robot hosts the camera.\nStampNote provides the browser session.',66,187,656,101,31,C.muted);
 await photo(s,'rover-detail-white.png',40,305,700,356,'Retouched close side view of the prototype, showing the board, camera mount and chassis');
 const steps=[['01','Power on','The Pi starts Chromium.'],['02','Open robotic-control','The dedicated camera page loads.'],['03','Start the camera','The site requests the USB webcam.'],['04','Share the live view','A signed-in session enables Live tunnel.']];
 steps.forEach((v,i)=>{const y=186+i*115;text(s,v[0],782,y,65,47,31,C.green,true);text(s,v[1],858,y,365,43,29,C.ink,true);text(s,v[2],858,y+47,358,58,22,C.muted);});
}

// 6. Hypotheses for discovery rather than claimed customer traction.
{
 const s=slide('First pilot: indoor visual checks',{notes:'Proposed target market and use-case hypotheses, not current customers. The suggested first pilot is a small indoor workspace with the owner’s permission, a known Wi-Fi network and a defined visual inspection task. Home/pet viewing is an adjacent concept. Avoid care, safety-critical monitoring, outdoor autonomy or security guarantees until separately validated.'});
 text(s,'Suggested starting point: small workshops and private workspaces.',66,195,1145,58,29,C.green);
 text(s,'Check a workspace remotely',66,311,540,58,35,C.ink,true);
 text(s,'See a bench, doorway or storage area\nwithout arranging a video call.',66,383,540,88,28,C.muted);
 text(s,'Investigate a changed view',666,311,550,58,35,C.ink,true);
 text(s,'Test whether a new camera angle\nhelps answer a specific question.',666,383,550,88,28,C.muted);
 text(s,'Pilot boundaries',66,551,1110,44,31,C.ink,true);
 text(s,'Known indoor space. Consenting users. Supervised movement once validated.',66,605,1110,40,25,C.muted);
}

// 7. Native editable comparison table.
{
 const s=slide('Where Rover could fit',{notes:'Conceptual comparison of workflows, not a competitor feature audit. A fixed camera can pan or tilt but remains at its installed location. A phone video call relies on a person to position it. Rover’s mobility benefit is a proposed outcome contingent on safe motor-control integration. No claim of better price, latency, image quality, reliability or autonomy is made.'});
 text(s,'A potential middle ground between an installed camera and an on-site person.',66,188,1144,64,27,C.muted);
 const values=[
 ['Workflow','Fixed camera','Phone video call','Rover concept'],
 ['Viewpoint','Installed location','Person positions it','Wheeled platform'],
 ['On-site help','Setup and adjustment','Needed during the call','Goal: less routine help'],
 ['User access','Camera app or browser','Calling app','StampNote browser'],
 ['Best initial role','Continuous fixed view','Guided human inspection','Remote visual checks'],
 ];
 const t=s.tables.add({rows:5,columns:4,left:64,top:280,width:1152,height:304,columnWidths:[246,272,290,344],values});
 t.styleOptions={headerRow:true,bandedRows:false};
 t.borders.assign({fill:'#DFE7E2',width:1,style:'solid'});
 for(let r=0;r<5;r++){
  t.rows[r].height=r===0?58:66;
  for(let c=0;c<4;c++){
   const cell=t.getCell(r,c);cell.fill=r===0?C.dark:(c===3?'#E8F2EC':(r%2===0?'#F8FAF8':C.white));
   cell.text.style={typeface:family,fontSize:23,color:r===0?C.white:C.ink,bold:r===0||c===0,autoFit:'none',verticalAlignment:'middle',insets:{left:14,right:12,top:9,bottom:9}};
  }
 }
 text(s,'Remote driving remains a development milestone.',66,622,1120,40,24,C.green);
}

// 8. Proposed model, with no invented revenue or price anchors.
{
 const s=slide('A route to first revenue',{dark:true,notes:'Business-model hypotheses for an early product pitch. No revenue, customers, funding, unit economics, price or market-size data were supplied. The recommended sequence is discovery and pilot evidence before selecting a commercial offer. Define pricing only after a bill of materials, assembly time, setup effort and ongoing support cost are known.'});
 text(s,'Proposed model',66,188,1100,41,26,C.accent);
 text(s,'Pilot engagement',66,283,510,53,38,C.white,true);
 text(s,'Work with a small number of owners\nto define and test a useful visual check.',66,357,535,96,29,C.light);
 text(s,'Hardware and setup',662,283,554,53,38,C.white,true);
 text(s,'Offer a configured robot once reliability\nand support needs are understood.',662,357,554,96,29,C.light);
 text(s,'Optional recurring service',66,539,1130,46,32,C.white,true);
 text(s,'Support and fleet management, if pilots demonstrate a continuing need.',66,597,1130,53,27,C.light);
}

// 9. Roadmap as flat, sequential editorial rows.
{
 const s=slide('The next build priorities',{notes:'Proposed sequence with no promised dates. First close the hardware and recovery gaps observed in this conversation. Then demonstrate safe motor control with an emergency stop and a defined operator workflow before a supervised pilot. Autonomous navigation, obstacle avoidance, battery endurance and outdoor use are not demonstrated capabilities.'});
 const rows=[
 ['01','Reliable capture','Validate the new webcam, boot capture and recovery after Wi-Fi loss.'],
 ['02','Safe remote movement','Integrate motor control, a stop action and supervised driving tests.'],
 ['03','A repeatable pilot','Measure setup effort, useful checks completed and support needs.'],
 ];
 rows.forEach((r,i)=>{const y=211+i*139;text(s,r[0],66,y,98,70,52,C.green,true);text(s,r[1],190,y+2,1018,49,35,C.ink,true);text(s,r[2],190,y+62,1018,58,27,C.muted);});
 text(s,'Success means a repeatable viewing task, not simply a working demo.',66,650,1120,34,23,C.green);
}

// 10. Clear early-stage ask with the final unique product photograph.
{
 const s=slide('Pilot partners for the next build',{notes:'Proposed call to action for partner or investor discussions, not an assertion that a pilot programme already has participants. Seek access to a small indoor test site and feedback on a concrete viewing task. Investment terms and a funding amount remain unspecified because the user has not supplied a budget or fundraising plan.'});
 await photo(s,'rover-rear-white.png',566,197,690,460,'Retouched rear photograph of the actual Rover prototype');
 text(s,'A real prototype.\nA clear next experiment.',66,211,530,116,39,C.green,true);
 text(s,'We are looking for a small indoor site\nand an owner willing to test a\nuseful remote viewing task.',66,358,510,134,29,C.muted);
 text(s,'Next milestone',66,535,500,42,30,C.ink,true);
 text(s,'A reliable session from power-on\nto a usable live view.',66,587,510,75,27,C.muted);
}

await fs.mkdir(buildDir,{recursive:true});await fs.mkdir(outDir,{recursive:true});
const candidatePath=path.join(buildDir,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
await fs.writeFile(path.join(buildDir,'presentation.json'),JSON.stringify(p.toProto()));
for(let i=0;i<slides.length;i++){
 const img=await p.export({slide:slides[i],format:'png',scale:1.5});
 await fs.writeFile(path.join(buildDir,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await img.arrayBuffer()));
 const layout=await slides[i].export({format:'layout'});
 await fs.writeFile(path.join(buildDir,`slide-${i+1}.layout.json`),await layout.text());
}
const finalPath=path.join(outDir,'Rover-Pitch-Deck.pptx');
const result=await finalizePresentation({workspaceDir,candidatePath,finalPath,pythonExecutable:RUNTIME_PYTHON,
 integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','7'],
 requiredNativeTableOwnerSlides:[7],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'design',families:[family]},verifyArtifactToolImport:true,
 receiptPath:path.join(buildDir,'validation.json')});
console.log(JSON.stringify({finalPath,result},null,2));
