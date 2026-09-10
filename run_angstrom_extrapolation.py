import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import scipy.io as sp
import sys
import srf_aod as srf
import rayleigh_scattering as rs
from datetime import datetime, timedelta

"""
Full pipeline for computing the Angstrom Exponent
from Langley fits. The Langley fits are output to 
.xlsx files by the I2R Matlab star processing code.
Currently, this method uses all Langley fits for 
each band, rather than using "common stars" (only 
stars that appear across all bands).

This method uses a linear least-squares fit approach
in log-log space, using either weighted or unweighted
aerosol optical depth measurements

Rayleigh and Ozone optical depths are convolved with
the star photometer's MidOpt filters to create
"effective" Rayleigh and Ozone ODs, which are 
subtracted from the total optical depths to 
yield the aerosol optical depths.

Created: Jackson Tobin 09/10/2026
"""



# Read the files:
fb450 = "/Users/jacksontobin/Local_Documents/NightTime_Research/ANGSTROM/Star_Photometry/Angstrom3_ColState/Angstrom_Overnight_2026_08_23_053000_063000/Band_450nm_BFS-PGE-16S7M_SN22245818/Langley_Plots/Band_450nm_BFS-PGE-16S7M_SN22245818_Langley_20260824_053009.xlsx"
fb470 = "/Users/jacksontobin/Local_Documents/NightTime_Research/ANGSTROM/Star_Photometry/Angstrom3_ColState/Angstrom_Overnight_2026_08_23_053000_063000/Band_470nm_BFS-PGE-16S7M_SN22245821/Langley_Plots/Band_470nm_BFS-PGE-16S7M_SN22245821_Langley_20260824_053009.xlsx"
fb490 = "/Users/jacksontobin/Local_Documents/NightTime_Research/ANGSTROM/Star_Photometry/Angstrom3_ColState/Angstrom_Overnight_2026_08_23_053000_063000/Band_490nm_BFS-PGE-16S7M_SN22010605/Langley_Plots/Band_490nm_BFS-PGE-16S7M_SN22010605_Langley_20260824_053009.xlsx"
fb520 = "/Users/jacksontobin/Local_Documents/NightTime_Research/ANGSTROM/Star_Photometry/Angstrom3_ColState/Angstrom_Overnight_2026_08_23_053000_063000/Band_520nm_BFS-PGE-16S7M_SN22011988/Langley_Plots/Band_520nm_BFS-PGE-16S7M_SN22011988_Langley_20260824_053010.xlsx"
b450 = pd.read_excel(fb450)
b470 = pd.read_excel(fb470)
b490 = pd.read_excel(fb490)
b520 = pd.read_excel(fb520)
print("Number of stars in each band:")
print(f'    450nm:   {len(b450)}')
print(f'    470nm:   {len(b470)}')
print(f'    490nm:   {len(b490)}')
print(f'    520nm:   {len(b520)}\n')

# Format the date-time string
_,_,datestr = fb450.partition('Angstrom_Overnight_')[0:10]
timestr = datestr[11:24].replace('_', '-')
datestr = datestr[0:10].replace('_', '/')
datestr = datestr + ' ' + timestr + 'UTC'

# Exclude band 470 if needed.
exclude = input(f"Use band 470nm? (y/n): ")
print('')
if exclude=='n':
    exclude = True
else: exclude = False
if exclude:
    bands = [b450, b490, b520]
    waves = ['450', '490', '520']
    wavelengths = np.array([450, 490, 520])*10**(-9)
else: 
    bands = [b450, b470, b490, b520]
    waves = ['450', '470', '490', '520']
    wavelengths = np.array([450, 470, 490, 520])*10**(-9)
band0 = bands[0]

# Create the start and end times
stimestr = datestr.split(' ')[1].split('-')[0]
etimestr = datestr.split(' ')[1].split('-')[1][:-3]
date = datestr.split(' ')[0].replace('/', '-')
stimestr = date+' '+stimestr
etimestr = date+' '+etimestr
stime = datetime.strptime(stimestr, '%Y-%m-%d %H%M%S')
etime = datetime.strptime(etimestr, '%Y-%m-%d %H%M%S')
# THESE are used in the Open Meteo API
sday = datetime.strftime(stime, '%Y-%m-%d')
eday = datetime.strftime(stime+timedelta(days=1), '%Y-%m-%d')

