# Palmer Penguins source snapshot

## Credits and licence

Horst AM, Hill AP, Gorman KB (2020). **palmerpenguins: Palmer Archipelago
(Antarctica) penguin data.** https://doi.org/10.5281/zenodo.3960218

Project documentation: https://allisonhorst.github.io/palmerpenguins/

Data were collected and made available by **Dr.Kristen Gorman and Palmer
Station LTER**. Original research: Gorman KB, Williams TD, Fraser WR (2014),
*Ecological sexual dimorphism and environmental variability within a community
of Antarctic penguins (genus Pygoscelis)*, PLoS ONE9(3):e90081.
https://doi.org/10.1371/journal.pone.0090081

The project documentation specifies **CC0 data terms**:
https://creativecommons.org/publicdomain/zero/1.0/
Its data-policy and original research links remain available from that page.
No artwork, R lesson source or third-party teaching prose is copied here.

## Exact retained input

- File: penguins.csv, the simplified eight-column table.
- Repository revision: `8957207b78d6ccd1b4654a9dd9c9041b657478ab`
- Download: https://raw.githubusercontent.com/allisonhorst/palmerpenguins/8957207b78d6ccd1b4654a9dd9c9041b657478ab/inst/extdata/penguins.csv
- Retrieved:2026-10-15.
- Byte length:15241.
- SHA-256: `f204db2c753b0937caac3cb35258562c14f073e4bbc76be24b4c51ce22767a93`
- Raw bytes are retained unchanged. A scoped Git attribute prevents newline
  conversion from changing this snapshot during a Windows checkout.

The full file has344 records and8fields: species, island, bill_length_mm,
bill_depth_mm, flipper_length_mm, body_mass_g, sex and year. Documented **NA**
tokens mean unknown. The four measurements each have2unknowns; recorded sex
has11. Species counts: Adelie152, Chinstrap68, Gentoo124. Collection years
are2007–2009; measurements are in millimetres or grams as their names state.

## Scope and transformations

The package describes penguin observations. The simplified table omits raw
individual identifiers and collection detail, so generated source positions
do not independently verify specimen identity, matched trajectories or every
sampling assumption. These records are not a census of Antarctic birds.
Species/island combinations have limited observed overlap. No causal island,
sex, species, year or climate intervention effect is identified by this EDA.

StudyHub's twelve-row inline walkthrough selects the first4source records
from each species in source order, for compact self-contained examples. It
is **not** the full sample and does not preserve its composition or island
coverage. Full-project findings always come from the entire retained CSV.

The project assigns source-record positions, converts declared unknowns and
types, logs declared whitespace/sex-case normalisation, flags equal-value
candidates and within-species IQR observations, and **retains all valid source
rows without imputation or automatic deduplication**. Invalid tokens stop the
run; per-question known-value exclusions are reported separately.

Fictional dirty-token and composition examples in the course are labelled as
such; they are not edits or allegations about the original research source.
Original explanations, exercises and Python code were authored for StudyHub.
