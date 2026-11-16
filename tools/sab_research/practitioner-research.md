# How practitioners actually choose and trade pairs — research memo for "Stat Arb for Non Quant · Volume 2"

Date: 2026-11-16 · Scope: the owner's question "is passing a statistical test enough, or do people who do this for a living work differently?" plus his two examples: (a) correlation and cointegration both significant → is the pair usable? (b) correlation 0.98 → maybe no money to be made.
Method: primary sources wherever I could open them (PDF text extracted and grepped; page = page of the version named), abstracts via the publisher, OpenAlex or Semantic Scholar where the full text was paywalled, and GitHub source code for open-source tools. Each item is marked **[verified: …]** with what I actually saw. Where I relied on a secondary summary, it says so. Nothing here is from memory alone.
Labels: **CONSENSUS** = several independent primary sources agree · **CONTESTED** = credible sources disagree · **FOLKLORE** = widely repeated practitioner rule with little or no published test.

Empirical check on our own data (formation + validation only, final test untouched) is in §8. Script: `/tmp/claude-0/-home-user-Claude-code-project/01c53d75-2767-5ee8-9670-4f78782fa8cb/scratchpad/pairs_check.py` (scratchpad; copy it into the repo if the numbers will be used in a page).

---

## 0. Short answer to the owner

1. **No one serious treats "p < 0.05" as a licence to trade.** In published work and in open-source practice, a cointegration test is one filter in a chain (economic grouping → cheap distance/correlation screen → cointegration test → mean-reversion speed and crossing filters → out-of-sample check → many pairs at once with stops). Tests are also used to *rank* pairs, not just to pass/fail them.
2. **Cointegration found in one window often does not survive into the next.** Clegg (2014) found only about 5% of S&P 500 pairs cointegrated in any year (the rate you would expect by chance) and only 4.5–7% of those still cointegrated the following year. Our data shows the same thing: 0 of 8 formation "passes" kept a stationary spread with the formation hedge ratio in validation.
3. **Owner's example (b) is right in principle and is a known flaw of the classic distance method.** The "perfect" pair in Gatev et al.'s ranking has a spread of zero and therefore no profit. Krauss (2017) shows the method's top-ranked pairs have the *lowest* spread volatility. What you need is a spread that moves enough to cover costs and keeps coming back, not prices that move together.
4. **Owner's example (a): both tests significant is still not enough.** Our own data gives a sharp example. All 8 formation "cointegrated" pairs contain LTC, and their hedge ratios are about 0 (−0.06 to +0.07). The test was detecting that **LTC on its own** was range-bound, not a two-coin relationship. A practitioner would catch this by asking "what is the economic link, and does h make sense?"
5. **Practitioners add an economic reason, diversification, time stops and periodic re-formation**, and they expect the edge to decay (Do & Faff 2010/2012; Rad, Low & Faff 2016; Clegg & Krauss 2018 all report shrinking or vanished profits after about 2002–2010).

---

## 1. Pair selection in practice: methods and comparative evidence

### 1.1 The main families

| Family | What it ranks on | Key reference | Notes |
|---|---|---|---|
| Distance (GGR) | Sum of squared differences (SSD) of normalised price indices over a 12-month formation; trade the top 5/20 pairs for 6 months; open at a 2-SD gap, close at the crossing | Gatev, Goetzmann & Rouwenhorst (2006), *RFS* 19(3):797–827, doi 10.1093/rfs/hhj020 | **[verified: Yale ICF WP 08-03 version, Feb 2006, §2.1–2.2 and the Table 2 discussion]** "We form pairs over a twelve-month period (formation period) and trade them in the next six-month period"; the method is chosen because "Interviews with pair traders suggest that they try to find two stocks whose prices 'move together.'" Top-20 pairs: "71% of the stocks in the top 20 pairs are utility stocks". Headline result up to about 11%/yr. |
| Distance with refinements | Same, but only within 48 Fama–French industries, and favouring pairs with many **zero crossings** in formation | Do & Faff (2010) *FAJ* 66(4):83–95; Do & Faff (2012) *J. Financial Research* 35(2):261–287 | **[verified via Krauss 2015 WP p. 8; JFR abstract via OpenAlex]** Krauss: Do & Faff "only allow for matching securities within the 48 Fama-French industries" and "favor pairs with a high number of zero-crossings in the formation period"; the top portfolios "are still slightly profitable, even after full consideration of transaction costs". JFR abstract: about "30 basis points per month among portfolios of well-matched pairs that are formed within refined industry groups", but "both these types of contrarian investing are largely unprofitable after 2002." |
| Return correlation | Pearson correlation of monthly returns over 5 years; trade divergence from the most-correlated partner(s) | Chen, Chen, Chen & Li (2019), *Management Science* 65(1):370–389, doi 10.1287/mnsc.2017.2825 | **[verified: abstract via OpenAlex]** profits "largely explained by the short-term reversal and a version of the industry momentum". |
| Cointegration (Vidyamurthy) | Engle–Granger regression of log prices, then a *tradability* check | Vidyamurthy (2004), *Pairs Trading: Quantitative Methods and Analysis*, Wiley | **[verified only via Krauss 2015 WP p. 22]** "Key for a practitioner is not necessarily a cointegrated pair, but a spread with strong mean-reversion properties. A valid proxy for the latter is the zero-crossing frequency". I did not see the book itself. |
| Cointegration after a distance shortlist | Rank by SSD, test the top pairs with Engle–Granger, keep the first 20 that pass | Rad, Low & Faff (2016), *Quantitative Finance* 16(10):1541–1558, doi 10.1080/14697688.2016.1164337 | **[verified: author PDF, §4.2.2, journal p. 1546]** "we sort all possible combinations of pairs based on their SSD … Second, we test each of the pairs with the least SSD for cointegration … We continue until 20 cointegrated pairs with minimum SSD are selected". |
| Copula | Fit marginals and a copula to returns; trade on conditional probabilities | Rad, Low & Faff (2016); Tadi & Witzany (2025), *Financial Innovation* 11, doi 10.1186/s40854-024-00702-7 | See §5 for crypto. |
| Time-series / OU / stochastic control | Model the spread as OU, derive entry/exit rules | Survey: Krauss (2017) *J. Economic Surveys* 31(2):513–545, doi 10.1111/joes.12153 | **[verified: FAU WP 09/2015 on EconStor]** Krauss groups the field into "distance approach, cointegration, time-series approach, stochastic control, and other methods" and reviews more than 90 papers. |
| Residual / factor stat arb | Regress each stock on PCA factors or a sector ETF, trade the OU residual | Avellaneda & Lee (2010), *Quantitative Finance* 10(7):761–782, doi 10.1080/14697680903124632 | **[verified: NYU preprint, June 2009, §4]** A 60-day rolling estimate, and only names with fast mean reversion are kept: "We selected stocks with mean-reversion times less than 1/2 period (κ > 252/30 = 8.4)". Thresholds: open at \|s\| > 1.25, close long at −0.50, close short at 0.75. **No significance test is used as the gate; the gate is reversion speed.** |
| ML clustering | PCA on returns → OPTICS clusters → pairs only within a cluster → 4 rules (see §4) | Sarmento & Horta (2020), *Expert Systems with Applications* 158:113490, doi 10.1016/j.eswa.2020.113490 | **[verified: Sarmento MSc thesis, IST Lisbon, Sep 2019, §3.5]** Thresholds are in §4. Data: 5-minute prices of 208 commodity-linked ETFs (search snippet of the published version; not checked in full text). |
| Partial cointegration | The spread = random walk + AR(1); select and trade on the mean-reverting part | Clegg & Krauss (2018), *Quantitative Finance* 18(1):121–138, doi 10.1080/14697688.2017.1370122 | **[verified: FAU WP 05/2016 on EconStor]** same-GICS-sector pairs only, 48-month formation "to increase the power of the tests" (p. 13); more than 12%/yr after costs over 1990–2015, but in 01/2010–10/2015 "all strategies disappoint, including PCI. Annualized returns are all close to zero in the negative domain" (p. 29, Table 13). |

