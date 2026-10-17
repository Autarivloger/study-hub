"""Week46 Days 1-2: classification interfaces and logistic reasoning."""

TRAIN_LOGISTIC = '''from lab import make_splits, make_candidates, positive_scores
d = make_splits()
m = make_candidates()["logistic"].fit(d["X_train"], d["y_train"])
p = positive_scores(m, d["X_valid"])
'''

IRIS_BINARY = '''from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
iris = load_iris(as_frame=True)
mask = iris.target > 0
X = iris.data.loc[mask, ["petal length (cm)", "petal width (cm)"]]
y = (iris.target.loc[mask] == 2).astype(int)
Xt, Xv, yt, yv = train_test_split(X, y, test_size=0.2, stratify=y, random_state=46)
m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000, tol=1e-7)).fit(Xt, yt)
'''

L(0, '1. Define categories before choosing a classifier',
  'Distinguish binary, multiclass and multilabel questions and name the target meaning.',
  [('Binary; multiclass; multilabel', 'Binary chooses between two classes. Multiclass chooses one of several mutually exclusive classes. Multilabel can assign several labels to one sample; it is a different output contract.'),
   ('Positive class; outcome window', 'Positive names the event of interest, not a good outcome. In the main project label1 means cancellation within the next30days, after the input snapshot.')],
  'Week45 predicted quantities. This week predicts category membership. Cancellation versus retention is binary classification; one of three Iris species is multiclass; assigning both urgent and billing tags to a message is multilabel. Numeric codes do not turn categories into measured amounts.\n\nWrite what one row represents, what every label means and when the answer becomes known. Our main project uses independent fictional subscriptions with inputs recorded before the prediction and cancellation observed within a defined follow-up window. A subscription still inside that window is not automatically a verified negative.\n\nThe positive class is a convention you must state. Here it is cancellation, even though cancellation is not the desired business outcome. In the separate Iris exercise, positive means virginica among two selected species. Keep those label definitions separate. No model score decides whether a recorded outcome is correct or whether the proposed decision is useful.',
  'tasks = {"cancel or retain": "binary", "one Iris species": "multiclass", "urgent plus billing tags": "multilabel"}\nfor task, kind in tasks.items():\n    print(task + ": " + kind)\nprint("Main project: 1=cancelled within30days; 0=retained")',
  'Write an explicit positive/negative mapping for a delayed-delivery classification task.',
  'labels = {0: "not delayed under the declared deadline", 1: "delayed under the declared deadline"}\nfor code, meaning in labels.items():\n    print(code, meaning)',
  'Reject treating an unfinished30-day follow-up as a verified retention label.',
  'follow_up_days = 12\nprint("Complete30-day outcome observed:", follow_up_days >= 30)\nprint("Pending is not automatically a negative label")',
  [('Does positive necessarily mean a desirable outcome?', 'No; it names the declared event', 'Always', 'Only when coded1', 'The convention must be stated rather than inferred from the word positive.'),
   ('Which task can assign several tags to one row?', 'Multilabel', 'Ordinary multiclass only', 'Numerical regression', 'Multilabel outputs are not one mutually exclusive class per sample.')],
  'Treat unfinished outcomes as negatives and assume everyone knows what label1 means.', 'Define the event, follow-up window and meaning of every label first.',
  'The dictionary classifies task shapes, not predictive quality. The follow-up check separates a completed observation from an answer that is still unknown.')

