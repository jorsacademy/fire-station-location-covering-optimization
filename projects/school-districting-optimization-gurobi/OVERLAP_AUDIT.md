# Repository Overlap Audit — School Districting and Redistricting

This document records portfolio overlap without merging, archiving, renaming, or deleting repositories.

## `school-districting-optimization-gurobi`

**Overlap but justified.**

Role: educational MILP/course implementation for neighborhood-grade cohort assignment.

Distinctive scope:

- baseline assignment formulation;
- school/grade capacities;
- grade availability;
- travel-distance minimization;
- continuity-preference extension;
- course-style notebook and teaching sequence.

## `school-redistricting-optimization-gurobi`

**Overlap but justified.**

Role: richer redistricting toolkit built around a broader operational model.

Distinctive scope:

- capacity/utilization limits;
- school-opening decisions;
- minimum class sizes;
- maximum travel restrictions;
- continuity rewards;
- sibling co-location;
- grade-progression switching penalties;
- optional socioeconomic-balance penalties;
- package layout, validation, tests, and CI.

## Audit decision

Keep both repositories. The first is the compact teaching model; the second is the extended toolkit. They share the same domain and some decision variables, but the implementation depth and educational purpose differ materially.

If maintenance ever becomes burdensome, shared synthetic-data conventions or common validation helpers could be extracted, but a repository merge is not currently justified.
