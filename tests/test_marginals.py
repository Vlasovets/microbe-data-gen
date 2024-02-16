import unittest
import pandas as pd
import numpy as np
from source.models import fit_nb, fit_poisson
import statsmodels.api as sm
from scipy.stats import chi2, logistic, nbinom
from scipy.optimize import minimize


class TestMarginal(unittest.TestCase):
    def setUp(self):
        """
        Set up test data for the test case.

        This method generates a DataFrame with four columns: 'nb', 'poisson', 'zinb', and 'zip'. Each column contains
        100 random numbers generated from a different distribution: negative binomial, Poisson, zero-inflated negative
        binomial, and zero-inflated Poisson, respectively.

        The parameters for the distributions are as follows:
        - Negative binomial: number of successes = 10, probability of success = 0.5
        - Poisson: lambda = 5
        - Zero-inflated negative binomial: same as negative binomial, but with a 50% chance of being replaced with zero
        - Zero-inflated Poisson: same as Poisson, but with a 50% chance of being replaced with zero

        The generated DataFrame is stored in the instance variable `self.df` for use in the test methods.
        """
        size = 100  # size of the data
        n = 10  # number of successes for negative binomial
        p = 0.5  # probability of success for negative binomial and Poisson
        lambda_ = 5  # lambda parameter for Poisson
        zero_prob = 0.5  # probability of zero for zero-inflated distributions

        nb_data = np.random.negative_binomial(n, p, size=size)
        poisson_data = np.random.poisson(lambda_, size=size)
        zinb_data = nbinom.rvs(n, p, size=size)
        zinb_data[np.random.random(size) < zero_prob] = 0
        zip_data = np.random.poisson(lambda_, size=size)
        zip_data[np.random.random(size) < zero_prob] = 0

        self.df = pd.DataFrame({
            'nb': nb_data,
            'poisson': poisson_data,
            'zinb': zinb_data,
            'zip': zip_data
        })

    def test_nb(self):
        """
        Test the fit_nb function with negative binomial data.

        This test checks that the fit_nb function correctly estimates the parameters of a negative binomial distribution.
        The test generates a negative binomial model using the statsmodels library, then compares the parameters estimated
        by statsmodels with the parameters estimated by fit_nb.

        The parameters being tested are theta (1 / alpha) and mu (exp(const)).

        The test uses the assertAlmostEqual method to check that the estimated parameters are close to the true parameters,
        up to a certain number of decimal places.
        """
        x = self.df['nb']
        intercept = np.ones(len(x))

        mle_nb = sm.NegativeBinomial(x, exog=intercept).fit()

        theta_nb= 1 / mle_nb.params['alpha']
        mu = np.exp(mle_nb.params['const'])

        _, test_theta_nb, test_mu = fit_nb(x)

        self.assertAlmostEqual(test_theta_nb, theta_nb)
        self.assertAlmostEqual(test_mu, mu)

    def test_poisson(self):
        """
        Test the fit_poisson function with zero-inflated Poisson data.

        This test checks that the fit_poisson function correctly estimates the parameters of a zero-inflated Poisson distribution.
        The test generates a zero-inflated Poisson model using the statsmodels library, then compares the parameters estimated
        by statsmodels with the parameters estimated by fit_poisson.

        The parameters being tested are zero_prob (probability of observing zero counts) and mu (mean parameter for the Poisson model).

        The test uses the assertAlmostEqual method to check that the estimated parameters are close to the true parameters,
        up to a certain number of decimal places.

        The fit_poisson function is called with a p-value cutoff of 0.05, meaning that the zero-inflated model will be chosen
        if the p-value of the likelihood ratio test is less than 0.05.
        """
        x = self.df['zip']
        intercept = np.ones(len(x))

        mle_zip = sm.ZeroInflatedPoisson(x, intercept).fit()

        zero_prob = logistic.cdf(mle_zip.params['inflate_const'])
        mu = np.exp(mle_zip.params['const'])

        test_zero_prob, _, test_mu = fit_poisson(x, intercept=intercept, pval_cutoff=0.05)

        self.assertAlmostEqual(test_zero_prob, zero_prob)
        self.assertAlmostEqual(test_mu, mu)


if __name__ == '__main__':
    unittest.main()


# mle_poisson = sm.GLM(x, intercept, family=sm.families.Poisson()).fit()

# mle_zinb = sm.ZeroInflatedNegativeBinomialP(x, intercept).fit()
# theta_zinb = 1 / mle_zinb.params['alpha']
            
# [logistic.cdf(mle_zinb.params['inflate_const']), theta_zinb, np.exp(mle_zinb.params['const'])]
    


# def neg_llf(alpha):
#     try:
#         model = sm.GLM(x, intercept, family=sm.families.NegativeBinomial(alpha=alpha)).fit()
#         return -model.llf
#     except:
#         return np.inf

# # Initial guess for alpha
# alpha_init = 1.0

# # Find the optimal alpha
# result = minimize(neg_llf, alpha_init, bounds=[(0, 10)])

# # Get the optimal alpha and dispersion
# alpha_opt = result.x[0]
# dispersion = 1 / alpha_opt

# print("Naive Estimated alpha (dispersion parameter):", theta_nb)
# print("GLM Estimated alpha (dispersion parameter):", dispersion)