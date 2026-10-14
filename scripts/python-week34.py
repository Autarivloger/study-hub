"""Add Week 34 without rewriting prior lessons; execute and embed real charts."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DAYS = {f"34.{d}": {"parts": []} for d in range(6)}
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def chart(body):
    return 'import matplotlib.pyplot as plt\nimport numpy as np\nimport pandas as pd\n' + clean(body) + '\nfig.savefig("chart.png", dpi=110)\nplt.close(fig)\n'


def section(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def evaluated(code, image=None):
    target = section("out", "")
    JOBS.append((clean(code), target, image))
    return target


def lesson(day, title, goal, terms, explanation, syntax, example, walkthrough,
           mistake, task, solution, challenge, challenge_code, takeaway, quizzes):
    parts = DAYS[f"34.{day}"]["parts"]
    index = len(parts)
    picture = section("figure", src="", alt=title + ": executed example chart",
        note="Actual chart from the example. Read the axes and units, then compare the shape with the printed values. Running this example in a fresh practice folder saves chart.png.")
    questions = []
    for i, (q, answer, wrong1, wrong2, why) in enumerate(quizzes):
        correct = (index + i) % 3
        options = [answer, wrong1, wrong2]
        for _ in range(correct):
            options.insert(0, options.pop())
        questions.append({"q": q, "options": options, "correct": correct, "why": why})
    parts.append({"title": title, "sections": [
        section("h", title), section("key", "Learning objective: " + goal),
        *[section("new", name, note=note) for name, note in terms],
        section("p", explanation), section("syn", syntax, note="Pattern only; the complete example follows."),
        section("code", clean(example)), evaluated(example, picture), picture, section("p", walkthrough),
        section("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        section("ex", task, practiceId=f"34.{day}.{index}.build"),
        section("sol", code=clean(solution), out="", why="Build check: " + takeaway),
        section("ex", "Mini challenge: " + challenge, practiceId=f"34.{day}.{index}.challenge"),
        section("sol", code=clean(challenge_code), out="", why="Challenge check: " + takeaway),
        section("try", q=quizzes[0][0], code="# Predict first; explain your reason before revealing.", a=quizzes[0][1], why=quizzes[0][4]),
        section("checkpoint", lesson={"id": f"course:34.{day}.{index}", "quiz": questions}), section("key", takeaway)
    ]})
    for s in parts[-1]["sections"]:
        if s["t"] == "sol":
            JOBS.append((s["code"], s, None))


import csv
import io
RAW_BYTES=(ROOT/"docs"/"python-week34"/"penguins.csv").read_bytes()
records=list(csv.DictReader(io.StringIO(RAW_BYTES.decode("utf-8"))))
excerpt=[]
for species in ["Adelie","Chinstrap","Gentoo"]:
    excerpt.extend([row for row in records if row["species"]==species][:4])
buffer=io.StringIO(); writer=csv.DictWriter(buffer,fieldnames=list(records[0]),lineterminator="\n");writer.writeheader();writer.writerows(excerpt)
EXCERPT=buffer.getvalue()
NUMERIC=["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g","year"]
RAW_SETUP='import io\nraw=pd.read_csv(io.StringIO('+repr(EXCERPT)+'),dtype="string",keep_default_na=False)\n'
DATA_SETUP=RAW_SETUP+'df=raw.replace("NA",pd.NA)\nfor col in '+repr(NUMERIC)+':\n    df[col]=pd.to_numeric(df[col],errors="raise")\ndf["_source_record"]=np.arange(1,len(df)+1)\n'


def example(body):
    return chart(DATA_SETUP+clean(body))


lesson(0,"1. Start with a question, a unit and a denominator",
    "Frame an answerable descriptive question before choosing a chart.",
    [("EDA; analysis question", "Exploratory Data Analysis examines structure, quality and patterns using numerical and graphical evidence. It can generate questions; it does not automatically confirm an explanation."),
     ("Unit; target; denominator", "A row here records a penguin observation in the source, not an island average. The target statement must specify recorded birds, available measurements and the relevant denominator; this simplified file does not supply bird identity metadata to verify every sampling assumption."),
     ("Real excerpt versus full project", "Early examples use twelve real source rows: four from each species. The downloadable project uses all344 rows. Excerpt summaries must not be presented as the full sample's findings.")],
    "Weeks27–33 supplied arrays, tables, cleaning, charts and statistics. Now connect them into one reproducible investigation. Ask how recorded body mass differs between species, among rows with known mass. "
    "That is different from asking whether a species causes a mass difference or whether an island makes birds heavier. The first question is descriptive; the latter claims require a suitable design. "
    "Write the unit, measurement, grouping, inclusion rule and scope before calculating. Keep all source rows for an audit even when one chart uses only complete coordinates. "
    "The Palmer Penguins data has real measurements with unknown values. This week treats those unknowns as information to report, not as zeros to fill for convenience.",
    'known=df.loc[df["body_mass_g"].notna()]\nsummary=known.groupby("species")["body_mass_g"].agg(["count","mean"])',
    example('summary=df.groupby("species")["body_mass_g"].agg(["count","mean"])\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(summary.index,summary["mean"]); ax.set(ylabel="Mean known mass (g)",title="Twelve-row walkthrough, not full344-row result")\nprint("Source rows:",len(df),"Known mass:",int(df["body_mass_g"].notna().sum()))\nprint(summary.round(2).to_dict())'),
    "count counts known mass, not every species row. The chart's population is this explicit twelve-row excerpt. The full-project result is produced separately from the retained344-row file.",
    ('# Call a species-group mean the causal effect of island', '# Describe known mass among the recorded species groups', "A grouped comparison does not isolate an island or species intervention."),
    "For the excerpt, count rows per species and known mass per species. Draw known counts and print both denominators.",
    example('rows=df.groupby("species").size(); known=df.groupby("species")["body_mass_g"].count()\nfig,ax=plt.subplots(); ax.bar(known.index,known.values); ax.set_ylabel("Known mass rows")\nprint("All:",rows.to_dict(),"Known:",known.to_dict())'),
    "Change the question to median known mass by species; draw medians and print the unit and retained count.",
    example('med=df.groupby("species")["body_mass_g"].median()\nfig,ax=plt.subplots(); ax.bar(med.index,med.values); ax.set_ylabel("Median mass (g)")\nprint("Unit:g; known rows:",int(df["body_mass_g"].notna().sum()))'),
    "Define the question and represented observations before drawing; distinguish descriptive comparisons from causal claims.",
    [("Which denominator belongs to a known-mass mean?","Rows with known mass","All possible Antarctic birds","Only the heaviest birds","Unknown mass does not contribute a measured value."),
     ("Do the early twelve rows represent the full344-row result?","No","Always","Only if plotted as bars","The walkthrough is an explicitly labelled excerpt.")])

lesson(0,"2. A data dictionary is part of the analysis",
    "Classify fields by meaning, units and permissible operations.",
    [("Data dictionary", "A dictionary records what each column means, its unit, valid values, unknown tokens and the observation scope. Storage dtype is evidence about representation, not a complete semantic description."),
     ("Identifier versus measurement", "A numeric year is a collection-period label, not a physical measurement to average into a biological result. Generated row labels identify source positions, not verified individual birds.")],
    "This file has species, island, bill length/depth in millimetres, flipper length in millimetres, body mass in grams, recorded sex and year. "
    "Changing grams to kilograms requires division by1000 and a matching label. Adding bill length to body mass is not meaningful simply because both columns are numeric. "
    "Species and island are related in the collection: not every species is recorded on every island. Missing category combinations therefore matter before an island comparison. "
    "Read SOURCE.md in the project for provenance and scope. The simplified table omits much raw collection metadata; do not infer independent identity from a new row number.",
    'dictionary={"body_mass_g":"Known body mass in grams","year":"Recorded collection year"}',
    example('known=df["body_mass_g"].dropna(); kg=known/1000\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.hist(kg.to_numpy(dtype=float),bins=5); ax.set(xlabel="Body mass (kg)",ylabel="Excerpt records",title="A declared unit conversion")\nprint("First known grams/kg:",float(known.iloc[0]),float(kg.iloc[0]))\nprint("Year labels:",sorted(df["year"].unique().tolist()))'),
    "The conversion changes the displayed scale, not the birds. A year label is kept as a category of collection time; averaging it would not answer a biological measurement question.",
    ('df["size"]=df["body_mass_g"]+df["bill_length_mm"]', 'df["body_mass_kg"]=df["body_mass_g"]/1000', "Use compatible quantities and state any transformation's unit."),
    "Convert known flipper lengths to centimetres, plot a histogram and print the first conversion.",
    example('mm=df["flipper_length_mm"].dropna(); cm=mm/10\nfig,ax=plt.subplots(); ax.hist(cm.to_numpy(dtype=float),bins=5); ax.set_xlabel("Flipper length (cm)")\nprint(float(mm.iloc[0]),float(cm.iloc[0]))'),
    "Count the excerpt's recorded year labels without treating them as a body-size measurement.",
    example('counts=df["year"].value_counts().sort_index()\nfig,ax=plt.subplots(); ax.bar(counts.index.astype(str),counts.values); ax.set_ylabel("Recorded rows")\nprint(counts.to_dict())'),
    "Document meaning and units; numeric storage does not make every arithmetic operation meaningful.",
    [("What does a generated source row label establish?","A position in this snapshot","Verified independent bird identity","A biological measurement","Identity metadata is not created by numbering rows."),
     ("How do grams become kilograms?","Divide by1000 and update the label","Multiply by1000","Only rename the axis","The numbers and stated units must agree.")])

lesson(0,"3. Turn five questions into an evidence plan",
    "Map each question to variables, exclusions and a useful visual.",
    [("Question-to-evidence plan", "For each question list columns, unit, inclusion rule, summary/chart and a limitation. This makes later choices reviewable instead of letting attractive plots dictate the investigation."),
     ("Exploration register", "Record initial questions and later discoveries separately. A hypothesis suggested by the same inspected data is exploratory; it is not retrospectively a preregistered confirmation.")],
    "Use five starting questions: how much data is known; how mass varies; how flipper length and mass relate; how species/sex groups differ; and which island comparisons have actual overlap. "
    "A count chart answers coverage, a histogram describes one numeric variable, a scatter describes complete pairs, grouped summaries describe category comparisons, and a support table exposes absent combinations. "
    "Write exclusions per question. Mass-only summaries need not discard a bird merely because recorded sex is unknown. A sex-stratified mass comparison needs both fields. "
    "Questions can change as you inspect data, but the register should show when and why. EDA is valuable for generating leads without pretending that every lead was planned before seeing the observations.",
    'plan=[{"question":"Mass by species","columns":["species","body_mass_g"],"exclude":"Unknown mass"}]',
    example('cols=["body_mass_g","flipper_length_mm","bill_length_mm","bill_depth_mm"]\ncounts=df[cols].notna().sum()\nfig,ax=plt.subplots(figsize=(7,3.5),layout="constrained"); ax.barh(counts.index,counts.values); ax.set(xlabel="Known excerpt records",title="Question1: available measurement evidence")\nprint("Possible source rows:",len(df))\nprint(counts.to_dict())'),
    "These counts describe available fields, not the number of independent plants you can prove from identity metadata. The chart tells you which questions have measured inputs.",
    ('# Start by producing every plot and choose a story afterward', '# Save five questions with denominators, then record later exploratory changes', "An evidence plan reduces hidden outcome-driven choices."),
    "For mass versus flipper length, count complete pairs and excluded rows; draw only the complete pairs.",
    example('valid=df[["body_mass_g","flipper_length_mm"]].notna().all(axis=1); part=df.loc[valid]\nfig,ax=plt.subplots(); ax.scatter(part["flipper_length_mm"],part["body_mass_g"]); ax.set(xlabel="Flipper mm",ylabel="Mass g")\nprint(int(valid.sum()),int((~valid).sum()))'),
    "For sex-stratified mass, count rows with both values and contrast that with the mass-only count.",
    example('mass=df["body_mass_g"].notna(); both=df[["body_mass_g","sex"]].notna().all(axis=1)\nfig,ax=plt.subplots(); ax.bar(["Mass known","Mass+sex known"],[int(mass.sum()),int(both.sum())])\nprint(int(mass.sum()),int(both.sum()))'),
    "Choose evidence and exclusions by question, and distinguish planned analyses from data-suggested exploration.",
    [("Must a mass-only summary exclude every unknown-sex row?","No","Always","Only on Tuesdays","Sex is not required for that particular question."),
     ("What should happen when a new pattern suggests a question?","Record it as exploratory","Pretend it was preplanned","Delete the old plan","The investigation can evolve transparently.")])

lesson(0,"4. Freeze the source and define a reproducible run",
    "Separate raw input, derived data, decisions and a fresh report bundle.",
    [("Provenance; source hash", "Provenance records where a snapshot came from and which bytes were used. SHA-256 detects byte differences; it does not prove data accuracy, authorship or independence."),
     ("Raw/derived/output layers", "Keep a read-only raw snapshot, a typed derived table and a new output directory for each run. A transformation log explains decisions; a second run must not silently replace the first.")],
    "A reproducible report starts before plotting. Retain the source CSV, its pinned repository revision, licence and hash. Store code and analysis choices alongside it. "
    "Use a fresh destination such as eda-run-01, then eda-run-02. The project later refuses an existing bundle and stages its own temporary output before publication. "
    "Hash equality means byte equality for this check; it cannot certify that an unknown measurement is correct or that a source's collection process suits your question. "
    "This continues the Week29 audited-pipeline approach. Reuse its ideas—raw preservation, explicit validation and a decision log—rather than calling its student-score-specific schema on a different penguin dataset.",
    'digest=hashlib.sha256(raw_bytes).hexdigest()\n# Write derived outputs into a new destination.',
    chart(RAW_SETUP+'import hashlib\ntext=raw.to_csv(index=False,lineterminator="\\n"); before=hashlib.sha256(text.encode()).hexdigest(); changed=raw.copy(); changed.loc[0,"body_mass_g"]="4000"\nafter=hashlib.sha256(changed.to_csv(index=False,lineterminator="\\n").encode()).hexdigest()\nfig,ax=plt.subplots(); ax.bar(["Original excerpt","Changed copy"],[len(raw),len(changed)]); ax.set_ylabel("Rows (same count, changed bytes)")\nprint("Same row count:",len(raw)==len(changed))\nprint("Same byte digest:",before==after)'),
    "The hash is of a normalised excerpt export here, not the pinned full-file digest. Equal shape does not imply equal contents; SOURCE.md records the full raw-file fingerprint separately.",
    ('raw.to_csv("penguins.csv",index=False)  # overwrite the evidence', 'derived.to_csv("eda-run-01/cleaned.csv",index=False)', "Keep raw observations available and write derived artifacts to an explicitly owned destination."),
    "Copy a table before changing one mass value; prove the original token remains unchanged and plot original/copy values.",
    chart(RAW_SETUP+'changed=raw.copy(); changed.loc[0,"body_mass_g"]="4000"\nfig,ax=plt.subplots(); ax.bar(["Original","Derived copy"],[float(raw.loc[0,"body_mass_g"]),float(changed.loc[0,"body_mass_g"])])\nprint("Original preserved:",raw.loc[0,"body_mass_g"]=="3750")'),
    "Compute an excerpt byte hash twice without changing the bytes and print that they match.",
    chart(RAW_SETUP+'import hashlib\nblob=raw.to_csv(index=False).encode(); one=hashlib.sha256(blob).hexdigest(); two=hashlib.sha256(blob).hexdigest()\nfig,ax=plt.subplots(); ax.bar(["First","Second"],[len(blob),len(blob)])\nprint(one==two)'),
    "Reproducibility preserves bytes, code and decisions; a matching digest alone is not a data-quality guarantee.",
    [("What does a matching source hash check?","Matching bytes","Guaranteed correct measurements","A random sampling design","Source validity needs additional evidence."),
     ("Should Week29's student schema be applied unchanged to penguins?","No; reuse the pattern with the right schema","Always","Only if pandas accepts it","Reusable principles do not make different column contracts identical.")])

lesson(1,"1. Read raw tokens before making assumptions",
    "Distinguish a documented unknown token from an invalid measurement.",
    [("dtype='string'; keep_default_na=False", "Read raw fields as strings and disable automatic NA guessing to preserve exact source tokens. Then apply the source's documented NA convention explicitly."),
     ("Schema and parser agreement", "Check the exact header, unique field names, row widths and row count before relying on inferred types. A successful read_csv call alone does not prove that rows were parsed as intended.")],
    "An automatic parser can turn a literal token into missingness or infer a category code as a number. Preserving raw strings lets you inspect those decisions. "
    "This source documents NA as unknown. That is distinct from a typo such as 'heavy', an impossible negative measurement or an empty required category. "
    "The project validates eight exact columns and row widths, then explicitly converts the four measurements and year. It logs counts without changing the source snapshot. "
    "Strictness here is deliberate: unexpected tokens stop the project for review instead of being silently coerced to unknown. Later cleaning examples add fictional dirty tokens to demonstrate the distinction; they are not edits to the public dataset.",
    'raw=pd.read_csv(path,dtype="string",keep_default_na=False)\nunknown=raw.eq("NA")',
    chart(RAW_SETUP+'counts=raw.eq("NA").sum()\nfig,ax=plt.subplots(figsize=(7,3.5),layout="constrained"); ax.barh(counts.index,counts.values); ax.set(xlabel="Literal NA tokens",title="Preserved raw excerpt tokens")\nprint("Fields:",raw.columns.tolist())\nprint("All raw columns are strings:",all(isinstance(t,pd.StringDtype) for t in raw.dtypes))'),
    "The histogram-like bar chart counts the documented token, not every possible invalid value. The later validator must still inspect non-NA numeric fields.",
    ('pd.to_numeric(raw["body_mass_g"],errors="coerce")  # silently equate typos and NA', 'tokens=raw["body_mass_g"].replace("NA",pd.NA)\nvalues=pd.to_numeric(tokens,errors="raise")', "Separate documented unknowns from malformed values before conversion."),
    "Count literal NA values in mass and sex before conversion and plot their counts.",
    chart(RAW_SETUP+'counts=raw[["body_mass_g","sex"]].eq("NA").sum()\nfig,ax=plt.subplots(); ax.bar(counts.index,counts.values)\nprint(counts.to_dict())'),
    "Show that raw mass tokens remain strings after a converted copy is made; print the first token and converted number.",
    chart(RAW_SETUP+'converted=pd.to_numeric(raw["body_mass_g"].replace("NA",pd.NA),errors="raise")\nfig,ax=plt.subplots(); ax.hist(converted.dropna().to_numpy(dtype=float),bins=5)\nprint(type(raw.iloc[0]["body_mass_g"]).__name__,raw.iloc[0]["body_mass_g"],float(converted.iloc[0]))'),
    "Preserve tokens, check parsing, and make unknown-versus-invalid handling explicit.",
    [("Does errors='coerce' distinguish a typo from documented NA?","Not by itself","Always","Only for sex","Both can become missing unless token evidence is retained."),
     ("Why initially preserve strings?","To inspect source tokens and conversion rules","To prohibit arithmetic forever","To make all rows independent","The raw layer should retain what the source actually supplied.")])

lesson(1,"2. Profile every field with the correct kind of summary",
    "Build a first-look ledger covering numeric and categorical columns.",
    [("Profile ledger", "A compact profile records dtype, row count, known count, unknown count and distinct known values for each field. Numeric ranges and category vocabularies add semantic checks."),
     ("describe is a starting point", "DataFrame.describe gives useful summaries but does not know your field meanings, unit contract, parsing errors or target population. Inspect numeric and categorical fields deliberately.")],
    "A first look should not stop after head. Inspect every column and reconcile counts: known plus unknown must equal source rows for each field. "
    "For numeric measurements use count, centre, spread and range. For species/island/sex use frequencies and a known-value vocabulary. For year inspect collection labels. "
    "A profile can expose missing measurements and unexpected categories before an attractive chart hides them. It cannot establish the reason values are missing or the independence of birds. "
    "Write the ledger to the final report so another reader can see which evidence supported each calculation.",
    'profile=pd.DataFrame({"known":df[cols].notna().sum(),"unknown":df[cols].isna().sum()})',
    example('cols=raw.columns.tolist(); profile=pd.DataFrame({"known":df[cols].notna().sum(),"unknown":df[cols].isna().sum(),"distinct_known":df[cols].nunique(dropna=True)})\nfig,ax=plt.subplots(figsize=(7,3.5),layout="constrained"); ax.barh(profile.index,profile["known"]); ax.set(xlabel="Known excerpt records",title="Every source field has a ledger")\nprint("Counts reconcile:",bool((profile["known"]+profile["unknown"]).eq(len(df)).all()))\nprint(profile.to_dict())'),
    "The generated _source_record is intentionally excluded from the source-field profile. Its uniqueness would be a property of our numbering rather than an independently validated specimen key.",
    ('# Inspect only numeric describe and assume all categories are valid', '# Combine numeric ranges, category vocabularies and a missingness ledger', "A table can have plausible numeric summaries and still contain category or identity problems."),
    "Profile known/unknown counts for all four measurements; plot unknown counts and print that every denominator reconciles.",
    example('cols=["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]; known=df[cols].notna().sum(); unknown=df[cols].isna().sum()\nfig,ax=plt.subplots(); ax.barh(cols,unknown.values)\nprint(bool((known+unknown).eq(len(df)).all()))'),
    "Print known species and island vocabularies; plot species frequencies without treating the counts as a census.",
    example('counts=df["species"].value_counts()\nfig,ax=plt.subplots(); ax.bar(counts.index,counts.values)\nprint(sorted(df["species"].dropna().unique().tolist()),sorted(df["island"].dropna().unique().tolist()))'),
    "Profile all fields according to meaning and reconcile every known/unknown denominator.",
    [("What should known plus unknown equal per field?","Source row count","Number of charts","The population size automatically","Every represented source row belongs to one of the two states."),
     ("Can describe alone validate sampling design?","No","Always","Only for numeric fields","It summarises values, not the collection mechanism.")])

lesson(1,"3. Missingness patterns are evidence, not a mechanism diagnosis",
    "Inspect which fields are unknown together without claiming why.",
    [("Missingness pattern; co-missingness", "A row-level indicator matrix shows which variables are known or unknown together. Shared gaps can suggest questions about collection or processing, but cannot alone identify a missing-data mechanism."),
     ("Complete-case scope", "Dropping every row with any unknown value changes the represented set. It can discard known mass simply because sex is unknown; choose exclusions by the actual analysis question.")],
    "In the full file, two rows lack the four measurements and eleven lack recorded sex. These counts differ, so one blanket dropna call is not a neutral cleanup. "
    "Inspect a missingness matrix and grouped counts. Then ask the source documentation or collection team about plausible reasons. "
    "You cannot prove missing-completely-at-random, missing-at-random or missing-not-at-random from a heatmap alone. Those are assumptions about relationships involving observed and unobserved information. "
    "Keep the unknown rows in the cleaned table; select the required-known subset separately for each summary and disclose how many rows were excluded.",
    'missing=df[cols].isna()\ncomplete=df.dropna(subset=required_for_question)',
    example('cols=["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g","sex"]; missing=df[cols].isna()\nfig,ax=plt.subplots(figsize=(7,3.5),layout="constrained"); ax.imshow(missing.to_numpy(dtype=int),aspect="auto",cmap="Greys",vmin=0,vmax=1); ax.set(xticks=np.arange(len(cols)),xticklabels=cols,ylabel="Excerpt row",title="Dark means unknown, not zero"); ax.tick_params(axis="x",labelrotation=20)\nprint("Rows with any unknown:",int(missing.any(axis=1).sum()))'),
    "The pattern shows co-occurrence of unknown fields. It does not explain the cause of their absence or justify replacing them with a species mean.",
    ('df=df.dropna()  # call every excluded row invalid', 'mass_rows=df.loc[df["body_mass_g"].notna()]  # retain other known information', "Missingness is analysis-specific, not proof that an entire record is invalid."),
    "Compare the excerpt's mass-only known count with complete rows across all original eight fields.",
    example('mass=int(df["body_mass_g"].notna().sum()); complete=int(df[raw.columns.tolist()].notna().all(axis=1).sum())\nfig,ax=plt.subplots(); ax.bar(["Known mass","All fields known"],[mass,complete])\nprint(mass,complete)'),
    "Show a hypothetical table with known mass but unknown sex; count how many usable masses a global dropna would discard.",
    chart('df=pd.DataFrame({"mass":[3000,4000,5000],"sex":["female",None,"male"]}); lost=int(df["mass"].notna().sum()-len(df.dropna()))\nfig,ax=plt.subplots(); ax.bar(["Known mass","Global complete rows"],[3,len(df.dropna())])\nprint("Usable masses discarded:",lost)'),
    "Document missingness and subset rules; an observed pattern cannot prove the mechanism behind unknown values.",
    [("Can a missingness heatmap prove MCAR?","No","Always","Only with few unknowns","The mechanism involves assumptions beyond the displayed pattern."),
     ("Must unknown sex invalidate a known mass?","No","Always","Only for Gentoo","The needed fields depend on the question.")])

lesson(1,"4. Register hypotheses and inspect duplicate candidates",
    "Keep evidence-generating observations separate from specimen identity claims.",
    [("Candidate duplicate; identity evidence", "Identical feature values can occur for different birds. duplicated marks value equality under selected columns; without an appropriate source key it does not establish that two records are one specimen."),
     ("Hypothesis ledger", "Record an idea, supporting observation, alternative explanations and a future check. A pattern found in these rows is an exploratory lead; avoid selecting a threshold solely to make its p-value smaller.")],
    "Possible leads include larger average Gentoo mass, mass/flipper association, sex-related subgroup differences, island/species overlap limitations and missingness variation. "
    "Each lead needs alternatives: species composition, collection context, unknown outcomes or unequal subgroup counts may explain a pooled pattern. "
    "When two rows match, retain them unless source identity evidence supports deduplication. Generated row numbers help trace decisions but cannot create that identity evidence. "
    "In the final report, a genuine observed subgroup difference is still descriptive and conditional on available measurements. Treat future confirmation as a new design task rather than retroactively declaring these observations a randomised study.",
    'candidate=df.duplicated(subset=measurement_columns,keep=False)\n# Review identities; do not delete solely because features match.',
    chart('df=pd.DataFrame({"source_row":[1,2,3],"mass_g":[3500,3500,4200],"flipper_mm":[190,190,205]}); flags=df.duplicated(["mass_g","flipper_mm"],keep=False)\nfig,ax=plt.subplots(); ax.scatter(df["flipper_mm"],df["mass_g"]); ax.set(xlabel="Flipper mm",ylabel="Mass g",title="Equal coordinates can conceal multiple records")\nprint("Matching-value candidates:",int(flags.sum()))\nprint("Records retained:",len(df))'),
    "The first two records share a plotting position and feature values. The table still contains three records; no specimen identity proof has been supplied.",
    ('df=df.drop_duplicates(measurement_columns)  # assume identical birds', '# Flag equal-value candidates and seek source identity evidence', "Deduplication needs a justified key and policy, not just matching measurements."),
    "Construct three rows with two equal masses but different source labels; print candidate count and retain all three.",
    chart('df=pd.DataFrame({"row":[1,2,3],"mass":[3000,3000,4500]}); flags=df.duplicated(["mass"],keep=False)\nfig,ax=plt.subplots(); ax.bar(df["row"].astype(str),df["mass"])\nprint(int(flags.sum()),len(df))'),
    "For the real excerpt, print the species mass medians as an exploratory lead and explicitly label the comparison descriptive.",
    example('med=df.groupby("species")["body_mass_g"].median()\nfig,ax=plt.subplots(); ax.bar(med.index,med.values); ax.set_ylabel("Median known mass (g)")\nprint(med.to_dict())\nprint("Descriptive excerpt lead, not a causal effect")'),
    "Register promising patterns and identity uncertainties; do not turn observations into unsupported confirmation or deletions.",
    [("What does duplicated prove without an identity key?","Value equality under selected columns","Same individual bird","Collection independence","Equal rounded measurements can belong to different specimens."),
     ("How should a data-suggested hypothesis be labelled?","Exploratory","Preregistered automatically","Causal proof","The discovery process must remain visible.")])

lesson(2,"1. A cleaning pipeline returns evidence, not just a table",
    "Separate raw, converted and analysis layers and reconcile their row counts.",
    [("Pure transformation; copy", "A transformation can take raw tokens and return a new table plus decisions, leaving the input unchanged. This makes before/after checks possible and reduces accidental overwrites."),
     ("Row reconciliation", "Track source, retained, rejected and intentionally excluded counts. If no row deletion was authorised, the cleaned table must retain every source row, including partially unknown records.")],
    "Week29's student-score pipeline was specific to its schema. Reuse its structure, not its column names or rejection rules. "
    "For penguins, convert documented NA tokens, inspect valid categories and positive finite measurements, keep all source rows, and create per-question subsets later. "
    "A cleaning function should return the table and an audit record. Assertions can enforce a row count or source-position invariant, but a passing assertion does not establish that measurements are biologically correct. "
    "The source is already a simplified research table. Honest cleaning may consist mainly of explicit typing and missingness retention; there is no need to invent repairs to make a project seem impressive.",
    'cleaned=raw.copy()\nassert len(cleaned)==len(raw)\n# Return cleaned data and the decision ledger.',
    chart(RAW_SETUP+'cleaned=raw.replace("NA",pd.NA).copy(); cleaned["body_mass_g"]=pd.to_numeric(cleaned["body_mass_g"],errors="raise")\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(["Raw rows","Typed rows"],[len(raw),len(cleaned)]); ax.set_ylabel("Retained records")\nprint("Rows preserved:",len(cleaned)==len(raw))\nprint("Original NA token retained:",raw.loc[3,"body_mass_g"]=="NA")'),
    "The original fourth excerpt mass remains the literal source token. Its derived missing value does not imply a deleted bird. Row retention is a declared invariant.",
    ('raw["body_mass_g"]=pd.to_numeric(raw["body_mass_g"],errors="coerce")', 'cleaned=raw.copy()\ncleaned["body_mass_g"]=pd.to_numeric(cleaned["body_mass_g"].replace("NA",pd.NA),errors="raise")', "Preserve original tokens and separate a validated derived representation."),
    "Make a typed mass copy, print source/typed row counts and verify raw dtypes are still strings.",
    chart(RAW_SETUP+'cleaned=raw.copy(); cleaned["body_mass_g"]=pd.to_numeric(cleaned["body_mass_g"].replace("NA",pd.NA))\nfig,ax=plt.subplots(); ax.hist(cleaned["body_mass_g"].dropna().to_numpy(dtype=float),bins=5)\nprint(len(raw),len(cleaned),isinstance(raw["body_mass_g"].dtype,pd.StringDtype))'),
    "Flag all rows with unknown mass but retain them; print flagged and retained counts.",
    example('flags=df["body_mass_g"].isna()\nfig,ax=plt.subplots(); ax.bar(["Known","Unknown"],[int((~flags).sum()),int(flags.sum())])\nprint(int(flags.sum()),len(df))'),
    "Reuse pipeline structure with a dataset-specific contract and explicit evidence for every row change.",
    [("Must meaningful cleaning delete some rows?","No","Always","Only on a real dataset","Typing and documented missingness handling can be the justified changes."),
     ("What should remain available after conversion?","Original tokens and decisions","Only a chart","Only the first row","Raw preservation allows an audit of derived values.")])

lesson(2,"2. Normalise categories only under a documented rule",
    "Trim known formatting differences without guessing unknown labels.",
    [("Normalisation versus semantic repair", "Removing surrounding whitespace or casefolding under an approved category rule changes formatting. Guessing that an unfamiliar label means a known category changes meaning and needs evidence."),
     ("Change ledger", "For each edited token retain source position, column, old token, new token and rule. Documented NA conversion is a missingness decision, not a recovered measurement.")],
    "The real source uses canonical species, island and sex labels. A teaching fixture can show how to handle ' Male ' under a declared case/whitespace rule while refusing 'maybe'. "
    "Normalisation must not silently collapse distinct identifiers or invent a sex label from measurements. Unknown is not a third measured sex category; it is a source evidence state. "
    "The project records whitespace changes, explicit sex casefolding and documented NA conversion. Unrecognised categories stop the run for review. "
    "A chart may display unknowns as 'Unknown' for readability, but the cleaned data keeps the underlying missing value so later code can distinguish it from known labels.",
    'normalised=token.str.strip().str.casefold()\nvalid=normalised.isin(["female","male"])|normalised.isna()',
    chart('tokens=pd.Series([" Male ","female","NA","maybe"],dtype="string"); normal=tokens.str.strip().replace("NA",pd.NA).str.casefold(); bad=normal.notna()&~normal.isin(["female","male"])\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(["Known label","Unknown","Review invalid"],[int((normal.notna()&~bad).sum()),int(normal.isna().sum()),int(bad.sum())]); ax.set_ylabel("Fictional tokens")\nprint("Invalid tokens:",tokens[bad].tolist())\nprint("First normalised:",normal.iloc[0])'),
    "The fictitious 'maybe' token is not converted into a biological label or silently lost. The real-source snapshot remains unchanged.",
    ('sex=sex.fillna("female")  # guess a missing category', 'display=sex.fillna("Unknown")  # display only; retain missing in the cleaned table', "Presentation labels must not become invented source observations."),
    "Normalise [' male','FEMALE ','NA'] under the declared rule and plot known/unknown counts.",
    chart('tokens=pd.Series([" male","FEMALE ","NA"],dtype="string"); normal=tokens.str.strip().replace("NA",pd.NA).str.casefold()\nfig,ax=plt.subplots(); ax.bar(["Known","Unknown"],[int(normal.notna().sum()),int(normal.isna().sum())])\nprint(normal.fillna("<unknown>").tolist())'),
    "Compare source and trimmed tokens ['Adelie',' Adelie ']; count changed strings without claiming they are duplicate specimens.",
    chart('raw=pd.Series(["Adelie"," Adelie "],dtype="string"); fixed=raw.str.strip(); changed=raw.ne(fixed)\nfig,ax=plt.subplots(); ax.bar(["Unchanged","Trimmed"],[int((~changed).sum()),int(changed.sum())])\nprint(int(changed.sum()))'),
    "Normalise justified formatting, preserve original tokens and stop on unknown meanings rather than guessing.",
    [("What justifies mapping 'maybe' to a known sex?","Additional evidence, not convenience","Any parser default","A heavier body mass","A category cannot be inferred safely from a desire for complete data."),
     ("Should a display label Unknown replace the raw evidence?","No","Always","Only for bars","Keep source and derived missingness separate from presentation.")])

lesson(2,"3. Numeric conversions need a token-level rejection check",
    "Distinguish finite positive measurements, documented unknowns and invalid values.",
    [("Coercion audit", "errors='coerce' is useful diagnostically only when newly missing values are compared with documented unknown tokens. Otherwise malformed values disappear into the same missing state."),
     ("Finite-value and unit checks", "Numeric parsing may accept infinity or scientifically implausible values. np.isfinite rejects nonfinite measurements; positivity is a declared physical-measurement contract, not a general rule for every numeric variable.")],
    "A mass token can be known, documented NA or invalid. A robust pipeline distinguishes all three before analysis. "
    "This project accepts documented NA for measurements and sex, requires a known collection year and known species/island, and rejects malformed, nonfinite or nonpositive measurements. "
    "It does not use an IQR fence as a biological validity rule. An extreme positive value may deserve review without automatic deletion. "
    "The example's dirty tokens are fictional additions for learning, not claims that the original Palmer table contains these errors. Every rejection should point back to its source record and field.",
    'parsed=pd.to_numeric(tokens.mask(documented_unknown),errors="coerce")\ninvalid=(~documented_unknown)&(parsed.isna()|~np.isfinite(parsed)|parsed.le(0))',
    chart('tokens=pd.Series(["3750","NA","heavy","inf","-5"],dtype="string"); unknown=tokens.eq("NA"); parsed=pd.to_numeric(tokens.mask(unknown),errors="coerce").astype(float); invalid=(~unknown)&(parsed.isna()|~np.isfinite(parsed)|parsed.le(0))\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(["Valid known","Documented unknown","Invalid"],[int((~unknown&~invalid).sum()),int(unknown.sum()),int(invalid.sum())]); ax.set_ylabel("Fictional mass tokens")\nprint("Reject for review:",tokens[invalid].tolist())'),
    "'heavy', infinity and-5 fail different parts of the contract. The literal NA is retained as unknown. A diagnostic coercion is followed by an explicit invalid-token mask.",
    ('values=pd.to_numeric(tokens,errors="coerce").fillna(0)', 'unknown=tokens.eq("NA")\n# Audit invalid conversions separately; do not invent zero masses.', "Coercion followed by zero filling hides both unknown and malformed evidence."),
    "Classify ['3500','NA','oops'] into known, documented unknown and invalid and plot the three counts.",
    chart('tokens=pd.Series(["3500","NA","oops"],dtype="string"); unknown=tokens.eq("NA"); parsed=pd.to_numeric(tokens.mask(unknown),errors="coerce"); bad=~unknown&parsed.isna()\nfig,ax=plt.subplots(); ax.bar(["Known","Unknown","Invalid"],[int(parsed.notna().sum()),int(unknown.sum()),int(bad.sum())])\nprint(tokens[bad].tolist())'),
    "Convert known grams [3000,4500] to kilograms, preserve one unknown and print known/unknown counts.",
    chart('grams=pd.Series([3000.,4500.,np.nan]); kg=grams/1000\nfig,ax=plt.subplots(); ax.hist(kg.dropna(),bins=[2,3.5,5]); ax.set_xlabel("kg")\nprint(kg.dropna().tolist(),int(kg.isna().sum()))'),
    "Validate parsed numbers under a stated unit contract; never erase invalid-token evidence with automatic missing or zero conversion.",
    [("Is infinity a finite measured mass?","No","Always","Only if parsed successfully","Parsing and semantic validity are separate checks."),
     ("What makes coercion auditable?","Comparing failed values with original documented-unknown tokens","Filling every failure with0","Dropping all failed rows silently","The token ledger preserves why a value became missing.")])

lesson(2,"4. Flag outliers within a relevant group and retain them",
    "Use IQR flags as review prompts without rewriting the dataset.",
    [("Groupwise IQR flag", "Calculate quartiles within a relevant group, then flag values outside Q1-1.5IQR to Q3+1.5IQR. This is a descriptive convention; group choice and sample size affect the flag."),
     ("No automatic deduplication", "A source-position column supports traceability. It cannot prove that equal measurement rows refer to one bird, so the project records duplicate-value candidates and retains them.")],
    "A large Gentoo can look unusual relative to a pooled sample containing smaller species. Start by inspecting species before treating the pooled tail as invalid. "
    "Even within species, a flag does not prove a measurement error. Keep the value, source position, rule and follow-up question. "
    "Small groups can have unstable quartiles; do not interpret a short excerpt's fence as a research finding. The full project computes flags from all known masses by species. "
    "The decision log explicitly says that flagged records are retained. This preserves the ability to compare summaries before any future justified repair.",
    'q=df.groupby("species")["body_mass_g"].transform(lambda s:s.quantile(0.75))\n# Use matching group quartiles; retain flags as a separate column.',
    chart('df=pd.DataFrame({"species":["A"]*5+["B"]*5,"mass":[10,11,12,13,40,50,51,52,53,54]}); g=df.groupby("species")["mass"]; q1=g.transform(lambda s:s.quantile(.25)); q3=g.transform(lambda s:s.quantile(.75)); flags=df["mass"].gt(q3+1.5*(q3-q1))|df["mass"].lt(q1-1.5*(q3-q1))\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.boxplot([df.loc[df["species"].eq(s),"mass"] for s in ["A","B"]],tick_labels=["A","B"]); ax.set_ylabel("Fictional mass units")\nprint("Flagged values:",df.loc[flags,"mass"].tolist())\nprint("Rows retained:",len(df))'),
    "Week30 transform aligns group-derived quartiles back to original rows. The value40 is flagged in A; none of the larger B values is automatically a bad record.",
    ('df=df.loc[~flags]  # delete solely because a plotting rule flagged it', 'df["mass_iqr_flag"]=flags  # retain evidence for review', "A descriptive fence supplies a review prompt, not deletion authority."),
    "For [10,11,12,13,40], calculate an upper IQR fence, flag40 and prove all five rows remain.",
    chart('s=pd.Series([10,11,12,13,40]); q1,q3=s.quantile([.25,.75]); flags=s.gt(q3+1.5*(q3-q1))\nfig,ax=plt.subplots(); ax.boxplot(s)\nprint(s[flags].tolist(),len(s))'),
    "For identical measurements [3500,3500,4000], assign unique source positions and print candidates without dropping them.",
    chart('df=pd.DataFrame({"source_row":[1,2,3],"mass":[3500,3500,4000]}); flags=df.duplicated("mass",keep=False)\nfig,ax=plt.subplots(); ax.bar(df["source_row"].astype(str),df["mass"])\nprint(int(flags.sum()),len(df))'),
    "Make flags traceable and group-aware; retain observations until source evidence supports a specific correction.",
    [("Does a groupwise IQR flag prove a typo?","No","Always","Only above the median","Flags still require a source investigation."),
     ("Why can pooled flags differ from groupwise flags?","The reference distributions differ","Groups change the raw measurements","The row IDs are probabilities","Different species can have different size distributions.")])

lesson(2,"5. Decision logs and analysis-specific sensitivity",
    "Compare inclusion policies and show their denominators without choosing a favourite result silently.",
    [("Sensitivity analysis", "Repeat a stated summary under plausible, documented analysis choices and compare the effect on results. It does not mean searching for whichever policy gives the desired conclusion."),
     ("Cleaning versus analysis exclusion", "Cleaning keeps a valid partially known record. A particular analysis may exclude it because required fields are missing; log that exclusion separately from source rejection or repair.")],
    "Compare mean known mass among all mass-known records with mean mass among records also having known sex. These are different represented subsets, not competing automatic truths. "
    "Report both n values, both means and why the rule changes. Differences can reflect selection into the known-sex subset, not an error in either arithmetic. "
    "Keep a decision ledger: source tokens retained; documented NA converted; invalid values rejected; equal-value candidates and IQR flags retained; required-field subsets selected per question. "
    "The full project writes audit_changes.csv, decisions.json and inclusion.csv so a reader can trace these choices without relying on memory.",
    'mass_only=df.loc[df["body_mass_g"].notna()]\nsex_mass=df.dropna(subset=["sex","body_mass_g"])',
    example('sets={"Mass known":df.loc[df["body_mass_g"].notna()],"Mass+sex known":df.dropna(subset=["body_mass_g","sex"])}\nmeans=[part["body_mass_g"].mean() for part in sets.values()]\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(list(sets),means); ax.set(ylabel="Mean mass (g)",title="Two inclusion rules, explicitly named")\nprint({name:{"n":len(part),"mean":round(float(part["body_mass_g"].mean()),2)} for name,part in sets.items()})'),
    "In this excerpt both policies happen to retain the same mass-known rows. That is itself a result; the full344-row source has additional known-mass/unknown-sex records, so the project reports actual full-data counts.",
    ('# Publish only the policy with the largest group difference', '# Publish the compared rules, counts and estimates with their rationale', "Transparent sensitivity reveals the consequence of choices rather than concealing a search."),
    "Use a fictional table mass[3000,4000,5000] with sex[female,None,male] and print mean/n for both inclusion rules.",
    chart('df=pd.DataFrame({"mass":[3000,4000,5000],"sex":["female",None,"male"]}); a=df; b=df.dropna(subset=["sex"])\nfig,ax=plt.subplots(); ax.bar(["All known mass","Known sex"],[a["mass"].mean(),b["mass"].mean()])\nprint(len(a),float(a["mass"].mean()),len(b),float(b["mass"].mean()))'),
    "Change the unknown-sex row's mass to6000 and show that the policy can change both count and mean.",
    chart('df=pd.DataFrame({"mass":[3000,6000,5000],"sex":["female",None,"male"]}); a=df; b=df.dropna(subset=["sex"])\nfig,ax=plt.subplots(); ax.bar(["All known mass","Known sex"],[a["mass"].mean(),b["mass"].mean()])\nprint(len(a),round(float(a["mass"].mean()),2),len(b),float(b["mass"].mean()))'),
    "Show the effect of inclusion choices with counts and reasons; cleaning, source rejection and analysis exclusions are different actions.",
    [("What should accompany a sensitivity comparison?","Rules, denominators and estimates","Only the preferred number","A smaller p-value alone","Readers need to see what changed and why."),
     ("Is an analysis-specific exclusion the same as proving a bad row?","No","Always","Only for missing sex","A row can be valid and usable for another question.")])

lesson(3,"1. Inspect every numeric variable on its own scale",
    "Combine a distribution view with count, centre, spread and range.",
    [("Univariate analysis", "Examine one variable at a time before relationships. For each measurement report known n, unknown n, units, mean/median, sample SD, quartiles and range; use a histogram or ECDF to show shape."),
     ("Common bins for comparison", "Choose shared edges when comparing groups of the same quantity. Different units need separate labelled axes, not a single unlabelled value distribution.")],
    "A useful EDA does not skip an uninteresting-looking column. Body mass, bill length, bill depth and flipper length each need a first distribution check. "
    "A mean can conceal skew, gaps or mixed populations, while a histogram depends on its bins. Pair the picture with numerical summaries and a known-value denominator. "
    "Use the quantile and ddof conventions from Week33 explicitly. Keep year as collection labels and source position as a reference, not another biological measurement to correlate. "
    "The excerpt's distributions are only walkthrough evidence; the full project profiles all four measurements across the344-row source and retains unknown counts.",
    'known=df[column].dropna()\nsummary=known.agg(["count","mean","median","std","min","max"])',
    example('cols=["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]; fig,axs=plt.subplots(2,2,figsize=(8,6),layout="constrained")\nfor ax,col in zip(axs.flat,cols):\n    known=df[col].dropna(); ax.hist(known.to_numpy(dtype=float),bins=5); ax.set(title=col,xlabel="g" if col=="body_mass_g" else "mm",ylabel="Known records"); print(col,"n",len(known),"mean/median",round(float(known.mean()),2),round(float(known.median()),2))'),
    "Separate scales preserve measurement units. Similar bar shapes across panels do not imply the same physical range or a common distribution model.",
    ('# Stack mass_g and flipper_mm into an unlabeled measurement histogram', '# Draw each quantity on its own labelled unit scale', "Numeric storage does not make grams and millimetres interchangeable."),
    "Plot the known mass ECDF using sorted observed values and print known n and median.",
    example('known=np.sort(df["body_mass_g"].dropna().to_numpy(dtype=float)); proportion=np.arange(1,len(known)+1)/len(known)\nfig,ax=plt.subplots(); ax.step(known,proportion,where="post"); ax.set(xlabel="Mass g",ylabel="Observed cumulative proportion")\nprint(len(known),float(np.median(known)))'),
    "Draw flipper lengths and print min/max plus sample SD using ddof1.",
    example('known=df["flipper_length_mm"].dropna().to_numpy(dtype=float)\nfig,ax=plt.subplots(); ax.hist(known,bins=5); ax.set_xlabel("Flipper mm")\nprint(float(known.min()),float(known.max()),round(float(known.std(ddof=1)),3))'),
    "Every numeric field deserves a unit-aware distribution and a reconciled numerical summary before relationship claims.",
    [("Should year be interpreted as a body-size measurement?","No","Always","Only with pandas","The field's meaning chooses the summary."),
     ("Why pair a histogram with counts and summaries?","Bins can hide aspects of a distribution","To prove a normal model","To eliminate missingness","Multiple views expose what one summary can conceal.")])

lesson(3,"2. Category counts must keep unknowns visible",
    "Separate known category frequencies from a missing-data display label.",
    [("value_counts(dropna=False)", "Frequency counts can include missing values when dropna=False. For plotting, a temporary Unknown label is readable; preserve actual missingness in the cleaned table."),
     ("Sample composition versus prevalence", "Counts or shares in the collected file describe its composition, not automatically the prevalence of species, islands or recorded sex in the whole environment.")],
    "Count species, island, recorded sex and year separately. Each has a different interpretation, and only sex is unknown in some source records. "
    "A species count of152 Adelie is the count in this snapshot, not an estimate of every Antarctic Adelie penguin. Source coverage and sampling design limit the scope. "
    "Use a stable ordering for repeated views and show Unknown when relevant. If a category is absent from a subset, distinguish no recorded rows from proof that no such population exists. "
    "The full report supplies category_counts.csv and an explicit unknown-sex count so categories are not hidden by a plotting default.",
    'display=df["sex"].fillna("Unknown")\ncounts=display.value_counts()',
    example('counts=df["sex"].fillna("Unknown").value_counts().reindex(["female","male","Unknown"],fill_value=0)\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(counts.index,counts.values); ax.set(ylabel="Excerpt records",title="Recorded sex plus missing evidence")\nprint(counts.to_dict())\nprint("Reconciles:",int(counts.sum())==len(df))'),
    "The temporary display vocabulary has three labels but only two known source values. Unknown is a missingness state, not an invented measured label.",
    ('counts=df["sex"].value_counts()  # silently claim it counts every row', 'counts=df["sex"].fillna("Unknown").value_counts()', "Default known-only counts omit missing records unless you account for them separately."),
    "Count excerpt island labels, plot them and verify the total equals source rows.",
    example('counts=df["island"].value_counts()\nfig,ax=plt.subplots(); ax.bar(counts.index,counts.values); ax.set_ylabel("Recorded rows")\nprint(int(counts.sum())==len(df))'),
    "Show the difference between known-sex denominator and all-row denominator for the female share.",
    example('female=int(df["sex"].eq("female").fillna(False).sum()); known=int(df["sex"].notna().sum()); all_rows=len(df)\nfig,ax=plt.subplots(); ax.bar(["Among known sex","Among all rows"],[female/known,female/all_rows])\nprint(round(female/known,4),round(female/all_rows,4))'),
    "Category shares need their denominator and source scope; a missing-value label is presentation, not a new observation.",
    [("What does a sample species share describe directly?","This file's composition","The entire Antarctic population","A causal effect of island","General prevalence requires appropriate sampling evidence."),
     ("Are known-only and all-row shares necessarily equal?","No","Always","Only with three species","Unknown labels change the denominator.")])

lesson(3,"3. Numeric pairs: plot, count and inspect grouping",
    "Analyse complete paired coordinates without silently changing identity.",
    [("Pair-complete mask", "Select rows where both variables are known. Do not drop unknowns independently in each Series, because that can misalign observations."),
     ("Pooled versus group association", "An overall correlation mixes groups. Compare a species-coloured scatter and, where enough variation exists, within-species descriptions before interpreting a pooled association.")],
    "For flipper length and mass, one point should carry both values from the same recorded row. Report included and excluded counts. "
    "Then inspect whether species form clusters. A strong pooled association may reflect differences between species as well as variation within them. "
    "Week33 explained that Pearson measures linear association, can be undefined for constant columns, and does not establish causation. Reuse that reasoning instead of reporting a coefficient alone. "
    "The full project records a pair-count matrix, pooled coefficients and species-stratified coefficients. It does not turn those exploratory coefficients into a new family of confirmatory p-values.",
    'valid=df[["flipper_length_mm","body_mass_g"]].notna().all(axis=1)\npaired=df.loc[valid]',
    example('cols=["flipper_length_mm","body_mass_g"]; valid=df[cols].notna().all(axis=1); paired=df.loc[valid]\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nfor name,part in paired.groupby("species"): ax.scatter(part[cols[0]],part[cols[1]],label=name)\nax.set(xlabel="Flipper length mm",ylabel="Body mass g",title="Paired excerpt values, species visible"); ax.legend()\nprint("Included/excluded:",len(paired),len(df)-len(paired))\nprint("Descriptive r:",round(float(paired[cols].corr().iloc[0,1]),4))'),
    "The joint mask preserves rows. Species colours provide context for the association; they do not by themselves identify a causal adjustment.",
    ('x=df["flipper_length_mm"].dropna(); y=df["body_mass_g"].dropna()', 'paired=df.dropna(subset=["flipper_length_mm","body_mass_g"])', "Separate dropping can combine coordinates from different source rows."),
    "Draw bill length versus bill depth with complete pairs and print their known-pair count.",
    example('part=df.dropna(subset=["bill_length_mm","bill_depth_mm"])\nfig,ax=plt.subplots(); ax.scatter(part["bill_length_mm"],part["bill_depth_mm"]); ax.set(xlabel="Bill length mm",ylabel="Bill depth mm")\nprint(len(part))'),
    "Count known pairs among all four measurements using an indicator-matrix product; plot the count matrix.",
    example('cols=["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]; known=df[cols].notna().astype(int); pairs=known.T.dot(known)\nfig,ax=plt.subplots(); ax.imshow(pairs.to_numpy(),cmap="Blues"); ax.set_title("Known pair counts")\nprint(pairs.to_dict())'),
    "Preserve row pairing, report pair counts and inspect grouped structure before interpreting a pooled coefficient.",
    [("How should missing x/y values be filtered?","Jointly by row","Independently then re-zipped","Filled with zero automatically","The coordinates must refer to the same observation."),
     ("Does a species-coloured scatter prove a causal effect?","No","Always","Only with high r","A visual grouping is not an identified intervention design.")])

lesson(3,"4. Numeric by category: counts belong beside group summaries",
    "Compare means, medians and spreads without hiding different known sample sizes.",
    [("Group summary contract", "A group summary should state all rows, known outcomes, unknown outcomes and the chosen statistic. Size and count differ when a measurement is unknown."),
     ("Descriptive group difference", "A difference between observed means is a result about the represented groups. It is not automatically a causal effect, a population estimate or evidence that every individual in one group exceeds every individual in another.")],
    "Compare mass by species using both boxes and a summary table. Add known n and unknown count so readers see the evidence behind the middle and spread. "
    "The full source's known-mass counts are151 Adelie,68 Chinstrap and123 Gentoo. Different counts matter when combining or reweighting summaries. "
    "A larger Gentoo mean does not imply no overlap between individual masses. The box and raw distribution help expose that distinction. "
    "Keep the calculation descriptive; do not add a default confidence interval merely because a plotting function can generate one without validating the collection design.",
    'g=df.groupby("species")["body_mass_g"]\nsummary=g.agg(["size","count","mean","median","std"])',
    example('g=df.groupby("species")["body_mass_g"]; summary=g.agg(["size","count","mean","median"]); summary["unknown"]=summary["size"]-summary["count"]\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); labels=summary.index.tolist(); ax.boxplot([df.loc[df["species"].eq(s),"body_mass_g"].dropna().to_numpy(dtype=float) for s in labels],tick_labels=labels); ax.set(ylabel="Known mass g",title="Excerpt distributions; known n in output")\nprint(summary.round(2).to_dict())'),
    "The box receives only known masses, while size still retains all species rows. Unknowns remain in the cleaned source and the denominator ledger.",
    ('g.count()  # label this every source row', 'g.agg(["size","count"])  # distinguish all rows from known outcomes', "Missing measurements create different denominators for size and count."),
    "Compare species mean and median known mass side by side in the excerpt; print both sets.",
    example('summary=df.groupby("species")["body_mass_g"].agg(["mean","median"]); x=np.arange(len(summary))\nfig,ax=plt.subplots(); ax.bar(x-.18,summary["mean"],.35,label="Mean"); ax.bar(x+.18,summary["median"],.35,label="Median"); ax.set(xticks=x,xticklabels=summary.index,ylabel="Mass g"); ax.legend()\nprint(summary.round(2).to_dict())'),
    "Print and draw the unknown-mass count for each species instead of silently excluding those rows from a coverage report.",
    example('unknown=df["body_mass_g"].isna().groupby(df["species"]).sum()\nfig,ax=plt.subplots(); ax.bar(unknown.index,unknown.values); ax.set_ylabel("Unknown mass rows")\nprint(unknown.to_dict())'),
    "Pair group estimates with denominators and distribution context; a mean difference does not describe every individual or prove a cause.",
    [("What does group size include that count on mass omits?","Rows with unknown mass","Only outliers","Extra invented birds","Count uses known measurements; size uses rows."),
     ("Does a larger mean imply all values are larger?","No","Always","Only with boxes","Distributions can overlap despite different centres.")])

lesson(3,"5. Category pairs: counts, row shares and observed support",
    "Build a cross-tab with an explicit percentage denominator.",
    [("crosstab; normalize='index'", "pd.crosstab counts category combinations. normalize='index' divides each row by its own total; normalise across columns or the whole table only when that matches the question."),
     ("Observed support versus population impossibility", "A zero cell means no records for that combination in the supplied table. It is not proof that the combination cannot exist in nature or a licence to estimate its unobserved outcome.")],
    "Species by island is more than a decorative table: it reveals where the source offers comparison overlap. In the full file, Gentoo records are on Biscoe and Chinstrap on Dream; Adelie occurs across the three islands. "
    "An island mean therefore mixes different species compositions. Calculating a single island effect from that comparison would be unsupported. "
    "Use counts first, then conditional shares with a clear denominator. A row-normalised species/island table describes where each species' recorded rows appear. "
    "Do not substitute an absent cell with an invented average mass. Observation counts can be zero while the corresponding population property remains unobserved.",
    'counts=pd.crosstab(df["species"],df["island"])\nshares=pd.crosstab(df["species"],df["island"],normalize="index")',
    example('counts=pd.crosstab(df["species"],df["island"]); shares=counts.div(counts.sum(axis=1),axis=0)\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.imshow(counts.to_numpy(),cmap="Blues"); ax.set(xticks=np.arange(len(counts.columns)),xticklabels=counts.columns,yticks=np.arange(len(counts)),yticklabels=counts.index,title="Excerpt observed species/island support")\nprint("Counts:",counts.to_dict())\nprint("Row shares sum to1:",bool(np.allclose(shares.sum(axis=1),1)))'),
    "The excerpt intentionally takes only the first four records per species, so its island coverage is narrower than the full file. Do not present this small support table as the full dataset's support.",
    ('# Fill an absent species/island mean with0g and compare it', '# Mark unsupported mean combinations missing; retain0 only for observed row counts', "No recorded observations is not a measured zero biological outcome."),
    "Cross-tab species by recorded sex using a display Unknown label; print that counts sum to all excerpt rows.",
    example('table=pd.crosstab(df["species"],df["sex"].fillna("Unknown"))\nfig,ax=plt.subplots(); ax.imshow(table.to_numpy(),cmap="Blues"); ax.set_title("Includes missing-sex display column")\nprint(int(table.to_numpy().sum())==len(df))'),
    "Row-normalise that table and print every species' total share; keep the Unknown label as an evidence state.",
    example('table=pd.crosstab(df["species"],df["sex"].fillna("Unknown")); shares=table.div(table.sum(axis=1),axis=0)\nfig,ax=plt.subplots(); ax.imshow(shares.to_numpy(),vmin=0,vmax=1,cmap="Blues")\nprint(shares.sum(axis=1).round(6).to_dict())'),
    "Report counts and conditional-share denominators; missing comparison support must remain visible rather than becoming a zero-valued outcome.",
    [("What does a row-normalised table condition on?","The row category","Always the whole population","The largest cell only","Each row total is its denominator."),
     ("Does an empty species/island cell prove biological impossibility?","No","Always","Only for penguins","The source records limited observed support.")])

lesson(4,"1. Stratify only where the source has comparison support",
    "Inspect species/sex groups and distinguish an unsupported effect from an observed difference.",
    [("Stratum; overlap support", "A stratum is a defined subgroup. A within-stratum comparison needs observations in the groups being compared; absent combinations cannot be repaired by simply adding another regression variable."),
     ("Confounded composition", "The species mixture varies across islands in this source. An overall island mean combines that mixture with any other differences, so it does not isolate a geographic effect.")],
    "Start with observed counts for species by island, then inspect mass by species and recorded sex among known fields. Each layer should show its own denominator. "
    "Gentoo and Chinstrap do not both appear on every island in the full snapshot. There is no observed same-species comparison across all those islands for these groups. "
    "Sex-stratified summaries reveal another dimension of the source's mass distribution, but they remain observational comparisons. Unknown sex and unequal counts still matter. "
    "The task is to state the genuine recorded subgroup difference and its scope, not to promise a causal explanation that the available design cannot support.",
    'part=df.dropna(subset=["sex","body_mass_g"])\nsummary=part.groupby(["species","sex"])["body_mass_g"].agg(["count","mean"])',
    example('part=df.dropna(subset=["sex","body_mass_g"]); summary=part.groupby(["species","sex"])["body_mass_g"].agg(["count","mean"])\nfig,ax=plt.subplots(figsize=(7,3.5),layout="constrained"); labels=[s+"/"+sex for s,sex in summary.index]; ax.barh(labels,summary["mean"]); ax.set(xlabel="Mean known mass g",title="Excerpt species/sex groups with known n in output")\nprint(summary.round(2).to_dict())'),
    "The table shows which groups have evidence. A small excerpt subgroup can be just one record, so do not invent an SD interval or general-population precision claim for it.",
    ('# Control for species and claim an island effect even with missing overlap', '# Inspect supported within-species comparisons and state unsupported ones', "A statistical adjustment cannot manufacture data in absent combinations."),
    "Count known mass records by species/sex in the excerpt and draw their counts.",
    example('part=df.dropna(subset=["sex","body_mass_g"]); counts=part.groupby(["species","sex"]).size()\nfig,ax=plt.subplots(); ax.barh([s+"/"+x for s,x in counts.index],counts.values)\nprint(counts.to_dict())'),
    "For a fictional support table A only islandX and B only islandY, show the counts and print that no same-species cross-island comparison exists.",
    chart('table=pd.DataFrame([[5,0],[0,5]],index=["Species A","Species B"],columns=["X","Y"])\nfig,ax=plt.subplots(); ax.imshow(table.to_numpy(),cmap="Blues"); ax.set_title("No same-species cross-island overlap")\nprint("Supported cross-island species:",int(table.gt(0).all(axis=1).sum()))'),
    "Stratification requires real support; descriptive subgroup comparisons do not create a causal design.",
    [("Can adding a covariate manufacture missing comparison support?","No","Always","Only for linear regression","Unobserved combinations remain unobserved."),
     ("What belongs beside a subgroup mean?","Its known-outcome count","Only a colour","A causal label automatically","Group size and missingness contextualise the estimate.")])

lesson(4,"2. Multivariate matrices need pair counts and a common rule",
    "Compare pairwise and complete-case correlation summaries transparently.",
    [("Pairwise versus common rows", "Pairwise correlations may use different known rows for each pair. Complete-case analysis uses one common set across selected variables, often retaining fewer records. Both require disclosed denominators."),
     ("Correlation matrix limits", "A matrix hides scatter shape, grouping, units and collection context. Fixed-1 to1 colour limits support comparison, while undefined coefficients must remain undefined.")],
    "The four body measurements make a compact matrix, but it is a map of descriptive linear associations rather than four-variable causal reasoning. "
    "Keep a pair-count matrix next to it. In the original snapshot the four measurement gaps coincide, giving342 known measurement rows, but this coincidence is a property to inspect rather than assume for every future file. "
    "Add recorded sex to a common-row rule and the available set changes again. A correlation change can reflect different retained rows as well as different conditioning. "
    "Use scatter and subgroup views to investigate notable cells before writing a story. Do not declare population significance from an unverified sample merely because a software function can calculate p-values.",
    'known=df[cols].notna().astype(int)\npair_counts=known.T.dot(known)\ncorr=df[cols].corr(min_periods=3)',
    example('cols=["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]; known=df[cols].notna().astype(int); counts=known.T.dot(known); corr=df[cols].corr(min_periods=3)\nfig,ax=plt.subplots(figsize=(6,4),layout="constrained"); im=ax.imshow(corr.to_numpy(dtype=float),vmin=-1,vmax=1,cmap="RdBu_r"); ax.set(xticks=np.arange(4),xticklabels=["Bill L","Bill D","Flipper","Mass"],yticks=np.arange(4),yticklabels=["Bill L","Bill D","Flipper","Mass"],title="Excerpt Pearson coefficients, not causal effects"); fig.colorbar(im,ax=ax,label="r")\nprint("Pair counts:",counts.to_dict())'),
    "The colourbar has a fixed numeric meaning. The matrix remains descriptive and uses only meaningful measurements, not numeric row positions or year labels.",
    ('corr=df.select_dtypes("number").corr()  # include generated row positions', 'corr=df[measurement_columns].corr(min_periods=3)', "Choose variables by meaning rather than correlating every numeric storage field."),
    "Calculate complete rows across mass, flipper and bill length, draw the common-row scatter and print excluded rows.",
    example('cols=["body_mass_g","flipper_length_mm","bill_length_mm"]; part=df.dropna(subset=cols)\nfig,ax=plt.subplots(); ax.scatter(part["flipper_length_mm"],part["body_mass_g"])\nprint(len(part),len(df)-len(part))'),
    "In a fictional table with x[1,2,3,4], y[2,None,6,8], z[4,3,None,1], print each pair count and the all-three complete count.",
    chart('df=pd.DataFrame({"x":[1,2,3,4],"y":[2,None,6,8],"z":[4,3,None,1]}); known=df.notna().astype(int); counts=known.T.dot(known)\nfig,ax=plt.subplots(); ax.imshow(counts.to_numpy(),cmap="Blues")\nprint(counts.to_dict(),"Common:",len(df.dropna()))'),
    "Carry denominators into multivariate summaries and inspect the observations and group structure behind a striking coefficient.",
    [("Can different correlation cells use different rows?","Yes","Never","Only after plotting","Pairwise missingness can change the contributing set."),
     ("Should source-row positions be correlated as biological measurements?","No","Always","Only if unique","Their numerical encoding does not make a physical variable.")])

lesson(4,"3. Standardise a descriptive group mix without claiming causality",
    "Compare an observed mean with a stated equal-weight subgroup target.",
    [("Direct standardisation; target weights", "Combine subgroup means with an explicit common weight distribution to compare a defined descriptive target. This changes the weighting question; it does not by itself identify a causal effect or represent a real target population."),
     ("Positivity for weights", "A weighted subgroup estimate requires observed outcomes in every positively weighted subgroup. Do not invent a missing subgroup mean or silently renormalise weights over whichever cells happen to exist.")],
    "Species can have unequal recorded male/female counts among known masses. Their observed means therefore reflect both subgroup means and the sample mix. "
    "For a teaching sensitivity, average female and male means equally within each species. Label this an equal-known-sex-weight descriptive estimate; do not call it the true species mean. "
    "This target excludes unknown-sex evidence by construction. Compare it with the available known-sex weighted mean and report subgroup counts. "
    "When a subgroup is absent, mark the standardised result unavailable instead of substituting zero or pretending the remaining subgroup is the whole target.",
    'means=part.groupby(["species","sex"])["body_mass_g"].mean().unstack()\nstandardised=0.5*means["female"]+0.5*means["male"]',
    example('part=df.dropna(subset=["sex","body_mass_g"]); means=part.groupby(["species","sex"])["body_mass_g"].mean().unstack().reindex(columns=["female","male"]); equal=0.5*means["female"]+0.5*means["male"]; observed=part.groupby("species")["body_mass_g"].mean(); x=np.arange(len(equal))\nfig,ax=plt.subplots(figsize=(7,3.5),layout="constrained"); ax.bar(x-.18,observed.reindex(equal.index),.35,label="Observed known-sex mix"); ax.bar(x+.18,equal,.35,label="Equal female/male weights"); ax.set(xticks=x,xticklabels=equal.index,ylabel="Descriptive mean mass g"); ax.legend()\nprint("Equal-weight estimates:",equal.round(2).to_dict())'),
    "The equal weights answer a declared alternative mix question. They do not fill unknown sex, eliminate other confounding or validate extrapolation beyond the recorded groups.",
    ('standardised=means.fillna(0).mean(axis=1)', 'standardised=0.5*means["female"]+0.5*means["male"]  # missing subgroup stays missing', "Zero filling fabricates an unobserved subgroup mass."),
    "For subgroup means3000 and4000 with observed counts1 and3, compare the count-weighted mean with an equal-weight target.",
    chart('means=np.array([3000.,4000.]); observed=float(np.average(means,weights=[1,3])); equal=float(means.mean())\nfig,ax=plt.subplots(); ax.bar(["Observed mix","Equal weights"],[observed,equal])\nprint(observed,equal)'),
    "Show that an equal-weight estimate with one unknown subgroup remains unknown rather than treating its mass as0.",
    chart('means=pd.Series({"female":3000.,"male":np.nan}); estimate=0.5*means["female"]+0.5*means["male"]\nfig,ax=plt.subplots(); ax.bar(["Known subgroup"],[3000]); ax.set_title("Second subgroup unavailable; target not estimated")\nprint("Estimate unavailable:",bool(pd.isna(estimate)))'),
    "State the weighting target, require support and distinguish descriptive standardisation from a causal or population guarantee.",
    [("Does an equal-weight estimate automatically describe a real population?","No","Always","Only for two groups","The target weights are an explicit analysis choice."),
     ("What if a positively weighted subgroup has no outcome evidence?","Keep the estimate unavailable","Use0g","Ignore that subgroup silently","Support is required for the stated target.")])

lesson(4,"4. Collection years are repeated cross-sections, not guaranteed trajectories",
    "Separate year-level summaries from within-individual change.",
    [("Cross-sectional year summary", "A year mean compares recorded rows in that year. Without verified matched identities, it is not a longitudinal path for the same penguins."),
     ("Composition shift", "Changes in species/sex mix, collection context and missingness can move a pooled year mean even when subgroup means do not change. Inspect year-by-group support and known counts.")],
    "The full source includes2007–2009. Plotting three overall means does not prove that the same birds gained or lost mass over time. "
    "First ask which records contribute each year, how species composition differs and which outcomes are known. The simplified dataset does not provide individual IDs for matching across years. "
    "The fictional illustration below holds two group means fixed while their row proportions change. The aggregate moves anyway. "
    "The project records actual year/species means and counts from the full file, and its interpretation describes observed collection-year differences rather than individual growth or a climate effect.",
    'summary=df.groupby(["year","species"])["body_mass_g"].agg(["size","count","mean"])',
    chart('df=pd.DataFrame({"year":[2007,2007,2009,2009],"group":["A","B","A","B"],"mean_g":[3000,5000,3000,5000],"count":[8,2,2,8]}); totals=df.assign(total=df["mean_g"]*df["count"]).groupby("year").agg(total=("total","sum"),n=("count","sum")); means=totals["total"]/totals["n"]\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.plot(means.index,means.values,marker="o"); ax.set(xticks=[2007,2009],ylabel="Pooled mean g",title="Fictional mix changes; subgroup means unchanged")\nprint(means.to_dict())'),
    "The pooled means3400 and4600 differ entirely because group composition changes in this constructed example. No individual before/after observation was supplied.",
    ('# Label year means as the same birds growth curve', '# Label them recorded year summaries and inspect composition', "A year column alone cannot establish repeated individual identity."),
    "Using the same two fixed means3000,5000, calculate year means under mixtures50/50 and25/75.",
    chart('a=float(np.average([3000,5000],weights=[50,50])); b=float(np.average([3000,5000],weights=[25,75]))\nfig,ax=plt.subplots(); ax.bar(["Year A mix","Year B mix"],[a,b])\nprint(a,b)'),
    "For the excerpt, count rows by year and print that its range is only the observed excerpt range, not necessarily the full source range.",
    example('counts=df.groupby("year").size()\nfig,ax=plt.subplots(); ax.bar(counts.index.astype(str),counts.values); ax.set_ylabel("Excerpt records")\nprint("Excerpt years:",counts.index.tolist())'),
    "Year summaries describe collected rows; composition and identity limitations prevent an automatic individual-change interpretation.",
    [("Does a year column identify matched birds?","No","Always","Only if sorted","Matching requires identity evidence beyond a date label."),
     ("Can pooled means change with fixed subgroup means?","Yes, through composition","Never","Only with bad arithmetic","Changing group weights changes the aggregate target.")])

lesson(4,"5. Robust conclusions survive a disclosed sensitivity check",
    "Compare centre and inclusion choices and state what remains unresolved.",
    [("Robustness of a descriptive conclusion", "A conclusion is more transparent when its behaviour under reasonable stated choices is shown. Similar results are not proof of causality; different results identify sensitivity worth explaining."),
     ("Sensitivity ledger", "Record baseline and alternative rules, row counts, group counts, estimates and the reason for each choice. Avoid an arbitrary trim or threshold chosen only to strengthen a story.")],
    "Two practical checks are mean versus median within species and all-known-mass versus known-sex/mass subsets. Keep unknowns and subgroup counts visible in both. "
    "If Gentoo remains heavier on these descriptive summaries, you can say that the observed ordering holds under those particular checks. You cannot say every conceivable analysis confirms a biological cause. "
    "A notable change is useful evidence too. Explain which rows or weights changed instead of treating it as an inconvenience to hide. "
    "The final report includes sensitivity.csv and an executive summary that qualifies its main finding with sample, missingness and species/island support limitations.",
    'baseline=df.groupby("species")["body_mass_g"].agg(["count","mean","median"])\n# Compare a documented alternative on its own stated row set.',
    example('base=df.groupby("species")["body_mass_g"].agg(["mean","median"]); x=np.arange(len(base))\nfig,ax=plt.subplots(figsize=(7,3.5),layout="constrained"); ax.bar(x-.18,base["mean"],.35,label="Mean"); ax.bar(x+.18,base["median"],.35,label="Median"); ax.set(xticks=x,xticklabels=base.index,ylabel="Known mass g",title="One disclosed centre-choice check"); ax.legend()\nprint("Mean ordering:",base["mean"].sort_values().index.tolist())\nprint("Median ordering:",base["median"].sort_values().index.tolist())'),
    "Ordering under two summaries is a narrow descriptive result, not a universal robustness guarantee. Ties and the small excerpt sample also deserve disclosure.",
    ('# Try many exclusions, publish only the largest difference', '# State a few reasonable checks and report every compared outcome', "A sensitivity analysis should reveal choices rather than conceal a search."),
    "For [3000,3100,3200,7000], show mean versus median and keep the extreme value in the source.",
    chart('values=np.array([3000,3100,3200,7000]); fig,ax=plt.subplots(); ax.bar(["Mean","Median"],[values.mean(),np.median(values)])\nprint(float(values.mean()),float(np.median(values)),len(values))'),
    "Compare all known masses with a justified measurement-specific subset in a fictional table, printing both denominators and means instead of choosing a preferred result.",
    chart('df=pd.DataFrame({"mass":[3000,4000,6000],"sex":["female","male",None]}); a=df["mass"]; b=df.dropna(subset=["sex"])["mass"]\nfig,ax=plt.subplots(); ax.bar(["Mass known","Mass+sex known"],[a.mean(),b.mean()])\nprint(len(a),round(float(a.mean()),2),len(b),float(b.mean()))'),
    "Use stated sensitivity checks to qualify descriptive claims, and preserve all compared rules and denominators.",
    [("Do similar means/medians prove causation?","No","Always","Only in a real dataset","Robustness of a summary is not causal identification."),
     ("What should happen to an alternative result that changes the story?","Report it and explain the changed scope","Hide it","Delete its input rows","Sensitivity is evidence, not a result to suppress.")])

CLEAN_CORE='''
import csv
import io
COLS=["species","island","bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g","sex","year"]
MEASURES=["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]
SPECIES=["Adelie","Chinstrap","Gentoo"]
ISLANDS=["Biscoe","Dream","Torgersen"]

def load_tokens(text):
    rows=list(csv.reader(io.StringIO(text),strict=True))
    if not rows or rows[0]!=COLS or len(rows)<2 or len(rows)>10001:
        raise ValueError("Require documented header and1–10000 records")
    if any(len(row)!=len(COLS) for row in rows[1:]): raise ValueError("Ragged source rows")
    return pd.DataFrame(rows[1:],columns=COLS,dtype="string")

def clean_tokens(raw):
    if raw.columns.tolist()!=COLS: raise ValueError("Wrong raw schema")
    clean=raw.copy().reset_index(drop=True); changes=[]
    for col in COLS:
        for pos,old in enumerate(raw[col]):
            new=old.strip()
            if new!=old: changes.append([pos+1,col,old,new,"strip surrounding whitespace"])
            clean.loc[pos,col]=new
    for col,allowed in [("species",SPECIES),("island",ISLANDS)]:
        if not clean[col].isin(allowed).all(): raise ValueError("Unknown required category: "+col)
    for col in MEASURES:
        values=[]
        for pos,token in enumerate(clean[col]):
            if token=="NA":
                values.append(float("nan")); changes.append([pos+1,col,token,"<NA>","documented unknown, retained"])
            else:
                try: value=float(token)
                except ValueError as error: raise ValueError(f"Invalid {col}, record {pos+1}") from error
                if not np.isfinite(value) or not 0<value<=1_000_000:
                    raise ValueError(f"Invalid finite positive {col}, record {pos+1}")
                values.append(value)
        clean[col]=pd.Series(values,dtype=float)
    sex=[]
    for pos,token in enumerate(clean["sex"]):
        if token=="NA":
            sex.append(pd.NA); changes.append([pos+1,"sex",token,"<NA>","documented unknown, retained"])
        else:
            value=token.casefold()
            if value not in ["female","male"]: raise ValueError("Unknown sex token")
            if value!=token: changes.append([pos+1,"sex",token,value,"declared sex casefold rule"])
            sex.append(value)
    clean["sex"]=pd.Series(sex,dtype="string")
    if not clean["year"].isin(["2007","2008","2009"]).all(): raise ValueError("Expected source collection years2007–2009")
    clean["year"]=clean["year"].astype(int)
    clean.insert(0,"_source_record",np.arange(1,len(clean)+1))
    duplicate=clean.duplicated(COLS,keep=False)
    g=clean.groupby("species")["body_mass_g"]
    q1=g.transform(lambda s:s.quantile(.25)); q3=g.transform(lambda s:s.quantile(.75)); iqr=q3-q1
    flag=(clean["body_mass_g"].lt(q1-1.5*iqr)|clean["body_mass_g"].gt(q3+1.5*iqr)).fillna(False)
    clean["duplicate_value_candidate"]=duplicate
    clean["mass_iqr_flag"]=flag
    audit=pd.DataFrame(changes,columns=["source_record","column","old_token","new_token","rule"])
    decisions={"source_rows":len(raw),"retained_rows":len(clean),"deleted_rows":0,"imputed_values":0,
        "unknown_counts":{col:int(clean[col].isna().sum()) for col in COLS},
        "duplicate_candidate_rows":int(duplicate.sum()),"iqr_flag_rows":int(flag.sum()),
        "policy":"NA retained; malformed input stops; flags and equal-value candidates retained; no invented identity"}
    return clean,audit,decisions
'''

REPORT_CORE='''
def group_mass(df,keys):
    result=df.groupby(keys,dropna=False)["body_mass_g"].agg(["size","count","mean","median","std"])
    result["unknown_mass"]=result["size"]-result["count"]
    return result

def summarize(df):
    pairs=df.dropna(subset=["flipper_length_mm","body_mass_g"])
    if len(pairs)<3 or pairs["flipper_length_mm"].nunique()<2 or pairs["body_mass_g"].nunique()<2:
        raise ValueError("Report needs at least3 variable known flipper/mass pairs")
    profile=pd.DataFrame({"known":df[COLS].notna().sum(),"unknown":df[COLS].isna().sum(),
        "distinct_known":df[COLS].nunique(dropna=True)})
    categories=[]
    for col in ["species","island","sex","year"]:
        for name,n in df[col].astype("string").fillna("Unknown").value_counts().items(): categories.append([col,name,int(n)])
    support=pd.crosstab(df["species"],df["island"]).reindex(index=SPECIES,columns=ISLANDS,fill_value=0)
    known=df[MEASURES].notna().astype(int); counts=known.T.dot(known)
    both=df.dropna(subset=["sex","body_mass_g"])
    means=both.groupby(["species","sex"])["body_mass_g"].mean().unstack().reindex(index=SPECIES,columns=["female","male"])
    standardised=pd.DataFrame({"equal_known_sex_weight_mean_g":.5*means["female"]+.5*means["male"]})
    sensitivity=pd.concat([group_mass(df,["species"]).assign(rule="all known mass"),
        group_mass(both,["species"]).assign(rule="known sex and mass")]).reset_index()
    tables={"profile":profile,"category_counts":pd.DataFrame(categories,columns=["column","category","count"]),
        "species_mass":group_mass(df,["species"]),"species_sex_mass":group_mass(df,["species","sex"]),
        "support_species_island":support,"year_species_mass":group_mass(df,["year","species"]),
        "correlation":df[MEASURES].corr(min_periods=3),"pair_counts":counts,
        "sensitivity":sensitivity,"standardised_mass":standardised}
    species=tables["species_mass"]
    winner=species["mean"].idxmax()
    facts={"rows":len(df),"known_mass":int(df["body_mass_g"].notna().sum()),"unknown_mass":int(df["body_mass_g"].isna().sum()),
        "unknown_sex":int(df["sex"].isna().sum()),"known_sex_mass":len(both),"flipper_mass_pairs":len(pairs),
        "species_rows":{s:int(n) for s,n in df.groupby("species").size().items()},
        "species_known_mass":{s:int(n) for s,n in species["count"].items()},
        "species_mean_mass_g":{s:float(v) if pd.notna(v) else None for s,v in species["mean"].items()},
        "species_median_mass_g":{s:float(v) if pd.notna(v) else None for s,v in species["median"].items()},
        "largest_observed_mean_species":winner,"pooled_flipper_mass_r":float(pairs[["flipper_length_mm","body_mass_g"]].corr().iloc[0,1]),
        "within_species_flipper_mass_r":{s:float(p[["flipper_length_mm","body_mass_g"]].corr().iloc[0,1])
            if len(p)>=3 and p["flipper_length_mm"].nunique()>1 and p["body_mass_g"].nunique()>1 else None
            for s,p in pairs.groupby("species")},
        "year_labels":[int(v) for v in sorted(df["year"].unique())],
        "interpretation":"Descriptive historical recorded sample; no island causal effect, matched-bird growth or Antarctic census claim"}
    return tables,facts

def overview(df,tables):
    fig,axs=plt.subplots(4,2,figsize=(12,14),layout="constrained")
    known=df["body_mass_g"].dropna()
    axs[0,0].hist(known,bins=15); axs[0,0].set(title="1. Known mass distribution",xlabel="Mass g",ylabel="Records")
    present=[s for s in SPECIES if df.loc[df["species"].eq(s),"body_mass_g"].notna().any()]
    axs[0,1].boxplot([df.loc[df["species"].eq(s),"body_mass_g"].dropna() for s in present],tick_labels=present)
    axs[0,1].set(title="2. Known mass by species",ylabel="Mass g")
    pairs=df.dropna(subset=["flipper_length_mm","body_mass_g"])
    for s,part in pairs.groupby("species"):
        axs[1,0].scatter(part["flipper_length_mm"],part["body_mass_g"],label=s,s=15)
    axs[1,0].set(title="3. Complete coordinate pairs",xlabel="Flipper mm",ylabel="Mass g"); axs[1,0].legend(fontsize=8)
    profile=tables["profile"]; axs[1,1].barh(profile.index,profile["unknown"]); axs[1,1].set(title="4. Unknowns retained",xlabel="Records")
    means=df.dropna(subset=["sex","body_mass_g"]).groupby(["species","sex"])["body_mass_g"].mean().unstack().reindex(index=SPECIES,columns=["female","male"])
    x=np.arange(3)
    axs[2,0].bar(x-.18,means["female"],.35,label="female"); axs[2,0].bar(x+.18,means["male"],.35,label="male")
    axs[2,0].set(xticks=x,xticklabels=SPECIES,title="5. Recorded-sex known-mass means",ylabel="Mass g"); axs[2,0].legend(fontsize=8)
    support=tables["support_species_island"]; values=support.to_numpy()
    axs[2,1].imshow(values,cmap="Blues"); axs[2,1].set(xticks=np.arange(3),xticklabels=ISLANDS,yticks=np.arange(3),yticklabels=SPECIES,title="6. Observed comparison support")
    for (r,c),v in np.ndenumerate(values): axs[2,1].text(c,r,str(v),ha="center",va="center",color="white" if v>values.max()/2 else "black")
    annual=tables["year_species_mass"].reset_index()
    for s,part in annual.groupby("species"):
        axs[3,0].plot(part["year"],part["mean"],marker="o",label=s)
    axs[3,0].set(title="7. Year summaries, not matched growth",xlabel="Collection year",ylabel="Mean known mass g",xticks=sorted(df["year"].unique()))
    corr=tables["correlation"].to_numpy(dtype=float)
    image=axs[3,1].imshow(np.ma.masked_invalid(corr),vmin=-1,vmax=1,cmap="RdBu_r")
    axs[3,1].set(title="8. Descriptive correlations; pair n supplied",xticks=np.arange(4),xticklabels=["Bill L","Bill D","Flipper","Mass"],yticks=np.arange(4),yticklabels=["Bill L","Bill D","Flipper","Mass"])
    fig.colorbar(image,ax=axs[3,1],label="Pearson r")
    fig.suptitle(f"Palmer Penguins: {len(df)} recorded rows; descriptive EDA, unknown values retained")
    return fig
'''

lesson(5,"1. Write claim, evidence, limitation and next check",
    "Make each finding traceable without overstating what it establishes.",
    [("Finding structure", "A useful finding states the observed result, the supporting statistic/chart and denominator, a limitation, and a sensible next check. This turns a chart collection into an understandable report."),
     ("Observation versus explanation", "A larger recorded group mean is an observation under an inclusion rule. Explaining why it differs requires additional evidence about design, composition and measurement.")],
    "A sentence such as 'Gentoo are bigger because they live on Biscoe' exceeds the file's support. A defensible sentence names the recorded known-mass comparison and its counts, then states the limited overlap and observational scope. "
    "Write what you can see before proposing a cause. Include the chart/table name so another reader can reproduce the number. "
    "State one useful next step: inspect raw collection metadata, verify identity/design assumptions or plan a comparison with actual overlap. More charts of the same unsupported comparison do not supply missing evidence. "
    "Use the twelve-row excerpt to practise wording, and reserve full-source claims for the generated344-row report.",
    'finding={"claim":observed_result,"evidence":table_and_n,"limit":scope,"next":check}',
    example('summary=df.groupby("species")["body_mass_g"].agg(["count","mean"]); top=summary["mean"].idxmax()\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(summary.index,summary["mean"]); ax.set(ylabel="Known mass g",title="Describe the represented sample")\nprint("Excerpt finding:",top,"has the largest observed group mean",round(float(summary.loc[top,"mean"]),1),"g; known n",int(summary.loc[top,"count"]))\nprint("Limit: excerpt and observational group composition; not a causal island effect")'),
    "The generated wording identifies the winner from the table and includes a known n. The scope label prevents an excerpt result from masquerading as the whole source.",
    ('print("This chart proves an island makes birds heavier")', 'print("Observed group means differ; island/species support limits explanation")', "The source has limited overlap and no identified island intervention."),
    "Generate a sentence giving the excerpt's known-mass count and unknown count, then draw those counts.",
    example('known=int(df["body_mass_g"].notna().sum()); unknown=int(df["body_mass_g"].isna().sum())\nfig,ax=plt.subplots(); ax.bar(["Known","Unknown"],[known,unknown])\nprint(f"The excerpt has {known} known and {unknown} unknown mass records.")'),
    "State the complete-pair scatter count and a no-causality limitation beside its chart.",
    example('part=df.dropna(subset=["flipper_length_mm","body_mass_g"])\nfig,ax=plt.subplots(); ax.scatter(part["flipper_length_mm"],part["body_mass_g"])\nprint(f"Observed association uses {len(part)} complete excerpt pairs; it does not establish a causal effect.")'),
    "Every main claim needs a source, denominator, limitation and next check; a plausible explanation is not a demonstrated cause.",
    [("What should a main finding cite?","Its table/chart and represented denominator","Only a colour","A causal claim automatically","Traceable evidence makes a report reviewable."),
     ("Can more plots create absent comparison overlap?","No","Always","Only with a heatmap","Missing design evidence requires an appropriate new check or collection.")])

lesson(5,"2. Build a report figure for the reader's questions",
    "Use complementary panels and inspect labels at their final reading size.",
    [("Report narrative", "Order panels so the reader sees coverage, distributions, comparisons and limitations. A multi-panel figure is useful when each panel answers a different question."),
     ("Accessible encodings and final size", "Reuse Week31's labels, units, stable colours, non-colour cues and export-size checks. A large DPI cannot repair tiny labels or misleading scales.")],
    "The full project has eight panels: mass distribution, species boxes, complete-pair scatter, unknown counts, recorded-sex means, island/species support, collection-year means and a correlation matrix. "
    "That sequence shows both findings and reasons for caution. Keep a zero baseline for ordinary positive bars and a fixed correlation colour range. "
    "The support table's zero counts describe the file, not impossible penguin populations. Year lines compare collection summaries, not matched individual growth. "
    "Inspect the PNG and the accompanying tables together. A static figure cannot carry every exact value; the CSV files and report text provide the detailed audit trail.",
    'fig,axs=plt.subplots(2,2,layout="constrained")\n# One explicit question and unit per panel.',
    example('fig,axs=plt.subplots(1,3,figsize=(10,3.5),layout="constrained"); known=df["body_mass_g"].dropna(); axs[0].hist(known.to_numpy(dtype=float),bins=5); axs[0].set(title="Distribution",xlabel="Mass g",ylabel="Known records"); means=df.groupby("species")["body_mass_g"].mean(); axs[1].bar(means.index,means.values); axs[1].set(title="Group means",ylabel="Mass g"); missing=df[["body_mass_g","sex"]].isna().sum(); axs[2].bar(missing.index,missing.values); axs[2].set(title="Unknown evidence",ylabel="Records")\nfor ax in axs[1:]: ax.tick_params(axis="x",labelrotation=20)\nprint("Complementary panels:",len(fig.axes))'),
    "The three panels use different quantities, so they do not share a misleading common y scale. Units and denominators are visible rather than delegated to a vague title.",
    ('plt.subplots(1,2,sharey=True)  # grams in one, counts in the other', 'plt.subplots(1,2,sharey=False)  # label grams and counts separately', "Shared numeric scales do not make unlike units comparable."),
    "Make two panels: known mass histogram and unknown sex count. Print their different y-axis labels.",
    example('fig,axs=plt.subplots(1,2,layout="constrained"); axs[0].hist(df["body_mass_g"].dropna().to_numpy(dtype=float),bins=5); axs[0].set(xlabel="Mass g",ylabel="Known mass records"); axs[1].bar(["Unknown sex"],[int(df["sex"].isna().sum())]); axs[1].set_ylabel("Unknown-sex records")\nprint([ax.get_ylabel() for ax in axs])'),
    "Create grouped mean/median bars with a legend and a0 baseline; print the lower axis limit.",
    example('summary=df.groupby("species")["body_mass_g"].agg(["mean","median"]); x=np.arange(len(summary))\nfig,ax=plt.subplots(); ax.bar(x-.18,summary["mean"],.35,label="Mean"); ax.bar(x+.18,summary["median"],.35,label="Median"); ax.set(xticks=x,xticklabels=summary.index,ylabel="Mass g",ylim=(0,6000)); ax.legend()\nprint(ax.get_ylim()[0])'),
    "A report figure should answer complementary questions with clear scales and a detailed data trail alongside it.",
    [("Can one shared y-axis sensibly label grams and record counts?","No","Always","Only at high DPI","The measurement meanings differ."),
     ("What supplements a static overview with exact evidence?","The tables, counts and report text","Only more colours","A larger file name","The audit trail carries values that a picture cannot show precisely.")])

lesson(5,"3. Assemble the dataset-specific audited preparation",
    "Run the reusable pipeline pattern with explicit penguin rules and no silent row removal.",
    [("load_tokens; clean_tokens", "These are our own project functions, not pandas builtins. The first checks CSV structure; the second returns a typed table, token-change ledger and decisions while preserving source rows."),
     ("Source contract scope", "The project expects the pinned simplified eight-column schema, documented NA tokens, known species/islands and years2007–2009. Positive finite measurements are required when known. Unknown tokens, wrong widths and malformed values stop for review.")],
    "Read the function in stages rather than memorising it: validate header/width, preserve tokens, apply declared formatting rules, convert documented unknowns, validate fields, assign source positions and retain review flags. "
    "The audit records old/new tokens and rule names. This source should not need guessed species or imputed masses. "
    "If a future file violates the source contract, the program stops instead of fabricating a clean-looking result. A bounded valid-looking value is still not independently proven biologically accurate. "
    "The example runs the full preparation on the real twelve-row excerpt; the standalone project runs the same functions on all344 original rows.",
    'raw=load_tokens(text)\ncleaned,audit,decisions=clean_tokens(raw)',
    chart(clean(CLEAN_CORE)+'raw=load_tokens('+repr(EXCERPT)+')\ndf,audit,decisions=clean_tokens(raw)\nfig,ax=plt.subplots(figsize=(7,3.5),layout="constrained"); unknown=df[COLS].isna().sum(); ax.barh(unknown.index,unknown.values); ax.set(xlabel="Unknown records retained",title="Audited excerpt preparation")\nprint("Rows/deleted/imputed:",decisions["retained_rows"],decisions["deleted_rows"],decisions["imputed_values"])\nprint("Logged token actions:",len(audit))'),
    "No row is deleted or imputed. The audit includes legitimate documented-NA actions; an action count is not a count of source errors corrected.",
    ('# Call every missing-token conversion a corrected bad measurement', '# Label documented unknown conversion separately from source errors or repairs', "Changing representation does not recover an unknown measurement."),
    "Run preparation on the excerpt, prove the raw table is unchanged and draw known/unknown mass counts.",
    chart(clean(CLEAN_CORE)+'raw=load_tokens('+repr(EXCERPT)+')\nbefore=raw.copy(deep=True); df,audit,decisions=clean_tokens(raw)\nfig,ax=plt.subplots(); ax.bar(["Known","Unknown"],[int(df["body_mass_g"].notna().sum()),int(df["body_mass_g"].isna().sum())])\nprint("Raw unchanged:",raw.equals(before))'),
    "Change one derived raw-copy mass token to 'heavy'; catch the validation error and keep the unmodified source available.",
    chart(clean(CLEAN_CORE)+'raw=load_tokens('+repr(EXCERPT)+')\nchanged=raw.copy(); changed.loc[0,"body_mass_g"]="heavy"\nfig,ax=plt.subplots(); ax.bar(["Retained source rows"],[len(raw)])\ntry:\n    clean_tokens(changed)\nexcept ValueError:\n    print("Invalid mass refused; original token:",raw.loc[0,"body_mass_g"])'),
    "An audited pipeline makes scope and changes reviewable; a tidy output is not permission to erase raw evidence.",
    [("Are load_tokens and clean_tokens pandas builtins?","No; they are project functions","Always","Only on Windows","Their names describe our dataset-specific contract."),
     ("Does converting NA recover a measured mass?","No","Always","Only after validation","It preserves an explicitly unknown outcome.")])

lesson(5,"4. Generate an executive summary from checked values",
    "Write the main answer first, then its scope and unresolved explanation.",
    [("Executive summary", "A short summary should lead with the observed answer, include the represented sample/units, state the most important limitation and identify a next check. Generate its numbers from validated tables instead of manually retyping them."),
     ("Finding consistency checks", "The text, tables and chart must use the same inclusion rules and counts. A source hash and fixed code help reproduce values, but the text still needs review for unsupported interpretation.")],
    "A concise reader-facing summary is not a log of every function call. Say which recorded group has the largest known-mass mean and give the supporting n and value. "
    "Then state missingness and the observational collection's limits. An unexplained island comparison or a year growth story would overreach. "
    "Generate the sentence from the same table used in the charts so a changed input cannot leave stale numbers in the narrative. "
    "The full project writes report.md with an executive paragraph, eight panel interpretations, denominator and decision details, sensitivity findings, source attribution and next checks.",
    'winner=summary["mean"].idxmax()\ntext=f"Among known outcomes, {winner} has the largest recorded group mean..."',
    example('summary=df.groupby("species")["body_mass_g"].agg(["count","mean"]); winner=summary["mean"].idxmax(); mean=float(summary.loc[winner,"mean"]); n=int(summary.loc[winner,"count"])\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(summary.index,summary["mean"]); ax.set_ylabel("Known mass g")\nprint(f"In this twelve-row excerpt, {winner} has the largest observed known-mass mean ({mean:.1f}g; n={n}).")\nprint("The sample and species/island composition do not identify a causal island effect.")'),
    "The summary starts with an answer rather than library names. The scope and causal limitation stay attached to that answer.",
    ('print("All Gentoo everywhere are heavier because of this island")', 'print("The recorded known-mass groups differ; source scope and composition limit explanation")', "A summary should not turn a sample statistic into a universal individual or causal claim."),
    "Generate a source/known/unknown mass sentence directly from counts and show the two outcome-availability bars.",
    example('known=int(df["body_mass_g"].notna().sum()); unknown=int(df["body_mass_g"].isna().sum())\nfig,ax=plt.subplots(); ax.bar(["Known","Unknown"],[known,unknown])\nprint(f"Of {len(df)} excerpt records, {known} have known mass and {unknown} do not.")'),
    "Check that your generated winner equals the largest bar's source-table mean and print the result.",
    example('means=df.groupby("species")["body_mass_g"].mean(); winner=means.idxmax()\nfig,ax=plt.subplots(); bars=ax.bar(means.index,means.values)\nprint("Text/chart agree:",bool(np.isclose(means.loc[winner],max(b.get_height() for b in bars))))'),
    "Lead with a supported result, generate numbers from checked tables and keep limitations and next steps beside the claim.",
    [("Where should narrative numbers come from?","The validated summary tables","Memory alone","The largest-looking colour","Shared data reduces stale or inconsistent reporting."),
     ("Should an executive summary list every library call first?","No; lead with the answer and scope","Always","Only with real data","Implementation details should not obscure the reader's decision.")])

CAPSTONE_SETUP=clean(CLEAN_CORE)+clean(REPORT_CORE)+'raw=load_tokens('+repr(EXCERPT)+')\ndf,audit,decisions=clean_tokens(raw)\ntables,facts=summarize(df)\n'

lesson(5,"5. Milestone: a complete offline penguin EDA report",
    "Reproduce the real-data investigation with source, decisions, charts, findings and limitations.",
    [("Full project versus inline walkthrough", "The self-contained inline example runs the same pipeline on the twelve-row excerpt. The downloadable eda_report.py uses the retained344-row penguins.csv. The two scopes are labelled separately; do not copy excerpt values into the full report."),
     ("Palmer Penguins source", "The simplified table is distributed by palmerpenguins from data collected by Kristen Gorman and Palmer Station LTER, with CC0 data terms. SOURCE.md records the exact repository revision, SHA-256 and credits; no artwork is copied."),
     ("Report bundle contract", "The project produces17 files in a new destination: cleaned records, audits/decisions, coverage/categories, grouped/support/year/correlation/sensitivity tables, review flags, an eight-panel PNG, summary JSON and report Markdown. Existing inputs and bundles are retained.")],
    "The full source has344 records:152 Adelie,68 Chinstrap and124 Gentoo. Mass is known in342 records and recorded sex is unknown in11. "
    "Among known masses, the full sample's mean is about3700.7g for Adelie,3733.1g for Chinstrap and5076.0g for Gentoo, with known n151,68,123. This is a genuine descriptive subgroup difference in the recorded data, not a causal effect or a statement about every individual. "
    "The report shows distributions, complete paired relationships, species/sex groups, island support and year composition. It compares mean/median and known-sex inclusion choices, keeps unknowns and flags, and documents what cannot be identified. "
    "Run the full project locally and read report.md alongside its CSV tables. Explain each main finding and exclusion; then change an explicit question or sensitivity rule in a copy, retain the original output and compare a new bundle. "
    "No test is added merely to create a significance story. These are descriptive exploratory findings; confirmation would need appropriate independent evidence and design. The existing Day7 Review & rest shuffles all56 practice prompts from this week.",
    'raw=load_tokens(local_text)\ndf,audit,decisions=clean_tokens(raw)\ntables,facts=summarize(df)\nfig=overview(df,tables)',
    chart(CAPSTONE_SETUP+'fig=overview(df,tables)\nprint("INLINE EXCERPT ONLY: rows",facts["rows"],"known mass",facts["known_mass"])\nprint("Deleted/imputed:",decisions["deleted_rows"],decisions["imputed_values"])\nprint("Source layers and denominators remain separate")'),
    "This overview is explicitly a twelve-row walkthrough. The standalone run recomputes the real full-source counts and findings; it never substitutes the excerpt for the344-row investigation.",
    ('# Present the twelve-row overview as the complete344-row analysis', '# Run eda_report.py on the retained full CSV and label every artifact with its actual scope', "A real dataset excerpt remains an excerpt, even when its code is reproducible."),
    "Run the excerpt pipeline and print source, known-mass, known-sex/mass and complete-pair counts beside its overview.",
    chart(CAPSTONE_SETUP+'fig=overview(df,tables)\nprint({k:facts[k] for k in ["rows","known_mass","known_sex_mass","flipper_mass_pairs"]})'),
    "Convert a copied excerpt's mass to kilograms for one chart, then prove the cleaned source still holds grams; do not change the report contract silently.",
    chart(CAPSTONE_SETUP+'known=df["body_mass_g"].dropna(); kg=known/1000\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.hist(kg,bins=5); ax.set(xlabel="Mass kg (display conversion)",ylabel="Known excerpt records")\nprint("First source grams/display kg:",float(known.iloc[0]),float(kg.iloc[0]))'),
    "Week34 mastery: question, provenance, profile, audited preparation, variable/group analysis, sensitivity and a reproducible report with supported findings and clear limits.",
    [("How many rows does the full retained source contain?","344","12","342","The inline walkthrough has12; known mass has342; the source has344."),
     ("What does a missing mass mean here?","Unknown, retained in the cleaned table","Zero grams","An automatically invalid bird","NA is the documented source evidence state."),
     ("Does the full known-mass mean ordering prove a causal island effect?","No","Always","Only if Gentoo is largest","Species/island support and the observational design limit explanation."),
     ("What links a changed token to evidence?","Source position, column, old/new token and rule","Only the final plot","A new random seed","The audit ledger makes decisions traceable."),
     ("Should equal measurement rows be deleted automatically?","No","Always","Only above344 rows","Feature equality is not specimen identity."),
     ("Can a mass-only analysis use unknown-sex rows?","Yes, if mass is known","Never","Only after guessing sex","Required fields depend on the question."),
     ("What does an empty support cell prove?","No recorded rows for that combination","Biological impossibility","A0g mean","Observed support is not a universal population statement."),
     ("Do year-level means establish same-bird growth?","No","Always","Only if sorted","The simplified table does not supply matching identities."),
     ("What must accompany a correlation matrix?","Pair counts, scope and shape/group checks","A causal label","Only a p-value","Coefficients alone hide denominators and structure."),
     ("What does equal-known-sex weighting estimate?","A stated descriptive mix target","The true population mean automatically","A causal sex intervention","Weighting changes the question and needs subgroup support."),
     ("How should sensitivity outcomes be reported?","With all compared rules, counts and estimates","Only the largest difference","Delete inconvenient alternatives","The purpose is transparency about analysis choices."),
     ("Where should another full report run be saved?","A new bundle directory","Over the raw CSV","Silently over the previous run","The project retains inputs and earlier results.")])

PROJECT='''"""Week34: audited offline exploratory analysis of a pinned penguin CSV."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
''' + clean(CLEAN_CORE) + clean(REPORT_CORE) + '''
def narrative(facts,tables,decisions,digest):
    winner=facts["largest_observed_mean_species"]
    estimates="; ".join(f"{s}: {facts['species_mean_mass_g'][s]:.1f}g, n={facts['species_known_mass'][s]}"
        for s in facts["species_mean_mass_g"] if facts["species_mean_mass_g"][s] is not None)
    return "\\n".join([
        "# Palmer Penguins — descriptive EDA report",
        "## Executive summary",
        f"Among {facts['known_mass']} known-mass records from {facts['rows']} source rows, {winner} has the largest observed species mean. Recorded means: {estimates}. "
        +f"Mass is unknown in {facts['unknown_mass']} rows and recorded sex in {facts['unknown_sex']}. "
        +"These historical observations do not isolate an island effect, establish matched-bird growth or describe an Antarctic census. Check collection/identity metadata and comparison support before causal or population claims.",
        "## Five questions and evidence",
        "1. Which evidence is available? profile.csv and category_counts.csv reconcile source/known/unknown counts.",
        "2. How does mass vary? species_mass.csv and overview panels1–2 show distributions and centres; no automatic outlier removal.",
        f"3. How do flippers and mass relate? {facts['flipper_mass_pairs']} complete pairs; pooled Pearson r={facts['pooled_flipper_mass_r']:.4f}. Pair counts and species-specific coefficients are supplied; association is not cause.",
        "4. How do species/recorded-sex groups compare? species_sex_mass.csv retains group counts and unknown-sex evidence. standardised_mass.csv answers an explicitly equal-known-sex-weight target, not a population or causal effect.",
        "5. Which island comparisons are supported? support_species_island.csv reports recorded combinations; a zero count is not a0g outcome or biological impossibility.",
        "## Eight-panel reading guide",
        "1. Histogram: known mass in grams; unknown outcomes excluded from this picture but retained in the ledger.",
        "2. Boxes: species distributions, not proof that all individuals in one species exceed every other individual.",
        "3. Scatter: coordinates stay paired; species clusters can drive pooled association.",
        "4. Missingness: documented unknowns, not zeros or proven invalid records.",
        "5. Recorded-sex means: use known sex+mass only; subgroup counts are in the CSV.",
        "6. Support: species/island mixture limits island-effect interpretation; absent cells remain unobserved outcomes.",
        "7. Collection years: repeated cross-sectional summaries, not verified individual trajectories; inspect year/species counts.",
        "8. Correlations: fixed-1 to1 scale, pairwise known observations; undefined values remain undefined.",
        "## Decisions and sensitivity",
        f"Retained {decisions['retained_rows']} of {decisions['source_rows']} rows; deleted {decisions['deleted_rows']}; imputed values {decisions['imputed_values']}. "
        +f"Retained IQR-flag rows:{decisions['iqr_flag_rows']}; equal-value candidate rows:{decisions['duplicate_candidate_rows']}. Neither is automatic error or identity evidence.",
        f"Known sex+mass subset:{facts['known_sex_mass']} rows, compared with all {facts['known_mass']} known masses in sensitivity.csv. Compare both mean and median ordering and subgroup counts; do not silently select a preferred result.",
        "The source's simplified table lacks identity metadata for independently checking matched individuals or every sampling assumption. Unknown-value mechanisms are not identified by the missingness display.",
        "No causal test, automatic significance search or verified random-population inference is claimed. Reasonable follow-up includes raw metadata review and new comparisons with appropriate support/design.",
        "## Provenance and reproduction",
        "Source: Horst, Hill & Gorman (2020), palmerpenguins; data collected by Kristen Gorman and Palmer Station LTER. https://allisonhorst.github.io/palmerpenguins/ ; https://doi.org/10.1371/journal.pone.0090081 ; CC0 data terms. See SOURCE.md.",
        "Input SHA-256: "+digest,
        "Reproduce with the retained CSV, this script and the documented environment. Use a fresh output bundle; keep raw bytes and earlier reports.",
        ""]) 

