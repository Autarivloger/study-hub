"""Author Week 30 additively; execute each output in an isolated practice folder."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
DAYS = {f"30.{d}": {"parts": []} for d in range(6)}
EXECUTED = 0


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def output(code):
    global EXECUTED
    with tempfile.TemporaryDirectory(prefix="studyhub-w30-") as folder:
        run = subprocess.run([sys.executable, "-c", clean(code)], cwd=folder,
                             capture_output=True, encoding="utf-8", timeout=35,
                             env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if run.returncode:
        raise RuntimeError(run.stderr + "\n" + code)
    EXECUTED += 1
    return run.stdout.replace("\r\n", "\n").rstrip()


def s(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def add(day, title, goal, concepts, explanation, syntax, code, walk, mistake,
        task, solution, challenge, challenge_code, key, quizzes):
    parts = DAYS[f"30.{day}"]["parts"]
    index = len(parts)
    questions = []
    for n, (q, answer, wrong1, wrong2, why) in enumerate(quizzes):
        rotation = (index + n) % 3
        options = [answer, wrong1, wrong2]
        for _ in range(rotation):
            options.insert(0, options.pop())
        questions.append({"q": q, "options": options, "correct": rotation, "why": why})
    parts.append({"title": title, "sections": [
        s("h", title), s("key", "Learning objective: " + goal),
        *[s("new", name, note=note) for name, note in concepts],
        s("p", explanation), s("syn", syntax, note="Pattern first; run the complete example below."),
        s("code", clean(code)), s("out", output(code)), s("p", walk),
        s("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        s("ex", task, practiceId=f"30.{day}.{index}.build"),
        s("sol", code=clean(solution), out=output(solution), why="Build check: " + key),
        s("ex", "Mini challenge: " + challenge, practiceId=f"30.{day}.{index}.challenge"),
        s("sol", code=clean(challenge_code), out=output(challenge_code), why="Challenge check: " + key),
        s("try", q=quizzes[0][0], code="# Predict and explain before revealing.",
          a=quizzes[0][1], why=quizzes[0][4]),
        s("checkpoint", lesson={"id": f"course:30.{day}.{index}", "quiz": questions}), s("key", key),
    ]})


def lesson(day, title, goal, concepts, explanation, syntax, example, walk,
           wrong, right, reason, task, solution, challenge, challenge_code,
           takeaway, questions):
    """Keep the existing section renderer and durable practice/quiz identifiers."""
    add(day, title, goal, concepts, explanation, syntax, example, walk,
        (wrong, right, reason), task, solution, challenge, challenge_code,
        takeaway, questions)


SALES = '''
import pandas as pd
sales = pd.DataFrame({
    "region": ["NP", "JP", "NP", "JP", "NP", "JP"],
    "product": ["Book", "Book", "Pen", "Pen", "Book", "Pen"],
    "customer": ["A", "B", "A", "C", "D", "B"],
    "units": [2, 1, 3, 2, 1, 1],
    "price": [100, 100, 20, 20, 100, 20],
})
sales["revenue"] = sales["units"] * sales["price"]
'''

lesson(0, "1. Split, calculate, combine: your first groupby",
    "State the input row meaning and summarize revenue for each region.",
    [("Grain", "Grain means what one row represents. Here each row is a sale line, not a unique customer or order. A group summary changes the grain to one row per region."),
     ("GroupBy; split-apply-combine", "groupby splits rows with matching keys, applies a calculation to each group, and combines results. Creating a GroupBy object alone does not compute a summary."),
     ("as_index=False; sort", "as_index=False keeps group labels as ordinary columns. sort=True sorts group keys; it does not sort transactions by date or revenue.")],
    "Weeks28–29 taught selection and cleaning. Now ask a precise question: how much revenue is represented by each region? "
    "Start by defining a row: one product line purchased by a customer. Multiply units by price on each row, then sum those amounts per region. "
    "groupby('region')['revenue'] selects exactly the measurement to aggregate. Do not sum ID columns merely because they contain numbers. "
    "Grouping is like putting receipts into labeled boxes and calculating a total inside each box. The resulting two rows summarize six observations. "
    "These examples use a single fictional currency; adding unlike currencies would require an explicit conversion policy.",
    'sales.groupby("region", as_index=False)["revenue"].sum()',
    SALES + '''
summary = sales.groupby("region", as_index=False, sort=True)["revenue"].sum()
print(summary.to_dict(orient="records"))
print("Same total:", int(summary["revenue"].sum()) == int(sales["revenue"].sum()))
''',
    "Read left to right: split by region, select revenue, sum, keep labels as columns. NP contains 200+60+100; JP contains100+40+20. The conservation check is a useful guard against omitted groups.",
    'sales.groupby("region").sum()  # sum every numeric column without a question',
    'sales.groupby("region")["revenue"].sum()',
    "IDs, prices and quantities have different meanings. Choose the metric before choosing the function.",
    "Using the sample sales, report total units per region as ordinary columns.",
    SALES + 'print(sales.groupby("region", as_index=False)["units"].sum().to_dict(orient="records"))',
    "Calculate revenue by product and prove product totals add to the original revenue.",
    SALES + '''
totals = sales.groupby("product")["revenue"].sum()
print(totals.to_dict())
print(int(totals.sum()), int(sales["revenue"].sum()))
''',
    "Know the grain, choose a meaningful measurement, and reconcile grouped totals with their source.",
    [("What does one row in the regional summary represent?", "One region", "One customer", "One product line", "Aggregation changes the row meaning."),
     ("Does constructing a GroupBy alone produce totals?", "No; request a calculation", "Yes, always sum", "Yes, always mean", "The grouping describes a calculation to perform.")])

lesson(0, "2. Count rows, observed values and unique people separately",
    "Choose size, count or nunique from the actual denominator.",
    [("size versus count", "size counts rows in each group. count counts nonmissing values in the selected column; it can give different counts for different columns."),
     ("nunique; dropna=False", "nunique counts distinct observed values by default. groupby(dropna=False) retains a group for missing keys; this is separate from missing measurements."),
     ("sum(min_count=1)", "A group whose measurements are all missing otherwise commonly sums to zero. min_count=1 requires one observed measurement, preserving an unknown total as missing.")],
    "How many transactions, how many known scores, and how many distinct learners are three different questions. "
    "A customer who bought twice contributes two rows but only one distinct customer. A row with an unknown measurement still exists. "
    "Default groupby drops rows whose grouping key is missing, which can shrink the represented population without changing your code's row count visibly. "
    "Decide whether unknown categories should be retained, then reconcile size totals. Missing measurements are a separate decision: an unknown total is not observed zero.",
    'g = df.groupby("region", dropna=False)\ng.size()\ng["score"].count()\ng["customer"].nunique()',
    '''
import pandas as pd
df = pd.DataFrame({"region": ["NP", "NP", "JP", None],
                   "customer": ["A", "A", "B", "C"], "score": [80, None, None, 70]})
g = df.groupby("region", dropna=False, sort=False)
report = pd.DataFrame({"rows": g.size(), "known_scores": g["score"].count(),
                       "people": g["customer"].nunique(), "score_total": g["score"].sum(min_count=1)})
print(report.to_string())
print("Rows accounted:", int(g.size().sum()) == len(df))
''',
    "NP has two rows, one known score and one person. JP has one row but zero known scores, so its score total remains missing. The missing-region row is retained because dropna=False applies to group keys.",
    'g["score"].count()  # label this as all transactions', 'g.size()  # all transaction rows',
    "count excludes missing scores, not rows that failed to happen.",
    "For customers A,A,B in NP with values10,missing,20, print rows, known values and distinct customers.",
    '''
import pandas as pd
df = pd.DataFrame({"region": ["NP"]*3, "customer": ["A", "A", "B"], "value": [10, None, 20]})
g = df.groupby("region")
print(g.size().to_dict(), g["value"].count().to_dict(), g["customer"].nunique().to_dict())
''',
    "Keep an unknown-region row in a units report and verify all3 rows are counted.",
    '''
import pandas as pd
df = pd.DataFrame({"region": ["NP", None, "JP"], "units": [2, 3, 1]})
g = df.groupby("region", dropna=False)
print("All rows:", int(g.size().sum()))
print("All units:", int(g["units"].sum().sum()))
''',
    "Write the denominator in words before calculating it; unknown does not mean zero.",
    [("Which counts every row per group?", "size", "count on a nullable score", "nunique", "size counts observations regardless of selected value missingness."),
     ("What retains missing grouping keys?", "groupby(dropna=False)", "fill every value with zero", "sort=False alone", "This argument controls group-key omission.")])

lesson(0, "3. Two grouping keys and categorical combinations",
    "Read one-row-per-region-and-product results and distinguish observed from possible groups.",
    [("Multiple grouping keys; MultiIndex", "A list of keys groups by their combinations. With as_index=True, combinations form a MultiIndex; as_index=False returns regular key columns."),
     ("observed=True", "For categorical grouping keys, observed=True reports combinations that actually occur. observed=False can include unused categories/combinations. Set the choice explicitly.")],
    "A total per region hides which products earned it. Add product as a second grouping key: the result now has one row per observed region/product pair. "
    "Reading the grain aloud prevents a common mistake: assuming each row is still a transaction and counting summary rows as sales. "
    "Categorical columns also carry a declared universe of possible labels, including unused ones. Observed groups and a complete planning grid answer different questions. "
    "An absent group is not automatically proof of zero activity; your source may be incomplete. Use an explicit completeness contract before filling absent combinations.",
    'sales.groupby(["region","product"], as_index=False, observed=True)["revenue"].sum()',
    SALES + '''
sales["product"] = pd.Categorical(sales["product"], categories=["Book", "Pen", "Bag"])
observed = sales.groupby(["region", "product"], as_index=False, observed=True)["revenue"].sum()
print(observed.to_dict(orient="records"))
print("Observed rows:", len(observed))
print("Possible combinations:", len(sales.groupby(["region", "product"], observed=False).size()))
''',
    "Bag exists in the declared category list but has no sale. observed=True retains four real region/product combinations; the two-region/three-product grid has six possible cells.",
    'Treat len(grouped_summary) as transaction count', 'Use sales.groupby(keys).size() for row counts',
    "A summary row represents a group, not the observations inside it.",
    "Group the sample by region/product and print units and revenue totals.",
    SALES + 'print(sales.groupby(["region","product"], as_index=False)[["units","revenue"]].sum().to_dict(orient="records"))',
    "Produce the same two-key revenue report with a MultiIndex, then turn its keys into columns.",
    SALES + '''
indexed = sales.groupby(["region","product"])["revenue"].sum()
print(indexed.index.names)
print(indexed.reset_index().columns.tolist())
''',
    "Every extra key changes the summary grain. Declare observed versus possible combinations deliberately.",
    [("What is the grain after grouping by region/product?", "One observed key pair", "One customer", "One transaction", "Both keys identify a summary row."),
     ("What does observed=True mean for categorical grouping?", "Only occurring groups", "All declared combinations", "Only numeric values", "It controls whether unused categorical groups appear.")])

lesson(0, "4. Eight questions from one small sales table",
    "Translate business questions into meaningful, reconcilable grouped calculations.",
    [("Weighted average unit price", "Total revenue divided by total units weights prices by purchased quantities. The simple mean of sale-line prices gives each line equal weight, which answers a different question."),
     ("get_group; idxmax", "get_group selects one named group for inspection. idxmax returns the label of the first maximum in a Series; define how ties should be handled before calling it a unique winner.")],
    "Practice question-first thinking. Ask revenue, units, sale-line count, unique customers, mean line revenue, largest line revenue, revenue per product within region, and average paid price per unit. "
    "Those are eight reports, but they do not need eight unrelated techniques. Choose the key and measurement, then the reducer. "
    "Revenue divided by units is a weighted unit price; mean(revenue) is average line value. None of these proves profit because costs are absent. "
    "Do not call a line an order: an order may contain multiple product lines. Inspect NP with get_group and manually add its three receipts before trusting the output.",
    'g = sales.groupby("region")\ng["revenue"].sum() / g["units"].sum()',
    SALES + '''
g = sales.groupby("region")
print("1 Revenue:", g["revenue"].sum().to_dict())
print("2 Units:", g["units"].sum().to_dict())
print("3 Sale lines:", g.size().to_dict())
print("4 Customers:", g["customer"].nunique().to_dict())
print("5 Mean line value:", g["revenue"].mean().round(2).to_dict())
print("6 Largest line:", g["revenue"].max().to_dict())
print("7 Region/product:", sales.groupby(["region","product"])["revenue"].sum().to_dict())
print("8 Weighted unit price:", (g["revenue"].sum()/g["units"].sum()).round(2).to_dict())
''',
    "The same split supports several reducers. np revenue360 over6units yields60 per unit; jp revenue160 over4units yields40. These differ from both the mean line revenue and the unweighted mean price.",
    'sales.groupby("region")["price"].mean()  # claim weighted unit price',
    'g["revenue"].sum() / g["units"].sum()',
    "Mean price weights sale lines equally, whereas the desired statistic weights units.",
    "Report unique customers and total revenue per product; explain why their units differ.",
    SALES + '''
g = sales.groupby("product")
print("People:", g["customer"].nunique().to_dict())
print("Revenue:", g["revenue"].sum().to_dict())
''',
    "Find the highest-revenue region, inspect its customer list, and note that idxmax selects the first tied label.",
    SALES + '''
g = sales.groupby("region")
winner = g["revenue"].sum().idxmax()
print("Top region:", winner)
print("Its people:", sorted(g.get_group(winner)["customer"].unique().tolist()))
''',
    "Define numerator, denominator and row meaning. Revenue is not profit, and lines are not automatically orders.",
    [("Which computes weighted paid unit price?", "Revenue total / units total", "Mean line price always", "Mean revenue", "The ratio weights by purchased quantities."),
     ("Does revenue alone prove profit?", "No; costs are absent", "Always", "Only with groupby", "Profit requires a cost definition and data.")])

lesson(1, "1. agg: several calculations with clear names",
    "Produce a named summary whose columns describe their units and calculations.",
    [("agg; named aggregation", "agg requests one or several reductions. keyword_name=('input_column','function') gives each output column a readable name and explicitly selects its source."),
     ("size versus nunique reminder", "An aggregation of size counts sale lines; nunique(customer) counts distinct people. Label them accordingly.")],
    "Day1 repeated groupby calculations to make each question visible. Day2 combines them into a report. "
    "The output name goes on the left, and the input column/function tuple goes on the right. This is called named aggregation; it produces ordinary, readable column names. "
    "A list of functions can create multiple column levels instead, useful for exploration but harder to export. Prefer a report with names such as revenue_total, units_total and customers. "
    "Do not use 'count' ambiguously: a missing customer token makes customer.count differ from row count. Include a short report dictionary saying what each metric means.",
    'sales.groupby("region", as_index=False).agg(revenue_total=("revenue","sum"), customers=("customer","nunique"))',
    SALES + '''
summary = sales.groupby("region", as_index=False).agg(
    revenue_total=("revenue", "sum"), units_total=("units", "sum"),
    sale_lines=("revenue", "size"), customers=("customer", "nunique"),
    mean_line_revenue=("revenue", "mean"))
print(summary.round(2).to_dict(orient="records"))
''',
    "Each tuple points to one column and a reducer. The result keeps region as a column and each metric gets a single name. Rounding here is display formatting, not a change to stored measurements.",
    'g.agg(revenue_total=("units", "sum"))', 'g.agg(revenue_total=("revenue", "sum"))',
    "A nice label cannot correct a calculation on the wrong source column.",
    "Create a product report with line count, revenue total and maximum line revenue using named aggregation.",
    SALES + '''
report = sales.groupby("product", as_index=False).agg(lines=("revenue","size"),
    revenue_total=("revenue","sum"), max_line=("revenue","max"))
print(report.to_dict(orient="records"))
''',
    "Apply sum and mean to revenue per region as a list; inspect the resulting column names.",
    SALES + '''
report = sales.groupby("region")["revenue"].agg(["sum", "mean"])
print(report.columns.tolist())
print(report.round(2).to_dict(orient="index"))
''',
    "Named aggregation makes the measurement, operation and output label reviewable.",
    [("In total=('revenue','sum'), which names the output?", "total", "revenue", "sum", "The keyword supplies the output column name."),
     ("Which reducer counts distinct customers?", "nunique", "sum", "size", "Repeated purchase lines should not multiply unique people.")])

lesson(1, "2. transform: give each row its group's context",
    "Add group totals and revenue shares without collapsing the original table.",
    [("transform", "transform produces a result aligned to original rows. A scalar group total is repeated onto every member row; aggregation instead collapses a group to one summary."),
     ("Aligned division; where", "Series arithmetic aligns by row labels. where(condition) keeps values only where a condition holds, making a zero denominator missing rather than manufacturing a percentage.")],
    "Sometimes each transaction needs context: what proportion of its region's revenue did it contribute? "
    "A two-row aggregate cannot simply be assigned to a six-row transaction column; pandas aligns index labels, not your intention. "
    "transform('sum') repeats the regional total on each original row. Then each revenue divides by the appropriate total. "
    "Check that shares sum to100% within groups with a positive total. For zero totals, the share is undefined; do not quietly substitute100 or divide by zero. "
    "Negative refunds change the interpretation of shares, so this example explicitly uses nonnegative sale revenue.",
    'total = sales.groupby("region")["revenue"].transform("sum")\nsales["share_pct"] = 100 * sales["revenue"] / total.where(total.ne(0))',
    SALES + '''
total = sales.groupby("region")["revenue"].transform("sum")
sales["share_pct"] = 100 * sales["revenue"] / total.where(total.ne(0))
print(sales[["region","revenue","share_pct"]].round(2).to_dict(orient="records"))
print("Share totals:", sales.groupby("region")["share_pct"].sum().round(2).to_dict())
''',
    "All NP rows receive360 as their denominator, all JP rows receive160. Six rows remain six rows; the group calculation enriches them rather than replacing them.",
    'sales["total"] = sales.groupby("region")["revenue"].sum()',
    'sales["total"] = sales.groupby("region")["revenue"].transform("sum")',
    "A group-indexed summary does not align with the transaction index.",
    "Add regional mean line revenue and each row's difference from that mean.",
    SALES + '''
sales["region_mean"] = sales.groupby("region")["revenue"].transform("mean")
sales["difference"] = sales["revenue"] - sales["region_mean"]
print(sales[["region","difference"]].round(2).to_dict(orient="records"))
''',
    "Calculate shares for group A values0,0 and group B values10,30. Keep A shares missing.",
    '''
import pandas as pd
df = pd.DataFrame({"group": ["A","A","B","B"], "value": [0,0,10,30]})
total = df.groupby("group")["value"].transform("sum")
share = 100 * df["value"] / total.where(total.ne(0))
print("Missing:", share.isna().tolist())
print("B:", share[df["group"].eq("B")].tolist())
''',
    "Aggregate changes grain; transform preserves rows and alignment. State the zero-denominator policy.",
    [("What shape does transform('sum') normally return?", "One value per original row", "One value per group only", "One scalar for all data", "It aligns group results back to members."),
     ("What is a share with zero group revenue?", "Undefined; handle explicitly", "Always100%", "Always50%", "A zero denominator cannot establish a proportion.")])

lesson(1, "3. filter whole groups; filter rows deliberately",
    "Distinguish group qualification from selecting individual transactions.",
    [("GroupBy.filter", "filter retains all original rows of groups whose predicate returns True. A lambda receives one group's DataFrame and must return a Boolean."),
     ("transform-based mask", "A repeated group total can form a Boolean row mask. It is often simpler than a custom group filter for built-in sums/counts."),
     ("lambda reminder", "lambda g: expression is a small unnamed function from the earlier functions path. Here g is one group, not the whole table.")],
    "Keep all sale lines from regions earning at least300. This differs from keeping individual lines worth300. "
    "No line reaches300, yet NP reaches360 across its three lines. A group filter keeps those three observations together. "
    "For simple built-in calculations, transform plus a mask is clear and often efficient. Use filter when the group predicate needs several aspects of the group's data. "
    "Document that the retained population has changed; group selection can bias a comparison toward larger groups. A report on selected regions is not the total business.",
    'sales.groupby("region").filter(lambda g: g["revenue"].sum() >= 300)',
    SALES + '''
whole_groups = sales.groupby("region").filter(lambda g: g["revenue"].sum() >= 300)
single_rows = sales[sales["revenue"] >= 300]
mask = sales.groupby("region")["revenue"].transform("sum") >= 300
print("Group filter:", whole_groups["revenue"].tolist())
print("Row filter:", single_rows["revenue"].tolist())
print("Same group result:", sales[mask].equals(whole_groups))
''',
    "The predicate sees one region at a time, returns True for NP, and all three NP lines survive. The row condition evaluates each line independently and retains nothing.",
    'sales[sales["revenue"] >= 300]  # regions with total >=300',
    'sales[sales.groupby("region")["revenue"].transform("sum") >= 300]',
    "A row threshold does not test a group's combined total.",
    "Keep all sale lines for products purchased by at least3 distinct customers.",
    SALES + '''
kept = sales.groupby("product").filter(lambda g: g["customer"].nunique() >= 3)
print(kept["product"].tolist())
''',
    "Use transform('size') to keep region/product pairs with at least2 sale lines.",
    SALES + '''
count = sales.groupby(["region","product"])["revenue"].transform("size")
print(sales[count >= 2][["region","product"]].to_dict(orient="records"))
''',
    "Say whether your rule selects groups or observations; report the retained population.",
    [("A group passes filter: what is retained?", "All rows in that group", "Only its largest row", "Only one summary row", "filter returns original member rows."),
     ("Is revenue>=300 on each row equivalent to a regional total threshold?", "No", "Always", "Only when sorted", "Several small lines can jointly exceed the threshold.")])

lesson(1, "4. Reliable rankings and weighted summaries",
    "Calculate an interpretable summary and rank products with a stated tie policy.",
    [("nlargest; stable tie policy", "nlargest returns rows with the largest metric. For a reproducible full ordering, sort by revenue descending and a declared secondary key ascending."),
     ("Ratio of totals versus mean of ratios", "Aggregate numerators and denominators at the required grain before division when you want a weighted rate. Averaging row rates answers a different question.")],
    "Combine the three tools: agg for a compact report, transform for row context, and a sort for ranking. "
    "A rank is meaningless until its scope is named. Top product globally can differ from top product within a region. "
    "For weighted price, sum revenue and units first, divide second; this also makes denominator validation visible. "
    "If products tie, sorting alphabetically is a display policy, not evidence one performed better. Decide whether your report displays one winner or all tied winners. "
    "Avoid a custom apply when named reductions already express your calculation; it makes the result easier to inspect.",
    'report = sales.groupby(["region","product"], as_index=False).agg(revenue=("revenue","sum"), units=("units","sum"))\nreport.sort_values(["region","revenue","product"], ascending=[True,False,True])',
    SALES + '''
report = sales.groupby(["region","product"], as_index=False).agg(
    revenue=("revenue","sum"), units=("units","sum"))
report["weighted_price"] = report["revenue"] / report["units"].where(report["units"].ne(0))
ordered = report.sort_values(["region","revenue","product"], ascending=[True,False,True])
print(ordered.to_dict(orient="records"))
print("One displayed winner:", ordered.groupby("region", sort=False).head(1)[["region","product"]].to_dict(orient="records"))
''',
    "groupby(...).head(1) takes the first ordered row inside each region. Sorting by region, descending revenue and product first establishes exactly which row that is. NP's book wins; JP's book wins here too.",
    'report.groupby("region").head(1)  # assume this is highest revenue',
    'Sort by descending revenue, then select within each region',
    "head follows current row order; it is not an implicit ranking operation.",
    "Return the two highest-revenue products globally, with their unit totals.",
    SALES + '''
report = sales.groupby("product", as_index=False).agg(revenue=("revenue","sum"), units=("units","sum"))
print(report.nlargest(2, "revenue").to_dict(orient="records"))
''',
    "For tied regional product revenues, keep every tied winner using transform('max').",
    '''
import pandas as pd
report = pd.DataFrame({"region": ["NP","NP","JP"], "product": ["A","B","A"], "revenue": [100,100,80]})
top = report.groupby("region")["revenue"].transform("max")
print(report[report["revenue"].eq(top)].to_dict(orient="records"))
''',
    "Choose the grouping scope, ratio denominator and tie policy before presenting a ranking.",
    [("Does groupby.head(1) automatically choose a revenue winner?", "No; sort first", "Always", "Only for strings", "It uses current member order."),
     ("Which keeps all tied maxima within regions?", "Compare revenue with transform('max')", "Take head(1) unsorted", "Drop duplicates by region", "The repeated maximum lets every tied row satisfy the mask.")])

ORDERS = '''
import pandas as pd
lines = pd.DataFrame({"line_id": [1,2,3], "product_id": ["P1","P2","P1"], "customer_id": ["C1","C2","C1"], "units": [2,3,1]})
products = pd.DataFrame({"product_id": ["P1","P2"], "product": ["Book","Pen"], "unit_price": [100,20]})
customers = pd.DataFrame({"customer_id": ["C1","C2"], "region": ["NP","JP"]})
'''

lesson(2, "1. merge: enrich sale lines without changing their grain",
    "Join transaction, product and customer tables with explicit many-to-one contracts.",
    [("Fact and dimension tables", "A fact table contains events or measurements; a dimension supplies one row per lookup key. Here a sale line references one product and one customer."),
     ("merge; on; validate='many_to_one'", "merge matches key values. on names the join key explicitly. many_to_one requires the right lookup key to be unique, while repeated left keys are allowed."),
     ("Foreign key", "A foreign key such as product_id refers to a record in another table. Uniqueness and coverage are different: a lookup can be unique but still omit a referenced ID.")],
    "Yesterday one table already carried prices and regions. Real systems often separate transactions, products and customers. "
    "A transaction knows P1 and C1; lookup tables explain those IDs. Repeat P1 in many lines, but require exactly one product row for P1. "
    "Left joins retain sale lines while adding attributes. Validate each join's cardinality and check indicator coverage before multiplying price by units. "
    "The row grain must remain one sale line. Merely getting a DataFrame with plausible columns is not proof the join is correct. "
    "This toy product price is fixed for the period; real historical revenue should use the recorded transaction price, not today's catalog price.",
    'lines.merge(products, on="product_id", how="left", validate="many_to_one", indicator=True)',
    ORDERS + '''
enriched = lines.merge(products, on="product_id", how="left", validate="many_to_one", indicator=True)
assert enriched["_merge"].eq("both").all()
enriched = enriched.drop(columns="_merge").merge(customers, on="customer_id", how="left", validate="many_to_one", indicator=True)
assert enriched["_merge"].eq("both").all()
enriched["revenue"] = enriched["units"] * enriched["unit_price"]
print(enriched[["line_id","product","region","revenue"]].to_dict(orient="records"))
print("Rows:", len(lines), len(enriched))
''',
    "P1 matches the same Book lookup for line1 and line3. C1 supplies NP for both lines. There are still three rows; the two validation checks prevent duplicate lookup matches and coverage loss.",
    'lines.merge(products)  # infer join columns and trust the result',
    'Name on/how/validate, then check unmatched keys and row accounting',
    "Implicit common columns can become unintended keys as the tables evolve.",
    "Join product names onto sale lines and report line IDs in their original order.",
    ORDERS + '''
out = lines.merge(products[["product_id","product"]], on="product_id", how="left", validate="many_to_one")
print(out[["line_id","product"]].to_dict(orient="records"))
''',
    "Give customers the key name id, then join using left_on/right_on and keep all three lines.",
    ORDERS + '''
lookup = customers.rename(columns={"customer_id":"id"})
out = lines.merge(lookup, left_on="customer_id", right_on="id", how="left", validate="many_to_one")
print(out[["line_id","region"]].to_dict(orient="records"))
''',
    "Explicit keys, unique lookup keys, matched coverage and unchanged event grain make a trustworthy enrichment.",
    [("Which contract fits repeated sale product IDs and unique catalog IDs?", "many_to_one", "one_to_one", "many_to_many only", "Many fact rows can reference one dimension row."),
     ("Does cardinality validation prove all left keys matched?", "No; inspect coverage separately", "Always", "Only for dates", "A unique dimension can still lack a required key.")])

lesson(2, "2. Join types and unmatched-row accounting",
    "Choose left, inner, right or outer by the population you need to represent.",
    [("left; inner; right; outer", "Left retains left keys; right retains right keys; inner retains matching keys; outer represents their union. Duplicate matching keys can still multiply rows."),
     ("indicator; _merge", "indicator=True labels rows as left_only, right_only or both. It diagnoses coverage rather than assuming missing attributes imply an unmatched key."),
     ("suffixes", "Overlapping non-key column names receive suffixes. Choose meaningful names such as _sale and _catalog rather than forgetting which source supplied a value.")],
    "An inner join can remove a valid sale simply because its product is absent from a catalog export. "
    "A left join keeps that fact visible for investigation; an outer join can also reveal unused catalog records. "
    "Coverage is not just len(out)==len(left): duplicate right rows can add rows while unmatched left keys remove rows, masking each other. "
    "Use cardinality validation and the indicator together. Report unmatched IDs and choose whether to stop or quarantine them. Do not replace an unknown price with zero and call it a valid sale.",
    'left.merge(right, on="id", how="outer", indicator=True, validate="one_to_one")',
    '''
import pandas as pd
sales = pd.DataFrame({"id": ["A","B"], "units": [2,3]})
catalog = pd.DataFrame({"id": ["A","C"], "price": [10,20]})
for how in ["left","inner","right","outer"]:
    out = sales.merge(catalog, on="id", how=how, validate="one_to_one", indicator=True)
    print(how, out[["id","_merge"]].astype("string").to_dict(orient="records"))
''',
    "A matches, B exists only in sales, C only in catalog. The indicator states source membership explicitly. Nullable measurements alone cannot reliably provide that diagnosis because a matched row can also contain a missing price.",
    'Inner-join and report only len(out) without exclusions',
    'Left-join with indicator and list all left_only keys',
    "An inner join silently changes which events your report describes.",
    "Left join sales IDs A,B to catalog A,C and print the unmatched sales ID.",
    '''
import pandas as pd
sales = pd.DataFrame({"id":["A","B"]})
catalog = pd.DataFrame({"id":["A","C"], "price":[10,20]})
out = sales.merge(catalog, on="id", how="left", validate="one_to_one", indicator=True)
print(out.loc[out["_merge"].eq("left_only"), "id"].tolist())
''',
    "Join two prices with meaningful suffixes and inspect both sources instead of overwriting one.",
    '''
import pandas as pd
sale = pd.DataFrame({"id":["A"], "price":[9]})
catalog = pd.DataFrame({"id":["A"], "price":[10]})
out = sale.merge(catalog, on="id", suffixes=("_sale","_catalog"), validate="one_to_one")
print(out.to_dict(orient="records"))
''',
    "Join type defines represented population; indicator exposes coverage and suffixes preserve provenance.",
    [("Which keeps left facts even if lookup keys are missing?", "left join", "inner join", "right join always", "Left membership is preserved, though matches may multiply without validation."),
     ("Which indicator value represents an unmatched sale in a left join?", "left_only", "both", "right_only", "The row exists on the left but not the lookup.")])

lesson(2, "3. Row multiplication, null keys and validation failures",
    "Predict merge cardinality and reject duplicate or missing lookup keys.",
    [("Many-to-many expansion", "If a key occurs m times on the left and n on the right, matching can produce m*n rows for that key. The revenue in a fact table may be repeated."),
     ("MergeError", "pandas raises MergeError when validate's uniqueness contract fails. Catch it to explain the data issue; do not retry without the contract."),
     ("Null-key matching", "pandas merge can match missing keys with other missing keys, unlike usual SQL null expectations. Reject null keys where IDs are required.")],
    "Two P1 sale lines joined to two P1 catalog rows produce four matched rows. This does not discover new sales; it repeats each sale under two lookup records. "
    "A historical price table may legitimately have several versions, but then product_id alone is insufficient: a date/version rule is needed. "
    "Do not drop duplicate catalog keys arbitrarily to make the error disappear. Ask why they repeat. "
    "Also check IDs for missingness and preserve their text types from Week29. Two unknown IDs should not establish a meaningful business relationship merely because pandas matches their null markers.",
    'if lookup["id"].isna().any() or lookup["id"].duplicated().any():\n    raise ValueError("Lookup IDs must be known and unique")',
    '''
import pandas as pd
left = pd.DataFrame({"id":["P1","P1"], "revenue":[100,200]})
right = pd.DataFrame({"id":["P1","P1"], "version":["old","new"]})
expanded = left.merge(right, on="id")
print("Rows:", len(expanded), "Repeated revenue:", int(expanded["revenue"].sum()))
try:
    left.merge(right, on="id", validate="many_to_one")
except pd.errors.MergeError:
    print("Rejected duplicate lookup keys")
''',
    "Two times two is four. The input revenue300 becomes600 when duplicated matches are summed. many_to_one fails before a misleading report is produced.",
    'Retry a failed validated merge using validate="many_to_many"',
    'Investigate repeated lookup IDs and declare a valid version/key rule',
    "many_to_many permits duplication; it does not solve the correctness problem.",
    "Predict and print the row count when3 left rows for A join2 right rows for A.",
    '''
import pandas as pd
left = pd.DataFrame({"id":["A"]*3})
right = pd.DataFrame({"id":["A"]*2})
print("Rows:", len(left.merge(right, on="id")))
''',
    "Demonstrate that null keys can match, then explicitly reject them before a business join.",
    '''
import pandas as pd
left = pd.DataFrame({"id":pd.Series([None],dtype="string"), "value":[10]})
right = pd.DataFrame({"id":pd.Series([None],dtype="string"), "name":["unknown"]})
print("Null matches:", len(left.merge(right, on="id")))
if left["id"].isna().any() or right["id"].isna().any():
    print("Stop: IDs must be known")
''',
    "Validate cardinality and known IDs before computing totals; expansion is a data-contract issue.",
    [("Two left and three right matches for one key produce how many rows?", "Six", "Five", "Two", "The matching key creates a Cartesian combination."),
     ("Can missing keys match in pandas merge?", "Yes; reject them if IDs must be known", "Never", "Only in SQL", "Null-key behavior must be included in the join policy.")])

lesson(2, "4. Join, reconcile, then aggregate",
    "Verify three-table enrichment and preserve original revenue before reporting by region.",
    [("DataFrame.join", "join matches indexes by default, or uses a left column with on against the right index. A unique lookup index and validate still matter; it is not vertical concatenation."),
     ("Reconciliation invariant", "An invariant is a condition expected to remain true, such as unchanged line IDs, row count and source revenue after dimension enrichment.")],
    "Now turn the three-table example into a reliable analysis. Store the original line IDs, join products with a unique key, check every match, then do the same for customers. "
    "Calculate revenue once using a declared price policy and verify the grouped regional sums equal the joined source total. "
    "join offers a shorter syntax for a dimension whose key is already an index. It still matches labels, not row positions. "
    "If catalog prices vary historically, use recorded line prices or a taught version-selection policy; this week's project keeps a transaction price on every fact row. "
    "These checks precede the final report so a convincing total cannot hide a broken join.",
    'lines.join(customers.set_index("customer_id"), on="customer_id", how="left", validate="many_to_one")',
    ORDERS + '''
out = lines.merge(products, on="product_id", how="left", validate="many_to_one", indicator=True)
assert out["_merge"].eq("both").all()
out = out.drop(columns="_merge").join(customers.set_index("customer_id"), on="customer_id", how="left", validate="many_to_one")
assert out["region"].notna().all()
assert out["line_id"].tolist() == lines["line_id"].tolist()
out["revenue"] = out["units"] * out["unit_price"]
summary = out.groupby("region")["revenue"].sum()
print(summary.to_dict())
print("Reconciled:", int(summary.sum()) == int(out["revenue"].sum()))
''',
    "set_index turns customer IDs into lookup labels. on='customer_id' maps each line's customer key to those labels. We retain three sale lines, then regional revenueNP300 andJP60 reconciles to360.",
    'pd.concat([lines, customers], axis=1)  # assume rows match customers',
    'Match customer_id explicitly with merge or an indexed join',
    "Side-by-side placement is not a relational match unless indexes intentionally encode the same keys.",
    "Enrich lines with customer regions using join and print unchanged line IDs and source row count.",
    ORDERS + '''
out = lines.join(customers.set_index("customer_id"), on="customer_id", validate="many_to_one")
print(out["line_id"].tolist(), len(out))
print(out["region"].tolist())
''',
    "Remove customer C2 from the lookup and stop the report when coverage is incomplete.",
    ORDERS + '''
lookup = customers[customers["customer_id"].ne("C2")]
out = lines.merge(lookup, on="customer_id", how="left", validate="many_to_one", indicator=True)
missing = out.loc[out["_merge"].ne("both"), "customer_id"].unique().tolist()
print("Missing customer keys:", missing)
if missing:
    print("Report stopped; source preserved")
''',
    "Treat row identity, match coverage and conserved totals as requirements before interpreting summaries.",
    [("join matches which labels by default?", "Indexes", "Row positions regardless of labels", "Every common column", "Use on when a left column should match the right index."),
     ("When should unmatched foreign keys be investigated?", "Before publishing aggregates", "After assuming price zero", "Only after plotting", "Unknown lookup attributes make the report incomplete.")])

lesson(3, "1. concat down rows: append compatible observations",
    "Combine monthly tables while preserving source labels and checking the schema.",
    [("concat; axis=0; ignore_index", "concat stacks tables along rows by default. ignore_index=True assigns a fresh0..n-1 row index; it does not remove duplicate observations."),
     ("Column alignment", "Row concatenation aligns column names, not positions. Default outer alignment takes the column union and introduces missing values when a source lacks a column."),
     ("Source provenance", "A source column records where each observation came from. Add it before stacking so repeated IDs can be investigated later.")],
    "Day3 matched related entities across tables. Day4 combines tables that already describe the same kind of observation. "
    "January sale lines and February sale lines can be stacked vertically if their schemas and units agree. Column order may differ because concat matches names. "
    "A new index is only a new label sequence, not proof transactions are distinct. Preserve durable line IDs and a source_month column. "
    "Do not repeatedly concat inside a large loop; collect frames first and concatenate once. If required columns are missing, stop rather than accepting a union full of unexplained nulls.",
    'combined = pd.concat([jan.assign(source_month="Jan"), feb.assign(source_month="Feb")], ignore_index=True)',
    '''
import pandas as pd
jan = pd.DataFrame({"line_id":["J1","J2"], "revenue":[100,40]})
feb = pd.DataFrame({"revenue":[80], "line_id":["F1"]})
combined = pd.concat([jan.assign(source_month="Jan"), feb.assign(source_month="Feb")], ignore_index=True)
print(combined.to_dict(orient="records"))
print("Rows:", len(combined), "Total:", int(combined["revenue"].sum()))
''',
    "Although February lists revenue first, the final revenue column remains correct. The new index is0,1,2 and source_month identifies every row's input.",
    'pd.concat([jan,feb], ignore_index=True)  # claim duplicates are removed',
    'Check durable line_id uniqueness separately after concat',
    "Index labels and business identities are different.",
    "Stack two tables with IDs A,B and C, adding source names first.",
    '''
import pandas as pd
a = pd.DataFrame({"id":["A","B"], "value":[1,2]})
b = pd.DataFrame({"id":["C"], "value":[3]})
out = pd.concat([a.assign(source="a.csv"), b.assign(source="b.csv")], ignore_index=True)
print(out.to_dict(orient="records"))
''',
    "Show what happens when one monthly source has a misspelled revenue column; detect the schema problem before combining.",
    '''
import pandas as pd
a = pd.DataFrame({"id":["A"], "revenue":[10]})
b = pd.DataFrame({"id":["B"], "reveneu":[20]})
print("Unwanted union:", pd.concat([a,b], ignore_index=True).columns.tolist())
required = {"id","revenue"}
print("Schemas valid:", all(set(frame.columns)==required for frame in [a,b]))
''',
    "Stack compatible observation tables, retain provenance, and verify business IDs independently of the index.",
    [("Does ignore_index remove duplicate observations?", "No; it relabels rows", "Always", "Only numeric rows", "Business identity needs its own check."),
     ("How does vertical concat align fields?", "By column names", "Only by column position", "By cell values", "Different column orders can still combine correctly.")])

lesson(3, "2. concat across columns: indexes control alignment",
    "Diagnose outer/inner index alignment and use relational keys when required.",
    [("axis=1; join='outer'/'inner'", "axis=1 combines columns while aligning row indexes. Outer uses the index union; inner uses the intersection, potentially discarding unmatched labels."),
     ("verify_integrity", "verify_integrity=True rejects duplicate labels on the concatenation axis. With axis=1 it checks column labels; with axis=0 it checks row labels. It does not validate foreign-key cardinality.")],
    "Side-by-side concatenation is safe only when row labels intentionally identify the same entities. "
    "Scores indexed A,B and minutes indexed B,C align B together; they do not pair A's score with B's minutes by position. "
    "Outer concat represents A,B,C with missing cells where a source lacks the entity. Inner keeps only B, which changes the population. "
    "Do not reset both indexes just to force a match: that discards the identity information protecting you from wrong associations. "
    "Use merge if identity lives in a column and needs explicit coverage/cardinality checks.",
    'pd.concat([scores, minutes], axis=1, join="outer", verify_integrity=True)',
    '''
import pandas as pd
scores = pd.Series([80,90], index=["A","B"], name="score")
minutes = pd.Series([30,45], index=["B","C"], name="minutes")
outer = pd.concat([scores,minutes], axis=1, join="outer", verify_integrity=True)
inner = pd.concat([scores,minutes], axis=1, join="inner")
print("Outer labels:", outer.index.tolist())
print("B values:", outer.loc["B"].tolist())
print("Missing:", outer.isna().sum().to_dict())
print("Inner labels:", inner.index.tolist())
''',
    "B receives score90 and minutes30 because the same label matches. A lacks minutes and C lacks score. The inner result intentionally represents only the shared labelB.",
    'Reset both indexes then combine unrelated people by position',
    'Keep meaningful indexes or merge explicit IDs',
    "Position is not a relationship unless a source contract guarantees it.",
    "Join scores for X,Y and hours for Y,Z using outer concat; print represented labels and Y's values.",
    '''
import pandas as pd
scores = pd.Series([70,85], index=["X","Y"], name="score")
hours = pd.Series([2,3], index=["Y","Z"], name="hours")
out = pd.concat([scores,hours], axis=1)
print(out.index.tolist(), out.loc["Y"].tolist())
''',
    "Reject two side-by-side columns with the same name using verify_integrity.",
    '''
import pandas as pd
a = pd.DataFrame({"score":[80]}, index=["A"])
b = pd.DataFrame({"score":[90]}, index=["A"])
try:
    pd.concat([a,b], axis=1, verify_integrity=True)
except ValueError:
    print("Rejected duplicate column labels")
''',
    "Axis1 aligns row labels; inner intersection can exclude entities. Integrity checks concern labels on the chosen axis.",
    [("Which pairs entities in axis1 concat?", "Matching index labels", "Same row position always", "Highest value", "Indexes define alignment."),
     ("What does verify_integrity check for axis1?", "Duplicate output column labels", "Unique customer foreign keys", "Whether source values are correct", "The concatenation axis contains columns.")])

lesson(3, "3. Twelve monthly CSVs, one validated local dataset",
    "Combine a declared twelve-file set without silently omitting a month.",
    [("Path; read_csv(dtype=...)", "Path is the file-path object from earlier file lessons. Explicit read_csv dtypes retain ID zeros and keep measurements consistent across monthly exports."),
     ("Declared input manifest", "A manifest is the list of files you expect. Building Jan–Dec names explicitly can detect a missing month that a broad file search would simply omit."),
     ("assign", "assign returns a table with named columns added or replaced. Here it records source_file before concatenation.")],
    "A folder containing11 files is not automatically a valid twelve-month report. Declare the expected names, require each file, and validate required columns. "
    "Collect tables in a list, add source_file, then concat once. Validate line IDs across the entire combined dataset, because duplicates may cross file boundaries. "
    "The example creates fictional CSVs inside a fresh TemporaryDirectory and reads them locally; it does not touch your actual files. "
    "For your own exports, separate fixtures from input and require stable schemas, units and calendar meanings. A timestamp field would also need the Day5 parsing policy.",
    'paths = [folder / f"2025-{m:02d}.csv" for m in range(1,13)]\nframes = [pd.read_csv(p, dtype={"line_id":"string", "revenue":"int64"}).assign(source_file=p.name) for p in paths]\ncombined = pd.concat(frames, ignore_index=True)',
    '''
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd
with TemporaryDirectory() as temp:
    folder = Path(temp)
    paths = [folder / f"2025-{m:02d}.csv" for m in range(1,13)]
    for month, path in enumerate(paths, start=1):
        path.write_text(f"line_id,revenue\\n{month:03d},{month*10}\\n", encoding="utf-8")
    frames = []
    for path in paths:
        frame = pd.read_csv(path, dtype={"line_id":"string", "revenue":"int64"})
        if set(frame.columns) != {"line_id","revenue"}:
            raise ValueError("Unexpected monthly schema")
        frames.append(frame.assign(source_file=path.name))
    combined = pd.concat(frames, ignore_index=True)
    assert combined["line_id"].is_unique
    print("Files:", combined["source_file"].nunique(), "Rows:", len(combined))
    print("First ID:", combined.loc[0,"line_id"], "Revenue:", int(combined["revenue"].sum()))
''',
    "range(1,13) yields12months, :02d formats01..12, and :03d creates text IDs001..012. Keeping IDs as strings preserves zeros. Revenue10+20+...+120 totals780.",
    'Load whatever *.csv happens to return and call it a complete year',
    'Require the declared twelve names and report files/rows/source coverage',
    "A missing file must not disappear from the report's coverage claims.",
    "Combine3 declared monthly files with amounts10,20,30 and show every source filename.",
    '''
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd
with TemporaryDirectory() as temp:
    paths = [Path(temp)/f"m{m}.csv" for m in range(1,4)]
    for m,p in enumerate(paths,1):
        p.write_text(f"id,value\\n{m:03d},{m*10}\\n", encoding="utf-8")
    out = pd.concat([pd.read_csv(p,dtype={"id":"string"}).assign(source=p.name) for p in paths],ignore_index=True)
    print(out["source"].tolist(), int(out["value"].sum()))
''',
    "Create only2 of3 expected files and identify the missing file before reading anything.",
    '''
from pathlib import Path
from tempfile import TemporaryDirectory
with TemporaryDirectory() as temp:
    paths = [Path(temp)/f"m{m}.csv" for m in range(1,4)]
    for p in paths[:2]:
        p.write_text("id,value\\nA,10\\n", encoding="utf-8")
    print("Missing:", [p.name for p in paths if not p.is_file()])
''',
    "Declare expected sources, preserve types and source names, then validate across file boundaries.",
    [("Why specify string dtype for line IDs?", "Preserve identity text and leading zeros", "Make every value numeric", "Prevent duplicates automatically", "IDs are labels, not measurements."),
     ("Can a wildcard prove all12 required months exist?", "No; compare with an expected list", "Always", "Only if sorted", "An absent file never appears in the wildcard result.")])

lesson(3, "4. Overlap is a decision, not an index problem",
    "Diagnose duplicate business IDs across exports without erasing legitimate repeat events.",
    [("Duplicated business keys", "duplicated(subset=...) checks the identity you declare. Repeated customers are legitimate; repeated unique sale-line IDs need investigation."),
     ("concat(keys=...)", "keys adds an outer source level to the row index. This preserves origin but still does not deduplicate overlapping events."),
     ("Schema/coverage audit", "A small audit records file counts, raw/combined rows, repeated IDs, types and metric totals. It documents the source population before reporting.")],
    "Monthly exports can overlap when a system re-exports the end of the previous month. concat retains both records. "
    "Repeating C1 as a customer is normal; repeating L1 as a globally unique line ID is different. Week29's duplicate-selection policies still apply: define identity, timestamps and valid version rules before removing rows. "
    "If no rule is supplied, fail visibly rather than guessing which version is right. A MultiIndex source key can aid investigation but cannot decide truth. "
    "Reconcile row counts and amounts before and after any approved deduplication and retain source evidence.",
    'overlap = combined[combined.duplicated("line_id", keep=False)]',
    '''
import pandas as pd
jan = pd.DataFrame({"line_id":["L1","L2"], "customer":["C1","C1"], "revenue":[100,20]})
feb = pd.DataFrame({"line_id":["L2","L3"], "customer":["C1","C2"], "revenue":[20,50]})
out = pd.concat([jan.assign(source="Jan"),feb.assign(source="Feb")],ignore_index=True)
overlap = out[out.duplicated("line_id",keep=False)]
print("Overlap:", overlap[["line_id","source"]].to_dict(orient="records"))
print("Raw rows:", len(out), "Raw total:", int(out["revenue"].sum()))
print("Report allowed:", out["line_id"].is_unique)
''',
    "L2 appears in both sources and would be counted twice. The raw total190 is not automatically an approved annual total. CustomerC1 repeats across distinct lines, so deduplicating by customer would destroy legitimate purchases.",
    'combined.drop_duplicates("customer")',
    'Investigate line_id overlap; apply only an explicit event/version policy',
    "Customers can legitimately make repeated purchases.",
    "Use concat(keys=['Jan','Feb']) on two frames and inspect the source/row index levels.",
    '''
import pandas as pd
a = pd.DataFrame({"value":[10,20]})
b = pd.DataFrame({"value":[30]})
out = pd.concat([a,b], keys=["Jan","Feb"], names=["source","row"])
print(out.index.tolist(), out.index.names)
''',
    "For unique line IDs but repeated customers, confirm the file can pass the ID rule and show distinct-customer count separately.",
    '''
import pandas as pd
out = pd.DataFrame({"line_id":["L1","L2","L3"], "customer":["C1","C1","C2"]})
print("Line IDs unique:", out["line_id"].is_unique)
print("Customers:", out["customer"].nunique(), "Lines:", len(out))
''',
    "Index relabeling and provenance help inspection; only a declared business policy resolves overlapping events.",
    [("Is a repeated customer necessarily a duplicate transaction?", "No", "Always", "Only after concat", "One customer may have several legitimate sale lines."),
     ("Does concat(keys=...) remove overlaps?", "No; it records source index levels", "Always", "Only if two files", "Provenance and deduplication are separate operations.")])

DATES = '''
import pandas as pd
df = pd.DataFrame({"when": ["2025-01-06", "2025-02-15", "2025-03-31"]})
df["when"] = pd.to_datetime(df["when"], format="%Y-%m-%d", errors="raise")
'''

lesson(4, "1. Parse timestamps under a declared time convention",
    "Distinguish date labels, naive local clocks and timezone-aware instants.",
    [("Datetime Series; to_datetime", "to_datetime converts declared date/time text to pandas datetime values. Explicit format and errors='raise' expose malformed records; errors='coerce' requires an audit of resulting NaT."),
     ("Naive versus aware", "A naive datetime has no timezone. An aware datetime identifies an instant with timezone information. A date-only field may be a calendar label, not an instant."),
     ("UTC; utc=True", "UTC is a common reference for instants. utc=True converts explicit offsets to UTC; with naive input it treats the clock as UTC rather than discovering the source timezone.")],
    "A date can mean an accounting day, while a timestamp can mean the exact moment a sale occurred. Ask the source which meaning applies. "
    "Parse date-only exports with their exact known format and audit failures; do not guess ambiguous03/04 dates. "
    "For timestamp strings already carrying offsets, utc=True puts all instants on one reference clock. Two different clock readings can represent the same instant. "
    "For a Tokyo local clock without an offset, localize to Asia/Tokyo first, then convert to UTC. Simply passing utc=True would incorrectly label that local clock as UTC. "
    "Week29 already taught conversion auditing; this week uses correct times to group events.",
    'pd.to_datetime(text, format="%Y-%m-%d", errors="raise")\npd.to_datetime(offset_text, utc=True)',
    '''
import pandas as pd
clock = pd.Series(["2025-01-01 09:00:00"])
naive = pd.to_datetime(clock, format="%Y-%m-%d %H:%M:%S")
tokyo = naive.dt.tz_localize("Asia/Tokyo")
print("Tokyo:", str(tokyo.iloc[0]))
print("UTC:", str(tokyo.dt.tz_convert("UTC").iloc[0]))
offsets = pd.Series(["2025-01-01T09:00:00+09:00", "2025-01-01T00:00:00+00:00"])
parsed = pd.to_datetime(offsets, utc=True)
print("Same instant:", parsed.iloc[0] == parsed.iloc[1])
''',
    "Localizing gives the naive09:00 clock its declared Tokyo context; converting represents the same instant as00:00 UTC. The offset-bearing strings then compare equal.",
    'pd.to_datetime(tokyo_local_text, utc=True)  # assume source timezone discovered',
    'Parse naive local text, tz_localize("Asia/Tokyo"), then tz_convert("UTC")',
    "utc=True does not infer a missing source timezone.",
    "Parse valid date2025-02-28 and invalid2025-02-30 with coercion; report exactly which source token failed.",
    '''
import pandas as pd
raw = pd.Series(["2025-02-28", "2025-02-30"])
parsed = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
print("Invalid:", raw[parsed.isna()].tolist())
print("Known:", parsed.dropna().dt.strftime("%Y-%m-%d").tolist())
''',
    "Convert2025-01-01T00:30+09:00 to UTC and explain why the UTC calendar day is different.",
    '''
import pandas as pd
times = pd.to_datetime(pd.Series(["2025-01-01T00:30:00+09:00"]), utc=True)
print(str(times.iloc[0]))
print(times.dt.tz_convert("Asia/Tokyo").dt.strftime("%Y-%m-%d").tolist())
''',
    "Declare whether the field is a date or instant, the exact format and source timezone before grouping.",
    [("Can utc=True discover a naive source's timezone?", "No", "Always", "Only for Tokyo", "It treats naive input as UTC."),
     ("What follows errors='coerce'?", "Inspect and account for NaT failures", "Fill failures with today", "Assume all records valid", "Coercion can hide malformed dates if not audited.")])

lesson(4, "2. The dt accessor: calendar components and periods",
    "Extract year, month, weekday and quarter without mixing years accidentally.",
    [("dt accessor", "dt exposes vectorized datetime operations on a Series, such as year, month, dayofweek and quarter. It requires datetime-like values rather than raw text."),
     ("dayofweek; strftime", "dayofweek uses Monday0 through Sunday6. strftime formats a datetime using explicit directives; use numeric weekday codes when locale-dependent names would be ambiguous."),
     ("to_period('M')", "A monthly Period names a calendar interval such as2025-01, rather than an instant. It retains year and month together for cross-year summaries.")],
    "After parsing, .dt selects calendar information for every row. .dt.month alone gives numbers1..12 and loses the year. "
    "Grouping January2024 with January2025 may be correct for a seasonal comparison, but wrong for a chronological monthly report. "
    "Use monthly periods or year plus month for the latter. Periods represent intervals; timestamp labels represent instants or boundaries. "
    "For timezone-aware data, first convert to the business timezone and deliberately remove timezone information only after identifying the local calendar clock; this prevents grouping a Tokyo sale under its previous UTC day.",
    'df["year"] = df["when"].dt.year\ndf["month"] = df["when"].dt.month\ndf["period"] = df["when"].dt.to_period("M")',
    DATES + '''
df["year"] = df["when"].dt.year
df["month"] = df["when"].dt.month
df["weekday"] = df["when"].dt.dayofweek
df["quarter"] = df["when"].dt.quarter
df["period"] = df["when"].dt.to_period("M").astype("string")
print(df.drop(columns="when").to_dict(orient="records"))
''',
    "Jan6 is Monday(code0), Feb15 is Saturday(code5), Mar31 is Monday. All three dates are in quarter1. Period labels preserve the year alongside the month.",
    'Group a multi-year chronological report by dt.month alone',
    'Group by dt.to_period("M") or [year,month]',
    "Month numbers repeat annually and collapse different calendar intervals.",
    "For2024-01-10 and2025-01-10, show distinct monthly period labels despite identical month numbers.",
    '''
import pandas as pd
s = pd.to_datetime(pd.Series(["2024-01-10","2025-01-10"]), format="%Y-%m-%d")
print(s.dt.month.tolist(), s.dt.to_period("M").astype("string").tolist())
''',
    "Convert a UTC instant to Tokyo's local calendar date before assigning its month.",
    '''
import pandas as pd
utc = pd.to_datetime(pd.Series(["2024-12-31T15:30:00Z"]),utc=True)
local = utc.dt.tz_convert("Asia/Tokyo")
month = local.dt.tz_localize(None).dt.to_period("M")
print(local.dt.strftime("%Y-%m-%d").tolist(), month.astype("string").tolist())
''',
    "Calendar keys must retain the required year and use the report's business timezone.",
    [("What numeric weekday is Monday?", "0", "1", "7", "dayofweek is zero-based."),
     ("Which separates January2024 from January2025?", "Monthly periods", "Month number alone", "Day number alone", "A Period includes both year and month.")])

lesson(4, "3. Date arithmetic and sorted elapsed durations",
    "Calculate deadlines and elapsed gaps without confusing row order with time order.",
    [("Timedelta; to_timedelta", "A Timedelta is a duration, such as48hours. Adding it to a datetime shifts the instant by elapsed time. It differs from an arbitrary number of calendar months."),
     ("diff; dt.total_seconds", "diff subtracts adjacent values in current row order. After chronological sorting, timedelta.total_seconds converts the elapsed duration to a numeric measurement."),
     ("Group-specific gap", "Sort by entity and timestamp before groupby.diff. This measures gaps within each entity rather than between unrelated customers.")],
    "A due time two days after an event can be calculated with a duration. A 'next calendar month' deadline requires a calendar rule because months have different lengths. "
    "Never label an unsorted diff as time between consecutive events. It subtracts positions in the existing table, not the automatically previous timestamp. "
    "Within-customer gaps need both sorting and grouping. The first event for each customer has no previous event, so its gap is missing. "
    "dt.days returns the whole-day component of a duration, not precise fractional elapsed days; use total_seconds/86400 when you need elapsed fractions.",
    'ordered = df.sort_values(["customer","when"])\ngap = ordered.groupby("customer")["when"].diff()\nhours = gap.dt.total_seconds() / 3600',
    '''
import pandas as pd
df = pd.DataFrame({"customer":["A","B","A"], "when":["2025-01-03 12:00","2025-01-02 09:00","2025-01-01 00:00"]})
df["when"] = pd.to_datetime(df["when"],format="%Y-%m-%d %H:%M")
ordered = df.sort_values(["customer","when"])
ordered["gap_hours"] = ordered.groupby("customer")["when"].diff().dt.total_seconds()/3600
print(ordered[["customer","gap_hours"]].to_dict(orient="records"))
print("Deadline:", str(ordered.iloc[0]["when"] + pd.Timedelta(days=2)))
''',
    "A's first event has no gap, the next is60hours later. B's lone event also has no gap. Adding2days to Jan1midnight gives Jan3midnight.",
    'df["when"].diff()  # call this chronological customer gaps',
    'Sort by customer/time, then groupby(customer).diff()',
    "Unsorted or cross-customer subtraction measures the wrong relationship.",
    "Parse Jan1midnight and Jan2noon, then report exact elapsed hours and fractional days.",
    '''
import pandas as pd
s = pd.to_datetime(pd.Series(["2025-01-01 00:00","2025-01-02 12:00"]),format="%Y-%m-%d %H:%M")
gap = s.iloc[1]-s.iloc[0]
print("Hours:", gap.total_seconds()/3600, "Days:", gap.total_seconds()/86400)
''',
    "Create a90-minute deadline and verify its elapsed difference, using to_timedelta.",
    '''
import pandas as pd
start = pd.Timestamp("2025-01-01 09:00")
deadline = start + pd.to_timedelta(90,unit="m")
print(str(deadline), (deadline-start).total_seconds()/60)
''',
    "Elapsed durations, calendar offsets, sorting and grouping answer different time questions.",
    [("Does diff sort timestamps automatically?", "No", "Always", "Only when grouped", "It follows existing row order."),
     ("What is36 elapsed hours in days?", "1.5 using total_seconds/86400", "Exactly1 via every method", "2 always", "Whole-day components discard the fractional part.")])

lesson(4, "4. Timezones, ambiguous clocks and reporting boundaries",
    "Use local business dates and fail visibly on ambiguous daylight-saving clock text.",
    [("tz_localize versus tz_convert", "localize assigns a timezone to a naive clock; convert changes the displayed timezone of an aware instant without changing that instant."),
     ("ambiguous; nonexistent", "Some local clocks occur twice or never during daylight-saving changes. tz_localize can raise for these; resolve with source offsets or a documented policy, not a guess."),
     ("Half-open interval", "A window start<=time<end includes its start and excludes its end. Adjacent windows then avoid counting an exact boundary twice.")],
    "Tokyo currently has no daylight-saving clock changes, but imported records may come from places that do. "
    "An autumn local01:30 can occur twice. Without an offset or event ordering contract, that text does not uniquely identify an instant. Prefer source timestamps carrying offsets. "
    "For revenue by local date, convert UTC instants to the reporting timezone before extracting dates. A UTC end-of-month instant can already belong to the next month locally. "
    "Use half-open date filters for adjacent reporting windows: include Jan1midnight, exclude Feb1midnight. This prevents the same exact boundary from being reported twice.",
    'local = utc.dt.tz_convert("Asia/Tokyo")\nmask = local.ge(start) & local.lt(end)',
    '''
import pandas as pd
utc = pd.to_datetime(pd.Series(["2024-12-31T15:00:00Z","2025-01-31T15:00:00Z"]),utc=True)
local = utc.dt.tz_convert("Asia/Tokyo")
start = pd.Timestamp("2025-01-01",tz="Asia/Tokyo")
end = pd.Timestamp("2025-02-01",tz="Asia/Tokyo")
print("Tokyo dates:", local.dt.strftime("%Y-%m-%d").tolist())
print("January:", (local.ge(start)&local.lt(end)).tolist())
''',
    "The UTC Dec31instant is Tokyo Jan1 and belongs in January. The UTC Jan31instant is Tokyo Feb1 and is excluded by the half-open January window.",
    'Use UTC month for a Tokyo-local accounting report',
    'Convert to the declared business timezone before assigning calendar periods',
    "Calendar boundaries depend on the reporting timezone.",
    "Parse the two offset versions of a repeated New York01:30 clock and measure their elapsed difference.",
    '''
import pandas as pd
s = pd.to_datetime(pd.Series(["2025-11-02T01:30:00-04:00","2025-11-02T01:30:00-05:00"]),utc=True)
print(s.dt.strftime("%H:%M UTC").tolist())
print("Minutes apart:", (s.iloc[1]-s.iloc[0]).total_seconds()/60)
''',
    "Test timestamps exactly on Jan1 and Feb1 against the January half-open window.",
    '''
import pandas as pd
s = pd.to_datetime(pd.Series(["2025-01-01","2025-02-01"]),format="%Y-%m-%d")
inside = s.ge(pd.Timestamp("2025-01-01")) & s.lt(pd.Timestamp("2025-02-01"))
print(inside.tolist())
''',
    "A clock string needs a timezone policy; reporting windows need an explicit boundary convention.",
    [("Which changes timezone display of an aware instant?", "tz_convert", "tz_localize again", "Drop the raw date", "The represented instant remains unchanged."),
     ("Why use start<=time<end for adjacent windows?", "Avoid double-counting boundaries", "Always discard the first event", "Make all months30days", "Only one adjacent window includes their shared boundary.")])

lesson(5, "1. Resample: calendar intervals have a meaning",
    "Turn dated sale lines into daily or monthly totals with explicit coverage and missing-value rules.",
    [("DatetimeIndex; resample", "set_index('when') makes datetimes the row labels. resample groups observations into time bins; request a reduction such as sum or count."),
     ("MS; ME; D", "MS labels monthly bins at month starts; ME uses month-end frequency; D is daily. Use current frequency aliases and document bin boundaries/labels."),
     ("reindex; complete coverage", "reindex introduces an explicit expected calendar. Missing bins may be filled with zero only when absence really means no events in a fully captured period.")],
    "resample is time-based grouping. Start with parsed timestamps, set them as the index, sort, then choose a calendar frequency. "
    "A monthly total needs its year and month, plus a statement about complete source coverage. No rows in February could mean no sales or a missing export; only a complete-feed contract permits zero. "
    "sum(min_count=1) keeps an empty or all-missing bin unknown until you deliberately apply that policy. "
    "The example covers a complete January–March sale feed, so absent February transactions mean zero revenue. The input has only valid known amounts. "
    "Label months at their starts with MS, and explain left-closed/left-labeled bins rather than relying on unexplained defaults.",
    'monthly = indexed["revenue"].resample("MS", closed="left", label="left").sum(min_count=1)',
    '''
import pandas as pd
df = pd.DataFrame({"when":["2025-01-01","2025-01-31","2025-03-01"],"revenue":[100,50,200]})
df["when"] = pd.to_datetime(df["when"],format="%Y-%m-%d")
indexed = df.set_index("when").sort_index()
monthly = indexed["revenue"].resample("MS",closed="left",label="left").sum(min_count=1)
print("Unknown bins:", monthly.isna().tolist())
complete = monthly.fillna(0).astype("int64")  # declared complete Jan–Mar event feed
print(dict(zip(complete.index.strftime("%Y-%m"),complete.tolist())))
''',
    "Jan1 and Jan31 belong to January; Mar1 belongs to March. February is initially missing because no observed values entered its bin. Only the stated complete-feed rule converts that missing total to0.",
    'Fill every absent month with zero without checking source coverage',
    'Keep unknown periods missing; fill absent events only under complete coverage',
    "A missing export and an observed no-sale month are different facts.",
    "Resample dated revenues10,20 on Jan1/Jan2 and30 on Feb1 to monthly totals.",
    '''
import pandas as pd
s = pd.Series([10,20,30],index=pd.to_datetime(["2025-01-01","2025-01-02","2025-02-01"]))
monthly = s.resample("MS",closed="left",label="left").sum(min_count=1)
print(dict(zip(monthly.index.strftime("%Y-%m"),monthly.tolist())))
''',
    "Build an explicit Jan1–Jan3 daily calendar with Jan1/Jan3 values10/30; retain Jan2 as unknown before applying any policy.",
    '''
import pandas as pd
s = pd.Series([10,30],index=pd.to_datetime(["2025-01-01","2025-01-03"]))
calendar = pd.date_range("2025-01-01","2025-01-03",freq="D")
aligned = s.reindex(calendar)
print(aligned.isna().tolist(), aligned.fillna(0).astype("int64").tolist())
''',
    "Choose calendar bins, labels and source coverage explicitly; missing periods are not automatically observed zero.",
    [("Which alias labels monthly bins at month starts?", "MS", "D", "h", "MS means month start."),
     ("When is an absent event month legitimately zero?", "When complete coverage establishes no events", "Whenever a file is missing", "Only if plotted", "Coverage is a data contract, not a filling trick.")])

lesson(5, "2. Rolling windows: seven observations or seven days?",
    "Distinguish fixed-row windows from elapsed-time windows and prevent look-ahead.",
    [("rolling(7) versus rolling('7D')", "rolling(7) uses seven observations. With a sorted DatetimeIndex, rolling('7D') uses observations in the elapsed seven-day interval, which may contain a different number of rows."),
     ("min_periods; closed; center", "min_periods sets the minimum known observations for a result. closed='right' includes the current right endpoint and excludes the left endpoint. center=False labels a trailing window without future rows."),
     ("Daily calendar first", "A7-observation mean is a7-day mean only on a complete one-row-per-day calendar. Insert missing calendar labels deliberately and decide whether gaps are zero or unknown.")],
    "Smoothing reduces daily fluctuations, but the denominator matters. Seven sale records are not seven calendar days. "
    "A time-based window on irregular event rows averages event measurements in that time interval, not daily totals. For a daily-revenue average, aggregate events to days and establish the full calendar first. "
    "min_periods=7 with a seven-row daily window leaves the first six results missing. That is more honest than calling a two-day mean a full-week mean. "
    "Trailing windows include information available up to that date. Centered windows use later observations and should not be presented as a live historical predictor.",
    'daily.rolling(7,min_periods=7).mean()\nirregular.rolling("7D",closed="right",min_periods=1).mean()',
    '''
import pandas as pd
irregular = pd.Series([10,20,90],index=pd.to_datetime(["2025-01-01","2025-01-02","2025-01-10"]))
print("Last3 rows:", float(irregular.rolling(3,min_periods=1).mean().iloc[-1]))
print("Last7 days:", float(irregular.rolling("7D",closed="right",min_periods=1).mean().iloc[-1]))
daily = pd.Series([10,20,30,40,50,60,70],index=pd.date_range("2025-01-01",periods=7,freq="D"))
mean = daily.rolling(7,min_periods=7).mean()
print("Incomplete windows:", int(mean.isna().sum()), "Day7:", float(mean.iloc[-1]))
''',
    "At Jan10, the last3observations still include Jan1/Jan2, but the last7days contain only Jan10. On a complete daily calendar, seven rows really are seven days, and their mean is40.",
    'events.rolling(7).mean()  # label7 events as7 days',
    'Aggregate to a daily calendar, then roll7 daily observations',
    "Row counts and elapsed calendar coverage are not interchangeable.",
    "For daily values1..8, compute a7-day mean and show the two fully observed windows.",
    '''
import pandas as pd
s = pd.Series(range(1,9),index=pd.date_range("2025-01-01",periods=8,freq="D"))
print(s.rolling(7,min_periods=7).mean().dropna().tolist())
''',
    "On Jan1/Jan8 values10/80, test right-closed7D endpoint behavior at Jan8.",
    '''
import pandas as pd
s = pd.Series([10,80],index=pd.to_datetime(["2025-01-01","2025-01-08"]))
print("Right-closed:", float(s.rolling("7D",closed="right",min_periods=1).sum().iloc[-1]))
print("Both-closed:", float(s.rolling("7D",closed="both",min_periods=1).sum().iloc[-1]))
''',
    "Name window units, endpoint inclusion, minimum observations and whether future information is used.",
    [("Does rolling(7) always mean7 calendar days?", "No; it means7 observations", "Always", "Only on irregular data", "It needs a complete daily calendar for that interpretation."),
     ("Why prefer trailing windows for an as-of report?", "They avoid future observations", "They always increase revenue", "They discard all old rows", "Centered windows can include later data.")])

lesson(5, "3. shift and honest month-over-month growth",
    "Compare consecutive calendar months and represent zero-base/unknown growth explicitly.",
    [("shift", "shift(1) moves values down one position while retaining index labels. It means the previous month only after the data has one row for every consecutive calendar month."),
     ("Growth fraction versus percent", "(current-previous)/previous is a fraction; multiply by100 for percent. pct_change computes fractional change despite its name; use fill_method=None and handle zeros explicitly."),
     ("Undefined growth", "A first month has no previous baseline. A zero or unknown prior month cannot yield an ordinary finite relative-growth percentage.")],
    "Sorting observed monthly rows is insufficient if February is absent: shift would compare March with January. Establish the monthly calendar first. "
    "Calculate an absolute difference and a relative change separately. From100 to150 is +50 currency units and +50%, while from0 to100 has +100 units but undefined ordinary percent growth. "
    "Preserve those undefined values rather than replacing them with100%, zero or infinity. A missing previous month also makes the comparison unknown. "
    "The latest incomplete month must not be compared as though it were fully observed; the project requires a declared complete-month window.",
    'previous = monthly.shift(1)\ngrowth_pct = 100 * (monthly-previous) / previous.where(previous.gt(0))',
    '''
import pandas as pd
monthly = pd.Series([100,150,0,100],index=pd.date_range("2025-01-01",periods=4,freq="MS"))
previous = monthly.shift(1)
delta = monthly-previous
growth = 100 * delta / previous.where(previous.gt(0))
print("Absolute changes:", delta.dropna().tolist())
print("Growth missing:", growth.isna().tolist())
print("Known growth percentages:", growth.dropna().tolist())
''',
    "Jan has no baseline; Feb grows50%; Mar falls100%; Apr has an undefined zero-base percent. The absolute changes remain useful:50,-150,100.",
    'monthly.pct_change()  # present0.5 as0.5% and allow infinite zero-base output',
    'Multiply fractional change by100 and mask invalid prior baselines',
    "The function name does not change the units of its fractional result.",
    "For months100,120,90, report absolute change and percentage change, retaining the first missing baseline.",
    '''
import pandas as pd
s = pd.Series([100,120,90],index=pd.date_range("2025-01-01",periods=3,freq="MS"))
previous = s.shift(1)
print((s-previous).dropna().tolist())
print((100*(s-previous)/previous.where(previous.gt(0))).dropna().tolist())
''',
    "Show why an observed Jan/March pair needs a February label before shift can mean previous calendar month.",
    '''
import pandas as pd
s = pd.Series([100,200],index=pd.to_datetime(["2025-01-01","2025-03-01"]))
calendar = pd.date_range("2025-01-01","2025-03-01",freq="MS")
aligned = s.reindex(calendar)  # February coverage is unknown, not zero
print("Missing months:", aligned.isna().tolist())
print("March prior unknown:", pd.isna(aligned.shift(1).iloc[-1]))
''',
    "Require consecutive, fully covered months, state percentage units, and preserve undefined baselines.",
    [("A fractional change0.5 equals what percent?", "50%", "0.5%", "500%", "Multiply the fractional result by100."),
     ("What is ordinary relative growth from0 to100?", "Undefined", "100% automatically", "0%", "The previous-value denominator is zero.")])

COHORT = '''
import pandas as pd
events = pd.DataFrame({
    "customer": ["A","B","A","C","A","B","C","D"],
    "when": ["2025-01-02","2025-01-15","2025-02-02","2025-02-16", "2025-03-03","2025-03-10","2025-03-20","2025-03-29"]})
events["month"] = pd.to_datetime(events["when"],format="%Y-%m-%d").dt.to_period("M")
events["cohort"] = events.groupby("customer")["month"].transform("min")
events["age"] = ((events["month"].dt.year-events["cohort"].dt.year)*12 + events["month"].dt.month-events["cohort"].dt.month)
'''

lesson(5, "4. Cohort retention without inventing future observations",
    "Calculate monthly active-customer retention using distinct people and observable cohort ages.",
    [("Cohort; cohort age", "A cohort groups customers by their first observed purchase month. Age0 is that month; age1 is the following calendar month, even across year boundaries."),
     ("Retention denominator", "Monthly purchase retention here means distinct cohort customers active at age k divided by the cohort's age0 size. It is not revenue growth or the fraction of all current customers."),
     ("Right censoring; left truncation", "Future months are unobservable for newer cohorts (right censoring), so keep them missing. A limited source history may also miss earlier purchases (left truncation): first observed does not prove true acquisition."),
     ("unstack; isna policy", "unstack moves a grouped index level into columns. Fill an absent active count with zero only for an elapsed month covered by the complete feed; future cells stay missing.")],
    "Repeat customers matter, but count people once per month even when they buy several times. First assign each customer's first observed purchase month with transform('min'). "
    "Calculate calendar month age as year_difference*12+month_difference; days/30 would be wrong around uneven months. "
    "Group by cohort and age, count unique customers, then divide by each cohort's age0 size. "
    "Through March, January has ages0,1,2 observable, February only0,1, and March only0. An unobserved future cell is not0% retention. "
    "This measures observed purchase behavior, not cancellation or continuous product usage. Cohort labels describe first observed purchases within this dataset, not necessarily new customers.",
    'counts = events.groupby(["cohort","age"])["customer"].nunique().unstack("age")\nretention_pct = 100 * counts.div(counts[0], axis=0)',
    COHORT + '''
last_month = pd.Period("2025-03",freq="M")
counts = events.groupby(["cohort","age"])["customer"].nunique().unstack("age").reindex(columns=range(3))
for cohort in counts.index:
    for age in counts.columns:
        if cohort+int(age) <= last_month:
            if pd.isna(counts.loc[cohort,age]):
                counts.loc[cohort,age] = 0  # complete event feed through March
        else:
            counts.loc[cohort,age] = float("nan")
retention = 100 * counts.div(counts[0],axis=0)
print(retention.rename_axis(index="first_observed_month",columns="age").to_string())
''',
    "January's A/B cohort has2people: both active at age0, A alone at age1(50%), both at age2(100%). February's C cohort is active in February and March; age2 is future and missing. March's D has only its age0 observed.",
    'retention.fillna(0)  # treat all future cohorts as churned',
    'Keep future cohort ages missing; fill only elapsed fully covered months',
    "Future activity cannot be observed today. Repeated monthly lines must not inflate people counts.",
    "Duplicate one A purchase in March; prove the number of active January-cohort customers at age2 remains2.",
    COHORT + '''
repeated = pd.concat([events,events[events["customer"].eq("A")&events["age"].eq(2)]],ignore_index=True)
count = repeated.groupby(["cohort","age"])["customer"].nunique()
print(int(count.loc[(pd.Period("2025-01",freq="M"),2)]))
''',
    "Calculate age across December2024 to January2025 and confirm it is1, not-11.",
    '''
import pandas as pd
cohort = pd.Period("2024-12",freq="M")
month = pd.Period("2025-01",freq="M")
age = (month.year-cohort.year)*12+month.month-cohort.month
print("Calendar age:", age)
''',
    "Count distinct people, fix the cohort denominator, state source-history limits and keep future cells missing.",
    [("Should February cohort's age2 be0% in a report ending March?", "No; that month is not observed yet", "Always", "Only when sales are low", "A future cell is censored, not evidence of lost customers."),
     ("Do multiple purchase lines by one customer increase monthly active-person count?", "No; use nunique", "Always", "Only for cohort0", "Retention counts distinct cohort members.")])

PROJECT = r'''
import argparse
import csv
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd


def load_table(path, columns):
    raw = Path(path).read_bytes()
    if len(raw) > 5 * 1024 * 1024:
        raise ValueError("CSV exceeds this exercise's 5 MiB limit")
    text = raw.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text), strict=True))
    if not rows or len(set(rows[0])) != len(rows[0]) or set(rows[0]) != set(columns):
        raise ValueError("Missing, duplicate or unexpected CSV headers")
    if len(rows) > 10001 or any(len(row) != len(rows[0]) for row in rows[1:]):
        raise ValueError("CSV row count/width violates the learning contract")
    return pd.read_csv(io.StringIO(text), dtype="string", keep_default_na=False)


def require_keys(frame, key, unique):
    if frame[key].isna().any() or frame[key].str.strip().eq("").any():
        raise ValueError(f"Missing key: {key}")
    if unique and frame[key].duplicated().any():
        raise ValueError(f"Duplicate key: {key}")


def build_reports(lines, products, customers, start, end):
    lines, products, customers = lines.copy(), products.copy(), customers.copy()
    schemas = [(lines, {"line_id","date","product_id","customer_id","units","unit_price_minor"}),
               (products, {"product_id","product"}), (customers, {"customer_id","region"})]
    for frame, columns in schemas:
        if not frame.columns.is_unique or set(frame.columns) != columns or frame.empty:
            raise ValueError("Unexpected or empty input table")
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start.tzinfo is not None or end.tzinfo is not None or start.day != 1 or end.day != 1:
        raise ValueError("Use naive month-start calendar boundaries")
    if start != start.normalize() or end != end.normalize() or end <= start:
        raise ValueError("Expected an increasing midnight month-start window")
    months = pd.date_range(start, end, freq="MS", inclusive="left")
    if len(months) > 24:
        raise ValueError("This learning report supports up to24 complete months")
    require_keys(lines, "line_id", True)
    for key in ["product_id","customer_id"]:
        require_keys(lines,key,False)
    require_keys(products,"product_id",True)
    require_keys(customers,"customer_id",True)
    for frame, field in [(products,"product"),(customers,"region")]:
        if frame[field].isna().any() or frame[field].str.strip().eq("").any():
            raise ValueError("Lookup descriptions must be known")
    if not lines["date"].str.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}").fillna(False).all():
        raise ValueError("Dates must use YYYY-MM-DD")
    lines["date"] = pd.to_datetime(lines["date"],format="%Y-%m-%d",errors="raise")
    if not (lines["date"].ge(start)&lines["date"].lt(end)).all():
        raise ValueError("Sale date lies outside the declared complete window")
    for column in ["units","unit_price_minor"]:
        valid = lines[column].str.fullmatch(r"[0-9]{1,7}").fillna(False)
        if not valid.all():
            raise ValueError("Amounts must be nonnegative integer tokens")
        lines[column] = pd.to_numeric(lines[column],errors="raise").astype("int64")
        if not lines[column].between(1,1_000_000).all():
            raise ValueError("This exercise requires positive units/prices <=1000000")
    lines["revenue_minor"] = lines["units"] * lines["unit_price_minor"]
    out = lines
    for lookup, key in [(products,"product_id"),(customers,"customer_id")]:
        out = out.merge(lookup,on=key,how="left",validate="many_to_one",indicator=True)
        if not out["_merge"].eq("both").all():
            raise ValueError(f"Unmatched foreign key: {key}")
        out = out.drop(columns="_merge")
    assert out["line_id"].tolist() == lines["line_id"].tolist()
    assert int(out["revenue_minor"].sum()) == int(lines["revenue_minor"].sum())
    indexed = out.set_index("date").sort_index()
    # Caller contract: all events captured for every day in [start,end).
    daily = indexed["revenue_minor"].resample("D").sum().reindex(
        pd.date_range(start,end,freq="D",inclusive="left"),fill_value=0)
    daily_report = daily.rename("revenue_minor").to_frame()
    daily_report["rolling7_mean_minor"] = daily.rolling(7,min_periods=7).mean()
    monthly = daily.resample("MS",closed="left",label="left").sum().reindex(months,fill_value=0)
    monthly_report = monthly.rename("revenue_minor").to_frame()
    previous = monthly.shift(1)
    monthly_report["change_minor"] = monthly-previous
    monthly_report["growth_pct"] = 100*(monthly-previous)/previous.where(previous.gt(0))
    top = out.groupby(["region","product_id","product"],as_index=False,observed=True).agg(
        revenue_minor=("revenue_minor","sum"),units=("units","sum"))
    top = top.sort_values(["region","revenue_minor","product_id"],ascending=[True,False,True])
    top["rank_in_region"] = top.groupby("region").cumcount()+1
    activity = out.assign(month=out["date"].dt.to_period("M"))
    activity["cohort"] = activity.groupby("customer_id")["month"].transform("min")
    activity["age"] = ((activity["month"].dt.year-activity["cohort"].dt.year)*12
                       +activity["month"].dt.month-activity["cohort"].dt.month)
    counts = activity.groupby(["cohort","age"])["customer_id"].nunique().unstack("age")
    counts = counts.reindex(columns=range(len(months))).astype("float64")
    last = months[-1].to_period("M")
    for cohort in counts.index:
        for age in counts.columns:
            counts.loc[cohort,age] = (0 if pd.isna(counts.loc[cohort,age]) else counts.loc[cohort,age]) if cohort+int(age)<=last else float("nan")
    retention = 100*counts.div(counts[0],axis=0)
    assert int(monthly.sum()) == int(out["revenue_minor"].sum())
    assert retention.stack().dropna().between(0,100).all()
    summary = {"sale_lines":len(out),"revenue_minor":int(monthly.sum()),
               "start_inclusive":str(start.date()),"end_exclusive":str(end.date()),
               "coverage_policy":"Caller declares complete event feed; absent events are zero",
               "currency_policy":"One fictional currency; integer minor units; positive sales only",
               "price_policy":"Recorded transaction price, not current catalog price",
               "cohort_policy":"First observed purchase in this window, not proven acquisition"}
    return {"enriched":out,"daily":daily_report,"monthly":monthly_report,
            "top_products":top,"cohort_counts":counts,"retention_pct":retention},summary


def publish(reports, summary, destination):
    destination = Path(destination)
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError("Choose a new bundle name in an existing parent directory")
    with TemporaryDirectory(prefix="studyhub-sales-",dir=destination.parent) as temp:
        folder = Path(temp)
        for name,frame in reports.items():
            include_index = name in {"daily","monthly","cohort_counts","retention_pct"}
            frame.to_csv(folder/(name+".csv"),index=include_index,date_format="%Y-%m-%d",lineterminator="\n")
        (folder/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False),encoding="utf-8")
        os.rename(folder,destination)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Week30 complete-feed sales analytics practice")
    parser.add_argument("lines");parser.add_argument("products");parser.add_argument("customers")
    parser.add_argument("destination");parser.add_argument("--start",required=True)
    parser.add_argument("--end",required=True,help="Exclusive complete-month boundary")
    parser.add_argument("--complete-feed",action="store_true",required=True,
                        help="Confirm every event in the window is represented")
    args = parser.parse_args(argv)
    try:
        lines = load_table(args.lines,["line_id","date","product_id","customer_id","units","unit_price_minor"])
        products = load_table(args.products,["product_id","product"])
        customers = load_table(args.customers,["customer_id","region"])
        reports,summary = build_reports(lines,products,customers,args.start,args.end)
        publish(reports,summary,args.destination)
    except (ValueError,OSError,csv.Error) as error:
        parser.exit(1,"Report stopped: "+str(error)+"\n")
    print("Published",len(reports)+1,"files; sale lines",summary["sale_lines"],"revenue minor units",summary["revenue_minor"])
    return 0
'''

FIXTURES = {
    "sale_lines.csv": "line_id,date,product_id,customer_id,units,unit_price_minor\n"
    "L1,2025-01-02,P1,C1,2,10000\nL2,2025-01-15,P2,C2,5,2000\n"
    "L3,2025-02-02,P1,C1,1,10000\nL4,2025-02-16,P2,C3,5,3000\n"
    "L5,2025-03-03,P2,C1,2,2500\nL6,2025-03-10,P1,C2,3,10000\n"
    "L7,2025-03-20,P1,C3,1,10000\nL8,2025-03-29,P2,C4,4,2500\n",
    "products.csv": "product_id,product\nP1,Book\nP2,Pen\n",
    "customers.csv": "customer_id,region\nC1,NP\nC2,JP\nC3,NP\nC4,JP\n",
}
SETUP = "\n" + "\n".join(f'Path({name!r}).write_text({data!r},encoding="utf-8")' for name,data in FIXTURES.items()) + '''
lines = load_table("sale_lines.csv",["line_id","date","product_id","customer_id","units","unit_price_minor"])
products = load_table("products.csv",["product_id","product"])
customers = load_table("customers.csv",["customer_id","region"])
'''

lesson(5, "5. Sales analytics contract: the complete Week30 project",
    "Join three sources, reconcile revenue, publish monthly growth, regional product rankings and observable cohort retention.",
    [("Recorded transaction price; minor units", "The fact row stores the price paid at purchase time. Integer minor units avoid accumulating binary decimal errors in revenue sums. Every row must use one declared currency; refunds, tax and currency conversion are outside this project."),
     ("cumcount; div(axis=0)", "cumcount numbers rows within each group in current order, starting0; after explicit ranking sort, +1 creates a displayed regional rank. div(axis=0) aligns the retention denominator by cohort row labels."),
     ("Complete feed; bounded practice schema", "The program requires a declared full-month window with all events captured. It rejects duplicate/unknown keys, malformed dates and invalid amounts instead of repairing them silently. At most24 complete months and10000 rows per local input CSV are supported."),
     ("New output bundle", "publish writes all files into one owned temporary directory and renames it to a new destination. Existing bundles are refused. pathlib, argparse, json and csv come from earlier engineering weeks; no network calls are made.")],
    "You now have the pieces of an analysis that can be checked. Begin with eight fictional sale lines and two unique lookups. The fact row carries historical price; the catalog supplies only product descriptions. "
    "Part1 of the program loads text without destroying IDs, validates file shape and key uniqueness, and parses dates/prices under the written contract. "
    "Part2 enriches every line through two many-to-one joins, refuses unmatched keys, and proves the original IDs and revenue survived. "
    "Part3 constructs the complete daily calendar, sums months, computes trailing7-day means and masks invalid growth baselines. "
    "Part4 ranks products within regions and builds first-observed-purchase cohorts with future cells left missing. "
    "Part5 publishes six CSVs and a summary JSON into a fresh folder. Read one function at a time, explain its checks aloud, then modify it only after the supplied project tests pass. "
    "A --complete-feed flag records your assertion; it cannot detect records never supplied. Do not assert completeness for a partial export. The source files are retained unchanged.",
    'reports, summary = build_reports(lines, products, customers, "2025-01-01", "2025-04-01")\npublish(reports, summary, "run-01")',
    PROJECT + SETUP + '''
reports,summary = build_reports(lines,products,customers,"2025-01-01","2025-04-01")
print("Lines:", summary["sale_lines"], "Revenue minor:", summary["revenue_minor"])
print("Monthly minor:", reports["monthly"]["revenue_minor"].tolist())
print("Known growth%:", reports["monthly"]["growth_pct"].dropna().round(2).tolist())
print("Regional winners:", reports["top_products"].groupby("region",sort=False).head(1)[["region","product"]].to_dict(orient="records"))
print("January retention%:", reports["retention_pct"].iloc[0].tolist())
''',
    "January30000, February25000 and March55000 sum to110000minorunits. Growth is-16.67% then120%. Both regions' highest-revenue product is Book. January's2-person cohort has100%,50%,100% observed retention; March has no future evidence. The daily calendar has90days; the first six rolling means remain missing.",
    'Join current catalog prices, fill every missing cohort cell0, overwrite an earlier report',
    'Use recorded prices, preserve future unknowns, validate joins and publish a fresh bundle',
    "Each shortcut can change the meaning of the report even if the program runs.",
    "Run the complete project with the supplied fictional CSVs, publish run-01, inspect the seven files and prove all source bytes are unchanged.",
    PROJECT + SETUP + '''
paths = [Path(name) for name in ["sale_lines.csv","products.csv","customers.csv"]]
before = [path.read_bytes() for path in paths]
reports,summary = build_reports(lines,products,customers,"2025-01-01","2025-04-01")
publish(reports,summary,"run-01")
print("Files:", sorted(path.name for path in Path("run-01").iterdir()))
print("Inputs unchanged:", before == [path.read_bytes() for path in paths])
print("Saved total:", json.loads(Path("run-01/summary.json").read_text(encoding="utf-8"))["revenue_minor"])
''',
    "Prove duplicate dimension keys stop the project and an existing output folder is preserved.",
    PROJECT + SETUP + '''
bad_products = pd.concat([products,products.iloc[[0]]],ignore_index=True)
try:
    build_reports(lines,bad_products,customers,"2025-01-01","2025-04-01")
except ValueError:
    print("Duplicate catalog refused")
reports,summary = build_reports(lines,products,customers,"2025-01-01","2025-04-01")
publish(reports,summary,"run-01")
before = Path("run-01/summary.json").read_bytes()
try:
    publish(reports,summary,"run-01")
except ValueError:
    print("Existing report refused")
print("Old summary unchanged:", before == Path("run-01/summary.json").read_bytes())
''',
    "Week30 mastery: meaningful group summaries, preserved observation grain, validated joins, source-aware concat, correct calendar/timezone policies, honest rolling/growth and censored retention.",
    [("Which price calculates historical sale revenue?", "Recorded transaction price", "Today's catalog price always", "Region mean price", "Catalog changes must not rewrite historical purchases."),
     ("Can --complete-feed prove missing source events do not exist?", "No; it records the source-completeness assertion", "Always", "Only for January", "The program cannot recover unsupplied events."),
     ("Should first-observed purchase prove customer acquisition?", "No; earlier history may be absent", "Always", "Only for two customers", "Limited source history can left-truncate cohorts."),
     ("What does size count per group?", "Member rows", "Only known selected values", "Distinct people", "count and nunique have different denominators."),
     ("What preserves row-aligned group totals?", "transform", "agg alone", "Unsorted head", "Transformation repeats results onto original rows."),
     ("Does successful many_to_one validation prove coverage?", "No; inspect unmatched keys", "Always", "Only when sorted", "Lookup uniqueness and foreign-key coverage are separate."),
     ("Does ignore_index remove duplicate sale IDs?", "No", "Always", "Only across months", "It replaces index labels, not business identities."),
     ("Should a missing export month be filled as known zero?", "No; investigate coverage", "Always", "Only if revenue is integer", "Unknown source coverage cannot establish no events."),
     ("Does rolling(7) on event rows measure seven calendar days?", "No", "Always", "Only in January", "A fixed window counts observations."),
     ("What is ordinary percentage growth from a zero baseline?", "Undefined", "100%", "0%", "The denominator is zero."),
     ("What happens to future cohort ages?", "Remain missing", "Become0% churn", "Become100% retained", "Future behavior is not observed."),
     ("Where should this project's next run be saved?", "A new bundle directory", "Over the last report silently", "Over source CSV files", "Old outputs and inputs remain available for comparison.")])

DAYS["30.4"]["parts"][3]["sections"].insert(3, s("new", "ge; lt; element-wise &",
    note="ge(start) compares each datetime with >=start; lt(end) compares with <end. & combines Boolean Series element-wise; parenthesize each comparison when writing operators such as >= directly."))
DAYS["30.5"]["parts"][0]["sections"].insert(3, s("new", "date_range; periods; inclusive",
    note="date_range builds an explicit regular DatetimeIndex. periods requests a number of timestamps; start/end define bounds. inclusive='left' includes the start but excludes the end, matching the reporting window."))
DAYS["30.0"]["parts"][0]["sections"].insert(3, s("sh", 'python -m pip install "pandas>=3,<4"',
    note="Reuse the Week28–29 Python environment. Initial installation needs internet; the lessons and all supplied fictional CSVs work offline afterward. Outputs verified with pandas3.0.1."))
DAYS["30.5"]["parts"][4]["sections"].append(s("sh",
    "python sales_report.py sale_lines.csv products.csv customers.csv run-01 --start 2025-01-01 --end 2025-04-01 --complete-feed\npython sales_report.py --help",
    note="Standalone project and fictional inputs: docs/python-week30. Choose run-02 for a second run. These code examples create fictional fixture files only inside a fresh practice folder; keep original real data elsewhere."))
DAYS["30.5"]["parts"][4]["sections"].append(s("p",
    "Primary references: https://pandas.pydata.org/docs/user_guide/groupby.html · "
    "https://pandas.pydata.org/docs/user_guide/merging.html · https://pandas.pydata.org/docs/user_guide/timeseries.html · "
    "https://pandas.pydata.org/docs/user_guide/window.html. Original explanations, local fictional fixtures, exercises and executed solutions are included for offline study."))


def write():
    target = ROOT / "study-hub.html"
    original = target.read_bytes().decode("utf-8")
    start = original.index("const DAY_TEACH = {")
    end = original.index("\n};\n\nconst REST_DAY",start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS):
        raise RuntimeError("Week30 already exists; refusing to overwrite")
    addition = "\n".join(json.dumps(k)+": "+json.dumps(v,ensure_ascii=False,indent=2)+"," for k,v in DAYS.items()).replace("</","<\\/")
    prefix = original[:end].rstrip()
    if not prefix.endswith(","):
        prefix += ","
    temporary = target.with_suffix(".html.tmp")
    temporary.write_bytes((prefix+"\n"+addition+original[end:]).encode("utf-8"))
    temporary.replace(target)
    folder = ROOT / "docs" / "python-week30"
    folder.mkdir(exist_ok=True)
    (folder/"sales_report.py").write_text('"""Week30 fictional complete-feed sales analytics. Python3.11+, pandas3.x."""\n'+PROJECT+'\nif __name__ == "__main__":\n    raise SystemExit(main())\n',encoding="utf-8")
    for name,data in FIXTURES.items():
        (folder/name).write_text(data,encoding="utf-8",newline="\n")
    parts = [part for day in DAYS.values() for part in day["parts"]]
    questions = sum(len(section["lesson"]["quiz"]) for part in parts for section in part["sections"] if section["t"]=="checkpoint")
    print(f"Added Week30:6 days, {len(parts)} parts, {len(parts)*2} practice exercises, {questions} quiz questions, {EXECUTED} executed outputs.")


if __name__ == "__main__":
    write()

