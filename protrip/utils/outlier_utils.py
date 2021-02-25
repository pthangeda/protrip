import math

def z_score_outliers(values, z_thresh=3.0):
    if len(values)<2:
        return []
    mean_val = sum(values)/len(values)
    var_val = sum((x-mean_val)**2 for x in values)/(len(values)-1) if len(values)>1 else 0
    stdv = math.sqrt(var_val)
    if stdv<1e-9:
        return []
    outliers = []
    for i,v in enumerate(values):
        z = abs((v-mean_val)/stdv)
        if z>z_thresh:
            outliers.append((i,v,z))
    return outliers

def iqr_outliers(values, factor=1.5):
    if not values:
        return []
    s = sorted(values)
    n = len(s)
    q1 = s[int(0.25*(n-1))]
    q3 = s[int(0.75*(n-1))]
    iqr = q3-q1
    l = q1 - factor*iqr
    h = q3 + factor*iqr
    out = []
    for i,v in enumerate(values):
        if v<l or v>h:
            out.append((i,v))
    return out

def remove_outliers(values, method='zscore', param=3.0):
    if method=='zscore':
        out = z_score_outliers(values, param)
        idx_out = set(x[0] for x in out)
        filtered = [v for i,v in enumerate(values) if i not in idx_out]
        return filtered
    elif method=='iqr':
        out = iqr_outliers(values, param)
        idx_out = set(x[0] for x in out)
        filtered = [v for i,v in enumerate(values) if i not in idx_out]
        return filtered
    else:
        return values
