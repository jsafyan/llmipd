import marimo

__generated_with = "0.9.17"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import scipy

    return mo, np, pd, plt, scipy


@app.cell
def __(pd):
    url = "https://raw.githubusercontent.com/Axelrod-Python/tournament/gh-pages/assets/strategies_std_payoff_matrix.csv"
    df = pd.read_csv(url, header=None)

    df.head()
    return df, url


@app.cell
def __():
    from scipy.linalg import interpolative as sli

    return (sli,)


@app.cell
def __(df, sli):
    mat = df.values
    k, idx, proj = sli.interp_decomp(mat, 0.15)
    return idx, k, mat, proj


@app.cell
def __(k):
    print(k)
    return


@app.cell
def __(idx, k, mat, proj, sli):
    B = sli.reconstruct_skel_matrix(mat, k, idx)
    recon = sli.reconstruct_matrix_from_id(B, idx, proj)
    return B, recon


@app.cell
def __(recon):
    return recon


@app.cell
def __(mat):
    return mat


@app.cell
def __(mat, np, recon):
    np.linalg.norm(mat - recon)
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
