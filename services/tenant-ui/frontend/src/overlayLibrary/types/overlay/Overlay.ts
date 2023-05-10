import {
  ICaptureBaseData,
  IOverlayData,
} from '../../interfaces/overlay/OverlayData.interface';

export class CaptureBase {
  #flagged_attributes: string[];

  type: string;
  classification: string;
  attributes: {
    [key: string]: string;
  };
  digest: string;

  constructor(captureBase: ICaptureBaseData) {
    this.type = captureBase.type;
    this.classification = captureBase.classification;
    this.attributes = captureBase.attributes;
    this.#flagged_attributes = captureBase.flagged_attributes;
    this.digest = captureBase.digest ?? '';
  }

  get flaggedAttributes(): string[] {
    return this.#flagged_attributes;
  }
}

export class Overlay {
  #capture_base: string;

  type: string;
  digest: string;

  constructor(overlay: IOverlayData) {
    this.type = overlay.type;
    this.#capture_base = overlay.capture_base;
    this.digest = overlay.digest ?? '';
  }

  get captureBase(): string {
    return this.#capture_base;
  }
}
