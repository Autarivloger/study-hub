"""Add Week 32 without rewriting prior lessons; execute and embed real charts."""
import base64
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DAYS = {f"32.{d}": {"parts": []} for d in range(6)}
POOL = ThreadPoolExecutor(max_workers=4)
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def chart(body):
    return 'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n' + clean(body) + '\nfig.savefig("chart.png", dpi=110)\nplt.close(fig)\n'


def execute(code):
    with tempfile.TemporaryDirectory(prefix="studyhub-w32-") as folder:
        result = subprocess.run([sys.executable, "-c", code], cwd=folder,
            capture_output=True, encoding="utf-8", timeout=90,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "MPLBACKEND": "Agg"})
        if result.returncode:
            raise RuntimeError(result.stderr + "\n" + code)
        if result.stderr.strip():
            raise RuntimeError("Unexpected chart warning: " + result.stderr)
        picture = Path(folder) / "chart.png"
        return result.stdout.replace("\r\n", "\n").rstrip(), picture.read_bytes() if picture.exists() else None


def section(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def evaluated(code, image=None):
    target = section("out", "")
    JOBS.append((POOL.submit(execute, clean(code)), target, image))
    return target


def lesson(day, title, goal, terms, explanation, syntax, example, walkthrough,
           mistake, task, solution, challenge, challenge_code, takeaway, quizzes):
    parts = DAYS[f"32.{day}"]["parts"]
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
        section("ex", task, practiceId=f"32.{day}.{index}.build"),
        section("sol", code=clean(solution), out="", why="Build check: " + takeaway),
        section("ex", "Mini challenge: " + challenge, practiceId=f"32.{day}.{index}.challenge"),
        section("sol", code=clean(challenge_code), out="", why="Challenge check: " + takeaway),
        section("try", q=quizzes[0][0], code="# Predict first; explain your reason before revealing.", a=quizzes[0][1], why=quizzes[0][4]),
        section("checkpoint", lesson={"id": f"course:32.{day}.{index}", "quiz": questions}), section("key", takeaway)
    ]})
    for s in parts[-1]["sections"]:
        if s["t"] == "sol":
            JOBS.append((POOL.submit(execute, s["code"]), s, None))


SMALL = '''
df=pd.DataFrame({
    "track":["Python"]*4+["Japanese"]*4+["Security"]*4,
    "mode":["Solo","Guided","Solo","Guided"]*3,
    "day":[1,2,3,4]*3,
    "minutes":[10,20,30,40,15,25,35,45,20,30,40,50],
    "score":[45,60,65,80,50,65,70,85,55,65,75,90],
    "tasks":[1,2,3,4,2,3,4,5,2,3,5,6]})
'''


def example(body):
    return chart(clean(SMALL)+clean(body))


def plotly_example(body):
    return 'import pandas as pd\nimport plotly.express as px\n'+clean(SMALL)+clean(body)+'''\nfig.write_html("chart.html",include_plotlyjs=True,full_html=True,auto_open=False)
fig.write_image("chart.png",width=900,height=500)
'''


lesson(0,"1. Seaborn translates column names into a chart",
    "Map named DataFrame columns to meaningful visual variables.",
    [("Seaborn; sns", "Seaborn is a statistical plotting library built on Matplotlib. sns is our import alias. It accepts column names from a pandas DataFrame, reducing repetitive preparation and labelling."),
     ("Tidy or long-form data", "A variable has its own column and an observation its own row. Here a row is one fictional practice session; track, minutes and score describe that session."),
     ("data; x; y; hue", "data supplies the table. x and y name coordinate columns. hue maps a column to colour groups and supplies a decoding legend; it is not a mathematical operation on the data.")],
    "Week31 taught the Figure and Axes that own a chart. Seaborn uses those same objects; it adds a convenient way to describe what each column should do. "
    "Read sns.scatterplot(data=df,x='minutes',y='score') as: draw one mark per complete pair of minutes and score from this table. "
    "Adding hue='track' separates subject labels through colour. The library knows column names, but it does not know whether a row means a learner, a session or a monthly average. You must state that grain. "
    "Our twelve-row sample is fictional practice-session data, not evidence about real learners or the comparative difficulty of languages. The lesson pictures are embedded offline. "
    "Use the supplied table rather than sns.load_dataset: that helper may download data from the internet and is unnecessary for these exercises. Run snippets in a fresh practice folder because they reuse chart.png.",
    'sns.scatterplot(data=df,x="minutes",y="score",hue="track",ax=ax)',
    example('''
fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")
sns.scatterplot(data=df,x="minutes",y="score",hue="track",ax=ax)
ax.set(title="Twelve fictional practice sessions",xlabel="Minutes per session",ylabel="Score (out of 100)")
print("Rows:",len(df))
print("Tracks:",sorted(df["track"].unique().tolist()))
'''),
    "Seaborn names legend categories from the track column. Matplotlib still sets the final title and unit labels. A visible upward association is descriptive; the sample cannot establish that extra minutes caused higher scores.",
    ('sns.scatterplot(data=df,x="minutes",y="result")  # no result column', 'sns.scatterplot(data=df,x="minutes",y="score")', "Semantic names must match real columns in the supplied table."),
    "Plot tasks against score, colour by track and print the number of source observations.",
    example('fig,ax=plt.subplots(layout="constrained")\nsns.scatterplot(data=df,x="tasks",y="score",hue="track",ax=ax)\nax.set(xlabel="Tasks per session",ylabel="Score")\nprint(len(df))'),
    "Keep only Python sessions, draw minutes against score and print the retained row count.",
    example('subset=df.loc[df["track"].eq("Python")]\nfig,ax=plt.subplots()\nsns.scatterplot(data=subset,x="minutes",y="score",ax=ax)\nprint("Python sessions:",len(subset))'),
    "Seaborn draws named variables; you remain responsible for observation grain, units and interpretation.",
    [("What does hue='track' do?","Maps track categories to colour","Calculates a correlation","Downloads tracks","The legend describes the visual category mapping."),
     ("What is one row in this example?","One fictional practice session","A whole population","A guaranteed unique learner","The data contract defines a row, not the plotting function.")])

