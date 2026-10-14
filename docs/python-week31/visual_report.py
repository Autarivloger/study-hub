"""Week31: local four-panel visual report from the Week30 source contract."""
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
        "FICTIONAL LEARNING REPORT — not real business performance\n"
        +"Window: "+summary["start_inclusive"]+" inclusive to "+summary["end_exclusive"]+" exclusive.\n"
        +"Coverage: "+summary["coverage_policy"]+". This is a caller assertion, not proof of completeness.\n"
        +"Currency: one fictional currency,100 minor units per displayed unit. Positive sales only.\n"
        +f"Represented sale lines: {len(sales)}. Revenue: {total/100:.2f} fictional units.\n"
        +"A. Monthly totals in calendar order: "+month_units+" fictional units.\n"
        +"B. Region totals: "+json.dumps({str(k):int(v) for k,v in regions.items()})+" minor units.\n"
        +"C. Product totals: "+json.dumps({str(k):int(v) for k,v in products.items()})+" minor units.\n"
        +"D. Histogram uses individual sale-line amounts with bins of100 units or coarser for larger values (at most20 intervals); it does not use monthly totals.\n"
        +"Limitations: costs, profit, causal explanations and future performance are not established.\n"
        +"The selected source window may not describe other periods. No inferential claim is made.\n")
    with TemporaryDirectory(prefix="studyhub-visual-",dir=destination.parent) as temp:
        folder=Path(temp)
        with matplotlib.rc_context({"font.size":10,"axes.spines.top":False,"axes.spines.right":False}):
            fig=draw_report(sales,monthly)
            try:
                for ext in ["png","svg","pdf"]:
                    fig.savefig(folder/("report."+ext),dpi=300,facecolor="white")
            finally:
                plt.close(fig)
        monthly[["revenue_minor"]].to_csv(folder/"monthly_plot.csv",date_format="%Y-%m-%d",lineterminator="\n")
        regions.to_csv(folder/"region_plot.csv",lineterminator="\n")
        products.to_csv(folder/"product_plot.csv",lineterminator="\n")
        sales[["line_id","revenue_minor"]].to_csv(folder/"sale_line_plot.csv",index=False,lineterminator="\n")
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
        parser.exit(1,"Visual report stopped: "+str(error)+"\n")
    print("Published8 files; revenue minor units",total)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
