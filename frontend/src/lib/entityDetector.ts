/**
 * Universal Entity Detection & Classification Utility
 * Deterministically identifies entity type from user input strings:
 * IP, DOMAIN, EMAIL, PHONE, USERNAME, CVE, VEHICLE, or KEYWORD.
 */

export type DetectedEntityType =
  | 'DOMAIN'
  | 'IP'
  | 'EMAIL'
  | 'PHONE'
  | 'USERNAME'
  | 'CVE'
  | 'VEHICLE'
  | 'KEYWORD';

export interface EntityDetectionResult {
  type: DetectedEntityType;
  label: string;
  normalized: string;
  badgeColor: string;
  confidence: number;
}

export function detectEntityType(input: string): EntityDetectionResult {
  const trimmed = input.trim();
  if (!trimmed) {
    return {
      type: 'DOMAIN',
      label: 'Domain / FQDN',
      normalized: '',
      badgeColor: 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/60 dark:text-indigo-300',
      confidence: 0,
    };
  }

  // 1. IP Address (IPv4 / IPv6 / CIDR)
  const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\/[0-9]{1,2})?$/;
  const ipv6Regex = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
  if (ipv4Regex.test(trimmed) || ipv6Regex.test(trimmed)) {
    return {
      type: 'IP',
      label: 'IP Address / Subnet',
      normalized: trimmed,
      badgeColor: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/60 dark:text-blue-300',
      confidence: 0.99,
    };
  }

  // 2. Email Address
  const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
  if (emailRegex.test(trimmed)) {
    return {
      type: 'EMAIL',
      label: 'Email Address',
      normalized: trimmed.toLowerCase(),
      badgeColor: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/60 dark:text-amber-300',
      confidence: 0.98,
    };
  }

  // 3. Vulnerability CVE
  const cveRegex = /^CVE-\d{4}-\d{4,8}$/i;
  if (cveRegex.test(trimmed)) {
    return {
      type: 'CVE',
      label: 'Vulnerability CVE',
      normalized: trimmed.toUpperCase(),
      badgeColor: 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/60 dark:text-rose-300',
      confidence: 0.99,
    };
  }

  // 4. Vehicle License Plate
  const vehicleRegex = /^[A-Z]{2}\s?[0-9]{1,2}\s?[A-Z]{0,3}\s?[0-9]{4}$/i;
  if (vehicleRegex.test(trimmed.trim())) {
    return {
      type: 'VEHICLE',
      label: 'Vehicle License Plate',
      normalized: trimmed.replace(/\s+/g, '').toUpperCase(),
      badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300',
      confidence: 0.95,
    };
  }

  // 5. Phone Number
  const digits = trimmed.replace(/[^0-9]/g, '');
  if (
    (trimmed.startsWith('+') || trimmed.includes('-') || trimmed.includes('(')) &&
    digits.length >= 7 &&
    digits.length <= 15
  ) {
    return {
      type: 'PHONE',
      label: 'Phone Number',
      normalized: trimmed,
      badgeColor: 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/60 dark:text-purple-300',
      confidence: 0.92,
    };
  }

  // 6. Domain / URL
  const domainRegex = /^(?:https?:\/\/)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?:\/.*)?$/;
  if (domainRegex.test(trimmed) && !trimmed.includes(' ') && !trimmed.startsWith('@')) {
    const cleanDomain = trimmed.replace(/^https?:\/\//i, '').split('/')[0].split(':')[0];
    return {
      type: 'DOMAIN',
      label: 'Domain / FQDN',
      normalized: cleanDomain.toLowerCase(),
      badgeColor: 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/60 dark:text-indigo-300',
      confidence: 0.96,
    };
  }

  // 7. Username / Handle
  if (/^@?[a-zA-Z0-9_.-]{3,30}$/.test(trimmed) && !trimmed.includes('.')) {
    return {
      type: 'USERNAME',
      label: 'Username / Handle',
      normalized: trimmed.replace(/^@/, ''),
      badgeColor: 'bg-teal-50 text-teal-700 border-teal-200 dark:bg-teal-950/60 dark:text-teal-300',
      confidence: 0.88,
    };
  }

  return {
    type: 'KEYWORD',
    label: 'Entity / Search Keyword',
    normalized: trimmed,
    badgeColor: 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300',
    confidence: 0.75,
  };
}