### 1.2 Which works out of sample? (CONTESTED, with a clear decay pattern)

- **Rad, Low & Faff (2016)** **[verified: abstract and §5.3 of the author PDF]**: US equities 1962–2014. Mean monthly excess returns of 91, 85 and 43 bps before costs and 38, 33 and 5 bps after costs (distance, cointegration, copula). "from 2009, the frequency of trading opportunities via the distance and cointegration methods" fell considerably. Converged trades: more than 98% are profitable. The distance method has the highest share of converged trades, 62.53%; unconverged trades carry the fat left tail. → **The simple distance method is competitive; cointegration is better in turbulent markets.**
- **Huck & Afawubo (2015)**, *Applied Economics* 47(6):599–613, doi 10.1080/00036846.2014.975417 **[verified: abstract text via search snippet and Krauss WP p. 24–25]**: on S&P 500 constituents, after risk and costs the distance method gives insignificant excess returns, while cointegration gives "a high, stable and robust return".
- **Do & Faff (2010)** **[verified: abstract; 32% figure via Krauss WP p. 7]**: profitability is declining. "32 percent of all identified pairs based on the distance metric actually do not converge". Worsening arbitrage risk explains "up to 70 percent of the drop in profits" (FAJ abstract).
- **Bui & Ślepaczuk (2022)**, *Physica A* 592:126784, doi 10.1016/j.physa.2021.126784 **[verified: abstract via OpenAlex]**: NASDAQ-100, daily, 2000–2021. A Hurst-based selection "is better than the cointegration method but is not superior as compared to the correlation method", and none of them beats the benchmark.
- **Farago & Hjalmarsson (2019)**, *JFQA* 54(2):629–665 **[verified: abstract via RePEc]**: if stocks really were cointegrated, theoretical Sharpe ratios would be implausibly high. They find "there is little evidence of cointegration", so pairs profits must come from "a weaker or less stable dependency structure". → **The profits academics measure probably do not come from true cointegration.**

**Bottom line (CONSENSUS on the direction, CONTESTED on the ranking):** no method dominates everywhere. Every family loses most of its after-cost edge in recent US equity samples. Methods that add *a mean-reversion check* on top of *closeness* (industry + crossings, SSD + cointegration, partial cointegration) do better than closeness alone.

---

## 2. Correlation vs cointegration, and the "0.98 but no money" problem

### 2.1 What the sources say (CONSENSUS)

- **High correlation is neither necessary nor sufficient.**
  - The Quantopian lecture "Introduction to Pairs Trading" (Mackenzie & Margenot) builds both counter-examples: "Correlation Without Cointegration … two series that just diverge" and "Cointegration Without Correlation … a normally distributed series and a square wave". **[verified: notebook in github.com/quantopian/research_public, commit e183ecd, `notebooks/lectures/Introduction_to_Pairs_Trading/notebook.ipynb`]**
  - Krauss (2015 WP p. 7): GGR's "high correlation may well be spurious, since high correlation is not related to a cointegration relationship (Alexander, 2001)".
  - Palomar, *Portfolio Optimization* (online book, §15.4) on KO–PEP: "Their returns show a correlation of 0.66, which is statistically significant, but different from cointegration". All residual unit-root tests fail to reject at 1%; half-life is 70 days. **[verified: portfoliooptimizationbook.com/book/15.4-discovering-pairs.html]**
- **Ernie Chan (blog, 6 Nov 2006, "Cointegration is not the same as correlation")** **[verified: epchan.blogspot.com]**: "If two stocks simply move in a correlated manner, there may never be any widening of the spread." This is almost exactly the owner's example (b).
- **The analytic version of example (b)** — Krauss (2015 WP pp. 6–7, eqs. 1–2) **[verified]**: SSD = spread variance + (spread mean)². So "an 'ideal pair' in the sense of GGR with zero squared distance has a spread of zero and thus produces no profits", and "table 2 of GGR's results clearly shows decreasing spread volatility as we move up the ranking". "GGR's selection metric is prone to form pairs with low spread variance, which ultimately limits profit potential". Krauss's suggested fix: keep low drift in the spread mean, then prefer **high** spread variance, then test cointegration with family-wise error control.
- Krauss also notes (WP pp. 9–10, eqs. 4–5) that high **return** correlation lowers the variance of spread *returns*, but the two legs can still have different volatilities. That is why a hedge ratio, not 1:1, is needed.
- **Open-source code puts the fix into practice.** ArbitrageLab's distance module offers `method='variance'` (among the top-SSD `selection_pool`, sort by spread variance) and `method='zero_crossing'`, plus `skip_top` "if you'd like to take num_top pairs starting from the 10th one". **[verified: `arbitragelab/distance_approach/basic_distance_approach.py`, commit 32ccd56, May 2024, BSD-3]**

### 2.2 Numbers: how much spread is there at a given correlation? (our own arithmetic, §8.6)

Take two coins with 3.5% daily volatility each and h = 1. Daily spread volatility = σ√(2(1−ρ)): ρ 0.80 → 2.21%, 0.95 → 1.11%, **0.98 → 0.70%**, 0.995 → 0.35%. The profit per trade with the book's rule (enter at 2 SD, exit at 0.5 SD) is about 1.5 × the stationary SD of the spread. At ρ = 0.98 with a 5-day half-life that is about 2.1% per trade, roughly 11× the book's 0.20% round-trip cost but only 3.6× a retail-like 0.60% (0.1% fee + 0.05% slippage per fill). At ρ = 0.995 with a 2-day half-life it is 0.74%: 3.7× book cost and **1.2× retail cost, i.e. no money**.
**So the owner's intuition holds once correlation is very high and reversion is fast, especially at retail costs or intraday.** At daily frequency with 0.05% fees, our 10 coins never get there: the highest return correlation is 0.82, and the spread SD is 47–301× the round-trip cost (§8.2). For our data, cost is not the binding constraint; *drift of the spread* is.

### 2.3 Level correlation is meaningless for trending assets (CONSENSUS)

Correlation of price *levels* between two trending series is the classic spurious-regression trap; that is the reason cointegration testing exists. In our data, BTC/SOL has level correlation **0.97** but an Engle–Granger p of 0.31. The five highest level-correlation pairs lost money under the rolling-ruler rule (0/5 profitable, §8.4).

---

## 3. Do practitioners require statistical significance?

### 3.1 Persistence: cointegration found in-sample often disappears (CONSENSUS)