L(0, '2. Freeze inputs, labels and paired evaluation partitions',
  'Inspect a stratified training partition without learning from final outcomes.',
  [('make_data; make_splits', 'The supplied lab simulates1200 independent subscriptions locally. make_splits returns stratified720/240/240 training/validation/final-test rows with paired indices.'),
   ('Prediction-time feature contract', 'Tenure in months, recent weekly sessions, unresolved ticket count and days inactive must be available before the predicted30-day outcome. Later cancellation details are not inputs.')],
  'The project has four named numeric inputs. Its generator uses an authored relationship plus random outcome sampling to make an imbalanced exercise. These are not real customer records, and their scores cannot establish actual retention performance or causal effects. The teaching data never comes from your Study Hub progress.\n\nSplit paired X and y together and preserve approximate class proportions. The helper reserves a final test before development and gives validation a separate role. Inspect training counts and feature meanings now. Later parts use validation for candidate and threshold choices, with the final test reserved for reporting.\n\nThis shuffled design follows the simulator’s independent-row assumption. Real repeated account snapshots need grouping and time-aware feature windows; future periods may require chronological evaluation. Stratification preserves label composition, not every feature distribution or source independence. Do not blindly copy the split merely because both projects contain a cancellation target.',
  'from lab import make_splits, FEATURES\nd = make_splits()\nprint("Features:", FEATURES)\nprint("Partition rows:", [len(d["X_" + part]) for part in ["train", "valid", "test"]])\nprint("Training labels:", d["y_train"].value_counts().sort_index().to_dict())\nprint("Paired training index:", d["X_train"].index.equals(d["y_train"].index))',
  'Verify disjoint identities across all three partitions without using their target values.',
  'from lab import make_splits\nd = make_splits()\na, b, c = [set(d["X_" + name].index) for name in ["train", "valid", "test"]]\nprint("Disjoint:", not (a & b or a & c or b & c))\nprint("All1200rows covered:", a | b | c == set(range(1200)))',
  'Exclude the later cancellation date from a proposed snapshot feature list.',
  'fields = {"weekly_sessions": True, "tenure_months": True, "later_cancellation_date": False}\nprint("Snapshot inputs:", [name for name, available in fields.items() if available])',
  [('Does stratification prove repeated accounts are independent?', 'No', 'Always', 'Only for a binary target', 'A label-proportion constraint does not establish source independence.'),
   ('Can later cancellation details be input to an earlier prediction?', 'No', 'Yes if stored in the historical table', 'Only after scaling', 'Availability at prediction time determines whether a feature is usable.')],
  'Split random account snapshots without checking related sources or future columns.', 'Review the row unit, time boundary, paired indices and intended evaluation population.',
  'Only training label counts are inspected here. Partition identity checks answer a different question from target balance and do not claim the simulator represents actual customers.')

L(0, '3. Separate model scores from class decisions',
  'Read predict_proba columns through classes_ and apply an explicit threshold rule.',
  [('LogisticRegression; make_candidates', 'LogisticRegression is a classifier despite its name; it models linear log-odds and uses a sigmoid for a binary score. make_candidates constructs fresh declared lab pipelines; Day2 explains the model mathematics.'),
   ('predict_proba; classes_; positive_scores', 'Probability columns follow classes_. The supplied positive_scores helper locates label1 rather than assuming a column position has a meaning.'),
   ('Decision threshold; >= convention', 'A threshold converts a score to a flag. This lab explicitly flags when score>=threshold, including equality; library default tie conventions need not be identical.')],
  'A score and a decision answer different questions. predict_proba gives one estimated class probability per class. A decision rule then chooses a label or action. Changing that rule can change false alarms and missed events without changing the fitted model or its scores.\n\nAlways identify the probability column using classes_. A two-column array is not self-documenting, and label codes can differ in another project. Here positive_scores selects the cancellation column by label1. A value such as0.2 is a model estimate, not verified truth or automatically calibrated population risk.\n\nThe example fits one training-only logistic pipeline and predicts validation scores. It prints only a few rows to make the mapping visible. The0.5 rule is an explicitly chosen starting convention, not a business-optimal threshold. Day4 evaluates other thresholds using validation evidence while leaving the final test aside.',
  TRAIN_LOGISTIC + 'print("Class-column order:", m.classes_.tolist())\nprint("First positive scores:", p[:5].round(3).tolist())\nprint("Flags at0.5:", (p[:5] >= 0.5).astype(int).tolist())\nprint("Rows remain paired:", len(p) == len(d["y_valid"]))',
  'Map a two-column score table to labels[2,7] and select the declared positive label7.',
  'import numpy as np\nclasses = [2, 7]\nscores = np.array([[0.8, 0.2], [0.1, 0.9]])\npositive = classes.index(7)\nprint("Label7 scores:", scores[:, positive].tolist())',
  'Apply the lab’s equality rule to scores[0.49,0.5,0.51].',
  'import numpy as np\np = np.array([0.49, 0.5, 0.51])\nprint("Flags:", (p >= 0.5).astype(int).tolist())',
  [('What identifies a probability column’s label?', 'classes_', 'Its colour in a chart', 'The number of input columns', 'The class ordering belongs to the fitted estimator.'),
   ('Can changing a threshold alter decisions without refitting?', 'Yes', 'Never', 'Only if labels change', 'A decision rule acts on an existing score vector.')],
  'Assume every column1 always has the desired event meaning and every score is certainty.', 'Read the label mapping, state the decision rule and assess score reliability.',
  'The pipeline learns imputation, scaling and logistic state only from training. The score vector is then converted to flags by a separate visible comparison.')

