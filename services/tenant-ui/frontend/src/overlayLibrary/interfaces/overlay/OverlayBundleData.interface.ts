import { ICaptureBaseData, IOverlayData } from './OverlayData.interface';

export interface IOverlayBundleData {
  capture_base: ICaptureBaseData;
  overlays: IOverlayData[];
}
