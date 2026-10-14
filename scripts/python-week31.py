"""Add Week 31 without rewriting prior lessons; execute and embed real charts."""
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
DAYS = {f"31.{d}": {"parts": []} for d in range(6)}
POOL = ThreadPoolExecutor(max_workers=4)
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def chart(body):
    return 'import matplotlib.pyplot as plt\n' + clean(body) + '\nfig.savefig("chart.png", dpi=110)\nplt.close(fig)\n'


def execute(code):
    with tempfile.TemporaryDirectory(prefix="studyhub-w31-") as folder:
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
    parts = DAYS[f"31.{day}"]["parts"]
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
        section("ex", task, practiceId=f"31.{day}.{index}.build"),
        section("sol", code=clean(solution), out="", why="Build check: " + takeaway),
        section("ex", "Mini challenge: " + challenge, practiceId=f"31.{day}.{index}.challenge"),
        section("sol", code=clean(challenge_code), out="", why="Challenge check: " + takeaway),
        section("try", q=quizzes[0][0], code="# Predict first; explain your reason before revealing.", a=quizzes[0][1], why=quizzes[0][4]),
        section("checkpoint", lesson={"id": f"course:31.{day}.{index}", "quiz": questions}), section("key", takeaway)
    ]})
    for s in parts[-1]["sections"]:
        if s["t"] == "sol":
            JOBS.append((POOL.submit(execute, s["code"]), s, None))


lesson(0, "1. Figure, Axes and your first visible chart",
    "Identify the whole picture, its plotting area and the data coordinates.",
    [("Matplotlib; pyplot; plt", "Matplotlib is a Python drawing library. pyplot is its figure-management module; plt is just our short import name. It is not a new Python keyword."),
     ("Figure; Axes; Axis", "A Figure is the whole canvas. An Axes is one plotting area with data, title and labels; one Axes has an x Axis and a y Axis. The names sound similar but refer to different things."),
     ("subplots; plot; marker", "plt.subplots() returns a Figure and an Axes. ax.plot(x,y) joins paired coordinates in input order. marker='o' adds a dot at each actual observation."),
     ("savefig; close; show", "fig.savefig writes this exact figure to a local file. plt.close(fig) releases it. plt.show() opens a window in a desktop GUI backend; some notebooks display automatically. Save before a blocking show, then close when finished.")],
    "You already know objects and methods from Weeks18–19. Here fig and ax are ordinary objects returned by a function; fig.savefig and ax.plot are methods. "
    "Picture a notebook page with one graph drawn on it: the page is the Figure and the graph area is the Axes. The x values below are study-day numbers; the y values are minutes actually studied. "
    "A point (2,30) says thirty minutes on day two, not a second learner. The line helps follow this ordered series, while the dots identify the three observations. "
    "The website shows a saved picture, not an interactive Python interpreter. Run the complete example in local Python to create your own chart.png. "
    "Use a fresh practice folder: the examples deliberately reuse that filename. Reading these lessons and their embedded pictures needs no internet; installing the Python package initially does.",
    'fig, ax = plt.subplots()\nax.plot(x, y)\nfig.savefig("chart.png")\nplt.close(fig)',
    chart('''
fig, ax = plt.subplots(figsize=(6, 3), layout="constrained")
ax.plot([1, 2, 3], [20, 30, 25], marker="o")
ax.set(title="Three study days", xlabel="Day", ylabel="Minutes")
print("Axes:", len(fig.axes))
print("Day 2 minutes:", 30)
'''),
    "figsize is width and height in inches; layout='constrained' reserves room for labels. ax.set sets several named properties together. The printed output describes the data; the picture is the graphical output. Notice the drop from day2 to day3.",
    ('plt = "my chart"\nplt.subplots()', 'import matplotlib.pyplot as plt\nfig, ax = plt.subplots()', "Do not replace the imported module with a string; your variable names still follow normal Python assignment rules."),
    "Plot days1,2,3,4 with minutes10,20,15,30. Label both axes and print the number of observations.",
    chart('fig, ax = plt.subplots(layout="constrained")\nx=[1,2,3,4]; y=[10,20,15,30]\nax.plot(x,y,marker="o")\nax.set(xlabel="Day",ylabel="Minutes",title="Four study days")\nprint("Observations:",len(x))'),
    "Change the last observation to40 minutes and print the improvement over day1.",
    chart('fig, ax = plt.subplots(layout="constrained")\ny=[10,20,15,40]\nax.plot([1,2,3,4],y,marker="o")\nax.set(xlabel="Day",ylabel="Minutes")\nprint("Improvement:",y[-1]-y[0],"minutes")'),
    "Keep data meaning, canvas and plotting area separate; save the specific Figure you created.",
    [("Which object is the whole canvas?", "Figure", "One x tick", "A data row", "A Figure can contain several plotting areas."),
     ("What is plt?", "An alias for the pyplot module", "A Python keyword", "The data file", "The import chooses a convenient ordinary name.")])

lesson(0, "2. Explicit objects versus the current plot",
    "Draw through a named Axes when managing more than one figure.",
    [("Implicit interface; current Axes", "plt.plot draws on pyplot's current Axes, creating one if needed. This interface is convenient for small sketches, but hidden current state is easy to confuse."),
     ("Explicit interface; Line2D", "ax.plot targets a named Axes and returns a list of line artists. An artist is a drawable object. get_ydata reads a line's values; get_title reads an Axes title.")],
    "Both interfaces can create the same chart. The difference is how the destination is selected. In a short sketch, plt.plot is fine; with multiple figures, ax.plot makes ownership visible. "
    "Calling plt.subplots again changes pyplot's current figure. A later plt.title then acts on that current area, which may differ from the first graph you meant to edit. "
    "Use explicit references when building the sales report later this week. You do not need to avoid pyplot altogether: it still creates figures and manages windows. "
    "Read each line as a sentence: create canvasA and areaA; draw on areaA; label areaA; create canvasB and areaB; draw on areaB. This is the same object-oriented thinking you practiced with your own classes.",
    'fig, ax = plt.subplots()\nlines = ax.plot(x, y)\nax.set_title("Explicit target")',
    chart('''
fig_a, ax_a = plt.subplots()
ax_a.plot([1,2,3],[2,4,3],marker="o")
ax_a.set_title("First figure")
fig, ax = plt.subplots(figsize=(6,3),layout="constrained")
line, = ax.plot([1,2,3],[2,4,3],marker="o")
ax.set(title="Same values, explicit destination",xlabel="Day",ylabel="Tasks")
print(ax_a.get_title())
print(line.get_ydata().tolist())
plt.close(fig_a)
'''),
    "line, = unpacks a one-item list, a tuple-unpacking pattern you already know. The numbers match in both figures. Closing fig_a does not close fig; ownership is explicit throughout.",
    ('fig_a, ax_a = plt.subplots()\nfig_b, ax_b = plt.subplots()\nplt.title("Title for A")', 'ax_a.set_title("Title for A")', "After creating B, pyplot's current destination is B; naming ax_a avoids that accidental change."),
    "Create two figures. Title them Morning and Evening through their own Axes and print both titles.",
    chart('first, a = plt.subplots()\nfig, ax = plt.subplots()\na.set_title("Morning"); ax.set_title("Evening")\nax.plot([1,2],[4,6])\nprint(a.get_title(),ax.get_title())\nplt.close(first)'),
    "Give the first figure a line with values3,5 and the second one6,4. Print the two final values without using plt.plot.",
    chart('first,a=plt.subplots()\nfig,ax=plt.subplots()\nla,=a.plot([1,2],[3,5]); lb,=ax.plot([1,2],[6,4])\nprint(int(la.get_ydata()[-1]),int(lb.get_ydata()[-1]))\nplt.close(first)'),
    "Choose explicit Axes references for reliable chart ownership; pyplot is still useful for figure creation.",
    [("After creating B, how do you title A reliably?", "ax_a.set_title(...) ", "plt.title(...) without selecting A", "Rename B's data", "The named Axes selects the intended target."),
     ("Does ax.plot return the Figure?", "No; it returns line artists", "Yes, always", "It returns a CSV", "Keep fig and the returned artists as separate objects.")])

lesson(0, "3. Pair, sort and check your coordinates",
    "Preserve x/y pairing, sort ordered series and show unknown values honestly.",
    [("Input order; paired sorting", "A line joins points in the order supplied, not automatically from lowest x to highest. Sort rows or pairs together so measurements keep their matching coordinates."),
     ("NaN gap", "float('nan') is a missing numeric value. A line breaks around it; dropping that point may instead connect across an unknown interval. Choose the meaning deliberately.")],
    "A chart can be technically valid and still tell the wrong story. If March is followed by January then February in your rows, the line travels backward in time. "
    "Sorting x alone is worse: January may acquire March's sales value. Week30 taught sorting whole rows before time calculations; exactly the same rule applies here. "
    "A missing month is not automatically zero revenue. With a complete feed, absence may mean zero under a declared contract; with an incomplete export, it means unknown. "
    "Use a gap to communicate unknown observations, and state that meaning in the caption. Validate paired lengths before plotting; a mismatched x and y should be corrected at the source rather than padded with invented numbers.",
    'pairs = sorted(zip(x, y))\nxs, ys = zip(*pairs)\nax.plot(xs, ys)',
    chart('''
pairs=sorted([(3,55),(1,30),(2,25)])
xs,ys=zip(*pairs)
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
ax.plot(xs,ys,marker="o",label="Known monthly totals")
ax.set(xticks=[1,2,3],xlabel="Month number",ylabel="Revenue (fictional units)")
ax.legend()
print("Sorted pairs:",pairs)
print("Same pair count:",len(xs)==len(ys))
'''),
    "zip keeps each month attached to its amount. sorted compares month numbers here. At the end, the original March value55 still belongs to month3. xticks chooses visible tick locations; labels and legends are developed on Day3.",
    ('x.sort()  # y remains in its old order', 'pairs = sorted(zip(x,y))', "Separate sorting can invent new observations by changing x/y associations."),
    "Sort pairs (4,40),(2,20),(1,10) and draw them; print the resulting pairs.",
    chart('pairs=sorted([(4,40),(2,20),(1,10)])\nx,y=zip(*pairs)\nfig,ax=plt.subplots()\nax.plot(x,y,marker="o")\nprint(pairs)'),
    "Show an unknown day2 between known values10 and30. Print whether day2 is missing; keep the break instead of filling it with zero.",
    chart('import math\ny=[10,float("nan"),30]\nfig,ax=plt.subplots()\nax.plot([1,2,3],y,marker="o")\nax.set(xlabel="Day",ylabel="Observed minutes",title="Day 2 not recorded")\nprint("Day 2 unknown:",math.isnan(y[1]))'),
    "Charts inherit data contracts: sort paired observations and distinguish an unknown measurement from observed zero.",
    [("Does ax.plot automatically sort dates?", "No; it connects input order", "Always", "Only if values are positive", "Prepare ordered data before drawing."),
     ("What can a gap represent?", "An explicitly unknown observation", "Always zero", "A guaranteed holiday", "The caption must explain the missing-data policy.")])

