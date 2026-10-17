import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import phonenumbers
from phonenumbers import NumberParseException

class SearchMode(str, Enum):
    EXACT_IDENTIFIER = "EXACT_IDENTIFIER"
    TEXT_SEARCH = "TEXT_SEARCH"
    FUZZY_SEARCH = "FUZZY_SEARCH"
    SEMANTIC_SEARCH = "SEMANTIC_SEARCH"

class IdentifierType(str, Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    VEHICLE_PLATE = "VEHICLE_PLATE"
    NOT_AN_IDENTIFIER = "NOT_AN_IDENTIFIER"

# RFC 5322 compliant email regex
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)

# Common phone number character pattern to detect potential phone queries
PHONE_CANDIDATE_REGEX = re.compile(r"^\+?[0-9\s\-()./]{7,25}$")

class NormalizedEmail(BaseModel):
    raw_email: str
    canonical_email: str
    domain: str
    local_part: str
    is_valid: bool = True
    validation_error: Optional[str] = None

class NormalizedPhone(BaseModel):
    raw_phone: str
    e164: str
    country_code: int
    national_number: int
    region_code: Optional[str] = None
    is_valid: bool = True
    validation_error: Optional[str] = None

def normalize_email(email_str: str) -> Tuple[Optional[NormalizedEmail], Optional[str]]:
    """
    Deterministically validates and normalizes an email address.
    
    Policy:
    - Trims leading and trailing whitespace.
    - Validates email syntax against RFC standards.
    - Preserves the original raw email as observed in the source.
    - Lowercases the domain part (domain is case-insensitive per RFC).
    - Preserves local-part casing and avoids unsafe provider-specific transforms
      (e.g., does NOT remove dots or plus-addressing suffixes).
    - Canonical email is formed as local_part@lowercase_domain.
    
    Returns (NormalizedEmail, None) on success or (None, error_message) on failure.
    """
    if not email_str:
        return None, "Empty email address provided"
    
    trimmed = email_str.strip()
    if not trimmed:
        return None, "Email address contains only whitespace"
    
    if not EMAIL_REGEX.match(trimmed):
        return None, f"Invalid email format: '{trimmed}' does not satisfy RFC syntax requirements"
    
    parts = trimmed.split("@")
    if len(parts) != 2:
        return None, "Email address must contain exactly one '@' separator"
    
    local_part, domain = parts[0], parts[1].lower()
    canonical_email = f"{local_part}@{domain}"
    
    return NormalizedEmail(
        raw_email=trimmed,
        canonical_email=canonical_email,
        domain=domain,
        local_part=local_part,
        is_valid=True
    ), None

def normalize_phone(
    phone_str: str,
    default_region: Optional[str] = "US"
) -> Tuple[Optional[NormalizedPhone], Optional[str]]:
    """
    Deterministically validates and normalizes a phone number into canonical E.164.
    
    Policy:
    - Uses Google's phonenumbers library.
    - Rejects input containing alphabetic letters or non-phone symbols.
    - Parses international country codes if prefixed with '+' or country exit codes.
    - Uses configured default_region only when international prefix is absent.
    - Rejects ambiguous numbers or numbers failing ITU-T E.164 validity check.
    - Preserves original raw representation.
    - Strictly avoids substring or digit-overlap matching.
    
    Returns (NormalizedPhone, None) on success or (None, error_message) on failure.
    """
    if not phone_str:
        return None, "Empty phone number provided"
    
    trimmed = phone_str.strip()
    # Reject strings with alphabetic letters immediately
    if any(c.isalpha() for c in trimmed):
        return None, "Phone number contains alphabetic characters and cannot be parsed as a phone identifier"
    
    # Must contain at least 7 digits
    digits_only = re.sub(r"\D", "", trimmed)
    if len(digits_only) < 7:
        return None, f"Phone number '{trimmed}' has insufficient digits (minimum 7 required for valid telecommunications identifier)"
    
    try:
        # If starts with +, parse with None region to force international code resolution
        if trimmed.startswith("+"):
            parsed = phonenumbers.parse(trimmed, None)
            if phonenumbers.is_valid_number(parsed):
                e164_format = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                region_code = phonenumbers.region_code_for_number(parsed)
                return NormalizedPhone(
                    raw_phone=trimmed,
                    e164=e164_format,
                    country_code=parsed.country_code,
                    national_number=parsed.national_number,
                    region_code=region_code,
                    is_valid=True
                ), None
            else:
                if phonenumbers.is_possible_number(parsed):
                    return None, f"Phone number '{trimmed}' has valid length but is not assigned to a valid telecommunications range"
                return None, f"Invalid phone number: '{trimmed}' is not a valid international phone number"

        # If no '+' prefix, try primary default_region first, then common candidate plans (IN, GB, US, CA, AU)
        candidate_regions = [default_region] if default_region else []
        for r in ["IN", "GB", "US", "CA", "AU"]:
            if r not in candidate_regions:
                candidate_regions.append(r)

        valid_parsed = None
        last_err = None

        for region in candidate_regions:
            try:
                parsed = phonenumbers.parse(trimmed, region)
                if phonenumbers.is_valid_number(parsed):
                    valid_parsed = parsed
                    break
                elif phonenumbers.is_possible_number(parsed):
                    last_err = f"Phone number '{trimmed}' has valid length but is not assigned to a valid telecommunications range"
            except Exception:
                continue

        if valid_parsed and phonenumbers.is_valid_number(valid_parsed):
            e164_format = phonenumbers.format_number(valid_parsed, phonenumbers.PhoneNumberFormat.E164)
            region_code = phonenumbers.region_code_for_number(valid_parsed)
            return NormalizedPhone(
                raw_phone=trimmed,
                e164=e164_format,
                country_code=valid_parsed.country_code,
                national_number=valid_parsed.national_number,
                region_code=region_code,
                is_valid=True
            ), None

        return None, last_err or f"Invalid phone number: '{trimmed}' is not assigned to a valid telecommunications range"
        
    except NumberParseException as e:
        return None, f"Phone number parsing error: {e._msg}"
    except Exception as e:
        return None, f"Unexpected error parsing phone number: {str(e)}"

