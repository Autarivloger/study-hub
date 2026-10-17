"""Week47 Days 1-2: evaluation design and bounded nested search."""

FIXED47 = '''from lab import make_splits, make_pipeline
d = make_splits()
m = make_pipeline().fit(d["X_train"], d["y_train"])
'''
TUNED47 = '''from lab import make_splits, make_tuned
d = make_splits()
m = make_tuned().fit(d["X_train"], d["y_train"])
'''

L(0, '1. Evaluate the procedure, not just the winning score',
  'Separate fitting, selection, outer evaluation and final reporting.',
  [('Selection procedure', 'The whole sequence of preparation, model/parameter choices, threshold development and refitting. An evaluation must account for every decision that learns from data.'),
   ('Inner versus outer evaluation', 'Inner folds guide choices. Outer held-out folds evaluate those choices as a procedure. A separate final holdout can still provide a last frozen report.')],
  'Week46 showed that a validation-selected threshold can disappoint on final cases. The repair is not to choose whichever final threshold looks nicer. Define the next development procedure, reserve suitable evaluation data and measure the complete selection process.\n\nIf you compare many parameter settings and publish the best inner score, that score has also guided your choice. It is development evidence. In nested evaluation, each outer fitting portion performs its own search without seeing the outer validation answers. Only then is its chosen procedure scored on those outer cases.\n\nThis project uses a new fixed simulation and a reserved final holdout. A new simulator seed is not new evidence about actual customers. The outer results describe a predeclared procedure; repeatedly changing that procedure because of outer scores also consumes their independence. Take time to draw the boundaries before writing a search object.',
  'roles = {"fit rows": "learn state", "inner validation": "select settings", "outer validation": "evaluate the search procedure", "final holdout": "report the frozen full-training procedure"}\nfor name, role in roles.items():\n    print(name + ": " + role)',
  'Order five stages from task definition through final reporting.',
  'stages = ["define task and split", "run selection inside each outer fit", "score outer validation", "fit declared selection on full training", "report final holdout"]\nfor number, stage in enumerate(stages, 1):\n    print(number, stage)',
  'Identify the mistake in choosing an algorithm from outer scores and calling those same scores untouched.',
  'print("Outer scores guided a new choice")\nprint("They are now development feedback for that revised choice")',
  [('Does the best inner score automatically evaluate the winning choice independently?', 'No', 'Always', 'Only with a large parameter grid', 'The same inner feedback helped choose that winner.'),
   ('What must stay inside an outer fitting portion?', 'Every data-driven selection and fitted preparation step', 'Only the final coefficient fit', 'Only file saving', 'The outer validation answers must not influence the procedure they evaluate.')],
  'Try many choices, then report the best development score as independent performance.', 'Evaluate the declared selection procedure on cases that did not guide it.',
  'The dictionary separates four roles that can otherwise be confused under the word test. Its ordering is a design contract, not a claim that any model has improved.')

L(0, '2. Use K-fold when the row independence assumption fits',
  'Construct reproducible fitting/validation positions and keep paired data aligned.',
  [('KFold; positional indices', 'KFold divides sample positions into fitting and validation folds. Use iloc for pandas positions, and apply the same positions to X and y.'),
   ('Independent row assumption', 'A shuffled ordinary fold design assumes rows are suitable independent evaluation cases. It does not separate repeated people, accounts or future periods automatically.')],
  'K-fold rotates a held-out portion through the dataset, fitting a fresh estimator each time. Each observation is evaluated once in an ordinary partitioning K-fold design. Fold scores summarise different fits rather than repeated predictions from one fitted object.\n\nThe split indices are positions, not necessarily the original row labels after a previous split. Mixing loc with positional arrays can select the wrong records or fail. Verify X and y pairing and keep original row ids separately for tracing outcomes.\n\nOrdinary KFold does not preserve classification proportions by itself. It is often useful for suitable regression rows; rare-event classification usually needs stratification as well. More importantly, neither ordinary nor stratified random rows solves source or time dependence. Choose according to how the future prediction will be used.',
  'from sklearn.model_selection import KFold\nimport pandas as pd\nX = pd.DataFrame({"measurement": range(12)}, index=range(100, 112))\ny = pd.Series(range(12), index=X.index)\ncv = KFold(n_splits=3, shuffle=True, random_state=47)\nfor number, (fit, valid) in enumerate(cv.split(X), 1):\n    print("Fold", number, "fit", len(fit), "valid", len(valid), "overlap", len(set(fit) & set(valid)))\n    print("Paired:", X.iloc[valid].index.equals(y.iloc[valid].index))',
  'Verify all twelve positions receive one validation visit.',
  'from sklearn.model_selection import KFold\npositions = [int(i) for _, valid in KFold(n_splits=3).split(range(12)) for i in valid]\nprint("Visits:", len(positions), "unique:", len(set(positions)))',
  'Show the difference between row label101 and positional index1.',
  'import pandas as pd\ns = pd.Series([10, 20, 30], index=[100, 101, 102])\nprint("Position1:", s.iloc[1])\nprint("Label101:", s.loc[101])',
  [('What does KFold return for selecting pandas rows?', 'Positional index arrays', 'Always original row labels', 'Only target classes', 'Use iloc to apply fold positions.'),
   ('Does shuffled KFold guarantee account-level independence?', 'No', 'Always', 'Only with a fixed seed', 'Related rows can occupy different row positions and folds.')],
  'Apply fold positions with loc or treat shuffled rows as automatically independent.', 'Use paired positional selection and justify the independence unit.',
  'Each fold uses eight fitting and four validation positions. Original labels start at100, demonstrating why position and label selection are different.')

