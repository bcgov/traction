import { IOverlayData } from './OverlayData.interface';

export interface ICharacterEncodingOverlayData extends IOverlayData {
  default_character_encoding: string;
  attr_character_encoding: {
    [key: string]: string;
  };
}

export interface IFormatOverlayData extends IOverlayData {
  attribute_formats: {
    [key: string]: string;
  };
}

export interface IInformationOverlayData extends IOverlayData {
  language: string;
  attribute_information: {
    [key: string]: string;
  };
}

export interface ILabelOverlayData extends IOverlayData {
  language: string;
  attribute_labels: {
    [key: string]: string;
  };
  attribute_categories: string[];
  category_labels: {
    [key: string]: string;
  };
}

export interface IMetaOverlayData extends IOverlayData {
  language: string;
  name: string;
  description: string;
  credential_help_text: string;
  credential_support_url: string;
  issuer: string;
  issuer_description: string;
  issuer_url: string;
}

export interface IStandardOverlayData extends IOverlayData {
  attr_standards: {
    [key: string]: string;
  };
}
