const jiti = require('jiti')(__filename);
const assert = require('assert');

const { getEntityCategory } = jiti('./categoryUtils.ts');

console.log('[TEST] Running getEntityCategory verification suite...');

// 1. Phone variants must be PHONE, NEVER DOMAIN
assert.strictEqual(getEntityCategory('PHONE'), 'PHONE');
assert.strictEqual(getEntityCategory('phone'), 'PHONE');
assert.strictEqual(getEntityCategory('TELEPHONE'), 'PHONE');
assert.strictEqual(getEntityCategory('msisdn'), 'PHONE');
assert.strictEqual(getEntityCategory('cell'), 'PHONE');
assert.strictEqual(getEntityCategory('mobile'), 'PHONE');
assert.strictEqual(getEntityCategory('EntityType.PHONE'), 'PHONE');
assert.strictEqual(getEntityCategory('entitytype.phone'), 'PHONE');

// 2. Email variants
assert.strictEqual(getEntityCategory('EMAIL'), 'EMAIL');
assert.strictEqual(getEntityCategory('email_address'), 'EMAIL');

// 3. Person / Identities
assert.strictEqual(getEntityCategory('PERSON'), 'PERSON');
assert.strictEqual(getEntityCategory('name'), 'PERSON');
assert.strictEqual(getEntityCategory('username'), 'PERSON');
assert.strictEqual(getEntityCategory('account'), 'PERSON');

// 4. Vehicles
assert.strictEqual(getEntityCategory('VEHICLE'), 'VEHICLE');
assert.strictEqual(getEntityCategory('plate'), 'VEHICLE');
assert.strictEqual(getEntityCategory('vehicle_plate'), 'VEHICLE');

// 5. Locations
assert.strictEqual(getEntityCategory('LOCATION'), 'LOCATION');
assert.strictEqual(getEntityCategory('geo'), 'LOCATION');
assert.strictEqual(getEntityCategory('coordinates'), 'LOCATION');

// 6. Media / Video / Image / Post
assert.strictEqual(getEntityCategory('VIDEO'), 'VIDEO');
assert.strictEqual(getEntityCategory('youtube_video'), 'VIDEO');
assert.strictEqual(getEntityCategory('post'), 'POST');
assert.strictEqual(getEntityCategory('image'), 'IMAGE');

// 7. Articles / News
assert.strictEqual(getEntityCategory('ARTICLE'), 'ARTICLE');
assert.strictEqual(getEntityCategory('news'), 'ARTICLE');

// 8. Domains & IPs
assert.strictEqual(getEntityCategory('DOMAIN'), 'DOMAIN');
assert.strictEqual(getEntityCategory('hostname'), 'DOMAIN');
assert.strictEqual(getEntityCategory('ip'), 'IP');
assert.strictEqual(getEntityCategory('ipv4'), 'IP');

// 9. Threats & Evidence
assert.strictEqual(getEntityCategory('THREAT_INDICATOR'), 'THREAT_INDICATOR');
assert.strictEqual(getEntityCategory('vulnerability'), 'THREAT_INDICATOR');
assert.strictEqual(getEntityCategory('evidence'), 'EVIDENCE');
assert.strictEqual(getEntityCategory('keyword'), 'KEYWORD');

// 10. CRITICAL REGRESSION: Unknown values must return UNKNOWN, NEVER DOMAIN!
assert.strictEqual(getEntityCategory('unknown_xyz'), 'UNKNOWN');
assert.strictEqual(getEntityCategory(''), 'UNKNOWN');
assert.strictEqual(getEntityCategory(null), 'UNKNOWN');
assert.strictEqual(getEntityCategory(undefined), 'UNKNOWN');
assert.notStrictEqual(getEntityCategory('phone'), 'DOMAIN', 'CRITICAL BUG: phone must never be DOMAIN');

console.log('[TEST] PASS: All 25 getEntityCategory assertions passed successfully!');
