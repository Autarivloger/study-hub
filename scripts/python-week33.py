"""Add Week 33 without rewriting prior lessons; execute and embed real charts."""
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
DAYS = {f"33.{d}": {"parts": []} for d in range(6)}
POOL = ThreadPoolExecutor(max_workers=2)
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def chart(body):
    return 'import matplotlib.pyplot as plt\nimport numpy as np\nimport pandas as pd\n' + clean(body) + '\nfig.savefig("chart.png", dpi=110)\nplt.close(fig)\n'


def execute(code):
    with tempfile.TemporaryDirectory(prefix="studyhub-w33-") as folder:
        result = subprocess.run([sys.executable, "-c", code], cwd=folder,
            capture_output=True, encoding="utf-8", timeout=90,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "MPLBACKEND": "Agg"})
        if result.returncode:
            raise RuntimeError(f"Example process exit {result.returncode}: {result.stderr}\n{result.stdout}\n{code}")
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
    parts = DAYS[f"33.{day}"]["parts"]
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
        section("ex", task, practiceId=f"33.{day}.{index}.build"),
        section("sol", code=clean(solution), out="", why="Build check: " + takeaway),
        section("ex", "Mini challenge: " + challenge, practiceId=f"33.{day}.{index}.challenge"),
        section("sol", code=clean(challenge_code), out="", why="Challenge check: " + takeaway),
        section("try", q=quizzes[0][0], code="# Predict first; explain your reason before revealing.", a=quizzes[0][1], why=quizzes[0][4]),
        section("checkpoint", lesson={"id": f"course:33.{day}.{index}", "quiz": questions}), section("key", takeaway)
    ]})
    for s in parts[-1]["sections"]:
        if s["t"] == "sol":
            JOBS.append((POOL.submit(execute, s["code"]), s, None))


lesson(0,"1. Mean, median and mode: different questions",
    "Calculate three centres by hand and explain sensitivity to an extreme value.",
    [("Population; sample; observation", "A population is the full collection you want to describe. A sample is the observed subset. An observation is the unit represented by one row; several sessions from one learner are not several independent learners."),
     ("Mean; median; mode", "Mean is sum divided by count. Median is the middle sorted value, or the average of the two middle values. Modes are the most frequent values; there can be several or no uniquely useful mode."),
     ("NumPy mean/median; pandas mode", "np.mean and np.median calculate numeric centres. Series.mode returns all tied most frequent values rather than assuming there is exactly one.")],
    "Begin with five recorded session durations:10,10,20,30,80 minutes. Their total is150, so the mean is30. Sorted position three is20, so the median is20. Ten occurs twice, making it the unique mode. "
    "These statements describe different features of the same observations. The long80-minute session pulls the mean upward; it does not make the median incorrect. "
    "Choose a summary for the question instead of whichever number looks best. To plan total resource use, a mean can be useful; to describe a typical middle session under skew, the median may be clearer. "
    "Always include count and units. None of these numbers establishes a causal learning effect or describes learners who were never observed. Weeks31–32 supplied the plotting foundations; now the chart supports an explicit numerical calculation.",
    'mean=sum(values)/len(values)\nmedian=np.median(values)\nmodes=pd.Series(values).mode()',
    chart('values=[10,10,20,30,80]\nmean=sum(values)/len(values); median=float(np.median(values))\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nax.hist(values,bins=[0,20,40,60,80,100],edgecolor="white")\nax.axvline(mean,color="#D55E00",label="Mean30"); ax.axvline(median,color="#0072B2",linestyle="--",label="Median20")\nax.set(xlabel="Minutes per session",ylabel="Sessions",title="Same observations, different centres"); ax.legend()\nprint("Mean:",mean,"Median:",median,"Modes:",pd.Series(values).mode().tolist())'),
    "ax.axvline adds a reference at an x coordinate; it does not add a new observation. The mean and median differ because the recorded distribution has a long upper tail.",
    ('typical=max(values)  # label this the mean', 'typical=sum(values)/len(values)', "A named statistic has a defined calculation; the largest value is a maximum, not a mean."),
    "For [2,2,4,8,14], calculate and print mean, median and every mode; draw the values.",
    chart('values=[2,2,4,8,14]\nfig,ax=plt.subplots(); ax.hist(values,bins=[0,4,8,12,16])\nprint(float(np.mean(values)),float(np.median(values)),pd.Series(values).mode().tolist())'),
    "Compare [10,10,20,30,80] with the same first four values and a last value800. Print both means and medians.",
    chart('a=[10,10,20,30,80]; b=[10,10,20,30,800]\nfig,ax=plt.subplots(); ax.boxplot([a,b],tick_labels=["Original","Changed last value"])\nprint("Means:",float(np.mean(a)),float(np.mean(b)))\nprint("Medians:",float(np.median(a)),float(np.median(b)))'),
    "Choose and name the centre; preserve count, units and the observation meaning.",
    [("Which centre averages every value?","Mean","Median always","Mode always","The mean uses the sum and count."),
     ("Can several values tie as modes?","Yes","Never","Only for percentages","A frequency tie can produce several modes.")])

lesson(0,"2. Variance and standard deviation, one subtraction at a time",
    "Calculate squared deviations and distinguish sample from population divisors.",
    [("Deviation; variance; standard deviation", "A deviation is a value minus the mean. Variance averages squared deviations under a chosen divisor; standard deviation is its square root. SD has the original measurement unit; variance has squared units."),
     ("ddof; sample versus population divisor", "For a finite population description divide squared deviations by n. The usual sample variance estimate uses n-1. NumPy defaults to ddof=0, pandas std defaults to ddof=1. Set the choice explicitly."),
     ("n-1 is not a bias repair", "The sample-variance divisor has a statistical rationale under suitable sampling assumptions; it does not fix selection bias or make repeated observations independent. Sample SD is not itself generally an unbiased SD estimator.")],
    "For2,4,6 the mean is4. Deviations are-2,0,2, and squared deviations4,0,4 sum to8. "
    "As a complete three-value population, variance is8/3. As a sample variance estimate, use8/(3-1)=4 and SD2. "
    "Squaring prevents positive and negative deviations cancelling; taking a square root restores the original unit. A large SD means more spread, not automatically a worse outcome. "
    "Check at least two known values before sample SD. One observation cannot estimate sample variation. A library disagreement may simply be a different ddof rather than a programming bug.",
    'sample_var=sum((x-mean)**2 for x in values)/(len(values)-1)\nsample_sd=math.sqrt(sample_var)',
    chart('import math\nvalues=np.array([2.,4.,6.]); mean=float(values.mean())\nsquared=(values-mean)**2\nsample_var=float(squared.sum()/(len(values)-1))\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(["2","4","6"],squared)\nax.set(xlabel="Observed value",ylabel="Squared deviation",title="Squared deviations sum to8")\nprint("Squared deviations:",squared.tolist())\nprint("Sample variance:",sample_var,"SD:",math.sqrt(sample_var))\nprint("NumPy/pandas agree:",np.isclose(np.std(values,ddof=1),pd.Series(values).std(ddof=1)))'),
    "The equality check compares the same ddof. np.isclose allows for floating-point rounding. The graph displays squared deviations, not raw values or probabilities.",
    ('np.std(values) == pd.Series(values).std()  # assume identical defaults', 'np.std(values,ddof=1)  # compare with pandas std(ddof=1)', "The default divisors differ; match the statistical definition first."),
    "Compute sample variance and SD for [1,3,5] by hand and confirm with NumPy.",
    chart('values=np.array([1.,3.,5.]); mean=values.mean(); variance=float(((values-mean)**2).sum()/2)\nfig,ax=plt.subplots(); ax.bar(["1","3","5"],(values-mean)**2)\nprint(variance,float(np.sqrt(variance)),float(np.std(values,ddof=1)))'),
    "For [2,4,6], print variance with ddof0 and1; label them as finite-population and sample calculations.",
    chart('values=[2,4,6]; results=[float(np.var(values,ddof=0)),float(np.var(values,ddof=1))]\nfig,ax=plt.subplots(); ax.bar(["Divide by n","Divide by n-1"],results)\nprint([round(v,6) for v in results])'),
    "State the divisor and unit; matching a formula does not validate how the sample was collected.",
    [("What unit does variance have for minutes?","Minutes squared","Minutes","No unit always","Squaring deviations squares the measurement unit."),
     ("Which NumPy argument matches ordinary pandas sample SD?","ddof=1","ddof=0 always","axis=None alone","Set the divisor convention explicitly.")])

lesson(0,"3. Quartiles, IQR and quantile conventions",
    "Calculate a middle spread and state how quartiles were defined.",
    [("Quantile; percentile; quartile", "A quantile locates a position in ordered observations. The25th and75th percentiles are lower and upper quartiles. Finite samples have several valid interpolation conventions; state the one used."),
     ("IQR; quantile method='linear'", "IQR is Q3-Q1, the spread of the middle half under the stated convention. np.quantile(...,method='linear') interpolates between adjacent ordered values; this is not necessarily the same as splitting halves manually.")],
    "For1,2,3,4,5,6,7,8 the linear interpolation convention gives Q1=2.75 and Q3=6.25, so IQR=3.5. "
    "A school worksheet that uses medians of halves may report different quartiles for this finite list. That does not mean one calculator has lost observations. "
    "The IQR is less affected by extreme tails than a squared-deviation measure. It still omits information: two samples can share the same quartiles and differ within or beyond them. "
    "Keep the raw values available and use a box or strip plot alongside the numerical summary. An interpolated quartile need not equal an actual observed value.",
    'q1,q3=np.quantile(values,[0.25,0.75],method="linear")\niqr=q3-q1',
    chart('values=np.arange(1,9); q1,q3=np.quantile(values,[0.25,0.75],method="linear")\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.boxplot(values,tick_labels=["Eight observations"])\nax.set(ylabel="Value",title="Quartiles use the linear convention")\nprint("Q1:",float(q1),"Q3:",float(q3),"IQR:",float(q3-q1))'),
    "The box spans the two quartiles; its middle line marks the median. Whisker and flier conventions from Week31 are drawing rules, not a guarantee that every value outside is invalid.",
    ('# Mix one hand-calculation convention with another library default', 'np.quantile(values,[0.25,0.75],method="linear")', "Use the same documented convention when comparing numerical results."),
    "For [10,20,30,40,50], print linear Q1, median and Q3 and draw a box.",
    chart('values=[10,20,30,40,50]\nfig,ax=plt.subplots(); ax.boxplot(values)\nprint(np.quantile(values,[0.25,0.5,0.75],method="linear").tolist())'),
    "Change the last value from50 to500 and compare median and IQR before/after.",
    chart('a=[10,20,30,40,50]; b=[10,20,30,40,500]\nfig,ax=plt.subplots(); ax.boxplot([a,b],tick_labels=["A","B"])\nfor values in [a,b]:\n    q=np.quantile(values,[0.25,0.5,0.75],method="linear"); print(float(q[1]),float(q[2]-q[0]))'),
    "Declare the quantile convention and combine middle-spread summaries with the actual observations.",
    [("Can an interpolated quartile be unobserved?","Yes","Never","Only if values are missing","Finite-sample interpolation can produce a value between records."),
     ("What is IQR?","Q3 minus Q1","Maximum minus minimum always","Mean squared error","It measures a stated middle-half spread.")])

lesson(0,"4. Skew, unusual records and missing-value ledgers",
    "Inspect tails and denominators without deleting records to improve a summary.",
    [("Skew; tail sensitivity", "A skewed distribution has an asymmetric tail. Mean/median differences can suggest asymmetry, but do not fully define it or prove a particular distribution model."),
     ("Missingness ledger", "Record source rows, known values and exclusions for each summary. pandas numeric summaries commonly skip missing values; NumPy mean normally propagates NaN unless a nan-aware function is chosen."),
     ("IQR fence", "Q1-1.5*IQR and Q3+1.5*IQR are common descriptive flags. They identify values for investigation, not a universal rule that justifies deletion.")],
    "A long duration may be a genuine deep-work session, a timer left running or a unit-entry mistake. The number alone does not identify which explanation is right. "
    "Inspect the original record and its collection process before repair. Preserve original values and document any justified change, as Week29 taught. "
    "Unknown duration is not zero duration. A known-value mean must carry its known count; otherwise a report can silently change population between calculations. "
    "For a small sample, a histogram and a sorted list often teach more than a specialised skew coefficient. Start with observable shape and explicit exclusions before fitting a distribution.",
    'known=series.dropna()\nsource_n=len(series); known_n=len(known)',
    chart('s=pd.Series([10.,12.,15.,18.,120.,np.nan]); known=s.dropna(); q1,q3=known.quantile([0.25,0.75]); upper=q3+1.5*(q3-q1)\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.hist(known,bins=[0,20,40,60,80,100,120])\nax.set(title="Investigate the long tail; retain the unknown",xlabel="Minutes",ylabel="Known sessions")\nprint("Source/known/unknown:",len(s),len(known),int(s.isna().sum()))\nprint("Flagged, not deleted:",known[known.gt(upper)].tolist())'),
    "The120-minute value is flagged but remains in the data. The unknown row is absent from the histogram, while its count remains visible in the output.",
    ('s=s.fillna(0)  # every unknown becomes a measured zero', 'known=s.dropna()  # disclose source and known counts', "Imputing a zero invents a measurement unless an explicit source contract justifies it."),
    "For [5,10,None,15], print known mean and unknown count, then plot only known values.",
    chart('s=pd.Series([5,10,None,15]); known=s.dropna()\nfig,ax=plt.subplots(); ax.hist(known,bins=[0,10,20])\nprint(float(known.mean()),int(s.isna().sum()))'),
    "Keep [10,12,14,16,100] intact; flag values above a linear IQR upper fence and print source length afterward.",
    chart('s=pd.Series([10,12,14,16,100]); q1,q3=s.quantile([0.25,0.75]); flags=s.gt(q3+1.5*(q3-q1))\nfig,ax=plt.subplots(); ax.boxplot(s)\nprint(s[flags].tolist(),len(s))'),
    "Unusual, missing and invalid are different states; keep an evidence trail for every exclusion or repair.",
    [("Does an IQR flag prove a bad record?","No; investigate its origin","Always","Only above100","A descriptive fence is not a source-validation rule."),
     ("What denominator belongs with a known-value mean?","The number of known values","Every possible learner","Only the flagged rows","Report source and excluded counts as well.")])

