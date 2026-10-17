# News Media Integrity & Forensic Extraction Architecture

## 1. Problem Statement & Root Cause Analysis

Investigators reported that news intelligence results frequently displayed misleading or mismatched imagery:
- Article A displayed stock imagery completely unrelated to its geopolitical content.
- Articles without photos displayed generic Unsplash photos that could easily be mistaken for verified on-the-ground intelligence assets.
- Cross-article media leakage occurred during dossier compilation and relationship expansions.

### Root Cause in Legacy Code

In `backend/app/modules/news_intelligence/search_engine.py`:
```python
# Legacy defective code:
hero_img = item.get("hero_image") or self._pick_default_hero_image(req.query, idx)
```
The method `_pick_default_hero_image` maintained lists of generic Unsplash photographs for categories like `GEOPOLITICAL`, `CYBER_THREAT`, `FINANCIAL`, and `ELECTION`. It assigned an image based on `images[idx % len(images)]`.

Consequently:
1. Every article was arbitrarily assigned a stock photo even when no real media existed.
2. Sorting, filtering, or reordering search results changed the `idx` modulo value, causing the exact same article to display different pictures depending on page position!
3. In `dossier_compiler.py`, synthetic SHA-256 EXIF checksums were generated from article titles rather than authentic image bytes, giving analysts a false sense of forensic media verification.

---

## 2. Corrected Media Integrity Architecture

### 1. Authentic Publisher Extraction Only
- Media assets are extracted strictly from verified publisher metadata:
  - OpenGraph image tags (`<meta property="og:image" content="...">`).
  - Twitter/X Card image tags (`<meta name="twitter:image" content="...">`).
  - Valid RSS media enclosures (`<enclosure url="..." type="image/jpeg">` or `<media:content>`).
- If none of these metadata fields are present, `hero_image` and `thumbnail_url` are explicitly set to `None`.

### 2. Neutral Placeholder Guarantee
- When `hero_image` is `None`, the application renders a clean, neutral typography-based SVG placeholder.
- **Epistemic Principle**: *An unillustrated article is infinitely superior to an article with a misleading or fabricated photograph.*
- The dossier compiler sets:
  ```python
  hero_image=hero_image if hero_image else None,
  hero_image_caption=(f"Publisher-associated imagery for '{title}' by {publisher}." if hero_image else None),
  hero_image_forensic_note=("Image extracted from verified publisher OpenGraph metadata." if hero_image else "No verified publisher imagery associated with this article. Placeholder state rendered to prevent false attribution.")
  ```

### 3. Stable Article ID & Canonical URL Binding
- Each news article retains a stable canonical URL and SHA-256 hash ID (`art_<hash>`).
- Reordering, filtering, pagination, and relationship graph expansion preserve the exact image URL reference without positional drift.
- Article B never adopts Article A's image unless both articles genuinely cite the exact same upstream media asset URL.

---

## 3. Regression Test Verification

The test suite in `backend/tests/test_news_media_integrity.py` validates:
1. `test_article_without_verified_media_has_none_image`: Confirms `hero_image=None` when no verified media exists.
2. `test_article_with_verified_opengraph_preserves_its_own_image`: Confirms verified OpenGraph URLs are faithfully retained.
3. `test_article_b_never_inherits_article_a_image`: Confirms isolation between articles in the same batch.
4. `test_dossier_compiler_preserves_verified_media_or_renders_placeholder`: Confirms authentic forensic notes and removal of fabricated EXIF claims.
