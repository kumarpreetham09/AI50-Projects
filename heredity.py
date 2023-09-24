import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    p = 1
    for person in people:
        if people[person]["father"] == None:

            # determine number of genes
            if person in two_genes:
                g = 2
            elif person in one_gene:
                g = 1
            else:
                g = 0

            # determine trait of person
            if person in have_trait:
                t = True
            else:
                t = False
            
            prob = PROBS["gene"][g]
            prob *= PROBS["trait"][g][t] 
            
            p *= prob

        else:
            mother = people[person]['mother']
            father = people[person]['father']


            mother_prob = calculate(mother,one_gene,two_genes)
            father_prob = calculate(father,one_gene,two_genes)
            v = 0

            # determine prob of person getting respective number of genes from parents
            if person in one_gene:
                prob_genes = (1-mother_prob) * father_prob + mother_prob * (1-father_prob)
                v = 1
            elif person in two_genes:
                prob_genes = mother_prob * father_prob
                v = 2
            
            else:
                prob_genes = (1-mother_prob) * (1-father_prob)
                v = 0
            

            if person not in have_trait:
                prob = prob_genes * PROBS["trait"][v][False]

            else:
                prob = prob_genes * PROBS["trait"][v][True]
            
            
            p *= prob     
                     
    return p
    


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        
    for person in probabilities:
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        
        gene_factor = 0
        trait_factor = 0
        for i in probabilities[person]["gene"].values():
            gene_factor += i

        for i in range(3):
            probabilities[person]["gene"][i] = probabilities[person]["gene"][i] * (1/gene_factor) 

        for j in probabilities[person]["trait"].values():
            trait_factor += j

        for j in range(2):
            probabilities[person]["trait"][j] = probabilities[person]["trait"][j] * (1/trait_factor)

def calculate(name, one_gene, two_genes):

    if name in one_gene:
        value = 0.5
    elif name in two_genes:
        value = (1-PROBS["mutation"])
    else:
        value = PROBS["mutation"]

    return value


if __name__ == "__main__":
    main()