lesson(0,"5. Weighted means and unequal denominators",
    "Combine totals correctly and avoid averaging percentages with unequal bases.",
    [("Weighted mean", "A weighted mean is sum(value*weight)/sum(weights). Weights need a stated meaning; counts, exposure and survey weights are not interchangeable concepts."),
     ("Aggregate proportion", "Combining successes across groups uses total successes/total trials. An ordinary mean of group percentages gives every group equal weight, which answers a different question.")],
    "GroupA completes9 of10 tasks and groupB1 of2. Their percentages are90 and50; an equal-group average is70%. "
    "Across all12 tasks,10 were completed, so the task-level completion rate is83.33%. Neither arithmetic is mysterious: the denominators differ. "
    "Write the target unit before combining summaries. Are you describing a typical group equally weighted, or the share of individual tasks completed? "
    "Weights must be finite and have a positive total for the ordinary nonnegative weighted mean taught here. Reweighting cannot repair all selection bias and does not turn a convenience sample into a random sample.",
    'overall=sum(successes)/sum(trials)\nweighted=np.average(rates,weights=trials)',
    chart('successes=np.array([9,1]); trials=np.array([10,2]); rates=successes/trials\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(["Equal group mean","All task rate"],[100*rates.mean(),100*successes.sum()/trials.sum()])\nax.set(ylabel="Completion (%)",ylim=(0,100),title="Different denominators, different questions")\nprint("Equal-group percent:",round(100*rates.mean(),2))\nprint("All-task percent:",round(100*successes.sum()/trials.sum(),2))'),
    "The83.33% rate weights groups by their trial counts. The70% result is an equal-group average, not the combined task success fraction.",
    ('overall=np.mean([0.9,0.5])  # claim this is10/12', 'overall=(9+1)/(10+2)', "Use the correct denominator rather than averaging unlike group bases."),
    "Combine5/10 and90/100 successes; print the equal-group mean and overall fraction.",
    chart('success=np.array([5,90]); trials=np.array([10,100]); rates=success/trials\nfig,ax=plt.subplots(); ax.bar(["Equal groups","All trials"],[rates.mean(),success.sum()/trials.sum()])\nprint(round(float(rates.mean()),4),round(float(success.sum()/trials.sum()),4))'),
    "Compute the weighted mean of scores60,80 with weights1,3 and verify it by expanding [60,80,80,80].",
    chart('weighted=float(np.average([60,80],weights=[1,3])); expanded=float(np.mean([60,80,80,80]))\nfig,ax=plt.subplots(); ax.bar(["Weighted","Expanded"],[weighted,expanded])\nprint(weighted,expanded)'),
    "A summary is meaningful only with a defined unit and denominator; combine counts before rates when the target is all trials.",
    [("What combines success rates across all trials?","Total successes divided by total trials","Always the simple mean of group rates","The largest percentage","The aggregate denominator counts every represented trial."),
     ("Can weighting automatically fix any selection bias?","No","Always","Only if weights sum to100","The source design and target population still matter.")])

lesson(1,"1. Normal models: parameters are assumptions",
    "Separate a model density from observations and simulate reproducibly.",
    [("Normal distribution; loc; scale", "A normal model is a symmetric continuous distribution. loc is its mean and scale its positive standard deviation. It extends without finite bounds; it may be inappropriate for bounded scores or strictly positive durations."),
     ("SciPy stats; pdf; cdf", "SciPy supplies scientific algorithms; from scipy import stats imports its statistics module. A pdf is density, not probability at an exact continuous point. A cdf gives probability at or below a threshold under the model."),
     ("default_rng; seed; simulation", "np.random.default_rng(seed) creates a random generator. A fixed seed makes a chosen computational run reproducible in the tested environment, not representative of real people or proof that the model is correct.")],
    "Start with a model whose centre is50 and SD10. This does not claim that any particular course score actually follows a normal distribution. "
    "Simulate observations from that model, then compare the sample histogram with its theoretical density. The simulated mean will normally differ slightly from50. "
    "For a continuous model, probability belongs to an interval: the area between40 and60, not the height of the curve at50. Density may even exceed1 in tightly concentrated units without violating probability rules. "
    "Check whether the variable's range and observed shape suit a normal approximation. Real0–100 scores have bounds that an unrestricted normal model does not respect.",
    'rng=np.random.default_rng(7)\nvalues=rng.normal(loc=50,scale=10,size=2000)\nprob=stats.norm.cdf(60,loc=50,scale=10)-stats.norm.cdf(40,loc=50,scale=10)',
    chart('from scipy import stats\nrng=np.random.default_rng(7); values=rng.normal(50,10,2000); x=np.linspace(10,90,300)\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.hist(values,bins=25,density=True,alpha=0.5,label="Simulation")\nax.plot(x,stats.norm.pdf(x,loc=50,scale=10),label="Assumed normal density"); ax.set(xlabel="Model value",ylabel="Density"); ax.legend()\nprint("Model P(40 to60):",round(float(stats.norm.cdf(60,50,10)-stats.norm.cdf(40,50,10)),4))\nprint("Simulated mean:",round(float(values.mean()),3))'),
    "np.linspace creates evenly spaced plotting coordinates. density=True normalises histogram area, as in Week32. The orange curve is known from the chosen model; the blue observations are generated, not measured learner data.",
    ('probability=stats.norm.pdf(50,50,10)  # call this P(X=50)', 'probability=stats.norm.cdf(60,50,10)-stats.norm.cdf(40,50,10)', "Density height is not a continuous point probability; calculate interval area via CDF differences."),
    "Simulate1000 values from a normal model with mean0 and SD1; plot them and print the chosen parameters and rounded observed mean.",
    chart('rng=np.random.default_rng(8); values=rng.normal(0,1,1000)\nfig,ax=plt.subplots(); ax.hist(values,bins=25,density=True)\nprint("Model mean/SD:",0,1,"Sample mean:",round(float(values.mean()),3))'),
    "Calculate model probability between-1 and1 for a standard normal and draw its density.",
    chart('from scipy import stats\nx=np.linspace(-4,4,300)\nfig,ax=plt.subplots(); ax.plot(x,stats.norm.pdf(x))\nprint(round(float(stats.norm.cdf(1)-stats.norm.cdf(-1)),4))'),
    "A distribution is an explicit model; simulations and smooth density curves do not establish its truth for real data.",
    [("What does a continuous PDF height represent?","Density","Probability at exactly that point","A row count always","Probability is obtained by area over an interval."),
     ("Does a fixed seed validate a model?","No","Always","Only for normal models","It controls computation, not the collection or assumptions.")])

lesson(1,"2. Uniform models and inclusive integer boundaries",
    "Distinguish continuous intervals from discrete equally likely outcomes.",
    [("Continuous uniform; integer uniform", "rng.uniform(low,high) generates continuous draws over a range. rng.integers(low,high) generates integers with the upper bound excluded by default. A fair die uses integers(1,7), not integers(1,6)."),
     ("Equal density versus equal point mass", "A continuous uniform model has constant density across its interval; each exact point has probability zero. A discrete die assigns probability1/6 to each of six faces.")],
    "Uniform means equally weighted possibilities under a specified model, but the type of possibility matters. A random arrival time within ten minutes is continuous; a six-faced die is discrete. "
    "The die's six outcomes each have positive point probability. A continuous interval contains infinitely many points, so probability is attached to interval length. "
    "Boundary conventions in code are a common source of mistakes. NumPy's high integer bound is excluded, so1 through6 requires high=7. "
    "A short simulated sequence will not show identical face counts. Equal model probabilities describe the generating mechanism, not a requirement that every finite sample be perfectly balanced.",
    'die=rng.integers(1,7,size=10000)\narrival=rng.uniform(0,10,size=10000)',
    chart('rng=np.random.default_rng(11); die=rng.integers(1,7,10000); counts=np.bincount(die,minlength=7)[1:]\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(np.arange(1,7),counts/len(die))\nax.axhline(1/6,color="#D55E00",linestyle="--",label="Model1/6"); ax.set(xlabel="Die face",ylabel="Simulated share"); ax.legend()\nprint("Faces present:",sorted(np.unique(die).tolist()))\nprint("Shares sum:",round(float((counts/len(die)).sum()),6))'),
    "np.bincount counts nonnegative integer occurrences. We discard index0 because a die has no face0. Unequal bars illustrate sampling variation, not evidence that the simulation promised exact quotas.",
    ('rng.integers(1,6,1000)', 'rng.integers(1,7,1000)', "The upper integer bound is excluded; high6 would never produce face6."),
    "Simulate2000 arrivals uniform on0–10 and print the observed proportion in0–2 beside the model value0.2.",
    chart('rng=np.random.default_rng(12); values=rng.uniform(0,10,2000)\nfig,ax=plt.subplots(); ax.hist(values,bins=np.arange(0,11),density=True)\nprint("Observed:",round(float((values<2).mean()),3),"Model:",0.2)'),
    "Generate1000 integers from0 through3 inclusive and print all possible values actually seen.",
    chart('rng=np.random.default_rng(13); values=rng.integers(0,4,1000)\nfig,ax=plt.subplots(); ax.bar(np.arange(4),np.bincount(values,minlength=4))\nprint(sorted(np.unique(values).tolist()))'),
    "Specify discrete versus continuous outcomes and read endpoint conventions before trusting a simulation.",
    [("Which call includes a possible die face6?","rng.integers(1,7)","rng.integers(1,6)","rng.integers(0,6) as a1–6 die","The upper bound is excluded."),
     ("Must1000 fair-die draws give identical counts?","No","Always","Only with a seed","Equal probabilities still produce finite-sample variation.")])

lesson(1,"3. Binomial counts require a fixed trial model",
    "Connect Bernoulli trials, expected count and the exact probability mass.",
    [("Bernoulli; binomial; n; p", "A Bernoulli trial has two outcomes. A binomial count adds successes across n independent trials with the same success probability p. Its mean is n*p and variance n*p*(1-p)."),
     ("pmf; binom", "A probability mass function gives the model probability of each discrete count. stats.binom.pmf(k,n,p) differs from a continuous density: point probabilities may be positive.")],
    "Ten hypothetical independent trials, each with success probability0.3, give a binomial count from0 to10. The expected count is3, but individual experiments can differ. "
    "The assumptions matter. A learner's consecutive quiz responses may depend on shared preparation and question difficulty, so a binomial model is not automatically justified merely because answers are right or wrong. "
    "Different probabilities across trials, dependence or a changing number of trials require another description. Use this example to understand the mechanism rather than asserting that real learning has a fixed success probability. "
    "Compare the simulated count frequencies with the theoretical mass and verify that the probabilities over all possible counts sum to one.",
    'counts=rng.binomial(n=10,p=0.3,size=5000)\nprob=stats.binom.pmf(3,n=10,p=0.3)',
    chart('from scipy import stats\nrng=np.random.default_rng(14); values=rng.binomial(10,0.3,5000); k=np.arange(11)\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(k,np.bincount(values,minlength=11)/len(values),alpha=0.5,label="Simulation")\nax.plot(k,stats.binom.pmf(k,10,0.3),"o-",label="Model mass"); ax.set(xlabel="Successes in10 trials",ylabel="Probability/share"); ax.legend()\nprint("Model mean:",10*0.3)\nprint("Mass sum:",round(float(stats.binom.pmf(k,10,0.3).sum()),6))'),
    "The model gives positive probability for exact counts. In5000 repeated experiments, observed frequencies approximately follow that mass; no single experiment is required to produce exactly three successes.",
    ('# Call any dependent set of yes/no observations binomial', '# Check fixed n, common p and independence under the model', "Two outcome labels alone do not establish binomial sampling assumptions."),
    "For n4,p0.5, print P(exactly2 successes) and draw the full probability mass.",
    chart('from scipy import stats\nk=np.arange(5); mass=stats.binom.pmf(k,4,0.5)\nfig,ax=plt.subplots(); ax.bar(k,mass)\nprint(round(float(mass[2]),4))'),
    "Simulate5000 binomial counts with n20,p0.2 and compare sample mean with model mean4.",
    chart('rng=np.random.default_rng(15); values=rng.binomial(20,0.2,5000)\nfig,ax=plt.subplots(); ax.hist(values,bins=np.arange(-0.5,21.5))\nprint(round(float(values.mean()),3),20*0.2)'),
    "A binomial model describes a specified independent fixed-trial process, not every binary dataset.",
    [("What is a binomial mean?","n*p","n+p","p/n","It adds the expected success contributions of n trials."),
     ("Are binary outcomes alone sufficient for a binomial model?","No","Always","Only for small samples","Trial count, common probability and dependence must be considered.")])

