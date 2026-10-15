# V3 Specification Checklist

Use this checklist before generating a new project specification.

- [ ] project ID is stable lowercase snake case
- [ ] project version is a new `vNN` value
- [ ] intent is explicitly `original` or `replacement`
- [ ] supported generator ID and exact version are selected
- [ ] input units are explicit (`mm` or `inch`)
- [ ] every required parameter has a real value and source
- [ ] impossible dimensions and minimum walls have been considered
- [ ] printer profile, material, nozzle, and fit profile are selected
- [ ] calibration values are labeled `unverified_starter` or have proven evidence
- [ ] all replacement protected interfaces have authoritative Measurement Contract entries
- [ ] measurement tolerance, source, confidence, and notes are recorded
- [ ] unresolved assumptions and conflicts are visible
- [ ] fit coupon is selected when only clearance remains uncertain
- [ ] generated artifact list is empty for a new draft spec
- [ ] physical verification is `not_confirmed` for an unprinted version
- [ ] workspace target does not already exist

Do not generate a full replacement part when a required nominal protected
interface is missing. A coupon can test clearance; it cannot invent the mating
dimension.
