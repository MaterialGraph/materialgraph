# MG-IA-IMP-002 — Document or expose screening decision-ordering semantics

- Classification: API explainability improvement
- Priority: P2
- Confidence: high

Candidate screening intentionally ranks primarily by reconstructed pre-risk score, then known-risk status, displayed score, and material ID. Tests confirm that a known-risk candidate may precede an otherwise better-scoring unknown-risk candidate. Because consumers may assume the list is ordered by the displayed `score`, expose a decision key/tier or document the ordering policy explicitly.
