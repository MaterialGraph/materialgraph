import React from 'react';
import { createRoot } from 'react-dom/client';
import { useMaterialExplorer } from './useMaterialExplorer';
import { SourcePicker } from './SourcePicker';
import { MaterialIdentity } from './MaterialIdentity';
import { CandidateList } from './CandidateList';
import { ObjectiveInvestigation } from './objective/ObjectiveInvestigation';
import './style.css';

function App() {
  const explorer = useMaterialExplorer();
  const { selected } = explorer;
  return <div className="shell">
    <header><div className="brand">Material<span>Graph</span><small>Research workspace / 01</small></div><div className="headerNote">MATERIAL EXPLORER <span>·</span> READ ONLY</div></header>
    <div className="intro"><p className="eyebrow">EXPLORE THE MATERIAL LANDSCAPE</p><h1>Start with a material.<br/><em>Follow the evidence.</em></h1><p>Select a source identity, inspect available properties, then explore explainable candidates. Scores describe encoded rules, not experimental validation.</p></div>
    <main className="layout">
      <SourcePicker {...explorer}/>
      <section className="workspace">
        {!selected && <div className="panel welcome"><span className="eyebrow">A PLACE TO BEGIN</span><h2>Select a material to open its workspace.</h2><p>Each source identity stays distinct, even when two materials share a formula.</p></div>}
        <MaterialIdentity {...explorer}/>
        <CandidateList {...explorer}/>
        {explorer.detail && <ObjectiveInvestigation key={explorer.detail.id} materialId={explorer.detail.id}/>}
      </section>
    </main><footer>MaterialGraph · Evidence and limits stay visible.</footer>
  </div>;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