stime_str = stime.strftime('%Y-%m-%d')
etime_str = stime.strftime('%Y-%m-%d')

# Pressure for Rayleigh calculation
pressure = srf.get_pressure(lat=40.58776075373724, lon=-105.14760680964913,
                            stime=stime_str, etime=etime_str)
p_time = pressure[(pressure['time'] < etime) & (pressure['time'] > stime)]
p_av = np.mean(p_time['surface_pressure'])
print(f"Pressure at {stime_str}:    {p_av}hPa\n")

# Get the rayleigh optical depth
tau_rs = []
for w in wavelengths:
    w *= 10**6  # Convert m to µm
    tau_rs.append(srf.tau_rs(w, p_av))

print("Rayleigh ODs -------------------")
for i, w in zip(tau_rs,waves):
    print(f"    {w}nm:   {i:.4f}")
print('')

# HARDCODED: Ozone absorption coefficients at each band
a450 = 4.199999999999999740e-03
a470 = 1.009999999999999960e-02
a490 = 2.129999999999999949e-02
a520 = 4.809999999999999692e-02

# Read the Ozone absorption coefficient data
with open('./o3_coeff.txt', 'r') as f:
    lams = []
    coeffs = []
    for line in f:
        lams.append(float(line.split(' ')[0]))
        coeffs.append(float(line.split(' ')[1]))
    f.close()

if exclude:
    del lams[1]
    del coeffs[1]
else:
    pass

if exclude:
    a = [a450, a490, a520]
else:
    a = [a450, a470, a490, a520]

# Ozone column amount in atm-cm from DU
o3_du = 300 / 1000 # estimated
tau_o3 = np.array([o3_du*a_lam for a_lam in a])

# Print outputs
print("Ozone ODs ----------------------")
for i,w in zip(tau_o3, waves):
    print(f"    {w}nm:   {i:.4f}")
print('')

# Loop through each band
for band, rs, o3 in zip(bands, tau_rs, tau_o3):
    band['Langley_slope'] += o3
    band['Langley_slope'] += rs

results = {}
# Calculate the weighted mean AOD for each band
for wave, band, i in zip(waves, bands, range(len(waves))):
    # Individual weights
    band['slope_weight'] = 1 / band['seSlope']**2

    # Mean AOD
    mean_aod = np.mean(-band['Langley_slope'])
    # mean_aod = mean_od - tau_rs[i] - tau_o3[i]


    weighted_aod = np.sum( band['slope_weight'] *
                           (-band['Langley_slope']) ) / np.sum( band['slope_weight'] )
    
    # Standard error of AOD
    se_formal = np.sqrt(1 / np.sum(band['slope_weight']))
    se_empirical = np.std(-band['Langley_slope'], ddof=1) / np.sqrt(len(-band['Langley_slope']))
    # Take the greater of the two...
    seSlope_band = np.maximum(se_formal, se_empirical)

    # Add to the results
    results[f'{wave}'] = {'mean_aod':mean_aod,
                            'weighted_aod':weighted_aod,
                            'se_formal':se_formal,
                            'se_empirical':se_empirical,
                            'seSlope_band':seSlope_band}
    
results = pd.DataFrame(results)

# -----------------------------
# Target wavelength
# -----------------------------
# lam_ref = 675
lam_ref = float(input("Target wavelength [nm]: "))
lambda_ref = lam_ref*10**(-9)

# weighted vs mean AOD
weighted = False

# Compute the logorithmic wavelength, AOD, and weights
lnLambda = np.log( wavelengths )
w = 1 / results.loc['seSlope_band']**2
# How to calculate the error bars???
if weighted:
    lnAOD = np.log( results.loc['weighted_aod'] )
    lnErr = results.loc['seSlope_band'] / results.loc['weighted_aod']
else:
    lnAOD = np.log( results.loc['mean_aod'] )
    lnErr = results.loc['seSlope_band'] / results.loc['mean_aod']



# -----------------------------------
# Plot the wavelengths/AODs in log-log space
# -----------------------------------
fig, ax2 = plt.subplots(figsize=(12,4))

# im2=ax2.plot(lnLambda, lnAOD, marker='>', color='red')
im2=ax2.errorbar(lnLambda, lnAOD, yerr=lnErr, 
                 marker='*', color='red', capsize=4)