lesson(0,"2. Axes-level and figure-level functions own different things",
    "Compose Axes functions and manage a figure-level grid through its returned object.",
    [("Axes-level function", "scatterplot, histplot and boxplot draw on one Matplotlib Axes. Supply ax= to select the destination and compose them inside your own subplots."),
     ("Figure-level function; grid object", "relplot, displot and catplot create and manage their own figure and facets. They return a grid object with .figure and .axes; do not pass ax= expecting to embed them in an existing area."),
     ("height; aspect", "Figure-level functions size each facet using height in inches and aspect as width divided by height. This differs from the total figsize of a Matplotlib Figure.")],
    "The two interfaces are both useful. Use an Axes-level function when you already have a planned report layout, just as you used ax.plot in Week31. "
    "Use a figure-level function when repeated panels should be arranged by column values. Calling it after plt.subplots does not make it draw into that earlier Axes. "
    "Retain the returned grid, customise it with grid methods and save grid.figure. Closing a different current figure can leave the real chart open. "
    "The paired example uses two Axes-level functions under one Figure. Later days develop figure-level facets and compare them with manual layouts. Seaborn does not replace the lifecycle rule: create, draw, save the named figure, then close that figure.",
    'sns.histplot(data=df,x="minutes",ax=axs[0])\ng=sns.relplot(data=df,x="minutes",y="score",col="track")\ng.figure.savefig("facets.png")',
    example('''
fig,axs=plt.subplots(1,2,figsize=(7,3),layout="constrained")
sns.scatterplot(data=df,x="minutes",y="score",ax=axs[0])
sns.histplot(data=df,x="minutes",bins=[0,20,40,60],ax=axs[1])
axs[0].set(title="Relationship",xlabel="Minutes",ylabel="Score")
axs[1].set(title="Distribution",xlabel="Minutes",ylabel="Sessions")
print("Axes in caller's figure:",len(fig.axes))
'''),
    "Both functions honour their ax argument, so the Figure contains exactly two plotting areas. The histogram counts12 session rows; it does not summarise a different population.",
    ('fig,ax=plt.subplots()\nsns.relplot(data=df,x="minutes",y="score",ax=ax)', 'sns.scatterplot(data=df,x="minutes",y="score",ax=ax)', "relplot owns its Figure; scatterplot composes on a supplied Axes."),
    "Create one row of two Axes and put a score histogram beside a tasks/score scatter. Print the Axes count.",
    example('fig,axs=plt.subplots(1,2,layout="constrained")\nsns.histplot(data=df,x="score",bins=4,ax=axs[0]); sns.scatterplot(data=df,x="tasks",y="score",ax=axs[1])\nprint(len(fig.axes))'),
    "Use relplot to create one minutes/score panel per mode. Save its returned Figure and print the number of facets.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.relplot(data=df,x="minutes",y="score",col="mode",height=3,aspect=1)
g.figure.savefig("chart.png"); print("Facets:",len(g.axes.flat)); plt.close(g.figure)
''',
    "Use Axes-level functions for a destination you own; use the returned grid when a figure-level function owns the layout.",
    [("Which accepts an existing ax for composition?","sns.scatterplot","sns.relplot as a grid owner","sns.displot as a grid owner","Axes-level calls target one existing plotting area."),
     ("What does relplot height control?","The height of each facet","The number of input rows","The maximum score","Total figure dimensions also depend on facet count and aspect.")])

lesson(0,"3. Reshape wide measurements without changing their meaning",
    "Use melt to distinguish identifiers, measurement names and values.",
    [("melt; id_vars; var_name; value_name", "DataFrame.melt turns selected measurement columns into long rows. id_vars retains identifiers; var_name stores the old column names and value_name stores their measurements."),
     ("Comparability of stacked measurements", "A long table does not make unlike units interchangeable. Before and After scores share a unit; minutes and score do not become one valid measurement merely because both are numeric.")],
    "Wide data often puts repeated measurements in separate columns. A table with learner, Before and After can be drawn with hue='stage' after reshaping. "
    "Each new row now means one learner-stage measurement. The row count doubles, but the number of independent learners has not doubled. "
    "Keep the learner ID during melt so pairing is recoverable. A plot that ignores that ID can hide which two values came from the same person. "
    "Do not melt minutes and scores into a single unlabeled Value axis for convenient code: they use different units. The data shape should serve a clearly defined question, not erase meaning.",
    'long=wide.melt(id_vars="learner",var_name="stage",value_name="score")',
    chart('''
wide=pd.DataFrame({"learner":["L1","L2","L3"],"Before":[50,60,70],"After":[60,65,80]})
long=wide.melt(id_vars="learner",var_name="stage",value_name="score")
fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")
sns.stripplot(data=long,x="stage",y="score",jitter=False,ax=ax)
ax.set(title="Same three learners measured twice",ylabel="Score (same scale)")
print("Measurements:",len(long),"Learners:",long["learner"].nunique())
'''),
    "The six marks are six measurements from three learners. The plot shows positions, not a statistical significance test. Later you will retain pairing with units in individual trajectories.",
    ('long=wide.drop(columns="learner").melt()  # identity lost', 'long=wide.melt(id_vars="learner",var_name="stage",value_name="score")', "Keeping IDs preserves paired and repeated-measurement information."),
    "Melt two learners' quiz1=[40,60], quiz2=[50,70] scores into long form. Plot the scores by quiz and print measurement and learner counts.",
    chart('wide=pd.DataFrame({"learner":["A","B"],"quiz1":[40,60],"quiz2":[50,70]})\nlong=wide.melt(id_vars="learner",var_name="quiz",value_name="score")\nfig,ax=plt.subplots()\nsns.stripplot(data=long,x="quiz",y="score",jitter=False,ax=ax)\nprint(len(long),long["learner"].nunique())'),
    "From that long table retain quiz2 only, plot one mark per learner and print the two scores.",
    chart('wide=pd.DataFrame({"learner":["A","B"],"quiz1":[40,60],"quiz2":[50,70]})\nlong=wide.melt(id_vars="learner",var_name="quiz",value_name="score")\npart=long.loc[long["quiz"].eq("quiz2")]\nfig,ax=plt.subplots()\nsns.scatterplot(data=part,x="learner",y="score",ax=ax)\nprint(part["score"].tolist())'),
    "Reshaping changes table grain, not measurement units or the number of independent people.",
    [("Three learners measured twice become how many independent learners?","Still three","Six automatically","One","Measurement rows and independent units differ."),
     ("Why retain learner in id_vars?","To preserve identity and pairing","To convert scores into minutes","To sort colours","Otherwise the association between repeated measurements can be lost.")])

lesson(0,"4. Check the summary and scope the theme",
    "Inspect a plotted summary and use temporary appearance settings.",
    [("set_theme; axes_style; plotting_context", "set_theme changes global plotting defaults. axes_style and plotting_context can be used with with to scope appearance and reading-size choices. A Matplotlib rc_context can scope a complete theme around its creation."),
     ("Estimator and errorbar preview", "Some Seaborn functions compute summaries rather than plotting every row. For the first summary example, estimator='mean' chooses the mean and errorbar=None explicitly omits uncertainty intervals. Day3 explains what those choices do and do not mean.")],
    "A higher-level function can calculate something before it draws. That convenience deserves an audit: compute the same mean with pandas and read the resulting values. "
    "The mean is a descriptive summary of these rows. Omitting an uncertainty interval is not proof of precise population knowledge; we are not making that claim from fictional data. "
    "Theme defaults should also be explicit. In a reusable script, scope them so unrelated charts do not unexpectedly inherit larger fonts or different backgrounds. "
    "Compare three familiar Matplotlib questions in your practice: category mean, numeric distribution and paired relationship. Seaborn helps express column roles, while Matplotlib still handles labels, limits and exporting.",
    'with sns.axes_style("whitegrid"),sns.plotting_context("notebook"):\n    sns.barplot(data=df,x="track",y="score",estimator="mean",errorbar=None,ax=ax)',
    example('''
with sns.axes_style("whitegrid"),sns.plotting_context("notebook"):
    fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")
    sns.barplot(data=df,x="track",y="score",estimator="mean",errorbar=None,ax=ax)
    ax.set(title="Descriptive session means, no inferential interval",ylabel="Mean score",ylim=(0,100))
print(df.groupby("track",sort=True)["score"].mean().to_dict())
'''),
    "The means differ because the fictional rows differ. The chart does not establish a track's teaching quality. errorbar=None is a disclosed choice; Day3 contrasts it with a measure of observed spread.",
    ('sns.barplot(data=df,x="track",y="score")  # assume raw scores', 'sns.barplot(data=df,x="track",y="score",estimator="mean",errorbar=None)', "Know whether each mark is a row or a calculated summary, and state the interval policy."),
    "Plot mean minutes per track with no interval and print the matching pandas means.",
    example('fig,ax=plt.subplots()\nsns.barplot(data=df,x="track",y="minutes",estimator="mean",errorbar=None,ax=ax)\nprint(df.groupby("track")["minutes"].mean().to_dict())'),
    "Create a histogram inside a scoped ticks style, label its count axis and print the total source row count.",
    example('with sns.axes_style("ticks"):\n    fig,ax=plt.subplots(); sns.histplot(data=df,x="minutes",bins=[0,20,40,60],ax=ax)\n    ax.set(ylabel="Sessions (count)")\nprint(len(df))'),
    "Inspect the statistic before trusting the chart; scope theme settings and keep semantic choices visible.",
    [("What does a default category bar often summarise?","A mean rather than each raw row","Always a row count","Only the maximum","Functions have statistical defaults that must match the question."),
     ("Does errorbar=None establish a precise population mean?","No","Yes","Only on white backgrounds","It omits intervals; it supplies no new evidence.")])

lesson(1,"1. Histogram groups need common bin edges",
    "Compare distributions using the same intervals and known counts.",
    [("histplot; bins; multiple", "histplot counts values in numeric intervals. Explicit bins define the edges; hue separates groups. multiple='layer' overlaps groups, 'dodge' places group bars beside each other, and 'stack' adds them."),
     ("common_bins", "When comparing subsets, common_bins=True requests shared bins. Explicit edges make the interval contract especially clear; separate automatic bins can make comparisons misleading.")],
    "You met histogram intervals in Week31. Seaborn adds a grouped distribution in one call, but bin choices still control the visual story. "
    "Use the same edges for every track. If one chart uses ten-minute intervals and another twenty-minute intervals, a taller bar may reflect the wider interval rather than more concentrated observations. "
    "Layered bars can hide each other, so compare transparency, dodge or faceting according to the question. Start with counts when you need to see the number of sessions. "
    "Our tracks have equal sample sizes here, which makes counts easier to compare. Always inspect sample sizes when they differ. Choosing common bins does not make an unrepresentative sample representative.",
    'sns.histplot(data=df,x="minutes",hue="track",bins=[0,20,40,60],multiple="dodge",common_bins=True,ax=ax)',
    example('fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nsns.histplot(data=df,x="minutes",hue="track",bins=[0,20,40,60],multiple="dodge",common_bins=True,ax=ax)\nax.set(title="Shared intervals across tracks",ylabel="Sessions (count)")\nprint(df.groupby("track").size().to_dict())'),
    "All bars refer to the same0–20,20–40 and40–60 intervals. Dodge separates tracks within each interval. The printed sizes explain the count denominator.",
    ('# Compare separate automatic histograms with unrelated edges', 'sns.histplot(data=df,x="minutes",hue="track",bins=[0,20,40,60])', "Agree on bins before comparing bar heights."),
    "Plot scores by track with edges40,60,80,100 and side-by-side bars. Print the total row count.",
    example('fig,ax=plt.subplots()\nsns.histplot(data=df,x="score",hue="track",bins=[40,60,80,100],multiple="dodge",ax=ax)\nprint(len(df))'),
    "Draw a single histogram with the same score edges and verify bar heights sum to12.",
    example('fig,ax=plt.subplots()\nsns.histplot(data=df,x="score",bins=[40,60,80,100],ax=ax)\nprint("Represented:",int(sum(p.get_height() for p in ax.patches)))'),
    "Compare histograms under a shared interval and sample-size contract.",
    [("Why share bin edges?","Intervals must mean the same thing across groups","It proves causation","It removes all missing values","Different interval widths can explain different bar heights."),
     ("What does multiple='dodge' do?","Places group bars beside each other within intervals","Sorts source dates","Converts counts to medians","It is a presentation choice for grouped histograms.")])

lesson(1,"2. Count, proportion and density use different denominators",
    "Distinguish bar height from area and state within-group normalisation.",
    [("stat='density'", "Histogram density scales so total bar area integrates to1 under the chosen normalisation. With unequal bin widths, heights are not probabilities; height times width gives the interval's probability mass."),
     ("common_norm", "With hue, common_norm=False normalises each group separately. common_norm=True shares normalisation across groups, weighting their contributions. This differs from common_bins, which controls interval edges.")],
    "Raw counts describe how many recorded observations fall in an interval. A normalised view instead asks about distribution shape or share under a stated denominator. "
    "Density is an area rule, not a percentage label. A narrow interval can have a high density while holding little probability mass. "
    "When every track is normalised independently, their areas each sum to one, even if one track has far fewer sessions. This helps compare shapes but conceals sample-size differences unless those sizes are supplied. "
    "Do not switch to density to make a tiny group appear equally well supported. Print the group counts and say whether the denominator is each group or the full sample.",
    'sns.histplot(data=df,x="minutes",hue="track",stat="density",common_norm=False,bins=[0,20,40,60])',
    example('fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nsns.histplot(data=df,x="minutes",hue="track",stat="density",common_norm=False,bins=[0,20,40,60],element="step",fill=False,ax=ax)\nax.set(title="Each track normalised separately",ylabel="Density per minute")\nprint("Per-track rows:",df.groupby("track").size().to_dict())'),
    "element='step' outlines histogram intervals; fill=False avoids opaque overlap. The y-axis is density per minute, not the percentage of all sessions.",
    ('ax.set_ylabel("Percent")  # after stat="density"', 'ax.set_ylabel("Density per minute")', "A formatter or label must not silently redefine a density as a percentage."),
    "Draw one density histogram of minutes with edges0,20,40,60. Calculate area from rectangle heights and widths and print the rounded total.",
    example('fig,ax=plt.subplots()\nsns.histplot(data=df,x="minutes",bins=[0,20,40,60],stat="density",ax=ax)\narea=sum(p.get_height()*p.get_width() for p in ax.patches)\nprint("Area:",round(area,6))'),
    "Repeat using unequal edges0,10,30,60; prove the total area is still1 rather than summing heights.",
    example('fig,ax=plt.subplots()\nsns.histplot(data=df,x="minutes",bins=[0,10,30,60],stat="density",ax=ax)\nprint("Area:",round(sum(p.get_height()*p.get_width() for p in ax.patches),6))'),
    "For density, interpret area; disclose whether normalisation is per group or across the whole sample.",
    [("What integrates to1 in a normalised density histogram?","Bar area","Sum of heights always","Number of categories","Area is height multiplied by interval width."),
     ("What does common_norm=False do with hue?","Normalises each group separately","Forces every group to have equal rows","Changes bin boundaries only","Equal area does not imply equal sample size.")])

lesson(1,"3. KDE is a smoothing choice, not hidden truth",
    "Explain bandwidth, boundaries and why small discrete samples need caution.",
    [("KDE; bandwidth; bw_adjust", "Kernel density estimation builds a smooth density curve from observations. bw_adjust scales its smoothing bandwidth: smaller values make more local bumps and larger values smooth more strongly."),
     ("cut; clip", "cut=0 limits the drawn KDE range to observed extrema. clip restricts its evaluation range. Neither makes ordinary KDE a boundary-corrected estimator nor proves that unobserved values are impossible.")],
    "A smooth line can look more certain than twelve points deserve. KDE estimates a shape using a smoothing rule; changing that rule can create or remove apparent peaks. "
    "For quantities constrained to be nonnegative, a default smooth curve may extend into impossible negatives. Restricting where it is drawn helps presentation but does not solve all boundary bias. "
    "Very small samples, repeated integer counts and constant groups can be poor fits for KDE. An ECDF or raw-point plot often states the observed evidence more directly. "
    "Compare two bandwidth choices on the same values. Describe what changed in the display and resist declaring multiple learner populations simply because the narrow curve has multiple bumps.",
    'sns.kdeplot(data=df,x="minutes",bw_adjust=0.6,cut=0,ax=ax)',
    example('fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nfor bw in [0.5,1.5]:\n    sns.kdeplot(data=df,x="minutes",bw_adjust=bw,cut=0,label="bw_adjust="+str(bw),ax=ax)\nax.set(title="Same data, different smoothing",ylabel="Estimated density"); ax.legend()\nprint("Observed minutes:",sorted(df["minutes"].unique().tolist()))'),
    "Only smoothing changes, not the observations. A bandwidth label makes that choice visible. The plot is an estimate of a distribution shape, not a directly measured curve.",
    ('sns.kdeplot(data=df,x="minutes",bw_adjust=0.1)  # every bump is a real population', 'sns.kdeplot(data=df,x="minutes",bw_adjust=1,cut=0)', "Inspect sensitivity and the underlying values before interpreting bumps."),
    "Draw a KDE of scores with cut=0 and print the observed minimum and maximum.",
    example('fig,ax=plt.subplots()\nsns.kdeplot(data=df,x="score",cut=0,ax=ax)\nprint(int(df["score"].min()),int(df["score"].max()))'),
    "Compare bw_adjust0.7 and1.4 on a single Axes with a legend; print whether both curves were drawn.",
    example('fig,ax=plt.subplots()\nfor bw in [0.7,1.4]: sns.kdeplot(data=df,x="minutes",bw_adjust=bw,cut=0,label=str(bw),ax=ax)\nax.legend(); print("Two curves:",len(ax.lines)==2)'),
    "Show smoothing sensitivity; a smooth estimate does not add observations or establish real subpopulations.",
    [("What changes when bw_adjust increases?","The smoothing bandwidth increases","New sessions are collected","The scores become probabilities","The same observations generate a smoother estimate."),
     ("Does cut=0 remove all KDE boundary bias?","No; it limits drawing support","Yes","It deletes outliers","Display support and the estimator's boundary behaviour are different issues.")])

lesson(1,"4. ECDF: read a threshold share without bins",
    "Interpret the proportion of observations at or below a threshold.",
    [("ECDF; ecdfplot", "An empirical cumulative distribution shows the observed share at or below each x value. It is a step function using actual observations, without histogram bins or KDE bandwidth."),
     ("Threshold denominator", "For a complete score column, count(score<=threshold)/number of observed scores gives the ECDF height there. With missing scores, the denominator is known scores, and the missing count must be reported.")],
    "If the question is how many recorded sessions scored at most65, a cumulative plot is direct. Move horizontally from65 to the step, then read its vertical proportion. "
    "The right end reaches1 for each independently normalised group; this does not mean every possible learner was sampled. "
    "Repeated values create larger steps because several observations arrive at the same threshold. An ECDF avoids tuning bins or smoothing, but you still need a clear sample definition and missing-data policy. "
    "A high cumulative share at a low score means more of that sample has low scores. It does not mean a stronger teaching method or prove the samples are comparable.",
    'sns.ecdfplot(data=df,x="score",hue="track",ax=ax)\nshare=df["score"].le(65).sum()/df["score"].notna().sum()',
    example('fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nsns.ecdfplot(data=df,x="score",ax=ax)\nax.set(title="Recorded share at or below each score",ylabel="Proportion of observed scores")\nprint("At most65:",round(df["score"].le(65).mean(),3))\nprint("Known scores:",int(df["score"].notna().sum()))'),
    "Seven of twelve scores are at most65, so the printed share is0.583 after rounding. The ECDF steps encode the exact observed count fractions, not inferred population probabilities.",
    ('df["score"].le(65).mean()  # denominator includes missing rows', 'known=df["score"].dropna(); share=known.le(65).mean()', "With unknown scores, compute the threshold share among known values and disclose exclusions."),
    "Plot an ECDF of minutes and print the proportion at most30 minutes.",
    example('fig,ax=plt.subplots()\nsns.ecdfplot(data=df,x="minutes",ax=ax)\nprint("At most30:",round(df["minutes"].le(30).mean(),3))'),
    "Use scores[50,None,70,80], keep the unknown count, and print the known-score share at most70.",
    chart('scores=pd.Series([50,None,70,80]); known=scores.dropna()\nfig,ax=plt.subplots()\nsns.ecdfplot(x=known,ax=ax)\nprint("Unknown:",int(scores.isna().sum()))\nprint("Known share:",round(known.le(70).mean(),3))'),
    "An ECDF answers threshold questions about the observed sample; state the known-value denominator.",
    [("At x=65, what does an ECDF height describe?","Share of observed scores at most65","Mean score","Density at exactly65","The cumulative rule includes observations equal to the threshold."),
     ("Does an ECDF need a bandwidth?","No","Always","Only for integer scores","It uses observed steps rather than a smoothed estimate.")])

lesson(1,"5. Rugs, discrete counts and visible missingness",
    "Add raw-location cues and keep missing-value accounting outside the plot.",
    [("rugplot", "A rug draws a short mark at each observation's location beside an axis. Overlapping marks can conceal repeated values; a rug is a location cue, not a reliable frequency table."),
     ("discrete=True; valid-pair mask", "For integer-valued counts, discrete=True centres histogram bins on integer values. A valid-pair mask retains rows where every plotted coordinate is observed; it preserves row pairing.")],
    "A distribution plot may silently omit missing measurements. That can be an acceptable drawing rule only when you retain an explicit account of what was omitted. "
    "Show the source row count, known-value count and exclusions. A rug helps locate observations but several equal values may occupy the same position. "
    "For a task count, bins centred on integers respect the discrete quantity better than an apparently continuous KDE. Zero tasks is a possible value; a missing task count is a different state. "
    "When comparing two coordinates, drop missingness by row, not separately in each column. The latter can attach one session's minutes to another's score.",
    'valid=df[["minutes","score"]].notna().all(axis=1)\nsns.histplot(data=df,x="tasks",discrete=True,ax=ax)',
    example('fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nsns.histplot(data=df,x="tasks",discrete=True,ax=ax)\nsns.rugplot(data=df,x="tasks",height=0.06,ax=ax)\nax.set(title="Discrete task counts plus raw locations",ylabel="Sessions")\nprint(df["tasks"].value_counts().sort_index().to_dict())'),
    "The table, not the rug's visible tick count, preserves frequencies of repeated values. height controls the rug marks as a fraction of the Axes height.",
    ('x=df["minutes"].dropna(); y=df["score"].dropna()', 'valid=df[["minutes","score"]].notna().all(axis=1)\npaired=df.loc[valid]', "Separate dropping can destroy the original pairing."),
    "Plot a discrete histogram of counts[0,1,1,2,3] plus a rug and print the number of ones.",
    chart('values=pd.Series([0,1,1,2,3])\nfig,ax=plt.subplots()\nsns.histplot(x=values,discrete=True,ax=ax); sns.rugplot(x=values,ax=ax)\nprint("Ones:",int(values.eq(1).sum()))'),
    "Use rows minutes[10,None,30], score[50,60,None]; plot complete pairs and print included/excluded counts.",
    chart('df=pd.DataFrame({"minutes":[10,None,30],"score":[50,60,None]})\nvalid=df[["minutes","score"]].notna().all(axis=1)\nfig,ax=plt.subplots()\nsns.scatterplot(data=df.loc[valid],x="minutes",y="score",ax=ax)\nprint(int(valid.sum()),int((~valid).sum()))'),
    "Keep raw-location cues, integer semantics and missing-data counts distinct.",
    [("Can a rug hide repeated equal values?","Yes","Never","Only if scores are missing","Overlapping marks occupy the same position."),
     ("How should incomplete x/y observations be filtered?","By a joint row mask","Drop each column independently","Replace unknowns with zero silently","A row mask retains coordinate pairing.")])

lesson(2,"1. Countplot counts rows, not people or numeric totals",
    "Choose countplot only when category frequency answers the question.",
    [("countplot; order; hue_order", "countplot displays category row frequencies. order fixes category order and hue_order fixes subgroup order. Neither deduplicates people nor sums another measurement."),
     ("Row frequency versus unique units", "Two sessions from one learner contribute two session rows but only one distinct learner. Counting rows and counting people are different questions.")],
    "A track with more recorded sessions may contain more people, more repeat visits or simply more complete logging. countplot cannot distinguish those explanations. "
    "State the row meaning first. If the question is distinct learners per track, calculate nunique by track and plot that prepared result instead. "
    "A fixed category order makes comparisons stable across charts; sorting labels independently in each facet can change their positions. "
    "The tiny example below uses twelve session rows, four per track. Its bars are counts rather than score means or summed minutes. Avoid relabelling a count axis as Learners without establishing that the source has one row per learner.",
    'sns.countplot(data=df,x="track",order=["Python","Japanese","Security"],ax=ax)',
    example('fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nsns.countplot(data=df,x="track",order=["Python","Japanese","Security"],color="#0072B2",ax=ax)\nax.set(title="Recorded session counts",ylabel="Session rows")\nprint("Counts:",df.groupby("track").size().to_dict())'),
    "Each of the three bars has height4. This is frequency of rows under the declared session grain, not a performance measure.",
    ('sns.countplot(data=df,x="track"); ax.set_ylabel("Revenue")', 'sns.countplot(data=df,x="track"); ax.set_ylabel("Recorded sessions")', "Countplot counts category occurrences, not another numeric column."),
    "Count sessions by mode and print the expected row frequencies.",
    example('fig,ax=plt.subplots()\nsns.countplot(data=df,x="mode",color="#0072B2",ax=ax)\nprint(df.groupby("mode").size().to_dict())'),
    "Use learnerIDs A,A,B and tracks Python,Python,Japanese. Compute unique learners per track, draw those totals with Matplotlib bars and print them.",
    chart('rows=pd.DataFrame({"learner":["A","A","B"],"track":["Python","Python","Japanese"]})\ntotals=rows.groupby("track")["learner"].nunique()\nfig,ax=plt.subplots(); ax.bar(totals.index,totals.values); ax.set_ylabel("Distinct learners")\nprint(totals.to_dict())'),
    "Frequency of observations is a valid quantity only when it matches the question's denominator.",
    [("What does countplot count?","Category rows","Always distinct learners","The sum of scores","Repeated observations are counted repeatedly."),
     ("How do you find unique people per category?","Compute groupby(...).nunique() on IDs","Rename the count axis","Use darker colours","The statistic must change, not just its label.")])

lesson(2,"2. Barplot estimates: mean, spread and uncertainty differ",
    "Set the estimator and interval deliberately and inspect the raw distribution.",
    [("estimator; mean; median", "barplot calculates a statistic per category, a mean by default. estimator='median' selects the middle-value summary. A category bar is not automatically a count or total."),
     ("errorbar='sd'; errorbar=None", "errorbar='sd' shows mean plus/minus one sample standard deviation as observed spread. None omits intervals. SD is not a confidence interval for the population mean."),
     ("Default bootstrap CI", "The default barplot interval estimates mean uncertainty using bootstrap resampling. Its interpretation requires an appropriate sampling/unit structure; a seed makes random output reproducible, not statistically valid. Week33 develops inference.")],
    "Two categories can share a mean but have very different individual values. A mean bar should not replace looking at raw observations or a distribution. "
    "An SD interval describes spread around the mean. A confidence interval addresses uncertainty about an estimate under assumptions; it is a different claim. "
    "Repeated sessions from the same learner are not automatically independent people. A default row bootstrap should not be accepted as an inferential guarantee. "
    "Our plot explicitly uses SD and calls it descriptive spread. For a small synthetic dataset, this is a lesson in reading the statistic, not evidence that one course is superior. A range can even extend outside possible score bounds; never hide that with an unexplained axis crop.",
    'sns.barplot(data=df,x="track",y="score",estimator="mean",errorbar="sd",ax=ax)',
    example('fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nsns.barplot(data=df,x="track",y="score",estimator="mean",errorbar="sd",color="#0072B2",ax=ax)\nax.set(title="Session means with one SD of observed spread",ylabel="Score",ylim=(0,110))\nprint(df.groupby("track")["score"].agg(["mean","std"]).round(2).to_dict())'),
    "pandas std uses the sample standard deviation by default. The printed numbers let you inspect the plotted summary. This interval is deliberately not labelled95% confidence.",
    ('sns.barplot(...,errorbar="sd"); ax.set_title("95% confidence")', 'sns.barplot(data=df,x="track",y="score",errorbar="sd",ax=ax)\nax.set_title("Mean plus/minus one SD")', "Spread of observations and uncertainty of an estimate must not be relabelled as one another."),
    "Plot median score per track with no interval. Print the three medians.",
    example('fig,ax=plt.subplots()\nsns.barplot(data=df,x="track",y="score",estimator="median",errorbar=None,color="#0072B2",ax=ax)\nprint(df.groupby("track")["score"].median().to_dict())'),
    "Compare means and medians for groupA [10,10,10,90], groupB [25,30,35,40]. Plot medians and print both statistics.",
    chart('df=pd.DataFrame({"group":["A"]*4+["B"]*4,"score":[10,10,10,90,25,30,35,40]})\nfig,ax=plt.subplots()\nsns.barplot(data=df,x="group",y="score",estimator="median",errorbar=None,color="#0072B2",ax=ax)\nprint(df.groupby("group")["score"].agg(["mean","median"]).to_dict())'),
    "Name the statistic and interval; defaults are implementation choices, not a substitute for a study design.",
    [("What does errorbar='sd' show?","Observed spread around the mean","A95% CI automatically","All individual values","SD and confidence intervals answer different questions."),
     ("Does a random seed fix non-independent observations?","No","Always","Only with many colours","Reproducibility does not validate the sampling assumptions.")])

lesson(2,"3. Box and strip: put the observations back",
    "Combine a compact summary with visible values while disclosing overplotting.",
    [("stripplot; jitter", "stripplot places individual values along a category axis. Jitter spreads overlapping positions horizontally; it does not change scores. jitter=False leaves exact alignment and may overlap marks."),
     ("Overlay; showfliers", "Overlay raw points and a box on the same Axes. showfliers=False suppresses the box's separate flier symbols when raw points already display every value; it does not delete those source rows.")],
    "A box shows quartiles while a strip restores the actual observations that a summary can hide. In a four-row group, showing those values is often more informative than a confident-looking estimate. "
    "If the strip already includes every source value, separate box flier symbols can duplicate marks. Suppressing those symbols is a drawing choice, not a cleaning step. "
    "Jitter helps with overlaps, but horizontal displacement has no measurement meaning. Here we use no jitter to keep the example deterministic; equal scores can overlap and should be acknowledged. "
    "Use the Week31 box-plot rules: a flier is not automatically an error, whiskers are not a universal confidence interval and the box alone does not reveal every distribution shape.",
    'sns.boxplot(data=df,x="track",y="score",showfliers=False,ax=ax)\nsns.stripplot(data=df,x="track",y="score",jitter=False,color="black",ax=ax)',
    example('fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nsns.boxplot(data=df,x="track",y="score",showfliers=False,color="#a8cfe5",ax=ax)\nsns.stripplot(data=df,x="track",y="score",jitter=False,color="black",size=5,ax=ax)\nax.set(title="Quartiles plus the source score positions",ylabel="Score")\nprint("Values retained:",len(df))'),
    "Both calls draw onto the same ax. Black marks retain values even when the box does not draw flier symbols. Four recorded scores per track remain in the source.",
    ('df=df[df["score"]<80]  # remove points because box marks them', 'sns.boxplot(data=df,x="track",y="score",showfliers=False,ax=ax)\nsns.stripplot(data=df,x="track",y="score",jitter=False,ax=ax)', "Investigate unusual records before deletion; raw overlays can display them without duplicate symbols."),
    "Draw a score box plus a black strip for Python sessions only and print the four scores.",
    example('part=df.loc[df["track"].eq("Python")]\nfig,ax=plt.subplots()\nsns.boxplot(data=part,x="track",y="score",color="#a8cfe5",ax=ax)\nsns.stripplot(data=part,x="track",y="score",jitter=False,color="black",ax=ax)\nprint(part["score"].tolist())'),
    "Show values[10,10,10,90] with a box whose flier symbol is hidden plus a strip. Print proof that90 remains in the input.",
    chart('df=pd.DataFrame({"group":["A"]*4,"value":[10,10,10,90]})\nfig,ax=plt.subplots()\nsns.boxplot(data=df,x="group",y="value",showfliers=False,ax=ax)\nsns.stripplot(data=df,x="group",y="value",jitter=False,color="black",ax=ax)\nprint("90 retained:",df["value"].eq(90).any())'),
    "Use a summary and raw marks together; display choices must not silently remove inconvenient observations.",
    [("Does showfliers=False remove input rows?","No; it hides separate flier symbols","Always","It replaces them with zero","An overlay can still show those exact values."),
     ("What does horizontal jitter represent?","A display offset to reduce overlap","A new score","A measured time difference","Do not interpret the offset as a data variable.")])

lesson(2,"4. Violin and swarm: shape estimates versus individual marks",
    "Read density width cautiously and inspect raw-point placement limits.",
    [("violinplot; inner; density_norm", "A violin mirrors an estimated density. Width represents the chosen density normalisation, not automatically sample count. inner='stick' adds observation positions; density_norm='area' gives equal-area scaling."),
     ("swarmplot", "A swarm places individual marks without overlap when space permits, using lateral offsets with no measurement meaning. Crowded swarms can fail to place all marks and warn; they are not a scalable solution for every dataset.")],
    "A violin can suggest a detailed shape even when only a few observations exist. Remember Day2's bandwidth lesson: a smooth outline is an estimate. "
    "Use the raw values, sample counts and sensitivity to smoothing before interpreting peaks. cut=0 restricts the drawn range but does not validate an inferred population. "
    "A swarm keeps individual values visible more effectively than an aligned strip in modest groups. Its lateral positions are layout adjustments, not another measured variable. "
    "Do not respond to placement warnings by pretending every record is visible. For larger datasets, choose smaller marks, transparency, a histogram or another summary and report the denominator.",
    'sns.violinplot(data=df,x="track",y="score",cut=0,inner="stick",density_norm="area",ax=ax)',
    example('fig,axs=plt.subplots(1,2,figsize=(8,3.5),layout="constrained")\nsns.violinplot(data=df,x="track",y="score",cut=0,inner="stick",density_norm="area",color="#a8cfe5",ax=axs[0])\nsns.swarmplot(data=df,x="track",y="score",size=4,color="#0072B2",ax=axs[1])\naxs[0].set_title("Estimated shape; four values per track"); axs[1].set_title("Individual values")\nfor ax in axs: ax.tick_params(axis="x",labelrotation=20)\nprint(df.groupby("track").size().to_dict())'),
    "The left outline is not evidence that four values reveal a stable distribution. The right has actual observation positions. Neither chart turns a fictional comparison into a real teaching evaluation.",
    ('sns.violinplot(...); print("Every smooth bump is a true subgroup")', 'sns.violinplot(data=df,x="track",y="score",cut=0,inner="stick",ax=ax)', "Expose observations and smoothing choices before interpreting a violin."),
    "Draw score violins with cut=0 and inner='point'. Print the group sizes.",
    example('fig,ax=plt.subplots()\nsns.violinplot(data=df,x="track",y="score",cut=0,inner="point",color="#a8cfe5",ax=ax)\nprint(df.groupby("track").size().to_dict())'),
    "Create a swarm of minutes by mode with small marks and print the total input size.",
    example('fig,ax=plt.subplots()\nsns.swarmplot(data=df,x="mode",y="minutes",size=4,color="#0072B2",ax=ax)\nprint("Input rows:",len(df))'),
    "Density width, raw counts and lateral placement are different encodings; do not read one as another.",
    [("Does equal-area violin width directly show group sample size?","No","Always","Only for blue violins","Density normalisation and sample counts are distinct."),
     ("What can happen in an overcrowded swarm?","Some marks may not be placed and a warning appears","Source data is deduplicated","The scores change","Inspect warnings and choose a representation that fits.")])

lesson(2,"5. Choose among category views by the question",
    "Explain what each view retains, summarises or obscures.",
    [("catplot; kind", "catplot is the figure-level categorical interface. kind selects a family such as count, bar, box, violin, strip or swarm; its returned grid owns the Figure."),
     ("Category order contract", "Use one explicit order for comparable views and one stated observation population. Changing category positions or exclusions between views makes comparisons harder to audit.")],
    "Do not learn plotting functions as isolated commands. Ask what the reader needs: recorded session frequencies, average scores, quartiles, an estimated shape or every observation. "
    "For frequencies use countplot. For a stated statistic use barplot with a disclosed estimator and interval. For a compact distribution use boxplot; for a smoothed shape use violinplot cautiously. "
    "For individual values choose strip or swarm, taking overlap and sample size into account. Several views can complement one another without any one being universally best. "
    "The example places a box beside a mean bar using exactly the same rows and order. Write one sentence about what the bar hides: variation and the actual number of distinct score values.",
    'g=sns.catplot(data=df,x="track",y="score",kind="box",order=order)',
    example('order=["Python","Japanese","Security"]\nfig,axs=plt.subplots(1,2,figsize=(8,3.5),layout="constrained")\nsns.boxplot(data=df,x="track",y="score",order=order,color="#a8cfe5",ax=axs[0])\nsns.barplot(data=df,x="track",y="score",order=order,estimator="mean",errorbar=None,color="#0072B2",ax=axs[1])\naxs[0].set_title("Quartiles"); axs[1].set_title("Means only")\nfor ax in axs: ax.set_ylim(0,100); ax.tick_params(axis="x",labelrotation=20)\nprint("Same source rows:",len(df))'),
    "The means-only panel compresses four scores to one number per category. The box preserves more distribution information but still does not show every individual mark.",
    ('# Use any category plot and call it "number of learners"', '# Define the denominator, then choose count, summary or raw-value view', "The question and units choose the function, not familiarity with its name."),
    "Use catplot(kind='box') for scores by mode, save its Figure and print the number of Axes.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.catplot(data=df,x="mode",y="score",kind="box",height=3,aspect=1.4)
g.figure.savefig("chart.png"); print(len(g.axes.flat)); plt.close(g.figure)
''',
    "Put a countplot and a stripplot side by side, label their different y units and print those labels.",
    example('fig,axs=plt.subplots(1,2,layout="constrained")\nsns.countplot(data=df,x="mode",color="#0072B2",ax=axs[0]); sns.stripplot(data=df,x="mode",y="score",jitter=False,ax=axs[1])\naxs[0].set_ylabel("Sessions"); axs[1].set_ylabel("Score")\nprint([ax.get_ylabel() for ax in axs])'),
    "Choose category frequency, statistic, distribution or individual values deliberately, then keep the comparison contract consistent.",
    [("Which view directly keeps individual y values?","Strip or swarm","A mean-only bar","A row-count bar","Raw-value plots retain observations subject to overlap."),
     ("What does catplot return?","A figure-owning grid","Always one raw Axes","A CSV table","Use its figure for export and lifecycle management.")])

