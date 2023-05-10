import { BrandingOverlay } from './BrandingOverlay';
import { Overlay } from './Overlay';
import {
  CharacterEncodingOverlay,
  FormatOverlay,
  InformationOverlay,
  LabelOverlay,
  MetaOverlay,
  StandardOverlay,
} from './SemanticOverlay';

export const OverlayType: {
  [key: string]: typeof Overlay | typeof BrandingOverlay;
} = {
  'spec/overlays/character_encoding/1.0': CharacterEncodingOverlay,
  'spec/overlays/label/1.0': LabelOverlay,
  'spec/overlays/information/1.0': InformationOverlay,
  'spec/overlays/format/1.0': FormatOverlay,
  'spec/overlays/standard/1.0': StandardOverlay,
  'spec/overlays/meta/1.0': MetaOverlay,
  'aries/overlays/branding/1.0': BrandingOverlay,
};