L(0, '4. Visualise a two-feature decision boundary',
  'Explain the boundary as a threshold contour in input space.',
  [('Decision boundary', 'The set of input locations where a decision changes under a chosen threshold. A logistic model has a linear log-odds boundary in the supplied feature representation.'),
   ('make_classification; meshgrid; np.c_', 'make_classification generates local synthetic labelled points. meshgrid creates a coordinate grid; np.c_ combines flattened coordinate columns into input rows. These are prediction queries, not new observed training evidence.')],
  'With two inputs you can draw where a model changes its decision. The background below shows regions predicted negative or positive at a declared0.5 threshold. The points are the supplied synthetic observations. The line is a model boundary, not a verified physical separation between real customer types.\n\nThe model is linear in its supplied log-odds features, so the binary boundary is a straight line in this two-dimensional representation. Curved or expanded features can produce a different boundary in original input coordinates. A plot cannot establish calibration, fairness or future performance by itself.\n\nThis fit uses all displayed points as a geometry demonstration. No held-out performance claim is made. The grid only asks the fitted model for predictions at coordinates; do not count those grid positions as hundreds of new independently observed cases. The separate project’s partitions remain unchanged.',
  'import numpy as np\nimport matplotlib.pyplot as plt\nfrom sklearn.datasets import make_classification\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nX, y = make_classification(n_samples=120, n_features=2, n_redundant=0, n_informative=2, class_sep=1.2, random_state=46)\nm = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X, y)\nxx, yy = np.meshgrid(np.linspace(X[:, 0].min()-0.5, X[:, 0].max()+0.5, 140), np.linspace(X[:, 1].min()-0.5, X[:, 1].max()+0.5, 140))\nscore = m.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1].reshape(xx.shape)\nprint("Grid shape:", score.shape)\nprint("Fitted class labels:", m.classes_.tolist())\nfig, ax = plt.subplots(figsize=(6, 4.2))\nax.contourf(xx, yy, score >= 0.5, levels=[-0.5, 0.5, 1.5], colors=["#e0ebf5", "#f7e0c7"])\nax.contour(xx, yy, score, levels=[0.5], colors=["#333333"])\nax.scatter(X[:, 0], X[:, 1], c=y, cmap="coolwarm", edgecolors="white", s=25)\nax.set(xlabel="Synthetic feature A", ylabel="Synthetic feature B", title="Logistic decision regions at threshold0.5")\nfig.tight_layout()\nfig.savefig("chart.png", dpi=110)\nplt.close(fig)',
  'Classify two points under an invented linear score x1+x2-1 at a zero score boundary.',
  'import numpy as np\nX = np.array([[0.0, 0.0], [1.0, 1.0]])\nscore = X[:, 0] + X[:, 1] - 1\nprint("Linear scores:", score.tolist())\nprint("Positive side:", (score >= 0).tolist())',
  'Explain why a grid with10000positions is not10000new observed outcomes.',
  'print("Grid positions: model queries")\nprint("Independent observed outcomes: not supplied by the grid")',
  [('What does the shaded background represent?', 'The fitted model’s decisions at queried coordinates', 'Verified true labels everywhere', 'A calibrated confidence interval', 'The background is generated from predictions, not new ground truth.'),
   ('Does this training geometry plot establish held-out accuracy?', 'No', 'Always', 'Only if the line is straight', 'No independent evaluation outcomes were used for this illustration.')],
  'Count synthetic grid predictions as new validation evidence.', 'Distinguish a decision visualisation from independently observed evaluation cases.',
  'The grid is transformed and scored by the same fitted pipeline. The0.5 contour separates its two decision regions; the original points show the training geometry only.',
  figure=('Synthetic two-feature logistic decisions and the0.5 score contour', 'Background colours are model decisions, not verified truth. All displayed points were used for this geometry fit; no held-out score is claimed.'))

