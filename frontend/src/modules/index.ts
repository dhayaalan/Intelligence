import { registerOsintModule } from './osint';
import { registerThreatIntelModule } from './threat_intelligence';

let registered = false;

export function initializeFrontendModules() {
  if (registered) return;
  registerOsintModule();
  registerThreatIntelModule();
  registered = true;
}