lesson(1,"4. Poisson rates, exposure and model recognition",
    "Scale expected events by exposure and distinguish a model from a fitted story.",
    [("Poisson; lambda; exposure", "A simple homogeneous Poisson process models independent event counts with a stable rate over exposure. For exposure t and rate r, the count mean is lambda=r*t; the Poisson variance equals its mean."),
     ("Model diagnostics", "Compare the variable type, possible range, dependence, changing exposure and observed shape with model assumptions. Similar mean and variance alone do not prove a Poisson mechanism.")],
    "If an idealised process averages two events per hour, three hours has expected count six. The units are part of the calculation: events/hour multiplied by hours. "
    "Unequal observation windows need exposure-aware rates before comparing counts. Ten alerts over ten hours and ten over one hour do not represent the same rate. "
    "Real events may arrive in bursts or vary by time of day, breaking a simple stable independent-rate model. Do not recognise a distribution merely by the shape of a histogram. "
    "Compare the families now: continuous symmetric normal, continuous uniform interval, fixed-trial binomial and exposure-based Poisson counts. Write why the mechanism might fit, and what evidence could contradict it.",
    'expected=rate_per_hour*hours\ncounts=rng.poisson(lam=expected,size=5000)',
    chart('from scipy import stats\nrng=np.random.default_rng(16); expected=2*3; values=rng.poisson(expected,5000); k=np.arange(18)\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(k,stats.poisson.pmf(k,expected)); ax.set(xlabel="Events in3 hours",ylabel="Model probability",title="Rate2/hour times exposure3 hours")\nprint("Expected count:",expected)\nprint("Simulated mean/variance:",round(float(values.mean()),3),round(float(values.var(ddof=0)),3))'),
    "The plotted finite range omits a very small positive upper-tail probability; it is not an assertion that counts above17 are impossible. The full Poisson support extends to all nonnegative integers.",
    ('# Compare10 events/hour with10 events/10hours as equal rates', 'rate=events/exposure_hours', "Counts require a consistent exposure denominator."),
    "Calculate rates for10 events in2 hours and15 in5 hours, draw rate bars and label events/hour.",
    chart('events=np.array([10,15]); hours=np.array([2,5]); rates=events/hours\nfig,ax=plt.subplots(); ax.bar(["A","B"],rates); ax.set_ylabel("Events/hour")\nprint(rates.tolist())'),
    "With rate3/hour over2 hours, calculate P(zero events) using SciPy and draw the first16 count probabilities.",
    chart('from scipy import stats\nk=np.arange(16)\nfig,ax=plt.subplots(); ax.bar(k,stats.poisson.pmf(k,6))\nprint("P(zero):",round(float(stats.poisson.pmf(0,6)),6))'),
    "Choose distributions from variable type and process assumptions; keep exposure visible and investigate contradictions.",
    [("At rate2/hour over3 hours, what is lambda?","6 events","2/3 events","5 events","Rate multiplied by exposure gives the expected count."),
     ("Does a histogram alone establish the generating process?","No","Always","Only with many bins","Mechanism, dependence and exposure require separate evidence.")])

lesson(2,"1. Probability rules from a finite sample space",
    "Count equally likely outcomes and use union, intersection and complement correctly.",
    [("Sample space; event", "The sample space lists possible outcomes under a model. An event is a subset. Counting favourable/total outcomes gives probability only when those outcomes are equally likely."),
     ("Union; intersection; complement", "A union means A or B (including both), intersection means both, and complement means not A. P(A or B)=P(A)+P(B)-P(both); subtraction avoids double-counting."),
     ("Disjoint versus independent", "Disjoint events cannot happen together. Independent events satisfy P(both)=P(A)*P(B). Positive-probability disjoint events are not independent.")],
    "For a fair die, the six faces are equally likely. Let A be an even result and B a result at least4. "
    "A={2,4,6}, B={4,5,6}. Their intersection is{4,6}; the union{2,4,5,6} has four outcomes. Adding the two half-probabilities without subtracting overlap would incorrectly give1. "
    "The complement of A is an odd result with probability1/2. Independence is a separate multiplication property, not a synonym for events that cannot co-occur. "
    "A set diagram or a table of outcomes is often safer than memorising rules without their denominators. Unequally weighted outcomes require summing probabilities rather than simple counts.",
    'p_union=(len(A)+len(B)-len(A&B))/len(space)',
    chart('space=set(range(1,7)); A={2,4,6}; B={4,5,6}\nvalues=[len(A)/6,len(B)/6,len(A&B)/6,len(A|B)/6]\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(["A","B","Both","Either"],values); ax.set(ylabel="Probability",ylim=(0,1),title="Overlapping events on a fair die")\nprint("Both:",sorted(A&B),"Either:",sorted(A|B))\nprint("Union probability:",round(len(A|B)/6,4))'),
    "Python sets express the event operations directly: & intersects and | forms a union. They do not make the outcomes equally likely; fairness is an external model assumption.",
    ('p_either=p_A+p_B  # overlapping events counted twice', 'p_either=p_A+p_B-p_both', "The shared outcomes belong in the union only once."),
    "For a fair die let A={1,2}, B={2,3}. Print union and intersection probabilities and draw them.",
    chart('A={1,2}; B={2,3}; probs=[len(A|B)/6,len(A&B)/6]\nfig,ax=plt.subplots(); ax.bar(["Either","Both"],probs)\nprint(probs)'),
    "Calculate the complement probability of rolling6 and plot probabilities of6 versus not6.",
    chart('p=1/6\nfig,ax=plt.subplots(); ax.bar(["6","Not6"],[p,1-p])\nprint(round(1-p,6))'),
    "Name the sample space and weighting; subtract overlap and distinguish disjointness from independence.",
    [("Why subtract P(both) in the union rule?","It was counted twice","To make events independent","To change the sample size","Shared outcomes contribute once to the union."),
     ("Are disjoint positive-probability events independent?","No","Always","Only on dice","Knowing one occurred rules out the other.")])

lesson(2,"2. Conditional probability changes the denominator",
    "Read P(A given B) and check independence against the actual model.",
    [("Conditional probability", "P(A|B)=P(A and B)/P(B), provided P(B)>0. Restrict the sample space to B, then ask what fraction also satisfies A."),
     ("Direction matters", "P(flag|issue) and P(issue|flag) use different denominators. Reversing the words does not preserve the probability."),
     ("Conditional independence check", "For events of positive probability, independence means learning B does not change P(A). Observed approximate equality in a small sample is not proof of a real mechanism's independence.")],
    "Consider a fictional100-item audit: ten items have an issue, eight of those are flagged; ninety have no issue, nine of those are flagged. "
    "Among issue items,8/10=80% are flagged. Among flagged items,8/17 is about47%. Those are different questions using the same table. "
    "The table is a teaching fixture, not an evaluated security detector. In practice, labels and collection rules would need verification. "
    "When someone quotes a probability, ask after conditioning on what. A conditional statement without its denominator is easy to misread, especially when the underlying condition is uncommon.",
    'p_flag_given_issue=8/10\np_issue_given_flag=8/(8+9)',
    chart('table=np.array([[8,2],[9,81]])\nfig,ax=plt.subplots(figsize=(5,3.5),layout="constrained"); im=ax.imshow(table,cmap="Blues"); ax.set(xticks=[0,1],xticklabels=["Flag","No flag"],yticks=[0,1],yticklabels=["Issue","No issue"]); fig.colorbar(im,ax=ax,label="Fictional count")\nfor (r,c),value in np.ndenumerate(table): ax.text(c,r,str(value),ha="center",va="center",color="black")\nprint("P(flag|issue):",8/10)\nprint("P(issue|flag):",round(8/17,4))'),
    "Rows describe issue status and columns flag status. np.ndenumerate yields each matrix index and value so the plot can display counts. The denominators10 and17 come from different margins.",
    ('p_issue_given_flag=8/10', 'p_issue_given_flag=8/17', "The given event is Flag, so use all17 flagged items as the denominator."),
    "For12 flagged issue items and18 flagged nonissue items, calculate P(issue|flag) and plot their shares among flags.",
    chart('fig,ax=plt.subplots(); ax.bar(["Issue","No issue"],[12/30,18/30])\nprint("P(issue|flag):",12/30)'),
    "For two independent fair coin flips, enumerate outcomes and verify P(first H and second H)=P(first H)*P(second H).",
    chart('outcomes=[("H","H"),("H","T"),("T","H"),("T","T")]\npa=sum(a=="H" for a,b in outcomes)/4; pb=sum(b=="H" for a,b in outcomes)/4; both=sum(a==b=="H" for a,b in outcomes)/4\nfig,ax=plt.subplots(); ax.bar(["Both","Product"],[both,pa*pb])\nprint(both,pa*pb)'),
    "Read the given event as the denominator; conditional probabilities do not generally reverse.",
    [("Which denominator belongs to P(issue|flag)?","All flagged items","All issue items","All nonissue items","The given condition restricts the population being considered."),
     ("Can P(A|B) be assumed equal to P(B|A)?","No","Always","Only when rounded","The events and their base frequencies determine separate quantities.")])

lesson(2,"3. Bayes' rule and the base-rate lesson",
    "Combine prior frequency with conditional evidence using natural counts.",
    [("Prior; likelihood; posterior", "A prior describes the condition frequency before the flag. Likelihood describes how flag behaviour depends on the condition. The posterior updates the condition probability after observing the flag, under the chosen model."),
     ("Bayes' rule", "P(issue|flag)=P(flag|issue)*P(issue)/P(flag). The denominator includes flags from both issue and nonissue items. Natural counts make this accounting visible.")],
    "Imagine10000 fictional items, with1% issues. A flag catches90% of issues and falsely flags5% of nonissues. "
    "There are100 issue items:90 flagged. Of9900 nonissues,495 are flagged. Only90 of585 flagged items have an issue, about15.4%. "
    "A high catch rate therefore does not imply a high issue probability for every flag. The rare underlying condition and false flags matter. "
    "This is a mathematical illustration, not a claim about an actual security product. Changing the base rate while keeping flag performance fixed changes the updated probability. Always carry the assumptions and units into an interpretation.",
    'posterior=(sensitivity*prior)/(sensitivity*prior+false_positive_rate*(1-prior))',
    chart('prior=0.01; catch=0.9; false_flag=0.05\ntrue_flags=10000*prior*catch; false_flags=10000*(1-prior)*false_flag\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(["Issue flags","Nonissue flags"],[true_flags,false_flags]); ax.set(ylabel="Expected flags per10000 model items",title="Base rate changes what a flag means")\nprint("Expected flags:",true_flags,false_flags)\nprint("P(issue|flag):",round(true_flags/(true_flags+false_flags),4))'),
    "These are expected counts under exact model frequencies. A real finite sample could differ. All flagged items belong in the denominator, including false flags.",
    ('posterior=catch  # ignore condition prevalence and false flags', 'posterior=catch*prior/(catch*prior+false_flag*(1-prior))', "Sensitivity is not the same as the probability that a flagged item has the condition."),
    "Use prior0.1, catch0.9 and false-flag rate0.05. Calculate and plot the expected true and false flags per10000.",
    chart('true=10000*0.1*0.9; false=10000*0.9*0.05\nfig,ax=plt.subplots(); ax.bar(["True flags","False flags"],[true,false])\nprint(round(true/(true+false),4))'),
    "Compare posterior probabilities for priors0.01 and0.1 with the same catch/false-flag rates.",
    chart('priors=[0.01,0.1]; post=[0.9*p/(0.9*p+0.05*(1-p)) for p in priors]\nfig,ax=plt.subplots(); ax.bar(["Prior1%","Prior10%"],post)\nprint([round(v,4) for v in post])'),
    "Update with both true and false evidence under a stated base rate; natural counts make Bayes' denominator concrete.",
    [("Which contributes to the flag denominator?","Both true and false flags","Only true flags","Only unflagged items","Bayes' rule accounts for every way to observe the evidence."),
     ("Can changing the prior change the posterior?","Yes","Never","Only if the catch rate changes","The same evidence performance can imply different updated probabilities.")])

lesson(2,"4. Monte Carlo checks and simulation error",
    "Compare a simulated probability with a counted exact answer.",
    [("Monte Carlo; indicator", "Monte Carlo approximates a quantity with random draws from a specified model. An indicator is1 when an event occurs and0 otherwise; its average estimates that event's probability."),
     ("Monte Carlo standard error", "For independent simulated indicators, an approximate simulation SE is sqrt(p_hat*(1-p_hat)/N). It describes finite simulation noise, not source bias, model error or uncertainty from unobserved real data.")],
    "Two fair dice have36 equally likely ordered outcomes. A sum at least10 occurs for six outcomes, giving exact probability1/6. "
    "Simulate10000 pairs and average the event indicator. The result should be near1/6, not exactly equal. A seed allows you to reproduce the run. "
    "More simulation reduces Monte Carlo noise roughly with the square root of the number of draws; it does not correct the assumption that the dice are independent and fair. "
    "Use exact counting where possible to audit your code. A mismatched boundary, excluded face6 or wrong axis can otherwise produce a precise answer to the wrong experiment.",
    'rolls=rng.integers(1,7,size=(10000,2))\nhit=rolls.sum(axis=1)>=10\np_hat=hit.mean()',
    chart('rng=np.random.default_rng(17); rolls=rng.integers(1,7,size=(10000,2)); hit=rolls.sum(axis=1)>=10; p=float(hit.mean()); se=float(np.sqrt(p*(1-p)/len(hit)))\nexact=sum(a+b>=10 for a in range(1,7) for b in range(1,7))/36\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(["Simulation","Exact model"],[p,exact]); ax.set(ylabel="P(sum at least10)",title="10000 simulated independent die pairs")\nprint("Simulated/exact:",round(p,4),round(exact,4))\nprint("Monte Carlo SE:",round(se,5))'),
    "axis=1 adds the two dice within each experiment. Summing axis0 would combine all experiments into two totals and answer a different question.",
    ('rolls.sum(axis=0)>=10', 'rolls.sum(axis=1)>=10', "Each row is one pair of dice; retain one event indicator per experiment."),
    "Simulate10000 single-die rolls and compare the observed share of sixes with1/6.",
    chart('rng=np.random.default_rng(18); values=rng.integers(1,7,10000); p=float((values==6).mean())\nfig,ax=plt.subplots(); ax.bar(["Simulation","Exact"],[p,1/6])\nprint(round(p,4),round(1/6,4))'),
    "Enumerate exact two-die probability of sum7, then simulate10000 pairs as a separate check.",
    chart('exact=sum(a+b==7 for a in range(1,7) for b in range(1,7))/36\nrng=np.random.default_rng(19); rolls=rng.integers(1,7,(10000,2)); estimated=float((rolls.sum(axis=1)==7).mean())\nfig,ax=plt.subplots(); ax.bar(["Exact","Simulation"],[exact,estimated])\nprint(round(exact,4),round(estimated,4))'),
    "A simulation estimates a stated model quantity; report its noise and do not confuse reproducibility with validity.",
    [("What does averaging an event indicator estimate?","The event probability under the generating model","A causal effect automatically","The number of model assumptions","Each draw contributes0 or1."),
     ("Does increasing simulation size fix an incorrect model?","No","Always","Only after10000 draws","It reduces simulation noise around that model's answer.")])