L(0, '5. Keep multiclass probabilities and multilabel tasks distinct',
  'Read one-of-three probabilities and avoid applying a binary rule blindly.',
  [('Multiclass probability row; argmax', 'A mutually exclusive multiclass model returns one score per class, normally summing to1. argmax selects the largest score’s position, which must map back through classes_.'),
   ('Multilabel output contract', 'Several labels may independently apply to one row. That differs from choosing exactly one species, and the probability/output structure must be specified separately.')],
  'The packaged Iris dataset contains three mutually exclusive recorded species labels. In a multiclass fit, one prediction chooses one of those recorded classes. Its probability row gives an estimate for each class; selecting the maximum is different from independently flagging every column above an arbitrary binary threshold.\n\nMap positions back to class labels. A class vocabulary may be[10,20,30] rather than[0,1,2], so argmax alone is a position rather than a universal category code. The estimator’s predict handles its declared class mapping.\n\nThis small example fits the full Iris table to illustrate output shape only. It is not a final evaluation score. A later two-species exercise uses a stratified development split for logistic interpretation. Do not confuse either task with the main project’s cancellation labels or with multilabel message tags, where several labels can be true at once.',
  'import numpy as np\nfrom sklearn.datasets import load_iris\nfrom sklearn.pipeline import make_pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nd = load_iris(as_frame=True)\nm = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(d.data, d.target)\np = m.predict_proba(d.data.iloc[[0, 70, 140]])\nprint("Classes:", m.classes_.tolist())\nprint("Score shape:", p.shape)\nprint("Row sums:", p.sum(axis=1).round(6).tolist())\nprint("Mapped maximum labels:", m.classes_[np.argmax(p, axis=1)].tolist())',
  'Map the largest score in[0.2,0.7,0.1] to class labels[10,20,30].',
  'import numpy as np\nclasses = np.array([10, 20, 30])\np = np.array([0.2, 0.7, 0.1])\nprint("Predicted class:", int(classes[np.argmax(p)]))',
  'Represent a multilabel message without forcing it into one exclusive category.',
  'message_labels = {"urgent": True, "billing": True, "technical": False}\nprint("Assigned:", [name for name, present in message_labels.items() if present])',
  [('Does an argmax position always equal the original class code?', 'No; map it through classes_', 'Always', 'Only with three classes', 'Positions and label values are separate concepts.'),
   ('Is one-of-three species prediction the same as assigning several message tags?', 'No', 'Always', 'Only if tags are numbers', 'Mutually exclusive multiclass and multilabel questions have different output contracts.')],
  'Apply one binary threshold to every multiclass column and assume the task is unchanged.', 'Define whether labels are exclusive and use the corresponding decision contract.',
  'The shape is three samples by three classes. Row sums illustrate the exclusive probability convention; the code explicitly maps maximum positions back to fitted labels.')

L(0, '6. Establish a majority reference before trusting accuracy',
  'Explain how an apparently accurate classifier can miss every cancellation.',
  [('Majority-class baseline; prevalence', 'A majority reference always predicts the most common training class. Prevalence is the proportion of actual positive outcomes in the population or evaluated sample.'),
   ('Missed-event count', 'Count actual positive cases that receive a negative decision. A large overall correct proportion can conceal failure on the event of interest.')],
  'If only five of one hundred cases cancel, predicting retention for everyone gives ninety-five percent accuracy. It also finds none of the cancellations. The number is arithmetically correct but incomplete for a task that cares about missed events.\n\nUse a baseline fitted or specified from the training setting, then compare on the same held-out cases. A class label guess and a probability baseline are different references. A never-flag decision can be useful to quantify missed-event cost even though it supplies no useful ranking.\n\nThe invented list below isolates the accuracy trap. It is not the main project’s measured prevalence or a real business statistic. Day3 will name the confusion cells and precision/recall/F1 formulas. For now, always ask how many actual positives were found, how many were missed and how many negative cases were needlessly flagged.',
  'import numpy as np\nactual = np.array([0] * 95 + [1] * 5)\npredicted = np.zeros_like(actual)\nprint("Accuracy:", float((actual == predicted).mean()))\nprint("Actual cancellations:", int((actual == 1).sum()))\nprint("Cancellations found:", int(((actual == 1) & (predicted == 1)).sum()))\nprint("Cancellations missed:", int(((actual == 1) & (predicted == 0)).sum()))',
  'Compute the never-flag accuracy for80retentions and20cancellations.',
  'import numpy as np\ny = np.array([0] * 80 + [1] * 20)\nprint("Accuracy:", float((y == 0).mean()))\nprint("Positive events found: 0")',
  'Fit a majority DummyClassifier from training labels and inspect its decision.',
  'from sklearn.dummy import DummyClassifier\nm = DummyClassifier(strategy="most_frequent").fit([[0], [1], [2], [3]], [0, 0, 0, 1])\nprint("New decisions:", m.predict([[4], [5]]).tolist())',
  [('Can95%accuracy coexist with missing every positive event?', 'Yes', 'Never', 'Only if the code crashes', 'A rare-event task can have a very large negative class.'),
   ('Should a baseline and model be evaluated on different convenient rows?', 'No', 'Yes', 'Only for a dummy', 'An interpretable comparison needs matching evaluation cases.')],
  'Announce high accuracy without stating positive counts or missed events.', 'Report the class balance, baseline and error types relevant to the task.',
  'Every retained case is correct under the never-flag rule, while every cancellation is missed. The same decisions produce both the high accuracy and the complete positive-event failure.')