- **Clegg (2014)**, "On the persistence of cointegration in pairs trading", SSRN working paper. **[Partly verified.]** The paper itself is cited in Clegg & Krauss (2018 WP p. 2): "Clegg (2014) finds that the property of being cointegrated is not persistent". The numbers come from the CXO Advisory summary (25 Sep 2014), **not checked against the paper**: S&P 500 2002–2012, about 5.0% of pairs cointegrated in a given year by ADF (about what chance gives), of which 4.9% were still cointegrated the next year (Phillips–Perron 4.5%; most favourable test 7.2%). The quoted conclusion: "evidence does not support a belief that cointegration of pairs of liquid U.S. stocks persists to an extent that encourages a pairs trading strategy."
- Palomar §15.4 **[verified]**: "empirical studies have shown evidence that does not support the hypothesis that cointegration is a persistent property"; pairs "can just as easily lose cointegration in the subsequent out-of-sample period".
- The Quantopian lecture ends with exactly this outcome. The solar-stock pair found in 2014 fails out of sample: "since our p-value is above the cutoff of 0.05, we conclude that our model will no longer be valid" **[verified]**.
- Clegg & Krauss (2018) model the reason: spreads are "bombarded by a steady stream of permanent shocks" (WP p. 2), which is why they allow a random-walk component in the spread.

### 3.2 Multiple testing (CONSENSUS that it matters; practice is uneven)

- Krauss (2015 WP p. 24) on a Brazilian study: "Cointegration testing on 1225 pairs would thus produce 61 cointegrated pairs as false positives in expectation". He recommends controlling the family-wise error rate (Cummins & Bucca 2012). Do & Faff (2012) "test a total of 29 different combinations of selection algorithms", which makes them "more susceptible for data snooping" (WP p. 8).
- Quantopian lecture **[verified]**: "WARNING: This will incur a large amount of multiple comparisons bias." It describes a spectrum: an economic hypothesis for one pair incurs "no multiple comparisons bias"; a search through hundreds of securities incurs "a very large amount".
- Sarmento thesis §3.1 **[verified, p. 37 of the PDF]**: with 20 assets, "190 possible combinations, which means approximately 9 results would be wrong (5% of 190)".
- General finance: Harvey, Liu & Zhu (2016), *RFS* 29(1):5–68 — "a new factor needs to clear a much higher hurdle, with a t-statistic greater than 3.0". Bailey & López de Prado (2014), *JPM* 40(5):94–107 — the Deflated Sharpe Ratio. **[verified: abstracts via OpenAlex]**
- **Our book already does this right in chapter 3:** 2 passes out of 45 against 2.25 expected by luck. In §8 a different but common choice — the regression direction that gives the stronger statistic, a second test per pair — gives 8 passes. That itself is a lesson in how quickly the count of "discoveries" grows with analyst choices.

### 3.3 How p-values are actually used (practice; partly FOLKLORE)

- **As a filter inside a chain, not the sole gate.** Rad et al. (SSD → EG); Sarmento & Horta (cluster → EG at 1% → Hurst → half-life → crossings); Clegg & Krauss CI1 (same sector, then both ADF and Johansen at 5%).
- **As a ranking signal.** Dunis et al. (cited in Krauss WP pp. 23–24) find "in-sample t-statistics of the ADF test … seem to have a certain predictive power for the out-of-sample information ratio", so the *strength* of the statistic, not a yes/no, carries information. Do & Faff rank by zero crossings; GGR rank by SSD.
- **Not at all, replaced by a speed rule.** Avellaneda & Lee keep any residual whose OU mean-reversion time is under 30 days (κ > 8.4) on a rolling 60-day window. Chan, *Algorithmic Trading* (Wiley 2013), says, per secondary quotes that I could not open in the book, that "we don't necessarily need true stationarity or cointegration in order to implement a successful mean reversion strategy" (**unverified against the book**).
- **Rolling re-estimation** is the default in practice: GGR re-form every month with overlapping 6-month windows; Avellaneda & Lee re-estimate daily on 60 days; Clegg & Krauss re-form every month.

### 3.4 The economic reason (CONSENSUS)

- GGR offer results by S&P sector. Do & Faff, Clegg & Krauss and Rad et al. restrict to the same industry or sector, which "has a potential to identify more meaningful pairs and to reduce spurious correlations" (Krauss WP p. 8).
- Quantopian: start from "some underlying economic link … two companies that manufacture the same product, or two companies in one supply chain".
- Engelberg, Gao & Jagannathan (2009, SSRN 1330689) **[abstract seen in search snippets only; not opened]**: profits are higher when the divergence comes from liquidity shocks, lower when it comes from news specific to one stock ("such a divergence tends to persist"), and "closing out positions that do not converge within 10 days leads to higher risk adjusted returns … when compared to holding positions for 6 months". → **Why the legs diverged matters more than the p-value.**
- **For crypto the analogue of "same industry"** is a contract-level link: spot vs perp vs dated future (the volume 1 basis trades), the same coin on two venues, wrapped vs native, LST vs underlying, or an index vs its constituents. Two unrelated alt-coins have no economic anchor. This is **FOLKLORE-plus-logic**: I found no paper that tests "economic link vs none" in crypto pairs directly.

---

## 4. Practical filters people layer on top

| Filter | Threshold seen | Who (verified where) |
|---|---|---|
| Same industry/sector | 48 FF industries; GICS sector; 4 S&P groups | Do & Faff; Clegg & Krauss WP p. 14; GGR WP §2.1 |
| Cointegration p-value | 1% | Sarmento thesis §3.5 ("cointegrated, using a p-value of 1%") |
| | 5% (both ADF and Johansen) | Clegg & Krauss CI1 (WP p. 14) |
| | ArbitrageLab default 95% critical value | `spread_selection/cointegration.py`, `adf_cutoff_threshold=0.95` |
| Hurst exponent of spread | H < 0.5 | Sarmento §3.5; ArbitrageLab `hurst_exp_threshold=0.5` |
| Half-life | 1 day < HL < 1 year | Sarmento §3.5: "should lay between one day and one year"; ArbitrageLab `min_half_life=365`, which despite its name is a *maximum*: `half_life <= min_half_life` |
| | OU reversion time < 30 days on a 60-day window | Avellaneda & Lee §4 |
| Mean / zero crossings | ≥ 12 per year | Sarmento §3.5: "crosses a mean at least 12 times per year … one cross per month"; the reason given is "to provide enough liquidity" and to discard pairs that "do not cross the mean, providing no opportunities to exit". **Note:** ArbitrageLab's default `min_crossover_threshold=12` counts per *analysed period*, not per year |
| | rank by count | Do & Faff; ArbitrageLab `method='zero_crossing'` |
| Spread variance (high, not low) | rank top-SSD pool by variance | Krauss WP p. 8 (proposal); ArbitrageLab `method='variance'` |
| Max holding / time stop | a small multiple of the half-life | Chan blog 2007: "exit a spread once we have held it for 3 times the half-life"; reply: "some small multiple (<10) of this half life" |
| | 10 days beats 6 months | Engelberg et al. (abstract, unverified full text) |
| Wait one day after signal | — | GGR WP (discussion of Table 1, Panel B): profits drop "about 30-55" bps when opening on the day after divergence (bid-ask bounce) |
| Liquidity | top size deciles; no missing days | GGR (74% of top-20 stocks in top 3 size deciles, Table 2 Panel B discussion); Clegg & Krauss "do not exhibit missing data" |
| Longer formation for test power | 48 months | Clegg & Krauss WP p. 13 |
| Structural-break / stability of h | (not found with a published threshold) | Our ch. 5–6 cover it; partial cointegration and Kalman (Palomar §15.4) are the published responses. **FOLKLORE on thresholds.** |