lesson(0, "4. A chart-reading routine before more code",
    "Read the question, population, units, window and limitations of a chart.",
    [("Chart contract", "A chart contract states the question, what one observation represents, units, population, period and data limitations. These choices come before colours."),
     ("Observation versus conclusion", "A plotted value is an observation or summary under a data contract. A causal explanation needs evidence beyond the shape of a graph.")],
    "Practice reading before adding decoration. First ask what question the graph answers. Next inspect the horizontal categories or dates, the vertical unit, the coverage window and the meaning of a mark. "
    "These fictional totals show recorded revenue for January through March. They do not show costs, so they cannot establish profit. The line does not explain why sales changed. "
    "Only three monthly summaries are available; a claim about a lasting seasonal pattern would require more history. A title can state the observed finding while a caption carries scope and limitations. "
    "This habit prevents attractive charts from becoming confident stories unsupported by the data. Write one sentence of observation and a separate sentence of uncertainty for every chart you create this week.",
    'ax.set(title="Observed finding", xlabel="Reporting period", ylabel="Quantity (unit)")',
    chart('''
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
ax.plot([1,2,3],[300,250,550],marker="o")
ax.set(xticks=[1,2,3],xticklabels=["Jan","Feb","Mar"],ylabel="Revenue (fictional units)",title="March revenue exceeds January in this sample")
ax.set_xlabel("2025 complete months; 8 fictional sale lines")
print("Observed change:",550-300,"fictional units")
print("Not measured: costs, profit, cause")
'''),
    "The totals are the Week30 fixture divided by100 minor units per fictional currency unit. You can compare300,250,550 without claiming real business results. The subtitle makes the three-month coverage visible.",
    ('ax.set_title("Campaign proves higher profit")', 'ax.set_title("Recorded revenue is higher in March")', "Neither profit nor a causal campaign effect is measured here."),
    "Plot monthly known task counts5,8,6. Put both the time period and count unit on the chart, and print one supported observation.",
    chart('fig,ax=plt.subplots(layout="constrained")\nax.plot([1,2,3],[5,8,6],marker="o")\nax.set(xticks=[1,2,3],xlabel="Month in this sample",ylabel="Completed tasks (count)",title="Month 2 has the most recorded tasks")\nprint("Month 2:",8,"tasks")'),
    "Plot revenue100,150 and state why the increase alone does not prove higher profit.",
    chart('fig,ax=plt.subplots(layout="constrained")\nax.plot([1,2],[100,150],marker="o")\nax.set(xlabel="Month",ylabel="Revenue (fictional units)")\nprint("Revenue rose by",150-100)\nprint("Profit unknown: costs were not supplied")'),
    "A useful chart answers a scoped question; honest interpretation separates measured changes from missing evidence.",
    [("Can revenue alone establish profit?", "No; costs are missing", "Always", "Only on line charts", "Profit requires revenue and the relevant costs."),
     ("What should be chosen before colours?", "The question and units", "A 3D effect", "The thickest line", "Design follows the quantity and comparison being communicated.")])

lesson(1, "1. Lines for ordered change, bars for categories",
    "Choose line or bar from the meaning of x; build grouped bars with aligned positions.",
    [("bar; barh; BarContainer", "ax.bar draws vertical bars and barh draws horizontal ones. Bar heights or lengths encode magnitude, so an ordinary nonnegative bar comparison should start at zero. bar returns a container of rectangle artists."),
     ("Grouped bars; numeric positions", "For two series in each category, give them neighbouring numeric x positions and equal widths. np.arange creates integer positions; NumPy was introduced in Week27.")],
    "Months have an order and a line can emphasise change across that order. Book and Pen are categories with no implied intermediate product: bars are usually a clearer comparison. "
    "A line connecting products can imply a progression that the labels do not possess. For two regions per product, grouped bars let you compare each region inside each product. "
    "Place one bar slightly left and the other slightly right of the category centre. If both use exactly the same x coordinate, one hides the other. "
    "Use a shared baseline of zero so bar lengths remain proportional. A narrow line-chart scale may be acceptable with clear labels; the same truncated scale changes the visual meaning of bar length.",
    'x=np.arange(len(labels))\nax.bar(x-width/2, first, width=width)\nax.bar(x+width/2, second, width=width)',
    chart('''
import numpy as np
labels=["Book","Pen"]; x=np.arange(len(labels)); width=0.35
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
ax.bar(x-width/2,[300,300],width=width,label="NP")
ax.bar(x+width/2,[400,100],width=width,label="JP")
ax.set(xticks=x,xticklabels=labels,ylabel="Revenue (fictional units)",title="Revenue by product and region")
ax.set_ylim(bottom=0); ax.legend()
print("NP total:",sum([300,300]))
print("JP total:",sum([400,100]))
'''),
    "Each product has two bars; the legend identifies regions. This is a separate tiny illustration, not the full Week30 project. Equal widths and a zero baseline make length comparisons fair.",
    ('ax.bar(x,first); ax.bar(x,second)', 'ax.bar(x-width/2,first,width); ax.bar(x+width/2,second,width)', "Identical positions overlap instead of forming a side-by-side comparison."),
    "Draw a horizontal category chart for Reading12, Coding18, Review9 minutes. Print the largest category.",
    chart('labels=["Reading","Coding","Review"]; values=[12,18,9]\nfig,ax=plt.subplots(layout="constrained")\nax.barh(labels,values); ax.set(xlabel="Minutes",title="Practice activities")\nax.set_xlim(left=0)\nprint(labels[values.index(max(values))])'),
    "Build grouped bars for tasks A/B: planned5,8 and completed4,6. Print the total shortfall.",
    chart('import numpy as np\nx=np.arange(2); w=0.35\nfig,ax=plt.subplots(layout="constrained")\nax.bar(x-w/2,[5,8],w,label="Planned"); ax.bar(x+w/2,[4,6],w,label="Completed")\nax.set(xticks=x,xticklabels=["A","B"],ylabel="Tasks"); ax.legend()\nprint("Shortfall:",sum([5,8])-sum([4,6]))'),
    "Connect meaningful ordered positions; compare categories with bars whose baseline and grouping are explicit.",
    [("Why start ordinary positive bars at zero?", "Length encodes magnitude", "It sorts the categories", "It changes the data", "A truncated baseline exaggerates relative lengths."),
     ("How are grouped bars separated?", "Offset their numeric positions", "Use the same position twice", "Drop one series", "Small opposing offsets preserve each category centre.")])

lesson(1, "2. Scatter: one point is one paired observation",
    "Show relationships without inventing connections or claiming causation.",
    [("scatter; PathCollection", "ax.scatter places a mark at each paired x/y observation and returns a collection of those marks. get_offsets reads their coordinates. Unlike plot's default line, scatter does not connect them."),
     ("alpha; s", "alpha controls opacity from0 transparent to1 opaque. scatter's s controls marker area in points squared, not its radius. Overlapping points may need transparency rather than larger marks.")],
    "Suppose a row describes one fictional practice session with minutes studied and a score. A scatter plot asks whether sessions with more minutes tend to have different scores. "
    "It does not show time order unless a separate variable encodes that order. Joining these points into a line would assert a sequence that may not exist. "
    "Keep both coordinates from the same row when filtering missing data. If marks overlap, several sessions can look like one; transparency helps but does not reveal exact counts reliably. "
    "Even a clear upward pattern does not prove that extra minutes caused higher scores: task difficulty, prior knowledge and selection can differ. Week33 studies statistical reasoning; today describe the visible association carefully.",
    'points=ax.scatter(minutes, scores, s=50, alpha=0.7)',
    chart('''
minutes=[10,20,20,30,40]; scores=[45,65,55,70,80]
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
points=ax.scatter(minutes,scores,s=55,alpha=0.7)
ax.set(xlabel="Study minutes in one session",ylabel="Score (out of 100)",title="Five fictional sessions")
print("Points:",len(points.get_offsets()))
print("Sessions at 20 minutes:",minutes.count(20))
'''),
    "There are five paired observations. Two have x=20, but their different y values remain visible. The caption identifies a fictional sample, not an experiment that establishes a learning effect.",
    ('ax.plot(minutes,scores)  # unordered sessions connected', 'ax.scatter(minutes,scores)', "A relationship plot does not need an invented path between independent observations."),
    "Scatter units1,2,3,4 against revenue80,180,210,400. Label both units and print the number of points.",
    chart('x=[1,2,3,4]; y=[80,180,210,400]\nfig,ax=plt.subplots(layout="constrained")\npoints=ax.scatter(x,y)\nax.set(xlabel="Units per sale line",ylabel="Revenue (fictional units)")\nprint("Points:",len(points.get_offsets()))'),
    "Use a row-level paired filter on [(10,50),(None,60),(30,80)]. Plot only complete pairs and print the excluded count.",
    chart('rows=[(10,50),(None,60),(30,80)]\nvalid=[(x,y) for x,y in rows if x is not None and y is not None]\nx,y=zip(*valid)\nfig,ax=plt.subplots()\nax.scatter(x,y)\nax.set(xlabel="Minutes",ylabel="Score")\nprint("Excluded:",len(rows)-len(valid))'),
    "One scatter mark should have a clear observation meaning; visible association alone does not establish a cause.",
    [("What does one point represent here?", "One paired session observation", "One month automatically", "A causal effect", "The x and y must belong to the same row."),
     ("Does s specify a scatter marker's radius?", "No; it specifies area", "Always", "It specifies opacity", "Area is measured in points squared; alpha controls opacity.")])

lesson(1, "3. Histograms and box plots: distributions",
    "Separate numeric intervals from categories and read a box plot's limits.",
    [("hist; bins; count", "ax.hist groups numeric observations into bins and returns counts, bin edges and patches. Intervals are left-closed/right-open except that the last bin includes its right edge. A bin count depends on chosen edges."),
     ("Box plot; median; quartiles; IQR", "ax.boxplot summarises sorted values. The box spans the25th to75th percentiles and the middle line marks the median. IQR is upper minus lower quartile."),
     ("Whiskers; fliers", "Default whiskers reach the most extreme observed points within1.5 IQR of the quartiles. Marks beyond are fliers, not automatically errors or exactly a fixed percentile. Box plots do not show every feature of a distribution.")],
    "A bar chart compares named categories. A histogram groups one numeric variable into intervals, such as session durations from0 to10 minutes. "
    "Different bin widths can reveal or hide apparent structure, especially with small samples. State the edges and sample count rather than choosing only the picture that supports a favourite story. "
    "A box plot gives a compact summary for comparing several distributions. Two very different shapes can share similar quartiles, so it is not a replacement for examining the underlying values. "
    "A value outside the whiskers deserves investigation; deleting it merely because it is drawn as a flier would turn a visual convention into an unsupported cleaning rule.",
    'counts,edges,patches=ax.hist(values,bins=[0,10,20,30])\nax.boxplot([group_a,group_b],tick_labels=["A","B"])',
    chart('''
values=[5,8,10,12,18,20,22,29]
fig,axs=plt.subplots(1,2,figsize=(7,3),layout="constrained")
counts,edges,_=axs[0].hist(values,bins=[0,10,20,30],edgecolor="white")
axs[0].set(xlabel="Minutes",ylabel="Sessions (count)",title="Explicit 10-minute bins")
axs[1].boxplot(values,tick_labels=["All sessions"])
axs[1].set(ylabel="Minutes",title="Same eight observations")
print("Bin counts:",counts.astype(int).tolist())
print("Count reconciles:",int(counts.sum())==len(values))
'''),
    "axs is an array of two Axes; Day4 develops layouts. Histogram counts are2,3,3 because10 starts the second interval and20 starts the third. Both panels use the same eight values but answer different reading questions.",
    ('ax.bar(values,values)  # call this a distribution', 'ax.hist(values,bins=[0,10,20,30])', "Numeric bins count observations in intervals; unique-value bars are a different representation."),
    "Histogram scores [0,5,10,15,20] with edges0,10,20. Print the counts and explain where20 is counted.",
    chart('fig,ax=plt.subplots()\ncounts,edges,_=ax.hist([0,5,10,15,20],bins=[0,10,20])\nax.set(xlabel="Score",ylabel="Observations")\nprint(counts.astype(int).tolist())\nprint("20 belongs to the final bin")'),
    "Compare groupA [10,12,14,16,18] and groupB [8,12,16,20,50] with boxes. Print their medians, and do not remove50 automatically.",
    chart('import numpy as np\na=[10,12,14,16,18]; b=[8,12,16,20,50]\nfig,ax=plt.subplots()\nax.boxplot([a,b],tick_labels=["A","B"])\nax.set(ylabel="Minutes",title="A flier is a prompt to investigate")\nprint("Medians:",float(np.median(a)),float(np.median(b)))'),
    "Bins influence histograms; box plots summarise quartiles and flag distant values without proving they are wrong.",
    [("Are box-plot fliers automatically bad records?", "No; investigate them", "Yes; delete them", "They are always zero", "The whisker rule is a plotting convention, not source validation."),
     ("In bins [0,10,20], where is value20 counted?", "The last bin", "The first bin", "It is always discarded", "The final histogram interval includes its right edge.")])