lesson(3,"1. Define the population, sampling frame and unit",
    "Separate the target, observed records and independent sampling units.",
    [("Parameter; statistic; sampling frame", "A parameter describes a population, such as its mean. A statistic is calculated from a sample. The sampling frame is the set from which observations can actually be selected; it may omit part of the target population."),
     ("Selection bias; nonresponse; repeated units", "Selection can overrepresent some people; nonresponse can exclude others. Repeated measurements from one person retain dependence. Larger row counts do not automatically correct any of these problems."),
     ("choice; replace=False", "rng.choice selects from supplied values. replace=False samples without repeating the same array position; it does not prove that the supplied positions were distinct real people.")],
    "If you want to describe all learners but observe only people who choose an optional advanced exercise, the sample may systematically differ from the target. "
    "A large convenience sample can estimate its own selected mean very precisely while missing the population mean. This is bias rather than ordinary random sampling noise. "
    "Name the independent unit: learner, class, organisation or experimental batch. Recording each learner twenty times does not create twenty times as many independent learners. "
    "Our simulated finite population has80 values of20 and20 values of80, giving mean32. A deliberately selected high-only sample has mean80; more observations from that selected subset do not repair the selection.",
    'sample=rng.choice(population,size=20,replace=False)\nselected=population[population>50]',
    chart('population=np.array([20.]*80+[80.]*20); rng=np.random.default_rng(20); sample=rng.choice(population,20,replace=False); selected=population[population>50]\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(["Population","Random sample","High-only sample"],[population.mean(),sample.mean(),selected.mean()]); ax.set(ylabel="Mean simulated value",title="More selected records do not remove selection bias")\nprint("Population mean:",float(population.mean()))\nprint("High-only mean:",float(selected.mean()))'),
    "The population is completely known in this teaching simulation, so its mean can be checked. In real work the population parameter is often unknown and the collection design is essential evidence.",
    ('# Count repeated sessions as independently sampled people', '# Record learner IDs and define the independent sampling unit', "Rows and independent units can differ even when every row is unique."),
    "Draw10 records without replacement from a simulated population1–100; print source size, sample size and mean.",
    chart('population=np.arange(1,101); rng=np.random.default_rng(21); sample=rng.choice(population,10,replace=False)\nfig,ax=plt.subplots(); ax.hist(sample,bins=np.arange(0,101,10))\nprint(len(population),len(sample),round(float(sample.mean()),2))'),
    "For learnerIDs A,A,A,B,B, print rows and distinct learners and draw their row counts.",
    chart('ids=pd.Series(["A","A","A","B","B"]); counts=ids.value_counts()\nfig,ax=plt.subplots(); ax.bar(counts.index,counts.values)\nprint("Rows:",len(ids),"Learners:",ids.nunique())'),
    "Inference starts with a target and sampling design; independence and representativeness do not come from row count alone.",
    [("Can more biased sample rows alone remove selection bias?","No","Always","Only above1000","Sampling noise and systematic selection are separate issues."),
     ("What is a statistic?","A quantity calculated from a sample","Always the population truth","A random seed","The corresponding population quantity is a parameter.")])

lesson(3,"2. Sampling distributions and what the CLT actually changes",
    "Distinguish raw observations from the distribution of repeated sample means.",
    [("Sampling distribution", "Imagine repeatedly collecting a sample under the same design and computing a statistic. The distribution of those statistics is its sampling distribution; it is not the raw-data histogram."),
     ("CLT; finite variance; independence", "Under standard independent identically distributed finite-variance assumptions, the suitably standardised mean approaches a normal distribution as sample size increases. The required size depends on the underlying distribution;30 is not a universal guarantee."),
     ("Exponential model", "The exponential model here is a positive, right-skewed example with mean1 and variance1. It supplies a known population for a simulation, not a claim about actual learning durations.")],
    "Generate many samples from a skewed model, then plot one mean from each sample. With larger sample sizes, the means cluster more tightly and their shape becomes more approximately symmetric in this model. "
    "The individual observations do not become normal. Each observation is still drawn from the same skewed distribution. "
    "A convenient simulation uses a matrix: rows are independent repeated samples and columns are observations inside each sample. Taking mean(axis=1) retains one mean per repeated experiment. "
    "Dependence, severe heavy tails or an inappropriate design can invalidate a simple CLT argument. Do not invoke the word large without checking the assumptions and the estimator involved.",
    'samples=rng.exponential(scale=1,size=(2000,n))\nmeans=samples.mean(axis=1)',
    chart('rng=np.random.default_rng(22); fig,axs=plt.subplots(1,3,figsize=(9,3),layout="constrained")\nfor ax,n in zip(axs,[1,5,30]):\n    means=rng.exponential(1,(2000,n)).mean(axis=1); ax.hist(means,bins=30,density=True); ax.set(title="Mean of n="+str(n),xlabel="Sample mean",ylabel="Density")\n    print("n",n,"mean/SD",round(float(means.mean()),3),round(float(means.std(ddof=1)),3))'),
    "All three histograms contain2000 sample means, but each mean uses a different n. Larger n changes the estimator's repeated-sampling behaviour, not the underlying observation distribution.",
    ('# Claim every raw dataset becomes normal when n>=30', '# Assess the sampling distribution of the chosen statistic under its assumptions', "The CLT is about sums or means under conditions, not a universal transformation of raw data."),
    "Generate1000 samples of size10 from a uniform0–1 model, plot their means and compare their mean with0.5.",
    chart('rng=np.random.default_rng(23); means=rng.uniform(0,1,(1000,10)).mean(axis=1)\nfig,ax=plt.subplots(); ax.hist(means,bins=25)\nprint(round(float(means.mean()),3),0.5)'),
    "For an exponential mean1 model, compare SD of2000 sample means at n4 versus64 and print both.",
    chart('rng=np.random.default_rng(24); spreads=[]; fig,axs=plt.subplots(1,2,layout="constrained")\nfor ax,n in zip(axs,[4,64]):\n    means=rng.exponential(1,(2000,n)).mean(axis=1); spreads.append(round(float(means.std(ddof=1)),3)); ax.hist(means,bins=25); ax.set_title("n="+str(n))\nprint(spreads)'),
    "The CLT concerns a statistic's repeated-sampling distribution under conditions; it does not normalise the observations or cure bias.",
    [("Which distribution becomes approximately normal in the usual mean CLT?","The standardised sample-mean distribution","Every raw observation distribution","The missing-value pattern","The claim concerns repeated sample means under conditions."),
     ("Is n30 a universal normality guarantee?","No","Always","Only if rounded","Tail shape, dependence and the statistic matter.")])

lesson(3,"3. SD measures spread; SE measures estimator noise",
    "Derive the square-root sample-size rule under an IID mean model.",
    [("Standard error of a mean", "Under independent identically distributed sampling, estimated mean SE is sample SD divided by sqrt(n). It describes variation of the estimated mean across comparable repeated samples, not variation of individual observations."),
     ("Square-root rule", "With comparable SD and sampling design, multiplying n by4 roughly halves the mean SE. Dependence or substantial without-replacement sampling fractions require different accounting.")],
    "A class can have a wide spread of individual scores while its estimated mean is relatively stable if many independent observations are available. "
    "SD and SE answer these two different questions. Reporting a tiny SE as though it described variation among learners hides the real spread. "
    "For a model with population SD2, sample means from n4 have theoretical SE1; n64 gives0.25. Individual observations still have SD2 in both experiments. "
    "Use sample SD/sqrt(n) as an estimate when the assumptions suit the design. Repeated sessions per learner cannot simply enter n as though each session were a newly sampled independent learner.",
    'estimated_se=np.std(sample,ddof=1)/np.sqrt(len(sample))',
    chart('rng=np.random.default_rng(25); fig,axs=plt.subplots(1,2,figsize=(7,3),layout="constrained")\nfor ax,n in zip(axs,[4,64]):\n    means=rng.normal(0,2,(3000,n)).mean(axis=1); ax.hist(means,bins=30,density=True); ax.set(title="Means, n="+str(n),xlabel="Sample mean")\n    print("n",n,"theory/observed SE",round(2/np.sqrt(n),3),round(float(means.std(ddof=1)),3))'),
    "The printed observed SE is calculated from repeated simulated means. In a single real sample, that repetition is unavailable, so we estimate SE using the sample SD under the appropriate design.",
    ('learner_spread=sample.std(ddof=1)/np.sqrt(len(sample))', 'learner_spread=sample.std(ddof=1)\nmean_se=learner_spread/np.sqrt(len(sample))', "Do not label estimator uncertainty as individual variation."),
    "For [2,4,6,8], print sample SD and estimated mean SE; show both as distinct bars.",
    chart('values=np.array([2.,4.,6.,8.]); sd=float(values.std(ddof=1)); se=sd/np.sqrt(len(values))\nfig,ax=plt.subplots(); ax.bar(["Individual SD","Mean SE"],[sd,se])\nprint(round(sd,4),round(se,4))'),
    "With model SD12, calculate mean SE for n9 and36 and print their ratio.",
    chart('a=12/np.sqrt(9); b=12/np.sqrt(36)\nfig,ax=plt.subplots(); ax.bar(["n9","n36"],[a,b])\nprint(float(a),float(b),float(a/b))'),
    "Keep individual spread and mean precision separate, and count independent units according to the sampling design.",
    [("With the same IID spread, four times n gives approximately what SE?","Half as large","Four times as large","Exactly unchanged","Mean SE scales as1/sqrt(n)."),
     ("Does a small SE imply individual values are tightly clustered?","No","Always","Only with a mean","A stable mean may summarise a broad distribution.")])

lesson(3,"4. Confidence intervals describe a procedure's coverage",
    "Construct a t interval and interpret repeated coverage without a posterior claim.",
    [("t interval; critical value; degrees of freedom", "For an IID normal sample with unknown variance, a mean t interval is mean +/- t_critical*s/sqrt(n), with df=n-1. stats.t.ppf(0.975,df) supplies the two-sided95% critical value."),
     ("Frequentist coverage", "A95% confidence procedure covers a fixed true parameter in95% of repeated samples under its assumptions. It is not a95% posterior probability assigned to the parameter after observing one realised interval."),
     ("Coverage versus validity", "The nominal level is conditional on model and design assumptions. Bias, dependence or selective reporting can invalidate a displayed95% label.")],
    "Imagine a fixed population mean5 and repeatedly sample twelve independent normal values with SD2. Each sample produces its own mean, SD and interval. "
    "Some intervals miss5; the nominal procedure is not a promise that this one interval must cover it. The simulation lets us inspect repeated coverage because the generating mean is known. "
    "In a real one-sample analysis, the parameter is unknown. State the method, interval, confidence level, sampling unit and relevant assumptions. "
    "An interval around a population mean is also not a range containing95% of individual observations. A prediction question needs a different calculation and interpretation.",
    'critical=stats.t.ppf(0.975,df=n-1)\nlow,high=mean-critical*se,mean+critical*se',
    chart('from scipy import stats\nrng=np.random.default_rng(26); samples=rng.normal(5,2,(1000,12)); means=samples.mean(axis=1); se=samples.std(axis=1,ddof=1)/np.sqrt(12); half=stats.t.ppf(0.975,11)*se; covered=(means-half<=5)&(5<=means+half)\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nfor i in range(25): ax.errorbar(i,means[i],yerr=half[i],fmt="o",color="#0072B2" if covered[i] else "#D55E00")\nax.axhline(5,color="black",linestyle="--"); ax.set(xlabel="Repeated sample",ylabel="Mean interval",title="First25 intervals; true model mean5")\nprint("Coverage across1000:",round(float(covered.mean()),3))'),
    "Different intervals move around one fixed model mean. Orange marks indicate misses among the displayed25. The numerical coverage uses all1000 repetitions and varies with simulation noise.",
    ('# A95% mean interval contains95% of individual scores', '# A95% mean-interval procedure has stated repeated coverage under its assumptions', "Mean uncertainty, individual prediction and posterior probability are different claims."),
    "For [8,9,10,11,12], compute a two-sided95% mean t interval and print rounded limits.",
    chart('from scipy import stats\nvalues=np.array([8.,9.,10.,11.,12.]); mean=values.mean(); half=stats.t.ppf(0.975,4)*values.std(ddof=1)/np.sqrt(5)\nfig,ax=plt.subplots(); ax.errorbar([0],[mean],yerr=[half],fmt="o")\nprint(round(float(mean-half),3),round(float(mean+half),3))'),
    "With the same sample, compare90% and95% t-interval widths and print which is wider.",
    chart('from scipy import stats\nvalues=np.array([8.,9.,10.,11.,12.]); se=values.std(ddof=1)/np.sqrt(5); widths=[2*stats.t.ppf(q,4)*se for q in [0.95,0.975]]\nfig,ax=plt.subplots(); ax.bar(["90%","95%"],widths)\nprint("95% wider:",bool(widths[1]>widths[0]))'),
    "Interpret confidence through the stated procedure and assumptions; a mean interval is not an individual prediction interval.",
    [("What does nominal95% confidence describe?","Repeated-procedure coverage under assumptions","A posterior probability automatically","95% of observed values always","The realised interval is evaluated by a repeated-sampling construction."),
     ("Does95% confidence repair selection bias?","No","Always","Only for t intervals","A confidence label cannot compensate for an invalid design.")])

