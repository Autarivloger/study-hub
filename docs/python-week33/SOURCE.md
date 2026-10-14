# Iris dataset provenance

**Fisher, R. (1936). Iris [Dataset]. UCI Machine Learning Repository.**

- Dataset and metadata: https://archive.ics.uci.edu/dataset/53/iris
- Persistent identifier: https://doi.org/10.24432/C56C76
- Download: https://archive.ics.uci.edu/static/public/53/iris.zip
- File retained from that archive: **iris.data**,4551bytes.
- SHA-256: `6f608b71a7317216319b4d27b4d9bc84e6abd734eda7872b71a458569e2656c0`
- Retrieved for this course on2026-10-15.
- Licence specified by UCI: **Creative Commons Attribution4.0 International**.
  Terms: https://creativecommons.org/licenses/by/4.0/

The retained file is unchanged. Original UCI data has five fields per nonblank
row, without a header: sepal length, sepal width, petal length, petal width
(all centimetres), and species. There are150 plant instances,50 per species.
The teaching code adds descriptive column names and a sequential **row_id**;
that label is a source-row reference, not an original plant/specimen ID.

## Version limitation

UCI documents differences between this historical data and Fisher's paper
in the35th and38th setosa records. This exercise retains iris.data as supplied
and reports that limitation. It does not silently substitute bezdekIris.data,
a library's corrected copy, or an undocumented repair. Results involving
affected measurements can therefore differ from another Iris version.

Equal measurement rows are retained. Different plant instances can share
rounded measurements; feature equality does not establish specimen identity.
The file does not provide the metadata needed to independently establish a
random sample from a specified modern population or every independence
assumption. The capstone's p-values and intervals are **conditional teaching
calculations**, not a guarantee of population validity or causal effects.

All explanatory text, exercises, scripts and generated chart previews are
original additions to StudyHub. The underlying real botanical data is credited
to its source above; it is not synthetic and contains no StudyHub user data.