lesson(1, "4. Pie charts, denominators and a six-chart choice test",
    "Use part-to-whole charts only when the whole and categories make sense.",
    [("pie; autopct; normalisation", "ax.pie displays nonnegative parts of a total; by default it normalises the supplied values. autopct='%1.0f%%' formats percentage labels. A valid arithmetic sum does not prove the denominator is meaningful."),
     ("Mutually exclusive and exhaustive categories", "Each observation belongs to one category and all relevant categories are included. Overlapping labels or omitted categories undermine a part-to-whole interpretation.")],
    "A pie can communicate a simple composition when there are few distinct categories. Here Reading, Coding and Review partition sixty recorded minutes. "
    "If one minute could count as both Reading and Review, adding the values would double-count time and the pie would mislead. Missing activities also change the denominator. "
    "Close category values are usually easier to compare as bars; 3D pies further distort area and angle. Do not use a pie for negative profit or a long list of similar slices. "
    "Now rehearse all six chart choices using the same kind of session table: line for ordered daily minutes, bar for activity totals, scatter for minutes versus score, histogram for durations, box for duration spread by activity, pie for an exclusive time allocation. The question chooses the chart.",
    'ax.pie(values,labels=labels,autopct="%1.0f%%")',
    chart('''
labels=["Reading","Coding","Review"]; values=[15,30,15]
fig,ax=plt.subplots(figsize=(5,3.5),layout="constrained")
ax.pie(values,labels=labels,autopct="%1.0f%%",startangle=90)
ax.set_title("One recorded hour, exclusive activities")
print("Whole:",sum(values),"minutes")
print("Coding share:",100*values[1]/sum(values))
'''),
    "The50% label has a specific denominator:60 exclusive recorded minutes. startangle rotates the starting wedge; it does not change the quantities. A missing category would produce new percentages even if Coding stayed at30.",
    ('ax.pie([40,40],labels=["All study","Reading within study"])', 'ax.bar(["All study","Reading within study"],[40,40])', "A total and its subset overlap; they cannot be separate slices of the same whole. Even as bars, label their relationship clearly."),
    "Draw a pie for20,30,50 exclusive minutes and print the total and the first percentage.",
    chart('values=[20,30,50]\nfig,ax=plt.subplots()\nax.pie(values,labels=["A","B","C"],autopct="%1.0f%%")\nprint(sum(values),100*values[0]/sum(values))'),
    "Replace a pie with a horizontal bar for close shares49 and51. Print their difference in percentage points.",
    chart('fig,ax=plt.subplots()\nax.barh(["A","B"],[49,51]); ax.set(xlabel="Share (%)",xlim=(0,100))\nprint("Difference:",51-49,"percentage points")'),
    "Choose a chart by the question: a meaningful whole and non-overlapping parts are prerequisites for a pie.",
    [("Which comparison is usually easier for close values?", "Aligned bar lengths", "A 3D pie angle", "Unlabelled colours", "A common baseline supports precise comparisons."),
     ("Can a pie prove categories do not overlap?", "No; validate the category meaning", "Yes, because it sums to100%", "Only with three colours", "Normalisation is arithmetic, not a data-quality guarantee.")])

lesson(2, "1. Titles, units, legends and readable ticks",
    "Make labels explain the quantity rather than merely decorate the chart.",
    [("label; legend", "A plotted artist's label supplies its legend entry when ax.legend is called. A legend identifies series; the axis label explains what the values measure."),
     ("set_xticks; tick positions and labels", "Ticks locate reference marks on an axis. set_xticks(positions,labels=...) keeps labels paired with their exact positions. Labels alone must not float independently of positions.")],
    "An axis label such as Value forces the reader to guess. Revenue (fictional units) identifies both the measurement and its scale. "
    "A legend answers which line belongs to which series; it cannot replace the units. Label the lines when creating them, then request a legend. "
    "Keep categories readable with short names, horizontal bars or a modest rotation. Rotating a hundred labels does not repair a chart that is too crowded. "
    "A title should identify the question or a supported finding. Put sample coverage and exclusions in a caption or subtitle. Reuse the same units for comparisons and avoid a silent switch from minor currency units to whole units.",
    'ax.plot(x,y,label="Recorded")\nax.legend()\nax.set_xticks([1,2,3],labels=["Jan","Feb","Mar"])',
    chart('''
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
ax.plot([1,2,3],[300,250,550],marker="o",label="Recorded revenue")
ax.plot([1,2,3],[280,300,400],linestyle="--",label="Fictional plan")
ax.set_xticks([1,2,3],labels=["Jan","Feb","Mar"])
ax.set(title="Recorded and planned revenue",xlabel="2025 complete months",ylabel="Fictional currency units")
ax.legend()
print("Legend:",[text.get_text() for text in ax.get_legend().get_texts()])
'''),
    "The dashed series is explicitly a plan, not another observed result. get_legend returns the legend object and get_texts returns its label artists; get_text reads the string in each. This is inspecting objects, not parsing the picture.",
    ('ax.set_xticklabels(["Jan","Feb","Mar"])  # positions unspecified', 'ax.set_xticks([1,2,3],labels=["Jan","Feb","Mar"])', "Fix positions and their corresponding labels together."),
    "Draw planned3,4 versus completed2,5 tasks across two weeks with a legend and a count axis.",
    chart('fig,ax=plt.subplots(layout="constrained")\nax.plot([1,2],[3,4],label="Planned"); ax.plot([1,2],[2,5],label="Completed")\nax.set(xlabel="Week",ylabel="Tasks (count)"); ax.legend()\nprint("Series:",len(ax.lines))'),
    "Plot [10000,20000] minor units after dividing by100. Print the converted values and use the matching axis unit.",
    chart('values=[x/100 for x in [10000,20000]]\nfig,ax=plt.subplots()\nax.bar(["A","B"],values); ax.set(ylabel="Fictional currency units")\nprint(values)'),
    "Labels should expose units, series identity and scope; legends do not repair an undefined measurement.",
    [("Where does a legend normally get its series names?", "Artist label arguments", "The y-axis unit alone", "The filename", "Supply label when drawing each series, then call legend."),
     ("After dividing minor units by100, what changes?", "The displayed unit and label", "Only the colour", "The number of observations", "The axis must describe the transformed values.")])

lesson(2, "2. Limits, scales and grids without distortion",
    "Use axis limits and logarithmic scales deliberately and make comparisons fair.",
    [("set_xlim; set_ylim; grid; set_axisbelow", "Limits choose the displayed range; they can hide observations outside it. grid adds reference lines; set_axisbelow(True) places gridlines behind data artists."),
     ("Logarithmic scale", "A log axis assigns equal distances to equal ratios, such as1→10 and10→100. Ordinary log scales require positive values; zero and negative values need another representation, not an invented replacement.")],
    "A grid is a reading aid. Light horizontal references can help compare heights without becoming the main visual feature. "
    "Limits are analytical decisions: zooming a line can reveal small variation, but the scale must remain visible. For positive bars, retain zero unless there is a clearly explained specialised alternative. "
    "On a log axis, equal steps represent multiplication, not addition. This is useful for quantities spanning several orders of magnitude, but it changes how the reader interprets vertical distance. "
    "Check for zero and negative values before choosing it. Comparing charts with different limits can exaggerate differences even when each chart individually looks reasonable; Day4 uses shared axes to address that.",
    'ax.set_ylim(bottom=0)\nax.grid(axis="y",alpha=0.25)\nax.set_yscale("log")  # only when appropriate',
    chart('''
fig,axs=plt.subplots(1,2,figsize=(7,3),layout="constrained")
for ax in axs:
    ax.plot([1,2,3],[1,10,100],marker="o")
    ax.set(xlabel="Step",ylabel="Positive quantity")
    ax.grid(axis="y",alpha=0.25); ax.set_axisbelow(True)
axs[0].set_title("Linear: equal additive steps")
axs[1].set_yscale("log"); axs[1].set_title("Log: equal ratios")
print("Values positive:",all(v>0 for v in [1,10,100]))
print("Scales:",[ax.get_yscale() for ax in axs])
'''),
    "The same1,10,100 values appear in both panels. On the right, each tenfold jump occupies the same vertical distance. That pattern is a property of the scale, not a new dataset.",
    ('ax.bar(["A","B"],[99,100]); ax.set_ylim(98,101)', 'ax.bar(["A","B"],[99,100]); ax.set_ylim(bottom=0)', "Cutting off most of the bar makes a one-unit difference look disproportionately large."),
    "Draw bars99 and100 with a zero baseline and a light y-grid. Print the lower y-limit.",
    chart('fig,ax=plt.subplots()\nax.bar(["A","B"],[99,100]); ax.set_ylim(bottom=0)\nax.grid(axis="y",alpha=0.2); ax.set_axisbelow(True)\nprint("Baseline:",ax.get_ylim()[0])'),
    "Validate [0,10,100] before choosing log scale; keep a linear plot and print why the log precondition fails.",
    chart('values=[0,10,100]\nfig,ax=plt.subplots()\nax.plot([1,2,3],values,marker="o")\nax.set(ylabel="Quantity (linear scale)")\nprint("Ordinary log allowed:",all(v>0 for v in values))'),
    "A scale changes visual distances; show the scale and preserve the quantitative meaning of marks.",
    [("Equal distances on a log axis represent what?", "Equal ratios", "Equal differences always", "Equal sample counts", "Tenfold steps are equally spaced on a base10 log scale."),
     ("Can limits hide data?", "Yes; points outside the displayed range may disappear", "No", "Only legend entries", "Limits change the view, so inspect what they exclude.")])

lesson(2, "3. Annotate a finding, not every point",
    "Label a maximum with correct coordinates and keep annotations readable.",
    [("annotate; xy; xytext", "ax.annotate places text referring to a target point xy. xytext controls the text location. textcoords='offset points' makes that location an offset in display points rather than another data measurement."),
     ("arrowprops", "A dictionary of arrow drawing options; arrowstyle='->' requests an arrow from the annotation toward its target. An annotation does not modify the original data.")],
    "A useful annotation directs attention to one meaningful observation. Labeling every point can hide the series underneath. "
    "Find the maximum from the data, then use both its x and y coordinate. Confusing a value with its list index places the note at the wrong location. "
    "The largest value may occur more than once: this example labels the first occurrence, a stated display choice rather than a claim that it is uniquely best. "
    "Offsetting the text in display points helps it stay near the mark when the data unit changes. Leave enough room above the point and inspect the exported image; automatic layout cannot choose a meaningful position for every annotation.",
    'ax.annotate("Peak",xy=(x[i],y[i]),xytext=(0,12),textcoords="offset points",arrowprops={"arrowstyle":"->"})',
    chart('''
x=[1,2,3,4]; y=[20,40,30,40]
i=y.index(max(y))
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
ax.plot(x,y,marker="o")
ax.annotate("First peak: 40 min",xy=(x[i],y[i]),xytext=(0,15),textcoords="offset points",ha="center",arrowprops={"arrowstyle":"->"})
ax.set(xlabel="Day",ylabel="Minutes",ylim=(0,55),title="Two equal peaks; first labelled")
print("First peak day:",x[i])
print("Peak occurrences:",y.count(max(y)))
'''),
    "list.index returns the first matching position. x[i] is day2 even though i is1. ha='center' horizontally centres the text on its offset position. The second peak remains visible and is acknowledged in the title.",
    ('ax.annotate("Peak",xy=(max(y),max(y)))', 'i=y.index(max(y)); ax.annotate("Peak",xy=(x[i],y[i]))', "A vertical value is not automatically the matching horizontal coordinate."),
    "Annotate the maximum of x=[1,2,3], y=[5,12,8]. Print the actual peak coordinate.",
    chart('x=[1,2,3]; y=[5,12,8]; i=y.index(max(y))\nfig,ax=plt.subplots()\nax.plot(x,y,marker="o"); ax.set_ylim(0,16)\nax.annotate("Peak",xy=(x[i],y[i]),xytext=(0,12),textcoords="offset points")\nprint((x[i],y[i]))'),
    "Label the minimum of [8,3,6] at days1,2,3 and print its day. Keep enough vertical room for the label.",
    chart('x=[1,2,3]; y=[8,3,6]; i=y.index(min(y))\nfig,ax=plt.subplots()\nax.plot(x,y,marker="o"); ax.set_ylim(0,12)\nax.annotate("Lowest recorded",xy=(x[i],y[i]),xytext=(12,12),textcoords="offset points",arrowprops={"arrowstyle":"->"})\nprint("Minimum day:",x[i])'),
    "Compute the target from data, state tie choices and inspect annotation placement in the exported chart.",
    [("What is xy in annotate?", "The target data coordinate", "Always the text offset", "The filename", "xy identifies the point the annotation refers to."),
     ("What does y.index(max(y)) choose when maxima tie?", "The first maximum's index", "All tied indexes", "The last maximum only", "A single label needs a stated tie-handling choice.")])