L(1, '1. Turn a linear score into a sigmoid probability',
  'Connect linear score, sigmoid, odds and log-odds without confusing them.',
  [('Sigmoid; scipy.special.expit', 'The sigmoid maps a real score z to1/(1+exp(-z)). scipy.special.expit computes it stably, avoiding a naive exponential overflow for extreme scores.'),
   ('Odds; log-odds', 'For0<p<1, odds=p/(1-p) and log-odds=log(odds). Binary logistic regression models log-odds as a linear combination of the supplied features.')],
  'A binary logistic model first calculates z=b0+b1*x1+… and then converts z through the sigmoid. At z=0 the probability is0.5. Positive scores yield values above0.5 and negative scores below it. The mathematical conversion does not certify that those estimates are calibrated for a future population.\n\nProbability, odds and log-odds use different scales. Probability0.8 corresponds to odds4, not odds0.8. Taking the logarithm gives a real-valued score. Logistic regression is linear in that log-odds representation, which is why a coefficient is not a fixed percentage-point change in probability.\n\nThe chart draws a mathematical function, not a fitted customer model. Its flattened ends show that an equal score increase changes probability differently near the middle versus near an extreme. Day2’s real-data exercise will fit coefficients and interpret conditional changes while preserving this scale distinction.',
  'import numpy as np\nfrom scipy.special import expit\nimport matplotlib.pyplot as plt\nz = np.array([-2.0, 0.0, 2.0])\np = expit(z)\nprint("Linear scores:", z.tolist())\nprint("Probabilities:", p.round(4).tolist())\nprint("Odds:", (p / (1 - p)).round(4).tolist())\ngrid = np.linspace(-6, 6, 200)\nfig, ax = plt.subplots(figsize=(6, 3.8))\nax.plot(grid, expit(grid), color="#376ea6")\nax.axhline(0.5, color="#777777", linestyle="--")\nax.axvline(0, color="#777777", linewidth=0.8)\nax.set(xlabel="Linear log-odds score z", ylabel="Sigmoid probability", ylim=(-0.02, 1.02), title="A logistic score is not a percentage-point slope")\nfig.tight_layout()\nfig.savefig("chart.png", dpi=110)\nplt.close(fig)',
  'Convert probability0.8 into odds and log-odds.',
  'import numpy as np\np = 0.8\nodds = p / (1 - p)\nprint("Odds:", round(odds, 3))\nprint("Log-odds:", round(float(np.log(odds)), 3))',
  'Use expit on extreme scores without overflowing a naive exponential.',
  'from scipy.special import expit\nprint("Extreme sigmoid values:", expit([-1000.0, 0.0, 1000.0]).tolist())',
  [('What probability corresponds to log-odds zero?', '0.5', '0', '1', 'expit(0)=1/(1+1).'),
   ('Is a logistic coefficient a fixed probability percentage-point change?', 'No; it changes log-odds in the supplied representation', 'Always', 'Only for a binary target', 'The sigmoid makes probability changes depend on the starting score.')],
  'Interpret a coefficient of1 as adding100percentage points of probability.', 'Distinguish score, probability, odds and log-odds explicitly.',
  'The printed score0 maps to0.5, while scores−2 and2 map symmetrically around it. The curve illustrates the link function only; no labels were used to fit it.',
  syntax='z = intercept + sum(coefficient * feature)\nprobability = expit(z)\nodds = probability / (1 - probability)',
  figure=('The sigmoid converts linear log-odds into a bounded probability scale', 'The0.5 probability line meets log-odds zero. This is the mathematical link function, not evidence that a fitted model is calibrated.'))

