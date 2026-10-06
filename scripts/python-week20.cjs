// Additive authoring only: existing teaching and storage are never rewritten.
const fs=require('fs'),path=require('path');
const target=path.join(__dirname,'..','study-hub.html');
const S=(t,v,extra={})=>({t,v,...extra});
const units=[];
function unit(day,title,objective,concept,explanation,code,out,walk,mistake,task,solution,solutionOut,quiz){
  units.push({day,title,sections:[S('h',title),S('key','Learning objective: '+objective),S('new',concept,{note:explanation}),S('p',explanation),S('syn',code.split('\n').slice(0,Math.min(5,code.split('\n').length)).join('\n'),{note:'Read the complete executable example below; this preview shows the shape of the definition.'}),S('code',code),S('out',out),S('p',walk),S('mis',undefined,{wrong:mistake[0],right:mistake[1],why:mistake[2]}),S('ex',task),S('sol',undefined,{code:solution,out:solutionOut,why:'Trace the initial state, each operation, and the final result. '+walk}),S('try',undefined,{q:'Explain before running: '+quiz[0],code:'# Recall the rule before opening the answer.',a:quiz[1],why:quiz[2]}),S('key',objective+' Say why the design is useful, not just what the syntax looks like.'),S('checkpoint',undefined,{lesson:{id:'course:20.'+day+'.'+units.filter(u=>u.day===day).length,quiz:[{q:quiz[0],options:[quiz[1],quiz[3],quiz[4]],correct:0,why:quiz[2]}]}})]});
}
unit(0,'1. Encapsulation: state and rules together','Keep an account valid through operations, not arbitrary assignments.','invariant; public API; _non_public convention','An invariant is a rule that must remain true: balance >= 0. Encapsulation puts data and the operations enforcing that rule in one class. Python has no enforced protected keyword: _balance asks callers to use the public methods. It does not block access or secure secrets. Review classes in Week 18 and exceptions in Week 14 first.',`class BankAccount:
    def __init__(self, balance=0):
        if balance < 0:
            raise ValueError("negative opening balance")
        self._balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0 or amount > self._balance:
            raise ValueError("invalid withdrawal")
        self._balance -= amount

    def balance(self):
        return self._balance

a = BankAccount(100)
a.deposit(20)
a.withdraw(35)
print(a.balance())
try:
    a.withdraw(100)
except ValueError as error:
    print(error)
print(a.balance())`,'85\ninvalid withdrawal\n85','Validation runs before mutation. A failed withdrawal leaves the old balance intact. These integer units are simplified money; real currency needs a precise units/currency policy.',['a._balance = -100','a.withdraw(100)','An underscore communicates an internal field. Calling the checked method preserves the invariant.'],'Write a Counter starting at zero. add(amount) rejects nonpositive values before mutation. Show one accepted and one rejected update.',`class Counter:
    def __init__(self): self._value = 0
    def add(self, amount):
        if amount <= 0: raise ValueError("positive only")
        self._value += amount
    def value(self): return self._value
c = Counter()
c.add(3)
try: c.add(-2)
except ValueError as error: print(error)
print(c.value())`,'positive only\n3',['Does _balance prevent outside code from accessing it?','No; it is a convention.','Python trusts callers to respect a non-public API.','Yes; it is encrypted.','Yes; Python blocks all access.']);
unit(0,'2. Double underscores prevent accidental name clashes','Distinguish name mangling from access control.','__name; name mangling','A field named __value inside Base becomes _Base__value. This reduces accidental collisions in subclasses; it is not encryption, authentication, or a place to hide passwords. Names ending with two underscores, such as __init__, are protocol names rather than this convention.',`class Base:
    def __init__(self): self.__value = 10
    def base_value(self): return self.__value
class Child(Base):
    def __init__(self):
        super().__init__()
        self.__value = 20
c = Child()
print(c.base_value())
print(c._Child__value)
print(c._Base__value)`,'10\n20\n10','Base and Child have separate fields. The direct mangled access here is a demonstration, not the recommended caller API.',['Store a password in self.__password to keep it secret.','Keep credentials out of published source and use appropriate authentication.','Name mangling offers no confidentiality.'],'Build Parent and Child with separate __label values and public reader methods; print both.',`class Parent:
    def __init__(self): self.__label = "parent"
    def parent_label(self): return self.__label
class Child(Parent):
    def __init__(self):
        super().__init__()
        self.__label = "child"
    def child_label(self): return self.__label
c = Child()
print(c.parent_label(), c.child_label())`,'parent child',['What is the purpose of __value name mangling?','Avoid accidental subclass name collisions.','The class name is included in the stored attribute name.','Encrypt private data.','Stop every outside read.']);
unit(1,'1. Properties: a method behind attribute access','Read a computed value without storing duplicate state.','@property; getter; decorator','@property turns a getter method into attribute-style access. Read rectangle.area, not rectangle.area(). The @ line applies a decorator (Week 10). Compute derived values from their source fields so they cannot become stale.',`class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    @property
    def area(self):
        return self.width * self.height
r = Rectangle(3, 4)
print(r.area)
r.width = 5
print(r.area)`,'12\n20','Python calls the getter on each access. This first example demonstrates computation only; it does not validate dimensions yet.',['print(r.area())','print(r.area)','The getter result is a number, not a callable method.'],'Give Circle a read-only diameter computed from radius. Change radius and demonstrate that diameter updates.',`class Circle:
    def __init__(self, radius): self.radius = radius
    @property
    def diameter(self): return 2 * self.radius
c = Circle(3)
print(c.diameter)
c.radius = 5
print(c.diameter)`,'6\n10',['Why compute area instead of storing it separately?','It stays consistent with the current dimensions.','A computed property avoids two copies of the same fact.','Properties encrypt values.','Properties run only once.']);
unit(1,'2. Setters: validate every assignment','Use one validation path for construction and later changes.','@name.setter; backing attribute; read-only property','A setter handles obj.name = value. Use a different backing field such as _score: assigning self.score inside its own setter would call the setter again forever. Route __init__ through the property so initial values are checked too.',`class Student:
    def __init__(self, score): self.score = score
    @property
    def score(self): return self._score
    @score.setter
    def score(self, value):
        if type(value) is not int:
            raise TypeError("integer score required")
        if not 0 <= value <= 100:
            raise ValueError("score must be 0..100")
        self._score = value
s = Student(80)
s.score = 95
try: s.score = 101
except ValueError as error: print(error)
print(s.score)`,'score must be 0..100\n95','Type checking occurs before range checking; bool is excluded intentionally because it is an int subclass. A failed update does not alter _score. A getter without a setter rejects assignment with AttributeError.',['self.score = value  # inside the score setter','self._score = value','Writing the public property from its setter causes recursion.'],'Make Temperature with a Celsius property rejecting values below -273.15. Add a read-only Fahrenheit property. Test a rejected update.',`class Temperature:
    def __init__(self, celsius): self.celsius = celsius
    @property
    def celsius(self): return self._celsius
    @celsius.setter
    def celsius(self, value):
        if value < -273.15: raise ValueError("below absolute zero")
        self._celsius = value
    @property
    def fahrenheit(self): return self.celsius * 9 / 5 + 32
t = Temperature(0)
print(t.fahrenheit)
try: t.celsius = -300
except ValueError as error: print(error)
print(t.celsius)`,'32.0\nbelow absolute zero\n0',['Where should the setter store a valid score?','self._score','The backing name must differ from the property name.','self.score inside the setter','Only in a local variable']);
unit(2,'1. Friendly strings and diagnostic representations','Choose what a user and a developer need to see.','__str__; __repr__; !r conversion','print(obj) and str(obj) use __str__ for a friendly description. repr(obj), containers, and f-string !r use __repr__ for diagnostic detail. Both methods must return str. !r in an f-string applies repr, so string quotes and escapes remain visible.',`class Book:
    def __init__(self, title, pages):
        self.title, self.pages = title, pages
    def __str__(self): return f"{self.title} ({self.pages} pages)"
    def __repr__(self): return f"Book({self.title!r}, {self.pages!r})"
b = Book("Python", 120)
print(b)
print(repr(b))
print([b])`,'Python (120 pages)\nBook(\'Python\', 120)\n[Book(\'Python\', 120)]','The list uses repr of its elements. Constructor-like output is helpful but is not a guarantee that every repr can be evaluated. Never use eval on untrusted representation text.',['def __str__(self): print(self.title)','def __str__(self): return self.title','Printing returns None; the protocol requires a string result.'],'Give a Ticket a friendly destination and a diagnostic repr containing destination and price.',`class Ticket:
    def __init__(self, destination, price):
        self.destination, self.price = destination, price
    def __str__(self): return f"To {self.destination}: {self.price}"
    def __repr__(self): return f"Ticket({self.destination!r}, {self.price!r})"
t = Ticket("Tokyo", 500)
print(t)
print([t])`,'To Tokyo: 500\n[Ticket(\'Tokyo\', 500)]',['Which method is normally used for an object inside a list display?','__repr__','Containers show diagnostic representations of their elements.','__init__','Only __str__']);
unit(2,'2. Repr fallback and safe debugging','Make debugging useful without leaking sensitive fields.','representation fallback','If a class defines __repr__ but no __str__, the default __str__ uses __repr__. Include useful non-sensitive state. An account or token object should not print a secret just because it is being logged. A good repr is stable and concise.',`class Session:
    def __init__(self, user, token):
        self.user, self._token = user, token
    def __repr__(self): return f"Session(user={self.user!r}, token=<hidden>)"
s = Session("Sita", "demonstration-only")
print(s)
print(repr(s))`,'Session(user=\'Sita\', token=<hidden>)\nSession(user=\'Sita\', token=<hidden>)','Redaction reduces accidental logging disclosure; the field still exists and is not secured by an underscore. This is a fake token, not a credential.',['return f"Session(token={self._token})"','return f"Session(user={self.user!r}, token=<hidden>)"','Debug logs may be shared; avoid sensitive values in representations.'],'Write User(name, password) with a repr exposing only name. Show that print falls back to repr.',`class User:
    def __init__(self, name, password): self.name, self._password = name, password
    def __repr__(self): return f"User(name={self.name!r})"
u = User("Hari", "fake-value")
print(u)
print(repr(u))`,'User(name=\'Hari\')\nUser(name=\'Hari\')',['Must repr always be valid executable Python?','No; it should be informative and unambiguous.','A helpful diagnostic representation can use descriptive text.','Yes; always evaluate it.','It must return a dictionary.']);
unit(3,'1. Equality, ordering and NotImplemented','Compare values using meaningful state and cooperate with Python.','__eq__; __lt__; NotImplemented; __hash__','== calls equality methods; < calls ordering methods. Return NotImplemented when the other type is unsupported so Python can try the other operand. It is a singleton value, not an exception. is checks identity, not value. Defining equality without a compatible hash makes ordinary instances unhashable, which is appropriate for mutable value objects.',`class Score:
    def __init__(self, value): self.value = value
    def __eq__(self, other):
        if not isinstance(other, Score): return NotImplemented
        return self.value == other.value
    def __lt__(self, other):
        if not isinstance(other, Score): return NotImplemented
        return self.value < other.value
a, b = Score(80), Score(80)
print(a == b, a is b)
print([s.value for s in sorted([Score(90), Score(60), Score(80)])])
print(a == 80)`,'True False\n[60, 80, 90]\nFalse','sorted needs a consistent ordering. __lt__ does not automatically implement <= or > for every operand combination. Equality with an unsupported integer falls back to False here.',['return False  # every unsupported __lt__ operand','return NotImplemented','Returning False for an unsupported ordering hides a type mismatch.'],'Make Rank compare by number, sort three ranks, and show two distinct equal values.',`class Rank:
    def __init__(self, number): self.number = number
    def __eq__(self, other):
        if not isinstance(other, Rank): return NotImplemented
        return self.number == other.number
    def __lt__(self, other):
        if not isinstance(other, Rank): return NotImplemented
        return self.number < other.number
print(Rank(2) == Rank(2))
print([r.number for r in sorted([Rank(3), Rank(1), Rank(2)])])`,'True\n[1, 2, 3]',['What should an operator method return for an unsupported operand type?','NotImplemented','It allows Python to negotiate the operation or raise an appropriate TypeError.','raise NotImplemented','Always False']);
unit(3,'2. Arithmetic without surprising mutation','Add and subtract money only when currencies match.','__add__; __sub__; __radd__','a + b invokes operator methods such as __add__. Produce a new value rather than silently modifying a. __radd__ can support a reversed operand but should be added only if that operation makes sense. This example uses integer minor units, not binary floats, and refuses different currencies.',`class Money:
    def __init__(self, units, currency):
        self.units, self.currency = units, currency
    def __add__(self, other):
        if not isinstance(other, Money): return NotImplemented
        if self.currency != other.currency: raise ValueError("currency mismatch")
        return Money(self.units + other.units, self.currency)
    def __sub__(self, other):
        if not isinstance(other, Money): return NotImplemented
        if self.currency != other.currency: raise ValueError("currency mismatch")
        return Money(self.units - other.units, self.currency)
    def __repr__(self): return f"Money({self.units}, {self.currency!r})"
a, b = Money(100, "JPY"), Money(40, "JPY")
print(a + b)
print(a - b)
print(a)
try: print(a + Money(5, "USD"))
except ValueError as error: print(error)`,'Money(140, \'JPY\')\nMoney(60, \'JPY\')\nMoney(100, \'JPY\')\ncurrency mismatch','Currency mismatch is a valid Money operand with incompatible meaning, so it raises ValueError. A different type returns NotImplemented. This is a learning model, not a complete financial library.',['self.units += other.units; return self','return Money(self.units + other.units, self.currency)','Ordinary addition should not silently mutate either value.'],'Write Distance(metres) with __add__ returning a new Distance. Verify both inputs stay unchanged.',`class Distance:
    def __init__(self, metres): self.metres = metres
    def __add__(self, other):
        if not isinstance(other, Distance): return NotImplemented
        return Distance(self.metres + other.metres)
a, b = Distance(3), Distance(4)
c = a + b
print(c.metres, a.metres, b.metres)`,'7 3 4',['What should Money addition do with different currencies?','Reject the operation with a clear error.','A number alone cannot explain how currencies are converted.','Add the numbers and keep the first currency.','Change both accounts automatically.']);
unit(4,'1. Containers: len, indexing and membership','Let a Playlist participate in familiar collection operations.','__len__; __getitem__; __contains__; slicing','len(p) calls __len__, p[index] calls __getitem__, and item in p can call __contains__. Delegating to an internal list preserves ordinary negative indices, slices, and IndexError. Copy constructor input so callers do not accidentally share the same outer list.',`class Playlist:
    def __init__(self, songs): self._songs = list(songs)
    def __len__(self): return len(self._songs)
    def __getitem__(self, index): return self._songs[index]
    def __contains__(self, song): return song in self._songs
source = ["A", "B", "C"]
p = Playlist(source)
source.append("D")
print(len(p), p[0], p[-1])
print(p[1:])
print("B" in p, "D" in p)
try: print(p[9])
except IndexError: print("out of range")`,'3 A C\n[\'B\', \'C\']\nTrue False\nout of range','This design intentionally returns a list for a slice; document the choice. The outer copy is shallow, so mutable song objects would still be shared.',['def __getitem__(self, i): return None if i >= len(self._songs) else self._songs[i]','def __getitem__(self, i): return self._songs[i]','Returning None hides indexing errors and can break sequence iteration fallback.'],'Create Shelf with len, indexing, and membership delegated to its copied book list. Include a negative index and a slice.',`class Shelf:
    def __init__(self, books): self._books = list(books)
    def __len__(self): return len(self._books)
    def __getitem__(self, index): return self._books[index]
    def __contains__(self, book): return book in self._books
s = Shelf(["Python", "Japan", "Math"])
print(len(s), s[-1])
print(s[:2])
print("Japan" in s)`,'3 Math\n[\'Python\', \'Japan\']\nTrue',['What should an out-of-range integer index normally raise?','IndexError','Sequence users rely on this established protocol.','Return a made-up item.','Return zero silently.']);
unit(4,'2. Iterable versus iterator: independent passes','Create a fresh iterator for every traversal.','__iter__; iter(); next(); StopIteration','An iterable provides an iterator through iter(). An iterator remembers a position and next() advances it; exhaustion raises StopIteration. Returning iter(self._songs) creates a fresh list iterator each time. A collection should not normally be its own stateful iterator. Week 11 introduced generators; this implementation needs no new generator code.',`class Playlist:
    def __init__(self, songs): self._songs = list(songs)
    def __iter__(self): return iter(self._songs)
    def __len__(self): return len(self._songs)
p = Playlist(["A", "B"])
left, right = iter(p), iter(p)
print(next(left), next(left), next(right))
print(list(p))
print(list(p))
try: next(left)
except StopIteration: print("finished")
print(bool(Playlist([])))`,'A B A\n[\'A\', \'B\']\n[\'A\', \'B\']\nfinished\nFalse','The two iterators advance independently. list(p) requests another fresh iterator. Without __bool__, Python can use __len__: an empty collection is falsy. Do not mutate the collection during iteration unless a policy is explicitly documented.',['def __iter__(self): return self._songs','def __iter__(self): return iter(self._songs)','A list is iterable but is not itself an iterator; __iter__ must return an iterator.'],'Make Bag iterable and verify a nested loop produces all four pairs for two elements.',`class Bag:
    def __init__(self, items): self._items = list(items)
    def __iter__(self): return iter(self._items)
b = Bag([1, 2])
for x in b:
    for y in b:
        print(x, y)`,'1 1\n1 2\n2 1\n2 2',['Why return a new iterator on every __iter__ call?','Separate traversals need independent positions.','Nested loops and repeated traversals should not consume each other.','To erase the collection.','Because every iterator is permanent.']);