def publish(source,destination):
    source=Path(source); destination=Path(destination)
    if destination.exists() or not destination.parent.is_dir(): raise ValueError("Choose a new bundle in an existing parent")
    blob=source.read_bytes()
    if len(blob)>1024*1024: raise ValueError("Learning input exceeds1MiB")
    raw=load_tokens(blob.decode("utf-8-sig")); df,audit,decisions=clean_tokens(raw); tables,facts=summarize(df)
    digest=hashlib.sha256(blob).hexdigest(); facts["source_sha256"]=digest
    facts["source_url"]="https://allisonhorst.github.io/palmerpenguins/"
    report=narrative(facts,tables,decisions,digest)
    with TemporaryDirectory(prefix="studyhub-penguin-eda-",dir=destination.parent) as temp:
        folder=Path(temp)
        df.to_csv(folder/"cleaned.csv",index=False,lineterminator="\\n")
        audit.to_csv(folder/"audit_changes.csv",index=False,lineterminator="\\n")
        for name,frame in tables.items():
            include_index=name not in ["category_counts","sensitivity"]
            frame.to_csv(folder/(name+".csv"),index=include_index,lineterminator="\\n")
        df.loc[df["duplicate_value_candidate"]|df["mass_iqr_flag"]].to_csv(folder/"review_flags.csv",index=False,lineterminator="\\n")
        (folder/"decisions.json").write_text(json.dumps(decisions,indent=2,allow_nan=False),encoding="utf-8")
        (folder/"summary.json").write_text(json.dumps(facts,indent=2,allow_nan=False),encoding="utf-8")
        (folder/"report.md").write_text(report,encoding="utf-8")
        fig=overview(df,tables)
        try: fig.savefig(folder/"overview.png",dpi=150,facecolor="white")
        finally: plt.close(fig)
        os.rename(folder,destination)
    return facts