Evidence that these filters *help out of sample* is thin and mixed:
- Sarmento reports a "visible influence" of the Hurst and half-life constraints (thesis §6.2).
- Bui & Ślepaczuk find Hurst selection no better than correlation.
- Grande et al. (2024), *Mathematics* 12(18):2911 **[verified: abstract]**, find that crypto spreads with anti-persistent local Hurst "revert to their mean significantly faster".
- In our own data (§8), Hurst ranked the **wrong** way (Spearman +0.26 with profit, where lower Hurst "should" help).

---

## 5. Crypto specifically

- **Fil & Kristoufek (2020)**, "Pairs Trading in Cryptocurrency Markets", *IEEE Access* 8:172644–172651, doi 10.1109/ACCESS.2020.3024619. **[verified: full abstract via Semantic Scholar; full text not opened]**
  - Distance and cointegration methods on 26 liquid Binance coins at 5-minute, 1-hour and daily frequency. "In our backtests, the strategies underperform classical benchmarks." Results are "quite sensitive to parameter settings and external factors such as transaction costs or execution windows".
  - "the most common daily distance method returns −0.07% monthly, this increases to 11.61% monthly for 5-minute frequency".
  - They find "simple mean-reverting behavior in intraday prices that is missing in daily data".
  - → **For our daily-close book this is the single most relevant prior: daily crypto pairs did not work there.**
- **Leung & Nguyen (2019)**, *Studies in Economics and Finance* 36(4):581–599, doi 10.1108/SEF-08-2018-0264 **[verified: abstract]**: Johansen and EG find a cointegrated portfolio of BTC, ETH, BCH and **LTC**; strategies are "profitable under different configurations"; stop-loss variants are compared. In-sample flavour; old (2017–2018) data.
- **Tadi & Witzany (2025)**, *Financial Innovation* 11, doi 10.1186/s40854-024-00702-7 **[verified: abstract]**: linear and nonlinear cointegration tests plus a correlation filter, then copula signals; the method "outperforms previously examined trading strategies of pairs based on cointegration or copulas". Frequency and cost details were not checked (full text would not download).
- **Pindza & Mba (2026)**, *Quantitative Finance and Economics* 10(2):378–404, doi 10.3934/qfe.2026016 **[verified: abstract]**: ADF/KSS cointegration selection plus copula signals on 10 Binance USDT perps, hourly, 2021–2023. At 0.08% round-trip cost the market-neutral copula strategies "generated negative net returns after accounting for trading costs".
- **Fischer, Krauss & Deinert (2019)**, *JRFM* 12(1):31, doi 10.3390/jrfm12010031 **[verified: abstract]**: a cross-sectional (not pairs) random forest on 40 coins, minute data. Out-of-sample "7.1 bps per day, after transaction costs of 15 bps per half-turn", flagged against volume constraints.
- **Gabriel & Kunst (2024)**, IHS Vienna Working Paper 52 **[verified: abstract page]**: ten major coins; Johansen-based cointegrated portfolios "generate the highest abnormal log-returns" in and out of sample; five of six strategies beat passive out of sample. *Working paper, not peer-reviewed.*
- **Saji (2021)**, *IMFI* 18(3):127–141 **[verified: abstract]**: positive pairs profits, but on **monthly** closes over only 2018–2019 (24 observations). Too short to carry weight.

**Synthesis (CONTESTED):** published crypto pairs results are mostly positive in-sample or at high frequency. They turn flat or negative at daily frequency (Fil & Kristoufek) or after realistic costs (Pindza & Mba). LTC shows up repeatedly in "cointegrated" crypto findings (Leung & Nguyen; our chapter 3; §8 here). In our data that is because **LTC alone was stationary** over 2022–24 (ADF −3.50, p ≈ 0.008), not because of a stable pair link.

---

## 6. Community and GitHub practice: concrete pipelines

1. **Hudson & Thames ArbitrageLab** (github.com/hudson-and-thames/arbitragelab, BSD-3, last commit May 2024) **[verified in source]**:
   - *Cointegration/ML route* (`spread_selection/cointegration.py`, implementing Sarmento & Horta):
     1. Construct spreads with a chosen hedge ratio (OLS, TLS, min-half-life, Johansen, Box–Tiao, ADF-optimal).
     2. Engle–Granger statistic ≤ the 95% critical value.
     3. Hurst ≤ 0.5.
     4. 0 < half-life ≤ 365.
     5. Crossings ≥ 12. All four are intersected (`reduce(np.intersect1d, …)`).

     Upstream, `ml_approach/optics_dbscan_pairs_clustering.py` clusters PCA-reduced returns.
   - *Distance route* (`distance_approach/basic_distance_approach.py`):
     1. Min–max normalise prices.
     2. SSD, optionally within `industry_dict`.
     3. Take a `selection_pool` (default 50) of the lowest SSD.
     4. Re-sort by `standard`, `variance` or `zero_crossing`.
     5. Take `num_top` (default 5), optionally after `skip_top`.
     6. Trade at `divergence=2` historical SD, close at zero.
2. **Quantopian lecture series** (research_public, archived 2020) **[verified]**:
   1. Form an economic hypothesis and a small universe (solar stocks, with SPY included to expose market-driven false pairs).
   2. Run `coint` on all pairs at p < 0.05, with the explicit multiple-comparisons warning.
   3. Build the spread from an OLS hedge ratio.
   4. Rolling z-score signals.
   5. **Out-of-sample re-test**, which fails in the lecture's own example.
3. **Palomar, *Portfolio Optimization*, ch. 15** **[verified]**:
   1. Normalised price distance as a cheap prescreen.
   2. EG with several residual tests (ADF, PP, PGFF, ERSD, JOT, SPR), checked for agreement — in the EWA–EWC example some reject and some do not, so "caution".
   3. Johansen for more than two legs.
   4. Mean-crossing rate and half-life.
   5. A time-varying (Kalman) hedge or partial cointegration, because cointegration is not persistent.
4. **Ernie Chan** (blog, verified quotes above): use half-life to set the max holding period and lookbacks; time stops rather than price stops for mean reversion ("you could simply be too early"; trailing stops: "I don't recommend it for a mean reverting strategy").
5. **Quant StackExchange:** my searches did not return a specific thread I could verify, so I cite none.

---

## 7. Practitioner tricks and mindset beyond tests

