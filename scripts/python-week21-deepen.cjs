// Enhance Week 21 without removing any original section or shifting old parts.
const fs=require('fs'),cp=require('child_process');
const python='C:/Users/vlogerautari/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const target='study-hub.html';
let html=fs.readFileSync(target,'utf8').replace(/\r\n/g,'\n');
const a=html.indexOf('const DAY_TEACH = ')+18,b=html.indexOf('\n};\n\nconst REST_DAY',a);
const days=Function('return ('+html.slice(a,b+2)+')')();
if(days['21.0'].parts.some(p=>p.title.includes('Guided lab')))throw Error('Week21 deepening already installed');
const walk=[
 ['पहिले plain class सम्झ: __init__ ले self.title/self.pages बनाउँछ। @dataclass ले त्यही assignment भएको constructor, readable repr र field equality तयार गर्छ। Book("Python", 120) मा पहिलो argument title, दोस्रो pages हो; finished नदिँदा False हुन्छ। a == b ले field values तुलना गर्छ, a is b ले एउटै object हो कि होइन हेर्छ। b.finished बदल्दा a बदलिँदैन, त्यसैले equality False हुन्छ। Colon (:) field/type declaration हो; title = str जस्तो assignment होइन।',
  'default_factory=list मा list function आफैँ दिइन्छ। Notebook("Sita") बनाउँदा factory बोलिन्छ र नयाँ खाली list बन्छ; अर्को Notebook ले अर्को list पाउँछ। a.pages.append(...) ले a को list मात्र बदल्छ। default_factory=list() लेखेमा function होइन, बनिसकेको list दिन्छौ—त्यो गलत हुन्छ। Explicit list argument दिएमा factory प्रयोग हुँदैन; caller को list copy हुन्छ भन्ने नमान।',
  '__post_init__ generated constructor पछि चल्छ। पहिले quantity integer र nonnegative छ कि जाँचिन्छ; invalid भए object creation अस्वीकार हुन्छ। frozen=True ले normal field assignment रोक्छ। replace(a, quantity=5) ले a परिवर्तन नगरी नयाँ checked instance बनाउँछ। FrozenInstanceError पनि exception हो; try/except Week 14 कै हो। frozen भित्र list राखेमा list आफैँ freeze हुँदैन।'],
 ['name: str / count: int ले tools लाई input को shape भन्छ; -> str ले return value वर्णन गर्छ। log(...) ले print गरेर उपयोगी value फर्काउँदैन, त्यसैले -> None। label("Books", "many") जानाजानी गलत typed call हो, तर f-string ले string स्वीकार्ने हुँदा Python चल्छ। यही कारण hints र runtime validation एउटै कुरा होइनन्।',
  'stock.get(name) ले key भए value, नभए None दिन्छ। zero पनि valid stock हो, त्यसैले if value is None प्रयोग गर्छौ; if not value ले zero लाई missing ठान्थ्यो। Optional[int] र int | None एउटै allowed-value idea हुन्। Default argument नभएको parameter भने call गर्दा दिनैपर्छ—Optional नामले argument omission सुनिश्चित गर्दैन।',
  'Store(Protocol) ले count(name: str) -> int | None भन्ने contract बताउँछ। ... implementation placeholder हो। MemoryStore ले त्यही method दिएको हुनाले Store बाट inherit नगरी पनि compatible हुन्छ। display ले concrete storage होइन contract प्रयोग गर्छ। Mypy लाई fully typed file चाहिन्छ; --strict ले थप जाँच गर्छ। Runtime tests अझै चाहिन्छ किनकि सही types भएको calculation पनि गलत हुन सक्छ।'],
 ['Invoice को जिम्मेवारी data र total हो। plain_text/compact_text को जिम्मेवारी output format हो। दुवैले invoice.total() बोलाउँछन्; नयाँ format थप्दा arithmetic फेरिँदैन। SRP भनेको एउटा method मात्र राख्नु होइन—सम्बन्धित कामको coherent owner हुनु हो। यो example मा formatter का लागि नयाँ class आवश्यक छैन।',
  'checkout ले delivery.fee(subtotal) बाट nonnegative integer पाउने अपेक्षा गर्छ। Pickup र StandardDelivery दुवैले त्यो promise राख्छन्, त्यसैले एउटै caller चल्छ। नयाँ policy थप्ने seam OCP हो। String "free" फर्काउने Pickup ले arithmetic तोड्छ; method को नाम मिलेर मात्र LSP पूरा हुँदैन।',
  'Report(reader) मा reader बाहिरबाट दिइन्छ: यही constructor injection हो। Report ले values() मात्र जान्छ; delete/save/connect चाहिँदैन। सानो interface ISP हो। Concrete database आफैँ नबनाएर reader contractमा निर्भर हुनु DIP हो। EmptyReader दिएर खाली-data case बिना network test हुन्छ।'],
 ['checkout(80, standard) मा function value pass भएको छ। checkout ले पछि fee(amount) बोलाउँछ। standard(80) पास गर्यौ भने integer 20 पहिले नै बनेको हुन्छ; त्यसलाई function जस्तो बोलाउन मिल्दैन। Callable[[int], int] notation मा भित्रको list argument types हो, अन्तिम int result type हो।',
  'make_formatter(kind) ले कुन object बनाउने निर्णय गर्छ। त्यो object आएपछि caller ले format(amount) मात्र बोलाउँछ। Factory construction चयनका लागि हो; strategy algorithm चयनका लागि हो। Unknown kind मा ValueError उठाउँदा bug निर्माण ठाउँमै स्पष्ट हुन्छ, None फर्काएर पछाडि obscure error दिँदैन।',
  'subscribe मा listener function राखिन्छ; emit(event) मा त्यो function बोलिन्छ। list(self._listeners) ले यस emission को snapshot बनाउँछ। Callback ले subscribe/unsubscribe गरे पनि अहिलेको traversal बिग्रिँदैन। यो synchronous example हो: listener error भए propagation हुन्छ, automatic retry/durable delivery छैन।',
  'shared = Config("JPY") एकचोटि बनाउँछौ। Report(shared) दुवैले उही object पाउँछन्; अलग Config("NPR") ले अलग state दिन्छ। यो deliberate sharing हो, globally enforced singleton होइन। Singleton को उद्देश्य चिन, तर hidden global mutable stateले tests कसरी एकअर्कालाई असर गर्छ भन्ने पनि बुझ।'],
 ['Status("confirmed") ले underlying value बाट enum member खोज्छ। s.name identifier CONFIRMED हो; s.value stored string confirmed हो। Ordinary Enum member stringसँग बराबर होइन। Status.CONFIRMED जस्तो नामबाट codeमा choice स्पष्ट हुन्छ; external textलाई boundaryमा parse गर्नुपर्छ।',
  'auto() ले internal values बनाउँछ, तर definition order edit हुँदा ती numbersलाई पुरानो saved dataको स्थिर अर्थ मान्न हुँदैन। @unique ले एउटै valueका accidental aliases अस्वीकार गर्छ। SavedStatusमा explicit "new"/"done" values compatibilityको लागि राखिएका हुन्। UPPER_CASE नाम पनि convention हो, protection होइन।',
  'allowed[current] ले अहिलेको stateबाट जान मिल्ने target set दिन्छ। target छैन भने assignment अघि error उठ्छ। यही क्रमले failed transition पछि पुरानो state बचाउँछ। Enumले known choices दिन्छ; transition tableले कुन change valid हो बताउँछ। यी दुई अलग समस्या हुन्।'],
 ['पहिले old_total को परिणाम baseline बनाऊ। Receipt(prices).total(fee) ले त्यही परिणाम दिनुपर्छ। Class extraction गर्दा calculation, rounding र storage format एकैपटक बदल्नु हुँदैन। [] / एक item / धेरै items जस्ता casesले structure परिवर्तनमा व्यवहार सुरक्षित छ कि देखाउँछन्।',
  'यो project तहअनुसार पढ: Itemमा fields + validation; Repositoryमा find/save contract; MemoryRepositoryमा dict; Inventoryमा stock rules; low_below_twoमा policy; renderमा display। get() ले Optional Itemलाई missing/not-missing छुट्याउँछ। remove() ले amount validate गर्छ, sufficient stock जाँच्छ, replaceबाट checked snapshot बनाउँछ, त्यसपछि save गर्छ। पुरानो snapshot mutation हुँदैन।',
  'expect_error(..., lambda: ...) मा lambda ले operation पछि चलाउन मिल्ने function बनाउँछ। Helperले त्यही operation बोलाएर सही exception पर्खन्छ। Error आएपछि quantity पनि जाँचिन्छ: गलत codeले state बदलेर मात्र error उठाउन सक्छ। Testमा assert ठीक छ, production validationमा real exceptions प्रयोग गर्छौ; -O modeले assert हटाउन सक्छ।']
];
const s=(t,v,extra={})=>({t,v,...extra});
function out(code){const r=cp.spawnSync(python,['-c',code],{encoding:'utf8',timeout:6000});if(r.status!==0)throw Error(r.stderr);return r.stdout.replace(/\r\n/g,'\n').trimEnd();}
const labs=[
 {title:'Guided lab: manual records, dataclass records and ownership',goal:'Explain exactly what is generated and prove independent defaults.',new:'Field ownership: a factory makes a fresh default; copying explicit input is a separate policy.',intro:'Day 1 का तीन parts पछि गर। पहिले manual objectको assignments र repr सम्झ, त्यसपछि dataclass version हेरेर कुन boilerplate हट्यो भन। तलको notebook exampleमा explicit input list पनि copy गर्छौँ, ताकि callerले list change गर्दा object बदलिँदैन।',syntax:'tags: list[str] = field(default_factory=list)\n\ndef __post_init__(self):\n    self.tags = list(self.tags)',code:`from dataclasses import dataclass, field
@dataclass
class Notebook:
    name: str
    tags: list[str] = field(default_factory=list)
    def __post_init__(self):
        self.tags = list(self.tags)
source = ["python"]
a = Notebook("A", source)
b = Notebook("B")
source.append("outside")
a.tags.append("oop")
print(source)
print(a.tags, b.tags)
print(a.tags is source)`,trace:'source listमा outside थपिन्छ, तर __post_init__मा गरिएको list copyका कारण a.tagsमा त्यो आउँदैन। a.tagsमा oop थप्दा b.tags खाली नै रहन्छ। Outer list copy shallow हो; tags strings भएकाले यहाँ nested mutation समस्या छैन।',task:'Build CheckedBook(title,pages) as a frozen dataclass. Reject blank title and nonpositive/non-int pages, including True. Test valid construction, invalid construction and replace while preserving the old instance.',solution:`from dataclasses import dataclass, replace
@dataclass(frozen=True)
class CheckedBook:
    title: str
    pages: int
    def __post_init__(self):
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title required")
        if type(self.pages) is not int or self.pages <= 0:
            raise ValueError("positive integer pages required")
a = CheckedBook("Python", 120)
b = replace(a, pages=150)
print(a.pages, b.pages)
for title, pages in [(" ", 20), ("Python", 0), ("Python", True)]:
    try: CheckedBook(title, pages)
    except ValueError as error: print(error)`,task2:'Create two ReadingLog instances with an independent default list of finished titles. Append a title to the first and prove the second remains empty.',solution2:`from dataclasses import dataclass, field
@dataclass
class ReadingLog:
    finished: list[str] = field(default_factory=list)
a, b = ReadingLog(), ReadingLog()
a.finished.append("Python")
assert b.finished == []
print(a.finished, b.finished)`,questions:[['Does default_factory copy a list passed explicitly by the caller?','No; it only creates omitted default values.','Yes; every input is deep copied.','It prevents all mutation.'],['Why use type(pages) is int in this contract?','To exclude bool as well as other types.','Because isinstance cannot recognise int.','To convert a string automatically.'],['Does replace mutate its original instance?','No; it constructs another instance.','Yes; it changes all references.','It skips every constructor check.']]},
 {title:'Guided lab: hints, validation and missing values',goal:'Distinguish a type promise from a runtime check using concrete cases.',new:'Boundary validation checks actual values received from a caller; type hints alone do not do this.',intro:'पहिले : annotation र -> result type पढ। Exampleमा typed functionले text result बनाउँछ तर deliberately wrong count पनि format हुन्छ। दोस्रो functionमा explicit validation थपेका छौँ। यही दुई output तुलना गर्दा hint र check बीचको फरक स्पष्ट हुन्छ।',syntax:'def describe(count: int) -> str:\n    ...\n\nif type(count) is not int:\n    raise TypeError(...)',code:`def describe(count: int) -> str:
    return f"Count: {count}"
def checked_describe(count: int) -> str:
    if type(count) is not int:
        raise TypeError("integer count required")
    if count < 0:
        raise ValueError("negative count")
    return f"Count: {count}"
print(describe("many"))  # deliberate wrong typed call
print(checked_describe(0))
try: checked_describe("many")
except TypeError as error: print(error)`,trace:'describeको annotationले Pythonलाई argument रोक्न आदेश दिएको छैन। checked_describeको if/raise actual runtime code भएकाले wrong value रोक्छ। Zero valid हो, negative invalid हो। Error type/domain policy आफैँ स्पष्ट परिभाषित गर्नुपर्छ। Deliberate wrong typed callsलाई mypy-clean moduleमा नराख।',task:'Implement stock_label(name,stock) -> str using a dict[str,int]. Distinguish zero, positive stock and a missing key. Do not use truthiness to decide whether a key was found.',solution:`def stock_label(name: str, stock: dict[str, int]) -> str:
    value: int | None = stock.get(name)
    if value is None:
        return f"{name}: missing"
    return f"{name}: {value} available"
stock = {"Book": 0, "Pen": 4}
for name in ("Book", "Pen", "Bag"):
    print(stock_label(name, stock))`,task2:'Annotate add, subtotal and receipt; make subtotal accept an empty list. Predict results before running and check the typed functions with mypy when available.',solution2:`def add(a: int, b: int) -> int: return a + b
def subtotal(prices: list[int]) -> int: return sum(prices)
def receipt(prices: list[int]) -> str: return f"Total: {subtotal(prices)}"
print(add(2, 3))
print(receipt([]))
print(receipt([100, 20]))`,questions:[['A stock lookup returned 0. Is the item missing?','No; only None represents missing here.','Yes; zero and None mean the same.','Only if the checker is installed.'],['Does -> int automatically convert a result to int?','No; it describes the expected result.','Yes; Python casts the result.','It prints the result.'],['Can mypy replace tests for a wrong tax formula?','No; types and arithmetic correctness are different checks.','Yes; strict mode proves every result.','Only if the function returns float.']]},
 {title:'Guided lab: use SOLID to solve a real design problem',goal:'Separate reading data, calculating a result and displaying it.',new:'A design contract includes meaning and behaviour, not only a method signature.',intro:'Reportले input पढ्छ, average निकाल्छ, text print गर्छ र email पनि पठाउँछ भने unrelated reasons to change धेरै हुन्छन्। यहाँ readerले values दिन्छ, Reportले average निकाल्छ, formatterले text बनाउँछ। नयाँ source चाहिँ compatible reader हो; फरक output चाहिँ formatter हो।',syntax:'class Reader(Protocol):\n    def values(self) -> list[int]: ...',code:`from typing import Protocol
class Reader(Protocol):
    def values(self) -> list[int]: ...
class MemoryReader:
    def values(self) -> list[int]: return [70, 90]
class EmptyReader:
    def values(self) -> list[int]: return []
class Report:
    def __init__(self, reader: Reader) -> None: self.reader = reader
    def average(self) -> float:
        values = self.reader.values()
        return sum(values) / len(values) if values else 0.0
def format_report(report: Report) -> str:
    return f"Average: {report.average():.1f}"
print(format_report(Report(MemoryReader())))
print(format_report(Report(EmptyReader())))`,trace:'SRP: average र format अलग। OCP: अर्को reader थपेर caller reuse। LSP: readerले promised numbers दिनुपर्छ, string list होइन। ISP: Reportलाई values मात्र चाहिन्छ। DIP: Reportले MemoryReader आफैँ नबनाएर injected Reader contract लिन्छ। यी पाँच principles एकै tiny problemमा कसरी लागू भए हेर।',task:'Add a FixedReader storing a copied list, inject it into Report and prove mutating the caller list does not change the report. No database or internet is needed.',solution:`class FixedReader:
    def __init__(self, values): self._values = list(values)
    def values(self): return list(self._values)
class Report:
    def __init__(self, reader): self.reader = reader
    def average(self):
        values = self.reader.values()
        return sum(values) / len(values) if values else 0.0
source = [10, 30]
report = Report(FixedReader(source))
source.append(1000)
assert report.average() == 20.0
print(report.average())`,task2:'Keep the same average calculation and add two text formats. Prove formatting does not change report data.',solution2:`class Report:
    def __init__(self, values): self.values = list(values)
    def average(self): return sum(self.values) / len(self.values) if self.values else 0.0
def plain(report): return f"Average: {report.average():.1f}"
def compact(report): return f"AVG={report.average():.1f}"
r = Report([70, 90])
print(plain(r))
print(compact(r))
assert r.values == [70, 90]`,questions:[['Which change belongs in presentation rather than average()?','Changing the report wording.','Changing the mean calculation.','Changing the empty-data numerical rule.'],['Why inject a Reader into Report?','To replace the data source without coupling calculation to storage.','To avoid all tests.','To force inheritance in every class.'],['A reader returns ["free"] instead of numbers. What happened?','It broke the behavioural contract.','It improved interface segregation.','It is compatible because the method is named values.']]},
 {title:'Guided lab: factory and strategy working together',goal:'Choose construction separately from using a calculation policy.',new:'A factory assembles an object; a strategy supplies interchangeable behaviour. These responsibilities can cooperate.',intro:'Checkoutले total निकाल्छ। Delivery policyले fee निकाल्छ। make_checkoutले selected policyसँग Checkout बनाउँछ। पहिले “कसलाई बनाउने?” र “कसरी fee निकाल्ने?” छुट्याएर सोच। एउटा मात्र policy भए simple function पर्याप्त हुन सक्छ—pattern थप्नु आफैँ लक्ष्य होइन।',syntax:'service = make_checkout("pickup")\nresult = service.total(100)',code:`def standard_fee(amount): return 20
def pickup_fee(amount): return 0
class Checkout:
    def __init__(self, fee_policy): self.fee_policy = fee_policy
    def total(self, amount):
        if amount < 0: raise ValueError("negative subtotal")
        return amount + self.fee_policy(amount)
def make_checkout(kind):
    if kind == "standard": return Checkout(standard_fee)
    if kind == "pickup": return Checkout(pickup_fee)
    raise ValueError("unknown delivery")
print(make_checkout("standard").total(100))
print(make_checkout("pickup").total(100))
try: make_checkout("other")
except ValueError as error: print(error)`,trace:'Factoryमा Checkout(standard_fee) ले function pass गर्छ; fee function त्यहाँ तुरुन्त चल्दैन। total(100)मा policy call हुन्छ। Pickup ले 0 दिनु valid contract हो; "free" string दिनु invalid हुन्थ्यो। Unknown kind लाई स्पष्ट error ले रोक्छ।',task:'Extend the factory with express delivery costing 40. Reuse the same Checkout.total implementation and verify all three policies.',solution:`def standard(amount): return 20
def pickup(amount): return 0
def express(amount): return 40
class Checkout:
    def __init__(self, policy): self.policy = policy
    def total(self, amount): return amount + self.policy(amount)
def make_checkout(kind):
    policies = {"standard": standard, "pickup": pickup, "express": express}
    if kind not in policies: raise ValueError("unknown delivery")
    return Checkout(policies[kind])
for kind, expected in [("standard", 120), ("pickup", 100), ("express", 140)]:
    result = make_checkout(kind).total(100)
    assert result == expected
    print(kind, result)`,task2:'Make an observer unsubscribe itself during emission. Use a listener snapshot; show a second listener still gets both events.',solution2:`class Signal:
    def __init__(self): self.listeners = []
    def subscribe(self, listener): self.listeners.append(listener)
    def unsubscribe(self, listener): self.listeners.remove(listener)
    def emit(self, event):
        for listener in list(self.listeners): listener(event)
signal = Signal()
def once(event):
    print("once:", event)
    signal.unsubscribe(once)
def always(event): print("always:", event)
signal.subscribe(once)
signal.subscribe(always)
signal.emit("A")
signal.emit("B")`,questions:[['When does standard_fee run in the example?','When total(amount) invokes the policy.','When its name is passed to Checkout.','Only when the class is defined.'],['Which responsibility selects the Checkout configuration?','The factory.','The formatter.','The amount integer.'],['Why does the observer copy its listeners?','Callbacks can change subscriptions during emission.','To call every listener twice.','To make a global singleton.']]},
 {title:'Guided lab: enum parsing and safe transitions',goal:'Keep persisted states meaningful and reject invalid changes before mutation.',new:'Boundary parsing converts external text into a known state; transition validation is a separate step.',intro:'JSONमा Enum object सीधै serialize हुँदैन। त्यसैले stable .value string store गर्छौँ र पढ्दा Enum(value)ले reconstruct गर्छौँ। नयाँ state थप्दा पुरानो saved value को अर्थ नबदलिने policy चाहिन्छ। यो practice program हो; Study Hubको storage format बदलिएको छैन।',syntax:'payload = {"state": task.state.value}\nrestored = State(payload["state"])',code:`import json
from enum import Enum
class State(Enum):
    TODO = "todo"
    DONE = "done"
state = State.DONE
text = json.dumps({"state": state.value})
payload = json.loads(text)
restored = State(payload["state"])
print(text)
print(restored.name, restored is State.DONE)
try: State("donne")
except ValueError: print("unknown saved state")`,trace:'json.dumps मा state.value string हुन्छ। json.loads पछि पनि string नै हुन्छ; State(...) ले member खोज्छ। नाममा typo वा unsupported old value भए parsing असफल हुन्छ। चुपचाप अर्कै state नमान। Enum ले valid values चिनाउँछ; transition rule छुट्टै हुन्छ।',task:'Build Order with NEW → CONFIRMED → SHIPPED only. Reject NEW → SHIPPED and prove its state remains NEW; then perform both valid changes.',solution:`from enum import Enum
class State(Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
class Order:
    def __init__(self): self._state = State.NEW
    @property
    def state(self): return self._state
    def transition(self, target):
        allowed = {State.NEW: {State.CONFIRMED}, State.CONFIRMED: {State.SHIPPED}, State.SHIPPED: set()}
        if target not in allowed[self._state]: raise ValueError("invalid transition")
        self._state = target
o = Order()
try: o.transition(State.SHIPPED)
except ValueError as error: print(error)
assert o.state is State.NEW
o.transition(State.CONFIRMED)
o.transition(State.SHIPPED)
print(o.state.value)`,task2:'Define an enum with explicit low/high saved values, round-trip a value through JSON and verify an unsupported value is rejected.',solution2:`import json
from enum import Enum
class Priority(Enum):
    LOW = "low"
    HIGH = "high"
stored = json.dumps({"priority": Priority.HIGH.value})
restored = Priority(json.loads(stored)["priority"])
assert restored is Priority.HIGH
print(restored.name)
try: Priority("urgent")
except ValueError: print("unsupported priority")`,questions:[['What should go into the example JSON payload?','The enum’s explicit stable value.','The enum object without conversion.','Its dropdown index.'],['An invalid transition raised an error. What else should be tested?','The stored state remained unchanged.','Only the spelling of the class.','Whether auto() was used.'],['Does an enum validate legal transition order?','No; transition rules need their own code.','Yes; definition order supplies all rules.','Only if values are strings.']]},
 {title:'Guided lab: refactor, test and explain the inventory',goal:'Preserve behaviour and prove failures cannot corrupt state.',new:'Characterisation tests protect existing behaviour; failure-state tests verify rejected operations do not partially mutate data.',intro:'पहिले पुरानो function बाट observed output सुरक्षित राख। नयाँ class मा उही cases चलाऊ। Inventory project पहिले पूरा पढेर मात्र extension गर: Itemdata, Repositorymechanism, Inventoryrules, policystrategy, formatterpresentation। गल्ती भेटिए bug fix र structure change अलग commits मा राख।',syntax:'before = inventory.quantity\ntry:\n    inventory.remove(invalid_amount)\nexcept ValueError:\n    assert inventory.quantity == before',code:`class Inventory:
    def __init__(self, quantity):
        if type(quantity) is not int or quantity < 0: raise ValueError("invalid quantity")
        self._quantity = quantity
    @property
    def quantity(self): return self._quantity
    def remove(self, amount):
        if type(amount) is not int or amount <= 0 or amount > self._quantity:
            raise ValueError("invalid removal")
        self._quantity -= amount
inventory = Inventory(3)
for amount in (0, -1, True, 4):
    before = inventory.quantity
    try: inventory.remove(amount)
    except ValueError:
        assert inventory.quantity == before
        print("rejected", amount, "stock", inventory.quantity)
inventory.remove(2)
print("remaining", inventory.quantity)`,trace:'प्रत्येक invalid amount अघि before लिन्छौँ। remove ले mutation भन्दा पहिले सबै checks गर्छ, त्यसैले rejected case मा पुरानो quantity बच्यो। Valid removal 2 पछि quantity 3 बाट 1 हुनुपर्छ। Exception मात्र catch गरेर state नहेरेमा partial mutation bug छुट्न सक्छ। @property getter ले caller लाई read path दिन्छ; internal field को underscore confidentiality होइन।',task:'Refactor old_total(prices,fee) into a Receipt dataclass. Preserve outputs for empty, single and multiple prices. Use an independent default list and avoid changing numerical rules.',solution:`from dataclasses import dataclass, field
def old_total(prices, fee=0): return sum(prices) + fee
@dataclass
class Receipt:
    prices: list[int] = field(default_factory=list)
    def total(self, fee=0): return sum(self.prices) + fee
for prices, fee in [([], 0), ([100], 20), ([100, 40], 0)]:
    actual = Receipt(list(prices)).total(fee)
    assert actual == old_total(prices, fee)
    print(actual)`,task2:'Write a small checked stock record and a service that returns a replaced snapshot. Show that the old snapshot stays unchanged and an oversized removal leaves current stock unchanged.',solution2:`from dataclasses import dataclass, replace
@dataclass(frozen=True)
class Stock:
    quantity: int
    def __post_init__(self):
        if type(self.quantity) is not int or self.quantity < 0: raise ValueError("invalid stock")
class Service:
    def __init__(self, stock): self.stock = stock
    def remove(self, amount):
        if type(amount) is not int or amount <= 0 or amount > self.stock.quantity:
            raise ValueError("invalid removal")
        self.stock = replace(self.stock, quantity=self.stock.quantity - amount)
        return self.stock
old = Stock(3)
s = Service(old)
print(old.quantity, s.remove(2).quantity)
try: s.remove(2)
except ValueError: print("rejected")
print(old.quantity, s.stock.quantity)`,questions:[['A refactor also changes rounding and saved formats. Why is that risky?','It mixes structural and behavioural changes, hiding regressions.','It guarantees better tests.','It is required by dataclasses.'],['Which layer owns the stock removal rule in the full project?','Inventory.','The text formatter.','A random caller assignment.'],['What must you explain before adding a design pattern?','The problem it solves and the contract it preserves.','Only its fashionable name.','Why every function must become a class.']]}
];
for(let d=0;d<6;d++){
 const key='21.'+d,parts=days[key].parts;
 parts.forEach((part,i)=>{const explanation=walk[d][i];if(!explanation)throw Error('Missing walkthrough '+key+'.'+i);const index=part.sections.findIndex(s=>s.t==='out');part.sections.splice(index+1,0,s('p','Step-by-step walkthrough · सरल रूपमा\n'+explanation));});
 const lab=labs[d],id='course:21.lab.'+d;
 const questions=lab.questions.map((q,i)=>{const options=q.slice(1),correct=i%3;for(let j=0;j<correct;j++)options.unshift(options.pop());return {q:q[0],options,correct,why:q[1]};});
 parts.push({title:lab.title,optional:true,sections:[s('h',lab.title),s('key','Learning objective: '+lab.goal),s('new','Guided application',{note:lab.new}),s('p',lab.intro),s('syn',lab.syntax,{note:'A pattern to recognise; the full executable example follows.'}),s('code',lab.code),s('out',out(lab.code)),s('p',lab.trace),s('mis',undefined,{wrong:'Copy the syntax without checking state, inputs or the contract.',right:'Predict each operation, validate before mutation and test the resulting state.',why:'Correct-looking syntax does not guarantee correct behaviour. Explain the example before adapting it.'}),s('ex',lab.task,{practiceId:'21.lab.'+d+'.1'}),s('sol',undefined,{code:lab.solution,out:out(lab.solution),why:lab.trace+' The complete program is self-contained: run it first, then change one input and predict the difference.'}),s('ex',lab.task2,{practiceId:'21.lab.'+d+'.2'}),s('sol',undefined,{code:lab.solution2,out:out(lab.solution2),why:'Use the assertions to check the stated contract, then explain every output line. Refer to today’s original parts for the underlying concept.'}),s('try',undefined,{q:'Before running the example: which state or result should change, and what must stay unchanged?',code:'# Trace the input, operation and resulting state.',a:lab.trace,why:'Prediction tests understanding more directly than copying.'}),s('checkpoint',undefined,{lesson:{id,quiz:questions}}),s('key','Explain it without notes, write it from memory, then test one normal case and one rejected case. Repeat this lab whenever the idea feels unclear.')]});
}
// Only replace the six new-day literals. All other bytes stay intact.
for(let d=5;d>=0;d--){const key='21.'+d,start=html.indexOf('"'+key+'":',a),next=html.indexOf('\n"21.'+(d+1)+'":',start+1);const end=d===5?html.indexOf('\n};\n\nconst REST_DAY',start):next;if(start<0||end<0)throw Error('Missing day boundaries '+key);html=html.slice(0,start)+'"'+key+'": '+JSON.stringify(days[key],null,2)+',\n'+html.slice(end);}
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
fs.writeFileSync(target+'.tmp',html,'utf8');fs.renameSync(target+'.tmp',target);
console.log('Week21 improved:19 walkthroughs,6 further-study labs,12 complete exercises,18 new quiz questions; old part positions and identities retained.');
