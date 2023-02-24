import numpy as np
from skinny_glm import SkinnyGLM
from families import GaussianFamily
from links import *
import statsmodels.api as sm
import pytest

TOL = 1e-4
SEED = 2023

LINKS = [
    (IdentityLink(), sm.genmod.families.links.identity())
]

@pytest.mark.parametrize("links", LINKS)
def test_gaussian(links):
    np.random.seed(SEED)
    skinny_link = links[0]
    sm_link = links[1]

    n = 1000
    p = 1
    sigma = 1

    X = np.hstack([np.ones((n, p)), np.random.normal(size=(n, p))])
    b = np.random.normal(size=(1, p+1))
    mu = skinny_link.inv_link(X @ b.T)
    y = mu + np.random.normal(scale=sigma, size=(n, 1))
    
    skinny_model = SkinnyGLM(family=GaussianFamily(skinny_link))
    skinny_model._irls(X, y)

    stats_model = sm.GLM(y, X, family=sm.families.Gaussian(sm_link))
    stats_model = stats_model.fit()

    print(f"true parameter estimates: {b.flatten()}")
    print(f"skinny parameter estimates: {skinny_model.b.flatten()}")
    print(f"statsmodels parameter estimates: {stats_model.params.flatten()}")
    assert ((skinny_model.b.flatten() - stats_model.params.flatten())**2).sum() < TOL