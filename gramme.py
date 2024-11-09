"""
The gramme module (γραμμή which can mean line in ancient greek) is a linear logic "solver" Note, I call it a solver in quotes because it doesn't allow for backwards inferencing, only a forward search

It defines a Fact which has:
    a name (must be a unique string)
    a FactType 
        Linear: base (MUST be consumed for search to terminate)
        Affine: @ (can be consumed)
        Persistent: ! (Arbitrarily many copies)
    If it's an Implication -o it has a left and right side of type  set(Facts)
Note to self: Implication probably should've been a subclass of Fact, but ngl I couldn't be bothered to refactor this
"""
from enum import Enum

class FactType(Enum):
    LINE = 1
    AFFI = 2
    PERS = 3

class Fact:
    def __init__(self, name: str, ftype: FactType | None = FactType.LINE, left: set | None = None, right: set | None = None):
        #Throw errors
        if " " in name:
            raise Exception(f"'{name}' cannot include spaces!")
        # I don't think this necessarily has to be true
        #if (left and not right) or (right and not left):
        #    raise Exception(f"'{name}' must have both a left and right side")
        self.name = name
        self.ftype = ftype
        self.left = left
        self.right = right

    #Some helper methods that will make the code look cleaner
    def linear(name):
        """A fast constructor for a linear fact"""
        return Fact(name, FactType.LINE)
    def affine(name):
        """A fast constructor for an affine fact"""
        return Fact(name, FactType.AFFI)
    def persist(name):
        """A fast constructor for a persistent fact"""
        return Fact(name, FactType.PERS)
    #These next three could be handled by the above and some
    #use of the *args and whatever, but I'm choosing this way
    #so that it's more readable in the code
    def limply(name, left, right):
        """A fast constructor for a linear implication"""
        return Fact(name, FactType.LINE, left, right)
    def aimply(name, left, right):
        """A fast constructor for an affine implication"""
        return Fact(name, FactType.AFFI, left, right)
    def pimply(name, left, right):
        """A fast constructor for a persistent implication"""
        return Fact(name, FactType.PERS, left, right)

    #I'm only requiring name equality because of how I want
    #to be able to use the `in` keyword. i.e. I want to be
    #able to check if linear("hello") in {"hello", "goodbye"}
    #because the left side of an implication consists of 
    #names of facts, not facts themselves
    def __eq__(self, other):
        return self.name == other.name
    def __hash__(self):
        return hash(self.name)

    #So I can print
    def __repr__(self):
        if self.left or self.right:
            nameprefix = ""
            if self.ftype == FactType.AFFI:
                nameprefix = "@"
            if self.ftype == FactType.PERS:
                nameprefix = "!"
            return f"{nameprefix}{self.name} : {{{self.left} -o {self.right}}}"
        match self.ftype:
            case FactType.LINE:
                return f"{self.name}"
            case FactType.AFFI:
                return f"@{self.name}"
            case FactType.PERS:
                return f"!{self.name}"
            case _:
                raise Exception(f"Fact {self.name} without a type exists!")

class Context:
    def __init__(self, *args: Fact):
        self.facts = set(args)

    def consumed_all_linearities(self):
        """Checks if all linearities in the context have been consumed"""
        for fact in self.facts:
            if fact.ftype == FactType.LINE:
                return False
        return True

    def available_implications(self):
        """Returns a list of the available implications in the system"""
        return [fact for fact in self.facts if fact.left and fact.right]

    def can_apply_implication(self, implication):
        """Check if a given implication can be applied in the current context"""
        #i.e. check if self.facts is a superset of the 
        # implication's left side and if the implication
        # is in the context
        return self.facts >= implication.left and implication in self.facts

    def given_implication(self, implication):
        """Returns a new context with the implication applied"""
        if not self.can_apply_implication(implication):
            raise Exception(f"Tried to apply implication {implication} in context {self}")
        output_context = self.copy()
        #Remove all of the facts from the output_context i.e.
        # Just remove all the non-persistent ones
        for impl_fact in implication.left:
            fact = output_context[impl_fact]
            if fact.ftype is not FactType.PERS:
                output_context.facts.remove(fact)
        #Add in all the new facts
        for impl_fact in implication.right:
            output_context.facts.add(impl_fact)
        #Remove the implication if it's not persistent
        if implication.ftype is not FactType.PERS:
            output_context.facts.remove(implication)

        #Return the new context
        return output_context

    def context_with_fact(self, fact):
        """Return a new context with the new fact"""
        output_context = self.copy()
        output_context.facts.add(fact)
        return output_context

    def copy(self):
        """Returns a shallow copy of the current context"""
        next_facts = self.facts.copy()
        return Context(*next_facts)

    #I want it to be subscriptable and return the version 
    # of the fact in the context. Remember how Fact's __eq__
    # was implemented! We must interact with the resource's
    # ftype to apply the rules properly
    def __getitem__(self, otherfact):
        for fact in self.facts:
            if fact == otherfact:
                return fact
    def __repr__(self):
        return f"{self.facts}"

