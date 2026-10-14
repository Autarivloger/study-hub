"""Check chart contents and exports rather than only file existence."""
from pathlib import Path
import importlib.util
import os
import subprocess
import sys
import tempfile
import pandas as pd
from PIL import Image

sys.dont_write_bytecode=True
os.environ["PYTHONDONTWRITEBYTECODE"]="1"
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/"docs"/"python-week31"/"visual_report.py"
SOURCE=ROOT/"docs"/"python-week30"
spec=importlib.util.spec_from_file_location("visual_report",PROJECT)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
prep=module.preparation_module()
paths=[SOURCE/name for name in ["sale_lines.csv","products.csv","customers.csv"]]
data=[prep.load_table(p,cols) for p,cols in zip(paths,[
    ["line_id","date","product_id","customer_id","units","unit_price_minor"],
    ["product_id","product"],["customer_id","region"]])]
reports,summary=prep.build_reports(*data,"2025-01-01","2025-04-01")
before=[p.read_bytes() for p in paths]
fig=module.draw_report(reports["enriched"],reports["monthly"])
assert len(fig.axes)==4
assert fig.axes[0].lines[0].get_ydata().tolist()==[300,250,550]
assert [bar.get_height() for bar in fig.axes[1].patches]==[500,600]
assert [bar.get_width() for bar in fig.axes[2].patches]==[700,400]
assert [bar.get_height() for bar in fig.axes[3].patches]==[1,5,1,1]
assert len(fig.axes[0].texts)==1 and fig.axes[0].texts[0].xy[1]==550
assert fig.axes[0].get_ylim()[0]==0
module.plt.close(fig)
large=reports["enriched"].copy(); large["revenue_minor"]=10**12
large_monthly=large.set_index("date")["revenue_minor"].resample("MS").sum().to_frame()
large_fig=module.draw_report(large,large_monthly)
assert len(large_fig.axes[3].patches)<=20
assert sum(bar.get_height() for bar in large_fig.axes[3].patches)==len(large)
module.plt.close(large_fig)

with tempfile.TemporaryDirectory(prefix="studyhub-week31-project-") as temp:
    folder=Path(temp); destination=folder/"run-01"
    command=[sys.executable,str(PROJECT),*[str(p) for p in paths],str(destination),
        "--start","2025-01-01","--end","2025-04-01","--complete-feed"]
    result=subprocess.run(command,capture_output=True,text=True,encoding="utf-8")
    assert result.returncode==0,result.stderr
    assert len(list(destination.iterdir()))==8
    with Image.open(destination/"report.png") as image:
        assert image.size==(3000,2100)
        assert image.getbbox() is not None
    assert (destination/"report.svg").read_text(encoding="utf-8").find('<svg')>=0
    assert (destination/"report.pdf").read_bytes().startswith(b'%PDF')
    assert pd.read_csv(destination/"monthly_plot.csv")["revenue_minor"].tolist()==[30000,25000,55000]
    assert pd.read_csv(destination/"region_plot.csv").set_index("region")["revenue_minor"].to_dict()=={"JP":50000,"NP":60000}
    assert pd.read_csv(destination/"product_plot.csv").set_index("product")["revenue_minor"].to_dict()=={"Book":70000,"Pen":40000}
    assert len(pd.read_csv(destination/"sale_line_plot.csv"))==8
    text=(destination/"interpretation.txt").read_text(encoding="utf-8")
    assert "1100.00" in text and "300.00, 250.00, 550.00" in text and "not established" in text
    files={p.name:p.read_bytes() for p in destination.iterdir()}
    rerun=subprocess.run(command,capture_output=True,text=True)
    assert rerun.returncode!=0
    assert files=={p.name:p.read_bytes() for p in destination.iterdir()}
    assert sorted(p.name for p in folder.iterdir())==["run-01"]
    assert [p.read_bytes() for p in paths]==before
    assert subprocess.run(command[:-1],capture_output=True).returncode!=0
    bad=folder/"bad.csv";bad.write_text("line_id,date\nL1,wrong\n",encoding="utf-8")
    invalid=command.copy();invalid[2]=str(bad);invalid[5]=str(folder/"invalid")
    assert subprocess.run(invalid,capture_output=True).returncode!=0
    assert not (folder/"invalid").exists()
    # Failure while exporting is not allowed to publish a partial bundle or
    # leave an owned Figure open.
    original_save=module.matplotlib.figure.Figure.savefig
    def broken(*args,**kwargs): raise OSError("simulated export failure")
    module.matplotlib.figure.Figure.savefig=broken
    try:
        try: module.publish(reports,summary,folder/"failed")
        except OSError: pass
        else: raise AssertionError("Export failure was swallowed")
    finally: module.matplotlib.figure.Figure.savefig=original_save
    assert not (folder/"failed").exists()
    assert not module.plt.get_fignums()
    assert sorted(p.name for p in folder.iterdir())==["bad.csv","run-01"]

print("PASS: actual chart series/bars/bins/peak, PNG pixels and vector exports, exact plot CSVs, supported interpretation, unchanged sources, overwrite rejection, required coverage, invalid-source rejection and export-failure cleanup.")
