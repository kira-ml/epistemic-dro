# Literature and Method Notes

**Status:** Working reading list  
**Last updated:** 2026-10-27

This is not a literature review. It is the minimum set of references needed to implement and defend the project. Verify bibliographic details before citing in a paper.

---

## 1. Robust optimization and DRO

- Ben-Tal, A., & Nemirovski, A. (1998). Robust Convex Optimization. *Mathematics of Operations Research*, 23(4), 769–805.
- Bertsimas, D., Brown, D. B., & Caramanis, C. (2011). Theory and Applications of Robust Optimization. *SIAM Review*, 53(3), 464–501.
- Delage, E., & Ye, Y. (2010). Distributionally Robust Optimization Under Moment Uncertainty with Application to Data-Driven Problems. *Operations Research*, 58(3), 595–612.
- Mohajerin Esfahani, P., & Kuhn, D. (2018). Data-driven Distributionally Robust Optimization Using the Wasserstein Metric: Performance Guarantees and Tractable Reformulations. *Mathematical Programming*, 171(1–2), 115–166.
- Kuhn, D., Esfahani, P. M., Nguyen, V. A., & Shafieezadeh-Abadeh, S. (2019). Wasserstein Distributionally Robust Optimization: Theory and Applications in Machine Learning. *INFORMS TutORials in Operations Research*, 130–166.

**Project use:** The v1 implementation uses a box ambiguity set because it is convex, interpretable, and easy to test. Ellipsoidal DRO is the second specification. Wasserstein DRO is a stretch goal, not a requirement.

---

## 2. CVaR and portfolio optimization

- Markowitz, H. (1952). Portfolio Selection. *The Journal of Finance*, 7(1), 77–91.
- Rockafellar, R. T., & Uryasev, S. (2000). Optimization of Conditional Value-at-Risk. *Journal of Risk*, 2(3), 21–41.
- DeMiguel, V., Garlappi, L., & Uppal, R. (2009). Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy? *Review of Financial Studies*, 22(5), 1915–1953.
- Ledoit, O., & Wolf, M. (2004). Honey, I Shrunk the Sample Covariance Matrix. *Journal of Portfolio Management*, 30(4), 110–119.
- López de Prado, M. (2016). Building Diversified Portfolios that Outperform Out of Sample. *Journal of Portfolio Management*, 42(4), 59–69.

**Project use:** 1/N and sample MVO are mandatory baselines. CVaR is the tail measure. HRP is a robustness baseline. Covariance shrinkage is a diagnostic, not the main contribution.

---

## 3. Uncertainty quantification

- Lakshminarayanan, B., Pritzel, A., & Blundell, C. (2017). Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles. *Advances in Neural Information Processing Systems*, 30. arXiv:1612.01474.
- Vovk, V., Gammerman, A., & Shafer, G. (2005). *Algorithmic Learning in a Random World*. Springer.
- Angelopoulos, A. N., & Bates, S. (2021). A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification. arXiv:2107.07511.
- Gneiting, T., & Raftery, A. E. (2007). Strictly Proper Scoring Rules, Prediction, and Estimation. *Journal of the American Statistical Association*, 102(477), 359–378.

**Project use:** Ensemble variance and conformal intervals are both acceptable. The key requirement is calibration, not the brand of uncertainty method.

---

## 4. Empirical asset pricing and ML

- Fama, E. F., & French, K. R. (1993). Common Risk Factors in the Returns on Stocks and Bonds. *Journal of Financial Economics*, 33(1), 3–56.
- Gu, S., Kelly, B., & Xiu, D. (2020). Empirical Asset Pricing via Machine Learning. *Review of Financial Studies*, 33(5), 2223–2273.
- Harvey, C. R., Liu, Y., & Zhu, H. (2016). … and the Cross-Section of Expected Returns. *Review of Financial Studies*, 29(1), 5–68.
- López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley.

**Project use:** Features and baselines should be standard, not exotic. The contribution is the uncertainty/DRO layer, not a new alpha factor.

---

## 5. Backtest overfitting and multiple testing

- Bailey, D. H., & López de Prado, M. (2014). The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality. *Journal of Portfolio Management*, 40(5), 94–107.
- Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2014). Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance. *Notices of the American Mathematical Society*, 61(5), 458–471.
- Harvey, C. R., & Liu, Y. (2015). Backtesting. *Journal of Portfolio Management*, 42(1), 13–28.

**Project use:** Pre-register the primary metric; report all trials; use deflated Sharpe; never tune on the test set.

---

## 6. Data leakage and point-in-time data

- López de Prado, M. (2018). *Advances in Financial Machine Learning*, chapters on data snooping, purged cross-validation, and backtest overfitting.
- Bailey, D. H., & López de Prado, M. (2014). The Deflated Sharpe Ratio.
- Vendor documentation for CRSP/Compustat, Sharadar, or Norgate, especially delisting returns and report dates.

**Project use:** The data card is the primary artefact. The code guard is `src/epistemic_dro/leakage.py`.

---

## 7. Open questions for the literature review

1. Which DRO ambiguity set is most defensible for cross-sectional return forecasts: box, ellipsoid, or Wasserstein?
2. How should uncertainty be calibrated for monthly stock returns with a small cross-section?
3. Does DRO improve tail risk when the forecast is weak but calibrated?
4. How do transaction costs interact with robustification?
5. What is the right null model for a robust portfolio claim: 1/N, MVO, or the best baseline?

---

## 8. Citation discipline

- Do not cite a paper for a claim it does not make.
- Distinguish “the paper proves,” “the paper finds empirically,” and “the paper argues.”
- Verify volume, pages, and DOI before submission.
- Keep quotes short and exact; prefer paraphrase.