lesson(2, "4. Dates and percentages need honest formatting",
    "Format calendar ticks and fractions without changing what the numbers mean.",
    [("matplotlib.dates; DateFormatter", "The dates module supplies calendar-aware tick locators and formatters. DateFormatter('%b') displays month abbreviations; the underlying coordinates remain dates."),
     ("PercentFormatter; xmax", "PercentFormatter(xmax=1) interprets1 as100%. Use xmax=100 for values already stored as percentages. Formatting changes labels, not the underlying data."),
     ("tick_params", "tick_params changes tick appearance, such as label rotation. It does not change the actual data positions or values.")],
    "You studied date parsing and complete-month coverage in Week30. Keep timestamps as dates rather than converting them to loosely sorted month-name strings. "
    "Jan, Feb, Mar sort alphabetically into the wrong order if treated as ordinary labels without an explicit calendar order. A formatter changes the presentation while the original temporal coordinates remain intact. "
    "Percentages need an equally explicit convention. A fraction0.25 means25%; a numeric percentage25 also means25%, but the formatter's full-scale parameter must match. "
    "Do not multiply by100 and also format as though the values were fractions. Check a known reference value before trusting a whole chart of formatted ticks.",
    'ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))\nax.yaxis.set_major_formatter(PercentFormatter(xmax=1))',
    chart('''
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter
dates=[datetime(2025,m,1) for m in [1,2,3]]
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
ax.plot(dates,[0.25,0.50,0.75],marker="o")
ax.set_xticks(dates); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
ax.set(ylim=(0,1),ylabel="Share of observed sessions",title="Fractions displayed as percentages")
print("Middle value:",0.5,"=",50,"percent")
'''),
    "xaxis and yaxis are the Axis objects inside the Axes. set_major_formatter supplies their display rule. Fractions remain0.25,0.5,0.75; the visible tick text is expressed in percentages.",
    ('ax.plot([1,2],[25,50]); ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))', 'ax.plot([1,2],[25,50]); ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))', "The data is already on a0–100 percentage scale, so100 must represent100%."),
    "Plot fractions0.2,0.4,0.6 and display a0–100% y-axis. Print their underlying sum.",
    chart('from matplotlib.ticker import PercentFormatter\nvalues=[0.2,0.4,0.6]\nfig,ax=plt.subplots()\nax.plot([1,2,3],values,marker="o"); ax.set_ylim(0,1)\nax.yaxis.set_major_formatter(PercentFormatter(xmax=1))\nprint("Underlying sum:",round(sum(values),1))'),
    "Plot percentages20,40,60 with xmax=100 and print the largest underlying value, proving formatting does not rescale data.",
    chart('from matplotlib.ticker import PercentFormatter\nvalues=[20,40,60]\nfig,ax=plt.subplots()\nline,=ax.plot([1,2,3],values); ax.set_ylim(0,100)\nax.yaxis.set_major_formatter(PercentFormatter(xmax=100))\nprint("Largest stored value:",int(max(line.get_ydata())))'),
    "Formatters change visible labels; keep dates, fraction scales and percentage-point comparisons explicit.",
    [("Which xmax suits fraction0.25 displayed as25%?", "1", "100", "0.25", "A full-scale fraction of1 represents100%."),
     ("Does a DateFormatter sort a series?", "No; sort the data first", "Always", "Only on Mondays", "Display formatting does not reorder the observations.")])

lesson(3, "1. A 2-by-2 figure without losing your Axes",
    "Address individual panels and choose layouts before plotting.",
    [("subplots rows/columns; Axes array", "plt.subplots(2,2) returns a Figure and a2D NumPy array of Axes. axs[row,column] selects a panel; indexes start at0. With the default squeeze, one panel returns an Axes instead of an array."),
     ("squeeze=False; flat; suptitle", "squeeze=False keeps the Axes collection2D even for a1-by-1 layout. axs.flat iterates its panels in row-major order. fig.suptitle supplies a title for the whole figure.")],
    "A report often needs several complementary views. Instead of opening four unrelated windows, put them on one canvas and decide how the reader should move through them. "
    "The array describes layout, not a table of measurements: axs[0,1] is the upper-right plotting object. Each panel still has its own data and labels. "
    "Create the layout with enough physical space and enable constrained layout before adding titles. Text that fits on a wide desktop figure may be unreadable when pasted into a narrow document. "
    "Use a consistent reading order and one question per panel. More panels are useful only when each contributes information; duplicated or tiny panels increase effort without increasing understanding.",
    'fig,axs=plt.subplots(2,2,layout="constrained")\naxs[0,1].plot(x,y)\nfig.suptitle("Whole report")',
    chart('''
fig,axs=plt.subplots(2,2,figsize=(7,5),layout="constrained")
axs[0,0].plot([1,2,3],[3,2,5],marker="o"); axs[0,0].set_title("A. Monthly trend")
axs[0,1].bar(["Book","Pen"],[7,3]); axs[0,1].set_title("B. Category totals")
axs[1,0].scatter([1,2,3],[2,5,4]); axs[1,0].set_title("C. Paired observations")
axs[1,1].hist([1,1,2,3,3,3],bins=[0.5,1.5,2.5,3.5]); axs[1,1].set_title("D. Distribution")
fig.suptitle("Four complementary views — fictional data")
print("Axes array shape:",axs.shape)
print("Panels:",len(fig.axes))
'''),
    "The first index chooses a row and the second a column. Each chart is drawn on the named destination. The figure-level title describes the collection; panel titles identify each question. These are small layout illustrations, not identical measures.",
    ('axs[1].plot(x,y)  # with a2D 2-by-2 array', 'axs[1,0].plot(x,y)', "axs[1] is a row of Axes, not one plotting area."),
    "Make a2-by-2 grid and title panels A,B,C,D through axs.flat. Print the title order.",
    chart('fig,axs=plt.subplots(2,2,layout="constrained")\nfor ax,title in zip(axs.flat,["A","B","C","D"]):\n    ax.plot([1,2],[2,3]); ax.set_title(title)\nprint([ax.get_title() for ax in axs.flat])'),
    "Create a1-by-1 layout with squeeze=False, draw through axs[0,0], and print its array shape.",
    chart('fig,axs=plt.subplots(1,1,squeeze=False)\naxs[0,0].plot([1,2],[4,5])\nprint(axs.shape)'),
    "An Axes array is a map of plotting destinations; select a single panel before calling its plotting methods.",
    [("Which panel is axs[0,1]?", "Top right in a2-by-2 grid", "Bottom left", "The entire Figure", "Rows and columns are zero-indexed."),
     ("What keeps a1-by-1 Axes collection2D?", "squeeze=False", "sharex=True alone", "A legend", "The squeeze argument controls the return shape.")])

lesson(3, "2. Shared axes for fair panel comparisons",
    "Share comparable scales and avoid forcing unlike units onto one axis.",
    [("sharex; sharey", "Shared axes link their view limits and scales. Use them when quantities are comparable. Matplotlib may suppress repeated tick labels; each panel still needs an understandable context."),
     ("Common limits", "Equal numeric values should occupy equal distances across panels intended for magnitude comparison. Common units and aligned limits make that possible.")],
    "If two regional charts independently expand to their own minimum and maximum, a small series may appear just as large as a large one. "
    "A common y scale preserves absolute comparison. Sharing x is useful when panels describe the same time window. Labels may appear only on outer panels to reduce repetition, but the shared unit must remain clear. "
    "Do not share one y scale between revenue and number of customers merely because both are numeric. Different units need different labelled panels. "
    "Shared axes are not mandatory for every chart: independent scales may help inspect shape, but disclose that choice and avoid presenting the panels as direct magnitude comparisons.",
    'fig,axs=plt.subplots(1,2,sharex=True,sharey=True)\naxs[0].set_ylim(0,120)',
    chart('''
fig,axs=plt.subplots(1,2,sharex=True,sharey=True,figsize=(7,3),layout="constrained")
for ax,name,values in zip(axs,["A","B"],[[10,15,20],[60,90,100]]):
    ax.plot([1,2,3],values,marker="o"); ax.set(title="Region "+name,xlabel="Month")
axs[0].set(ylabel="Revenue (same fictional units)",ylim=(0,120))
print("Same y limits:",axs[0].get_ylim()==axs[1].get_ylim())
'''),
    "Both panels use0–120. RegionA really has lower values in this sample; the linked scale makes that visible. Changing the first y-limit changes the linked second view as well.",
    ('plt.subplots(1,2,sharey=True)  # left: dollars, right: people', 'plt.subplots(1,2,sharey=False)  # label each distinct unit', "Equal numeric ticks do not make unlike units comparable."),
    "Plot minutes[10,20] and[30,40] on two shared-y panels. Set0–50 and print whether limits agree.",
    chart('fig,axs=plt.subplots(1,2,sharey=True)\naxs[0].plot([1,2],[10,20]); axs[1].plot([1,2],[30,40])\naxs[0].set_ylim(0,50); axs[0].set_ylabel("Minutes")\nprint(axs[0].get_ylim()==axs[1].get_ylim())'),
    "Put revenue100,200 and people2,3 in separate unshared panels; print both y labels.",
    chart('fig,axs=plt.subplots(1,2,layout="constrained")\naxs[0].bar(["Jan","Feb"],[100,200]); axs[0].set_ylabel("Revenue (units)")\naxs[1].bar(["Jan","Feb"],[2,3]); axs[1].set_ylabel("People (count)")\nprint([ax.get_ylabel() for ax in axs])'),
    "Share axes for comparable measurements; distinguish absolute magnitude from shape and keep units explicit.",
    [("When is sharey a useful default?", "Panels compare the same quantity in the same unit", "One panel is money and another people", "The titles are long", "A common scale supports direct magnitude comparisons."),
     ("Can independent automatic limits make unequal series look similar?", "Yes", "Never", "Only in pies", "Each panel can otherwise stretch its range to fill the same visual height.")])