lesson(3,"1. Hue, size and style encode distinct variables",
    "Encode several variables without making an unreadable scatter plot.",
    [("size; sizes; style", "In scatterplot, size maps a variable to marker area and sizes selects the displayed area range. style maps categories to marker shapes. These are semantic column mappings, not new independent data."),
     ("Redundant versus additional encoding", "Using hue and style for the same category reinforces identity. Using size for a different numeric variable adds information but also reading effort. More variables are not automatically more useful.")],
    "x and y already use two variables. Colour can identify track and marker area can represent task count, giving four variables without extra axes. "
    "A legend must explain the encodings, and mark size should remain moderate so large points do not cover everything else. Numeric area is not a good channel for precise comparisons, so keep exact values available in a table or hover view. "
    "Style can reinforce track when colour differences are hard to see. That adds a second cue for the same variable rather than a fifth independent quantity. "
    "If the result is crowded, simplify or facet rather than treating visual density as sophistication. These are descriptive session observations, not causal effects of practice tasks.",
    'sns.scatterplot(data=df,x="minutes",y="score",hue="track",size="tasks",style="track",sizes=(30,140),ax=ax)',
    example('fig,ax=plt.subplots(figsize=(7,4),layout="constrained")\nsns.scatterplot(data=df,x="minutes",y="score",hue="track",style="track",size="tasks",sizes=(30,140),alpha=0.8,ax=ax)\nax.set(title="Four variables; track has two identity cues",xlabel="Minutes",ylabel="Score")\nprint("Task range:",int(df["tasks"].min()),int(df["tasks"].max()))'),
    "Track controls both colour and shape; tasks controls area. Only four source variables are represented: minutes, score, track and tasks. Large area is an approximate visual cue, not a substitute for the actual count.",
    ('# Add every available column to the plot regardless of readability', 'sns.scatterplot(data=df,x="minutes",y="score",hue="track",style="track",ax=ax)', "Simplify when encodings compete rather than improve the question."),
    "Plot tasks versus score with hue and style both mapped to mode. Print the distinct mode labels.",
    example('fig,ax=plt.subplots()\nsns.scatterplot(data=df,x="tasks",y="score",hue="mode",style="mode",ax=ax)\nprint(sorted(df["mode"].unique().tolist()))'),
    "Map marker size to minutes but keep all points the same colour. Label both coordinates and print the size-variable range.",
    example('fig,ax=plt.subplots()\nsns.scatterplot(data=df,x="tasks",y="score",size="minutes",sizes=(30,150),color="#0072B2",ax=ax)\nprint(int(df["minutes"].min()),int(df["minutes"].max()))'),
    "Every visual channel needs a reason and a decoding key; simplify when the reading cost exceeds the information gained.",
    [("Hue and style both mapped to track represent how many source variables?","One","Two","Four","Two visual channels can encode the same category."),
     ("What does scatter size normally encode?","Marker area","The sample's independence","A causal effect","Use a legend and do not mistake size for an exact printed value.")])

