import React, {useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const tabs = [
  ['safety','Site Safety'], ['cracks','Crack Analysis'], ['plan','Planning & Cost'], ['valuation','Property Valuation']
];
function App(){
  const [tab,setTab]=useState('safety'), [description,setDescription]=useState('');
  const [image,setImage]=useState(null), [project,setProject]=useState({area_sqft:1000,floors:1,location:'India',quality:'standard',budget_inr:'',description:''});
  const [busy,setBusy]=useState(false), [result,setResult]=useState(null), [error,setError]=useState('');
  async function submit(e){
    e.preventDefault(); setBusy(true);setError('');setResult(null);
    try{
      let response;
      if(tab==='safety'||tab==='cracks'){
        const fd=new FormData(); fd.append('description',description); if(image)fd.append('image',image);
        response=await fetch(`${API}/api/analyze/${tab}`,{method:'POST',body:fd});
      } else {
        const p={...project,area_sqft:Number(project.area_sqft),floors:Number(project.floors),budget_inr:project.budget_inr?Number(project.budget_inr):null};
        response=await fetch(`${API}/api/${tab==='plan'?'plan':'valuation'}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({description,project:p})});
      }
      const data=await response.json(); if(!response.ok)throw new Error(data.detail||'Request failed'); setResult(data);
    }catch(err){setError(err.message||'Unable to reach the API. Check that the backend is running.');}
    finally{setBusy(false);}
  }
  return <main>
    <header><div className="brand"><span className="mark">B</span><div><strong>BuildWise AI</strong><small>Construction intelligence workspace</small></div></div><span className="pill">AI ASSISTED · PRELIMINARY</span></header>
    <section className="hero"><p className="eyebrow">BUILD SMARTER. BUILD SAFER.</p><h1>One workspace for<br/><em>construction decisions.</em></h1><p className="intro">Review site risks, inspect visible cracks, estimate materials and costs, and explore property valuation assumptions.</p></section>
    <nav>{tabs.map(([id,label])=><button key={id} className={tab===id?'active':''} onClick={()=>{setTab(id);setResult(null);setError('')}}>{label}</button>)}</nav>
    <div className="layout"><form className="panel" onSubmit={submit}>
      <div className="panelhead"><div><p className="eyebrow">INPUT WORKSPACE</p><h2>{tabs.find(t=>t[0]===tab)?.[1]}</h2></div><span className="step">01 / INPUT</span></div>
      <label>Project or site description<textarea value={description} onChange={e=>setDescription(e.target.value)} placeholder="Describe what you see, the building type, site conditions, or project requirements…" rows="4"/></label>
      {(tab==='safety'||tab==='cracks')?<label className="upload"> <span className="uploadicon">＋</span><span><b>{image?image.name:'Add a site image'}</b><small>JPG, PNG, WEBP or GIF · up to 10 MB</small></span><input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={e=>setImage(e.target.files?.[0]||null)}/></label>:
      <div className="fields"><label>Built-up area (sq ft)<input type="number" min="1" required value={project.area_sqft} onChange={e=>setProject({...project,area_sqft:e.target.value})}/></label><label>Number of floors<input type="number" min="1" max="100" value={project.floors} onChange={e=>setProject({...project,floors:e.target.value})}/></label><label>Location<input value={project.location} onChange={e=>setProject({...project,location:e.target.value})}/></label><label>Construction quality<select value={project.quality} onChange={e=>setProject({...project,quality:e.target.value})}><option value="economy">Economy</option><option value="standard">Standard</option><option value="premium">Premium</option></select></label><label className="wide">Budget (INR, optional)<input type="number" min="0" value={project.budget_inr} onChange={e=>setProject({...project,budget_inr:e.target.value})} placeholder="e.g. 2500000"/></label></div>}
      <button className="submit" disabled={busy}>{busy?'Analyzing…':'Run AI analysis  ↗'}</button><p className="fine">AI outputs are preliminary estimates, not a substitute for site inspection or licensed professional advice.</p>
    </form><section className="panel output"><div className="panelhead"><div><p className="eyebrow">ANALYSIS REPORT</p><h2>Results & recommendations</h2></div><span className="step">02 / OUTPUT</span></div>
      {!result&&!error&&!busy&&<div className="empty"><div className="emptyicon">⌁</div><h3>Your report will appear here</h3><p>Choose a module, provide details, and run an analysis to receive structured findings and next steps.</p><div className="emptyline"><span>01</span> Submit project information</div><div className="emptyline"><span>02</span> Review AI-generated findings</div><div className="emptyline"><span>03</span> Verify with qualified professionals</div></div>}
      {busy&&<div className="loading"><div className="spinner"/><p>Reviewing inputs and preparing your report…</p></div>}
      {error&&<div className="error"><b>Could not complete analysis</b><p>{error}</p><small>Check backend status and API-key configuration.</small></div>}
      {result&&<><div className="resulttop"><span className="successdot"/> Analysis complete <button className="copy" onClick={()=>navigator.clipboard?.writeText(JSON.stringify(result,null,2))}>Copy JSON</button></div><pre>{JSON.stringify(result,null,2)}</pre><p className="fine">Review assumptions and limitations before acting on any recommendation.</p></>}
    </section></div>
    <footer><span>BUILDWISE AI</span><span>Designed for informed decisions, not automated certification.</span></footer>
  </main>
}
createRoot(document.getElementById('root')).render(<App/>);
