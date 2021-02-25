import math
import numpy as np

def compute_mean(values):
    if not values: return None
    return sum(values)/len(values)

def compute_var(values):
    if len(values)<2: return 0
    m = compute_mean(values)
    return sum((x-m)**2 for x in values)/(len(values)-1)

def compute_std(values):
    return math.sqrt(compute_var(values))

def compute_median(values):
    if not values: return None
    s = sorted(values)
    mid = len(s)//2
    if len(s)%2==1:
        return s[mid]
    else:
        return 0.5*(s[mid-1]+s[mid])

def percentile(values, perc):
    if not values: return None
    s = sorted(values)
    idx = int(perc*(len(s)-1))
    return s[idx]

def compute_cov_matrix(dataset):
    if len(dataset)<2:
        return None
    arr = np.array(dataset)
    return np.cov(arr, rowvar=False)

def basic_stats_dict(values):
    if not values: return {}
    return {
        'count': len(values),
        'mean': compute_mean(values),
        'std': compute_std(values),
        'min': min(values),
        'max': max(values),
        'median': compute_median(values),
        'q25': percentile(values, 0.25),
        'q75': percentile(values, 0.75)
    }

def correlation_coefficient(xs, ys):
    if len(xs)!=len(ys) or len(xs)<2:
        return None
    mx = compute_mean(xs)
    my = compute_mean(ys)
    num=0
    denx=0
    deny=0
    for x,y in zip(xs, ys):
        dx = x-mx
        dy = y-my
        num += dx*dy
        denx += dx*dx
        deny += dy*dy
    if denx<1e-12 or deny<1e-12:
        return None
    return num/math.sqrt(denx*deny)