L(0, '3. Preserve class support with stratified folds',
  'Use StratifiedKFold and inspect positive counts before fitting a rare-event model.',
  [('StratifiedKFold', 'A classification splitter that approximately preserves class proportions across folds. It does not create new events or guarantee source/time independence.'),
   ('make_data; make_splits', 'The supplied lab simulates independent subscriptions using fixed seed47. It reserves240 final rows and returns960 training rows; all examples use training only unless explicitly making the final report.')],
  'A rare-event fold with no actual positives cannot estimate binary positive-versus-negative ranking. Before fitting, count support in every planned partition. StratifiedKFold helps distribute the existing labels rather than leaving composition entirely to a random row shuffle.\n\nThe helper gives the main training portion only to this splitter. The final holdout is not a member of these folds. Label counts guide a planned split, not permission to fit preparation on validation or choose model features using final answers.\n\nA single rare example cannot become independent fitting and evaluation evidence by copying it. If the requested folds do not have enough positive support, change the design or gather suitable outcomes and explain the limitation. Group or chronological constraints may make exact class balance impossible; preserving the correct prediction setting matters more than forcing attractive counts.',
  'from lab import make_splits\nfrom sklearn.model_selection import StratifiedKFold\nd = make_splits()\nX, y = d["X_train"], d["y_train"]\ncv = StratifiedKFold(n_splits=3, shuffle=True, random_state=47)\nfor number, (fit, valid) in enumerate(cv.split(X, y), 1):\n    print("Fold", number, "fitting positives", int(y.iloc[fit].sum()), "validation positives", int(y.iloc[valid].sum()))',
  'Verify all outer-training labels remain paired after a fold selection.',
  'from lab import make_splits\nfrom sklearn.model_selection import StratifiedKFold\nd = make_splits()\nfit, valid = next(StratifiedKFold(n_splits=3).split(d["X_train"], d["y_train"]))\nprint("Paired:", d["X_train"].iloc[fit].index.equals(d["y_train"].iloc[fit].index))\nprint("Disjoint positions:", not set(fit) & set(valid))',
  'State what stratification cannot establish about a repeated customer table.',
  'print("Label proportions can be balanced")\nprint("Repeated sources can still cross row folds")\nprint("Choose group/time constraints when the task requires them")',
  [('Does stratification create more independent cancellation outcomes?', 'No', 'Always', 'Only with three folds', 'It distributes existing events rather than adding observations.'),
   ('Can a one-class validation subset estimate binary ROC AUC?', 'No', 'Always', 'Only after scaling', 'That ranking requires both actual comparison classes.')],
  'Trust only the total fold sizes and omit positive-event support.', 'Inspect label support and choose a split suited to the intended cases.',
  'The printed counts describe fitting and validation positives within the reserved960-row training portion. None of the final240 labels guides this example.')

