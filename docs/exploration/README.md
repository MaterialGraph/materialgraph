# MaterialGraph Exploration

## Purpose

This directory records external projects, scientific initiatives,
institutional frameworks, tools, publications, and industry observations
that may provide useful insight for MaterialGraph.

Exploration documents are a research notebook for the project. They
allow MaterialGraph to learn from developments in materials science,
scientific software, computational research, AI-assisted science, and
research infrastructure without turning every interesting idea into a
product requirement.

## Governance Rule

> **Exploration documents capture things worth thinking about. Canonical
> documents capture decisions MaterialGraph has actually made.**

An entry here does **not** automatically become a MaterialGraph
requirement, roadmap commitment, architectural decision, implementation
task, or scientifically validated capability.

External ideas should first be examined for relevance, scientific
meaning, compatibility with MaterialGraph's boundaries, researcher
value, and overlap with existing capabilities.

## Insight Lifecycle

``` text
External Observation
        |
        v
Exploration Note
        |
        v
Relevance Assessment
        |
        v
Does It Reveal a MaterialGraph Gap?
       / \
     No   Yes
     |     |
     v     v
 Retain   Distill Durable Insight
             |
             v
   Principle / Architecture /
   Requirement / Roadmap Candidate
             |
             v
      Canonical Documentation
             |
             v
       Validated Implementation
```

Promotion into canonical documentation should occur only when an insight
reveals a sufficiently understood and relevant MaterialGraph
requirement, principle, boundary, or validated future direction.

## Canonical Documents Remain Authoritative

Where an exploration note conflicts with canonical MaterialGraph
documentation, canonical documentation remains authoritative unless an
explicit reviewed change is made.

Relevant canonical documents include `what_should_be_materialgraph.md`,
`scientific_principles.md`, `research_architecture.md`,
`system_architecture.md`, `roadmap.md`, the current intelligence map,
and audit/remediation documentation.

## Recommended Entry Structure

Each external insight should record:

1.  Source / Project
2.  Why We Examined It
3.  Relevant Observations
4.  Potential MaterialGraph Insight
5.  Relationship to Existing Architecture
6.  What MaterialGraph Should Not Infer From It
7.  Current Decision
8.  Promotion Criteria

Suggested states are `OBSERVATION ONLY`,
`EXPLORATORY — NO IMPLEMENTATION COMMITMENT`,
`ARCHITECTURAL INSIGHT ACCEPTED`, `PROMOTED TO CANONICAL DOCUMENTATION`,
and `NOT CURRENTLY RELEVANT`.

## Scientific Discipline

External systems should not be treated as evidence that MaterialGraph
itself is scientifically valid. A useful architecture used by another
project may inspire MaterialGraph, but MaterialGraph must still validate
its own implementation, scientific semantics, researcher usefulness, and
scientific outputs independently.

Institutional activity in an adjacent problem space demonstrates
relevance of that problem space; it does not prove that MaterialGraph
solves the problem.

## Initial Scope

The initial exploration log records insights already examined during
MaterialGraph development: molecular-dynamics/scientific-compute
tooling, Apheris-related private/domain scientific context, localized
scientific evidence, Argonne ChemGraph, FORUM-AI, and DOE critical
minerals and materials.

As this material grows, individual topics may later be split into
dedicated files or subdirectories. Keep the directory simple until that
scale actually requires further organization.
