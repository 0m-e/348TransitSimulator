import pandas as pd
from scipy.stats import poisson, nbinom, geom

def get_error_prob(prop_file): #takes csv file of error code proportions,
    #returns as dict of actual probabilities of each error occuring

    df = pd.read_csv(prop_file)

    # Replace with actual column names if known
    error_dict = dict(zip(
        df["col"],
        df["Freq"] * 0.0174
    ))
    return error_dict

#takes a csv file of distribution type and parameter, returns a dictionary of
#error codes and their corresponding distributions
def get_distributions(fitted_file):

    df = pd.read_csv(fitted_file)

    # Dictionary to store PMFs
    pmf_dict = {}

    for _, row in df.iterrows():
        code = row["delay_code"]
        model = row["best_model"]

        if model == "pois":
            lam = row["lambda"]

            def pmf(k, lam=lam):
                return poisson.pmf(k, mu=lam)

        elif model == "nb":
            size = row["size"]   # corresponds to 'n'
            mu = row["mu"]

            # Convert (size, mu) → (n, p) for scipy
            p = size / (size + mu)

            def pmf(k, size=size, p=p):
                return nbinom.pmf(k, n=size, p=p)

        elif model == "geom":
            p = row["prob"]

            def pmf(k, p=p):
                return geom.pmf(k, p=p)

        else:
            continue

        pmf_dict[code] = pmf
    return pmf_dict