lesson(3,"2. Lineplot can aggregate before connecting points",
    "Distinguish a mean trajectory from raw observations at each x value.",
    [("lineplot; estimator; errorbar; sort", "lineplot normally groups repeated x positions and estimates a mean with uncertainty. estimator=None disables that aggregation. sort=True normally orders x within groups; ordering does not make arbitrary categories a temporal sequence."),
     ("Per-position sample size", "A mean at each day may represent different numbers or different people. Inspect the contributors at each x position before calling the line individual improvement.")],
    "Matplotlib ax.plot connects the values you supply. Seaborn lineplot may calculate a mean first when several rows share an x value. "
    "That is helpful for a declared descriptive summary but easy to overlook. A line of day means is not the path of one learner and may compare different contributors over time. "
    "Set the estimator and interval explicitly. errorbar=None below avoids making inferential claims from this synthetic table, while a printed groupby shows the exact mean and count at each day. "
    "Do not combine an already-aggregated mean table with a second unplanned weighted aggregation; decide which rows should contribute and how before plotting.",
    'sns.lineplot(data=df,x="day",y="score",estimator="mean",errorbar=None,ax=ax)',
    example('fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nsns.lineplot(data=df,x="day",y="score",estimator="mean",errorbar=None,marker="o",ax=ax)\nax.set(title="Mean across three sessions at each day",xlabel="Day label",ylabel="Mean score")\nprint(df.groupby("day")["score"].agg(["mean","count"]).round(2).to_dict())'),
    "Each day has three rows, one per track. The line compares their means; it does not follow one learner. A constant contributor count alone would still not establish constant identities.",
    ('sns.lineplot(data=df,x="day",y="score")  # assume every row is a line point', 'sns.lineplot(data=df,x="day",y="score",estimator="mean",errorbar=None)', "Know the aggregation and interval policy rather than interpreting defaults as raw data."),
    "Plot mean minutes at each day with errorbar=None and print the day-level means.",
    example('fig,ax=plt.subplots()\nsns.lineplot(data=df,x="day",y="minutes",estimator="mean",errorbar=None,marker="o",ax=ax)\nprint(df.groupby("day")["minutes"].mean().to_dict())'),
    "Filter to Python, where each day occurs once, and draw with estimator=None. Print the input day counts.",
    example('part=df.loc[df["track"].eq("Python")]\nfig,ax=plt.subplots()\nsns.lineplot(data=part,x="day",y="score",estimator=None,marker="o",ax=ax)\nprint(part.groupby("day").size().to_dict())'),
    "Inspect what a line summarises; a mean curve and an individual's trajectory answer different questions.",
    [("Does Seaborn lineplot always connect every raw row?","No; it can aggregate repeated x values","Always","Only in PNG","Its default estimator can combine observations."),
     ("Does equal count per day prove the same learners were measured?","No","Always","Only for four days","Identity must be checked independently of counts.")])