def main(argv=None):
    parser=argparse.ArgumentParser(description="Week34 audited offline penguin EDA")
    parser.add_argument("source"); parser.add_argument("destination");args=parser.parse_args(argv)
    try: facts=publish(args.source,args.destination)
    except (ValueError,OSError,csv.Error) as error: parser.exit(1,"EDA report stopped: "+str(error)+"\\n")
    print("Published17 files; source rows",facts["rows"],"known mass",facts["known_mass"])
    return 0

if __name__=="__main__": raise SystemExit(main())
'''


def write():
    target=ROOT/"study-hub.html";original=target.read_bytes().decode("utf-8")
    start=original.index("const DAY_TEACH = {");end=original.index("\n};\n\nconst REST_DAY",start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS): raise RuntimeError("Week34 already exists; refusing overwrite")
    with tempfile.TemporaryDirectory(prefix="studyhub-w34-verification-") as temp:
        manifest=Path(temp)/"examples.json";result=Path(temp)/"results.json"
        manifest.write_text(json.dumps([code for code,_,_ in JOBS]),encoding="utf-8")
        subprocess.run([sys.executable,str(ROOT/"scripts"/"python-example-worker.py"),str(manifest),str(result)],
            check=True,timeout=300,env={**os.environ,"MPLBACKEND":"Agg","OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1","PYTHONDONTWRITEBYTECODE":"1"})
        results=json.loads(result.read_text(encoding="utf-8"))
    for (_,destination,picture),result in zip(JOBS,results,strict=True):
        destination["v" if destination["t"]=="out" else "out"]=result["out"]
        if picture is not None:
            if not result["png"]: raise RuntimeError("Missing example image")
            picture["src"]="data:image/png;base64,"+result["png"]
    DAYS["34.0"]["parts"][0]["sections"].insert(3,section("sh",'python -m pip install "numpy>=2,<3" "pandas>=3,<4" "matplotlib>=3.10,<3.11"',note="Reuse your existing practice environment. Initial installation needs internet; this week's self-contained examples, embedded chart pictures and supplied project work offline afterward. Verified with NumPy2.3.5, pandas3.0.1 and Matplotlib3.10.9. Python runs locally outside this website."))
    DAYS["34.5"]["parts"][4]["sections"].append(section("sh","python eda_report.py penguins.csv eda-run-01\npython eda_report.py --help",note="From docs/python-week34. Retain penguins.csv, eda_report.py, SOURCE.md and README.md. Use eda-run-02 for another run. The CLI uses the full344-row source; inline walkthroughs use a labelled twelve-row excerpt."))
    DAYS["34.5"]["parts"][4]["sections"].append(section("p","Primary references: https://allisonhorst.github.io/palmerpenguins/ · https://www.itl.nist.gov/div898/handbook/eda/section1/eda11.htm · https://pandas.pydata.org/docs/user_guide/missing_data.html · https://pandas.pydata.org/docs/user_guide/merging.html. Original explanations, exercises, executed outputs and chart pictures are embedded for offline learning. Source credits and pinned raw-data hash are included in the project folder."))
    addition="\n".join(json.dumps(k)+": "+json.dumps(v,ensure_ascii=False,indent=2)+"," for k,v in DAYS.items()).replace("</","<\\/")
    prefix=original[:end].rstrip()
    if not prefix.endswith(","):prefix+="," 
    folder=ROOT/"docs"/"python-week34";folder.mkdir(exist_ok=True)
    (folder/"eda_report.py").write_text(PROJECT,encoding="utf-8",newline="\n")
    temporary=target.with_suffix(".html.tmp");temporary.write_bytes((prefix+"\n"+addition+original[end:]).encode("utf-8"));temporary.replace(target)
    print("Added Week34:6 days,28 parts,56 practice prompts,66 explained quiz questions,84 executed outputs and28 embedded chart pictures; all application/storage code unchanged.")


if __name__=="__main__":write()


