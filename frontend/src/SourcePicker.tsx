import { DatasetSearch } from './DatasetSearch';
// Browsing, paging and local ID lookup all go through the unified search.
type Props = { selected: number; select: (id: number) => void };
export function SourcePicker({ selected, select }: Props) {
  return <aside className="panel picker"><div className="sectionTitle"><span>01 / SELECT</span><h2>Materials</h2></div>
    <DatasetSearch selected={selected} select={select}/>
  </aside>;
}
