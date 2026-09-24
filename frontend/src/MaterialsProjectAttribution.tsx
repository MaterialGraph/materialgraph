export function recordSourceLabel(source: string): string {
  return source === 'materials_project' ? 'Materials Project' : source;
}

export function MaterialsProjectAttribution() {
  return <p className="materialsAttribution">
    Material record data: Materials Project (CC BY 4.0). MaterialGraph calculates the discovery, objective, chain, and comparison analysis shown here.{' '}
    <a href="https://materialsproject.org/" target="_blank" rel="noopener noreferrer">Materials Project</a>{' · '}
    <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">License</a>{' · '}
    <a href="https://materialsproject.org/about/cite" target="_blank" rel="noopener noreferrer">How to cite</a>
  </p>;
}