class Narrative():
    def __init__(self, *args):
        self.steps = list(args)

    def with_step(self, step):
        """Returns a (shallow) copy of the narrative with the next step"""
        next_narrative = self.copy()
        next_narrative.steps.append(step)
        return next_narrative

    def copy(self):
        """Returns a shallow copy of the current context"""
        next_steps = self.steps.copy()
        return Narrative(*next_steps)

    def __len__(self):
        return len(self.steps)

    def __eq__(self, other):
        if not isinstance(other, Narrative):
            return False
        if len(self) != len(other):
            return False
        for selfitm, otheritm in zip(self.steps, other.steps):
            if selfitm != otheritm:
                return False
        return True
    def __hash__(self):
        outstr = ""
        for step in self.steps:
            outstr += step.name
        return hash(outstr)

    def __repr__(self):
        out = ""
        for idx, itm in enumerate(self.steps):
            out += f"{idx}. {itm.name}\n"
        return out
        #return f"{self.steps}"
        #return f"{[impl.name for impl in self.steps]}"

class Query:
    """A Query"""
    def __init__(self, name: str, amount: int, implication: Fact):
        self.name = name
        self.amount = amount
        self.implication = implication

    def __eq__(self, other):
        if not isinstance(other, Query):
            return False
        return self.amount == other.amount and self.implication == other.implication

    def __hash__(self):
        return hash(f"{self.amount},{self.implication}")
    def __repr__(self):
        return f"Query {self.amount} times for {self.implication}"