def classify_query_intent_and_mode(
    query: str,
    requested_mode: Optional[str] = None,
    default_phone_region: Optional[str] = "US"
) -> Dict[str, Any]:
    """
    Deterministic backend query-intent and search-mode classifier.
    
    Strict invariant:
    - If query is an email or phone identifier, search mode is forced to EXACT_IDENTIFIER.
    - No automatic fallback to semantic, fuzzy, or broad text search.
    - User can explicitly request FUZZY_SEARCH or SEMANTIC_SEARCH for general text queries,
      but for identifiers, EXACT_IDENTIFIER is strictly maintained.
    """
    q = (query or "").strip()
    q_lower = q.lower()

    # Check explicit email prefix or direct email syntax
    is_explicit_email = q_lower.startswith("email:") or q_lower.startswith("mailto:")
    clean_email = q.split(":", 1)[1].strip() if is_explicit_email else q
    if (is_explicit_email or ("@" in clean_email and not clean_email.startswith("@"))) and not any(c in clean_email for c in [" ", "\t", "\n"]):
        norm_email, err = normalize_email(clean_email)
        if norm_email:
            return {
                "search_mode": SearchMode.EXACT_IDENTIFIER.value,
                "active_search_mode_label": "Exact email search",
                "identifier_type": IdentifierType.EMAIL.value,
                "is_identifier": True,
                "normalized_value": norm_email.canonical_email,
                "raw_query": q,
                "details": norm_email.dict(),
                "validation_error": None
            }
        else:
            return {
                "search_mode": SearchMode.EXACT_IDENTIFIER.value,
                "active_search_mode_label": "Exact email search (Invalid syntax)",
                "identifier_type": IdentifierType.EMAIL.value,
                "is_identifier": True,
                "normalized_value": None,
                "raw_query": q,
                "details": None,
                "validation_error": err
            }
    
    # Check explicit phone prefix or direct phone syntax
    is_explicit_phone = q_lower.startswith("phone:") or q_lower.startswith("tel:")
    clean_phone = q.split(":", 1)[1].strip() if is_explicit_phone else q
    if is_explicit_phone or (PHONE_CANDIDATE_REGEX.match(clean_phone) and any(c.isdigit() for c in clean_phone) and not any(c.isalpha() for c in clean_phone)):
        norm_phone, err = normalize_phone(clean_phone, default_region=default_phone_region)
        if norm_phone:
            return {
                "search_mode": SearchMode.EXACT_IDENTIFIER.value,
                "active_search_mode_label": "Exact phone search",
                "identifier_type": IdentifierType.PHONE.value,
                "is_identifier": True,
                "normalized_value": norm_phone.e164,
                "raw_query": q,
                "details": norm_phone.dict(),
                "validation_error": None
            }
        else:
            return {
                "search_mode": SearchMode.EXACT_IDENTIFIER.value,
                "active_search_mode_label": "Exact phone search (Invalid format)",
                "identifier_type": IdentifierType.PHONE.value,
                "is_identifier": True,
                "normalized_value": None,
                "raw_query": q,
                "details": None,
                "validation_error": err
            }
    
    # Check if query is a vehicle plate registration (e.g. "plate:BD51SMR" or matching plate syntax with digits and letters)
    is_explicit_plate = q.lower().startswith("plate:") or q.lower().startswith("registration:")
    clean_plate_candidate = q.split(":", 1)[1].strip() if is_explicit_plate else q
    if is_explicit_plate or (len(clean_plate_candidate) >= 5 and len(clean_plate_candidate) <= 12 and any(c.isdigit() for c in clean_plate_candidate) and any(c.isalpha() for c in clean_plate_candidate) and not any(c in clean_plate_candidate for c in ["@", ".", "/", "\\"])):
        from app.modules.osint.providers.vehicle_intelligence import vehicle_registration_provider
        matched_fmt = vehicle_registration_provider.match_plate_format(clean_plate_candidate)
        if matched_fmt or is_explicit_plate:
            return {
                "search_mode": SearchMode.EXACT_IDENTIFIER.value,
                "active_search_mode_label": f"Exact vehicle plate search ({matched_fmt.jurisdiction if matched_fmt else 'Standard'})",
                "identifier_type": IdentifierType.VEHICLE_PLATE.value,
                "is_identifier": True,
                "normalized_value": clean_plate_candidate.upper(),
                "raw_query": q,
                "details": {
                    "plate_number": clean_plate_candidate.upper(),
                    "jurisdiction": matched_fmt.jurisdiction if matched_fmt else "UNKNOWN",
                    "description": matched_fmt.description if matched_fmt else "Vehicle plate registration"
                },
                "validation_error": None
            }

    # General non-identifier queries
    req_upper = (requested_mode or "").upper()
    is_natural_question = any(q.lower().startswith(w) for w in ["what ", "who ", "why ", "how ", "where ", "which "]) or q.endswith("?")
    if req_upper in [SearchMode.FUZZY_SEARCH.value, "FUZZY"]:
        active_mode = SearchMode.FUZZY_SEARCH.value
        label = "Fuzzy text search"
    elif req_upper in [SearchMode.SEMANTIC_SEARCH.value, "SEMANTIC"] or is_natural_question:
        active_mode = SearchMode.SEMANTIC_SEARCH.value
        label = "Semantic text search"
    else:
        active_mode = SearchMode.TEXT_SEARCH.value
        label = "Text search"
        
    return {
        "search_mode": active_mode,
        "active_search_mode_label": label,
        "identifier_type": IdentifierType.NOT_AN_IDENTIFIER.value,
        "is_identifier": False,
        "normalized_value": q,
        "raw_query": q,
        "details": None,
        "validation_error": None
    }

