# Repository Overlap Audit — Fire-Station Location

This document records overlap without merging, archiving, renaming, or deleting repositories.

## `fire-station-location-covering-optimization`

**Keep separate.**

Mathematical role: set-covering-style facility-location model.

Distinctive elements:

- response-time coverage sets;
- minimum-cost station opening;
- required single/double coverage;
- construction-budget constraint;
- no explicit demand-to-station assignment variable.

## `fire-station-location-optimization-pulp`

**Keep separate.**

Mathematical role: location-allocation model with explicit demand assignments.

Distinctive elements:

- station-opening variables plus demand-to-station assignment variables;
- weighted response-time objective;
- station-count limit;
- construction budget;
- coverage-radius logic;
- sensitivity analysis and visualization.

## Audit decision

These repositories solve related public-service location problems but are not duplicates. One teaches **covering**, while the other teaches **location-allocation/assignment**.

The difference is structural, not cosmetic. They should remain independent and be cross-linked only through the existing research-series map.
