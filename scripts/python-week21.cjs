// Author only new DAY_TEACH keys. Never rewrite old teaching or application code.
const fs=require('fs'),path=require('path'),cp=require('child_process');
const python=process.env.STUDY_HUB_PYTHON || 'C:/Users/vlogerautari/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const units=[];
const s=(t,v,extra={})=>({t,v,...extra});
function output(code){const r=cp.spawnSync(python,['-c',code],{encoding:'utf8',timeout:6000,env:{...process.env,PYTHONIOENCODING:'utf-8'}});if(r.status!==0)throw Error(r.stderr);return r.stdout.replace(/\r\n/g,'\n').trimEnd();}
function add(d,title,goal,concepts,explain,syntax,code,walk,mistake,task,solution,challenge,answer,q){
 const p=units.filter(u=>u.day===d).length;
 const correct=p%3,options=[q[1],q[2],q[3]];for(let i=0;i<correct;i++)options.unshift(options.pop());
 units.push({day:d,title,sections:[s('h',title),s('key','Learning objective: '+goal),...concepts.map(([v,note])=>s('new',v,{note})),s('p',explain),s('syn',syntax,{note:'Syntax pattern: read the complete runnable example next.'}),s('code',code),s('out',output(code)),s('p',walk),s('mis',undefined,{wrong:mistake[0],right:mistake[1],why:mistake[2]}),s('ex',task,{practiceId:`21.${d}.${p}.build`}),s('sol',undefined,{code:solution,out:output(solution),why:answer}),s('ex','Mini challenge: '+challenge,{practiceId:`21.${d}.${p}.challenge`}),s('sol',undefined,{code:'# Design/retrieval answer; use the runnable solution above as your starting point.',why:answer}),s('try',undefined,{q:q[0],code:'# Predict and explain before revealing.',a:q[1],why:q[4]}),s('checkpoint',undefined,{lesson:{id:`course:21.${d}.${p}`,quiz:[{q:q[0],options,correct,why:q[4]}]}}),s('key',goal+' Explain the rule aloud, then write the example again without a template.') ]});
}
add(0,'1. Dataclasses: useful methods from declared fields','Replace repetitive record-class methods without hiding the domain rules.',[
 ['dataclasses module; @dataclass','A standard-library decorator generates methods such as __init__, __repr__ and __eq__ from declared fields. No pip package is needed.'],
 ['field annotation: name: str','The colon declares the intended field type; it is not an assignment or runtime validation. Day 2 explains annotations fully.']
],'Week 18 taught manual constructors; Week 20 taught repr and equality. A dataclass automates those repetitive pieces for a class whose main job is holding data. Methods you write still belong to the same ordinary class. Start with records, not every service in an application. Use Python 3.10 or newer for all this week’s examples.','from dataclasses import dataclass\n\n@dataclass\nclass Record:\n    name: str\n    count: int = 0',`from dataclasses import dataclass

@dataclass
class Book:
    title: str
    pages: int
    finished: bool = False

a = Book("Python", 120)
b = Book("Python", 120)
print(a)
print(a == b, a is b)
b.finished = True
print(a == b)`,'Book("Python",120) calls the generated constructor. Generated repr includes field names. Equality compares fields for the same concrete dataclass type; identity still checks whether two references point to one object. Required fields precede fields with defaults.',['class Book:\n    title = str','@dataclass\nclass Book:\n    title: str','title = str assigns a class attribute; it does not declare a dataclass field.'],'Convert Student(name, score=0) into a dataclass; create two equal students, then change one score.',`from dataclasses import dataclass
@dataclass
class Student:
    name: str
    score: int = 0
a, b = Student("Sita"), Student("Sita")
print(a)
print(a == b)
b.score = 90
print(a == b)`,'Rewrite Book, Student and Ticket records from older weeks; compare the generated behaviour with your old __init__/repr/eq methods.','Use annotated fields, put required fields first, and retain any real business methods. Confirm value equality, separate identity, defaults, and repr. A shorter class is useful only when its behaviour is still clear.',['Does @dataclass enforce that pages is an integer?','No; type annotations alone do not validate runtime values.','Yes; all wrong values are rejected.','It converts every value to int.','Dataclasses discover fields through annotations but normally do not enforce their annotated types.']);
add(0,'2. Mutable defaults: each instance needs its own list','Give each record an independent mutable collection.',[
 ['field; default_factory','field customises a dataclass field. default_factory receives a zero-argument callable, such as list, and calls it for each new instance.'],
 ['list[str]','A generic annotation describing a list whose elements are strings. Built-in collection type parameters work in Python 3.9+.']
],'Week 18 showed shared mutable class attributes. Dataclass defaults need the same care: a mutable list is not a safe shared default. Modern dataclasses reject many unhashable defaults. The factory solves ownership without requiring callers to remember to pass a list.','tags: list[str] = field(default_factory=list)',`from dataclasses import dataclass, field
@dataclass
class Notebook:
    owner: str
    pages: list[str] = field(default_factory=list)
a, b = Notebook("Sita"), Notebook("Hari")
a.pages.append("OOP notes")
print(a.pages)
print(b.pages)
print(a.pages is b.pages)`,'Pass list itself, not list(). A new empty list is made for each omitted pages argument. A caller-supplied list is not automatically copied: decide and document that ownership separately.',['pages: list[str] = []','pages: list[str] = field(default_factory=list)','A literal list would be a shared mutable default and is rejected by current dataclasses. default_factory=list() is also wrong: the factory must be callable.'],'Make Team(name, members) with an independent default list; add a member to only one team.',`from dataclasses import dataclass, field
@dataclass
class Team:
    name: str
    members: list[str] = field(default_factory=list)
a, b = Team("A"), Team("B")
a.members.append("Sita")
print(a.members, b.members)`,'Give each ShoppingList its own items list and explain the difference between an omitted list and one explicitly passed by the caller.','The factory handles omitted values only. For explicit mutable input, either document sharing or copy it in a normal constructor/post-init. Test that modifying A’s default collection never changes B.',['Which value should default_factory receive for a new list?','list','list()','[]','The callable list creates a fresh object every time the generated constructor needs a default.']);
add(0,'3. Validation, frozen records and honest limitations','Separate construction checks from later mutation rules.',[
 ['__post_init__','A hook called after a generated dataclass __init__. Use it for initial validation or derived setup.'],
 ['frozen=True; FrozenInstanceError','Frozen records reject ordinary field reassignment. This is shallow read-only behaviour, not deep immutability or security.'],
 ['replace','dataclasses.replace builds another instance with selected field values changed and runs its constructor/post-init.']
],'A dataclass does not make impossible data valid. __post_init__ can reject negative stock initially, but a mutable dataclass can still receive an invalid later assignment. Use a frozen snapshot or a carefully designed service/property when invariants must always hold.','@dataclass(frozen=True)\nclass Snapshot:\n    quantity: int\n    def __post_init__(self):\n        ...',`from dataclasses import dataclass, replace, FrozenInstanceError
@dataclass(frozen=True)
class Stock:
    quantity: int
    def __post_init__(self):
        if type(self.quantity) is not int or self.quantity < 0:
            raise ValueError("nonnegative integer required")
a = Stock(3)
b = replace(a, quantity=5)
print(a.quantity, b.quantity)
try: a.quantity = 9
except FrozenInstanceError: print("assignment refused")
try: Stock(-1)
except ValueError as error: print(error)`,'The old snapshot remains 3; replace creates a checked new snapshot. A frozen record containing a list could still have that list mutated. Prefer immutable field values such as tuples for snapshots; do not add unsafe_hash merely to silence an error.',['Check only in __post_init__, then permit any quantity assignment.','Use frozen snapshots or checked updates when invariants matter.','Initial validation does not automatically rerun after mutable field assignments.'],'Create frozen Point(x,y), then use replace to move x without changing the original.',`from dataclasses import dataclass, replace
@dataclass(frozen=True)
class Point:
    x: int
    y: int
a = Point(2, 3)
b = replace(a, x=7)
print(a, b)`,'Explain why a frozen dataclass with a list field is not deeply immutable; redesign its field as a tuple.','replace returns a different checked instance. Frozen prevents ordinary field rebinding but cannot freeze the contents of nested mutable objects. Prefer simple immutable snapshot fields and validate at their boundary.',['Does frozen=True prevent changes inside a list field?','No; freezing is shallow.','Yes; every nested value is frozen.','It encrypts the list.','Ordinary attribute assignment is blocked, while mutable objects referenced by fields can still change.']);
add(1,'1. Type hints: document inputs and results','Read and write annotations without confusing them with validation.',[
 ['parameter annotation; -> return annotation','name: str describes the expected input; -> str describes the intended result. A function returning no useful result uses -> None.'],
 ['static type checking','A checker analyses annotated code without running it. Python still needs runtime checks for untrusted values.']
],'Types describe the shape of values; validation checks domain rules such as stock >= 0. def greet(name: str) -> str is still an ordinary function. Hints help tools catch mistakes before execution but do not cast arguments, validate ranges, or prove the program correct.','def greet(name: str) -> str:\n    return "Hello " + name',`def label(name: str, count: int) -> str:
    return f"{name}: {count}"
def log(text: str) -> None:
    print(text)
log(label("Books", 3))
# This is deliberately type-incorrect but still executes:
print(label("Books", "many"))`,'The second call violates the hint but f-string formatting accepts a string, so Python prints it. A static checker reports the wrong argument. Do not copy the deliberately wrong call into your typed module.',['def total(prices: list[int]) -> str: return sum(prices)','def total(prices: list[int]) -> int: return sum(prices)','The return annotation must describe the returned value, not the display format you intend to print later.'],'Annotate subtotal, discount, total, label and announce. Use integer amounts and explicitly mark the print-only function -> None.',`def subtotal(prices: list[int]) -> int: return sum(prices)
def discount(amount: int, reduction: int) -> int: return amount - reduction
def total(prices: list[int], reduction: int) -> int:
    return discount(subtotal(prices), reduction)
def label(amount: int) -> str: return f"Total: {amount}"
def announce(text: str) -> None: print(text)
announce(label(total([100, 50], 20)))`,'Save the five functions as typed_receipt.py, then run python -m mypy --strict typed_receipt.py after installing mypy if needed. Deliberately pass a string where an int belongs and compare checker output with execution.','These five functions form a small complete typed module. Hints express the input/output contract, while validation remains separate. Read the Day 2 final part for mypy setup; installing the tool initially needs a connection, running it afterward can be offline.',['Does Python automatically reject label("Books", "many") because count is annotated int?','No; annotations are not automatically enforced.','Yes; the call is blocked.','It silently converts many to an integer.','The deliberately incorrect call runs because the function body can handle string formatting; a checker catches the mismatch.']);
add(1,'2. Collections, unions and narrowing None','Handle missing values before using them.',[
 ['dict[str, int]; tuple[str, int]','Collection annotations describe element shapes; tuple[str,int] means a two-position tuple with those respective types.'],
 ['int | None; Optional[int]; Union[int, str]','A union permits more than one type. int | None (Python 3.10+) means int or None, equivalent to Optional[int]. Optional does not mean the argument can simply be omitted.'],
 ['type narrowing','A branch such as if value is None separates the missing case; afterward a checker can treat the remaining value as int.']
],'A dictionary lookup may fail to find a key; express that possibility instead of pretending the value always exists. A parameter without a default is still required even if its type includes None. Use narrow, meaningful types rather than adding Any to hide errors.','def lookup(name: str) -> int | None:\n    ...\nvalue = lookup("Python")\nif value is not None:\n    ...',`from typing import Optional, Union
def find_stock(name: str, stock: dict[str, int]) -> Optional[int]:
    return stock.get(name)
stock = {"Book": 3}
for name in ("Book", "Pen"):
    value = find_stock(name, stock)
    if value is None:
        print(name, "missing")
    else:
        print(name, value + 1)
def show(code: Union[int, str]) -> str: return str(code)
print(show(7), show("A7"))`,'The missing branch uses identity with None, not a truthiness check: zero stock is a real value, not a missing entry. Built-in generics are notation, not new list/dict objects. Optional and Union come from typing; modern | spelling is an alternative.',['if not value: print("missing")','if value is None: print("missing")','A stock of zero is falsy but is not the same as a missing item.'],'Write find_score(name, scores) -> int | None; show that zero is found while an absent key is missing.',`def find_score(name: str, scores: dict[str, int]) -> int | None:
    return scores.get(name)
for name in ("Sita", "Hari"):
    score = find_score(name, {"Sita": 0})
    print("missing" if score is None else f"score={score}")`,'Write a function with argument count: int | None and no default. Explain why calling it with no argument still fails.','A type union describes values, not parameter omission. Only a default such as count=None makes that argument optional at the call site. Always distinguish None from valid zero/empty values.',['What does Optional[int] mean?','An int or None.','An argument that can always be omitted.','Only positive integers.','Optional[int] is a union with None; call-site defaults are a separate feature.']);