L(1, '2. Fit logistic regression on actual Iris measurements',
  'Train a two-species model with a documented positive label and scaled inputs.',
  [('Binary Iris mapping', 'This separate exercise excludes setosa, codes versicolor as0 and virginica as1, and uses petal length/width in centimetres. It does not use cancellation labels.'),
   ('Logistic training pipeline', 'StandardScaler learns reference statistics on training inputs; LogisticRegression fits regularised log-odds from paired training labels. The pipeline reuses that representation at prediction.')],
  'Use the Iris data packaged with scikit-learn, which contains recorded botanical measurements rather than our simulated subscriptions. Keep only versicolor and virginica and state the new binary mapping before fitting. Petal length and width are two distinct centimetre measurements.\n\nSplit the paired rows with stratification, then fit scaling and the classifier on the training portion only. The held-out portion here is a development illustration, not the final subscription test and not a newly independent scientific benchmark after reading these results.\n\nInspect classes, coefficients and a few validation scores. Scaling changes coefficient units: the logistic coefficients now act per training-standard-deviation change in each input, holding the other supplied input fixed. A botanical association does not prove an intervention changes species. The next part converts those fitted changes into odds ratios and original-input slopes carefully.',
  IRIS_BINARY + 'print("Training/validation rows:", len(Xt), len(Xv))\nprint("Classes: 0=versicolor, 1=virginica:", m.classes_.tolist())\nprint("Scaled coefficients:", m.named_steps["logisticregression"].coef_[0].round(3).tolist())\nprint("First positive scores:", m.predict_proba(Xv)[:3, 1].round(3).tolist())',
  'Check that the scaler saw only the80training rows.',
  IRIS_BINARY + 'print("Scaler fit rows:", int(m.named_steps["standardscaler"].n_samples_seen_))\nprint("Final subscription test used: False")',
  'Confirm the input columns exclude the target and retain measurement units.',
  IRIS_BINARY + 'print("Inputs:", X.columns.tolist())\nprint("Target in inputs:", "target" in X.columns)',
  [('What does positive label1 mean in this Iris exercise?', 'Virginica among the two selected species', 'Cancellation', 'An unknown species', 'Each task has its own explicitly documented mapping.'),
   ('Where did the scaler learn its reference statistics?', 'Only the Iris training rows', 'All held-out subscription rows', 'The validation answers', 'Fitted preprocessing belongs inside the training boundary.')],
  'Reuse label meanings across unrelated datasets and fit scaling on every row first.', 'State each task’s labels, units and training-only preparation.',
  'The mask selects100recorded flowers, then80are used for fitting and20for development. Coefficients are in the standardised input space, not direct per-centimetre probability changes.')

L(1, '3. Interpret coefficients through conditional odds ratios',
  'Translate a fitted slope into an odds multiplier and state its representation.',
  [('Odds ratio; exp(coefficient)', 'In a binary logistic equation, increasing one supplied feature unit while holding the others fixed multiplies fitted odds by exp(coefficient). It does not multiply probability by that amount.'),
   ('Scaled-to-original coefficient', 'After StandardScaler, dividing a scaled coefficient by its fitted scale converts the log-odds slope to one original input unit. The intercept also changes under the transformation.')],
  'Suppose a fitted logistic coefficient is0.7 per standardised feature unit. A one-unit increase multiplies fitted odds by exp(0.7), about two. It does not double the probability: starting odds and the nonlinear sigmoid determine the resulting probability.\n\nFor the Iris pipeline, a scaled unit is one training standard deviation. To express a slope per centimetre, divide by the learned scaler scale for that column. Keep the other supplied feature fixed in either interpretation, and do not rank coefficient magnitudes across incompatible units without context.\n\nThe example reconstructs the raw-input log-odds equation and verifies its probabilities against the pipeline. This is an algebra check, not a causal conclusion. Petal measurements are related, regularisation affects coefficients, and only two selected species are represented. A large conditional odds multiplier is not proof that physically changing a measurement changes an organism’s species.',
  IRIS_BINARY + 'import numpy as np\nfrom scipy.special import expit\ns = m.named_steps["standardscaler"]\nlr = m.named_steps["logisticregression"]\nraw_coef = lr.coef_[0] / s.scale_\nraw_intercept = lr.intercept_[0] - np.dot(lr.coef_[0], s.mean_ / s.scale_)\nprint("Log-odds slopes per cm:", raw_coef.round(3).tolist())\nprint("Conditional odds multipliers per cm:", np.exp(raw_coef).round(3).tolist())\nmanual = expit(raw_intercept + Xv.to_numpy() @ raw_coef)\nprint("Raw equation matches pipeline:", bool(np.allclose(manual, m.predict_proba(Xv)[:, 1])))',
  'For coefficient log(2), show the effect on odds and probability starting from probability0.2.',
  'import numpy as np\np = 0.2\nodds = p / (1 - p)\nmultiplier = float(np.exp(np.log(2.0)))\nnew_odds = odds * multiplier\nprint("Old odds:", odds)\nprint("New odds:", new_odds)\nprint("New probability:", round(new_odds / (1 + new_odds), 3))',
  'List two qualifications for a coefficient statement in this exercise.',
  'for condition in ["other supplied input held fixed", "prediction association, not a causal intervention"]:\n    print(condition)',
  [('Does exp(coefficient) multiply odds or probability?', 'Odds', 'Probability directly', 'The number of observed rows', 'The coefficient is additive on log-odds and multiplicative on odds.'),
   ('Can a conditional fitted odds ratio establish a causal species change?', 'No', 'Always', 'Only when large', 'Model interpretation is not identification of a causal intervention.')],
  'Call exp(coefficient) a direct probability multiplier or a proven causal effect.', 'Name the input scale, conditional odds interpretation and evidence limits.',
  'The reconstructed raw equation compensates for both centring and scaling. Its agreement with the pipeline verifies the unit conversion while retaining the fitted model’s limited interpretation.')