lesson(3, "3. GridSpec: give the main question more space",
    "Use an unequal layout without overlapping plotting areas.",
    [("GridSpec; add_gridspec; add_subplot", "A GridSpec describes rows and columns inside a Figure. fig.add_gridspec creates it; fig.add_subplot(gs[...]) creates an Axes covering selected cells. Slices can span multiple rows or columns."),
     ("width_ratios; height_ratios", "Ratios allocate relative space rather than exact pixel sizes. A2-to1 width ratio gives one column about twice the other's available plotting width.")],
    "Four equal panels are not always the best report. A time trend may need a wide horizontal area while two compact category summaries fit beside it. "
    "GridSpec lets the question determine the space. Start with one Figure, describe its grid, then add only the Axes you intend to use. "
    "Avoid creating a full subplots grid and then drawing overlapping Axes on top of it unless you deliberately remove the originals. Hidden Axes can retain ticks or backgrounds and confuse later editing. "
    "A grid slice selects a region: gs[:,0] means every row of the first column. It follows the same row/column slicing idea you learned in NumPy. Keep panel count and units clear even when sizes differ.",
    'gs=fig.add_gridspec(2,2,width_ratios=[2,1])\nmain=fig.add_subplot(gs[:,0])',
    chart('''
fig=plt.figure(figsize=(7,4),layout="constrained")
gs=fig.add_gridspec(2,2,width_ratios=[2,1])
main=fig.add_subplot(gs[:,0]); top=fig.add_subplot(gs[0,1]); bottom=fig.add_subplot(gs[1,1])
main.plot([1,2,3],[300,250,550],marker="o"); main.set(title="A. Trend",xlabel="Month",ylabel="Revenue (units)")
top.bar(["NP","JP"],[600,500]); top.set_title("B. Regions")
bottom.bar(["Book","Pen"],[700,400]); bottom.set_title("C. Products")
fig.suptitle("Main question gets the widest panel")
print("Axes:",len(fig.axes))
'''),
    "The tall first Axes spans both rows; the right column contains two separate areas. add_gridspec creates a layout description, not four unused Axes. Only three Axes are created.",
    ('fig,axs=plt.subplots(2,2)\nfig.add_subplot(2,1,1)  # overlaps existing panels', 'fig=plt.figure()\ngs=fig.add_gridspec(2,2)\nmain=fig.add_subplot(gs[:,0])', "Create the intended areas once instead of leaving unwanted overlapping Axes."),
    "Create a grid with one full-width top panel and two bottom panels. Print how many Axes exist.",
    chart('fig=plt.figure(layout="constrained")\ngs=fig.add_gridspec(2,2)\na=fig.add_subplot(gs[0,:]); b=fig.add_subplot(gs[1,0]); c=fig.add_subplot(gs[1,1])\nfor ax in [a,b,c]: ax.plot([1,2],[2,3])\nprint(len(fig.axes))'),
    "Use height_ratios=[2,1] for two stacked areas; title the top one Main and print the height ratio from the GridSpec.",
    chart('fig=plt.figure(layout="constrained")\ngs=fig.add_gridspec(2,1,height_ratios=[2,1])\na=fig.add_subplot(gs[0,0]); b=fig.add_subplot(gs[1,0])\na.plot([1,2],[3,4]); b.bar(["A","B"],[2,3]); a.set_title("Main")\nprint(gs.get_height_ratios())'),
    "GridSpec allocates space; add only the Axes your intended layout needs.",
    [("What does gs[:,0] select?", "All rows of the first column", "The first row only", "All data values", "The slice describes layout cells, not measurements."),
     ("Does add_gridspec alone create data plots?", "No; add Axes to its cells", "Yes; four lines", "It reads a CSV", "It describes placement; add_subplot creates each plotting area.")])

lesson(3, "4. Build a four-question report from one dataset",
    "Choose complementary panels while preserving the same data and units.",
    [("Aggregation before drawing", "Matplotlib does not know the business meaning of a row. Use pandas to calculate explicit summaries before passing their coordinates to plotting methods."),
     ("Layout engine", "layout='constrained' manages room for titles, ticks and labels. Do not then call tight_layout to replace that engine; choose one strategy and inspect the rendered result.")],
    "Use the same small table to ask four different questions: how did monthly revenue change, which region contributed, which products contributed and how variable were sale-line amounts? "
    "The line has one point per monthly total. A histogram has one input per sale line. Confusing those grains can turn a histogram of three monthly totals into a supposed distribution of individual purchases. "
    "Calculate the summaries first and reconcile their totals. The chart code should display a known result, not secretly perform inconsistent calculations in each panel. "
    "For real reports, name the coverage window and source assumptions. The illustration below uses four fictional observations and is separate from the eight-line Week30 capstone, which returns on Day6.",
    'monthly=df.groupby("month")["revenue"].sum()\naxs[0,0].plot(monthly.index,monthly.values)',
    chart('''
import pandas as pd
df=pd.DataFrame({"month":[1,1,2,3],"region":["NP","JP","NP","JP"],"product":["Book","Pen","Book","Pen"],"revenue":[100,50,80,120]})
monthly=df.groupby("month")["revenue"].sum()
regions=df.groupby("region")["revenue"].sum(); products=df.groupby("product")["revenue"].sum()
fig,axs=plt.subplots(2,2,figsize=(7,5),layout="constrained")
axs[0,0].plot(monthly.index,monthly.values,marker="o"); axs[0,0].set(title="Monthly total",xlabel="Month",ylabel="Revenue (units)")
axs[0,1].bar(regions.index,regions.values); axs[0,1].set(title="Region total",ylabel="Revenue (units)")
axs[1,0].bar(products.index,products.values); axs[1,0].set(title="Product total",ylabel="Revenue (units)")
axs[1,1].hist(df["revenue"],bins=[0,50,100,150]); axs[1,1].set(title="Sale-line distribution",xlabel="Revenue per line (units)",ylabel="Lines (count)")
fig.suptitle("Four questions; four fictional sale lines")
print("Reconciles:",monthly.sum()==regions.sum()==products.sum()==df["revenue"].sum())
'''),
    "The histogram counts lines, not months. The other three panels aggregate the same source, so their revenue totals agree. This total check catches some preparation errors, but it cannot prove an incomplete input is complete.",
    ('ax.hist(monthly.values)  # label as individual sale lines', 'ax.hist(df["revenue"])  # individual source observations', "Monthly summaries and individual sale lines are different populations."),
    "Create two panels comparing region totals and product totals from rows NP/Book100,JP/Pen50,NP/Pen25; print both totals.",
    chart('import pandas as pd\ndf=pd.DataFrame({"region":["NP","JP","NP"],"product":["Book","Pen","Pen"],"value":[100,50,25]})\nfig,axs=plt.subplots(1,2,layout="constrained")\nfor ax,key in zip(axs,["region","product"]):\n    totals=df.groupby(key)["value"].sum(); ax.bar(totals.index,totals.values); ax.set_title(key)\nprint(int(df.groupby("region")["value"].sum().sum()),int(df.groupby("product")["value"].sum().sum()))'),
    "Draw the histogram of the three individual values100,50,25 and verify its counts sum to3.",
    chart('fig,ax=plt.subplots()\ncounts,_,_=ax.hist([100,50,25],bins=[0,50,100,150])\nax.set(xlabel="Value per row",ylabel="Rows")\nprint("Rows represented:",int(counts.sum()))'),
    "One report may use several grains; label them and reconcile summaries before plotting.",
    [("A histogram of monthly totals describes what?", "The distribution of monthly totals", "Individual purchases automatically", "The number of products", "The observations are the values you supply."),
     ("Should tight_layout follow an active constrained layout?", "No; choose one layout strategy", "Always", "Only after adding colours", "Changing layout engines can undo the intended spacing.")])

lesson(4, "1. Local style contexts and reusable house rules",
    "Apply a consistent appearance without leaking global settings into later charts.",
    [("rcParams; rc_context", "rcParams stores Matplotlib defaults. matplotlib.rc_context temporarily applies a settings dictionary and restores previous defaults when its with block ends."),
     ("Style sheets; plt.style.context", "A style sheet is a named or local collection of defaults. plt.style.context applies one temporarily. Available built-in style names can be inspected with plt.style.available; a project's style should not silently depend on a missing name.")],
    "A house style should reduce repeated decisions: sensible font sizes, line widths, clean backgrounds and restrained grids. "
    "Avoid changing global defaults at import time inside a reusable module. A notebook or larger application may create unrelated charts afterward and inherit those changes accidentally. "
    "A with context groups a temporary choice around the figure creation that needs it. Keep semantic choices, such as units and scales, in the actual chart code; a theme cannot decide what a measurement means. "
    "Save inside the context when you want export settings to follow it too. Defaults affect newly created artists; changing them later does not rewrite every existing object.",
    'with matplotlib.rc_context({"font.size":11,"lines.linewidth":2}):\n    fig,ax=plt.subplots()',
    '''import matplotlib
import matplotlib.pyplot as plt
before=matplotlib.rcParams["lines.linewidth"]
with matplotlib.rc_context({"font.size":11,"lines.linewidth":2.5,"axes.spines.top":False,"axes.spines.right":False}):
    fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
    line,=ax.plot([1,2,3],[3,2,5],marker="o")
    ax.set(xlabel="Month",ylabel="Quantity",title="Scoped house style")
    fig.savefig("chart.png",dpi=110)
    print("Styled line width:",line.get_linewidth())
    plt.close(fig)
print("Default restored:",matplotlib.rcParams["lines.linewidth"]==before)
''',
    "The saved line uses width2.5. After leaving the with block, new charts regain the previous default. axes.spines.top/right control two border lines; removing them is an appearance choice, not a data transformation.",
    ('matplotlib.rcParams["font.size"]=30  # inside an imported helper', 'with matplotlib.rc_context({"font.size":11}):\n    fig,ax=plt.subplots()', "A local context avoids surprising later figures with leaked defaults."),
    "Use rc_context to give one line width3, print its width, and prove the previous default returns.",
    '''import matplotlib
import matplotlib.pyplot as plt
before=matplotlib.rcParams["lines.linewidth"]
with matplotlib.rc_context({"lines.linewidth":3}):
    fig,ax=plt.subplots(); line,=ax.plot([1,2],[2,4])
    print(line.get_linewidth()); fig.savefig("chart.png"); plt.close(fig)
print(matplotlib.rcParams["lines.linewidth"]==before)
''',
    "Create a temporary font-size12 style with no top spine. Print that spine's visibility from the created Axes.",
    '''import matplotlib
import matplotlib.pyplot as plt
with matplotlib.rc_context({"font.size":12,"axes.spines.top":False}):
    fig,ax=plt.subplots(); ax.bar(["A","B"],[2,3])
    print("Top border visible:",ax.spines["top"].get_visible())
    fig.savefig("chart.png"); plt.close(fig)
''',
    "Scope appearance defaults around figure creation and export; keep the measurement choices explicit.",
    [("What happens after rc_context ends?", "Previous defaults are restored", "All files are deleted", "Existing data is rescaled", "The context restores settings after its block."),
     ("Can a style choose the correct revenue denominator?", "No", "Always", "Only a dark style", "Meaning belongs to the data and chart contract.")])

