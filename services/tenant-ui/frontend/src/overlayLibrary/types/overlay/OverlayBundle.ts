/* eslint-disable  @typescript-eslint/ban-ts-comment */
import { BrandingOverlay } from './BrandingOverlay';
import { IBrandingOverlayData } from '../../interfaces/overlay/BrandingOverlayData.interface';
import { CaptureBase, Overlay } from './Overlay';
import { IOverlayBundleData } from '../../interfaces/overlay/OverlayBundleData.interface';
import { OverlayType } from './OverlayType';
import {
  FormatOverlay,
  InformationOverlay,
  LabelOverlay,
  MetaOverlay,
} from './SemanticOverlay';

export interface OverlayAttribute {
  name: string;
  type: string;
  information?: {
    [key: string]: string;
  };
  label?: {
    [key: string]: string;
  };
  format?: string;
}

export interface OverlayMetadata {
  name: {
    [key: string]: string;
  };
  description: {
    [key: string]: string;
  };
  credentialHelpText?: {
    [key: string]: string;
  };
  credentialSupportUrl?: {
    [key: string]: string;
  };
  issuer?: {
    [key: string]: string;
  };
  issuerDescription?: {
    [key: string]: string;
  };
  issuerUrl?: {
    [key: string]: string;
  };
}

class OverlayBundle {
  credentialDefinitionId!: string;
  captureBase!: CaptureBase;
  overlays!: Overlay[];
  languages!: string[];
  metadata!: OverlayMetadata;
  attributes!: OverlayAttribute[];

  constructor(credentialDefinitionId: string, bundle: IOverlayBundleData) {
    this.credentialDefinitionId = credentialDefinitionId;
    this.captureBase = new CaptureBase(bundle.capture_base);
    this.overlays = bundle.overlays
      .filter((overlay) => overlay.type !== 'aries/overlays/branding/1.0')
      .map((overlay) => {
        const OverlayClass = (OverlayType[overlay.type] ||
          Overlay) as typeof Overlay;
        return new OverlayClass(overlay);
      });
    this.overlays.push(
      ...bundle.overlays
        .filter((overlay) => overlay.type === 'aries/overlays/branding/1.0')
        .map((overlay) => {
          const OverlayClass = (OverlayType[overlay.type] ||
            BrandingOverlay) as typeof BrandingOverlay;
          return new OverlayClass(
            credentialDefinitionId,
            overlay as IBrandingOverlayData
          );
        })
    );
    this.languages = this.processLanguages();
    this.metadata = this.processMetadata();
    this.attributes = this.processOverlayAttributes();
  }

  get branding(): BrandingOverlay | undefined {
    return this.overlaysForType<BrandingOverlay>(
      'aries/overlays/branding/1.0'
    )[0];
  }

  displayAttribute(attributeName: string): OverlayAttribute | undefined {
    return this.attributes.find(
      (attribute) => attribute.name === attributeName
    );
  }

  private processMetadata(): OverlayMetadata {
    const metadata: OverlayMetadata = {
      name: {},
      description: {},
      credentialHelpText: {},
      credentialSupportUrl: {},
      issuer: {},
      issuerDescription: {},
      issuerUrl: {},
    };
    for (const overlay of this.overlaysForType<MetaOverlay>(
      'spec/overlays/meta/1.0'
    )) {
      const language = overlay.language ?? 'en';
      const {
        name,
        description,
        credentialHelpText,
        credentialSupportUrl,
        issuer,
        issuerDescription,
        issuerUrl,
      } = overlay;

      if (name) {
        metadata.name[language] = name;
      }
      if (description) {
        metadata.description[language] = description;
      }
      if (credentialHelpText) {
        // @ts-ignore
        metadata.credentialHelpText[language] = credentialHelpText;
      }
      if (credentialSupportUrl) {
        // @ts-ignore
        metadata.credentialSupportUrl[language] = credentialSupportUrl;
      }
      if (issuer) {
        // @ts-ignore
        metadata.issuer[language] = issuer;
      }
      if (issuerDescription) {
        // @ts-ignore
        metadata.issuerDescription[language] = issuerDescription;
      }
      if (issuerUrl) {
        // @ts-ignore
        metadata.issuerUrl[language] = issuerUrl;
      }
    }
    return metadata;
  }

  private processLanguages(): string[] {
    const languages: string[] = [];
    for (const overlay of this.overlaysForType<MetaOverlay>(
      'spec/overlays/meta/1.0'
    )) {
      const language = overlay.language;
      if (language && !languages.includes(language)) {
        languages.push(language);
      }
    }
    languages.sort((a, b) => a.localeCompare(b));
    return languages;
  }

  private processOverlayAttributes(): OverlayAttribute[] {
    const attributes: OverlayAttribute[] = [];
    const attributeMap = new Map(Object.entries(this.captureBase.attributes));
    for (const [name, type] of attributeMap) {
      attributes.push({
        name,
        type,
        information: this.processInformationForAttribute(name),
        label: this.processLabelForAttribute(name),
        format: this.processFormatForAttribute(name),
      });
    }
    return attributes;
  }

  private processInformationForAttribute(key: string): {
    [key: string]: string;
  } {
    const information: { [key: string]: string } = {};
    for (const overlay of this.overlaysForType<InformationOverlay>(
      'spec/overlays/information/1.0'
    )) {
      if (overlay.attributeInformation?.[key]) {
        const language = overlay.language ?? 'en';
        information[language] = overlay.attributeInformation[key];
      }
    }
    return information;
  }

  private processLabelForAttribute(key: string): { [key: string]: string } {
    const label: { [key: string]: string } = {};
    for (const overlay of this.overlaysForType<LabelOverlay>(
      'spec/overlays/label/1.0'
    )) {
      if (overlay.attributeLabels?.[key]) {
        const language = overlay.language ?? 'en';
        label[language] = overlay.attributeLabels[key];
      }
    }
    return label;
  }

  private processFormatForAttribute(key: string): string | undefined {
    for (const overlay of this.overlaysForType<FormatOverlay>(
      'spec/overlays/format/1.0'
    )) {
      if (overlay.attributeFormats?.[key]) {
        return overlay.attributeFormats[key];
      }
    }
    return;
  }

  private overlaysForType<T>(type: string): T[] {
    return this.overlays.filter((overlay) => overlay.type === type) as T[];
  }
}

export default OverlayBundle;