class Environment:
    """An environment used for parsing files and solving 
    implications based on the environment its in"""
    def __init__(self, STEP_MAX = 50, ATTEMPTS_MAX = 1000):
        self.resources = {}
        self.env = {}
        self.queries = set()
        self.STEP_MAX = STEP_MAX
        self.ATTEMPTS_MAX = ATTEMPTS_MAX
    
    def from_file(filename):
        env = Environment()
        with open(filename, "r") as file:
            linenum = 0
            for line in file:
                linenum += 1
                if len(line) <= 0: continue # empty
                if line[0] == "\n": continue #empty
                if line[0] == "%": continue #comment
                #Ignore "" and "*" while tokenizing
                ignorable = {"", "*"}
                tokens = [token for token in line.strip().split(" ") if token not in ignorable]

                if len(tokens) == 1:
                    env.add_resource(Fact(tokens[0]), linenum)
                    continue
                #implication
                if '-o' in tokens and '=' in tokens:
                    env.parse_implication(tokens, linenum)
                    continue
                #assignment
                if tokens[1] == "=":
                    env.parse_assignment(tokens, linenum)
                    continue
                if tokens[0][0] == "#":
                    env.parse_query(tokens, linenum)
                    continue
                raise Exception(f"Error parsing line {linenum}")
        return env

    def parse_implication(self, tokens, linenum):
        """Parse and add implication to environment"""
        fact = Fact(tokens[0])
        self.check_exists_already(fact, linenum)
        equalsind = tokens.index('=')
        if equalsind == -1:
            raise Exception(f"No equals sign on implication on line {linenum}")
        lolliind = tokens.index('-o')
        leftside = tokens[equalsind+1 : lolliind]
        rightside = tokens[lolliind+1 :]
        leftset, rightset = set(), set()
        for itm in leftside:
            exists = self.check_should_exist(Fact(itm))
            if not exists:
                raise Exception(f"Resource {key} on line {linenum} has not been previously declared")
            self.add_namespaced_fact_to(itm, leftset)
        for itm in rightside:
            itmname = itm
            if itm[0] == "@" or itm[0] == "!":
                itmname = itmname[1:]
            exists = self.check_should_exist(Fact(itmname))
            if not exists:
                raise Exception(f"Resource {key} on line {linenum} has not been previously declared")
            self.add_namespaced_fact_to(itm, rightset)
        self.add_resource(fact, linenum)
        self.add_to_environment(tokens[0], Fact.limply(tokens[0], leftset, rightset))

    def parse_assignment(self, tokens, linenum):
        """Parse and add assignment to environment"""
        self.check_exists_already(Fact(tokens[0]), linenum)
        equalsind = tokens.index('=')
        if equalsind == -1:
            raise Exception(f"No equals sign on implication on line {linenum}")
        assignset = set()
        for itmname in tokens[equalsind+1:]:
            self.add_namespaced_fact_to(itmname, assignset)
        self.add_resource(Fact(tokens[0]), linenum)
        self.add_to_environment(tokens[0], assignset)

    def parse_query(self, tokens, linenum):
        """Parse and add query to the environment"""
        queryname = tokens[0][1:]
        amount = tokens[1]
        if not amount.isnumeric():
            raise Exception(f"Query on line {linenum} has no requested amounts")
        amount = int(amount)

        lolliind = tokens.index('-o')
        if lolliind == -1:
            raise Exception(f"Query on line {linenum} has no implication")
        context, goal = set(), set()
        leftside = tokens[2:lolliind]
        rightside = tokens[lolliind+1:]
        if len(leftside) == 0:
            raise Exception(f"Query on line {linenum} has no context")
        if len(rightside) == 0:
            raise Exception(f"Query on line {linenum} has no goal")
        for itmname in leftside:
            self.add_namespaced_fact_to(itmname, context)
        for itmname in rightside:
            self.add_namespaced_fact_to(itmname, goal)
        self.add_query(queryname, amount, context, goal)

    def check_exists_already(self, fact: Fact, linenum = -1):
        """If we're in a file, we want it to raise an 
        error on collision. it should do nothing
        if the fact is added programmatically"""
        exists_already = self.resources.get(fact, 0)
        if linenum > 0:
            # If resource has already been found, error
            if exists_already != 0:
                raise Exception(f"Resource {key} on line {linenum} has not been previously declared")
            return exists_already > 0
        # If we're not in a file, we want the boolean
        else:
            return exists_already != 0

    def check_should_exist(self, fact: Fact):
        """Checks if a resource has already been declared"""
        exists_already = self.resources.get(fact, 0)
        #If it's anything but a 0, it exists
        return exists_already != 0

    def add_resource(self, fact: Fact, linenum = -1):
        """Adds fact as a resource to our list of available
        resources"""
        exists = self.check_exists_already(fact, linenum)
        if not exists:
            self.resources[fact] = linenum

    def add_namespaced_fact_to(self, factname, outset):
        """Adds facts to the outset by grabbing the
        fact that factname refers to from the envronment"""
        facttype = FactType.LINE
        if factname[0] == "@":
            facttype = FactType.AFFI
            factname = factname[1:]
        if factname[0] == "!":
            facttype = FactType.PERS
            factname = factname[1:]
        envget = self.env.get(factname, None)
        # If it's a set of facts it means the "factname"
        # Is a reference to a set of facts
        if isinstance(envget, set):
            for fact in envget:
                # Add each of the facts, also namespace aware
                # This flattens the sets

                # If it's a fact we need to preserve the type
                setfactname = fact
                if isinstance(fact, Fact):
                    if fact.ftype == FactType.AFFI:
                        setfactname = "@" + fact.name
                    elif fact.ftype == FactType.PERS:
                        setfactname = "!" + fact.name
                    else:
                        setfactname = fact.name
                self.add_namespaced_fact_to(setfactname, outset)
        # If it's an implication
        elif isinstance(envget, Fact):
            outset.add(Fact(factname, facttype, envget.left, envget.right))
        # If it's just a plain fact
        else:
            outset.add(Fact(factname, facttype))

    def add_to_environment(self, name, fact_or_set):
        """Adds a name to the namespace of facts"""
        self.env[name] = fact_or_set

    def add_query(self, queryname, amount, context, goal):
        """Adds a query to the system"""
        implication = Fact.limply(queryname, context, goal)
        query = Query(queryname, amount, implication)

        self.queries.add(query)

    def answer_query(self, query: Query, requests: int = None):
        requested_stories = query.amount
        if requests:
            requested_stories = requests
        context = Context(*query.implication.left)
        goal = query.implication.right
        return self._solve(0, requested_stories, set(), Narrative(), context, goal)

    def _solve(self, attempts, requests, narratives, narrative, context, goal):
        if attempts >= self.ATTEMPTS_MAX:
            return narratives, attempts
        if len(narratives) >= requests:
            return narratives, attempts
        #if every fact is in the goal and each linearity
        #has been consumed, we can add it
        goal_reached = True
        for fact in goal:
            if fact not in context.facts:
                goal_reached = False
                break
        if goal_reached and context.consumed_all_linearities():
            narratives.add(narrative)
            attempts += 1

        #Done too many steps, in too deep!
        if len(narrative) >= self.STEP_MAX:
            return None

        #Try each implicaiton and recur
        for implication in context.available_implications():
            if context.can_apply_implication(implication):
                narratives, attempts = self._solve(attempts, requests, narratives, narrative.with_step(implication), context.given_implication(implication), goal)

        return narratives, attempts

    def __repr__(self):
        return f"RES: {self.resources}\nENV: {self.env}\nQRS: {self.queries}"