def verify_identifier_match(
    queried_canonical: str,
    identifier_type: str,
    record_type: str,
    record_value: str,
    metadata: Optional[Dict[str, Any]] = None,
    sources: Optional[List[str]] = None
) -> bool:
    """
    Server-side verification confirming that a candidate record actually equals
    the queried identifier in the relevant source-backed field.
    
    Rules:
    - For EMAIL: record_type must be 'email' (or have email in metadata) and its normalized
      email must strictly equal queried_canonical. A mere occurrence in body text is REJECTED.
    - For PHONE: record_type must be 'phone' and its canonical E.164 must strictly equal
      queried_canonical. Digit-overlap, substring match, or body mention is REJECTED.
    - Sources consisting only of 'search_query' are rejected as unverified user input.
    """
    # Auto-detect if caller passed identifier_type first
    if str(queried_canonical).upper() in ["EMAIL", "PHONE", "EXACT_EMAIL", "EXACT_PHONE"]:
        queried_canonical, identifier_type = identifier_type, queried_canonical

    if not queried_canonical or not record_value:
        return False

    if sources and set(sources) == {"search_query"}:
        return False
        
    meta = metadata or {}
    r_type = (record_type or "").lower()
    
    if identifier_type == IdentifierType.EMAIL.value:
        # Check direct value
        norm_rec, _ = normalize_email(record_value)
        if norm_rec and norm_rec.canonical_email.lower() == queried_canonical.lower():
            return True
        # Check metadata contact fields
        contact_email = meta.get("email") or meta.get("contact_email")
        if contact_email:
            norm_c, _ = normalize_email(str(contact_email))
            if norm_c and norm_c.canonical_email.lower() == queried_canonical.lower():
                return True
        return False
        
    elif identifier_type == IdentifierType.PHONE.value:
        # Check direct value
        norm_p, _ = normalize_phone(record_value)
        if norm_p and norm_p.e164 == queried_canonical:
            return True
        # Check metadata contact fields
        contact_phone = meta.get("phone") or meta.get("phone_number") or meta.get("contact_phone")
        if contact_phone:
            norm_cp, _ = normalize_phone(str(contact_phone))
            if norm_cp and norm_cp.e164 == queried_canonical:
                return True
        return False

    elif identifier_type in [IdentifierType.VEHICLE_PLATE.value, "VEHICLE_PLATE", "VEHICLE"]:
        clean_target = re.sub(r"[\s\-_:]", "", queried_canonical.strip().upper())
        clean_rec = re.sub(r"[\s\-_:]", "", record_value.strip().upper())
        if clean_target == clean_rec or clean_target in clean_rec or clean_rec in clean_target:
            return True
        plate_in_meta = meta.get("plate_number") or meta.get("plate")
        if plate_in_meta:
            clean_meta = re.sub(r"[\s\-_:]", "", str(plate_in_meta).strip().upper())
            if clean_target == clean_meta:
                return True
        return False

    return False
