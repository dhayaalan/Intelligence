# GLOBAL NEWS SOURCE COVERAGE & REGIONAL DIRECTORY

## 1. Global Coverage Distribution

The dynamic country registry indexes **249+ countries and territories** recognized under ISO 3166-1. Coverage is categorized into:
- **Verified Active Coverage (`WORKING_TESTED_REAL`)**: Countries with pre-indexed verified publishers, public broadcasters, official government gazettes, and tested regional RSS editions.
- **Configurable Coverage (`NO_SOURCES_CONFIGURED` / `UNVERIFIED_COVERAGE`)**: Selectable territories where custom RSS feeds, publisher domains, or API endpoints can be dynamically registered via `POST /api/v1/news/sources` without altering source code.

### Regional Breakdown

| Continent / Region | Total Territories Indexed | Verified Active Countries | Primary News Providers & Editions | Official / Primary Gazettes |
|---|---|---|---|---|
| **Americas** | 53 | 10+ (US, CA, MX, BR, AR, CO, CL, PE, VE, CU, ...) | Google News (US, CA, MX, BR, AR, CO, CL, PE, VE, CU), Bing News, GDELT 2.0 | whitehouse.gov, state.gov, sec.gov, canada.ca, gob.mx, gov.br |
| **Europe** | 52 | 21+ (GB, FR, DE, IT, ES, NL, CH, SE, NO, PL, UA, RU, ...) | Google News (GB, FR, DE, IT, ES, NL, CH, SE, NO, PL, UA, RU), Bing News Europe | gov.uk, elysee.fr, bundesregierung.de, governo.it, kremlin.ru, gov.ua |
| **Asia** | 51 | 19+ (IN, CN, JP, KR, SG, ID, MY, PK, BD, SA, AE, IL, TR, ...) | Google News (IN, JP, KR, SG, ID, MY, PK, BD, SA, AE, IL, TR), GDELT Doc 2.0 | pib.gov.in, gov.cn, kantei.go.jp, moha.gov.sg, spa.gov.sa |
| **Africa** | 58 | 8+ (ZA, NG, EG, KE, GH, MA, ET, ...) | Google News (ZA, NG, EG, KE, GH, MA), AllAfrica Feed, GDELT 2.0 | gov.za, statehouse.gov.ng, presidency.gov.eg, president.go.ke |
| **Oceania** | 29 | 2+ (AU, NZ, FJ, PG, ...) | Google News (AU, NZ), Pacific Wire RSS Editions | pm.gov.au, beehive.govt.nz |
| **Polar / Special** | 6 | 0 (Uninhabited/Scientific bases) | External global scientific feeds | bas.ac.uk, antarctica.gov.au |

---

## 2. Verified Major Publishers & National Broadcasters

### Americas
- **United States (`US`)**: The New York Times, The Washington Post, Wall Street Journal, CNN, Associated Press, Bloomberg, Fox News, NPR, Reuters US.
- **Canada (`CA`)**: CBC / Radio-Canada, The Globe and Mail, Toronto Star, National Post.
- **Mexico (`MX`)**: El Universal, Reforma, La Jornada, Milenio.
- **Brazil (`BR`)**: Folha de S.Paulo, O Globo, G1, O Estado de S. Paulo.
- **Argentina (`AR`)**: Clarín, La Nación, Página/12, Infobae.
- **Colombia (`CO`)**: El Tiempo, El Espectador, Semana.
- **Chile (`CL`)**: El Mercurio, La Tercera, Emol.

