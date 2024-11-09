# ἀοιδός

ἀοιδός - singer

Computational Geometry M7: Poetry generation

aoidos generates epic poetry

## Form

An epic poem is differentiated from normal poetry in (I made this up based on 
random readings and wikipedia):

 - Massive Length
 - Super human characters
 - Heroic feats/activities
 - Divine intervention in human affairs
 - Grand scale (many countries, the universe)
 - Narrative form
 - Metrical
 - Use of epithets

My epics will adhere to:

 - Heroic Characters
 - Heroic feats/activities
 - Narrative form
 - Metrical
 - Highly adjectival

The Iliad is in dactylic hexameter, a form not conducive to the english language.
Instead, I will be using iambic hexameter. I'll also relax the "iamb" requirement,
as it is too rigid for the English language. Instead, it's best to think of one
or more unstressed syllables followed by a single stressed syllable. I'll also
be rewarding assonance and alliteration in mine.

As for sentences, Greek epic poetry allows sentence breaks anywhere in the line,
but mine will enforce each line being one sentence, with grammatical correctness
being rewarded.

Instead of epithets, my generator will instead reward the use of adjectives in 
the generated poem. 

---
ἀοιδός 
---

## Basic process

1. Generate a list of narrative elements
1. Using my linear logic "solver", generate a narrative based on the generated elements.
2. Assign weight to each step of the narrative.
3. Create n lines of poetry according to how much weight each section was assigned.
4. Run genetic algorithm on each generated section.
5. Tadah you have a narrative poem.

---
ἀοιδός 
---

## How do we generate a list of narrative elements?

We start off with characters.

 - Molly
 - Patrick

Then we make some of them heroes.

 - Heroic - Patrick
 - Normal - Molly

Then we establish relationships between them

 - Patrick (sibling) Molly
 - Molly (sibling) Patrick

Then each character is assigned a feeling to each character

 - Patrick (hates) Molly
 - Molly (hates) Patrick

Then 

---
ἀοιδός 
---

## How does the solver work?

The solver is called gramme from γραμμή which can mean line in ancient Greek.
It is based on, to my best understanding of the subject, a restricted subset
of Linear Logic[^1]. It is based also on the description of the narrative generation
system presented in "Linear Logic Programming for Narrative Generation"[^2].

It offers the following functionality:

1. Parse a .gram file, a subset of the celf programming language using only
the features used in LLPfNG Figure 1[^2].
2. Solve queries based on environments ingressed from .gram files, or otherwise
generated.

Queries come in the form of:

`name, requested narratives, initial narrative resources, goal narrative resources` 

If possible, it will produce the number of narratives requested, but if it 
cannot satisfy the request, it will produce as many as it can.

---
ἀοιδός 
---

## How are weights assigned?

---
ἀοιδός 
---

[^1] Girard paper
[^2] Linear Logic Programming for Narrative Generation
