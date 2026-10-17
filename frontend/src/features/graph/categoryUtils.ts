/**
 * Canonical Entity Category Normalization & Avatar Extraction Utilities.
 * Enforces strict typing across the entire investigation graph studio.
 * Unknown types map strictly to 'UNKNOWN' - NEVER silently to 'DOMAIN'.
 */

export const getEntityCategory = (type: string = ''): string => {
  if (!type) return 'UNKNOWN';
  let t = String(type).trim().toUpperCase();
  if (t.includes('.')) {
    t = t.split('.').pop() || t;
  }

  // PHONE / TELECOM
  if (['PHONE', 'TELEPHONE', 'MSISDN', 'CELL', 'MOBILE', 'PHONE_NUMBER', 'TEL'].includes(t)) {
    return 'PHONE';
  }

  // EMAIL
  if (['EMAIL', 'MAILBOX', 'EMAIL_ADDRESS'].includes(t)) {
    return 'EMAIL';
  }

  // PERSON / NAME / USERNAME / ACCOUNT
  if (['PERSON', 'NAME', 'USERNAME', 'ACCOUNT', 'THREAT_ACTOR', 'AUTHOR', 'ACTOR', 'PROFILE', 'USER', 'INDIVIDUAL'].includes(t)) {
    return 'PERSON';
  }

  // ORGANIZATION / REGISTRY
  if (['ORGANIZATION', 'ORG', 'COMPANY', 'GROUP', 'NGO', 'FOUNDATION', 'TERROR_GROUP', 'GOVERNMENT', 'AUTHORITY', 'REGISTRY', 'ENTERPRISE'].includes(t)) {
    return 'ORGANIZATION';
  }

  // VEHICLE
  if (['VEHICLE', 'CAR', 'AUTOMOBILE', 'PLATE', 'VEHICLE_PLATE', 'ASSET'].includes(t)) {
    return 'VEHICLE';
  }

  // DOMAIN / HOSTNAME / SUBDOMAIN
  if (['DOMAIN', 'SUBDOMAIN', 'HOSTNAME', 'FQDN', 'WEBSITE', 'URL', 'URI', 'VHOST'].includes(t)) {
    return 'DOMAIN';
  }

  // IP ADDRESS
  if (['IP', 'IPV4', 'IPV6', 'IP_ADDRESS', 'CIDR', 'SUBNET'].includes(t)) {
    return 'IP';
  }

  // LOCATION / GEO
  if (['LOCATION', 'GEO', 'COORDINATES', 'PLACE', 'CITY', 'COUNTRY', 'STATE', 'REGION', 'ADDRESS', 'JURISDICTION'].includes(t)) {
    return 'LOCATION';
  }

  // MEDIA / VIDEO / IMAGE / POST
  if (['VIDEO', 'YOUTUBE_VIDEO', 'CHANNEL'].includes(t)) {
    return 'VIDEO';
  }
  if (['IMAGE', 'PHOTO', 'AVATAR', 'PICTURE'].includes(t)) {
    return 'IMAGE';
  }
  if (['POST', 'TWEET', 'STATUS', 'SOCIAL_POST', 'THREAD', 'COMMENT'].includes(t)) {
    return 'POST';
  }

  // ARTICLE / NEWS / DOCUMENT
  if (['ARTICLE', 'NEWS', 'DOCUMENT', 'REPORT', 'PUBLICATION'].includes(t)) {
    return 'ARTICLE';
  }

  // EVIDENCE
  if (['EVIDENCE', 'RECORD', 'CERTIFICATE', 'PROOF'].includes(t)) {
    return 'EVIDENCE';
  }

  // THREAT INDICATOR / VULNERABILITY
  if (['VULNERABILITY', 'CVE', 'THREAT_INDICATOR', 'MALWARE', 'THREAT', 'EXPLOIT', 'IOC', 'ATTACK_VECTOR'].includes(t)) {
    return 'THREAT_INDICATOR';
  }

  // HASH / CRYPTO
  if (['HASH', 'SHA256', 'MD5', 'SHA1'].includes(t)) {
    return 'HASH';
  }

  // KEYWORD
  if (['KEYWORD', 'TAG', 'SEARCH_TERM', 'QUERY', 'TOPIC'].includes(t)) {
    return 'KEYWORD';
  }

  // Explicitly return UNKNOWN - never silently default to DOMAIN
  return 'UNKNOWN';
};

export const extractEntityAvatar = (ent: any): string | null => {
  if (!ent) return null;
  const meta = ent.metadata || {};
  const direct =
    meta.avatar_url ||
    meta.image_url ||
    meta.profile_image ||
    meta.profile_pic ||
    meta.thumbnail_url ||
    meta.avatar ||
    meta.image ||
    null;
  if (direct && typeof direct === 'string') return direct.trim();
  return null;
};