### Europe
- **United Kingdom (`GB`)**: BBC News, The Guardian, The Telegraph, Financial Times, The Times, Reuters UK, Sky News.
- **France (`FR`)**: Le Monde, Le Figaro, Libération, France 24, Agence France-Presse (AFP), Les Echos.
- **Germany (`DE`)**: Der Spiegel, Frankfurter Allgemeine Zeitung (FAZ), Süddeutsche Zeitung, Die Welt, Deutsche Welle (DW), Tagesschau.
- **Italy (`IT`)**: Corriere della Sera, La Repubblica, La Stampa, ANSA.
- **Spain (`ES`)**: El País, El Mundo, ABC, La Vanguardia, EFE.
- **Netherlands (`NL`)**: NOS, De Telegraaf, NRC Handelsblad, De Volkskrant.
- **Switzerland (`CH`)**: Neue Zürcher Zeitung (NZZ), Le Temps, Swissinfo.
- **Sweden (`SE`)**: Dagens Nyheter, Svenska Dagbladet, SVT Nyheter.
- **Ukraine (`UA`)**: Kyiv Post, The Kyiv Independent, Ukrinform, Ukrainska Pravda.

### Asia & Middle East
- **India (`IN`)**: The Hindu, Indian Express, Hindustan Times, NDTV, Times of India, Livemint, The Hindu BusinessLine, ANI News.
- **Japan (`JP`)**: Asahi Shimbun, The Mainichi, Yomiuri Shimbun, Nikkei, NHK World, The Japan Times.
- **China (`CN`)**: Xinhua News Agency, People's Daily, Global Times, Caixin, South China Morning Post.
- **South Korea (`KR`)**: Yonhap News Agency, The Korea Herald, The Chosun Ilbo, JoongAng Daily.
- **Singapore (`SG`)**: The Straits Times, Channel NewsAsia (CNA), The Business Times.
- **Saudi Arabia (`SA`)**: Arab News, Asharq Al-Awsat, Saudi Gazette, SPA.
- **United Arab Emirates (`AE`)**: The National, Gulf News, Khaleej Times, WAM.
- **Israel (`IL`)**: Haaretz, The Jerusalem Post, Times of Israel, Ynetnews.
- **Turkey (`TR`)**: Anadolu Agency, Daily Sabah, Hürriyet Daily News, Turkish Minute.

### Africa
- **South Africa (`ZA`)**: News24, Mail & Guardian, Daily Maverick, Sunday Times.
- **Nigeria (`NG`)**: Premium Times, The Punch, Vanguard, ThisDay, The Guardian Nigeria.
- **Kenya (`KE`)**: Daily Nation, The Standard, The Star, Capital FM Kenya.
- **Egypt (`EG`)**: Al-Ahram, Egypt Independent, Daily News Egypt, MENA.

---

## 3. Dynamic Source Ingestion Workflow

To register a newly discovered publisher or local provincial feed:

```bash
curl -X POST "http://localhost:8000/api/v1/news/sources" \
  -H "Authorization: Bearer <ANALYST_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "publisher_name": "Pacific Islands News Association",
    "canonical_domain": "pina.com.fj",
    "country_code": "FJ",
    "original_language": "en",
    "feed_or_endpoint": "https://pina.com.fj/feed/",
    "source_category": "COMMERCIAL",
    "is_verified": true
  }'
```

### Verification Pipeline:
1. Validates ISO-3166 alpha-2 or alpha-3 code against `GlobalCountryRegistry`.
2. Inspects canonical domain and ensures no duplication.
3. Automatically maps country TLDs and canonical publisher name aliases.
4. Updates country status to `WORKING_TESTED_REAL` and updates coverage metrics.

---

## 4. Transparent Coverage Limitations & Integrity Rules

1. **No Artificial Population**: If an obscure territory has 0 matching articles for a search, the system displays `article_count=0` and lists `NO_MATCHING_ARTICLES` or `NO_SOURCES_CONFIGURED`.
2. **Independence Distinction**: Articles published across different websites that share identical wire origins (e.g., syndicated Reuters or AP copycats) are flagged as `SYNDICATED_COPY` with their origin disclosed.
3. **No Inference from IP**: Retrieval through VPN tunnels (e.g. exit nodes in Europe or Asia) labels `collection_route="VPN-<REG>"` and never overwrites `publisher_country`.