L(1, '4. Control logistic complexity with C and convergence checks',
  'Explain inverse regularisation strength and inspect a small declared development comparison.',
  [('C; default L2 logistic regularisation', 'With the default L2 configuration used here, smaller positive C means stronger regularisation. C is not the same direction as Ridge alpha.'),
   ('log_loss preview', 'Log loss evaluates the probability assigned to observed labels; lower is better. It penalises confident mistakes heavily. The next part computes and explains its formula.'),
   ('max_iter; convergence', 'max_iter limits solver iterations; tol controls stopping tolerance. A convergence warning is unresolved fitting evidence, not a message to hide.')],
  'Logistic regression also regularises its fitted coefficients. In this configuration, C controls inverse strength: a smaller C puts more emphasis on the penalty. Do not carry over the Ridge-alpha direction from Week45 unchanged. Related inputs and weakly supported data can make regularisation particularly relevant.\n\nThe example compares three declared C values on the separate Iris development split. It prints coefficient size and validation log loss, which the next part explains in detail. This is development feedback, not a final subscription test result or proof that one C is universally best.\n\nFit the scaler inside each candidate pipeline and investigate convergence problems. Choosing a large max_iter does not repair an invalid feature contract or guarantee better probability estimates. The supplied examples use explicit iteration limits and treat unexpected warnings as authoring failures. More extensive searches belong inside a suitable development design rather than repeated final-test inspection.',
  IRIS_BINARY + 'import numpy as np\nfrom sklearn.metrics import log_loss\nfor C in [0.1, 1.0, 10.0]:\n    model = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=2000, tol=1e-7)).fit(Xt, yt)\n    coef = model.named_steps["logisticregression"].coef_[0]\n    print("C", C, "coefficient norm", round(float(np.linalg.norm(coef)), 3), "validation log loss", round(log_loss(yv, model.predict_proba(Xv), labels=[0, 1]), 3))',
  'Record the opposite strength directions of logistic C and Ridge alpha.',
  'controls = {"smaller logistic C": "stronger penalty", "larger Ridge alpha": "stronger penalty"}\nfor setting, effect in controls.items():\n    print(setting + ": " + effect)',
  'Inspect the fitted solver iteration count for the declared Iris pipeline.',
  IRIS_BINARY + 'print("Iterations:", m.named_steps["logisticregression"].n_iter_.tolist())\nprint("Configured limit:", m.named_steps["logisticregression"].max_iter)',
  [('Which change strengthens this logistic penalty?', 'Smaller positive C', 'Larger C always', 'Adding final test labels', 'C is inverse regularisation strength under this configuration.'),
   ('Should convergence warnings be suppressed to make a lesson look clean?', 'No; investigate them', 'Always', 'Only when accuracy is high', 'A warning can indicate an unresolved numerical or optimisation issue.')],
  'Assume C and Ridge alpha have identical meanings and tune them on final answers.', 'Read the estimator’s parameter definition and select settings within development.',
  'Every candidate gets the same Iris training and validation rows. The coefficients and score describe that candidate’s fit; no final subscription label is involved.')