lesson(3,"5. Bootstrap resampling and the correct independent unit",
    "Approximate a mean's sampling variation without pretending resampling adds new evidence.",
    [("Bootstrap; resampling with replacement", "A bootstrap repeatedly samples from observed units with replacement and recalculates a statistic. It approximates sampling behaviour under assumptions; it cannot recover unobserved groups or remove source bias."),
     ("Percentile interval; resampling unit", "A basic percentile interval takes quantiles of bootstrap statistics. Coverage can be poor for small, skewed or otherwise difficult samples. Resample independent units or appropriate clusters, not dependent rows blindly.")],
    "Take eight fictional independent learner averages. A bootstrap sample also contains eight draws, some repeated and some omitted, chosen from those observed averages. "
    "Repeat the calculation2000 times and inspect the distribution of means. The central95% quantiles are a simple percentile interval, not a guaranteed exact confidence method. "
    "If the source has repeated sessions from each learner, decide the target first. For an equally weighted learner-average mean, calculate one mean per learner and resample those units; this differs from a session-weighted mean when counts vary. "
    "More bootstrap repetitions reduce computational noise but do not increase the number of observed independent learners. Resampling three people ten thousand times is still evidence from three people.",
    'draws=rng.choice(values,size=(2000,len(values)),replace=True)\nmeans=draws.mean(axis=1)\nlimits=np.quantile(means,[0.025,0.975])',
    chart('values=np.array([45.,50.,55.,60.,62.,65.,70.,73.]); rng=np.random.default_rng(27); means=rng.choice(values,(2000,len(values)),replace=True).mean(axis=1); limits=np.quantile(means,[0.025,0.975])\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.hist(means,bins=30); ax.set(xlabel="Bootstrap learner-average mean",ylabel="Resamples",title="Eight observed units, not2000 new learners")\nprint("Observed units:",len(values))\nprint("Percentile limits:",[round(float(v),3) for v in limits])'),
    "The seed fixes this computation. A different bootstrap method or an unsuitable source design could change coverage; the program does not prove the sample is representative.",
    ('# Bootstrap every repeated session as an independent learner', 'learner_means=df.groupby("learner")["score"].mean()\n# Resample these units for an equally weighted learner-mean target', "The sampling unit and target weighting must match the question."),
    "Bootstrap2000 means from [2,4,6,8] using seed28, then print the mean of bootstrap means beside the observed mean.",
    chart('values=np.array([2.,4.,6.,8.]); rng=np.random.default_rng(28); means=rng.choice(values,(2000,4),replace=True).mean(axis=1)\nfig,ax=plt.subplots(); ax.hist(means,bins=20)\nprint(round(float(means.mean()),3),float(values.mean()))'),
    "For learnerA scores40,60 and B80, calculate equally weighted learner mean and all-session mean. Plot both and print their difference.",
    chart('df=pd.DataFrame({"learner":["A","A","B"],"score":[40,60,80]}); learner_mean=float(df.groupby("learner")["score"].mean().mean()); session_mean=float(df["score"].mean())\nfig,ax=plt.subplots(); ax.bar(["Equal learners","All sessions"],[learner_mean,session_mean])\nprint(learner_mean,session_mean,learner_mean-session_mean)'),
    "Bootstrap the appropriate units for a stated target; resampling reuses evidence and does not create new independent observations.",
    [("Do2000 bootstrap repetitions mean2000 newly observed people?","No","Always","Only with replacement","The original source units remain the evidence base."),
     ("Can equal-learner and all-session means differ?","Yes, when session counts vary","Never","Only if sorted","The two targets apply different weights.")])

lesson(4,"1. Hypotheses, p-values and decisions before results",
    "State a null model, alternative, statistic and analysis plan before looking for a small p.",
    [("Null; alternative; p-value", "A null is a specified model claim. A p-value is the probability, under that null and other assumptions, of a test statistic at least as incompatible as the observed one. It is not the probability that the null is true."),
     ("Alpha; Type I/II error; power", "A prechosen alpha bounds a test procedure's Type I error under its assumptions: rejecting a true null. Type II error means failing to reject under a specified alternative; power is its complement. Not rejecting does not prove equality."),
     ("binomtest; two-sided", "stats.binomtest compares an observed success count with a fixed binomial null. alternative='two-sided' considers departures in either direction using its exact discrete rule. Choose direction before examining outcomes.")],
    "Suppose ten independent tosses from a model produce eight heads. The null is a fair coin with p=0.5; the alternative is a different head probability. "
    "A two-sided exact test calculates how incompatible that count is with the specified null. The resulting p is about0.109, not a10.9% probability that the coin is fair. "
    "A threshold such as0.05 can be part of a declared decision rule, but it does not divide truth from falsehood or measure practical importance. "
    "Before running a study, define the target, outcome, independent units, comparison, direction, exclusions and test family. Collecting more data only until p becomes small changes the procedure and requires appropriate sequential methods.",
    'result=stats.binomtest(k=8,n=10,p=0.5,alternative="two-sided")\nprint(result.pvalue)',
    chart('from scipy import stats\nk=np.arange(11); mass=stats.binom.pmf(k,10,0.5); extreme=np.abs(k-5)>=3\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(k,mass,color=["#D55E00" if flag else "#0072B2" for flag in extreme]); ax.set(xlabel="Heads out of10",ylabel="Null probability",title="Two-sided incompatibility with a fair-coin model")\nresult=stats.binomtest(8,10,0.5,alternative="two-sided")\nprint("Exact p:",round(float(result.pvalue),6))\nprint("Not the probability the null is true")'),
    "For the symmetric fair-coin example, counts at least three away from five form the coloured tails. This illustration is not a universal rule for every two-sided discrete test.",
    ('print("P(null true)=",result.pvalue)', 'print("Tail incompatibility under the specified null:",result.pvalue)', "The conditional probability is under a model, not a posterior probability of that model."),
    "Calculate a two-sided fair-coin exact p for5 heads in10 tosses and plot the null mass.",
    chart('from scipy import stats\nk=np.arange(11)\nfig,ax=plt.subplots(); ax.bar(k,stats.binom.pmf(k,10,0.5))\nprint(float(stats.binomtest(5,10,0.5).pvalue))'),
    "Calculate the same test for10 heads in10 tosses, print its p and one sentence explaining why it does not measure effect importance.",
    chart('from scipy import stats\nk=np.arange(11)\nfig,ax=plt.subplots(); ax.bar(k,stats.binom.pmf(k,10,0.5))\nprint(round(float(stats.binomtest(10,10,0.5).pvalue),6))\nprint("Importance depends on the application and effect, not p alone")'),
    "Report the model, statistic, effect and assumptions; a p-value is neither a truth probability nor a measure of practical importance.",
    [("What is a p-value conditioned on?","The null model and test assumptions","The null being false automatically","A guaranteed representative population","It describes a statistic's null-model behaviour."),
     ("Does failure to reject prove equal populations?","No","Always","Only at alpha0.05","Limited power and sampling uncertainty can leave differences unresolved.")])

lesson(4,"2. Welch's t-test: independent means with an effect interval",
    "Compare means without assuming equal variances and preserve the comparison direction.",
    [("Welch t-test; equal_var=False", "stats.ttest_ind(a,b,equal_var=False) tests equal population means for independent samples without assuming equal variances. It still requires an appropriate independence/design model and a suitable sampling-distribution approximation."),
     ("Difference and confidence_interval", "The effect is mean(a)-mean(b), in the outcome's unit. result.confidence_interval returns a nominal interval for that same mean difference. A two-sided test and interval are not a causal design."),
     ("nan_policy='raise'", "This option refuses unknown input values rather than silently omitting them. If exclusions are justified, make and report them before testing.")],
    "Compare two independent fictional sets of durations. The question is a difference in mean minutes, not a difference in category counts or medians. "
    "Welch's method allows unequal variances; it does not make dependent sessions independent or rescue an inappropriate sample. Inspect raw values and consider skew, extreme observations and small group sizes. "
    "Report each n, both means, A-minus-B difference, interval and p. Keep the sign consistent: swapping group order reverses the effect and t statistic, while a two-sided p remains the same. "
    "The interval is marginal95% under the method's assumptions, not a95% probability statement about this realised effect. A small p alone cannot establish a meaningful improvement.",
    'result=stats.ttest_ind(a,b,equal_var=False,alternative="two-sided",nan_policy="raise")\nci=result.confidence_interval(0.95)',
    chart('from scipy import stats\na=np.array([12.,14.,15.,16.,18.,20.]); b=np.array([10.,11.,13.,15.,17.,19.]); result=stats.ttest_ind(a,b,equal_var=False,nan_policy="raise"); ci=result.confidence_interval(0.95)\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.boxplot([a,b],tick_labels=["Independent A","Independent B"]); ax.set(ylabel="Minutes",title="Inspect values before interpreting a mean comparison")\nprint("A-B minutes:",round(float(a.mean()-b.mean()),3))\nprint("95% limits:",round(float(ci.low),3),round(float(ci.high),3))\nprint("Two-sided p:",round(float(result.pvalue),6))'),
    "The plot describes the observed samples. The test adds a model-based comparison of means; neither the box nor the test identifies a treatment mechanism.",
    ('stats.ttest_ind(before,after)  # repeated measurements treated as independent', 'stats.ttest_ind(independent_a,independent_b,equal_var=False)', "Choose the method from the sampling design; Day5 Part3 handles paired observations."),
    "For A[5,7,8,9,11], B[4,5,7,8,10], print mean difference and a Welch two-sided p.",
    chart('from scipy import stats\na=np.array([5.,7.,8.,9.,11.]); b=np.array([4.,5.,7.,8.,10.]); result=stats.ttest_ind(a,b,equal_var=False)\nfig,ax=plt.subplots(); ax.boxplot([a,b],tick_labels=["A","B"])\nprint(round(float(a.mean()-b.mean()),4),round(float(result.pvalue),6))'),
    "Reverse the groups for that example and verify the two-sided p stays equal while the statistic changes sign.",
    chart('from scipy import stats\na=np.array([5.,7.,8.,9.,11.]); b=np.array([4.,5.,7.,8.,10.]); ab=stats.ttest_ind(a,b,equal_var=False); ba=stats.ttest_ind(b,a,equal_var=False)\nfig,ax=plt.subplots(); ax.bar(["A-B","B-A"],[a.mean()-b.mean(),b.mean()-a.mean()])\nprint(bool(np.isclose(ab.pvalue,ba.pvalue)),bool(np.isclose(ab.statistic,-ba.statistic)))'),
    "Match the design, report the effect in real units and keep direction, interval and p interpretation consistent.",
    [("What does equal_var=False select?","Welch's unequal-variance method","A paired test","A count-frequency test","It relaxes the equal-population-variance assumption, not independence."),
     ("What is the effect direction in ttest_ind(a,b)?","Mean a minus mean b","Always absolute difference","Median b minus median a","Sign and interval must follow the declared contrast.")])

lesson(4,"3. Paired t-tests analyse within-unit differences",
    "Keep matched identities and distinguish before/after association from causal proof.",
    [("Paired t-test; ttest_rel", "stats.ttest_rel(after,before) compares matched observations by testing their within-pair differences. Pairs must align and independent units should be the pairs, not the two columns treated as separate groups."),
     ("Pair-complete exclusions", "Filter unknown outcomes jointly by ID before testing and report excluded pairs. Sorting before and after separately destroys the matching. Small-sample t inference assumes approximately normal differences, not necessarily two individually normal columns.")],
    "Six fictional learners each have a before and after score. Their personal differences are the evidence for a paired mean-change calculation. "
    "A common learner-specific baseline is then accounted for through subtraction. But a before/after change without a suitable control may reflect time, practice or other changes; the paired test alone does not identify a teaching effect. "
    "Check identity, pair completeness and the distribution of differences. An unknown after score should not be filled with zero or paired with somebody else's before score. "
    "The code calls ttest_rel(after,before), so a positive result means a positive mean after-minus-before change. Report the number of independent learner pairs.",
    'difference=after-before\nresult=stats.ttest_rel(after,before,nan_policy="raise")',
    chart('from scipy import stats\nbefore=np.array([40.,50.,60.,65.,70.,80.]); after=np.array([45.,52.,61.,70.,76.,81.]); change=after-before; result=stats.ttest_rel(after,before,nan_policy="raise")\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(np.arange(1,7),change); ax.axhline(0,color="black"); ax.set(xlabel="Learner pair",ylabel="After-before points",title="Six matched fictional learners")\nprint("Pairs:",len(change),"Mean change:",round(float(change.mean()),3))\nprint("Paired p:",round(float(result.pvalue),6))'),
    "Each bar is a matched difference. The procedure tests a mean change under assumptions; it does not turn a temporal comparison into a randomised experiment.",
    ('before=np.sort(before); after=np.sort(after)  # independently reorder pairs', 'difference=after-before  # after aligning by learner ID', "Separate sorting invents new pairings and changes the question."),
    "Use before[50,60,70,80], after[52,65,71,84]; calculate changes and the paired mean-change p.",
    chart('from scipy import stats\nbefore=np.array([50.,60.,70.,80.]); after=np.array([52.,65.,71.,84.]); change=after-before\nfig,ax=plt.subplots(); ax.bar(np.arange(4),change)\nprint(change.tolist(),round(float(stats.ttest_rel(after,before).pvalue),6))'),
    "For three paired rows with one missing after score, keep complete pairs, draw differences and print retained/excluded counts without running a fragile two-pair inference.",
    chart('df=pd.DataFrame({"before":[50,60,70],"after":[55,None,72]}); valid=df.notna().all(axis=1); pair=df.loc[valid]; change=pair["after"]-pair["before"]\nfig,ax=plt.subplots(); ax.bar(pair.index.astype(str),change)\nprint("Retained/excluded:",int(valid.sum()),int((~valid).sum()))'),
    "Pair by identity, analyse differences and report causal limitations rather than treating a before/after p as proof of an intervention.",
    [("Which values drive a paired t-test?","Within-pair differences","All values randomly shuffled","Only group medians","The pairing is part of the design."),
     ("Does a paired before/after test alone establish a cause?","No","Always","Only if every score rose","Time and other changes can explain an observed difference.")])

