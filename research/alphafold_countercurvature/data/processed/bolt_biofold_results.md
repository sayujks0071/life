# Bolt-BioFold ⚡ Analysis Report

Sources: DefaultSeed_Proprioception, DefaultSeed_NuclearStiffness, DefaultSeed_ECM_Gravity, DefaultSeed_Proprioception_Dev

## 1. Results Table
| Identity | Species | Length | pLDDT_mean | pLDDT_median | pLDDT_frac_high | pLDDT_frac_ok | pLDDT_frac_low | PAE_mean | PAE_blockiness | Disorder_Proxy | Hinge_Cands | Rg | End_to_End | Curvature | Torsion | Anisotropy | Principal_Axis | Hotspots | Exposed_Frac | Charged_Patch | Domains | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PIEZO2 (Q9H5I5) | Homo sapiens | 709 | 79.4 | 88.4 | 0.42 | 0.37 | 0.21 | 17.0 | 2.8 | 0.14 | 0 | 43.4 | 28.4 | 0.329 | 1.428 | 4.44 | [-0.687, -0.068, 0.724] | 460:0.38; 239:0.38; 138:0.38 | 0.56 | 0.25 | 7 | MultiDomUncert |
| LMNA (P02545) | Homo sapiens | 664 | 76.4 | 93.1 | 0.58 | 0.11 | 0.31 | 24.9 | 2.56 | 0.26 | 0 | 71.2 | 278.1 | 0.344 | 1.194 | 4.75 | [-0.668, -0.244, 0.703] | 508:0.40; 519:0.39; 30:0.38 | 0.87 | 0.4 | 3 | MultiDomUncert |
| COL1A1 (P02452) | Homo sapiens | 1464 | 52.7 | 44.2 | 0.15 | 0.05 | 0.8 | 27.4 | 6.55 | 0.67 | 16 | 23.5 | 49.0 | 0.295 | 1.859 | 2.8 | [-0.475, 0.297, 0.828] | 1315:0.39; 1258:0.38; 1431:0.38 | 0.87 | 0.3 | 3 | LowConf, MultiDomUncert |
| RUNX3 (Q13761) | Homo sapiens | 415 | 60.6 | 46.3 | 0.28 | 0.04 | 0.68 | 25.6 | 0.0 | 0.56 | 12 | 15.8 | 53.0 | 0.284 | 1.965 | 2.06 | [-0.510, 0.008, 0.860] | 159:0.39; 69:0.38; 54:0.38 | 0.78 | 0.37 | 1 | LowConf |

### CSV Block
```csv
Identity,Species,Length,pLDDT_mean,pLDDT_median,pLDDT_frac_high,pLDDT_frac_ok,pLDDT_frac_low,PAE_mean,PAE_blockiness,Disorder_Proxy,Hinge_Cands,Rg,End_to_End,Curvature,Torsion,Anisotropy,Principal_Axis,Hotspots,Exposed_Frac,Charged_Patch,Domains,Flags
PIEZO2 (Q9H5I5),Homo sapiens,709,79.4,88.4,0.42,0.37,0.21,17.0,2.8,0.14,0,43.4,28.4,0.329,1.428,4.44,"[-0.687, -0.068, 0.724]",460:0.38; 239:0.38; 138:0.38,0.56,0.25,7,MultiDomUncert
LMNA (P02545),Homo sapiens,664,76.4,93.1,0.58,0.11,0.31,24.9,2.56,0.26,0,71.2,278.1,0.344,1.194,4.75,"[-0.668, -0.244, 0.703]",508:0.40; 519:0.39; 30:0.38,0.87,0.4,3,MultiDomUncert
COL1A1 (P02452),Homo sapiens,1464,52.7,44.2,0.15,0.05,0.8,27.4,6.55,0.67,16,23.5,49.0,0.295,1.859,2.8,"[-0.475, 0.297, 0.828]",1315:0.39; 1258:0.38; 1431:0.38,0.87,0.3,3,"LowConf, MultiDomUncert"
RUNX3 (Q13761),Homo sapiens,415,60.6,46.3,0.28,0.04,0.68,25.6,0.0,0.56,12,15.8,53.0,0.284,1.965,2.06,"[-0.510, 0.008, 0.860]",159:0.39; 69:0.38; 54:0.38,0.78,0.37,1,LowConf
```

## 2. Key Plots Summary
- `LMNA_plddt.png`: pLDDT profile for LMNA
- `LMNA_pae.png`: PAE heatmap for LMNA
- `PIEZO2_plddt.png`: pLDDT profile for PIEZO2
- `PIEZO2_pae.png`: PAE heatmap for PIEZO2
- `COL1A1_plddt.png`: pLDDT profile for COL1A1
- `COL1A1_pae.png`: PAE heatmap for COL1A1

## 3. Interpretation
**Family: DefaultSeed_ECM_Gravity**
- **COL1A1**: COL1A1: Anisotropy=2.8, pLDDT=53. Intermediate shape. Warning: Low confidence structure. Detected 16 potential flexible hinges; may act as mechanical sensor/switch. (Conf: Low). Test: Mutate hinge region to test effect on mechanosensitivity.

**Family: DefaultSeed_NuclearStiffness**
- **LMNA**: LMNA: Anisotropy=4.8, pLDDT=76. Highly extended/fibrous.  Rigid rod-like geometry suggests load-bearing capacity or long-range connectivity. (Conf: Medium). Test: Verify fiber formation in vivo; test mechanical stiffness.

**Family: DefaultSeed_Proprioception**
- **PIEZO2**: PIEZO2: Anisotropy=4.4, pLDDT=79. Highly extended/fibrous.  Rigid rod-like geometry suggests load-bearing capacity or long-range connectivity. (Conf: Medium). Test: Verify fiber formation in vivo; test mechanical stiffness.

**Family: DefaultSeed_Proprioception_Dev**
- **RUNX3**: RUNX3: Anisotropy=2.1, pLDDT=61. Intermediate shape. Warning: Low confidence structure. Detected 12 potential flexible hinges; may act as mechanical sensor/switch. (Conf: Low). Test: Mutate hinge region to test effect on mechanosensitivity.


## 4. Best Next Move
Add proteins: Expand search to include more cytoskeletal linkers.

## 5. Quality & Reproducibility Checklist
- Data Source: AlphaFold DB (fetched via scripts/02_fetch_afdb.py)
- Date/Time: 2026-02-05 19:31:50
- Code Version: 646c850
- Parameters: pLDDT threshold >= 70 for geometry; Smoothing window = default
- Notes: 4 structures analyzed. Source config: research/alphafold_countercurvature/config/targets.yaml