lesson(4, "2. Colours that preserve meaning and accessibility",
    "Use colour with redundant markers or labels and choose a meaningful palette.",
    [("Categorical, sequential, diverging palettes", "Categorical colours distinguish names; sequential maps show ordered magnitude; diverging maps emphasise values around a meaningful centre. A palette's structure should match its variable."),
     ("Redundant encoding", "Distinguish series by more than colour: line dashes, marker shapes, direct labels or bar hatches can keep them recognisable in grayscale or for readers with colour-vision differences.")],
    "Colour should tell the same story throughout a report. If NP is blue in one panel and orange in another, readers have to relearn the mapping or may misread it. "
    "Do not rely on a red-versus-green difference alone. Pair distinct colours with a solid circle-marked line versus a dashed square-marked line and clear names. "
    "A perceptually ordered map such as viridis is a useful starting point for increasing magnitudes; rainbow changes can create apparent boundaries unrelated to the data. "
    "No palette is automatically accessible in every context. Check contrast at final size, try grayscale and keep text or shape cues. Avoid decorative colour that adds a second legend without answering another question.",
    'ax.plot(x,a,color="#0072B2",marker="o",linestyle="-",label="NP")\nax.plot(x,b,color="#D55E00",marker="s",linestyle="--",label="JP")',
    chart('''
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
ax.plot([1,2,3],[2,4,3],color="#0072B2",marker="o",linestyle="-",label="NP")
ax.plot([1,2,3],[3,2,5],color="#D55E00",marker="s",linestyle="--",label="JP")
ax.set(xlabel="Month",ylabel="Recorded tasks",title="Colour plus markers and line style")
ax.legend()
print("Markers:",[line.get_marker() for line in ax.lines])
print("Line styles:",[line.get_linestyle() for line in ax.lines])
'''),
    "Both colour and shape identify each region. If the image is printed in grayscale, a circle/solid series and a square/dashed series still differ. This aids recognition but does not eliminate the need for legible labels.",
    ('ax.plot(x,a,color="red"); ax.plot(x,b,color="green")  # colour alone', 'ax.plot(x,a,marker="o",label="A"); ax.plot(x,b,marker="s",linestyle="--",label="B")', "Use a second identification channel and visible labels."),
    "Draw two category bars with different hatches and print the hatch patterns. Keep category names on the axis.",
    chart('fig,ax=plt.subplots()\nbars=ax.bar(["A","B"],[4,6],color=["#0072B2","#D55E00"])\nbars[0].set_hatch("//"); bars[1].set_hatch("xx")\nax.set_ylabel("Tasks")\nprint([bar.get_hatch() for bar in bars])'),
    "Use a line with square markers and a dashed pattern, then print those two properties.",
    chart('fig,ax=plt.subplots()\nline,=ax.plot([1,2,3],[2,4,3],marker="s",linestyle="--",label="Observed")\nax.legend()\nprint(line.get_marker(),line.get_linestyle())'),
    "Colour has a data role; reinforce category identity with labels and a non-colour cue.",
    [("What suits an increasing numeric magnitude?", "A sequential colour map", "An arbitrary category shuffle", "A separate rainbow for each point", "An ordered palette should correspond to an ordered variable."),
     ("What helps when colour differences are hard to see?", "Markers, dashes and clear labels", "Remove all labels", "Use red and green alone", "Redundant cues preserve series identity.")])

lesson(4, "3. Colour maps, normalisation and a real colourbar",
    "Keep numeric colour scales comparable and attach a colourbar to its plotted data.",
    [("c; cmap; vmin/vmax", "scatter's c can be one numeric value per point; cmap maps those values to colours. vmin and vmax set its numeric range. Repeated panels need a shared range if their colours are to be compared."),
     ("ScalarMappable; colorbar", "A numeric-colour plot carries the value-to-colour mapping. fig.colorbar(points,ax=ax) builds a matching scale from that plotted collection. A colourbar explains numeric colour; a legend explains named series.")],
    "A third variable can sometimes be encoded by colour. In this example, x is session duration, y is score and colour is the session's practice count. "
    "That extra variable is useful only if readers can decode it. Provide a labelled colourbar derived from the actual scatter object. "
    "Automatic colour ranges are local: value5 can look bright in a0–5 panel and dark in a0–100 panel. Set a shared range when comparing panels. "
    "Clipping colours at a limit hides distinctions beyond the range; either display the full range or explicitly disclose clipped values. If colour is the only way to recover an important number, provide a table or direct labels too.",
    'points=ax.scatter(x,y,c=counts,cmap="viridis",vmin=0,vmax=10)\nfig.colorbar(points,ax=ax,label="Practice count")',
    chart('''
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
points=ax.scatter([10,20,30,40],[50,60,75,80],c=[2,4,6,8],cmap="viridis",vmin=0,vmax=10,s=70)
fig.colorbar(points,ax=ax,label="Practice tasks (count)")
ax.set(xlabel="Study minutes",ylabel="Score",title="One numeric mapping, labelled colourbar")
print("Colour range:",points.get_clim())
print("Point counts:",points.get_array().astype(int).tolist())
'''),
    "get_clim reads the colour mapping limits, not the x/y viewing limits. The colourbar belongs to the points collection, so it shares the same numeric conversion. Four values2,4,6,8 lie within the declared0–10 range.",
    ('ax.scatter(x,y,c=counts)  # numeric colours, no decoding key', 'points=ax.scatter(x,y,c=counts,cmap="viridis"); fig.colorbar(points,ax=ax,label="Count")', "Readers need the colour quantity and scale, not just attractive points."),
    "Colour three points by counts1,5,9 using a0–10 range and print the limits.",
    chart('fig,ax=plt.subplots()\np=ax.scatter([1,2,3],[2,4,3],c=[1,5,9],cmap="viridis",vmin=0,vmax=10)\nfig.colorbar(p,ax=ax,label="Count")\nprint(p.get_clim())'),
    "Make two scatter panels with values[1,2] and[8,9], use the same0–10 colour range, and print whether their limits agree.",
    chart('fig,axs=plt.subplots(1,2,layout="constrained")\nplots=[]\nfor ax,values in zip(axs,[[1,2],[8,9]]):\n    p=ax.scatter([1,2],[2,3],c=values,cmap="viridis",vmin=0,vmax=10); plots.append(p)\nfig.colorbar(plots[0],ax=axs,label="Comparable count")\nprint(plots[0].get_clim()==plots[1].get_clim())'),
    "Match numeric colour to a labelled colourbar and preserve the same mapping across comparisons.",
    [("What should generate a numeric scatter colourbar?", "The plotted collection with its mapping", "An unrelated legend", "The CSV filename", "Use the same scalar-to-colour conversion as the marks."),
     ("Why share vmin/vmax across comparison panels?", "The same number should have the same colour", "To change the sample size", "To sort x values", "Otherwise independent automatic ranges can conceal differences.")])

lesson(4, "4. Reusable chart functions that return control",
    "Separate data preparation, drawing and export so a report can reuse each part.",
    [("Axes-in drawing helper", "A function can receive an existing Axes, draw on it and return artists for later editing. It should not secretly create another window or close the caller's figure."),
     ("Chart contract versus implementation", "Validate lengths, keys and units before drawing. A function returning artists gives the caller control over legends, annotation and export; it does not establish source completeness.")],
    "Week1 did not require functions before you learned def; now those foundations let you build reusable plotting code safely. "
    "A drawing helper receives the area to use. This lets the same helper work in a single chart or a panel of a larger report. "
    "Keep preparation outside when possible: the helper should draw a known monthly summary, not silently fill missing months, convert currencies or change the grain. "
    "Check paired lengths and reject an empty series before creating misleading output. Return the line so the caller can inspect or annotate it. Creation and closing belong to the code that owns the Figure, which makes later testing and composition easier.",
    'def draw_series(ax,x,y,label):\n    line,=ax.plot(x,y,label=label)\n    return line',
    chart('''
def draw_series(ax,x,y,label):
    if not x or len(x)!=len(y):
        raise ValueError("Need nonempty paired observations")
    line,=ax.plot(x,y,marker="o",label=label)
    return line
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
line=draw_series(ax,[1,2,3],[300,250,550],"Recorded")
ax.set(xlabel="Month",ylabel="Revenue (units)",title="Drawing helper targets its caller's Axes"); ax.legend()
print("Points:",len(line.get_xdata()))
try:
    draw_series(ax,[1,2],[100],"Broken")
except ValueError:
    print("Unpaired values refused")
'''),
    "The helper adds no extra Figure and does not close ax. The caller labels units, saves and closes. The validation uses ordinary Python lists; for NumPy arrays use len(x)==0 rather than truth-testing a multi-element array.",
    ('def draw(ax,x,y):\n    plt.figure(); plt.plot(x,y)', 'def draw(ax,x,y):\n    return ax.plot(x,y)', "A helper that ignores its supplied Axes breaks composition and figure ownership."),
    "Write a helper accepting ax, category names and values, rejecting unequal lengths and returning bars. Print the number of bars.",
    chart('def draw_bars(ax,names,values):\n    if len(names)!=len(values): raise ValueError("Unpaired categories")\n    return ax.bar(names,values)\nfig,ax=plt.subplots()\nbars=draw_bars(ax,["A","B"],[3,5])\nprint(len(bars))'),
    "Call a list-based line helper with empty inputs; catch ValueError. Then draw valid values to the same Axes.",
    chart('def draw(ax,x,y):\n    if len(x)==0 or len(x)!=len(y): raise ValueError("Need paired values")\n    return ax.plot(x,y)\nfig,ax=plt.subplots()\ntry:\n    draw(ax,[],[])\nexcept ValueError:\n    print("Empty input refused")\ndraw(ax,[1,2],[3,4])\nprint("Lines:",len(ax.lines))'),
    "Pass the destination explicitly, reject invalid inputs and let the Figure owner handle saving and closing.",
    [("Who should close a Figure passed to a drawing helper?", "The caller that owns its lifecycle", "The helper unconditionally", "Every line artist", "Closing inside a helper prevents further composition."),
     ("Does checking paired lengths prove complete source coverage?", "No", "Always", "Only for monthly data", "Structural validity and source completeness are separate checks.")])

lesson(5, "1. Inches, pixels and DPI: choose the final reading size",
    "Calculate raster dimensions and keep text readable at its intended placement.",
    [("DPI; raster image", "DPI is dots per inch. For an uncropped PNG, pixel width equals figure width in inches times export DPI. A6-inch figure exported at150DPI is900pixels wide. Raster pictures use a fixed grid of pixels."),
     ("Figure size; export size", "figsize determines the physical canvas. savefig(dpi=...) chooses raster resolution. Increasing DPI gives more pixels, but does not make tiny labels large when the image is placed at the same physical size.")],
    "Publication quality starts with where the chart will be read. A document column, a phone screen and a large slide need different physical sizes and text choices. "
    "A six-inch-wide figure at150DPI has900pixels across. At300DPI it has1800. Both still describe the same six-inch layout; the higher resolution does not fix overlapping labels or an unreadable five-point font. "
    "Design at the intended placement size, then choose enough raster resolution for the destination. A cropped bounding box changes the output extent, so the simple inch-times-DPI formula refers to the uncropped canvas. "
    "Inspect an actual export rather than assuming that a large file means a good chart.",
    'fig,ax=plt.subplots(figsize=(6,3))\nfig.savefig("chart.png",dpi=150)',
    '''import matplotlib.pyplot as plt
from PIL import Image
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
ax.plot([1,2,3],[300,250,550],marker="o")
ax.set(xlabel="Month",ylabel="Revenue (units)",title="6 by 3 inches, exported at150 DPI")
fig.savefig("chart.png",dpi=150)
with Image.open("chart.png") as image:
    print("PNG pixels:",image.size)
plt.close(fig)
''',
    "Pillow's Image.open inspects the saved file; with closes the file afterward. Pillow is installed as a Matplotlib dependency in this environment. The actual900-by450 pixel output verifies the size calculation rather than trusting the filename.",
    ('fig.savefig("tiny.png",dpi=1200)  # expect tiny labels to become readable', 'fig.set_size_inches(6,3)\nax.tick_params(labelsize=11)\nfig.savefig("readable.png",dpi=150)', "Readability depends on layout and text size at final placement, not DPI alone."),
    "Export a4-by2-inch figure at100DPI and inspect its actual pixel size.",
    '''import matplotlib.pyplot as plt
from PIL import Image
fig,ax=plt.subplots(figsize=(4,2)); ax.plot([1,2],[2,3])
fig.savefig("chart.png",dpi=100)
with Image.open("chart.png") as im: print(im.size)
plt.close(fig)
''',
    "Export the same4-by2-inch layout at200DPI, print its dimensions and state whether the observations changed.",
    '''import matplotlib.pyplot as plt
from PIL import Image
fig,ax=plt.subplots(figsize=(4,2)); ax.plot([1,2],[2,3])
fig.savefig("chart.png",dpi=200)
with Image.open("chart.png") as im: print(im.size)
print("Data unchanged:",[2,3])
plt.close(fig)
''',
    "Choose a readable physical layout first; verify raster dimensions and use DPI for resolution rather than as a layout repair.",
    [("How wide is an uncropped6-inch figure at150DPI?", "900 pixels", "150 pixels", "6 pixels", "Multiply physical inches by pixels per inch."),
     ("Does extra DPI alone fix tiny labels at the same printed size?", "No", "Always", "Only for PDFs", "Text and layout must be designed at the final physical size.")])