lesson(4,"4. Chi-square tests need counts and adequate expectations",
    "Build a contingency table, inspect expected counts and choose a method from the design.",
    [("Contingency table; independence null", "A contingency table cross-classifies categorical observations using counts. The chi-square independence null says the category distributions are independent in the specified model; rows must represent suitable independent observational units."),
     ("Expected counts; chi2_contingency", "Expected counts under independence equal row_total*column_total/grand_total. stats.chi2_contingency returns the statistic, p, degrees of freedom and expected table. This lesson uses correction=False explicitly."),
     ("Sparse tables; Fisher exact", "Small expected counts can undermine the chi-square approximation. A common teaching check is all expectations>=5; method choice depends on the table/design. stats.fisher_exact is an exact conditional option for a suitable2-by2 table, not a way to search for the smallest p.")],
    "Suppose independent fictional items are classified by group A/B and outcome pass/fail. A table [[30,20],[20,30]] has50 observations per group and50 of each outcome overall. "
    "The independence expectation is25 in each cell. Compare observed deviations with these expectations; do not feed percentages as though they were counts. "
    "An association test does not measure a causal effect, direction of mechanism or practical size by itself. Include observed group proportions and differences. "
    "Preselect a suitable procedure and check assumptions. Repeated records, empty margins or a sparse table need attention before a p-value. Switching tests after seeing results is not a valid analysis plan.",
    'result=stats.chi2_contingency(table,correction=False)\nexpected=result.expected_freq',
    chart('from scipy import stats\ntable=np.array([[30,20],[20,30]]); result=stats.chi2_contingency(table,correction=False)\nfig,ax=plt.subplots(figsize=(5,3.5),layout="constrained"); im=ax.imshow(table,cmap="Blues"); ax.set(xticks=[0,1],xticklabels=["Pass","Fail"],yticks=[0,1],yticklabels=["A","B"]); fig.colorbar(im,ax=ax,label="Count")\nprint("Expected:",result.expected_freq.tolist())\nprint("Chi-square/df/p:",round(float(result.statistic),3),result.dof,round(float(result.pvalue),6))'),
    "Each expected count is25, supporting the approximation's basic count check here. Independence of observations remains a design assumption the numeric table cannot prove.",
    ('stats.chi2_contingency([[0.6,0.4],[0.4,0.6]])', 'stats.chi2_contingency([[30,20],[20,30]],correction=False)', "The calculation requires counts; percentages discard the sample-size information."),
    "For [[20,20],[20,20]], calculate expected counts and p; plot the observed counts.",
    chart('from scipy import stats\ntable=np.array([[20,20],[20,20]]); result=stats.chi2_contingency(table,correction=False)\nfig,ax=plt.subplots(); ax.imshow(table,cmap="Blues")\nprint(result.expected_freq.tolist(),round(float(result.pvalue),6))'),
    "For the sparse2-by2 table [[1,8],[5,2]], inspect minimum expected count and demonstrate the preselected two-sided Fisher exact option.",
    chart('from scipy import stats\ntable=np.array([[1,8],[5,2]]); expected=stats.contingency.expected_freq(table)\nfig,ax=plt.subplots(); ax.imshow(table,cmap="Blues")\nprint("Minimum expected:",round(float(expected.min()),3))\nprint("Fisher two-sided p:",round(float(stats.fisher_exact(table,alternative="two-sided").pvalue),6))'),
    "Counts, expected frequencies and observational independence define the test context; a contingency p is not a causal explanation.",
    [("What belongs in an ordinary contingency table test?","Observed counts","Percentages with unknown denominators","Group means","The count scale determines the sampling information."),
     ("Does adequate expected count prove observations are independent?","No","Always","Only in a2-by2 table","The design, not the expected-frequency calculation, establishes independence.")])

lesson(4,"5. Effect size, multiple tests and honest reporting",
    "Report a family of results without selecting only favourable p-values.",
    [("Effect magnitude; practical relevance", "A raw mean difference retains its measurement unit. Practical relevance needs a domain threshold chosen with context; a p-value or its significance label is not an effect size."),
     ("Multiplicity; Bonferroni", "Testing a family creates more opportunities for false rejection. A simple Bonferroni family adjustment multiplies each valid p by the number of planned tests and caps it at1; it controls familywise error under suitable assumptions even with dependent tests."),
     ("Marginal versus simultaneous intervals", "Separate95% intervals are marginal intervals, not automatic simultaneous95% coverage for a whole family. Adjusted p-values do not silently turn unadjusted intervals into simultaneous intervals.")],
    "If twenty null tests are run at0.05, each has its own opportunity for a false rejection. Selecting the smallest p and hiding the rest changes the reader's understanding of the search. "
    "Choose the test family before looking for favourable results and report every planned comparison. Bonferroni is a simple conservative starting point, not permission to forget the underlying model assumptions. "
    "For p0.01 and0.04 in a two-test family, adjusted values are0.02 and0.08. Keep raw and adjusted values side by side. "
    "A statistically detectable effect may be too small to matter, and a wide interval may leave important possibilities unresolved. Include units, uncertainty, limitations and the analysis's exploratory or confirmatory status.",
    'adjusted=np.minimum(1,raw_p*number_of_planned_tests)',
    chart('raw=np.array([0.01,0.04]); adjusted=np.minimum(1,raw*2); x=np.arange(2)\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.bar(x-0.18,raw,width=0.35,label="Raw p"); ax.bar(x+0.18,adjusted,width=0.35,label="Bonferroni2 tests"); ax.axhline(0.05,color="black",linestyle="--",label="Prechosen alpha0.05"); ax.set(xticks=x,xticklabels=["Test1","Test2"],ylabel="p-value"); ax.legend()\nprint("Adjusted:",adjusted.tolist())'),
    "The adjustment accounts for a stated family size; it does not make a biased dataset valid. The same threshold can produce a different decision after accounting for the family.",
    ('print(min(all_p))  # publish only this result', 'print(all_p)\nadjusted=np.minimum(1,np.asarray(all_p)*len(all_p))', "Retain the whole planned family and disclose any exploratory search beyond it."),
    "Adjust p-values[0.02,0.2,0.8] for a three-test family and print the capped values.",
    chart('raw=np.array([0.02,0.2,0.8]); adjusted=np.minimum(1,raw*3)\nfig,ax=plt.subplots(); ax.bar(["A","B","C"],adjusted)\nprint([round(float(v),4) for v in adjusted])'),
    "Under independent true-null tests, calculate the chance of at least one false rejection among20 tests at alpha0.05 and compare it with0.05.",
    chart('family_error=1-(1-0.05)**20\nfig,ax=plt.subplots(); ax.bar(["One test","20 independent tests"],[0.05,family_error])\nprint(round(family_error,4))'),
    "Report effects and the full planned family; disclose exploratory choices and keep marginal interval claims separate from familywise decisions.",
    [("What is Bonferroni-adjusted p for0.04 in a two-test family?","0.08","0.02","0.04 always","Multiply by the family size and cap at1."),
     ("Does adjusting p automatically adjust a marginal95% interval?","No","Always","Only if both are printed","Simultaneous coverage requires its own interval procedure.")])

lesson(5,"1. Pearson correlation needs paired observations and a scatter check",
    "Calculate linear association and recognise constant or incomplete inputs.",
    [("Pearson r; pearsonr", "Pearson r summarises linear association between paired numeric values. stats.pearsonr returns r and a model-based p, but this part reports only the descriptive coefficient. Constant input makes r undefined."),
     ("Association is not general dependence", "A nonlinear relationship can have a near-zero Pearson r. A strong r can also be driven by an extreme observation or a mixed-group pattern. Inspect the scatter before reducing it to one number.")],
    "Minutes and score must come from the same observation. Filter them jointly, report retained count and check that both vary. "
    "The coefficient is dimensionless and lies between-1 and1 when defined. It describes direction and strength of a linear association, not a change in score caused by adding a minute. "
    "For a symmetric quadratic pattern y=x squared, the dependence is obvious but linear correlation can be zero. A printed coefficient alone would miss the shape. "
    "Formal inference for r has further assumptions about the paired sample and distribution; do not treat a small software-generated p as permission to ignore them. This part uses coefficients for exploration only.",
    'paired=df[["x","y"]].dropna()\nr=stats.pearsonr(paired["x"],paired["y"]).statistic',
    chart('from scipy import stats\nx=np.array([-2.,-1.,0.,1.,2.]); y=x**2\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.scatter(x,y); ax.set(xlabel="x",ylabel="x squared",title="Clear nonlinear structure; zero linear association")\nprint("Pearson r:",round(float(stats.pearsonr(x,y).statistic),6))\nprint("Dependent shape, not a straight line")'),
    "Symmetry balances positive and negative linear contributions. Zero r is not a universal independence test; this deterministic example makes the distinction visible.",
    ('# r near0 means no relationship of any kind', '# Inspect the scatter and the kind of relationship r measures', "Pearson measures linear association, not every possible dependency."),
    "For x[1,2,3,4], y[2,4,6,8], plot the pairs and print Pearson r.",
    chart('from scipy import stats\nx=[1,2,3,4]; y=[2,4,6,8]\nfig,ax=plt.subplots(); ax.scatter(x,y)\nprint(round(float(stats.pearsonr(x,y).statistic),6))'),
    "Use x[1,2,3], y[5,5,5]. Detect the constant y and print that correlation is undefined rather than calling the function and replacing NaN with0.",
    chart('x=np.array([1,2,3]); y=np.array([5,5,5])\nfig,ax=plt.subplots(); ax.scatter(x,y)\nprint("Correlation undefined:",bool(np.ptp(y)==0))'),
    "Preserve pairing, check variation and inspect shape; a correlation coefficient is not a causal slope or a general dependence verdict.",
    [("Can Pearson r be0 for a nonlinear dependency?","Yes","Never","Only with missing data","Linear association does not capture every shape."),
     ("What is r for a constant measured variable?","Undefined","Automatically0","Automatically1","There is no variation with which to define the usual correlation.")])

lesson(5,"2. Spearman ranks capture monotonic association",
    "Contrast rank association with linear association and handle ties honestly.",
    [("Rank; tied ranks; Spearman rho", "Spearman correlation is Pearson correlation of ranks. Ties receive an appropriate shared rank convention. It measures monotonic association: whether one variable tends to increase as the other increases, without requiring a straight line."),
     ("spearmanr; rankdata", "stats.spearmanr returns the rank coefficient and an inferential p. stats.rankdata shows assigned ranks. We report descriptive coefficients here; small-sample inference needs appropriate methods and assumptions.")],
    "For positive x values, y=x cubed is strictly increasing but curved. The order is perfectly preserved, so Spearman rho is1 even though a straight-line relationship is not perfect. "
    "Rank methods reduce sensitivity to the numerical size of extreme values, but they do not automatically remove bad data, selection bias or confounding. "
    "Repeated equal scores create tied ranks. Constant variables still have undefined rank correlation. Missingness still requires paired handling. "
    "Choose the association question before seeing which coefficient looks stronger: linear association and monotonic association are related but distinct descriptions.",
    'rho=stats.spearmanr(x,y).statistic\nranks=stats.rankdata(values)',
    chart('from scipy import stats\nx=np.array([1.,2.,3.,4.,5.]); y=x**3\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained"); ax.scatter(x,y); ax.set(xlabel="x",ylabel="x cubed",title="Perfect order, curved magnitude")\nprint("Pearson:",round(float(stats.pearsonr(x,y).statistic),4))\nprint("Spearman:",round(float(stats.spearmanr(x,y).statistic),4))'),
    "The rank coefficient1 describes the preserved ordering. It does not state that doubling x doubles y or that changing x experimentally would produce this response in a real system.",
    ('# Choose the largest correlation and hide the other question', '# State whether linear or monotonic association answers the question', "Selecting a favourable coefficient after inspection needs to be disclosed as exploration."),
    "For x1–5 and y[25,16,9,4,1], draw the decreasing pattern and print Spearman rho.",
    chart('from scipy import stats\nx=np.arange(1,6); y=[25,16,9,4,1]\nfig,ax=plt.subplots(); ax.scatter(x,y)\nprint(round(float(stats.spearmanr(x,y).statistic),4))'),
    "Inspect tied ranks for [10,10,20,30] and plot the assigned ranks against the original values.",
    chart('from scipy import stats\nvalues=[10,10,20,30]; ranks=stats.rankdata(values)\nfig,ax=plt.subplots(); ax.scatter(values,ranks)\nprint(ranks.tolist())'),
    "Spearman describes monotonic order, not necessarily a straight line, independent observations or causation.",
    [("A strictly increasing curved relation can have what Spearman rho?","1","Only0","Only negative values","Ranks preserve monotonic order even when magnitudes curve."),
     ("Do rank methods automatically remove confounding?","No","Always","Only without ties","The collection and causal structure remain relevant.")])

