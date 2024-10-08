import numpy as np
import math

class Lognormal:
    """
    Encapsulates a lognormal distirbution
    """
    def __init__(self, mean, stdev, random_seed=42):
        """
        Params:
        -------
        mean = mean of the lognormal distribution
        stdev = standard dev of the lognormal distribution
        """
        self.rand = np.random.default_rng(seed=random_seed)
        mu, sigma = self.normal_moments_from_lognormal(mean, stdev**2)
        self.mu = mu
        self.sigma = sigma
        
    def normal_moments_from_lognormal(self, m, v):
        '''
        Returns mu and sigma of normal distribution
        underlying a lognormal with mean m and variance v
        source: https://blogs.sas.com/content/iml/2014/06/04/simulate-lognormal
        -data-with-specified-mean-and-variance.html

        Params:
        -------
        m = mean of lognormal distribution
        v = variance of lognormal distribution
                
        Returns:
        -------
        (float, float)
        '''
        phi = math.sqrt(v + m**2)
        mu = math.log(m**2/phi)
        sigma = math.sqrt(math.log(phi**2/m**2))
        return mu, sigma
        
    def sample(self):
        """
        Sample from the normal distribution
        """
        return self.rand.lognormal(self.mu, self.sigma)
    
#NOT USED, FOR REFERENCE ONLY
class DiscreteNormal:
    """
    Encapsulates a normal distirbution with discrete values
    """
    def __init__(self, mu, sigma, discrete_lowest, discrete_highest, n_samples, random_seed=42) -> None:
        """
        Params:
        -------
        mu = mean of the normal distribution
        sigma = standard dev of the normal distribution
        discrete_lowest = lowest discrete number for the normal distribution
        discrete_highest = highest discrete number for the normal distribution
        n_samples = number of samples
        """
        self.mu = mu
        self.sigma = sigma
        self.discrete_lowest = discrete_lowest
        self.discrete_highest = discrete_highest
        self.n_samples = n_samples
        # self.seed = random_seed

    def sample(self):
        '''
        Returns a list of normally distributed discrete values within a range
                
        Returns:
        -------
        (list)
        '''
        # np.random.seed(self.seed)
        continuous_samples = np.random.normal(self.mu, self.sigma, self.n_samples)
        discrete_samples = np.clip(np.round(continuous_samples), self.discrete_lowest, self.discrete_highest).astype(int)
        return list(discrete_samples)

    def sample_count(self, discrete_samples):
        '''
        Returns a list of count of discrete distribution

        Params:
        -------
        discrete_samples = list of normally distributed discrete values within a range
                
        Returns:
        -------
        (list)
        '''
        value_counts = [np.sum(discrete_samples == x) for x in list(range(self.discrete_lowest, self.discrete_highest+1))]
        return value_counts