unit(5,'1. Instance, static and class methods','Choose self, no implicit argument, or cls deliberately.','@staticmethod; @classmethod; cls; alternative constructor','Instance methods receive self, the object. Static methods receive neither self nor cls: they group a related utility with a class. Class methods receive cls, the class actually used by the caller. cls(...) makes an alternative constructor preserve a subclass. A module function is often simpler than a static method when the utility is not class-specific.',`class Student:
    def __init__(self, name, age):
        if not self.valid_age(age): raise ValueError("invalid age")
        self.name, self.age = name, age
    @staticmethod
    def valid_age(age): return type(age) is int and 0 <= age <= 130
    @classmethod
    def from_string(cls, text):
        name, age = text.split(",")
        return cls(name.strip(), int(age.strip()))
class Graduate(Student): pass
s = Graduate.from_string("Sita, 24")
print(type(s).__name__, s.name, s.age)
print(Student.valid_age(-1))`,'Graduate Sita 24\nFalse','split and strip were taught with strings; int parses the text and may raise ValueError. A production parser must document its format and validate empty names and unexpected fields.',['return Student(name, age)  # inside from_string','return cls(name, age)','Hardcoding the base class loses the calling subclass.'],'Create Product.from_string for name:price and show a subclass is returned.',`class Product:
    def __init__(self, name, price): self.name, self.price = name, price
    @classmethod
    def from_string(cls, text):
        name, price = text.split(":")
        return cls(name.strip(), int(price))
class SpecialProduct(Product): pass
p = SpecialProduct.from_string("Book:300")
print(type(p).__name__, p.name, p.price)`,'SpecialProduct Book 300',['What does cls refer to in Graduate.from_string(...)?','Graduate','Classmethod binding passes the actual calling class.','Always Student','The current student instance']);
unit(5,'2. Week project: a Vector that feels natural','Combine properties, representations, operators, containers and construction.','protocol composition; Vector design contract','A two-dimensional vector can behave like a small sequence and a numeric value. Its addition and subtraction combine corresponding coordinates; lexicographic ordering compares x first, then y (not geometric length). This teaching version accepts integer coordinates only and is mutable/unhashable. Implement only operations whose meaning you can explain.',`class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y
    @property
    def x(self): return self._x
    @x.setter
    def x(self, value):
        if type(value) is not int: raise TypeError("integer coordinate required")
        self._x = value
    @property
    def y(self): return self._y
    @y.setter
    def y(self, value):
        if type(value) is not int: raise TypeError("integer coordinate required")
        self._y = value
    def __repr__(self): return f"Vector({self.x}, {self.y})"
    def __str__(self): return f"({self.x}, {self.y})"
    def __add__(self, other):
        if not isinstance(other, Vector): return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        if not isinstance(other, Vector): return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)
    def __eq__(self, other):
        if not isinstance(other, Vector): return NotImplemented
        return (self.x, self.y) == (other.x, other.y)
    def __lt__(self, other):
        if not isinstance(other, Vector): return NotImplemented
        return (self.x, self.y) < (other.x, other.y)
    def __len__(self): return 2
    def __getitem__(self, index): return (self.x, self.y)[index]
    def __iter__(self): return iter((self.x, self.y))
    def __contains__(self, value): return value in (self.x, self.y)
    @staticmethod
    def valid_coordinate(value): return type(value) is int
    @classmethod
    def from_string(cls, text):
        x, y = text.split(",")
        return cls(int(x), int(y))
a, b = Vector.from_string("3,4"), Vector(1,2)
print(a, repr(a))
print(a + b, a - b)
print(a == Vector(3,4), a is Vector(3,4))
print(len(a), a[-1], a[:], list(a), 4 in a)
print(sorted([a, b]))
try: a.x = "bad"
except TypeError as error: print(error)
print(a.x)`,'(3, 4) Vector(3, 4)\n(4, 6) (2, 2)\nTrue False\n2 4 (3, 4) [3, 4] True\n[Vector(1, 2), Vector(3, 4)]\ninteger coordinate required\n3','Read one method at a time and map it to caller syntax. Tuple comparison is lexicographic. bool(Vector(0,0)) is True because len is 2: a zero vector is not an empty collection. Arithmetic returns the base Vector intentionally; richer subclasses need an explicit compatible-result policy.',['Define dozens of dunders before deciding what operations mean.','Write the contract first, then implement and test each operation.','Predictable behaviour matters more than the number of methods.'],'Mini challenge: write Coordinate from memory with repr, equality, len, iteration and from_string. Then extend your Vector with a read-only magnitude_squared property and test (3,4) -> 25.',`class Coordinate:
    def __init__(self, x, y): self.x, self.y = x, y
    def __repr__(self): return f"Coordinate({self.x}, {self.y})"
    def __eq__(self, other):
        if not isinstance(other, Coordinate): return NotImplemented
        return (self.x, self.y) == (other.x, other.y)
    def __len__(self): return 2
    def __iter__(self): return iter((self.x, self.y))
    @classmethod
    def from_string(cls, text):
        x, y = text.split(",")
        return cls(int(x), int(y))
    @property
    def magnitude_squared(self): return self.x ** 2 + self.y ** 2
c = Coordinate.from_string("3,4")
print(repr(c), c == Coordinate(3,4))
print(len(c), list(c), c.magnitude_squared)`,'Coordinate(3, 4) True\n2 [3, 4] 25',['Why is bool(Vector(0,0)) True in this design?','Its sequence length is two.','Truth falls back to __len__ unless __bool__ defines another policy.','Its coordinates are positive.','All custom objects ignore length.']);
const days={};
for(let d=0;d<6;d++){
 const rows=units.filter(u=>u.day===d);
 rows.forEach((u,p)=>{let n=0;for(const s of u.sections)if(s.t==='ex')s.practiceId=`20.${d}.${p}.${n++}`;});
 days['20.'+d]={parts:rows.map(u=>({title:u.title,sections:u.sections}))};
 const final=days['20.'+d].parts.at(-1).sections;
 final.push(S('ex',`Retrieval practice: without notes, explain both parts of Day ${d+1}, rewrite the examples, change one input, and predict its output. Identify one invalid input and prove the object remains valid.`,{practiceId:`20.${d}.retrieval`}),S('sol',undefined,{code:'# Use the complete standalone solutions above as a reference after your own attempt.',why:'Compare reasoning and behaviour, not only spelling. Repeat the part if you cannot explain the validation or protocol.'}));
 final.push(S('tip','Study at your own pace. Use the existing Previous/Next part and completion controls; finish every part before moving on.'));
}
days['20.5'].parts.push({title:'3. Full-week review and transfer challenges',sections:[S('h','Week 20 review: explain, build, and test'),S('p','Retrieve before rereading: 1. What is an invariant? 2. Why is _balance not security? 3. What does name mangling solve? 4. Why must a setter use a backing field? 5. When does repr run? 6. Why return NotImplemented? 7. Why is equality different from identity? 8. Why does each loop need a fresh iterator? 9. When is cls better than a hardcoded constructor? 10. Why does a zero vector still have length two?'),S('ex','Transfer project: build a ReadingList with validated title, safe repr, copied internal books, len/indexing/iteration/membership, and a from_string constructor. Reject an empty title; test two independent iterators, negative indexing, slicing and an out-of-range index.',{practiceId:'20.5.transfer'}),S('sol',undefined,{code:`class ReadingList:
    def __init__(self, title, books):
        self.title = title
        self._books = list(books)
    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        if not isinstance(value, str): raise TypeError("text required")
        if not value.strip(): raise ValueError("empty title")
        self._title = value.strip()
    def __repr__(self): return f"ReadingList({self.title!r}, {self._books!r})"
    def __len__(self): return len(self._books)
    def __getitem__(self, index): return self._books[index]
    def __iter__(self): return iter(self._books)
    def __contains__(self, book): return book in self._books
    @classmethod
    def from_string(cls, text):
        title, books = text.split(":", 1)
        return cls(title, [b.strip() for b in books.split(",") if b.strip()])
r = ReadingList.from_string("Study:Python,Japan")
print(repr(r))
print(len(r), r[-1], r[:1], "Japan" in r)
a, b = iter(r), iter(r)
print(next(a), next(a), next(b))
try: r.title = " "
except ValueError as error: print(error)
print(r.title)
try: r[8]
except IndexError: print("out of range")`,out:"ReadingList('Study', ['Python', 'Japan'])\n2 Japan ['Python'] True\nPython Japan Python\nempty title\nStudy\nout of range",why:'The parser is deliberately a simple comma-separated format, not CSV with quoted commas. Constructor and assignment share validation; independent list iterators preserve traversal.'}),S('key','Day 7 is review/rest: revisit your Week 20 questions, rebuild Vector without a template, and explain the decisions. Week 21 introduces dataclasses and type hints; they are not required for this week.'),S('p','Reference (optional internet): Python official Classes tutorial, Built-in Functions (property, staticmethod, classmethod), and Data Model special methods. All teaching and exercises above work offline. https://docs.python.org/3/tutorial/classes.html · https://docs.python.org/3/library/functions.html · https://docs.python.org/3/reference/datamodel.html')]});
let html=fs.readFileSync(target,'utf8').replace(/\r\n/g,'\n');
const marker='\n};\n\nconst REST_DAY';
const start=html.indexOf('const DAY_TEACH = {'),end=html.indexOf(marker,start);
if(start<0||end<0)throw Error('Teaching boundaries missing');
const old=Function('return ('+html.slice(start+'const DAY_TEACH = '.length,end+2)+')')();
if(Object.keys(days).some(k=>old[k]))throw Error('Week 20 already exists: refuse overwrite');
const addition=Object.entries(days).map(([k,v])=>JSON.stringify(k)+': '+JSON.stringify(v,null,2)+',').join('\n');
html=html.slice(0,end).replace(/\s*$/, '').replace(/,?$/, ',')+'\n'+addition+html.slice(end);
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
fs.writeFileSync(target+'.tmp',html,'utf8');fs.renameSync(target+'.tmp',target);
console.log('Added Week 20: 6 days, 13 parts, 19 practice prompts, 12 retrieval quizzes; old teaching retained.');