add(1,'3. Mypy and typed interfaces: tools, not magic','Check a typed module and express a behaviour contract.',[
 ['mypy; --strict','A third-party static checker. Strict mode checks more annotations; it does not execute tests or validate business rules.'],
 ['Protocol','typing.Protocol describes the methods a value must provide; implementations can satisfy the contract without inheriting from it. This is static structural typing.'],
 ['generic type parameter','list[int] reuses one collection shape for a particular element type. You do not need to define a custom generic class yet.']
],'Use one small fully annotated file first. If mypy is not installed, python -m pip install mypy needs internet once; do not make the offline lesson depend on that download. After installation run python -m mypy --strict typed_receipt.py. Fix the reported file/line rather than suppressing every error. Protocol extends Week 19 duck typing with a tool-readable contract.','class Store(Protocol):\n    def count(self, name: str) -> int | None:\n        ...',`from typing import Protocol
class Store(Protocol):
    def count(self, name: str) -> int | None: ...
class MemoryStore:
    def __init__(self) -> None: self.stock: dict[str, int] = {"Book": 3}
    def count(self, name: str) -> int | None: return self.stock.get(name)
def display(store: Store, name: str) -> str:
    count = store.count(name)
    return "missing" if count is None else f"{name}: {count}"
print(display(MemoryStore(), "Book"))`,'The ... is an ellipsis placeholder in the interface stub, not a working implementation. MemoryStore satisfies the count contract without inheriting Store. Protocol is not a runtime validator and is not automatically suitable for isinstance checks.',['Use isinstance(value, Store) for every ordinary Protocol.','Let the checker verify the contract; validate actual data separately.','Ordinary Protocols are primarily static; runtime_checkable is a separate feature and still does not check full signatures.'],'Define a Printer Protocol with write(text: str) -> None; implement ConsolePrinter and use it through an annotated function.',`from typing import Protocol
class Printer(Protocol):
    def write(self, text: str) -> None: ...
class ConsolePrinter:
    def write(self, text: str) -> None: print(text)
def announce(printer: Printer, message: str) -> None:
    printer.write(message)
announce(ConsolePrinter(), "Ready")`,'Type-check the five receipt functions and this interface. Add an implementation whose write returns an integer and explain why the stated contract no longer matches.','The type checker should reject the incompatible implementation when passed as Printer. Runtime tests are still required: even a fully typed program can calculate the wrong answer.',['What does mypy do when checking a module?','Analyses its types without running its program.','Runs every business operation.','Automatically adds input validation.','Static checking and execution test different aspects of a program.']);
add(2,'1. Single responsibility: reasons to change','Give calculation and formatting different owners.',[
 ['SOLID; Single Responsibility Principle (SRP)','SOLID names five design guidelines. SRP asks a component to own a coherent responsibility: a change in presentation should not force a change in calculation.']
],'A class with many methods is not automatically bad; a class with unrelated reasons to change becomes hard to maintain. Start with the behaviour that actually differs. Do not create a class for every line of code: a pure calculation or formatter can remain a function.','class Invoice:\n    def total(self): ...\n\ndef format_invoice(invoice): ...',`class Invoice:
    def __init__(self, prices): self.prices = list(prices)
    def total(self): return sum(self.prices)
def plain_text(invoice): return f"Total: {invoice.total()}"
def compact_text(invoice): return f"TOTAL={invoice.total()}"
invoice = Invoice([100, 40])
print(plain_text(invoice))
print(compact_text(invoice))`,'Both formatters use the same arithmetic. A new display format does not require a new invoice subclass or a changed total algorithm. The copied prices list makes ownership explicit.',['Put file saving, email sending and arithmetic into one total() method.','Calculate in total(); pass the result to separate output code.','Mixing I/O with calculation makes tests depend on unrelated services.'],'Split a student average calculation from its human-readable grade report.',`def average(grades):
    if not grades: return 0.0
    return sum(grades) / len(grades)
def report(name, grades): return f"{name}: {average(grades):.1f}"
print(average([70, 90]))
print(report("Sita", [70, 90]))`,'Review a class from Week 18: list its reasons to change, then move only one unrelated formatting concern out of it.','Keep the numerical function independently testable, then have the formatter consume its result. Refactor one responsibility at a time, preserving outputs with tests.',['Which change should not require editing the total calculation?','Changing the report format.','Changing the tax calculation rule.','Changing the arithmetic definition.','Presentation and arithmetic have different reasons to change.']);
add(2,'2. Open/closed and substitution: keep the promise','Extend behaviour through a stable contract and respect it.',[
 ['Open/Closed Principle (OCP)','Add a new implementation behind a stable contract when repeated changes justify that boundary. It does not forbid editing code or fixing bugs.'],
 ['Liskov Substitution Principle (LSP)','An implementation used in place of another must uphold the caller’s behavioural promise, not merely have matching method names.']
],'Week 19 taught substitutability. A delivery fee contract promises a nonnegative integer for a valid order. A subclass that returns a string or rejects ordinary valid orders breaks that promise. Do not build elaborate extension points for a single simple calculation.','def checkout(order, delivery):\n    return order + delivery.fee(order)',`class StandardDelivery:
    def fee(self, subtotal): return 20
class Pickup:
    def fee(self, subtotal): return 0
def checkout(subtotal, delivery):
    if subtotal < 0: raise ValueError("negative subtotal")
    return subtotal + delivery.fee(subtotal)
for policy in (StandardDelivery(), Pickup()):
    print(checkout(100, policy))`,'checkout stays stable as a pickup policy is added. Both policies preserve the documented units and nonnegative fee result. A method returning "free" would force callers to special-case it.',['class Pickup:\n    def fee(self, subtotal): return "free"','class Pickup:\n    def fee(self, subtotal): return 0','Matching method names is insufficient when the result violates the arithmetic contract.'],'Add ExpressDelivery with fee 40 and test it through the same checkout caller.',`class ExpressDelivery:
    def fee(self, subtotal): return 40
def checkout(subtotal, delivery): return subtotal + delivery.fee(subtotal)
assert checkout(100, ExpressDelivery()) == 140
print("same caller, new policy")`,'Write a deliberately broken delivery implementation; identify whether it changes result type, input requirements or an expected guarantee.','A contract describes valid inputs, output meaning and side effects. Substitution is about keeping those promises. Add behaviour at the existing seam, not by branching on every concrete class.',['What would violate this delivery contract?','Returning a string instead of an integer fee.','Adding another valid policy.','Returning zero for pickup.','The caller expects nonnegative integer fee units and performs integer arithmetic.']);
add(2,'3. Small interfaces and dependency inversion','Let core rules receive collaborators they can replace.',[
 ['Interface Segregation Principle (ISP)','Clients should depend on the operations they actually need; a read-only report should not require delete/save methods.'],
 ['Dependency Inversion Principle (DIP); dependency injection','Core logic depends on a useful contract rather than constructing a particular database or printer inside itself. Injection means passing that collaborator in.']
],'A report needs values, not a full database administration API. Receive a small reader. A memory reader can test the same report without a database, credentials or network. Do not confuse dependency injection with a framework: an ordinary constructor argument is enough.','class Report:\n    def __init__(self, reader):\n        self.reader = reader',`class MemoryReader:
    def values(self): return [10, 20, 30]
class Report:
    def __init__(self, reader): self.reader = reader
    def average(self):
        values = self.reader.values()
        if not values: return 0.0
        return sum(values) / len(values)
print(Report(MemoryReader()).average())`,'Report knows only values(). A different file reader could provide the same promise. Keep connections and persistence outside the pure calculation; inject the collaborator at the program’s assembly point.',['self.reader = ProductionDatabase()  # inside Report','def __init__(self, reader): self.reader = reader','Constructing a concrete dependency inside core rules couples the report to that implementation.'],'Test Report with an EmptyReader, without inheriting a huge database interface.',`class EmptyReader:
    def values(self): return []
class Report:
    def __init__(self, reader): self.reader = reader
    def average(self):
        values = self.reader.values()
        return sum(values) / len(values) if values else 0.0
assert Report(EmptyReader()).average() == 0.0
print("empty report checked")`,'Explain all five SOLID letters using the invoice/delivery/report examples; name one place where a plain function is still the simplest design.','S: separate calculation/presentation. O: add delivery policies. L: preserve fee behaviour. I: a reader exposes only needed operations. D: receive a reader instead of constructing a database. These guidelines are judgement tools, not a requirement to multiply classes.',['How can Report be tested without a real database?','Pass a small fake reader with the same values() contract.','Disable the calculation.','Make every report connect to production.','Constructor injection separates core rules from the mechanism used to obtain data.']);
add(3,'1. Strategy: swap an algorithm deliberately','Change one policy without rewriting the service.',[
 ['Strategy pattern','Represent interchangeable algorithms behind a consistent call shape. Python functions can be strategies; a separate hierarchy is not always necessary.'],
 ['Callable[[int], int]','typing.Callable describes a callable with one integer argument returning an integer. Passing fee differs from calling fee(...).']
],'When only one calculation changes, pass that calculation. A delivery function can be changed without touching checkout. A class-based strategy is useful if the policy has its own state; a function is enough for the following example.','def checkout(amount, fee_policy):\n    return amount + fee_policy(amount)',`from typing import Callable
def standard(amount: int) -> int: return 20
def free_over_100(amount: int) -> int: return 0 if amount >= 100 else 20
def checkout(amount: int, fee: Callable[[int], int]) -> int:
    return amount + fee(amount)
print(checkout(80, standard))
print(checkout(120, free_over_100))`,'Pass standard, not standard(80), so checkout receives the algorithm rather than its already-computed result. Both functions share units and parameter shape.',['checkout(80, standard(80))','checkout(80, standard)','The first call passes an int; the service expects a callable.'],'Add a fixed fee of 40 as a function strategy and verify the same checkout routine accepts it.',`def express(amount): return 40
def checkout(amount, fee): return amount + fee(amount)
assert checkout(50, express) == 90
print(checkout(50, express))`,'Make a strategy with state (a configurable minimum for free shipping). Decide whether a closure or a small callable/class method is clearer; justify the choice.','The service receives a compatible algorithm. Use stateful classes only when the policy owns meaningful configuration; keep result units and validation consistent.',['What should be passed as a strategy?','A callable implementing the agreed algorithm.','Only the integer it returned earlier.','The strategy’s printed name.','The caller needs to invoke the policy when it has the actual input.']);
add(3,'2. Factory: choose construction in one place','Centralise object selection while exposing a stable operation.',[
 ['Factory pattern; ValueError for unknown kind','A factory chooses and returns an object. It separates construction decisions from callers using the object, and refuses unsupported kinds explicitly.']
],'A small factory may be a function with two branches. A dictionary of classes or a factory hierarchy is optional, not required. The returned implementations must honour the same caller contract. Keep the factory close to program assembly.','def make_formatter(kind):\n    if kind == "text": return TextFormatter()\n    raise ValueError("unknown kind")',`class TextFormatter:
    def format(self, amount): return f"Total: {amount}"
class CompactFormatter:
    def format(self, amount): return f"TOTAL={amount}"
def make_formatter(kind):
    if kind == "text": return TextFormatter()
    if kind == "compact": return CompactFormatter()
    raise ValueError("unknown formatter")
for kind in ("text", "compact"):
    print(make_formatter(kind).format(100))
try: make_formatter("other")
except ValueError as error: print(error)`,'The caller asks for format(amount), not a concrete type. Unknown input fails early instead of returning None and crashing at a distant method call.',['return None  # for unknown formatter','raise ValueError("unknown formatter")','A clear construction error is easier to diagnose than a later None.format failure.'],'Make a greeting factory returning FormalGreeting or FriendlyGreeting, both with greet(name).',`class FormalGreeting:
    def greet(self, name): return f"Welcome, {name}."
class FriendlyGreeting:
    def greet(self, name): return f"Hi {name}!"
def make_greeting(kind):
    if kind == "formal": return FormalGreeting()
    if kind == "friendly": return FriendlyGreeting()
    raise ValueError("unknown greeting")
print(make_greeting("friendly").greet("Sita"))`,'Add a new formatter, update only the construction choice, and prove existing callers still use format(amount) unchanged.','A factory chooses construction; strategy chooses an algorithm. They can work together but solve different problems. Every constructed object must preserve the operation the caller depends on.',['Where should unknown factory input be rejected?','At the factory boundary.','After a random method call fails.','Never; silently choose any object.','Failing early gives the caller a clear error at the source of the wrong selection.']);
add(3,'3. Observer: notify listeners after a real change','Keep notifications separate from the state transition.',[
 ['Observer pattern; subscribe/unsubscribe','An object publishes changes to registered listeners. Listeners react independently; unsubscribe removes a registration.'],
 ['listener snapshot','Copy the listener list for one notification pass so callbacks changing registrations do not corrupt the current traversal.']
],'Think of a stock change notifying a screen and an audit recorder. The notifier should not know the details of every listener. Define delivery policy: this simple implementation calls synchronously, permits each listener only once, and propagates listener errors. It is not a durable event queue.','for listener in list(self._listeners):\n    listener(event)',`class Signal:
    def __init__(self): self._listeners = []
    def subscribe(self, listener):
        if listener not in self._listeners: self._listeners.append(listener)
    def unsubscribe(self, listener):
        if listener in self._listeners: self._listeners.remove(listener)
    def emit(self, event):
        for listener in list(self._listeners): listener(event)
def display(event): print("screen:", event)
def audit(event): print("audit:", event)
signal = Signal()
signal.subscribe(display)
signal.subscribe(audit)
signal.emit("stock=3")
signal.unsubscribe(display)
signal.emit("stock=2")`,'The first event reaches both listeners; the second reaches only audit. Pass a listener function without calling it. In a production system decide how callback errors and ordering affect delivery.',['for listener in self._listeners: listener(event)  # callbacks modify this list','for listener in list(self._listeners): listener(event)','A snapshot makes registrations during callbacks take effect on later emits, not unpredictably within this pass.'],'Subscribe a recorder list through a callback, emit two events, unsubscribe, and show no third event is recorded.',`class Signal:
    def __init__(self): self.listeners = []
    def subscribe(self, listener): self.listeners.append(listener)
    def unsubscribe(self, listener): self.listeners.remove(listener)
    def emit(self, event):
        for listener in list(self.listeners): listener(event)
events = []
def record(event): events.append(event)
signal = Signal()
signal.subscribe(record)
signal.emit("A")
signal.emit("B")
signal.unsubscribe(record)
signal.emit("C")
print(events)`,'Make a listener unsubscribe itself during notification. Predict which listeners receive the current event and which receive the next one.','Each emission walks a copied registration list. Changes to registration apply to subsequent emissions. Keep the policy explicit; durable delivery, retries and async queues are later topics.',['Why copy listeners for an emission?','Callbacks may change registrations during the pass.','To permanently double every listener.','To hide events from listeners.','Walking a snapshot avoids skipping or revisiting entries when callbacks mutate the live registration list.']);
add(3,'4. Singleton: recognise it and understand the trade-off','Prefer explicit shared dependencies over hidden global state.',[
 ['Singleton pattern','A design intends one shared instance in some scope. A Python module can hold a shared instance, but that does not guarantee one instance across processes.'],
 ['global state; test isolation','Hidden shared mutable state lets one caller/test affect another. Passing a shared dependency explicitly makes that relationship visible.']
],'Learn what singleton means, but do not implement a clever __new__ trick just to use the name. If one configuration object is intentionally shared by two services, create it once at assembly and pass it to both. For independent tests create independent configuration objects.','config = Config()\nfirst = Service(config)\nsecond = Service(config)',`class Config:
    def __init__(self, currency): self.currency = currency
class Report:
    def __init__(self, config): self.config = config
shared = Config("JPY")
a, b = Report(shared), Report(shared)
isolated = Report(Config("NPR"))
print(a.config is b.config)
print(a.config.currency, isolated.config.currency)`,'This demonstrates explicitly shared lifetime rather than enforced singleton identity. The design remains testable because callers can inject a separate object. If configuration should be immutable, a frozen record is often appropriate.',['Make every constructor silently read and change one global config.','Create dependencies at assembly and pass them to users.','Hidden mutable singletons make tests order-dependent and hide ownership.'],'Create two services sharing one config and a third with its own config; explain scope and lifetime.',`class Config:
    def __init__(self, language): self.language = language
class Service:
    def __init__(self, config): self.config = config
c = Config("ja")
a, b, other = Service(c), Service(c), Service(Config("ne"))
assert a.config is b.config
assert other.config is not c
print("shared deliberately, isolated deliberately")`,'Compare factory, strategy, observer and singleton: name the problem each solves and one situation where it would be unnecessary.','Factory selects construction; strategy varies calculation; observer distributes notification; singleton concerns one shared instance/lifetime. A shared injected dependency often gives the required reuse without enforcing global identity.',['What is a common risk of a mutable singleton?','Hidden state leaking between callers or tests.','Every caller gets an independent copy automatically.','It guarantees correct business logic.','Shared mutable lifetime can make behaviour depend on earlier calls.']);
add(4,'1. Enum: name a finite set of states','Replace typo-prone status strings with explicit members.',[
 ['Enum; member; .name and .value','enum.Enum declares a finite set of named members. .name is its Python identifier and .value is the chosen underlying value.'],
 ['module constant; naming convention','UPPER_CASE communicates a constant but does not prevent reassignment. Enums model choices; unrelated numerical constants need not become enums.']
],'Use an enum for NEW/CONFIRMED/CANCELLED, not for every ordinary piece of text. A named status is different from its string value. At input/output boundaries, convert deliberately. Enum rejects unknown underlying values instead of silently accepting a typo.','class Status(Enum):\n    NEW = "new"\n    CONFIRMED = "confirmed"',`from enum import Enum
class Status(Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
s = Status("confirmed")
print(s.name, s.value)
print(s is Status.CONFIRMED)
print(s == "confirmed")
try: Status("confirmd")
except ValueError: print("unknown status")`,'Membership is not string equality for this ordinary Enum. Store/serialize the explicit .value and reconstruct with Status(value). This example does not alter Study Hub’s existing storage schema.',['status = "confirmd"','status = Status.CONFIRMED','Named members reduce typo-prone magic strings; external text still needs boundary conversion.'],'Build Priority with low/normal/high values; reconstruct high from text and print its name.',`from enum import Enum
class Priority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
p = Priority("high")
print(p.name, p.value)`,'Choose which fields in an old project are finite states and which are free text; replace only the finite choices in a separate practice copy.','Enums express a finite vocabulary. Validate external values at the boundary, preserve a deliberate serialization format, and leave user names/descriptions as strings.',['How do you turn stored text "confirmed" into this enum?','Status("confirmed")','Status.name("confirmed")','Compare every status to a misspelled literal.','Enum construction finds the member with that underlying value and rejects unknown values.']);
add(4,'2. auto, unique and stable storage values','Separate internal symbolic choices from persistent identifiers.',[
 ['auto()','Requests automatically generated member values. For ordinary Enum these are normally incrementing integers; do not assume those numbers are stable storage identifiers.'],
 ['@unique; enum aliases','By default duplicate values can create aliases. @unique rejects duplicates when every state must be distinct.']
],'Internal options can use auto when the numeric values are irrelevant. If values go into saved files or an API, prefer explicit stable strings. Inserting or rearranging members must not accidentally reinterpret old stored numbers.','@unique\nclass Action(Enum):\n    START = auto()\n    STOP = auto()',`from enum import Enum, auto, unique
@unique
class Action(Enum):
    START = auto()
    STOP = auto()
print([member.name for member in Action])
print(Action.START != Action.STOP)
class SavedStatus(Enum):
    NEW = "new"
    DONE = "done"
print(SavedStatus.DONE.value)`,'The output deliberately avoids depending on generated numeric values. @unique checks the class definition. Explicit text values are clearer when compatibility matters.',['Save Action.START.value as a permanent identifier without a policy.','Use explicit stable values for persistent states.','auto is convenient for internal symbols, not a migration plan for stored data.'],'Make a unique InternalMode with READ/WRITE using auto; separately define SavedMode with explicit text values.',`from enum import Enum, auto, unique
@unique
class InternalMode(Enum):
    READ = auto()
    WRITE = auto()
class SavedMode(Enum):
    READ = "read"
    WRITE = "write"
print(InternalMode.READ.name)
print(SavedMode.WRITE.value)`,'Explain why changing a persisted state vocabulary needs a migration even if the enum definition is only three lines.','Old saved values must continue to mean the same thing. Explicit stable values, boundary parsing and compatibility tests matter more than convenient automatic numbering.',['Which values are safer for a long-lived saved status format?','Explicit stable values with a documented meaning.','Whatever auto generates after each edit.','The displayed index in a dropdown.','Persistent data needs stable identifiers, not incidental definition order.']);
add(4,'3. State transitions: allowed values are not enough','Validate the change as well as the status.',[
 ['state transition; transition table','A state machine defines which changes are legal. An enum lists states but does not enforce allowed transitions by itself.']
],'NEW may become CONFIRMED or CANCELLED. A CANCELLED booking cannot be confirmed again in this policy. Reject the requested transition before mutating state. State-machine policy is a business decision; write it down rather than guessing from enum order.','if target not in allowed[current]:\n    raise ValueError("invalid transition")',`from enum import Enum
class Status(Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
class Booking:
    def __init__(self): self.status = Status.NEW
    def transition(self, target):
        allowed = {Status.NEW: {Status.CONFIRMED, Status.CANCELLED},
                   Status.CONFIRMED: {Status.CANCELLED}, Status.CANCELLED: set()}
        if target not in allowed[self.status]: raise ValueError("invalid transition")
        self.status = target
b = Booking()
b.transition(Status.CONFIRMED)
b.transition(Status.CANCELLED)
try: b.transition(Status.CONFIRMED)
except ValueError as error: print(error)
print(b.status.value)`,'The final state stays cancelled after a rejected request. Enum members are useful dictionary/set keys for an explicit transition table. Prevent callers from bypassing the method in a larger design by controlling access to the state.',['Set any enum value whenever a caller asks.','Check the transition policy before assignment.','An enum permits known values, not every possible sequence of those values.'],'Make Task states TODO/DONE with only TODO -> DONE allowed; prove a second completion is rejected.',`from enum import Enum
class State(Enum):
    TODO = "todo"
    DONE = "done"
class Task:
    def __init__(self): self.state = State.TODO
    def complete(self):
        if self.state is not State.TODO: raise ValueError("already completed")
        self.state = State.DONE
t = Task()
t.complete()
try: t.complete()
except ValueError as error: print(error)
print(t.state.value)`,'List valid transitions for a library loan and include an invalid transition test that confirms no state change.','Model the policy before code. Validate first, mutate second, and test both successful transitions and invalid transitions with preserved state.',['Does defining an Enum enforce legal transition order?','No; the application must implement transition rules.','Yes; enum order supplies all business rules.','Only if names are uppercase.','Enum specifies available choices, while a transition policy specifies legal changes.']);
add(5,'1. Safe refactoring: preserve observed behaviour first','Move code into objects without quietly changing its results.',[
 ['characterisation test','A test records what existing code does before restructuring. Refactoring preserves observable behaviour; bug fixes are separate deliberate changes.'],
 ['pure core; I/O boundary','Keep calculation/state rules testable without keyboard, file or network interactions. Connect I/O at the outer boundary.']
],'Week 16–17 taught small changes and tests. Start from a working function, write representative normal/empty/boundary tests, then extract a class only if ownership makes it useful. Do not change input formats, arithmetic and architecture all in one step.','expected = old_function(input)\nassert new_object.method(input) == expected',`def old_total(prices, fee=0): return sum(prices) + fee
class Receipt:
    def __init__(self, prices): self.prices = list(prices)
    def total(self, fee=0): return sum(self.prices) + fee
cases = [([], 0), ([100], 20), ([100, 40], 0)]
for prices, fee in cases:
    assert Receipt(prices).total(fee) == old_total(prices, fee)
print("3 compatibility cases passed")`,'The same values produce the same totals. These cases are not proof for every input, but they protect the behaviour being changed. Git commits let you review/refute one focused transformation.',['Refactor and change rounding/units/storage formats in one edit.','Record behaviour, restructure one boundary, then fix rules separately.','Mixed changes make it hard to tell whether a failure is an intended rule change or a regression.'],'Refactor old_average(grades) into GradeBook.average, preserving the empty-list result and ordinary averages.',`def old_average(grades): return sum(grades) / len(grades) if grades else 0.0
class GradeBook:
    def __init__(self, grades): self.grades = list(grades)
    def average(self): return sum(self.grades) / len(self.grades) if self.grades else 0.0
for grades in ([], [70], [60, 80]):
    assert GradeBook(grades).average() == old_average(grades)
print("average behaviour preserved")`,'Before refactoring your own 200-line script, identify one coherent responsibility and write five tests around that boundary. Move only that piece first.','Size alone is not the reason for a class. Find state ownership and rules, preserve caller-visible results, and keep unrelated fixes out of the refactoring commit.',['What should a pure refactoring preserve?','Observable behaviour covered by the stated contract.','Only the number of lines.','No tests are needed if names improve.','Refactoring changes structure; intentional behavioural fixes should be separately reviewed.']);