| Practice | Status | Source |
|---|---|---|
| Insist on an economic/structural link | CONSENSUS | §3.4 |
| Trade many pairs, not one; but pairs sharing a leg are *not* diversification | CONSENSUS (top-5/top-20 portfolios in all academic work). The leg-sharing point is shown in our data (§8.5: average PnL correlation 0.92 among the 8 LTC pairs, 1.00 among the XRP pairs) | GGR; Rad et al.; §8 |
| Time stops over price stops | CONSENSUS-ish | Chan 2007; Engelberg et al.; our engine `hold=30` |
| Re-form pairs periodically (monthly, rolling) | CONSENSUS | GGR, Clegg & Krauss, Avellaneda & Lee |
| Open the day after the signal | CONSENSUS | GGR WP, Table 1 Panel B discussion (already the book's `lag=1`) |
| Size by spread volatility / equal risk per pair | FOLKLORE (common, rarely tested in papers) | — |
| Avoid crowded trades; expect sudden simultaneous unwinds | CONSENSUS as a risk; hard to measure | Khandani & Lo (2011), *J. Financial Markets* 14(1):1–46: losses July–Aug 2007 attributed to deleveraging and the withdrawal of market-making capital (abstract per MIT DSpace record; not opened) |
| Expect decay; monitor live vs backtest | CONSENSUS | Do & Faff 2012 ("largely unprofitable after 2002"); Rad et al. (fewer opportunities after 2009); Clegg & Krauss Table 13 (2010–15 ≈ 0) |
| Treat significance as one input; demand a higher bar when you searched widely | CONSENSUS | HLZ 2016; Quantopian; Krauss |
| Check the hedge ratio makes sense (sign, size, not ≈ 0) | Logic + our data; not found stated as a rule in the papers I read | §8.5 |

What fails in live trading, as reported:
- non-convergence (32% of distance pairs; unconverged trades carry the left tail);
- permanent shocks breaking the link (Clegg & Krauss);
- costs and short-selling fees (Do & Faff 2012);
- crowding and deleveraging (Khandani & Lo);
- shrinking opportunity sets (Rad et al.).

---

## 8. Empirical check on our data (formation 2022-11-15 → 2024-11-14; validation 2024-11-15 → 2025-11-14)

### 8.1 Design

- **Data and spread.** 10 coins, 45 pairs, log closes. For each pair, Engle–Granger in both directions; keep the direction with the more negative statistic (a choice that inflates passes, deliberately shown). h is from the formation OLS, and the spread is X = log A − h log B.
- **Formation metrics.** Return correlation, level correlation, EG statistic and p (MacKinnon), half-life (AR(1)), mean crossings per year, spread SD ÷ round-trip cost, Hurst (lagged-difference estimator, lags 2–60), stability of h (first half vs second half), and SSD of normalised prices.
- **Validation rules.** All use `sab2_engine.run` at the book's cost basis (fee 0.05% per fill per leg; round trip = 0.20% of one leg's notional; next-day fill). Capital is 1,000, and the A leg is $500 at the formation-end price.
  - **Fixed ruler** (book default): z from the formation mean and SD; enter at 2, leave at 0.5, hold ≤ 30 days.
  - **Rolling ruler:** the same, but z from a trailing 60-day mean and SD.
  - **GGR distance:** 12-month formation and 6-month trading, two windows walking forward through validation; open at 2 formation-SD of the normalised gap, close at the crossing or at the window end.
- **Persistence.** The formation-h spread is ADF-tested on validation, and EG is re-estimated on validation.

### 8.2 Results table (all 45 pairs, sorted by return correlation)

Column notes:
- "EG p": ✓ = rejects at 5% using the book's EG critical value.
- "SD/RT" = stationary spread SD ÷ 0.20% round-trip cost.
- Net/Gross: fixed-ruler rule, USD on 1,000 capital.
- "GGR(2y)": a distance rule with the whole 2-year formation as the ruler, kept for completeness only. Its SD is so wide that most pairs never trigger; it is superseded by §8.3.
- "val EG": re-estimated EG passes on validation.

| pair | ρ ret | ρ level | EG stat | EG p | h | HL (d) | cross/yr | SD/RT | Hurst | Net | Gross | trades | GGR(2y) net | val EG |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ETH/BTC | 0.82 | 0.95 | -2.17 | 0.44 | 0.65 | 45 | 18.0 | 47 | 0.40 | 205 | 212 | 8 | 0 |  |
| DOT/ADA | 0.81 | 0.87 | -0.69 | 0.95 | 0.77 | 150 | 19.5 | 58 | 0.39 | -130 | -118 | 11 | 289 |  |
| DOT/ETH | 0.73 | 0.50 | -1.78 | 0.64 | 0.37 | 76 | 15.5 | 104 | 0.48 | -195 | -192 | 5 | 0 |  |
| DOT/LINK | 0.72 | 0.58 | -1.81 | 0.62 | 0.34 | 73 | 15.5 | 97 | 0.50 | -153 | -147 | 9 | 264 |  |
| ETH/ADA | 0.72 | 0.70 | -2.08 | 0.49 | 0.82 | 92 | 6.5 | 113 | 0.47 | 185 | 187 | 3 | 0 |  |
| DOT/SOL | 0.72 | 0.35 | -1.83 | 0.62 | 0.09 | 70 | 14.5 | 112 | 0.48 | 374 | 378 | 8 | 0 |  |
| BTC/DOGE | 0.71 | 0.77 | -1.86 | 0.60 | 1.06 | 88 | 12.0 | 147 | 0.42 | 32 | 33 | 1 | 0 |  |
| DOT/BTC | 0.70 | 0.30 | -1.81 | 0.63 | 0.15 | 72 | 17.5 | 114 | 0.49 | 350 | 355 | 8 | 0 |  |
| ADA/BTC | 0.70 | 0.60 | -1.97 | 0.54 | 0.35 | 66 | 15.0 | 108 | 0.47 | 610 | 617 | 7 | 0 |  |
| ADA/LINK | 0.69 | 0.81 | -1.99 | 0.53 | 0.54 | 56 | 17.0 | 79 | 0.47 | 188 | 199 | 10 | 0 |  |
| ETH/LINK | 0.69 | 0.85 | -1.93 | 0.56 | 0.66 | 74 | 3.5 | 84 | 0.51 | 97 | 99 | 3 | 434 |  |
| BTC/SOL | 0.68 | 0.97 | -2.43 | 0.31 | 0.46 | 45 | 15.5 | 56 | 0.41 | -119 | -110 | 11 | 0 |  |
| ADA/DOGE | 0.67 | 0.64 | -1.53 | 0.75 | 0.51 | 94 | 10.0 | 104 | 0.53 | 246 | 247 | 2 | 199 | ✓ |
| DOT/DOGE | 0.67 | 0.45 | -0.66 | 0.95 | 0.32 | 213 | 17.5 | 106 | 0.51 | 107 | 112 | 10 | 378 |  |
| ADA/SOL | 0.67 | 0.66 | -2.05 | 0.50 | 0.18 | 59 | 14.0 | 102 | 0.45 | 69 | 77 | 10 | 0 |  |
| ETH/DOGE | 0.66 | 0.78 | -1.06 | 0.89 | 0.73 | 140 | 17.0 | 100 | 0.48 | 87 | 92 | 7 | 136 |  |
| ETH/SOL | 0.66 | 0.92 | -2.60 | 0.24 | 0.30 | 40 | 13.0 | 61 | 0.42 | 133 | 137 | 7 | 0 |  |
| LINK/BTC | 0.64 | 0.83 | -1.61 | 0.72 | 0.73 | 85 | 16.5 | 113 | 0.47 | 71 | 73 | 2 | 0 |  |
| ETH/BNB | 0.64 | 0.81 | -2.26 | 0.40 | 0.67 | 70 | 7.0 | 93 | 0.46 | 39 | 40 | 2 | 87 |  |
| BTC/BNB | 0.64 | 0.82 | -1.99 | 0.54 | 1.00 | 112 | 14.5 | 131 | 0.45 | 0 | 0 | 0 | 0 |  |
| LTC/ETH | 0.64 | 0.05 | -3.45 | 0.04 ✓ | 0.02 | 23 | 11.5 | 73 | 0.37 | 366 | 372 | 8 | 0 | ✓ |
| LTC/ADA | 0.63 | 0.28 | -3.34 | 0.05 | 0.15 | 25 | 12.5 | 70 | 0.37 | 434 | 439 | 6 | 0 |  |
| LINK/SOL | 0.63 | 0.88 | -2.06 | 0.50 | 0.37 | 54 | 26.5 | 95 | 0.43 | 293 | 297 | 3 | 0 | ✓ |
| XRP/ADA | 0.62 | 0.39 | -2.62 | 0.23 | 0.26 | 35 | 14.5 | 82 | 0.38 | -780 | -759 | 11 | -434 | ✓ |
| LTC/DOT | 0.62 | 0.52 | -3.54 | 0.03 ✓ | 0.32 | 23 | 23.5 | 63 | 0.35 | 74 | 82 | 10 | 231 |  |
| LTC/LINK | 0.61 | -0.10 | -3.63 | 0.02 ✓ | -0.04 | 21 | 14.5 | 73 | 0.37 | 168 | 174 | 8 | 0 | ✓ |
| LTC/BTC | 0.60 | -0.13 | -3.64 | 0.02 ✓ | -0.04 | 21 | 11.5 | 73 | 0.38 | 215 | 221 | 8 | 0 |  |
| DOT/BNB | 0.60 | 0.30 | -1.77 | 0.64 | 0.19 | 73 | 20.5 | 114 | 0.49 | 232 | 236 | 8 | 57 |  |
| ADA/BNB | 0.59 | 0.51 | -1.72 | 0.67 | 0.36 | 80 | 17.5 | 117 | 0.49 | 389 | 397 | 8 | 143 |  |
| LINK/DOGE | 0.57 | 0.68 | -0.56 | 0.96 | 0.82 | 282 | 12.0 | 148 | 0.53 | 505 | 506 | 1 | 347 | ✓ |
| LTC/DOGE | 0.55 | 0.17 | -3.41 | 0.04 ✓ | 0.07 | 24 | 16.0 | 72 | 0.37 | 571 | 575 | 6 | 109 | ✓ |
| SOL/DOGE | 0.55 | 0.79 | -1.28 | 0.84 | 2.28 | 105 | 14.0 | 301 | 0.41 | 301 | 306 | 3 | 0 |  |
| SOL/BNB | 0.55 | 0.83 | -1.65 | 0.70 | 2.13 | 121 | 12.5 | 271 | 0.51 | 197 | 200 | 1 | 0 |  |
| LINK/BNB | 0.55 | 0.60 | -1.52 | 0.75 | 0.64 | 120 | 14.0 | 161 | 0.52 | 0 | 0 | 0 | 0 |  |
| BNB/DOGE | 0.53 | 0.87 | -1.16 | 0.87 | 0.99 | 81 | 21.0 | 93 | 0.36 | 362 | 368 | 5 | -167 |  |
| LTC/SOL | 0.53 | -0.19 | -3.69 | 0.02 ✓ | -0.03 | 20 | 15.5 | 72 | 0.38 | 220 | 226 | 8 | 0 | ✓ |
| LTC/BNB | 0.53 | 0.03 | -3.48 | 0.03 ✓ | 0.01 | 23 | 12.5 | 73 | 0.37 | 369 | 374 | 8 | 0 |  |
| XRP/DOT | 0.52 | 0.15 | -2.46 | 0.30 | 0.11 | 37 | 19.5 | 88 | 0.36 | -744 | -724 | 11 | -429 | ✓ |
| XRP/ETH | 0.51 | 0.56 | -2.86 | 0.15 | 0.32 | 28 | 21.5 | 74 | 0.38 | -728 | -707 | 11 | 182 | ✓ |
| LTC/XRP | 0.50 | -0.07 | -3.63 | 0.02 ✓ | -0.06 | 21 | 14.5 | 73 | 0.37 | 108 | 116 | 9 | -195 | ✓ |
| XRP/BTC | 0.49 | 0.61 | -3.26 | 0.06 | 0.24 | 23 | 18.5 | 71 | 0.35 | -716 | -695 | 11 | 530 | ✓ |
| XRP/DOGE | 0.48 | 0.27 | -2.87 | 0.14 | 0.15 | 31 | 11.5 | 86 | 0.37 | -753 | -733 | 11 | -344 | ✓ |
| XRP/LINK | 0.47 | 0.56 | -2.85 | 0.15 | 0.25 | 28 | 13.5 | 74 | 0.37 | -735 | -714 | 11 | -145 | ✓ |
| XRP/SOL | 0.46 | 0.54 | -3.09 | 0.09 | 0.10 | 25 | 20.5 | 75 | 0.35 | -730 | -710 | 11 | 0 | ✓ |
| XRP/BNB | 0.39 | 0.19 | -2.69 | 0.20 | 0.09 | 33 | 24.5 | 87 | 0.37 | -694 | -674 | 11 | 236 | ✓ |

