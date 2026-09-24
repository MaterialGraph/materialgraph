import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { useMaterialExplorer } from './useMaterialExplorer';
import { SourcePicker } from './SourcePicker';
import { MaterialIdentity } from './MaterialIdentity';
import { CandidateList } from './CandidateList';
import { ObjectiveInvestigation } from './objective/ObjectiveInvestigation';
import { PropertyComparisonWorkspace, WorkflowComparison } from './comparison/PropertyComparison';
import type { ComparisonLaunchContext } from './comparison/launch';
import './style.css';

export function App() {
  const explorer = useMaterialExplorer();
  const { selected } = explorer;
  const [launch, setLaunch] = useState<ComparisonLaunchContext | null>(null);
  const comparisonHeading = useRef<HTMLHeadingElement>(null);
  const discoveryHeading = useRef<HTMLDivElement>(null);
  const objectiveHeading = useRef<HTMLDivElement>(null);
  useEffect(() => { if (launch) comparisonHeading.current?.focus(); }, [launch]);
  function returnToWorkflow() {
    const target = launch?.originWorkflow === 'objective' ? objectiveHeading : discoveryHeading;
    setLaunch(null);
    requestAnimationFrame(() => target.current?.focus());
  }
  return <div className="shell">
    <header><div className="brand">Material<span>Graph</span><small>Research workspace / 01</small></div><div className="headerNote">MATERIAL EXPLORER <span>·</span> READ ONLY</div></header>
    <div className="intro"><p className="eyebrow">EXPLORE THE MATERIAL LANDSCAPE</p><h1>Start with a material.<br/><em>Follow the evidence.</em></h1><p>Select a source identity, inspect available properties, then explore explainable candidates. Scores describe encoded rules, not experimental validation.</p></div>
    <main className="layout" hidden={launch !== null}>
      <SourcePicker {...explorer}/>
      <section className="workspace">
        {!selected && <div className="panel welcome"><span className="eyebrow">A PLACE TO BEGIN</span><h2>Select a material to open its workspace.</h2><p>Each source identity stays distinct, even when two materials share a formula.</p></div>}
        <MaterialIdentity {...explorer}/>
        <div ref={discoveryHeading} tabIndex={-1}><CandidateList key={explorer.detail?.id ?? 0} {...explorer} onCompare={setLaunch}/></div>
        <div ref={objectiveHeading} tabIndex={-1}>{explorer.detail && <ObjectiveInvestigation key={explorer.detail.id} materialId={explorer.detail.id} onCompare={setLaunch}/>}</div>
        <PropertyComparisonWorkspace/>
      </section>
    </main>
    {launch && <main className="workflowComparison" aria-label="Workflow property comparison"><h1 ref={comparisonHeading} tabIndex={-1}>Comparison from {launch.originWorkflow === 'objective' ? 'Objective Investigation' : 'Candidate Discovery'}</h1>
      <button type="button" onClick={returnToWorkflow}>Return to {launch.originWorkflow === 'objective' ? 'Objective Investigation' : 'Candidate Discovery'}</button>
      <WorkflowComparison launch={launch}/>
    </main>}
    <footer>MaterialGraph · Evidence and limits stay visible.</footer>
  </div>;
}

const appRoot = document.getElementById('root');
if (appRoot) createRoot(appRoot).render(<React.StrictMode><App/></React.StrictMode>);