lesson(5,"3. Fit a line, read its units and inspect residuals",
    "Calculate a descriptive least-squares fit and distinguish in-sample R squared from prediction quality.",
    [("OLS; slope; intercept; linregress", "Ordinary least squares selects a line to minimise summed squared vertical residuals. stats.linregress returns its slope, intercept and correlation. A slope has y-units per x-unit; the intercept is a fitted y at x0, possibly outside observed support."),
     ("Fitted value; residual; R squared", "fitted=intercept+slope*x; residual=observed-fitted. For simple in-sample OLS with an intercept and nonconstant y, R squared equals r squared and measures the fraction of observed y sum-of-squares represented by the fitted line. It is not percent prediction accuracy."),
     ("Extrapolation; diagnostics", "Predictions outside observed x values may be unsupported. Inference and prediction intervals need further assumptions; residual patterns can expose nonlinearity, unequal spread or unusual points.")],
    "A line is a compact summary, not a claim that every point lies on it. Calculate fitted values and inspect residuals rather than reporting only a correlation. "
    "If x is minutes and y is points, a slope2 means the fitted line rises two points per minute within this descriptive model. It does not establish that an extra minute causes two points. "
    "The in-sample fit is optimised on the same observations used to score it. Future prediction performance requires separate evaluation and appropriate uncertainty; a high training R squared cannot supply that evidence. "
    "An intercept may have little substantive meaning when x0 lies far outside the observed range. Always state range, units and whether interpretation is descriptive.",
    'fit=stats.linregress(x,y)\npredicted=fit.intercept+fit.slope*x\nresidual=y-predicted\nr_squared=fit.rvalue**2',
    chart('from scipy import stats\nx=np.array([1.,2.,3.,4.,5.]); y=np.array([2.,4.,5.,4.,5.]); fit=stats.linregress(x,y); predicted=fit.intercept+fit.slope*x; residual=y-predicted\nfig,axs=plt.subplots(1,2,figsize=(8,3),layout="constrained"); axs[0].scatter(x,y); axs[0].plot(x,predicted,color="#D55E00"); axs[0].set(xlabel="x",ylabel="y",title="Descriptive fitted line"); axs[1].scatter(predicted,residual); axs[1].axhline(0,color="black"); axs[1].set(xlabel="Fitted y",ylabel="Observed minus fitted",title="Residual check")\nprint("Slope/intercept:",round(float(fit.slope),3),round(float(fit.intercept),3))\nprint("In-sample R squared:",round(float(fit.rvalue**2),4))\nprint("Residual sum near0:",bool(np.isclose(residual.sum(),0)))'),
    "The line slopes upward but does not pass through every observation. Residuals retain what the fit misses; near-zero residual sum is an algebraic property here, not proof of model adequacy.",
    ('print("Prediction accuracy percent:",100*fit.rvalue**2)', 'print("In-sample R squared:",fit.rvalue**2)', "R squared is not a percentage of correct future predictions."),
    "Fit y=[3,5,7,9] against x=[1,2,3,4], draw the line and print slope, intercept and R squared.",
    chart('from scipy import stats\nx=np.array([1.,2.,3.,4.]); y=np.array([3.,5.,7.,9.]); fit=stats.linregress(x,y)\nfig,ax=plt.subplots(); ax.scatter(x,y); ax.plot(x,fit.intercept+fit.slope*x)\nprint(float(fit.slope),float(fit.intercept),round(float(fit.rvalue**2),6))'),
    "Fit a straight line to x[-2,-1,0,1,2], y=x squared and plot residuals; print R squared without calling the relation absent.",
    chart('from scipy import stats\nx=np.array([-2.,-1.,0.,1.,2.]); y=x*x; fit=stats.linregress(x,y); residual=y-(fit.intercept+fit.slope*x)\nfig,ax=plt.subplots(); ax.scatter(x,residual); ax.axhline(0,color="black")\nprint("Linear R squared:",round(float(fit.rvalue**2),6))\nprint("The curved relationship remains")'),
    "Report units, range and residuals; a fitted line and high in-sample R squared do not establish cause or future accuracy.",
    [("What is a residual?","Observed y minus fitted y","Always a recording error","The slope alone","It is the vertical discrepancy left by the fitted model."),
     ("Does R squared0.9 mean90% correct predictions?","No","Always","Only in-sample","It is a sum-of-squares fit measure under the stated model.")])

lesson(5,"4. Pooled patterns, strata and causal restraint",
    "Check whether grouping explains an apparent overall relationship.",
    [("Stratification; confounding", "Stratification examines defined groups separately. A confounder can be related to both a measured predictor and outcome, creating or changing a pooled association. Stratification is a diagnostic, not an automatic causal identification method."),
     ("Ecological and composition effects", "A relation across group averages does not necessarily describe individual relations. Changing group composition can move an overall average without a comparable change within every group.")],
    "Imagine one fictional group with short durations and low scores, and another with longer durations and high scores. Pooling them creates an upward relationship even if the within-group score pattern is not upward. "
    "The grouping could represent prior skill or another factor, not a treatment effect of time. Plot categories and calculate within-group coefficients before attributing the pooled pattern to one variable. "
    "Even checking one group variable does not eliminate every confounder. A causal claim requires a suitable design and additional assumptions, not simply a more colourful scatter. "
    "This prepares you for the real Iris dataset: pooled flower measurements combine species with very different sizes. The capstone will report both pooled and species-specific descriptions.",
    'pooled=stats.pearsonr(df["x"],df["y"]).statistic\n# Inspect each declared stratum using the same paired variables.',
    chart('from scipy import stats\ndf=pd.DataFrame({"group":["A"]*3+["B"]*3,"x":[1,2,3,7,8,9],"y":[3,2,1,9,8,7]})\nfig,ax=plt.subplots(figsize=(6,3.5),layout="constrained")\nfor name,part in df.groupby("group"):\n    ax.scatter(part["x"],part["y"],label=name); print(name,"r:",round(float(stats.pearsonr(part["x"],part["y"]).statistic),4))\nax.set(xlabel="x",ylabel="y",title="Within groups decreases; pooled association rises"); ax.legend()\nprint("Pooled r:",round(float(stats.pearsonr(df["x"],df["y"]).statistic),4))'),
    "Each group's correlation is-1, while the pooled correlation is positive. The apparent contradiction disappears once you recognise that the summaries condition on different group information.",
    ('# A positive pooled correlation proves x increases y', '# Compare within-group patterns and identify the causal design still needed', "Composition can change association; observing a pattern does not identify an intervention effect."),
    "Draw groups A x[1,2,3], y[1,2,3] and B x[7,8,9], y[7,8,9]; print pooled and group correlations to show stratification need not reverse a pattern.",
    chart('from scipy import stats\nfig,ax=plt.subplots(); groups={"A":([1,2,3],[1,2,3]),"B":([7,8,9],[7,8,9])}\nfor name,(x,y) in groups.items(): ax.scatter(x,y,label=name); print(name,round(float(stats.pearsonr(x,y).statistic),4))\nax.legend(); print("Pooled:",round(float(stats.pearsonr([1,2,3,7,8,9],[1,2,3,7,8,9]).statistic),4))'),
    "For group means10 and30, compare a50/50 composition with90/10. Plot the overall means while holding both group means unchanged.",
    chart('means=np.array([10.,30.]); balanced=float(np.average(means,weights=[50,50])); changed=float(np.average(means,weights=[90,10]))\nfig,ax=plt.subplots(); ax.bar(["50/50 groups","90/10 groups"],[balanced,changed])\nprint(balanced,changed)'),
    "Inspect group composition and within-group relationships; descriptive adjustment alone is not a causal proof.",
    [("Can pooled and within-group associations differ in direction?","Yes","Never","Only with missing values","The mixture of groups can drive the pooled pattern."),
     ("Does checking one stratum variable prove causality?","No","Always","Only if every r agrees","Other confounding and design limitations may remain.")])

IRIS_RAW=(ROOT/"docs"/"python-week33"/"iris.data").read_bytes().decode("utf-8")
CORE='''
from scipy import stats
import csv
import io

FEATURES=["sepal_length_cm","sepal_width_cm","petal_length_cm","petal_width_cm"]
SPECIES=["Iris-setosa","Iris-versicolor","Iris-virginica"]

def read_iris(text):
    rows=[row for row in csv.reader(io.StringIO(text),strict=True) if row]
    if not rows or len(rows)>10000 or any(len(row)!=5 for row in rows):
        raise ValueError("Expected1–10000 five-field Iris rows")
    df=pd.DataFrame(rows,columns=FEATURES+["species"])
    if not df["species"].isin(SPECIES).all(): raise ValueError("Unknown species")
    for col in FEATURES:
        values=pd.to_numeric(df[col],errors="raise")
        if not (np.isfinite(values)&values.gt(0)&values.le(100)).all():
            raise ValueError("Need finite positive measurements<=100cm")
        df[col]=values.astype(float)
    df.insert(0,"row_id",np.arange(1,len(df)+1))
    return df

def analyse(df):
    for name in SPECIES:
        sample=df.loc[df["species"].eq(name),"sepal_length_cm"]
        if len(sample)<3 or sample.std(ddof=1)<=0: raise ValueError("Need variable groups of at least3")
    a=df.loc[df["species"].eq(SPECIES[0]),"sepal_length_cm"].to_numpy()
    b=df.loc[df["species"].eq(SPECIES[1]),"sepal_length_cm"].to_numpy()
    welch=stats.ttest_ind(a,b,equal_var=False,alternative="two-sided",nan_policy="raise")
    ci=welch.confidence_interval(0.95)
    band=np.where(df["sepal_width_cm"].ge(3.0),"wide","narrow")
    table=pd.crosstab(df["species"],band).reindex(index=SPECIES,columns=["narrow","wide"],fill_value=0)
    if (table.sum(axis=0)==0).any(): raise ValueError("Empty contingency margin")
    chi=stats.chi2_contingency(table.to_numpy(),correction=False)
    if (chi.expected_freq<5).any(): raise ValueError("Sparse expectations: choose a suitable method before testing")
    x=df["petal_length_cm"].to_numpy(); y=df["sepal_length_cm"].to_numpy()
    if np.ptp(x)==0 or np.ptp(y)==0: raise ValueError("Need varying regression coordinates")
    fit=stats.linregress(x,y)
    result={"n":len(df),"species_counts":{k:int(v) for k,v in df.groupby("species").size().items()},
        "welch":{"contrast":"setosa minus versicolor mean sepal length, cm","n_a":len(a),"n_b":len(b),
            "difference_cm":float(a.mean()-b.mean()),"t":float(welch.statistic),"df":float(welch.df),
            "p_raw":float(welch.pvalue),"p_bonferroni_2":min(1.,2*float(welch.pvalue)),
            "marginal_95_ci_cm":[float(ci.low),float(ci.high)]},
        "chi_square":{"threshold_cm":3.0,"chi2":float(chi.statistic),"df":int(chi.dof),
            "minimum_expected":float(chi.expected_freq.min()),"p_raw":float(chi.pvalue),
            "p_bonferroni_2":min(1.,2*float(chi.pvalue)),
            "cramers_v":float(np.sqrt(chi.statistic/(len(df)*min(table.shape[0]-1,table.shape[1]-1))))},
        "descriptive_fit":{"x":"petal length, cm","y":"sepal length, cm", "slope":float(fit.slope),
            "intercept":float(fit.intercept),"pearson_r":float(fit.rvalue),"in_sample_r_squared":float(fit.rvalue**2),
            "spearman_rho":float(stats.spearmanr(x,y).statistic),
            "within_species_pearson":{name:float(stats.pearsonr(part["petal_length_cm"],part["sepal_length_cm"]).statistic)
                for name,part in df.groupby("species")}}}
    return result,table,chi.expected_freq

def overview(df,result,table):
    fig,axs=plt.subplots(2,2,figsize=(10,8),layout="constrained")
    edges=np.histogram_bin_edges(df["sepal_length_cm"],bins=15)
    for name,part in df.groupby("species"):
        short=name.replace("Iris-","")
        axs[0,0].hist(part["sepal_length_cm"],bins=edges,histtype="step",label=short)
        axs[1,1].scatter(part["petal_length_cm"],part["sepal_length_cm"],label=short,s=18)
    axs[0,0].set(title="Recorded sepal-length distributions",xlabel="Sepal length (cm)",ylabel="Plants"); axs[0,0].legend(fontsize=8)
    axs[0,1].boxplot([df.loc[df["species"].eq(s),"sepal_length_cm"] for s in SPECIES],tick_labels=[s.replace("Iris-","") for s in SPECIES])
    axs[0,1].set(title="All three recorded species",ylabel="Sepal length (cm)")
    axs[1,0].imshow(table.to_numpy(),cmap="Blues")
    axs[1,0].set(xticks=[0,1],xticklabels=["Width<3cm","Width>=3cm"],yticks=[0,1,2],yticklabels=[s.replace("Iris-","") for s in SPECIES],title="Observed counts; expected counts supplied")
    for (row,col),value in np.ndenumerate(table.to_numpy()): axs[1,0].text(col,row,str(value),ha="center",va="center",color="white" if value>table.to_numpy().max()/2 else "black")
    fit=result["descriptive_fit"]; x=np.array([df["petal_length_cm"].min(),df["petal_length_cm"].max()])
    axs[1,1].plot(x,fit["intercept"]+fit["slope"]*x,color="black",linestyle="--",label="Pooled OLS")
    axs[1,1].set(title="Pooled fit mixes species; not a causal effect",xlabel="Petal length (cm)",ylabel="Sepal length (cm)")
    fig.suptitle(f"UCI Iris: {len(df)} recorded plants; conditional exploratory analysis")
    return fig
'''