### 8.3 Group results

Mean validation net, USD per pair on 1,000 capital; "prof." = profitable pairs.

| Group | n | Fixed ruler: mean net (prof.) | Rolling 60-d ruler: mean net (prof.) |
|---|---|---|---|
| All 45 | 45 | +24.8 (31/45) | −162.8 (19/45) |
| EG pass 5% (formation) | 8 | **+261.4 (8/8)** | +42.0 (7/8) |
| Return-corr top 5 (0.72–0.82) | 5 | −17.8 | −79.5 (2/5) |
| **Level-corr top 5 (0.87–0.97)** | 5 | +174.9 | **−206.8 (0/5)** |
| Return-corr bottom 5 (all XRP) | 5 | −725.7 | −766.9 (0/5) |
| Half-life ≤ 30 d | 13 | −29.6 (9/13) | — |
| EG p<0.10 & HL ≤ 30 & ≥12 crossings/yr (the ArbitrageLab-style chain) | 9 | +55.4 (7/9) | — |
| Hurst < 0.5 | 38 | +3.2 (26/38) | — |

**GGR distance method, 12-month formation and 6-month trading:**
- Window 1: top-5 SSD mean net +27.2, versus +37.2 for all 45 pairs. Spearman(SSD, net) −0.07.
- Window 2: top-5 SSD mean net +20.9, versus +20.3 for all 45. Spearman(SSD, net) +0.11.
- Only 28 and 18 round trips across all 45 pairs: crypto trends make the 2-SD trigger rare.
- The five highest-return-correlation pairs averaged +86.9 and +74.4 under GGR.

**Spearman rank correlation, formation metric vs validation net (n = 45):**

| Metric | Fixed ruler | Rolling ruler | GGR (2y ruler) |
|---|---|---|---|
| Return correlation | +0.17 | +0.37 | +0.07 |
| Level correlation | −0.08 | +0.02 | +0.02 |
| EG statistic (more negative = stronger) | +0.12 | +0.24 | +0.21 |
| Half-life | +0.06 | +0.23 | — |
| Crossings | −0.15 | −0.12 | — |
| SD/RT | +0.15 | +0.14 | — |
| Hurst | +0.26 | +0.30 | — |
| h drift | −0.12 | −0.05 | — |

For EG, half-life and Hurst a negative Spearman means the filter helped; for return correlation, crossings and SD/RT a positive one means it helped. Most filters have the "wrong" sign or are near zero. **Return correlation is the only metric that is consistently (weakly) positive.**

### 8.4 Persistence

- Formation EG passes: 8. With the **formation h**, 0 of 8 spreads are stationary in validation (ADF with EG critical values).
- Re-estimating EG on validation, 5 of 8 pass again. But 16 of 45 pairs pass on validation, including all 8 XRP pairs that lost about −700 each. Validation's own "cointegration" therefore says little about validation's profit.
- The return correlation is moderately stable: the correlation between formation ρ and validation ρ across the 45 pairs is 0.58.

### 8.5 What the headline "8/8 profitable" really is

