# Data-First Research Plan: Society, Crime, and Deviance

This document outlines a statistics-only framework to study links between social structure and crime/deviance using official data and well-sourced measures. It avoids ideological framing by defining hypotheses strictly in terms of observable variables and estimable parameters.

## 1. Core outcomes and units
- **Units**: country, region, city, neighbourhood (pick the most granular with reliable data) by year.
- **Outcomes**: counts and rates (per 100k people) for violent crime, property crime, drug offences, reoffending/recidivism.
- **Exposure**: population denominators for each unit-year.

## 2. Data sources (priority: official statistics)
- National statistics offices (e.g., ONS/UK, BLS & FBI/UCR/NIBRS/US, Eurostat, UNODC, World Bank, WHO mortality data for homicide).
- Demography and economy: census data, labour force surveys, tax/benefit statistics.
- Inequality and deprivation: Gini/Palma ratios, income quintile shares, multidimensional deprivation indices (e.g., Index of Multiple Deprivation).
- Education and housing: enrollment, attainment, school quality indices, social housing share, overcrowding measures.
- Health and biology proxies: birthweight distributions, prevalence of developmental conditions, substance use surveys; where available, anonymized polygenic scores or impulsivity/behavior scales from cohort studies (with ethics clearance).
- Geography: population density, urbanization, land-use, distance to services; night-time lights as an intensity proxy where administrative data lag.

## 3. Variable construction
- **Crime rate**: `rate_it = (crime_count_it / population_it) * 100000`.
- **Standardization**: z-score predictors to compare effect sizes; log-transform skewed predictors (e.g., density).
- **Age–sex structure**: % males 15–29, dependency ratios.
- **Inequality**: Gini, top 10% share, 90/10 ratio.
- **Deprivation/"underclass" latent factor**: poverty rate, long-term unemployment, low education %, social housing %, long-term benefit receipt.
- **Biological proxy variables**: cohort polygenic/behavioral risk scores, birth complications, or impulsivity indices—used only where sourced ethically and legally.

## 4. Hypotheses (parameterized, testable)
- **H1 Inequality**: Higher inequality associates with higher crime: `β_G > 0` in panel log-rate models.
- **H2 Deprivation latent factor**: A single factor extracted from deprivation indicators (see §6) predicts higher crime: `β_U > 0`.
- **H3 Demography**: Higher young-male share increases crime: `β_age > 0`.
- **H4 Density/urbanicity**: Higher density raises contact-based offences: `β_density > 0`; explore nonlinearity with splines/quadratics.
- **H5 Biological proxies**: Individual-level biological risk scores have direct effects `θ ≠ 0` after controlling for environment.
- **H6 Mediation**: Part of biological proxy effect is mediated through environment (gene–environment correlation): indirect effect `γ1 * α2 ≠ 0` in path models.

## 5. Core models (choose by data level)
- **Count GLM**: Poisson or Negative Binomial with offset for population: `log(λ_it) = α + X_it β`.
- **Panel with fixed effects**: `log(λ_it) = α_i + γ_t + X_it β` to isolate within-area changes over time.
- **Lagged models**: include `X_i,t-1` to respect temporal order.
- **Difference models**: `Δ log(rate_it) = β ΔX_it + …` to focus on changes.
- **Individual-level linear/GLM**: `Y_k = α + θ Z_k + W_k β + ε_k` for biological proxies and controls.
- **Path/SEM**: environment `E_k = γ0 + γ1 Z_k + η_k`; outcome `Y_k = α0 + α1 Z_k + α2 E_k + ε_k`; decompose direct/indirect effects.

## 5b. Advanced formulations (when data support them)
- **Zero-inflated / hurdle models**: separate prevalence vs. intensity. Example hurdle form: `Pr(C_it>0)=logit^{-1}(α_i+γ_t+X_it β_p)`, `C_it | C_it>0 ∼ NegBin(μ_it, κ)` with `log μ_it = α_i + γ_t + X_it β_i`.
- **Random-effects Poisson–Gamma (NegBin2) panel**: `log λ_it = α + u_i + v_t + X_it β`, with `u_i ~ N(0, σ_u^2)` capturing unobserved area heterogeneity.
- **Hierarchical shrinkage for small areas**: `β_j ~ N(0, τ^2)` or horseshoe priors; posterior mean shrinks unstable coefficients toward zero to avoid overfitting sparse geographies.
- **State-space / latent dynamic factors**: `λ_it = exp(α_i + γ_t + f_t + X_it β)`, with `f_t = ϕ f_{t-1} + ω_t`; useful for capturing global crime trends not explained by observables.
- **Spatiotemporal smoothing**: Conditional autoregressive (CAR) priors for neighboring areas `u_i | u_{-i} ∼ N( (∑_j w_ij u_j / ∑_j w_ij), σ^2 / ∑_j w_ij )` combined with yearly random walks `v_t = v_{t-1} + η_t` to stabilize maps of crime risk.
- **Causal DiD with staggered adoption**: event-time coefficients `β_{g,ℓ}` estimated with Sun–Abraham or Callaway–Sant’Anna estimators to handle heterogeneous treatment effects and timing.

## 6. Latent "underclass" factor (measurement then regression)
1. Indicators: poverty, long-term unemployment, low education, social housing, long-term benefit receipt.
2. Factor analysis/PCA: `D_j,i = λ_j U_i + ε_j,i`; extract factor scores `Û_i`.
3. Crime model: `log(λ_i) = β0 + β_U Û_i + controls`.
4. Test `H0: β_U = 0`.

## 7. Model diagnostics and robustness
- Overdispersion check; switch to Negative Binomial if variance >> mean.
- Multicollinearity: variance inflation factors; drop/recombine predictors if VIF high.
- Nonlinearity: splines/quadratics for density/inequality.
- Sensitivity: alternate deprivation indicators, alternate crime outcomes, exclude influential units, different lags.
- Goodness-of-fit: AIC/BIC, out-of-sample deviance, posterior predictive checks if Bayesian.

## 8. Causal-identification upgrades (if feasible)
- **Fixed-effects event studies** for policy shocks (e.g., benefit changes, policing reforms).
- **Instrumental variables**: plausibly exogenous shifts in inequality/deprivation (e.g., commodity price shocks in resource regions) affecting crime only via economic channels.
- **Difference-in-differences**: staggered adoption of policies with careful parallel-trends checks.
- **Synthetic controls**: for singular interventions (e.g., major policing reform in one city).

## 9. Ethics and reproducibility
- Use anonymized, legally shareable data; avoid re-identification risks with biological proxies.
- Pre-register hypotheses and model specifications; publish code and data cleaning steps.
- Provide uncertainty (CIs, posterior intervals), not just point estimates; avoid deterministic claims.

## 10. Minimal workflow (runnable blueprint)
1. Ingest official stats (crime counts, population, socioeconomics) into tidy panel tables.
2. Construct rates and standardized predictors; save data dictionary.
3. Run exploratory correlations and single-predictor GLMs.
4. Fit multivariable panel models with fixed effects and offsets.
5. Build latent deprivation factor; refit models including the factor.
6. Test inequality and demographic hypotheses; record coefficient signs, magnitudes, uncertainty.
7. Run sensitivity (alternate lags, functional forms, subsets).
8. Summarize results with tables/plots, highlighting which hypotheses survive robustness checks.

This plan keeps every claim linked to estimable parameters and official or well-sourced data, enabling transparent, reproducible analysis of the connections between social structure and crime/deviance.