L(1, '5. Log loss punishes confident wrong probabilities',
  'Compute binary log loss and distinguish its objective from accuracy.',
  [('Binary log loss; log_loss', 'For label y and positive score p, loss is−[y*log(p)+(1−y)*log(1−p)]. It rewards assigning higher probability to the observed label and heavily penalises confident mistakes.'),
   ('Probability assessment versus decisions', 'Two models can make the same thresholded decisions but have different log loss because their confidence differs. Regularised logistic fitting balances a log-loss objective with a penalty.')],
  'Accuracy sees only the chosen label. A probability assessment also asks how much probability the model assigned to the answer that actually occurred. Predicting a wrong label with near certainty receives a much larger log-loss penalty than a less confident error.\n\nThe tiny example compares probability vectors against the same two actual labels. It reports both thresholded accuracy and log loss. This is a metric illustration, not a fitted model evaluation. Do not compare log loss with a regression MAE number as if their units and meanings matched.\n\nLibrary implementations handle numerical limits to avoid directly taking log(0), but that does not make an extreme wrong prediction reliable. Keep labels explicit when evaluating very small subsets. A good development log loss alone does not establish perfect calibration or the right decision threshold; ranking, reliability and decision cost are related but different questions.',
  'import numpy as np\nfrom sklearn.metrics import log_loss, accuracy_score\ny = np.array([0, 1])\nfor name, p in {"reasonable": [0.1, 0.9], "one confidently wrong": [0.99, 0.99]}.items():\n    p = np.array(p)\n    print(name, "accuracy", accuracy_score(y, p >= 0.5), "log loss", round(log_loss(y, p, labels=[0, 1]), 3))',
  'Compare confidence levels when every thresholded decision is correct.',
  'from sklearn.metrics import log_loss\ny = [0, 1]\nprint("Cautious correct:", round(log_loss(y, [0.4, 0.6], labels=[0, 1]), 3))\nprint("Confident correct:", round(log_loss(y, [0.1, 0.9], labels=[0, 1]), 3))',
  'Calculate a single positive outcome’s negative-log probability for p=0.8.',
  'import numpy as np\nprint("Positive-case log loss:", round(float(-np.log(0.8)), 3))',
  [('Which error receives a large log-loss penalty?', 'Assigning near-zero probability to the observed label', 'A correct high-probability prediction', 'A low training row id', 'Log loss evaluates probability assigned to what actually happened.'),
   ('Can equal thresholded accuracy coexist with different log loss?', 'Yes', 'Never', 'Only for multiclass data', 'The confidence values retain information that hard labels discard.')],
  'Judge probability quality only from the fraction of hard labels correct.', 'Inspect a proper probability score and its evaluation setting as well as decisions.',
  'The confident-wrong vector assigns0.99 to a positive event even for the actual negative row. That small probability for the true negative label drives a large loss.')

L(1, '6. Probability calibration and ranking are separate',
  'Explain why a model probability is an estimate and why score ranking is insufficient.',
  [('Calibration', 'Among comparable cases receiving a probability near0.2, an adequately calibrated model would have an event frequency near0.2. This needs sufficient relevant evaluation data, not one observed outcome.'),
   ('ROC AUC; roc_auc_score preview', 'ROC AUC summarises positive-versus-negative score ranking, giving half credit to ties. It does not assess calibration. Day4 computes its pairwise meaning and curves in detail.'),
   ('brier_score_loss; monotonic score change', 'Binary Brier score averages squared differences between probability and0/1 outcomes. A strictly increasing score transformation can preserve ranking while changing Brier or log loss.')],
  'A probability describes a frequency claim across comparable cases, not certainty about one subscription. A model can rank cancellations above retentions well while systematically overstating their probability. Conversely, one probability score cannot be judged correct merely because one unlikely event did or did not happen.\n\nThe example sharpens an invented score vector with a strictly increasing logit transform. Its ordering stays the same, so ROC AUC stays the same, while Brier score changes. This demonstrates the distinction; four handpicked outcomes cannot certify calibration. Brier measures overall probability error and is not a pure isolated calibration measure.\n\nClass weighting and resampling in Day5 change fitting emphasis and can alter probability reliability under the natural population prevalence. Do not assume predict_proba is automatically a calibrated churn probability after those changes. Assess reliability on relevant untouched data and keep any fitted calibration procedure inside a proper development boundary.',
  'import numpy as np\nfrom scipy.special import expit\nfrom sklearn.metrics import roc_auc_score, brier_score_loss\ny = np.array([0, 1, 0, 1])\np = np.array([0.1, 0.4, 0.6, 0.9])\nsharp = expit(3 * np.log(p / (1 - p)))\nfor name, values in [("original", p), ("sharpened", sharp)]:\n    print(name, "ROC AUC", round(roc_auc_score(y, values), 3), "Brier", round(brier_score_loss(y, values), 3))',
  'Compute Brier score by hand for actual[0,1] and probabilities[0.2,0.8].',
  'import numpy as np\ny = np.array([0.0, 1.0])\np = np.array([0.2, 0.8])\nprint("Brier:", round(float(((p - y) ** 2).mean()), 3))',
  'State why a single cancelled customer cannot validate a predicted probability0.1.',
  'print("One binary outcome is not a frequency estimate")\nprint("Assess many relevant cases and the probability groups they received")',
  [('Does a strong ROC AUC guarantee calibrated probability values?', 'No', 'Always', 'Only for logistic regression', 'Ranking can remain unchanged while probability scale is distorted.'),
   ('Can four handpicked outcomes certify population calibration?', 'No', 'Always', 'Only if Brier is small', 'Calibration assessment needs adequate relevant evaluation evidence.')],
  'Call every predict_proba output a verified personal risk and every good ranking calibrated.', 'Assess ranking, probability quality and decision policy separately.',
  'The same sample ordering gives the same AUC under both score scales. Their different squared probability errors show information that ranking alone does not capture.')