- **Every formation EG pass is an LTC pair, and seven of the eight have h between −0.06 and +0.07.** With h ≈ 0, X ≈ log LTC: the test detected that **LTC alone** was stationary in formation (ADF on log LTC −3.50 vs the 5% critical value −2.87, p ≈ 0.008; no other coin passes; XRP is next at p ≈ 0.09). The "pair" trade is effectively a single-coin mean-reversion bet with a tiny second leg.
- Their daily PnLs have average pairwise correlation **0.92**, so 8 profitable pairs ≈ **one** profitable bet. A placebo of random 8-pair sets gives a median of +29 and a 95th percentile of +226. The LTC group's +261 sits at the 97.8th percentile, which counts as "significant" only if you ignore that the 8 are one bet.
- Likewise, the 8 XRP pairs (excluding LTC/XRP) have PnL correlation **1.00**. One event — XRP +152% in validation — cost about −700 each. Formation XRP was nearly stationary on its own too (p ≈ 0.09), so those small-h "pairs" were also single-coin bets, short XRP into a rally.
- **Under the fixed ruler, 297 of 312 exits were the 30-day time stop.** The spread almost never came back to |z| ≤ 0.5. The fixed-ruler P&L is mostly a bet that formation-period relative levels return, re-entered every 30 days, not trade-by-trade mean reversion. Removing the time stop raises the total from +1,118 to +2,213, which is luck of direction, not evidence for the rule.
- Costs are small next to the gross P&L at daily frequency: total gross +1,464, costs 346, net +1,118 for the fixed ruler. **For our 10 coins the "0.98 correlation, no money" problem does not appear.** The highest return correlation is 0.82, and every spread SD is ≥ 47× the round-trip cost. The binding problem is that spreads drift, not that they are too tight.

### 8.6 Answers to the owner's two examples on our data

- **(a) "Correlation and cointegration both significant → usable?"** Not reliably. The only pairs passing EG were "pairs" with h ≈ 0, i.e. one coin's behaviour, and their return correlations (0.50–0.64) were mid-table. None kept a stationary spread with the formation hedge ratio in validation. Their profit came from one coin and one direction, and it disappears under a rolling ruler (+42 average) or the GGR rule (+18).
- **(b) "Very high correlation → maybe no money."**
  - *Level* correlation as a selector lost money under the rolling ruler (top-5 level-correlation pairs 0/5 profitable) and was mixed under the fixed ruler.
  - *Return* correlation was the least-bad single predictor (Spearman +0.17 to +0.37), but the single highest pair, ETH/BTC at 0.82, made +205 under the fixed ruler and −378 under the rolling ruler.
  - The arithmetic of §2.2 shows that pure "too tight to pay costs" needs ρ ≳ 0.98 combined with a fast half-life and/or retail-level costs. That is a real risk intraday or for near-identical instruments (spot vs perp, two venues), **not** for these daily coin pairs.

**Caveats:** one validation year; 10 coins; 45 overlapping pairs (about 10 independent legs); one cost basis; XRP's rally dominates. These are teaching numbers, not evidence about crypto stat arb in general.

---

## 9. Implications for the book

### 9.1 Where each finding belongs (volume 2 plan, §4)

