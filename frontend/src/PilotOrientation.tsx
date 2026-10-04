import { useEffect, useRef, useState } from 'react';

const dismissalKey = 'materialgraph.pilot.orientation.v1';

export function PilotOrientation() {
  const dialog = useRef<HTMLDialogElement>(null);
  const helpButton = useRef<HTMLButtonElement>(null);
  const [open, setOpen] = useState(() => {
    try {
      return localStorage.getItem(dismissalKey) !== 'dismissed';
    } catch {
      return true;
    }
  });

  useEffect(() => {
    const element = dialog.current;
    if (!element) return;
    if (open && !element.open) element.showModal();
    if (!open && element.open) element.close();
  }, [open]);

  function dismiss() {
    try {
      localStorage.setItem(dismissalKey, 'dismissed');
    } catch {
      // Guidance remains usable when browser storage is unavailable.
    }
    dialog.current?.close();
    setOpen(false);
    helpButton.current?.focus();
  }

  return <div className="pilotOrientation">
    <div className="pilotHelp">
      <button
        ref={helpButton}
        type="button"
        aria-haspopup="dialog"
        aria-controls="pilot-getting-started"
        onClick={() => setOpen(true)}
      >Help / Getting started</button>
    </div>
    <dialog
      ref={dialog}
      id="pilot-getting-started"
      className="pilotGuide"
      aria-labelledby="pilot-guide-heading"
      onClick={event => {
        if (event.target !== event.currentTarget) return;
        const bounds = event.currentTarget.getBoundingClientRect();
        if (
          event.clientX < bounds.left || event.clientX > bounds.right ||
          event.clientY < bounds.top || event.clientY > bounds.bottom
        ) dismiss();
      }}
      onCancel={event => {
        event.preventDefault();
        dismiss();
      }}
    >
      <h2 id="pilot-guide-heading">Getting started with MaterialGraph</h2>
      <ol>
        <li>Select a source material to inspect its identity and reported properties.</li>
        <li>Use Candidate Discovery or Objective Investigation to explore alternatives. Review the explanations and limits alongside the results.</li>
        <li>Select two or three candidates and open Property Comparison. A copied comparison link requires pilot access and restores context on this instance; it fetches current values.</li>
      </ol>
      <p>This prototype searches a selected battery-relevant cohort. Rule scores and composition relationships are research starting points, not experimental validation or synthesis instructions.</p>
      <p>The separate comparison form accepts MaterialGraph IDs from this instance, not Materials Project identifiers.</p>
      <button type="button" autoFocus onClick={dismiss}>Continue to workspace</button>
    </dialog>
  </div>;
}
