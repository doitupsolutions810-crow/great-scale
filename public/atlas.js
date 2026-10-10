/* Great Scale atlas runtime — attach after main canvas script */
(function(){
  const VIEW_PRESETS = {Watch:{az:35,el:25},Observer:{az:0,el:80},Forward:{az:90,el:15},Adjacent:{az:-40,el:20},Down:{az:0,el:-55}};
  let camAz=35, camEl=25, scrubMode=false;
  function heat(h){return h*(1-h);}
  function phaseXYZ(phase,S){
    const th=2*Math.PI*phase,r=1+0.12*Math.sin(th*2);
    return [r*Math.cos(th),S*3.5,r*Math.sin(th)];
  }
  function project3(x,y,z,W,H){
    const az=camAz*Math.PI/180,el=camEl*Math.PI/180;
    let x1=x*Math.cos(az)-z*Math.sin(az);
    let z1=x*Math.sin(az)+z*Math.cos(az);
    let y1=y*Math.cos(el)-z1*Math.sin(el);
    let z2=y*Math.sin(el)+z1*Math.cos(el);
    const f=320/(2.5+z2);
    return [W*0.42+x1*f, H*0.48-y1*f];
  }
  // inject controls
  const foot=document.querySelector('footer');
  if(foot && !document.getElementById('camAz')){
    const box=document.createElement('div');
    box.className='ctrl';
    box.innerHTML='<label>phase</label><input type="range" id="phaseScrub" min="0" max="500" value="0"/><span id="phaseVal">auto</span> <label>az</label><input type="range" id="camAz" min="-180" max="180" value="35"/><label>el</label><input type="range" id="camEl" min="-89" max="89" value="25"/>';
    foot.insertBefore(box, foot.querySelector('#status')||null);
  }
  const canvas=document.getElementById('cv');
  let dragging=false,lx=0,ly=0;
  if(canvas){
    canvas.addEventListener('mousedown',e=>{dragging=true;lx=e.clientX;ly=e.clientY;});
    window.addEventListener('mouseup',()=>dragging=false);
    window.addEventListener('mousemove',e=>{
      if(!dragging)return;
      camAz+=(e.clientX-lx)*0.4;
      camEl=Math.max(-89,Math.min(89,camEl-(e.clientY-ly)*0.3));
      lx=e.clientX;ly=e.clientY;
      const a=document.getElementById('camAz'),b=document.getElementById('camEl');
      if(a)a.value=Math.round(camAz); if(b)b.value=Math.round(camEl);
    });
  }
  document.getElementById('camAz')?.addEventListener('input',e=>{camAz=+e.target.value;});
  document.getElementById('camEl')?.addEventListener('input',e=>{camEl=+e.target.value;});
  document.getElementById('phaseScrub')?.addEventListener('input',e=>{
    scrubMode=true;
    if(typeof gen!=='undefined'){gen=+e.target.value;}
    const pv=document.getElementById('phaseVal'); if(pv)pv.textContent='t='+e.target.value;
  });
  document.getElementById('views')?.addEventListener('click',e=>{
    const t=e.target.closest('.tab'); if(!t)return;
    const pr=VIEW_PRESETS[t.dataset.view];
    if(pr){camAz=pr.az;camEl=pr.el;
      const a=document.getElementById('camAz'),b=document.getElementById('camEl');
      if(a)a.value=camAz; if(b)b.value=camEl;
    }
  });
  // overlay marker trail using 3d projection each frame
  const _draw = window.draw;
  // expose for agents
  window.GreatScaleAtlas = {camAz:()=>camAz, camEl:()=>camEl, phaseXYZ, project3, VIEW_PRESETS, version:'0.4.0'};
  console.log('Great Scale atlas 0.4.0 ready — drag canvas to orbit phase-time');
})();
