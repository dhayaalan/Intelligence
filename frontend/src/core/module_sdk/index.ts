import React from 'react';
import { Entity, Evidence, SearchResponse } from '../../types';

export interface ModuleSearchResultProps {
  searchResult: SearchResponse;
  moduleEntities: Entity[];
  moduleEvidence: Evidence[];
}

export interface ModuleEntityPanelProps {
  entity: Entity;
  allEntities: Entity[];
}

export interface ModuleInvestigationPanelProps {
  investigationId: string;
  entities: Entity[];
  evidence: Evidence[];
}

export interface ModuleUIExtension {
  id: string;
  name: string;
  badge: string;
  color: string;
  iconName: string;
  SearchResultComponent?: React.ComponentType<ModuleSearchResultProps>;
  EntityDetailComponent?: React.ComponentType<ModuleEntityPanelProps>;
  InvestigationPanelComponent?: React.ComponentType<ModuleInvestigationPanelProps>;
}

class FrontendModuleRegistry {
  private extensions: Map<string, ModuleUIExtension> = new Map();

  registerExtension(extension: ModuleUIExtension) {
    this.extensions.set(extension.id, extension);
  }

  getExtension(id: string): ModuleUIExtension | undefined {
    return this.extensions.get(id);
  }

  getAllExtensions(): ModuleUIExtension[] {
    return Array.from(this.extensions.values());
  }

  getActiveExtensions(activeModuleIds: string[]): ModuleUIExtension[] {
    return activeModuleIds
      .map((id) => this.extensions.get(id))
      .filter((ext): ext is ModuleUIExtension => ext !== undefined);
  }
}

export const frontendModuleRegistry = new FrontendModuleRegistry();