| Chapter | Finding to add |
|---|---|
| 1 (regression, h) | §8.5: always read h. An h near 0 means "one coin, not a pair". The sign and size must make economic sense. Krauss on 1:1 vs regression h. |
| 2 (log prices) | Level correlation of trending prices is spurious (BTC/SOL 0.97 level correlation, p 0.31); use return correlation or log-spread tests. |
| 3 (ADF/EG) | The persistence evidence (Clegg 2014; Palomar; our 0/8). Multiple testing (Quantopian spectrum; Krauss's 61 false positives in 1,225; HLZ t > 3). "Testing both directions doubles your tests" (our 2 → 8 passes). The EG pass caused by one stationary leg (LTC). |
| 4 (half-life) | Half-life as a *gate* (Avellaneda & Lee < 30 days on 60; Sarmento 1 day–1 year) and to set max holding (Chan: about 3× HL). |
| 5–6 (rolling, Kalman) | The practitioner default is rolling re-estimation and periodic re-formation. Partial cointegration and Kalman as the published answer to non-persistence. Our fixed-vs-rolling ruler flip (+25 vs −163 mean). |
| 7 (entry/exit) | GGR's one-day wait (−30 to −55 bps, Table 1 Panel B); time stops vs price stops (Chan); Engelberg's 10-day result; 297/312 time-stop exits in our data. |
| 8–10 (factors, PCA, baskets) | Avellaneda & Lee as the "residual vs factor" template; Leung & Nguyen's BTC–ETH–BCH–LTC basket; Gabriel & Kunst (Johansen). |
| 11 (allocation) | Pairs sharing a leg are one bet (PnL correlation 0.92 and 1.00). Count *independent legs*, not pairs. |
| 12 (backtest) | Converged vs unconverged trades (Rad et al. 62.5% converged; the left tail comes from unconverged trades). |
| 13 (how many tries) | Do & Faff's 29 algorithm combinations; Deflated Sharpe; our placebo distribution for "8 random pairs". |
| 14 (costs, decay) | Do & Faff "largely unprofitable after 2002"; Rad et al. fewer opportunities after 2009; Clegg & Krauss 2010–15 ≈ 0; Fil & Kristoufek daily −0.07%/month vs 5-min +11.61%; Pindza & Mba negative after 0.08% costs; §2.2 cost arithmetic for very high ρ; Khandani & Lo on crowding. |
| 15 (ML) | Sarmento & Horta pipeline as "ML picks candidates; rules still gate"; Fischer et al. on capacity. |
| 16 (copula) | Rad et al.: copula 5 bps/month after costs but stable opportunity count; Tadi & Witzany; Pindza & Mba. |
| 17 (reading papers) | Add to the seven-question reading frame: "Is the selection one test or a chain? Is there an economic link? Is h sensible? Are the pairs independent?" |

### 9.2 "คนทำงานจริงทำอย่างไร" box ideas (one per chapter)

1. **Ch 1 — "อ่าน h ก่อนเชื่อเส้น"**: an h of 0.02 means you are trading one coin. Our LTC "pairs" table (7 of the 8 have h between −0.06 and +0.07). Practitioners check that the sign and size of h make economic sense.
2. **Ch 2 — "Correlation ของราคาหลอกตา"**: BTC/SOL level correlation 0.97, EG p 0.31. Chan's line: correlated stocks may "never" widen. The Quantopian two counter-examples.
3. **Ch 3 — "ผ่านปีนี้ ไม่ได้แปลว่าผ่านปีหน้า"**: Clegg's ~5% → ~5%; our 0/8 with the formation h. The Quantopian lecture failing its own out-of-sample re-test.
4. **Ch 3 — "ลองกี่ครั้ง นับด้วย"**: test both directions → passes go from 2 to 8; Krauss's 61 false positives from 1,225 pairs; HLZ's t > 3.
5. **Ch 4 — "Half-life คือประตู ไม่ใช่แค่ตัวเลข"**: Avellaneda & Lee keep only reversion times under 30 days; Sarmento keeps 1 day–1 year and ≥12 crossings/yr; Chan's max hold of 3× HL.
6. **Ch 5 — "เขาไม่ตรึงไม้บรรทัดไว้ทั้งปี"**: monthly re-formation (GGR, Clegg & Krauss), daily 60-day refit (A&L); our fixed vs rolling flip.
7. **Ch 7 — "รอหนึ่งวัน และตั้งเวลาออก"**: GGR's −30 to −55 bps from waiting a day; Engelberg's 10-day exit beating 6 months; Chan on why price stops hurt mean reversion.
8. **Ch 11 — "แปดคู่ที่มี LTC เหมือนกัน = หนึ่งเดิมพัน"**: PnL correlation 0.92 / 1.00; count independent legs.
9. **Ch 14 — "ทำไมกำไรหายไป"**: the decay timeline (2002 / 2009 / 2010–15); crypto daily vs 5-minute (Fil & Kristoufek); the §2.2 table answering the owner's "0.98" question with numbers.
10. **Ch 17 — "สายพานคัดคู่ของคนทำงานจริง"**: the ArbitrageLab/Sarmento chain drawn as a funnel: economic group → closeness → EG (as rank/filter) → Hurst/half-life/crossings → out-of-sample → many independent pairs with stops and re-formation. Run it on our 45 pairs: 9 pass, mean +55, 7/9 profitable — better than all pairs (+25), but still dominated by LTC.

### 9.3 Terminology

Terms new to the glossary that these boxes would need (proposed Thai, per CLAUDE.md format): Zero Crossing (การตัดผ่านค่าเฉลี่ย), Hurst Exponent (เลขชี้กำลังเฮิร์สต์), Partial Cointegration (โคอินทิเกรชันบางส่วน), Distance Method (วิธีระยะห่าง), Family-wise Error Rate (อัตราผิดพลาดรวมทั้งชุดการทดสอบ), Non-convergence (การไม่กลับมาบรรจบ), Time Stop (เส้นออกตามเวลา). These are **not** added to CLAUDE.md (out of scope for this memo); the chapter editors should add them when they use them.

---

## 10. Source list

Primary or verified as described:

1. Gatev, E., Goetzmann, W., Rouwenhorst, K.G. (2006). Pairs Trading: Performance of a Relative-Value Arbitrage Rule. *RFS* 19(3):797–827. WP version read: Yale ICF WP 08-03 (Feb 2006).
2. Do, B., Faff, R. (2010). Does Simple Pairs Trading Still Work? *FAJ* 66(4):83–95. doi 10.2469/faj.v66.n4.1 (abstract; details via Krauss).
3. Do, B., Faff, R. (2012). Are Pairs Trading Profits Robust to Trading Costs? *J. Financial Research* 35(2):261–287. doi 10.1111/j.1475-6803.2012.01317.x (abstract).
4. Rad, H., Low, R.K.Y., Faff, R. (2016). The profitability of pairs trading strategies: distance, cointegration and copula methods. *Quantitative Finance* 16(10):1541–1558 (author PDF read).
5. Krauss, C. (2017). Statistical arbitrage pairs trading strategies: Review and outlook. *J. Economic Surveys* 31(2):513–545. WP read: FAU Discussion Paper 09/2015 (EconStor).
6. Clegg, M., Krauss, C. (2018). Pairs trading with partial cointegration. *Quantitative Finance* 18(1):121–138. WP read: FAU 05/2016 (EconStor).
7. Clegg, M. (2014). On the persistence of cointegration in pairs trading. SSRN WP (figures via CXO Advisory summary only).
8. Huck, N., Afawubo, K. (2015). Pairs trading and selection methods: is cointegration superior? *Applied Economics* 47(6):599–613 (abstract).
9. Chen, H., Chen, S., Chen, Z., Li, F. (2019). Empirical Investigation of an Equity Pairs Trading Strategy. *Management Science* 65(1):370–389 (abstract).
10. Farago, A., Hjalmarsson, E. (2019). Stock Price Co-Movement and the Foundations of Pairs Trading. *JFQA* 54(2):629–665 (abstract).
11. Avellaneda, M., Lee, J.-H. (2010). Statistical arbitrage in the US equities market. *Quantitative Finance* 10(7):761–782 (NYU preprint, June 2009, read).
12. Sarmento, S.M., Horta, N. (2020). Enhancing a Pairs Trading strategy with the application of Machine Learning. *Expert Systems with Applications* 158:113490. Thesis read: IST Lisbon MSc, Sep 2019, §3.5.
13. Bui, Q., Ślepaczuk, R. (2022). Applying Hurst Exponent in pair trading strategies on Nasdaq 100 index. *Physica A* 592:126784 (abstract).
14. Fil, M., Kristoufek, L. (2020). Pairs Trading in Cryptocurrency Markets. *IEEE Access* 8:172644–172651 (abstract).
15. Leung, T., Nguyen, H. (2019). Constructing cointegrated cryptocurrency portfolios for statistical arbitrage. *Studies in Economics and Finance* 36(4):581–599 (abstract).
16. Tadi, M., Witzany, J. (2025). Copula-based trading of cointegrated cryptocurrency pairs. *Financial Innovation* 11 (abstract).
17. Pindza, E., Mba, J.C. (2026). Adaptive copula-based pairs trading with market overlay. *Quantitative Finance and Economics* 10(2):378–404 (abstract).
18. Fischer, T.G., Krauss, C., Deinert, A. (2019). Statistical Arbitrage in Cryptocurrency Markets. *JRFM* 12(1):31 (abstract).
19. Grande, M., Borondo, F., Losada, J.C., Borondo, J. (2024). Anti-Persistent Values of the Hurst Exponent Anticipate Mean Reversion in Pairs Trading: The Cryptocurrencies Market as a Case Study. *Mathematics* 12(18):2911 (abstract).
20. Gabriel, S., Kunst, R.M. (2024). Cointegrated portfolios and volatility modeling in the cryptocurrency market. IHS Working Paper 52 (abstract page).
21. Saji, T.G. (2021). Pairs trading in cryptocurrency market: A long-short story. *IMFI* 18(3):127–141 (abstract).
22. Harvey, C.R., Liu, Y., Zhu, C. (2016). …and the Cross-Section of Expected Returns. *RFS* 29(1):5–68 (abstract).
23. Bailey, D.H., López de Prado, M. (2014). The Deflated Sharpe Ratio. *JPM* 40(5):94–107 (abstract).
24. Khandani, A., Lo, A. (2011). What happened to the quants in August 2007? *J. Financial Markets* 14(1):1–46 (abstract per MIT DSpace, via search).
25. Engelberg, J., Gao, P., Jagannathan, R. (2009). An Anatomy of Pairs Trading. SSRN 1330689 (abstract via search snippets only).
26. Palomar, D.P. *Portfolio Optimization* (online book), §15.4, portfoliooptimizationbook.com (read).
27. Mackenzie, D., Margenot, M. Introduction to Pairs Trading. Quantopian Lecture Series, github.com/quantopian/research_public (notebook read).
28. Hudson & Thames. ArbitrageLab, github.com/hudson-and-thames/arbitragelab, commit 32ccd56 (source read).
29. Chan, E.P. Blog posts "Cointegration is not the same as correlation" (6 Nov 2006) and "What is your stop loss strategy?" (15 Jan 2007), epchan.blogspot.com (read). *Algorithmic Trading* (Wiley 2013): not opened; quotes marked unverified.
30. Vidyamurthy, G. (2004). *Pairs Trading: Quantitative Methods and Analysis*. Wiley: not opened; cited via Krauss.

Not found or not verified: a specific Quant StackExchange thread (none retrieved); Clegg (2014) full text; Fil & Kristoufek and Tadi & Witzany full texts (methodological details beyond the abstracts not checked).