## Tests go here
if __name__ == "__main__":
    env = Environment.from_file("./test_stories/mini_madame_bovary.gram")
    print(env)
    query = env.queries.pop()
    print(query)
    solutions, attempts = env.answer_query(query)
    print(solutions)
    print(attempts)
    """
    print("==========")
    print("A little testing data")
    print("==========")
    a = Fact.linear("hello")
    print(f"Linear fact: {a}")
    b = Fact.affine("goodbye")
    print(f"Affine fact: {b}")
    c = Fact.persist("DogsAreCool")
    print(f"Persistent fact: {c}")
    line_imply = Fact.limply("greetingExchange", {a}, {b})
    print(f"Linear Implication: {line_imply}")
    affi_imply = Fact.aimply("greetingExchange", {a}, {b})
    print(f"Affine Implication: {affi_imply}")
    pers_imply = Fact.pimply("greetingExchange", {a}, {b})
    print(f"Persistent Implication: {pers_imply}")

    c_same = Fact.persist("DogsAreCool")
    print(f"Equality check: {c} == {c_same} ? {c == c_same}")
    c_aff  = Fact.affine("DogsAreCool")
    print(f"Equality check: {c} == {c_aff} ? {c == c_aff}")

    context = Context(a, b, c, line_imply, affi_imply)
    print(f"Context: {context}")
    print(f"Size check (shouldn't add two of the same implication) {len(context.facts) == 4}")
    print(f"Equivalent fact is in context check: {pers_imply in context.facts}")

    implication_free_context = Context(a, b, c)
    print(f"implication_free_context's implications: {implication_free_context.available_implications()}")
    print(f"context's available implications: {context.available_implications()}")

    d = Fact.affine("FourthFact")
    necessary_implication = Fact.limply("unneeded_implication", {a, b, d}, {c})
    print(f"Context {context} should NOT be able to do implication {necessary_implication} -> {context.can_apply_implication(necessary_implication)}")
    print(f"But should be able to apply implication {affi_imply} -> {context.can_apply_implication(affi_imply)}")

    print(f"Context: {context}")
    applied_context = context.given_implication(line_imply)
    print(f"Context with implication {line_imply} applied newline: \n{applied_context}")
    persistent_fact = Fact.pimply("SayDogsAreCool", {c}, {a, b})
    persistent_context = context.context_with_fact(persistent_fact)
    pers_applied_context = persistent_context.given_implication(persistent_fact)
    print(f"PersContext: {persistent_context}")
    print(f"PersContext with implication {persistent_fact} newline: \n {pers_applied_context}")
    # A test taken from page 5 of https://www.cs.cmu.edu/~cmartens/lpnmr13.pdf
    print("==========")
    print("Emma and charles test")
    print("==========")
    initial_environment = \
    Context(Fact.affine("emma"), Fact.linear("convent"), \
            Fact.persist("novel"), Fact.affine("charles"), \
            Fact.affine("ball"), \
    Fact.aimply("emmaSpendsYearsInConvent", {Fact("emma"), Fact("convent")}, \
                {Fact.affine("emma"), Fact.persist("grace"), \
                 Fact.persist("education")}), \
    Fact.limply("emmaReadsNovel", {Fact("emma"), Fact("novel")}, \
                {Fact.affine("emma"), Fact.affine("escapism")}), \
    Fact.aimply("emmaGoesToBall", {Fact("emma"), Fact("novel")}, \
                {Fact.affine("emma"), Fact.affine("escapism")}),
    Fact.aimply("emmaMarries", {Fact("emma"), Fact("escapism"), \
                                Fact("charles"), Fact("grace")}, \
                {Fact.affine("emma"), Fact.affine("charles"), \
                 Fact.affine("emmaCharlesMarried")}))
    print(initial_environment)
    solution = solve(0, 1000, set(), Narrative(), initial_environment, {Fact("emmaCharlesMarried")})
    print(solution)
"""