ax2.grid(which='both',visible=True, linestyle='-.', 
            color='grey', alpha=0.3)
if weighted:
    for lnwave, lnaod, aod, name in zip(lnLambda, lnAOD, results.loc['weighted_aod'], waves):
        ax2.annotate(f'{name}nm, AOD={aod:.3f}', xy=(lnwave, lnaod))
else:
    for lnwave, lnaod, aod, name in zip(lnLambda, lnAOD, results.loc['mean_aod'], waves):
        ax2.annotate(f'{name}nm, AOD={aod:.3f}', xy=(lnwave, lnaod))
ax2.set_xlabel('ln(Wavelength)')
ax2.set_ylabel('ln(AOD)')
ax2.set_title("ln(AOD) vs ln(Wavelength)")
plt.tight_layout()
plt.show()


# ------------------------------------
# Weighted least-squares
# ------------------------------------
X = np.column_stack([np.ones(len(lnLambda)), lnLambda])
sqrt_w = np.array(np.sqrt(w)) # Is a 1x4 array
sqrt_w_T = sqrt_w[:,None] # Convert to a 4x1 array
X_w = X * sqrt_w_T # Scaled logorithmic wavelengths
Y_w = lnAOD * sqrt_w # Scaled logorithmic AODs

# Compute the Least-squares, returns b in ( a @ x = b )
b, res, rank, s = np.linalg.lstsq(X_w, Y_w, rcond=None)

# Create covariance matrix
deg_freedom = len(Y_w) - X_w.shape[1]
res_var = res[0] / deg_freedom
cov_mat = res_var * np.linalg.inv(X_w.T @ X_w)
uncertainties = np.sqrt(np.diagonal(cov_mat))
slope_err, int_err = uncertainties
alpha = -b[1]
lnBeta = b[0]
aod_ref = np.exp(lnBeta) * lambda_ref**(-alpha)
print(f'AOD at {lam_ref}nm: {aod_ref:.4f}\n')

# Extend the wavelengths to target wavelength
lambda_ext = np.append(wavelengths, lam_ref*10**(-9))
lnLambda_ext = np.log(lambda_ext)


# ---------------------------------------
# Plot the Angstrom extrapolation 
# ---------------------------------------
fig, ax = plt.subplots(figsize=(8,5))
# Plot the raw data
ax.errorbar(lnLambda, lnAOD, yerr=lnErr, capsize=4, 
            marker='>', color='red', label='Å-AOD')
# ax.plot(lnLambda, lnAOD, marker='>', color='red', label='Å-AOD')
# Plot the best-fit, extrapolated to 700nm
ax.plot(lnLambda_ext, lnBeta-alpha*lnLambda_ext, 
        color='blue', linestyle='--', alpha=0.6, 
        label=rf'Fit: $\alpha$={alpha:.3f}')
# ax.plot(lnLambda_ext, lnBeta-(alpha+slope_err)*(lnLambda_ext))
ax.scatter(np.log(lam_ref*10**(-9)), np.log(aod_ref), 
           marker='*', s=100, c='blue')
# Annotate the Bands
if weighted:
        for lnwave, lnaod, aod, name in zip(lnLambda, lnAOD, results.loc['weighted_aod'], waves):
                ax.annotate(f'{name}nm, AOD={aod:.3f}', 
                        xy=(lnwave, lnaod), size=12)
else:
        for lnwave, lnaod, aod, name in zip(lnLambda, lnAOD, results.loc['mean_aod'], waves):
                ax.annotate(f'{name}nm, AOD={aod:.3f}', 
                        xy=(lnwave, lnaod), size=12)
# Annotate the target wavelength
ax.annotate(f"{lam_ref}nm AOD: {aod_ref:.4f}", 
            xy=(np.log(lam_ref*10**(-9)), np.log(aod_ref)+0),
            xytext=(np.log(lam_ref*10**(-9))-0.13, np.log(aod_ref)),
            annotation_clip=True,
            backgroundcolor='#009',
            color='white',
            size=12)
ax.set_ylabel(r'ln($\tau$)', size=15)
ax.set_xlabel(r'ln($\lambda$) [m]', size=15)
plt.grid(which='both',visible=True, 
         linestyle='-.', color='grey', alpha=0.3)
plt.title(f"Angstrom AOD w/ Robust Fit: {datestr}", size=16)
plt.legend()
plt.tight_layout()
plt.show()