L(0, '4. Keep related sources together with grouped validation',
  'Check group disjointness and distinguish it from balanced class proportions.',
  [('GroupKFold; groups', 'GroupKFold assigns every row of a supplied group entirely to one validation fold. A group id represents a shared source such as account, person or device.'),
   ('StratifiedGroupKFold', 'A splitter that attempts class-proportion balance while keeping groups intact. Group constraints can prevent exact balance; the correct independence unit remains essential.')],
  'If three records belong to the same account, a random row split can let the model see that account during fitting and evaluate on a nearby snapshot. That may estimate familiarity with known accounts rather than the new-account performance you intended.\n\nPass source ids as groups and verify their intersection, not only row-number intersection. A group field should normally stay outside the predictive features unless the actual task justifies its use. Grouping and stratification solve different constraints; a group-aware splitter does not promise balanced rare-event support.\n\nThis small fictional example contains six groups with two rows each. It demonstrates assignment mechanics, not a model score. A real design needs enough independent groups and an appropriate time boundary as well. New-source and later-time prediction can require more than one constraint.',
  'import numpy as np\nfrom sklearn.model_selection import GroupKFold, StratifiedGroupKFold\nX = np.arange(12).reshape(-1, 1)\ngroups = np.repeat(np.arange(6), 2)\ny = np.tile([0, 1], 6)\nfor splitter in [GroupKFold(n_splits=3), StratifiedGroupKFold(n_splits=3)]:\n    for fold, (fit, valid) in enumerate(splitter.split(X, y, groups), 1):\n        overlap = set(groups[fit]) & set(groups[valid])\n        print(type(splitter).__name__, fold, "group overlap", len(overlap), "validation positives", int(y[valid].sum()))',
  'Detect source leakage even when row ids differ.',
  'fit_sources, valid_sources = {"A", "B"}, {"B", "C"}\nprint("Shared source:", sorted(fit_sources & valid_sources))',
  'Name the grouping unit for repeated device measurements.',
  'contract = {"row": "one device snapshot", "independence_unit": "device id", "intended_evaluation": "new devices"}\nprint(contract)',
  [('What must be disjoint for a new-account grouped evaluation?', 'Account sources across fit and validation', 'Only displayed row numbers', 'Only feature column names', 'Related rows can have different row labels but the same source.'),
   ('Does grouping automatically guarantee exact class proportions?', 'No', 'Always', 'Only with many rows', 'Source constraints can prevent exact label balance.')],
  'Check row ids only while repeated sources cross the evaluation boundary.', 'Choose and verify the actual independence unit.',
  'Both splitters keep the supplied group ids disjoint here. The balanced toy groups are convenient for illustration, not a promise about arbitrary real datasets.')

L(0, '5. Respect time and feature availability',
  'Construct later-period validation with a deliberate gap and causal feature window.',
  [('TimeSeriesSplit; gap', 'TimeSeriesSplit uses earlier positions for fitting and later positions for validation. gap excludes a specified number of positions immediately before validation; it is not automatically a number of calendar days.'),
   ('Outcome horizon and temporal leakage', 'Labels and rolling features must be available by each fitting boundary. Ordered rows alone cannot repair features computed from future observations.')],
  'For future-period prediction, shuffling later information into fitting can answer the wrong question. A chronological split better reflects what was known before the prediction. A gap can help separate overlapping measurement or outcome windows, but its correct size comes from the data process.\n\nTimeSeriesSplit operates on ordered positions. If records are irregularly spaced, a gap of two rows is not necessarily two days. Sort by the meaningful time field and consider calendar-based windows when needed. A thirty-day cancellation label is not fully observed twelve days after the snapshot.\n\nThe example shows positions only and makes no classification score claim. Some chronological folds may have too few positives or shifted feature distributions; inspect them rather than forcing an inappropriate stratified shuffle. Week47\'s main project remains an independent-event simulation, so its shuffled folds are a separately stated assumption.',
  'import numpy as np\nfrom sklearn.model_selection import TimeSeriesSplit\npositions = np.arange(12)\ncv = TimeSeriesSplit(n_splits=3, test_size=2, gap=1)\nfor number, (fit, valid) in enumerate(cv.split(positions), 1):\n    print("Fold", number, "latest fit", int(fit.max()), "first validation", int(valid.min()), "gap positions", int(valid.min() - fit.max() - 1))',
  'Check that all fitting times precede an invented validation period.',
  'fit_days, valid_days = [1, 2, 3, 4], [6, 7]\nprint("Earlier fitting:", max(fit_days) < min(valid_days))\nprint("Excluded day:", 5)',
  'Identify a future-dependent rolling feature as invalid at its prediction time.',
  'features = {"past seven-day usage": "available", "next seven-day usage": "future"}\nfor name, status in features.items():\n    print(name, "usable now:", status == "available")',
  [('Does gap=1 always mean one calendar day?', 'No; it counts positions', 'Always', 'Only on a DataFrame', 'Calendar meaning depends on record spacing.'),
   ('Can chronological rows make a future-computed feature safe?', 'No', 'Always', 'Only with a large gap', 'The feature\'s own information boundary must also be valid.')],
  'Shuffle a forecasting table or compute rolling statistics using the complete future timeline.', 'Match time windows, label availability and evaluation order to the real task.',
  'The printed position gap is exactly one. No target fitting is performed, so the example isolates split mechanics from assumptions about outcome support.')