lesson(3,"3. Individual trajectories retain the repeated unit",
    "Use units and estimator=None to keep distinct learners' paths separate.",
    [("units in lineplot", "units identifies a sampling or repeated-measurement unit. With estimator=None, Seaborn draws separate lines for those units instead of averaging them into one path. Unit IDs need not become legend entries."),
     ("Unique unit-time pairs", "One learner/day pair should have the measurement your design intends. Multiple measurements at one pair require an explicit selection or aggregation policy, not an accidental line zigzag.")],
    "When the same person appears on several days, their observations belong together. A line can preserve that pairing rather than jumping from one person's row to another. "
    "Specify units='learner' with estimator=None and sort the records by learner and day. Check duplicate learner/day pairs before drawing. "
    "The units setting is a drawing rule, not a complete repeated-measures statistical model. It does not establish causation or validate a population confidence interval. "
    "The example shows three fictional learners measured twice. Their six observations remain six measurements from three units. One learner's decline should not disappear behind an overall rising mean.",
    'sns.lineplot(data=df,x="day",y="score",units="learner",estimator=None,ax=ax)',
    chart('''
df=pd.DataFrame({"learner":["A","A","B","B","C","C"],"day":[1,2]*3,"score":[40,60,70,65,50,75]})
df=df.sort_values(["learner","day"])
fig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")
sns.lineplot(data=df,x="day",y="score",units="learner",estimator=None,marker="o",color="#0072B2",ax=ax)
ax.set(title="Three learners, six paired measurements",xticks=[1,2],ylabel="Score")
print("Units:",df["learner"].nunique())
print("Duplicate unit/day pairs:",int(df.duplicated(["learner","day"]).sum()))
'''),
    "Three lines are drawn without three legend entries. hue='learner' can label them when there are few learners; with many units, dozens of legend labels may be impractical.",
    ('sns.lineplot(data=df,x="day",y="score",estimator=None)  # mixed units', 'sns.lineplot(data=df,x="day",y="score",units="learner",estimator=None)', "Disabling aggregation alone does not identify which observations belong to each path."),
    "Draw two learners' paths: A scores40,60 and B70,65 over days1,2. Use units, and print how many learners declined.",
    chart('df=pd.DataFrame({"learner":["A","A","B","B"],"day":[1,2,1,2],"score":[40,60,70,65]})\nfig,ax=plt.subplots()\nsns.lineplot(data=df,x="day",y="score",units="learner",estimator=None,marker="o",ax=ax)\nchanges=df.groupby("learner")["score"].last()-df.groupby("learner")["score"].first()\nprint("Declined:",int(changes.lt(0).sum()))'),
    "Use three rows with duplicate learner/day A/1 and print that duplication before drawing the raw points without inventing a unique trajectory.",
    chart('df=pd.DataFrame({"learner":["A","A","A"],"day":[1,1,2],"score":[40,45,60]})\nfig,ax=plt.subplots()\nsns.scatterplot(data=df,x="day",y="score",ax=ax)\nprint("Duplicate unit/day rows:",int(df.duplicated(["learner","day"]).sum()))'),
    "Preserve repeated-unit identity; visual grouping is not a substitute for an appropriate statistical analysis.",
    [("Which combination draws separate raw unit paths?","units plus estimator=None","errorbar='sd' alone","A larger marker","The unit column determines which observations are connected."),
     ("Do six measurements from three learners mean six independent learners?","No","Always","Only when sorted","Repeated-unit structure survives reshaping and drawing.")])

lesson(3,"4. Relplot facets and stable semantic mappings",
    "Split views by category without changing colour or scale meaning between panels.",
    [("relplot; col; row; col_wrap", "relplot creates a figure-level relational grid. col and row split categories into facets; col_wrap wraps a column-only grid. kind='scatter' or 'line' selects its plotting family."),
     ("Global hue mapping; shared scales", "A consistent hue_order and palette keep categories mapped to the same colours across panels. Shared numeric limits support absolute comparisons; an empty facet is not a measured zero.")],
    "Faceting reduces overlap by repeating the same question for subsets. Keep axes and category mappings consistent so readers do not relearn the code for each panel. "
    "A facet with no records may reflect missing source coverage rather than no activity. Include explicit categories when the comparison requires their visibility, and label empty evidence honestly. "
    "The returned grid manages the Figure. Use set_axis_labels and set_titles on it, then save g.figure. This is the ownership pattern introduced on Day1. "
    "Facets should answer a comparison question, not multiply panels merely because several category columns exist. Start with track panels and mode colours; inspect whether the result is actually easier to read than one crowded Axes.",
    'g=sns.relplot(data=df,x="minutes",y="score",col="track",hue="mode",kind="scatter")',
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.relplot(data=df,x="minutes",y="score",col="track",col_order=["Python","Japanese","Security"],hue="mode",hue_order=["Solo","Guided"],kind="scatter",height=3,aspect=0.95)
g.set_axis_labels("Minutes per session","Score")
g.set_titles("{col_name}")
g.figure.savefig("chart.png",dpi=110); print("Facets:",len(g.axes.flat)); plt.close(g.figure)
''',
    "The three panels share compatible scales. Mode colours retain the same meaning in every panel. Filtering into separate unrelated plots would require manually preserving these choices.",
    ('# Map each facet independently and assume its first colour always means Solo', 'g=sns.relplot(data=df,x="minutes",y="score",col="track",hue="mode",hue_order=["Solo","Guided"])', "Global mappings prevent a category's colour from changing when subsets differ."),
    "Facet tasks/score by mode with relplot and print the facet count.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.relplot(data=df,x="tasks",y="score",col="mode",height=3,aspect=1)
g.figure.savefig("chart.png"); print(len(g.axes.flat)); plt.close(g.figure)
''',
    "Wrap track scatter facets into two columns using col_wrap=2. Print their count and keep colour mapped to mode.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.relplot(data=df,x="minutes",y="score",col="track",col_wrap=2,hue="mode",height=2.5,aspect=1)
g.figure.savefig("chart.png"); print(len(g.axes.flat)); plt.close(g.figure)
''',
    "Repeat the question with stable scales and meanings; an empty subset is an evidence state, not automatic zero.",
    [("Why keep hue_order consistent?","A colour should mean the same category in every panel","It makes observations independent","It removes missing data","Stable mapping reduces misleading panel differences."),
     ("What does col_wrap control?","How column facets wrap across rows","The y statistic","The number of data variables","It is a layout option for a column-faceted grid.")])

lesson(4,"1. FacetGrid builds a small-multiple system",
    "Map an Axes-level function over subsets and manage the whole grid.",
    [("FacetGrid; map_dataframe", "FacetGrid creates a category-based figure grid. map_dataframe calls an Axes-level function on each subset using named columns, retaining common facet semantics."),
     ("set_axis_labels; set_titles; add_legend", "These grid methods coordinate labels, facet title templates and legends. They do not change which rows or statistics enter each panel.")],
    "relplot and displot provide convenient complete recipes. FacetGrid gives you more direct control when a recipe does not match the display you need. "
    "Think in two steps: define how categories divide the table, then define what should be drawn within each subset. Keep common bins and scale limits explicit when distributions are compared. "
    "map_dataframe passes each subset to a function that understands data and named x/y columns. A Figure-level function would try to create another grid, so it is the wrong mapping target. "
    "When a simpler relplot or displot expresses the question clearly, prefer that convenience; use the lower-level grid when it earns its extra moving parts.",
    'g=sns.FacetGrid(df,col="track")\ng.map_dataframe(sns.histplot,x="score",bins=[40,60,80,100])',
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.FacetGrid(df,col="track",col_order=["Python","Japanese","Security"],height=3,aspect=1)
g.map_dataframe(sns.histplot,x="score",bins=[40,60,80,100],color="#0072B2")
g.set_axis_labels("Score","Session rows"); g.set_titles("{col_name}")
g.figure.savefig("chart.png",dpi=110); print("Grid panels:",len(g.axes.flat)); plt.close(g.figure)
''',
    "All three panels receive the same bin edges. No data is downloaded or loaded from an external service. The grid belongs to g, so export and close its Figure.",
    ('g.map_dataframe(sns.displot,x="score")', 'g.map_dataframe(sns.histplot,x="score")', "Map an Axes-level function; displot would create its own Figure-level grid."),
    "Build two mode facets and map an ECDF of scores. Print the number of facets.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.FacetGrid(df,col="mode",height=3)
g.map_dataframe(sns.ecdfplot,x="score"); g.set_axis_labels("Score","Proportion")
g.figure.savefig("chart.png"); print(len(g.axes.flat)); plt.close(g.figure)
''',
    "Create track facets with a minutes rug and histogram using common edges0,20,40,60. Print the source rows per track.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.FacetGrid(df,col="track",height=3)
g.map_dataframe(sns.histplot,x="minutes",bins=[0,20,40,60]); g.map_dataframe(sns.rugplot,x="minutes")
g.figure.savefig("chart.png"); print(df.groupby("track").size().to_dict()); plt.close(g.figure)
''',
    "Define the subsets once, map compatible Axes functions and keep scales, bins and ownership explicit.",
    [("Which belongs inside map_dataframe?","sns.histplot","sns.displot","sns.catplot","The mapped function should draw on a panel rather than create another grid."),
     ("Does a common grid validate source coverage?","No","Yes","Only for ECDFs","A layout system cannot prove that missing records do not exist.")])

