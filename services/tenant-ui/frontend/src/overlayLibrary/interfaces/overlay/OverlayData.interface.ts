export interface ICaptureBaseData {
  type: string;
  classification: string;
  attributes: {
    [key: string]: string;
  };
  flagged_attributes: string[];
  digest?: string;
}

export interface IOverlayData {
  type: string;
  capture_base: string;
  digest?: string;
}
