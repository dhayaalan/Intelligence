# Regional News Intelligence Architecture

## 1. Overview
The Regional News Intelligence engine enables source-aware collection, transliteration, and comparative framing analysis across distinct geographic zones (South India, North India, Pakistan, Bangladesh, United States, United Kingdom, and International Wires).

---

## 2. Dynamic Evidence Derivation
All comparative conclusions are strictly derived from live collected records:
1. **Dynamic Convergence**: Identifies shared factual entities and common vocabulary across regional dispatches rather than emitting static strings.
2. **Divergence Analysis**: Extracts vocabulary emphasized uniquely in specific geographic regions to highlight policy, security, or cultural framing differences.
3. **Cross-Regional Media Reuse**: Inspects canonical media references and perceptual image hashes across distinct regional dispatches to detect recycled archival imagery or contextual displacement.
4. **Honest Sample Size**: An empty search in a geography reports `sample_size = 0` without synthesizing false events or asserting that the event did not happen.

---

## 3. Multilingual Transliteration Vectors
Queries are expanded using vetted regional terminology vectors across regional scripts:
- **Hindi / Devanagari**: e.g., भारतीय वायु सेना, चुनाव, बाढ़
- **Tamil**: e.g., விமானப்படை, தேர்தல், வெள்ளம்
- **Urdu**: e.g., فضائیہ, انتخابات, سیلاب
- **Bengali**: e.g., ভারতীয় বিমানবাহিনী, নির্বাচন, বন্যা