const project=`from dataclasses import dataclass, replace
from enum import Enum
from typing import Protocol, Callable

class Category(Enum):
    BOOK = "book"
    TOOL = "tool"

@dataclass(frozen=True)
class Item:
    sku: str
    name: str
    quantity: int
    category: Category

    def __post_init__(self) -> None:
        if not self.sku.strip() or not self.name.strip():
            raise ValueError("sku and name required")
        if type(self.quantity) is not int or self.quantity < 0:
            raise ValueError("quantity must be a nonnegative integer")
        if not isinstance(self.category, Category):
            raise TypeError("Category required")

class Repository(Protocol):
    def find(self, sku: str) -> Item | None: ...
    def save(self, item: Item) -> None: ...

class MemoryRepository:
    def __init__(self) -> None:
        self._items: dict[str, Item] = {}
    def find(self, sku: str) -> Item | None:
        return self._items.get(sku)
    def save(self, item: Item) -> None:
        self._items[item.sku] = item

def make_repository(kind: str) -> Repository:
    if kind == "memory":
        return MemoryRepository()
    raise ValueError("unknown repository")

def never_low(item: Item) -> bool:
    return False

def low_below_two(item: Item) -> bool:
    return item.quantity < 2

class Inventory:
    def __init__(self, repository: Repository,
                 low_policy: Callable[[Item], bool]) -> None:
        self._repository = repository
        self._low_policy = low_policy

    def add(self, item: Item) -> None:
        if self._repository.find(item.sku) is not None:
            raise ValueError("duplicate sku")
        self._repository.save(item)

    def get(self, sku: str) -> Item:
        item = self._repository.find(sku)
        if item is None:
            raise KeyError(sku)
        return item

    def remove(self, sku: str, amount: int) -> Item:
        if type(amount) is not int or amount <= 0:
            raise ValueError("positive integer amount required")
        current = self.get(sku)
        if amount > current.quantity:
            raise ValueError("not enough stock")
        updated = replace(current, quantity=current.quantity - amount)
        self._repository.save(updated)
        return updated

    def is_low(self, sku: str) -> bool:
        return self._low_policy(self.get(sku))

def render(item: Item) -> str:
    return f"{item.sku}: {item.name} / {item.quantity} / {item.category.value}"
`;
const demo=`
inventory = Inventory(make_repository("memory"), low_below_two)
inventory.add(Item("B1", "Python", 3, Category.BOOK))
old = inventory.get("B1")
updated = inventory.remove("B1", 2)
print(render(updated))
print(old.quantity, updated.quantity, inventory.is_low("B1"))
try:
    inventory.remove("B1", 2)
except ValueError as error:
    print(error)
print(inventory.get("B1").quantity)
`;
add(5,'2. Milestone project: a typed inventory system','Combine the week’s tools around one clear state owner.',[
 ['repository interface','A repository separates how records are found/saved from the business rules using them. This example is intentionally in-memory and offline; it is not persistent storage.'],
 ['immutable snapshot update','replace creates a new validated Item. Retaining an old Item reference does not let a caller mutate current stock through ordinary field assignment.']
],'Build in layers: Item data/validation, Repository contract, MemoryRepository mechanism, Inventory business rules, a low-stock strategy and a formatter. Read one class at a time. Every import and syntax feature has been introduced earlier this week. The factory assembles storage; the strategy determines low-stock policy. Do not add inheritance between unrelated layers.','Item -> Repository contract -> Inventory rules -> render(item)',project+demo,'The returned old snapshot stays at quantity 3 while the saved replacement becomes 1. Duplicate SKUs, missing keys, impossible amounts and insufficient stock are separate errors. All checks run before saving; no file/network access is involved. The category is an explicit enum, never an arbitrary status string.',['Update current.quantity directly and bypass checks.','Validate amount, construct replacement, then save.','Frozen snapshots and controlled updates make ownership and failed-operation behaviour clear.'],'Rebuild the inventory project from the contract. Add one TOOL item and use never_low as an alternative strategy.',project+`
inventory = Inventory(make_repository("memory"), never_low)
inventory.add(Item("T1", "Pen", 2, Category.TOOL))
print(render(inventory.remove("T1", 1)))
print(inventory.is_low("T1"))`,'Add a read-only stock_value report or a second low-stock policy. Decide which existing layer owns it; write an invalid-input and valid-input test before implementing.','A new policy belongs in a strategy, not duplicated removal logic. The report reads snapshots; the Inventory owns state-changing rules. Preserve the repository contract and test both implementations through the same callers.',['Which layer decides whether a stock removal is allowed?','Inventory business rules.','The text formatter.','An arbitrary external assignment.','The repository stores records; the service enforces business rules before changing them.']);
const checks=`
def expect_error(error_type, operation) -> None:
    try:
        operation()
    except error_type:
        return
    raise AssertionError("expected error was not raised")

inventory = Inventory(make_repository("memory"), low_below_two)
inventory.add(Item("B1", "Python", 3, Category.BOOK))
assert inventory.get("B1").quantity == 3
expect_error(ValueError, lambda: inventory.add(Item("B1", "Other", 9, Category.BOOK)))
assert inventory.get("B1").name == "Python"
expect_error(KeyError, lambda: inventory.get("missing"))
for bad in (0, -1, True, 1.5):
    expect_error(ValueError, lambda: inventory.remove("B1", bad))
    assert inventory.get("B1").quantity == 3
expect_error(ValueError, lambda: inventory.remove("B1", 4))
assert inventory.get("B1").quantity == 3
old = inventory.get("B1")
assert inventory.remove("B1", 2).quantity == 1
assert old.quantity == 3
assert inventory.is_low("B1")
assert inventory.remove("B1", 1).quantity == 0
expect_error(ValueError, lambda: Item("", "Book", 1, Category.BOOK))
expect_error(ValueError, lambda: Item("B2", "Book", -1, Category.BOOK))
expect_error(TypeError, lambda: Item("B2", "Book", 1, "book"))
expect_error(ValueError, lambda: make_repository("unknown"))
print("inventory success and failure checks passed")
`;
add(5,'3. Tests, type-checking and the full-week review','Verify the contract, state preservation and design decisions.',[
 ['boundary test; failure-state assertion','A rejected operation must raise the intended error and leave stored state unchanged. Test the resulting state as well as the exception.'],
 ['assertion; python -O caution','assert states a test expectation. Optimised Python (-O) can remove asserts, so do not use them as production input validation. The service uses real exceptions instead.']
],'The standalone checks below use Week 10 lambda to delay an operation until the error helper calls it; lambda is a small function, not an already-executed result. This helper catches only the expected exception. Run normal Python, not -O. For strict typing, save the project definitions plus demo as inventory.py and run python -m mypy --strict inventory.py. The simple error helper below is a runtime test scaffold, not the strict-typed project module.','assert result == expected\nexpect_error(ValueError, lambda: invalid_operation())',project+checks,'Checks cover add/find, duplicate preservation, missing items, zero/negative/bool/fractional removal, insufficient stock, unchanged state on failure, old snapshot stability, valid zero stock, low-stock strategy, invalid records and unknown factories. The helper is intentionally minimal; later pytest parametrisation can express these cases more compactly.',['Assert only that an error occurred; ignore final stock.','Assert both the intended error and unchanged state.','A broken operation may change state and then raise, which exception-only tests miss.'],'Write a second inventory with never_low and prove one inventory does not affect the other; run the same repository contract checks against it.',project+`
a = Inventory(make_repository("memory"), low_below_two)
b = Inventory(make_repository("memory"), never_low)
a.add(Item("B1", "Python", 1, Category.BOOK))
b.add(Item("B1", "Python", 5, Category.BOOK))
assert a.is_low("B1") and not b.is_low("B1")
a.remove("B1", 1)
assert b.get("B1").quantity == 5
print("independent inventories and strategies passed")`,'Full-week recall: explain dataclass defaults/frozen, type hints vs validation, Optional vs omitted arguments, all five SOLID letters, the four patterns, stable enum values and safe refactoring. Rebuild Item/Repository/Inventory without a template and test one success and three failures.','Separate dependencies and state so tests cannot leak into each other. Run type checking and runtime tests: neither substitutes for the other. Day 7 remains review/rest; repeat any weak part before Week 22 regular expressions.',['What extra assertion matters after a rejected removal?','Stored quantity is unchanged.','Only that the repr looks shorter.','Only that mypy is installed.','Exception correctness and state preservation together establish the rejection contract.']);