L(0, '6. Run fresh complete fits across declared folds',
  'Use cross_validate and distinguish CV validation fields from the final holdout.',
  [('lab.make_pipeline', 'Our project helper returns named median-imputation, scaling and logistic-model steps. It differs from sklearn.pipeline.make_pipeline, which constructs a pipeline from estimator arguments.'),
   ('cross_validate; test_* names', 'cross_validate clones and fits the supplied estimator separately for each fold. Its test_* fields name fold-validation scores, not a project-wide reserved final test.'),
   ('Fold variability', 'Different fits and validation cases produce different scores. Their spread is descriptive, not automatically a confidence interval or a prediction interval.')],
  'After choosing a suitable splitter, pass a complete estimator pipeline to cross_validate. Each clone must learn its own preparation from its fitting positions. Pre-scaling all rows before the call would allow fold-validation information into the learned representation.\n\nThis fixed-model exercise uses average precision from Week46. It does not tune a parameter or assess the full search yet. The main release later evaluates a search procedure under a declared cost objective. Keeping those roles explicit avoids quietly switching objectives when a result is disappointing.\n\nThe membership image uses only the reserved training portion. Its grey/blue positions show which rows are fitted or validated in each fold; position order here is a shuffled independent-row design, not a timeline. Read the plotted membership separately from the printed AP scores.',
  'import numpy as np\nimport matplotlib.pyplot as plt\nfrom sklearn.model_selection import StratifiedKFold, cross_validate\nfrom lab import make_splits, make_pipeline\nd = make_splits()\nX, y = d["X_train"], d["y_train"]\nfolds = list(StratifiedKFold(n_splits=3, shuffle=True, random_state=47).split(X, y))\nr = cross_validate(make_pipeline(), X, y, cv=folds, scoring="average_precision", n_jobs=1, error_score="raise")\nprint("Fold AP:", r["test_score"].round(3).tolist())\nmembership = np.zeros((3, len(X)))\nfor row, (_, valid) in enumerate(folds):\n    membership[row, valid] = 1\nfig, ax = plt.subplots(figsize=(6.5, 2.6))\nax.imshow(membership, aspect="auto", interpolation="nearest", cmap="Blues", vmin=0, vmax=1)\nax.set(yticks=[0, 1, 2], yticklabels=["Fold1", "Fold2", "Fold3"], xlabel="Position inside reserved training table", title="Dark positions: validation; pale positions: fitting")\nfig.tight_layout()\nfig.savefig("chart.png", dpi=110)\nplt.close(fig)',
  'Check that each training position is assigned to one validation fold.',
  'import numpy as np\nfrom sklearn.model_selection import StratifiedKFold\nfrom lab import make_splits\nd = make_splits()\nvisits = np.zeros(len(d["X_train"]), dtype=int)\nfor _, valid in StratifiedKFold(n_splits=3).split(d["X_train"], d["y_train"]):\n    visits[valid] += 1\nprint("Exactly one visit:", bool((visits == 1).all()))',
  'Map three intended uses to a reasonable initial evaluation design.',
  'plans = {"independent rare events": "stratified folds", "new accounts with repeated rows": "grouped folds", "later dates": "chronological folds"}\nfor use, plan in plans.items():\n    print(use + ": " + plan)',
  [('Does test_score here automatically mean the reserved final holdout?', 'No; it is a fold-validation score', 'Always', 'Only for binary labels', 'Library field names do not redefine the outer experiment boundary.'),
   ('What should cross-validation receive to prevent preparation leakage?', 'The complete unfitted preparation-and-model pipeline', 'An all-data scaled table only', 'Final test answers', 'Each fitting fold must own its learned preparation.')],
  'Pre-fit preparation on all rows and call the subsequent classifier CV leakage-safe.', 'Fit the full declared procedure independently within each allowed fitting fold.',
  'The picture shows membership, while the printed AP values measure a fixed model on those folds. The final240 rows are absent from both.',
  figure=('Three stratified fitting/validation membership rows inside the960-row training portion', 'Dark positions are the current fold\'s validation rows; pale positions are fitting rows. Each training position receives one validation visit. The final holdout is not shown.'))