lesson(5, "2. PNG, SVG and PDF: save the right artifact",
    "Export raster and vector formats and inspect background and cropping choices.",
    [("Vector formats; SVG; PDF", "SVG and PDF can store lines and text as geometric instructions that scale smoothly. Embedded images and deliberately rasterized artists remain raster. PNG stores pixels and is convenient for web images."),
     ("bbox_inches; facecolor; transparent", "bbox_inches='tight' crops around visible content, changing image extent. facecolor controls the saved background; transparent=True requests transparency. Inspect each choice in the destination document.")],
    "Use PNG when you need a broadly supported image with predictable pixels. Use SVG for scalable web or editing workflows, and PDF for many document and print workflows. "
    "A vector extension does not guarantee small files or editable text: font settings and image artists affect the result. For this small course report, default Matplotlib fonts avoid dependencies on optional fonts installed only on your computer. "
    "Save the same Figure several times so its data, limits and labels stay consistent across formats. A white export background is a deliberate stable choice when the receiving page may have either dark or light styling. "
    "A transparent background may look attractive until black labels land on a dark slide. Check the final placement instead of assuming transparency is always better.",
    'fig.savefig("chart.png",dpi=200,facecolor="white")\nfig.savefig("chart.svg",facecolor="white")\nfig.savefig("chart.pdf",facecolor="white")',
    '''from pathlib import Path
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
ax.bar(["Book","Pen"],[700,400],color=["#0072B2","#D55E00"])
ax.set(ylabel="Revenue (fictional units)",title="One figure, three export formats")
for ext in ["png","svg","pdf"]:
    target=Path("chart."+ext)
    fig.savefig(target,dpi=150,facecolor="white")
    print(ext,"created:",target.is_file() and target.stat().st_size>0)
plt.close(fig)
''',
    "Path.stat().st_size checks that an artifact contains bytes, but cannot establish that labels are readable. Inspect the three files visually. The filename extension chooses the output format here.",
    ('fig.savefig("chart.jpg",format="svg")', 'fig.savefig("chart.svg")', "If format and extension disagree, readers and other software may treat the file incorrectly."),
    "Save one line figure as PNG and SVG with white backgrounds. Print which files were created.",
    '''from pathlib import Path
import matplotlib.pyplot as plt
fig,ax=plt.subplots(); ax.plot([1,2],[2,4])
for ext in ["png","svg"]:
    fig.savefig("chart."+ext,facecolor="white")
    print(ext,Path("chart."+ext).exists())
plt.close(fig)
''',
    "Save a tightly cropped PDF and an ordinary PNG from the same Figure, then print the PDF file signature.",
    '''from pathlib import Path
import matplotlib.pyplot as plt
fig,ax=plt.subplots(); ax.bar(["A","B"],[2,3]); ax.set_ylabel("Count")
fig.savefig("chart.pdf",bbox_inches="tight",facecolor="white")
fig.savefig("chart.png",facecolor="white")
print(Path("chart.pdf").read_bytes()[:4].decode("ascii"))
plt.close(fig)
''',
    "Keep extension and format consistent; inspect exports in their intended destination, especially cropped or transparent versions.",
    [("Which is a raster format?", "PNG", "SVG for ordinary vector lines", "PDF for ordinary vector lines", "PNG stores a fixed pixel grid."),
     ("Can bbox_inches='tight' change output pixel dimensions?", "Yes", "Never", "Only on scatter plots", "Cropping changes the saved extent.")])

lesson(5, "3. Figure lifecycle, repeated exports and an export checklist",
    "Avoid blank images, stale current figures and accumulating open windows.",
    [("Backend; Agg", "A backend renders a Figure to a window or file. Agg is a noninteractive raster renderer useful for automated file generation. Choose matplotlib.use('Agg') before importing pyplot in a file-only script."),
     ("Explicit close; get_fignums", "plt.close(fig) releases pyplot's reference to that Figure. get_fignums lists currently registered figures; closing each completed report prevents accidental accumulation in loops.")],
    "When a script makes many reports, leaving every Figure open wastes memory and can trigger a warning. Save the named figure, then close it when no further edits are needed. "
    "A blocking desktop show may unregister a figure after its window closes. Saving through pyplot afterward can therefore capture a new empty current figure. Save before show, or retain and use the exact Figure reference appropriately. "
    "For automated exports, use a file backend and skip window display altogether. This does not execute Python inside StudyHub: it is local Python drawing to files. "
    "Before release, inspect the data totals, chart choice, units, zero or log policy, legends, annotations, clipping, physical text size and output filenames. Do this at actual reading size, not only zoomed in.",
    'fig.savefig("report.png")\nplt.close(fig)\n# File-only script: select Agg before importing pyplot.',
    '''import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
for name,values in [("first",[2,3]),("second",[4,2])]:
    fig,ax=plt.subplots(figsize=(6,3),layout="constrained")
    ax.plot([1,2],values,marker="o"); ax.set(title=name,xlabel="Day",ylabel="Tasks")
    fig.savefig(name+".png")
    if name=="second": fig.savefig("chart.png")
    plt.close(fig)
print("Open figures:",len(plt.get_fignums()))
''',
    "The loop owns each Figure and releases it after saving. Different filenames keep the first result available. Saving both through fig rather than relying on the current pyplot target avoids state confusion.",
    ('plt.show()\nplt.savefig("report.png")  # after closing a blocking GUI window', 'fig.savefig("report.png")\nplt.show()\nplt.close(fig)', "Save the intended figure before a blocking display ends its managed lifecycle."),
    "Make and close three small charts named report1.png through report3.png; save the final one as chart.png too and print the open-figure count.",
    '''import matplotlib.pyplot as plt
for i in range(1,4):
    fig,ax=plt.subplots(); ax.plot([1,2],[i,i+1])
    fig.savefig(f"report{i}.png")
    if i==3: fig.savefig("chart.png")
    plt.close(fig)
print("Open:",len(plt.get_fignums()))
''',
    "Keep a Figure reference while another Figure becomes current; save the first explicitly, close both and print the count.",
    '''import matplotlib.pyplot as plt
first,a=plt.subplots(); a.plot([1,2],[4,6]); a.set_title("Intended export")
second,b=plt.subplots(); b.plot([1,2],[0,1])
first.savefig("chart.png")
plt.close(first); plt.close(second)
print("Open:",len(plt.get_fignums()))
''',
    "Own the lifecycle: create, draw, label, inspect, save the named Figure, then close it.",
    [("What is Agg useful for?", "File generation without an interactive window", "Hosting user passwords", "Downloading live stock prices", "It is a noninteractive rendering backend."),
     ("Why close completed figures in a loop?", "Avoid retaining unnecessary figures", "Change the data values", "Improve source completeness", "Closing releases pyplot's managed figure references.")])

# The same drawing function is embedded in the capstone and supplied as a local
# project. Preparation is reused from Week30 rather than silently reimplemented.
DRAW_REPORT = '''
def draw_report(sales, monthly):
    import matplotlib.dates as mdates
    fig,axs=plt.subplots(2,2,figsize=(10,7),layout="constrained")
    trend=monthly["revenue_minor"]/100
    regions=sales.groupby("region")["revenue_minor"].sum().sort_index()/100
    products=sales.groupby("product")["revenue_minor"].sum().sort_values(ascending=False)/100
    line_values=sales["revenue_minor"]/100
    axs[0,0].plot(trend.index,trend.values,marker="o",color="#0072B2")
    axs[0,0].set_xticks(trend.index)
    axs[0,0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    axs[0,0].tick_params(axis="x",labelrotation=20)
    axs[0,0].set(title="A. Monthly recorded revenue",ylabel="Revenue (fictional units)")
    axs[0,0].set_ylim(bottom=0)
    maximum=trend.idxmax()
    axs[0,0].annotate("First peak",xy=(maximum,trend.loc[maximum]),xytext=(-45,-20),
        textcoords="offset points",arrowprops={"arrowstyle":"->"})
    axs[0,1].bar(regions.index,regions.values,color="#0072B2")
    axs[0,1].set(title="B. Revenue by region",ylabel="Revenue (fictional units)")
    axs[1,0].barh(products.index,products.values,color="#D55E00")
    axs[1,0].invert_yaxis()
    axs[1,0].set(title="C. Revenue by product",xlabel="Revenue (fictional units)")
    bin_width=max(100,(int(line_values.max())//2000+1)*100)
    upper=(int(line_values.max())//bin_width+1)*bin_width
    edges=list(range(0,upper+1,bin_width))
    counts,_,_=axs[1,1].hist(line_values,bins=edges,color="#0072B2",edgecolor="white")
    axs[1,1].set(title="D. Individual sale-line distribution",xlabel="Revenue per line (fictional units)",ylabel="Sale lines (count)")
    for ax in axs.flat:
        ax.grid(axis="y",alpha=0.2); ax.set_axisbelow(True)
    fig.suptitle("Fictional sales: "+str(len(sales))+" lines; complete-month source contract")
    if int(counts.sum())!=len(sales):
        plt.close(fig)
        raise ValueError("Histogram excluded a sale line")
    return fig
'''

CAPSTONE_DATA = '''
import pandas as pd
sales=pd.DataFrame({
    "date":pd.to_datetime(["2025-01-02","2025-01-15","2025-02-02","2025-02-16","2025-03-03","2025-03-10","2025-03-20","2025-03-29"]),
    "region":["NP","JP","NP","NP","NP","JP","NP","JP"],
    "product":["Book","Pen","Book","Pen","Pen","Book","Book","Pen"],
    "revenue_minor":[20000,10000,10000,15000,5000,30000,10000,10000]})
monthly=sales.set_index("date")["revenue_minor"].resample("MS").sum().to_frame()
'''

