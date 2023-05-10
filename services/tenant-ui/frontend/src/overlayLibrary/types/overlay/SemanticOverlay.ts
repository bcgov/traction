import { Overlay } from './Overlay';
import {
  ICharacterEncodingOverlayData,
  IFormatOverlayData,
  IInformationOverlayData,
  ILabelOverlayData,
  IMetaOverlayData,
  IStandardOverlayData,
} from '../../interfaces/overlay/SemanticOverlay.interface';

export class CharacterEncodingOverlay extends Overlay {
  #default_character_encoding: string;
  #attr_character_encoding: {
    [key: string]: string;
  };

  constructor(overlay: ICharacterEncodingOverlayData) {
    super(overlay);
    this.#default_character_encoding = overlay.default_character_encoding;
    this.#attr_character_encoding = overlay.attr_character_encoding;
  }

  get defaultCharacterEncoding(): string {
    return this.#default_character_encoding;
  }

  get attributeCharacterEncoding(): { [key: string]: string } {
    return this.#attr_character_encoding;
  }
}

export class FormatOverlay extends Overlay {
  #attribute_formats: {
    [key: string]: string;
  };

  constructor(overlay: IFormatOverlayData) {
    super(overlay);
    this.#attribute_formats = overlay.attribute_formats;
  }

  get attributeFormats(): { [key: string]: string } {
    return this.#attribute_formats;
  }
}

export class InformationOverlay extends Overlay {
  #attribute_information: {
    [key: string]: string;
  };

  language: string;

  constructor(overlay: IInformationOverlayData) {
    super(overlay);
    this.language = overlay.language;
    this.#attribute_information = overlay.attribute_information;
  }

  get attributeInformation(): { [key: string]: string } {
    return this.#attribute_information;
  }
}

export class LabelOverlay extends Overlay {
  #attribute_labels: {
    [key: string]: string;
  };
  #attribute_categories: string[];
  #category_labels: {
    [key: string]: string;
  };

  language: string;

  constructor(overlay: ILabelOverlayData) {
    super(overlay);
    this.language = overlay.language;
    this.#attribute_labels = overlay.attribute_labels;
    this.#attribute_categories = overlay.attribute_categories;
    this.#category_labels = overlay.category_labels;
  }

  get attributeLabels(): { [key: string]: string } {
    return this.#attribute_labels;
  }

  get attributeCategories(): string[] {
    return this.#attribute_categories;
  }

  get categoryLabels(): { [key: string]: string } {
    return this.#category_labels;
  }
}

export class MetaOverlay extends Overlay {
  #credential_help_text: string;
  #credential_support_url: string;
  #issuer_description: string;
  #issuer_url: string;

  language: string;
  name: string;
  description: string;
  issuer: string;

  constructor(overlay: IMetaOverlayData) {
    super(overlay);
    this.language = overlay.language;
    this.name = overlay.name;
    this.description = overlay.description;
    this.#credential_help_text = overlay.credential_help_text;
    this.#credential_support_url = overlay.credential_support_url;
    this.issuer = overlay.issuer;
    this.#issuer_description = overlay.issuer_description;
    this.#issuer_url = overlay.issuer_url;
  }

  get credentialHelpText(): string {
    return this.#credential_help_text;
  }

  get credentialSupportUrl(): string {
    return this.#credential_support_url;
  }

  get issuerDescription(): string {
    return this.#issuer_description;
  }

  get issuerUrl(): string {
    return this.#issuer_url;
  }
}

export class StandardOverlay extends Overlay {
  #attr_standards: {
    [key: string]: string;
  };

  constructor(overlay: IStandardOverlayData) {
    super(overlay);
    this.#attr_standards = overlay.attr_standards;
  }

  get attributeStandards(): { [key: string]: string } {
    return this.#attr_standards;
  }
}
