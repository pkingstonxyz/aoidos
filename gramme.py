"""
The gramme module (γραμμή which can mean line in ancient greek) is a linear logic "solver" Note, I call it a solver in quotes because it doesn't allow for backwards inferencing, only a forward search

It defines a Fact which has:
    a name (must be a unique string)
    a FactType 
        Linear: base (MUST be consumed for search to terminate)
        Affine: @ (can be consumed)
        Persistent: ! (Arbitrarily many copies)
    If it's an Implication -o it has a left and right side of type  set(Facts)
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

# TODO: Change these to some "session" class' static var
STEP_MAX = 50
ATTEMPTS_MAX = 1000
def solve(attempts, requests, solutions, narrative, context, goal):
    ##MOST BASIC
    if attempts >= ATTEMPTS_MAX:
        return solutions, attempts
    if len(solutions) >= requests:
        return solutions, attempts

    ## "BASE CASE" if every fact in the goal is in the context, 
    # and we have consumed all the linear facts, we can add it to solutions
    goal_reached = True
    for fact in goal:
        if fact not in context.facts:
            goal_reached = False
    if goal_reached and context.consumed_all_linearities():
        solutions.add(narrative)
        attempts += 1

    ## BASE CASE: In too deep! We've done too many steps
    if len(narrative) >= STEP_MAX:
        print(narrative)
        return None

    ## Now for each available implication we try it out
    for implication in context.available_implications():
        if context.can_apply_implication(implication):
            solutions, attempts = solve(attempts, requests, solutions, narrative.with_step(implication), context.given_implication(implication), goal)

    return solutions, attempts

def check_exists_already(dictionary, key, linenum):
    # If this resource has already been found
    exists_already = dictionary.get(key, 0)
    if exists_already > 0:
        raise Exception(f"Resource {key} on line {linenum} has a name collision on line {exists_already}")

def check_should_exist(dictionary, key, linenum):
    # If this resource has already been found
    exists_already = dictionary.get(key, 0)
    if exists_already > 0:
        return
    raise Exception(f"Resource {key} on line {linenum} has not been previously declared")

def add_typed_fact(environment, fact, outset):
    #Determine the fact type
    facttype = FactType.LINE
    if fact[0] == "@":
        facttype = FactType.AFFI
        fact = fact[1:]
    if fact[0] == "!":
        facttype = FactType.PERS
        fact = fact[1:]
    envget = environment.get(fact, None)
    # If it's an implication
    if isinstance(envget, Fact):
        # Construct the fact with the correct facttype
        fact = Fact(fact, facttype, envget.left, envget.right)
        # And add it to the outset
        outset.add(fact)
    # Or if it's a set
    elif isinstance(envget, set):
        for fact in envget:
            outset.add(fact)
    # Or if it's just a plain fact
    else:
        fact = Fact(fact, facttype)
        outset.add(fact)

def parse_file(filename):
    lines = []
    resources = {}
    environment = {}
    with open(filename, "r") as file:
        inbrackets = False
        linenum = 0
        for line in file:
            linenum += 1
            #If the line is blank, do nothing
            if line[0] == "\n":
                continue
            #If the line begins with a comment do nothing
            if line[0] == "%":
                continue
            #Ignore "" and "*"
            ignorable = {"", "*"}
            tokens = [token for token in line.strip().split(" ") if token not in ignorable]

            # If there's only one token on the line
            if len(tokens) == 1:
                rname = tokens[0]
                check_exists_already(resources, Fact(rname), linenum)
                resources[Fact(rname)] = linenum
                continue

            #If it's an implication
            if '-o' in tokens:
                rname = tokens[0]
                check_exists_already(resources, Fact(rname), linenum)
                equalsind = tokens.index('=')
                if equalsind == -1:
                    raise Exception(f"No equals sign on implication on line {linenum}")
                lolliind = tokens.index('-o')
                leftside = tokens[equalsind+1 : lolliind]
                rightside = tokens[lolliind+1 :]
                leftset = set()
                rightset = set()
                for itm in leftside:
                    check_should_exist(resources, Fact(itm), linenum)
                    add_typed_fact(environment, itm, leftset)
                for itm in rightside:
                    if itm[0] == "@" or itm[0] == "!":
                        check_should_exist(resources, Fact(itm[1:]), linenum)
                    else:
                        check_should_exist(resources, Fact(itm), linenum)
                    add_typed_fact(environment, itm, rightset)
                resources[Fact(rname)] = linenum
                environment[rname] = Fact.limply(rname, leftset, rightset)
                continue
            #If it's a simple assignment
            if tokens[1] == "=":
                rname = tokens[0]
                check_exists_already(resources, Fact(rname), linenum)
                equalsind = tokens.index('=')
                if equalsind == -1:
                    raise Exception(f"No equals sign on implication on line {linenum}")
                assignset = set()
                for itm in tokens[equalsind+1:]:
                    add_typed_fact(environment, itm, assignset)
                resources[Fact(rname)] = linenum
                environment[rname] = assignset
                continue
            #If it hasn't been successfully parsed, 
            # it's a bad line
            raise Exception(f"Error parsing line {linenum}")
## Tests go here
if __name__ == "__main__":
    parse_file("story.gram")
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