lesson(5, "4. Sales visual report: prepare, draw, export and interpret",
    "Explain and export a four-panel report grounded in the exact Week30 fictional inputs.",
    [("draw_report; return fig", "This is our own reusable function, not a Matplotlib builtin. It takes already prepared sales and monthly summaries, creates four labelled panels and returns the Figure so the caller can export it."),
     ("idxmax; invert_yaxis; to_frame", "idxmax returns the label of the first maximum; here it is a timestamp. invert_yaxis puts the first horizontal-bar category at the top. Series.to_frame converts a one-column Series into a DataFrame."),
     ("Project reuse; source contract", "The supplied visual_report.py imports the existing Week30 preparation module from its neighbouring folder. It reuses strict raw-input checks and the same complete-feed declaration; the chart itself cannot prove that declaration.")],
    "Finish with the exact eight fictional sale-line amounts from Week30. Their monthly totals are300,250,550 whole fictional currency units, adding to1100. "
    "Region totals are NP600 and JP500; product totals are Book700 and Pen400. Those are revenue comparisons, not profit, causes or forecasts. "
    "The histogram describes eight sale-line amounts, not three monthly totals. Its100-unit edges produce counts1,5,1,1, with the final interval including its right edge. "
    "The inline example supplies the prepared fictional data directly so it is self-contained. The standalone project instead reads the original three Week30 CSVs, reuses their validated preparation, and publishes a new directory with PNG, SVG, PDF, exact plot-data CSVs and interpretation.txt. "
    "Keep the two neighbouring project folders when downloading. Choose a new output directory for every run; the project refuses to overwrite an existing bundle. Study the function in stages: summaries, layout, trend, category panels, distribution, then export. "
    "Day7's existing Review & rest collects this week's exercises; do not mark this part complete until you can explain every panel and reproduce a changed version.",
    'fig=draw_report(sales,monthly)\nfig.savefig("report.png",dpi=300,facecolor="white")\nplt.close(fig)',
    'import matplotlib.pyplot as plt\n'+clean(DRAW_REPORT)+clean(CAPSTONE_DATA)+'''
fig=draw_report(sales,monthly)
fig.savefig("chart.png",dpi=110,facecolor="white")
plt.close(fig)
print("Monthly units:",(monthly["revenue_minor"]/100).tolist())
print("Total units:",int(sales["revenue_minor"].sum()/100))
print("Revenue is not profit; cause and future sales are not established")
''',
    "Read A for the calendar trend, B for regional totals, C for product totals and D for individual-line spread. The first peak label targets March's timestamp. Histogram bin counts reconcile to eight input lines. The report keeps all units visible and uses the same values across export formats.",
    ('ax.plot(["Mar","Jan","Feb"],[550,300,250]); ax.set_title("Campaign proved profit")', 'ax.plot(sorted_dates,paired_revenue); ax.set_title("Recorded revenue by complete month")', "Keep calendar pairing and supported claims. Nothing here measures profit or isolates a campaign effect."),
    "Change the last fictional sale-line amount from10000 to20000 minor units. Recompute monthly data before drawing; print the changed March and overall totals.",
    'import matplotlib.pyplot as plt\n'+clean(DRAW_REPORT)+clean(CAPSTONE_DATA)+'''
sales.loc[7,"revenue_minor"]=20000
monthly=sales.set_index("date")["revenue_minor"].resample("MS").sum().to_frame()
fig=draw_report(sales,monthly)
fig.savefig("chart.png"); plt.close(fig)
print("March units:",int(monthly.iloc[-1]["revenue_minor"]/100))
print("Total units:",int(sales["revenue_minor"].sum()/100))
''',
    "Filter to NP sale lines, recompute the monthly summary, draw the report, and print monthly values and represented lines. Explain that this changes the population.",
    'import matplotlib.pyplot as plt\n'+clean(DRAW_REPORT)+clean(CAPSTONE_DATA)+'''
sales=sales.loc[sales["region"].eq("NP")].copy()
monthly=sales.set_index("date")["revenue_minor"].resample("MS").sum().to_frame()
fig=draw_report(sales,monthly)
fig.savefig("chart.png"); plt.close(fig)
print("NP monthly units:",(monthly["revenue_minor"]/100).tolist())
print("NP sale lines:",len(sales))
''',
    "Week31 mastery: clear chart questions, explicit Figure/Axes ownership, paired data, meaningful scales, readable panels, accessible cues and inspected exports.",
    [("Which sample month has the most recorded revenue?", "March:550 fictional units", "February:550 units", "January:700 units", "The exact Week30 sample totals are300,250,550."),
     ("How many observations feed the capstone histogram?", "Eight sale lines", "Three monthly totals", "Two regions", "Its grain is one recorded sale line."),
     ("Which object owns all four panels?", "The Figure", "The first x tick", "The CSV file", "Each panel is an Axes within one Figure."),
     ("What must stay together when sorting?", "Each x value and its corresponding y value", "Only category colours", "The filenames", "Sorting coordinates independently invents pairs."),
     ("Does a flier establish an invalid record?", "No", "Always", "Only in SVG", "Investigate the source before applying cleaning rules."),
     ("Which scale fits ordinary positive category bars?", "A visible zero baseline", "A hidden narrow cutoff", "An unlabeled log scale", "Bar lengths encode magnitudes from their baseline."),
     ("What does a numeric colourbar explain?", "The mapping from numeric values to colours", "Causal certainty", "The source filename", "It should share the plotted collection's mapping."),
     ("What does sharey support for same-unit panels?", "Fair absolute-scale comparison", "Automatic source cleaning", "Profit calculation", "Equal values retain comparable visual positions."),
     ("What is the ordinary lifecycle for file reports?", "Create, draw, save the named Figure, close", "Show a closed window then blindly save current", "Open figures forever", "Explicit ownership avoids stale current state and accumulation."),
     ("Does300DPI repair an unreadable layout?", "No; design readable text at final size", "Always", "Only for PNG", "Resolution and physical reading size are distinct."),
     ("Can this report prove a sales campaign caused growth?", "No; it is descriptive fictional evidence", "Yes, a rising line proves it", "Only if coloured red", "No causal comparison or campaign experiment was provided."),
     ("Where should a second project run be published?", "A new output bundle directory", "Over the source CSVs", "Silently over the first run", "The project preserves earlier artifacts and inputs.")])

PROJECT = '''"""Week31: local four-panel visual report from the Week30 source contract."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def preparation_module():
    source=Path(__file__).resolve().parents[1]/"python-week30"/"sales_report.py"
    spec=importlib.util.spec_from_file_location("week30_sales",source)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
''' + clean(DRAW_REPORT) + '''
def publish(reports,summary,destination):
    destination=Path(destination)
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError("Choose a new bundle name under an existing parent")
    sales=reports["enriched"]
    monthly=reports["monthly"]
    total=int(sales["revenue_minor"].sum())
    if total!=int(monthly["revenue_minor"].sum()):
        raise ValueError("Monthly totals do not reconcile")
    regions=sales.groupby("region")["revenue_minor"].sum()
    products=sales.groupby("product")["revenue_minor"].sum()
    month_units=", ".join(f"{x/100:.2f}" for x in monthly["revenue_minor"])
    interpretation=(
        "FICTIONAL LEARNING REPORT — not real business performance\\n"
        +"Window: "+summary["start_inclusive"]+" inclusive to "+summary["end_exclusive"]+" exclusive.\\n"
        +"Coverage: "+summary["coverage_policy"]+". This is a caller assertion, not proof of completeness.\\n"
        +"Currency: one fictional currency,100 minor units per displayed unit. Positive sales only.\\n"
        +f"Represented sale lines: {len(sales)}. Revenue: {total/100:.2f} fictional units.\\n"
        +"A. Monthly totals in calendar order: "+month_units+" fictional units.\\n"
        +"B. Region totals: "+json.dumps({str(k):int(v) for k,v in regions.items()})+" minor units.\\n"
        +"C. Product totals: "+json.dumps({str(k):int(v) for k,v in products.items()})+" minor units.\\n"
        +"D. Histogram uses individual sale-line amounts with bins of100 units or coarser for larger values (at most20 intervals); it does not use monthly totals.\\n"
        +"Limitations: costs, profit, causal explanations and future performance are not established.\\n"
        +"The selected source window may not describe other periods. No inferential claim is made.\\n")
    with TemporaryDirectory(prefix="studyhub-visual-",dir=destination.parent) as temp:
        folder=Path(temp)
        with matplotlib.rc_context({"font.size":10,"axes.spines.top":False,"axes.spines.right":False}):
            fig=draw_report(sales,monthly)
            try:
                for ext in ["png","svg","pdf"]:
                    fig.savefig(folder/("report."+ext),dpi=300,facecolor="white")
            finally:
                plt.close(fig)
        monthly[["revenue_minor"]].to_csv(folder/"monthly_plot.csv",date_format="%Y-%m-%d",lineterminator="\\n")
        regions.to_csv(folder/"region_plot.csv",lineterminator="\\n")
        products.to_csv(folder/"product_plot.csv",lineterminator="\\n")
        sales[["line_id","revenue_minor"]].to_csv(folder/"sale_line_plot.csv",index=False,lineterminator="\\n")
        (folder/"interpretation.txt").write_text(interpretation,encoding="utf-8")
        os.rename(folder,destination)
    return total

def main(argv=None):
    parser=argparse.ArgumentParser(description="Week31 fictional sales visual report")
    parser.add_argument("lines"); parser.add_argument("products"); parser.add_argument("customers")
    parser.add_argument("destination"); parser.add_argument("--start",required=True); parser.add_argument("--end",required=True)
    parser.add_argument("--complete-feed",action="store_true",required=True,help="Declare complete source coverage for the full window")
    args=parser.parse_args(argv)
    try:
        module=preparation_module()
        lines=module.load_table(args.lines,["line_id","date","product_id","customer_id","units","unit_price_minor"])
        products=module.load_table(args.products,["product_id","product"])
        customers=module.load_table(args.customers,["customer_id","region"])
        reports,summary=module.build_reports(lines,products,customers,args.start,args.end)
        total=publish(reports,summary,args.destination)
    except (ValueError,OSError) as error:
        parser.exit(1,"Visual report stopped: "+str(error)+"\\n")
    print("Published8 files; revenue minor units",total)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
'''

FIGURE_BRANCH = '''    if(s.t==="figure" && /^data:image\\/png;base64,[A-Za-z0-9+/=]+$/.test(s.src||"")) return `<figure style="margin:18px 0"><img src="${escapeAttr(s.src)}" alt="${escapeAttr(s.alt||"Lesson chart")}" style="display:block;width:100%;height:auto;border-radius:12px;background:#fff"><figcaption class="ls-p">${escapeHtml(s.note||"")}</figcaption></figure>`;
'''


def write():
    target=ROOT/"study-hub.html"
    original=target.read_bytes().decode("utf-8")
    start=original.index("const DAY_TEACH = {")
    end=original.index("\n};\n\nconst REST_DAY",start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS):
        raise RuntimeError("Week31 already exists; refusing to overwrite")
    for future,target_section,picture in JOBS:
        text,png=future.result()
        target_section["v" if target_section["t"]=="out" else "out"]=text
        if picture is not None:
            if not png: raise RuntimeError("Example did not produce chart.png")
            picture["src"]="data:image/png;base64,"+base64.b64encode(png).decode("ascii")
    POOL.shutdown()
    DAYS["31.0"]["parts"][2]["sections"].insert(3,section("new","legend; label; set properties",note="A plot's label names a series; ax.legend displays that name in a key. ax.set accepts named Axes properties such as xticks. Day3 develops legends, units and exact tick labels in detail."))
    DAYS["31.5"]["parts"][0]["sections"].insert(3,section("new","Pillow; Image.open",note="Pillow is the image library installed alongside Matplotlib. from PIL import Image imports its image interface. Image.open reads an exported picture; image.size reports pixel width and height. A with block closes the file after inspection."))
    DAYS["31.0"]["parts"][0]["sections"].insert(3,section("sh",'python -m pip install "matplotlib>=3.10,<3.11" "pandas>=3,<4"',note="Install once in your existing practice environment. Initial installation needs internet; local examples and all embedded chart pictures work offline afterward. Verified with Matplotlib3.10.9 and pandas3.0.1. These are local Python scripts, not code executed inside this website."))
    DAYS["31.5"]["parts"][3]["sections"].append(section("sh",'python visual_report.py ../python-week30/sale_lines.csv ../python-week30/products.csv ../python-week30/customers.csv visual-run-01 --start 2025-01-01 --end 2025-04-01 --complete-feed\npython visual_report.py --help',note="From docs/python-week31; keep the neighbouring python-week30 folder. Use visual-run-02 for a second run. The project, original CSVs and README are supplied in these folders."))
    DAYS["31.5"]["parts"][3]["sections"].append(section("p","Primary references: https://matplotlib.org/stable/users/explain/quick_start.html · https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html · https://matplotlib.org/stable/users/explain/colors/colormaps.html · https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.savefig.html. Essential explanations, executed examples, pictures and exercises are embedded for offline learning."))
    addition="\n".join(json.dumps(k)+": "+json.dumps(v,ensure_ascii=False,indent=2)+"," for k,v in DAYS.items()).replace("</","<\\/")
    prefix=original[:end].rstrip()
    if not prefix.endswith(","): prefix+="," 
    updated=prefix+"\n"+addition+original[end:]
    anchor='    if(s.t==="code") return '
    if updated.count(anchor)!=1: raise RuntimeError("Renderer anchor changed")
    updated=updated.replace(anchor,FIGURE_BRANCH+anchor,1)
    temporary=target.with_suffix(".html.tmp")
    temporary.write_bytes(updated.encode("utf-8")); temporary.replace(target)
    folder=ROOT/"docs"/"python-week31"; folder.mkdir(exist_ok=True)
    (folder/"visual_report.py").write_text(PROJECT,encoding="utf-8",newline="\n")
    print("Added Week31:6 days,24 parts,48 practice prompts,58 quiz questions,72 executed outputs,24 embedded offline chart pictures.")


if __name__=="__main__":
    write()