lesson(4,"2. PairGrid: relationships between selected numeric variables",
    "Separate diagonal distributions and off-diagonal paired relationships.",
    [("PairGrid; map_diag; map_offdiag", "PairGrid arranges numeric variables against each other. Diagonal panels show each variable alone; off-diagonal panels show paired relationships. Mapping methods choose the drawing functions."),
     ("Pairwise exploration", "A pairwise matrix can reveal patterns worth investigating but also creates many chances to notice accidental patterns. Exploration does not confirm a causal or statistical claim.")],
    "For minutes, score and tasks, a pair grid has nine positions. The diagonal asks what each variable's distribution looks like; off-diagonal panels compare two measurements from the same row. "
    "Choose the variables rather than plotting every numeric column: row IDs and category codes may be numeric without having a meaningful distance. "
    "Three variables already create substantial visual work. A larger matrix is useful only when it remains readable and serves specific questions. "
    "Missing values can cause different pairs to use different row subsets. Keep denominators visible, and treat apparent clusters or relationships as leads to check against the raw observations and study design.",
    'g=sns.PairGrid(df,vars=["minutes","score","tasks"])\ng.map_diag(sns.histplot)\ng.map_offdiag(sns.scatterplot)',
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.PairGrid(df,vars=["minutes","score","tasks"],height=2)
g.map_diag(sns.histplot,bins=4)
g.map_offdiag(sns.scatterplot,s=25)
g.figure.savefig("chart.png",dpi=110)
print("Grid shape:",g.axes.shape); plt.close(g.figure)
''',
    "The3-by3 layout is a view of three variables, not nine new variables. Mirrored off-diagonal panels reverse x and y; they are not independent evidence.",
    ('sns.PairGrid(df,vars=["numeric_record_id","score"])  # ID treated as magnitude', 'sns.PairGrid(df,vars=["minutes","score","tasks"])', "Numeric storage does not guarantee a meaningful quantitative relationship."),
    "Make a PairGrid for minutes and score only, with histograms on the diagonal. Print its shape.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.PairGrid(df,vars=["minutes","score"],height=2.5)
g.map_diag(sns.histplot,bins=4); g.map_offdiag(sns.scatterplot)
g.figure.savefig("chart.png"); print(g.axes.shape); plt.close(g.figure)
''',
    "Colour a two-variable PairGrid by mode, use a shared hue_order and add a legend. Print the category labels.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''g=sns.PairGrid(df,vars=["minutes","score"],hue="mode",hue_order=["Solo","Guided"],height=2.5)
g.map_diag(sns.histplot,bins=4); g.map_offdiag(sns.scatterplot); g.add_legend()
g.figure.savefig("chart.png"); print(g.hue_names); plt.close(g.figure)
''',
    "Select meaningful measurements, recognise mirrored views and separate exploratory patterns from confirmed explanations.",
    [("What belongs on a PairGrid diagonal?","One variable's distribution","A causal effect","A filename list","Off-diagonal panels compare pairs of variables."),
     ("Are mirrored scatter panels independent supporting datasets?","No; they reuse the same observations","Yes","Only with hue","Reversing x and y does not create new evidence.")])

lesson(4,"3. Pairplot and a missingness ledger",
    "Use the convenience wrapper without losing track of excluded observations.",
    [("pairplot; diag_kind; corner", "pairplot creates a ready-made PairGrid. vars selects numeric columns, diag_kind='hist' avoids an automatic KDE on the diagonal, and corner=True hides redundant upper-triangle panels."),
     ("Complete-case versus pairwise counts", "Complete-case filtering uses one common row set across selected variables. Pairwise handling may retain more rows per pair but gives different denominators. Neither silently repairs missingness or guarantees no selection bias.")],
    "A convenience wrapper does not eliminate analysis choices. Name the variables, diagonal representation and row inclusion rule. "
    "For a small synthetic sample, histogram diagonals avoid presenting a tiny group's smooth density as a stable truth. A corner grid reduces mirrored repetition. "
    "If you drop all incomplete rows, report how many and consider who was excluded. If you allow different pairs to use different rows, provide counts for each pair. "
    "Do not replace missing scores with zero to make every chart accept the table. That changes both distributions and relationships. The missingness ledger is part of the report, not an optional technical footnote.",
    'g=sns.pairplot(data=known,vars=["minutes","score","tasks"],diag_kind="hist",corner=True)',
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''df.loc[0,"score"]=float("nan")
cols=["minutes","score","tasks"]
known=df.dropna(subset=cols)
g=sns.pairplot(data=known,vars=cols,diag_kind="hist",corner=True,height=2)
g.figure.savefig("chart.png",dpi=110)
print("Complete rows:",len(known),"Excluded:",len(df)-len(known)); plt.close(g.figure)
''',
    "One unknown score reduces the common row set to11. Reporting the exclusion avoids giving the impression that every pair retained all12 sessions.",
    ('df=df.fillna(0)  # unknown score becomes a measured failure', 'known=df.dropna(subset=["minutes","score","tasks"])  # disclose excluded rows', "Zero is an observation, not a universal missing-value replacement."),
    "Make a two-variable pairplot with histogram diagonals, print the common nonmissing row count and save it.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''known=df.dropna(subset=["minutes","score"])
g=sns.pairplot(data=known,vars=["minutes","score"],diag_kind="hist",corner=True,height=2.5)
g.figure.savefig("chart.png"); print(len(known)); plt.close(g.figure)
''',
    "Make score unknown in two rows, keep minutes/tasks known, and print how many complete three-variable rows remain before pairplot.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(SMALL)+'''df.loc[[0,1],"score"]=float("nan")
known=df.dropna(subset=["minutes","score","tasks"])
g=sns.pairplot(data=known,vars=["minutes","score","tasks"],diag_kind="hist",corner=True,height=2)
g.figure.savefig("chart.png"); print("Complete:",len(known)); plt.close(g.figure)
''',
    "A compact pairplot still needs explicit variables, missingness accounting and a clear exploratory purpose.",
    [("What does corner=True remove?","Redundant upper-triangle views","All missing values","The original rows","It changes displayed panels, not the source table."),
     ("Does complete-case filtering guarantee no bias?","No","Always","Only for scores","Excluded rows may differ systematically from retained rows.")])

lesson(4,"4. Correlation heatmaps: numeric values and pair counts",
    "Read Pearson association with a fixed colour scale and explicit limits.",
    [("Correlation; Pearson r", "Pearson correlation describes linear association on a scale from-1 to1 when the calculation is defined. It does not establish causation or capture every nonlinear relationship. Constant variables have undefined correlation."),
     ("corr; heatmap; annot; mask", "DataFrame.corr calculates pairwise numeric correlations. heatmap displays a matrix; annot writes values into cells and mask hides selected cells. vmin=-1,vmax=1,center=0 fixes the comparison scale."),
     ("Pair-count matrix", "A nonmissing indicator matrix can be multiplied by its transpose counterpart to count rows known for each variable pair. Different pairs may use different observations; counts contextualise r.")],
    "A strong colour can be visually persuasive while hiding a tiny sample or a confounded comparison. Start with scatter plots, then use a heatmap as a compact summary of selected meaningful numeric variables. "
    "Check missingness, constant columns and the row unit. Repeated sessions do not become independent people in a correlation matrix. "
    "Use a symmetric-1 to1 scale so the same colour means the same association across reports. Undefined cells should remain undefined, not be replaced with zero, which would claim a measured absence of linear association. "
    "Week33 develops statistical interpretation. Here describe the observed linear association and state the data limitations without significance or causal claims.",
    'corr=df[cols].corr(min_periods=3)\nsns.heatmap(corr,annot=True,vmin=-1,vmax=1,center=0,cmap="vlag",ax=ax)',
    example('cols=["minutes","score","tasks"]\ncorr=df[cols].corr(min_periods=3)\nvalid=df[cols].notna().astype(int); counts=valid.T.dot(valid)\nfig,ax=plt.subplots(figsize=(5.5,4),layout="constrained")\nsns.heatmap(corr,annot=True,fmt=".2f",vmin=-1,vmax=1,center=0,cmap="vlag",square=True,ax=ax)\nax.set_title("Descriptive Pearson association, n=12 per pair")\nprint("Minutes/score r:",round(corr.loc["minutes","score"],3))\nprint("Pair n:",int(counts.loc["minutes","score"]))'),
    "astype(int) converts known-value indicators to1 and0; T transposes and dot sums matching known pairs. A coefficient is not an intervention effect. IDs are excluded from this numeric matrix.",
    ('corr=df[cols].corr().fillna(0)  # undefined becomes no association', 'corr=df[cols].corr(min_periods=3)  # retain undefined cells', "Undefined, zero and unobserved are different states."),
    "Plot the minutes/score correlation matrix with a fixed-1 to1 colour range and print its off-diagonal coefficient.",
    example('corr=df[["minutes","score"]].corr()\nfig,ax=plt.subplots()\nsns.heatmap(corr,annot=True,vmin=-1,vmax=1,center=0,cmap="vlag",ax=ax)\nprint(round(corr.loc["minutes","score"],3))'),
    "Set one score missing and print pair counts for minutes/tasks and minutes/score. Draw the resulting matrix without filling undefined values.",
    example('df.loc[0,"score"]=float("nan")\ncols=["minutes","score","tasks"]; known=df[cols].notna().astype(int); counts=known.T.dot(known)\nfig,ax=plt.subplots()\nsns.heatmap(df[cols].corr(min_periods=3),annot=True,vmin=-1,vmax=1,center=0,cmap="vlag",ax=ax)\nprint(int(counts.loc["minutes","tasks"]),int(counts.loc["minutes","score"]))'),
    "A heatmap summarises defined pairwise linear association; show denominators and never turn undefined values into fake zero evidence.",
    [("Does a large Pearson r establish a cause?","No","Always","Only in red cells","Confounding, sample structure and study design still matter."),
     ("How should a constant column's undefined correlation be treated?","Keep it undefined and explain","Replace it with0 automatically","Replace it with1","Undefined is not a measured absence of association.")])

lesson(5,"1. Plotly Express creates an interactive Figure",
    "Map familiar columns into a Plotly chart and distinguish its objects from Matplotlib.",
    [("Plotly Express; px; Plotly Figure", "Plotly Express is a convenient interface to interactive charts. Its functions return a Plotly Figure, not a Matplotlib Figure or Axes. Use its own methods for layout and HTML export."),
     ("Trace; color", "A trace is a plotted series. px.scatter(...,color='track') typically creates one trace per category. Plotly Express uses color where Seaborn uses hue for this semantic mapping."),
     ("write_image; Kaleido", "write_image exports a static preview and needs the optional Kaleido package plus compatible Chrome. write_html needs neither Kaleido nor image export. You may omit the write_image line when only making interactive HTML.")],
    "The same tidy data can feed a different chart system. A Plotly chart supports hover, zoom and legend interactions in a browser. "
    "It is not drawn on a Matplotlib Axes, so ax.set_title and plt.close are not its controls. Keep the returned fig and use update_layout or write_html. "
    "The embedded lesson picture is the actual static export of the example; a PNG itself has no hover. The example also saves chart.html, which retains interaction when opened locally. "
    "Interactivity is useful when readers need exact values or a focused subset. It does not fix a bad denominator, missing labels or an unjustified conclusion. Continue to use the chart-reading contract from Week31.",
    'fig=px.scatter(df,x="minutes",y="score",color="track")\nfig.write_html("chart.html",include_plotlyjs=True)',
    plotly_example('fig=px.scatter(df,x="minutes",y="score",color="track",symbol="track",title="Fictional practice sessions",labels={"minutes":"Minutes per session","score":"Score"})\nprint("Category traces:",len(fig.data))\nprint("Points:",sum(len(trace.x) for trace in fig.data))'),
    "Three track traces contain twelve coordinate pairs. The HTML contains the interactive figure; its image preview is included in this offline lesson so the visual result is visible without executing Python.",
    ('fig=px.scatter(df,x="minutes",y="score"); fig.savefig("chart.png")', 'fig=px.scatter(df,x="minutes",y="score"); fig.write_html("chart.html",include_plotlyjs=True)', "Plotly and Matplotlib Figures have different interfaces."),
    "Create an interactive tasks/score scatter coloured by mode and print the trace count.",
    plotly_example('fig=px.scatter(df,x="tasks",y="score",color="mode",title="Tasks and score")\nprint("Traces:",len(fig.data))'),
    "Create a Python-only interactive scatter and print the number of retained observations.",
    plotly_example('part=df.loc[df["track"].eq("Python")]\nfig=px.scatter(part,x="minutes",y="score",title="Python sessions only")\nprint("Rows:",len(part))'),
    "Use Plotly's own Figure API; static previews illustrate the output while HTML preserves interaction.",
    [("What does px.scatter return?","A Plotly Figure","A Matplotlib Axes","A CSV file","Use the methods of the returned chart system."),
     ("Does the embedded PNG support hover?","No; open the HTML chart","Always","Only in dark mode","PNG is a static preview; HTML contains the interactive chart.")])

lesson(5,"2. Hover details, category toggles and connected order",
    "Expose useful values while understanding what client-side interactions change.",
    [("hover_data; labels; update_layout", "hover_data selects extra columns to show and can format numeric values. labels supplies readable display names. update_layout changes the Plotly Figure's presentation."),
     ("Legend interaction; reset axes", "Clicking a category legend entry typically toggles that trace; double-click can isolate it. Zoom and pan change the visible region. These interactions do not remove the underlying data from the HTML or automatically recompute source summaries."),
     ("Plotly line order", "px.line connects rows in supplied order within groups. Sort paired rows before drawing; it does not automatically calculate Seaborn's default day-level mean.")],
    "A hover label can carry an exact score or task count without printing text on every mark. Include what answers the question and keep units understandable. "
    "Anything embedded in the HTML may be read by its recipient, including columns used in hover. Do not put private names, notes or tokens into a public chart; hiding a trace is not access control. "
    "Legend toggles are a view change. Hiding a category does not regenerate a separate mean bar or change the study population contract. "
    "For line charts, sort entire rows and choose whether you want raw unit paths or an explicitly prepared summary. A visually smooth connection is not an automatic statistical calculation.",
    'fig=px.scatter(df,x="minutes",y="score",color="track",hover_data={"tasks":True,"minutes":":.0f"})',
    plotly_example('fig=px.scatter(df,x="minutes",y="score",color="track",hover_data={"tasks":True,"minutes":":.0f"},labels={"minutes":"Minutes","score":"Score"},title="Hover for task count; legend toggles track")\nfig.update_layout(legend_title_text="Track")\nprint("Hover includes tasks:","tasks" in fig.data[0].hovertemplate)'),
    "The generated hover template refers to task data already included in the file. Client-side visibility does not remove those bytes. All examples contain fictional rows only.",
    ('fig=px.line(df,x="day",y="score")  # unsorted mixed sessions interpreted as a mean', 'summary=df.groupby("day",as_index=False)["score"].mean()\nfig=px.line(summary.sort_values("day"),x="day",y="score")', "Prepare and sort the intended summary; Plotly Express line does not silently reproduce Seaborn aggregation."),
    "Prepare day-level mean score, sort by day and plot an interactive line. Print the mean values.",
    plotly_example('summary=df.groupby("day",as_index=False)["score"].mean().sort_values("day")\nfig=px.line(summary,x="day",y="score",markers=True,title="Explicit daily session means")\nprint(summary["score"].round(2).tolist())'),
    "Add mode and tasks to scatter hover data but use only fictional rows. Print whether the hover template includes mode.",
    plotly_example('fig=px.scatter(df,x="minutes",y="score",hover_data=["mode","tasks"],title="Fictional details in hover")\nprint("mode" in fig.data[0].hovertemplate)'),
    "Interactive controls change the view; prepare summaries deliberately and publish only data appropriate for every file recipient.",
    [("Does hiding a trace remove its data from the HTML?","No","Always","Only after zooming","The file still contains the embedded data."),
     ("Does px.line automatically produce a mean at repeated x positions?","No; prepare the intended summary","Always","Only for scores","Its line connects supplied rows in their order.")])

lesson(5,"3. Export standalone interactive HTML for offline use",
    "Bundle the rendering library and test without network access.",
    [("include_plotlyjs=True; full_html=True", "True embeds Plotly.js inside a complete HTML document, making the ordinary chart self-contained. The file is larger, but does not need a CDN to render. A CDN option instead requires network access."),
     ("Responsive config; auto_open", "config={'responsive':True} lets the plot resize with its container. auto_open=False saves without launching a browser. Interactivity still depends on JavaScript being allowed in the reader's browser."),
     ("html.parser.HTMLParser", "Python's HTML parser reads actual tags and attributes. A subclass can collect external script src values through handle_starttag. Searching raw bundled JavaScript for HTML-like text can give false matches, so use a parser for the document structure.")],
    "Offline export is a packaging decision. A tiny HTML file that references a CDN can look correct while online and fail as soon as internet is unavailable. "
    "Embed the library for a shareable single-file chart. Opening an already-generated HTML chart does not require Python, Seaborn, Kaleido or a hosted account. "
    "The file must still be saved to the device for guaranteed local access; visiting a hosted URL once does not automatically place every auxiliary file into StudyHub's offline cache. "
    "This course includes a self-contained demo in docs/python-week32/interactive-demo.html. Save that file and try hover, legend toggle and zoom while disconnected. The main lesson's static preview remains embedded directly in study-hub.html.",
    'fig.write_html("chart.html",include_plotlyjs=True,full_html=True,auto_open=False,config={"responsive":True})',
    plotly_example('from pathlib import Path\nfig=px.scatter(df,x="minutes",y="score",color="track",title="Self-contained offline chart")\nfig.write_html("offline.html",include_plotlyjs=True,full_html=True,auto_open=False,config={"responsive":True})\ntext=Path("offline.html").read_text(encoding="utf-8")\nprint("Complete document:","<html>" in text)\nprint("Embedded library:","plotly.js v" in text.lower())'),
    "The completed file includes its JavaScript implementation and fictional plot data. The presence of embedded bytes is checked here; browser tests also load the supplied demo offline and exercise interaction.",
    ('fig.write_html("offline.html",include_plotlyjs="cdn")', 'fig.write_html("offline.html",include_plotlyjs=True,full_html=True)', "A CDN reference saves space but cannot guarantee offline rendering."),
    "Save a track-coloured chart as complete inline HTML, then print whether any external script src attribute exists.",
    plotly_example('from html.parser import HTMLParser\nfrom pathlib import Path\nclass Scripts(HTMLParser):\n    def __init__(self):\n        super().__init__(); self.external=[]\n    def handle_starttag(self,tag,attrs):\n        if tag=="script" and dict(attrs).get("src"):\n            self.external.append(dict(attrs)["src"])\nfig=px.scatter(df,x="minutes",y="score",color="track")\nfig.write_html("offline.html",include_plotlyjs=True,full_html=True)\nparser=Scripts(); parser.feed(Path("offline.html").read_text(encoding="utf-8"))\nprint("External script tags:",len(parser.external))'),
    "Set the chart title and responsive layout, write complete HTML without opening a window, and print that the file exists.",
    plotly_example('from pathlib import Path\nfig=px.scatter(df,x="tasks",y="score",title="Saved for offline reading")\nfig.write_html("offline.html",include_plotlyjs=True,auto_open=False,config={"responsive":True})\nprint(Path("offline.html").is_file())'),
    "A self-contained chart bundles data and rendering code; test the saved file offline rather than relying on a cached hosted visit.",
    [("Which option avoids a Plotly CDN requirement?","include_plotlyjs=True","include_plotlyjs='cdn'","A smaller filename","True embeds the library into the saved HTML."),
     ("Does opening a generated HTML chart require Python?","No; an enabled browser is enough","Always","Only on phones","Python is needed to generate it, not to render the already-written chart.")])

FIXTURE_ROWS=[]
for person in range(1,13):
    track=["Python","Japanese","Security"][(person-1)//4]
    for day in [1,2]:
        FIXTURE_ROWS.append({"session_id":f"S{len(FIXTURE_ROWS)+1:02d}","learner":f"L{person:02d}",
            "track":track,"mode":"Solo" if day==1 else "Guided","day":day,
            "minutes":18+person*2+(day-1)*5,"score":None if (person,day)==(6,2) else 44+person*2+(day-1)*3,
            "tasks":1+person%4+day})

DRAW_PANEL='''
ORDER=["Python","Japanese","Security"]
NUMERIC=["minutes","score","tasks"]
def draw_panel(index,df,ax):
    if index==0:
        sns.histplot(data=df,x="minutes",bins=[0,15,30,45,60],ax=ax)
        ax.set(title="1. Session duration",xlabel="Minutes",ylabel="Session rows")
    elif index==1:
        sns.ecdfplot(data=df,x="score",ax=ax)
        ax.set(title="2. Observed score thresholds",xlabel="Score",ylabel="Known-score proportion")
    elif index==2:
        sns.boxplot(data=df,x="track",y="score",order=ORDER,color="#a8cfe5",ax=ax)
        ax.set(title="3. Score distribution by track",ylabel="Score")
    elif index==3:
        sns.countplot(data=df,x="track",order=ORDER,color="#0072B2",ax=ax)
        ax.set(title="4. Session counts",ylabel="Session rows")
    elif index==4:
        sns.barplot(data=df,x="mode",y="score",order=["Solo","Guided"],estimator="mean",errorbar=None,color="#0072B2",ax=ax)
        ax.set(title="5. Mode means, not a treatment effect",ylabel="Mean known score",ylim=(0,100))
    elif index==5:
        sns.scatterplot(data=df,x="minutes",y="score",hue="track",style="track",hue_order=ORDER,ax=ax)
        ax.set(title="6. Paired complete observations",xlabel="Minutes",ylabel="Score")
    elif index==6:
        sns.lineplot(data=df,x="day",y="score",estimator="mean",errorbar=None,marker="o",ax=ax)
        ax.set(title="7. Descriptive day means",xticks=[1,2],ylabel="Mean known score")
    else:
        sns.heatmap(df[NUMERIC].corr(min_periods=3),annot=True,fmt=".2f",vmin=-1,vmax=1,center=0,cmap="vlag",ax=ax)
        ax.set_title("8. Pearson association, not cause")
    if index in [2,3]: ax.tick_params(axis="x",labelrotation=15)

def overview(df):
    fig,axs=plt.subplots(4,2,figsize=(11,14),layout="constrained")
    for index,ax in enumerate(axs.flat): draw_panel(index,df,ax)
    fig.suptitle(f"Fictional sessions:{len(df)} rows, {df['learner'].nunique()} learners, {df['score'].isna().sum()} unknown scores")
    return fig
'''

CAPSTONE_DATA='df=pd.DataFrame('+repr(FIXTURE_ROWS)+')\n'

lesson(5,"4. Eight-chart exploratory report with an evidence ledger",
    "Build a reproducible offline exploration and explain every chart's limitation.",
    [("Exploratory report; eight complementary questions", "This project uses a new fictional24-session fixture, not live personal records. Histograms, ECDF, boxes, counts, means, scatter, a day trend and a heatmap each answer a distinct scoped question."),
     ("Repeated units and confounding", "Twelve learners have two sessions each. All first sessions are Solo and all second sessions Guided, so mode is confounded with day. A score difference cannot isolate a guidance effect."),
     ("Evidence ledger", "Record source rows, unique units, known values, excluded pairs, exact summaries and limitations alongside chart files. One score is intentionally unknown, never silently replaced with zero.")],
    "Start with questions before plotting. How long were sessions, what share of known scores lies below a threshold, how are track scores distributed, and how many session rows are recorded? "
    "Then compare descriptive mode means, examine paired minutes/scores, inspect the day-level mean and summarise defined numeric associations. These eight views reuse one declared source without pretending that they are eight independent experiments. "
    "There are24 observations from12 learners and23 known scores. Day2 has one unknown score, so a day comparison changes the known-score contributors. Guided mode also coincides exactly with day2. "
    "The standalone project validates the local CSV, writes eight individual PNGs plus an overview, a self-contained interactive chart, prepared data, summary.json and interpretation.txt. Each written interpretation states what is observed and what is not established. "
    "The inline code supplies the complete fictional table and drawing functions so you can reproduce the overview without another file. Study it one branch at a time: index chooses which question the panel draws. "
    "Your mini challenge changes the population; recalculate every summary and caption. On the existing Review & rest day, shuffle this week's52 practice prompts and explain the chart choice before showing a solution.",
    'fig=overview(df)\nfig.savefig("report.png",dpi=150)\nplt.close(fig)',
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(DRAW_PANEL)+CAPSTONE_DATA+'''fig=overview(df)
fig.savefig("chart.png",dpi=110); plt.close(fig)
print("Sessions:",len(df),"Learners:",df["learner"].nunique(),"Known scores:",int(df["score"].notna().sum()))
print("Day counts:",df.groupby("day")["score"].count().to_dict())
''',
    "The counts panel includes all24 sessions; score panels use known scores. The scatter excludes one incomplete pair. The heatmap uses pairwise known rows and its companion summary records each denominator. No chart proves a mode effect, real-world teaching quality or independent population inference.",
    ('df["score"]=df["score"].fillna(0)\n# call the guided/solo difference a causal effect', '# Retain the unknown score, report denominators and disclose mode/day confounding', "Missing outcomes are not failures; an observed comparison does not isolate the cause."),
    "Remove the one unknown-score session for a complete-case overview. Print the changed source-row and learner counts and explain that counts now describe this subset.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(DRAW_PANEL)+CAPSTONE_DATA+'''df=df.dropna(subset=["score"])
fig=overview(df); fig.suptitle("Complete-case subset:23 sessions,12 learners")
fig.savefig("chart.png"); plt.close(fig)
print(len(df),df["learner"].nunique())
''',
    "Keep all sessions but add5 to every known score, recompute the overview and print the missing count and changed score mean. Do not turn the missing value into a score.",
    'import matplotlib.pyplot as plt\nimport seaborn as sns\nimport pandas as pd\n'+clean(DRAW_PANEL)+CAPSTONE_DATA+'''df["score"]=df["score"]+5
fig=overview(df); fig.suptitle("Changed fictional known scores; unknown retained")
fig.savefig("chart.png"); plt.close(fig)
print("Missing:",int(df["score"].isna().sum()))
print("Known mean:",round(df["score"].mean(),3))
''',
    "Week32 mastery: select statistical graphics deliberately, inspect aggregation and missingness, preserve units and mappings, and export offline interactive evidence with honest limits.",
    [("How many independent learner identities are recorded?","Twelve, measured twice","Twenty-four learners","Twenty-three learners","Session rows do not equal distinct people."),
     ("How many known scores exist?","23","24","12","One score is deliberately unknown."),
     ("What is the observation in countplot here?","A session row","A unique learner automatically","A score mean","Counts follow the input grain."),
     ("What describes KDE bandwidth?","A smoothing choice","A new source observation","A causal coefficient","Estimated shape depends on that choice."),
     ("What does an ECDF describe?","Share at or below each observed threshold","Mean duration","Regression slope","It is an empirical cumulative distribution."),
     ("Why does barplot need an estimator decision?","It summarises rows before drawing","It always draws every score","It only counts learners","Name the statistic and interval policy."),
     ("How should the unknown score be handled?","Retain missingness and disclose denominators","Replace it with0 automatically","Replace it with100","Unknown is not a measured outcome."),
     ("What retains individual repeated-unit paths?","units with estimator=None","A countplot title","A colourbar alone","The unit identifies which rows belong together."),
     ("Does a heatmap establish causation?","No","Always","Only if r is above0.9","Association and causal identification differ."),
     ("Why cannot this fixture isolate a Guided-mode effect?","Mode and day coincide, with repeated units and synthetic data","Because the chart is blue","Because PNG is static","There is no independent mode comparison under a valid causal design."),
     ("Which HTML export works without a Plotly CDN?","include_plotlyjs=True","include_plotlyjs='cdn'","A smaller title","The library is embedded into the document."),
     ("What happens to hidden trace data in a shared HTML?","It remains in the file","It is encrypted automatically","It is erased","Legend visibility is not access control.")])

PROJECT='''"""Week32 original fictional EDA; local validated CSV to an offline report."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px

def load_sessions(path):
    raw=Path(path).read_bytes()
    if len(raw)>1024*1024: raise ValueError("Learning CSV exceeds1MiB")
    text=raw.decode("utf-8-sig")
    rows=list(csv.reader(io.StringIO(text),strict=True))
    columns=["session_id","learner","track","mode","day","minutes","score","tasks"]
    if not rows or rows[0]!=columns or len(rows)<2 or len(rows)>10001:
        raise ValueError("Expected the documented exact header and1–10000 records")
    if any(len(row)!=len(columns) for row in rows[1:]): raise ValueError("Ragged CSV")
    df=pd.read_csv(io.StringIO(text),dtype="string",keep_default_na=False)
    for col in ["session_id","learner","track","mode"]:
        if df[col].str.strip().eq("").any(): raise ValueError("Blank identity/category")
    if df["session_id"].duplicated().any(): raise ValueError("Duplicate session IDs")
    if not df["track"].isin(["Python","Japanese","Security"]).all(): raise ValueError("Unknown track")
    if not df["mode"].isin(["Solo","Guided"]).all(): raise ValueError("Unknown mode")
    for col,low,high in [("day",1,31),("minutes",1,240),("tasks",0,100),("score",0,100)]:
        token=df[col]
        missing=token.eq("") if col=="score" else pd.Series(False,index=df.index)
        if not (missing|token.str.fullmatch(r"[0-9]+(?:\\.[0-9]+)?")).all():
            raise ValueError("Invalid numeric token: "+col)
        values=pd.to_numeric(token.mask(missing),errors="raise").astype("float64")
        if not values.dropna().between(low,high).all(): raise ValueError("Out of bounds: "+col)
        if col in ["day","tasks"] and not values.mod(1).eq(0).all(): raise ValueError("Integer required: "+col)
        df[col]=values
    if df.duplicated(["learner","day"]).any(): raise ValueError("Ambiguous learner/day pair")
    if df["score"].notna().sum()<3: raise ValueError("Need at least3 known scores")
    return df
''' + clean(DRAW_PANEL) + '''
def interactive(df):
    return px.scatter(df,x="minutes",y="score",color="track",symbol="track",
        hover_data=["session_id","mode","day","tasks"],
        labels={"minutes":"Minutes per session","score":"Score (out of100)"},
        title="Fictional complete pairs; hover and legend controls")

def evidence(df):
    known=df[NUMERIC].notna().astype(int)
    return {"sessions":len(df),"learners":int(df["learner"].nunique()),
        "known_scores":int(df["score"].notna().sum()),"unknown_scores":int(df["score"].isna().sum()),
        "complete_pairs":int(df[["minutes","score"]].notna().all(axis=1).sum()),
        "track_sessions":{str(k):int(v) for k,v in df.groupby("track").size().items()},
        "known_by_day":{str(int(k)):int(v) for k,v in df.groupby("day")["score"].count().items()},
        "mean_score":float(df["score"].mean()),
        "pair_counts":known.T.dot(known).to_dict(),
        "score_at_most65_share":float(df["score"].dropna().le(65).mean())}

def publish(df,destination):
    destination=Path(destination)
    if destination.exists() or not destination.parent.is_dir(): raise ValueError("Choose a new bundle in an existing parent")
    facts=evidence(df)
    notes=[
        "FICTIONAL EXPLORATION — no real learners or causal study",
        f"Source:{facts['sessions']} session rows, {facts['learners']} distinct learner IDs, {facts['known_scores']} known scores, {facts['unknown_scores']} unknown scores.",
        "1. Duration histogram: session minutes in explicit0/15/30/45/60 bins. The project requires minutes<=60 for this view, so none are silently excluded.",
        f"2. Score ECDF: observed share at most65 is {facts['score_at_most65_share']:.3f}, among known scores only.",
        "3. Track boxes: quartile summaries of known session scores; different tracks are not equivalent randomised groups.",
        "4. Session counts: "+json.dumps(facts["track_sessions"])+". These count sessions, not unique learners.",
        f"5. Mode means: overall known-score mean is {facts['mean_score']:.3f}. Mode comparison is descriptive, not a treatment effect; in the supplied fixture mode coincides with day.",
        f"6. Scatter: {facts['complete_pairs']} complete minutes/score pairs; the unknown outcome stays missing, not zero.",
        "7. Day means: known-score contributor counts "+json.dumps(facts["known_by_day"])+". Repeated learners and missing outcomes limit interpretation.",
        "8. Correlation: Pearson linear association with a fixed-1 to1 scale; undefined cells remain undefined. Exact pair counts are in summary.json.",
        "Limits: synthetic small repeated-measures sample; no causal, significance, forecast or real-world teaching-quality conclusion.",
        "Interactive HTML contains all embedded data; hidden traces are not private. It bundles Plotly.js for offline rendering."]
    if df["minutes"].gt(60).any(): raise ValueError("Project histogram contract requires minutes<=60")
    with TemporaryDirectory(prefix="studyhub-eda-",dir=destination.parent) as temp:
        folder=Path(temp)
        with matplotlib.rc_context({"font.size":10,"axes.spines.top":False,"axes.spines.right":False}):
            for index in range(8):
                fig,ax=plt.subplots(figsize=(6,4),layout="constrained")
                try:
                    draw_panel(index,df,ax); fig.savefig(folder/f"chart-{index+1}.png",dpi=150,facecolor="white")
                finally: plt.close(fig)
            fig=overview(df)
            try: fig.savefig(folder/"overview.png",dpi=150,facecolor="white")
            finally: plt.close(fig)
        interactive(df).write_html(folder/"interactive.html",include_plotlyjs=True,full_html=True,auto_open=False,config={"responsive":True})
        df.to_csv(folder/"prepared_sessions.csv",index=False,lineterminator="\\n")
        (folder/"summary.json").write_text(json.dumps(facts,indent=2,allow_nan=False),encoding="utf-8")
        (folder/"interpretation.txt").write_text("\\n".join(notes)+"\\n",encoding="utf-8")
        os.rename(folder,destination)
    return facts

def main(argv=None):
    parser=argparse.ArgumentParser(description="Week32 offline fictional Seaborn/Plotly exploration")
    parser.add_argument("source"); parser.add_argument("destination"); args=parser.parse_args(argv)
    try: facts=publish(load_sessions(args.source),args.destination)
    except (ValueError,OSError,csv.Error) as error: parser.exit(1,"Exploration stopped: "+str(error)+"\\n")
    print("Published13 files; sessions",facts["sessions"],"known scores",facts["known_scores"])
    return 0

if __name__=="__main__": raise SystemExit(main())
'''


def write():
    target=ROOT/"study-hub.html"; original=target.read_bytes().decode("utf-8")
    start=original.index("const DAY_TEACH = {"); end=original.index("\n};\n\nconst REST_DAY",start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS): raise RuntimeError("Week32 already exists; refusing overwrite")
    for future,destination,picture in JOBS:
        text,png=future.result()
        destination["v" if destination["t"]=="out" else "out"]=text
        if picture is not None:
            if not png: raise RuntimeError("Missing example picture")
            picture["src"]="data:image/png;base64,"+base64.b64encode(png).decode("ascii")
    POOL.shutdown()
    DAYS["32.0"]["parts"][0]["sections"].insert(3,section("sh",'python -m pip install "seaborn>=0.13.2,<0.14" "matplotlib>=3.10,<3.11" "pandas>=3,<4" "plotly>=6,<7"',note="Install once in your existing local practice environment; initial package installation needs internet. All examples use supplied fictional data without sns.load_dataset or network requests."))
    DAYS["32.5"]["parts"][0]["sections"].insert(3,section("sh",'python -m pip install "kaleido>=1,<2"',note="Optional only for write_image static PNG previews; Kaleido also needs compatible Chrome installed. The interactive write_html examples and standalone EDA project need Plotly, not Kaleido. To generate HTML alone, omit the write_image line. Verified with Seaborn0.13.2, Matplotlib3.10.9, pandas3.0.1, Plotly6.9.0 and Kaleido1.5.0."))
    for p in DAYS["32.5"]["parts"][:3]:
        for s in p["sections"]:
            if s["t"]=="figure": s["note"]="Actual static PNG export of this Plotly example. The picture itself has no hover; open the chart.html written by the example for hover, legend toggles and zoom. The supplied docs/python-week32/interactive-demo.html is a self-contained offline demo."
    DAYS["32.5"]["parts"][3]["sections"].append(section("sh","python exploration_report.py practice_sessions.csv exploration-run-01\npython exploration_report.py --help",note="From docs/python-week32. Choose exploration-run-02 for another run. Supplied files: exploration_report.py, practice_sessions.csv, interactive-demo.html and README.md. All records are fictional."))
    DAYS["32.5"]["parts"][3]["sections"].append(section("p","Primary references: https://seaborn.pydata.org/tutorial/function_overview.html · https://seaborn.pydata.org/tutorial/distributions.html · https://seaborn.pydata.org/tutorial/categorical.html · https://seaborn.pydata.org/tutorial/error_bars.html · https://seaborn.pydata.org/tutorial/axis_grids.html · https://plotly.com/python/interactive-html-export/. Original explanations, executed examples, solutions and chart previews are embedded for offline study."))
    addition="\n".join(json.dumps(k)+": "+json.dumps(v,ensure_ascii=False,indent=2)+"," for k,v in DAYS.items()).replace("</","<\\/")
    prefix=original[:end].rstrip()
    if not prefix.endswith(","): prefix+="," 
    updated=prefix+"\n"+addition+original[end:]
    folder=ROOT/"docs"/"python-week32";folder.mkdir(exist_ok=True)
    (folder/"exploration_report.py").write_text(PROJECT,encoding="utf-8",newline="\n")
    import csv
    with (folder/"practice_sessions.csv").open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(FIXTURE_ROWS[0]));writer.writeheader();writer.writerows(FIXTURE_ROWS)
    import pandas as pd
    import plotly.express as px
    df=pd.DataFrame(FIXTURE_ROWS)
    fig=px.scatter(df,x="minutes",y="score",color="track",symbol="track",hover_data=["session_id","mode","day","tasks"],title="Fictional sessions:23 complete pairs; hover and legend controls")
    fig.write_html(folder/"interactive-demo.html",include_plotlyjs=True,full_html=True,auto_open=False,config={"responsive":True})
    temporary=target.with_suffix(".html.tmp");temporary.write_bytes(updated.encode("utf-8"));temporary.replace(target)
    print("Added Week32:6 days,26 parts,52 practice prompts,62 explained quiz questions,78 executed outputs and26 embedded chart pictures; all application/storage code unchanged.")


if __name__=="__main__": write()