CAPSTONE_SETUP=clean(CORE)+'\ndf=read_iris('+repr(IRIS_RAW)+')\n'

lesson(5,"5. Real-data capstone: an auditable Iris statistics report",
    "Describe a real dataset, run a declared two-test family and report associations with honest limits.",
    [("UCI Iris; source and licence", "This is R.A.Fisher's historical Iris dataset distributed by UCI:150 plant records, four measurements in centimetres and three species. The supplied iris.data snapshot is CC BY4.0 with attribution in SOURCE.md; row IDs are generated source-row labels, not original specimen IDs."),
     ("Exploratory two-test teaching family", "The script declares two comparisons: Welch setosa-versicolor mean sepal length, and species versus sepal width>=3cm association. Bonferroni adjusts this two-test family. These are reproducible teaching choices, not a claim of a preregistered confirmatory study."),
     ("Cramer's V; conditional inference", "Cramer's V=sqrt(chi-square/(N*min(rows-1,columns-1))) describes table association magnitude. It is not a causal effect. Test p-values and intervals remain conditional on independence/model assumptions that a historical file cannot prove.")],
    "First inspect what each row means, the units, species counts and whether fields are known. Retain identical measurement rows: different plants can share rounded measurements, so equal values are not proof of duplicate specimens. "
    "The UCI page notes historical discrepancies in two setosa records. This project preserves the downloaded iris.data bytes rather than silently mixing corrections from another version; SOURCE.md records its hash and that limitation. "
    "The report supplies descriptive statistics, distributions, a mean difference with a marginal95% interval, a contingency table with expected counts, both raw/Bonferroni p-values, and a descriptive regression/correlation study. "
    "The width threshold is a stated teaching choice, not a natural species boundary or an optimised discovery. Pooled regression mixes species, so its slope is not a growth effect or a guaranteed predictor for another population. "
    "The historical collection is not documented here as a random sample of a specified modern target population. Treat inferential numbers as conditional demonstrations; no causal or general-population guarantee follows. "
    "Read the code in stages: validate records, calculate the two declared comparisons, preserve their effects and assumptions, then draw. The downloadable statistics_report.py writes seven files to a fresh output bundle and includes interpretation.txt with these limits. Your existing Day7 Review & rest reuses all56 practice prompts.",
    'df=read_iris(local_text)\nresult,table,expected=analyse(df)\nfig=overview(df,result,table)',
    chart(CAPSTONE_SETUP+'result,table,expected=analyse(df)\nfig=overview(df,result,table)\nprint("Plant counts:",result["species_counts"])\nprint("Setosa-versicolor cm:",round(result["welch"]["difference_cm"],3))\nprint("Minimum expected:",round(result["chi_square"]["minimum_expected"],3))\nprint("Pooled descriptive R squared:",round(result["descriptive_fit"]["in_sample_r_squared"],4))'),
    "The two-test family is separate from the descriptive coefficient exploration. A model produces numbers even when its assumptions are not established; the report therefore keeps those assumptions and the historical-source warning next to its results.",
    ('# Remove identical feature rows, optimise a width threshold and publish only the best p', '# Preserve original records, declare the teaching threshold and report the full test family', "Value equality is not identity; exploratory selection and source-version changes need disclosure."),
    "Reproduce the report and print both raw and Bonferroni-adjusted p-values in scientific notation so tiny values are not presented as exact zero.",
    chart(CAPSTONE_SETUP+'result,table,expected=analyse(df)\nfig=overview(df,result,table)\nfor name in ["welch","chi_square"]:\n    print(name,"raw",format(result[name]["p_raw"],".3g"),"adjusted",format(result[name]["p_bonferroni_2"],".3g"))'),
    "Compare pooled Pearson r with each species-specific r and print their values. Keep the report descriptive; do not select the strongest one as a causal answer.",
    chart(CAPSTONE_SETUP+'result,table,expected=analyse(df)\nfig=overview(df,result,table)\nprint("Pooled:",round(result["descriptive_fit"]["pearson_r"],4))\nprint("Within species:",{k:round(v,4) for k,v in result["descriptive_fit"]["within_species_pearson"].items()})'),
    "Week33 mastery: defined units and denominators, model-aware distributions/probability, design-aware sampling, correctly interpreted intervals/tests and a reproducible report with effects and limits.",
    [("What is an Iris row in this source?","A recorded plant","A study session","A species average","UCI describes instances as plants."),
     ("Should equal rounded measurements automatically be deduplicated?","No; values are not specimen identity","Always","Only in setosa","Different plants may share the same feature values."),
     ("What direction is the capstone mean contrast?","Setosa minus versicolor sepal length","Always absolute difference","Virginica minus pooled mean","The effect sign and interval follow the specified order."),
     ("What is the teaching table threshold?","Sepal width at least3cm","Petal length above5cm","The smallest p found among100 thresholds","The stated threshold is not silently optimised."),
     ("How many tests are in the adjusted teaching family?","Two","Every plot is another independent test","One","Welch and contingency association form the declared family."),
     ("Is the reported95% Welch interval simultaneous family coverage?","No; it is marginal","Always","Only if p is tiny","Adjusted p-values do not change the interval procedure."),
     ("Does a p-value measure P(null true)?","No","Always","Only with150 rows","It is a null-model tail probability under the method's assumptions."),
     ("Is an SD the same as mean SE?","No","Always","Only for percentages","SD concerns observations; SE concerns an estimator under a design."),
     ("Does the CLT make raw observations normal?","No","Always","Once n reaches30","It concerns suitable sums/means under conditions."),
     ("Can a large R squared establish a causal effect?","No","Always","Only in real datasets","Fit quality is not causal identification."),
     ("Where are the source version and licence recorded?","SOURCE.md and the retained iris.data snapshot","Only a random seed","Inside a user password","The dataset provenance is separate from analysis choices."),
     ("Where should the second report run be saved?","A new output bundle","Over the raw source","Silently over the first report","Inputs and previous artifacts are preserved.")])

PROJECT='''"""Week33 local UCI Iris statistics; conditional exploratory teaching report."""
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
''' + clean(CORE) + '''
def publish(source,destination):
    source=Path(source); destination=Path(destination)
    if destination.exists() or not destination.parent.is_dir(): raise ValueError("Choose a new bundle in an existing parent")
    raw=source.read_bytes()
    if len(raw)>1024*1024: raise ValueError("Learning input exceeds1MiB")
    df=read_iris(raw.decode("utf-8-sig")); result,table,expected=analyse(df)
    result["source_sha256"]=hashlib.sha256(raw).hexdigest()
    result["source_url"]="https://archive.ics.uci.edu/dataset/53/iris"
    result["analysis_status"]="Exploratory conditional teaching analysis; no random-target-population or causal guarantee"
    notes=["UCI IRIS — CONDITIONAL EXPLORATORY STATISTICS REPORT",
        "Source: Fisher,R.(1936). Iris [Dataset]. UCI. https://doi.org/10.24432/C56C76 ; CC BY4.0.",
        f"Rows:{len(df)}; counts:{result['species_counts']}; four measurements in centimetres, no unknown fields accepted.",
        "Identical feature rows are retained: measurement equality does not identify duplicate specimens.",
        "The supplied historical iris.data snapshot retains the UCI-noted record discrepancies. Source hash:"+result["source_sha256"],
        "Historical collection is not established here as a random sample of a modern target; independence/model assumptions remain conditional.",
        "Test1: Welch two-sided setosa-minus-versicolor mean sepal length, not a causal intervention.",
        f"Difference cm:{result['welch']['difference_cm']:.6g}; marginal95% CI:{result['welch']['marginal_95_ci_cm']}; raw p:{result['welch']['p_raw']:.6g}; Bonferroni2 p:{result['welch']['p_bonferroni_2']:.6g}.",
        "Test2: species versus sepal width>=3cm, a fixed teaching threshold, Pearson chi-square with correction=False.",
        f"Minimum expected count:{result['chi_square']['minimum_expected']:.6g}; Cramer's V:{result['chi_square']['cramers_v']:.6g}; raw p:{result['chi_square']['p_raw']:.6g}; Bonferroni2 p:{result['chi_square']['p_bonferroni_2']:.6g}.",
        "Family: exactly two teaching tests; adjustment does not repair bias or make the marginal interval simultaneous.",
        "Correlations and OLS are descriptive exploration, not additional confirmatory significance claims. Within-species coefficients are retained in analysis.json.",
        f"Pooled slope:{result['descriptive_fit']['slope']:.6g} cm/cm; in-sample R squared:{result['descriptive_fit']['in_sample_r_squared']:.6g}.",
        "R squared is not percent correct predictions. Species composition, measurement version and source design limit interpretation.",
        "Do not report tiny positive p-values as exact zero, tune thresholds silently, remove inconvenient records, or infer causation."]
    with TemporaryDirectory(prefix="studyhub-statistics-",dir=destination.parent) as temp:
        folder=Path(temp); fig=overview(df,result,table)
        try: fig.savefig(folder/"overview.png",dpi=150,facecolor="white")
        finally: plt.close(fig)
        df.groupby("species")[FEATURES].agg(["count","mean","median","std","min","max"]).to_csv(folder/"descriptive.csv",lineterminator="\\n")
        table.to_csv(folder/"contingency.csv",lineterminator="\\n")
        pd.DataFrame(expected,index=table.index,columns=table.columns).to_csv(folder/"expected.csv",lineterminator="\\n")
        fit=result["descriptive_fit"]; regression=df[["row_id","species","petal_length_cm","sepal_length_cm"]].copy()
        regression["fitted_sepal_cm"]=fit["intercept"]+fit["slope"]*regression["petal_length_cm"]
        regression["residual_cm"]=regression["sepal_length_cm"]-regression["fitted_sepal_cm"]
        regression.to_csv(folder/"regression_rows.csv",index=False,lineterminator="\\n")
        (folder/"analysis.json").write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
        (folder/"interpretation.txt").write_text("\\n".join(notes)+"\\n",encoding="utf-8")
        os.rename(folder,destination)
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description="Week33 local Iris statistics report")
    parser.add_argument("source"); parser.add_argument("destination"); args=parser.parse_args(argv)
    try: result=publish(args.source,args.destination)
    except (ValueError,OSError,csv.Error) as error: parser.exit(1,"Statistics report stopped: "+str(error)+"\\n")
    print("Published7 files; recorded plants",result["n"],"declared tests",2)
    return 0

if __name__=="__main__": raise SystemExit(main())
'''


def write():
    target=ROOT/"study-hub.html"; original=target.read_bytes().decode("utf-8")
    start=original.index("const DAY_TEACH = {"); end=original.index("\n};\n\nconst REST_DAY",start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS): raise RuntimeError("Week33 already exists; refusing overwrite")
    for future,destination,picture in JOBS:
        text,png=future.result();destination["v" if destination["t"]=="out" else "out"]=text
        if picture is not None:
            if not png: raise RuntimeError("Missing example picture")
            picture["src"]="data:image/png;base64,"+base64.b64encode(png).decode("ascii")
    POOL.shutdown()
    DAYS["33.0"]["parts"][0]["sections"].insert(3,section("sh",'python -m pip install "numpy>=2,<3" "pandas>=3,<4" "matplotlib>=3.10,<3.11" "scipy>=1.15,<2"',note="Install once in your local practice environment. Initial installation needs internet; lessons, embedded pictures, simulations and the supplied real-data project work offline afterward. Outputs verified with NumPy2.3.5, pandas3.0.1, Matplotlib3.10.9 and SciPy1.18.1. Python executes locally, outside the website."))
    DAYS["33.5"]["parts"][4]["sections"].append(section("sh","python statistics_report.py iris.data statistics-run-01\npython statistics_report.py --help",note="From docs/python-week33. Use statistics-run-02 next time. Supplied files: statistics_report.py, iris.data, SOURCE.md and README.md. The source is real public botanical data, not personal StudyHub data."))
    DAYS["33.5"]["parts"][4]["sections"].append(section("p","Primary references: https://docs.scipy.org/doc/scipy/reference/stats.html · https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html · https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html · https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html · https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf · https://archive.ics.uci.edu/dataset/53/iris. Original explanations, worked code, exercises and actual chart pictures are embedded for offline study."))
    addition="\n".join(json.dumps(k)+": "+json.dumps(v,ensure_ascii=False,indent=2)+"," for k,v in DAYS.items()).replace("</","<\\/")
    prefix=original[:end].rstrip()
    if not prefix.endswith(","): prefix+="," 
    folder=ROOT/"docs"/"python-week33";folder.mkdir(exist_ok=True)
    (folder/"statistics_report.py").write_text(PROJECT,encoding="utf-8",newline="\n")
    temporary=target.with_suffix(".html.tmp");temporary.write_bytes((prefix+"\n"+addition+original[end:]).encode("utf-8"));temporary.replace(target)
    print("Added Week33:6 days,28 parts,56 practice prompts,66 explained quiz questions,84 executed outputs and28 embedded chart pictures; all application/storage code unchanged.")


if __name__=="__main__":
    try:
        write()
    except BaseException:
        POOL.shutdown(wait=False,cancel_futures=True)
        raise