const days={};
for(let d=0;d<6;d++)days['21.'+d]={parts:units.filter(u=>u.day===d).map(u=>({title:u.title,sections:u.sections}))};
days['21.1'].parts.at(-1).sections.push(s('sh','python -m pip install mypy\npython -m mypy --strict typed_receipt.py',{note:'Optional tool setup: installation needs internet once. The lessons and standard-library examples are offline. Run the second line from the folder containing your saved file.'}));
days['21.5'].parts.at(-1).sections.push(s('p','Suggested Git sequence for your practice project: git init, add the working baseline and tests, commit; refactor one responsibility, rerun checks, commit; finally add a deliberate new feature in a separate commit. Never put credentials in source. This is for a separate practice folder, not an instruction to reset Study Hub.'),s('p','Optional official references: https://docs.python.org/3/library/dataclasses.html · https://docs.python.org/3/library/typing.html · https://docs.python.org/3/library/enum.html · https://mypy.readthedocs.io/en/stable/getting_started.html. All explanations and examples are included here for offline study.'),s('key','Week 21 checkpoint: build a checked record, annotate a small module, inject a collaborator, choose a useful pattern, model stable states, and refactor with preserved behaviour. Study the parts at your own pace.'));
const target=path.join(__dirname,'..','study-hub.html');
const html=fs.readFileSync(target,'utf8').replace(/\r\n/g,'\n'),start=html.indexOf('const DAY_TEACH = '),end=html.indexOf('\n};\n\nconst REST_DAY',start);
if(start<0||end<0)throw Error('Missing teaching boundaries');
const old=Function('return ('+html.slice(start+18,end+2)+')')();
if(Object.keys(days).some(k=>old[k]))throw Error('Week21 already authored; refuse overwrite');
const addition=Object.entries(days).map(([k,v])=>JSON.stringify(k)+': '+JSON.stringify(v,null,2)+',').join('\n');
const result=html.slice(0,end).replace(/\s*$/,'').replace(/,?$/,',')+'\n'+addition+html.slice(end);
for(const m of result.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
fs.writeFileSync(target+'.tmp',result,'utf8');fs.renameSync(target+'.tmp',target);
const artifact=path.join(__dirname,'..','docs','python-week21-inventory.py');
fs.writeFileSync(artifact,project+demo,'utf8');
console.log(`Added Week21: 6 days, ${units.length} parts, ${units.length*2} practice prompts, ${units.length} quizzes; ${units.length*2} examples executed before atomic write.`);
