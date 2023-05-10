import OverlayBundle from '../types/overlay/OverlayBundle';
import { IOverlayBundleData } from '../interfaces/overlay/OverlayBundleData.interface';

class OverlayBundleFactory {
  public static async fetchOverlayBundle(
    credentialDefinitionId: string,
    url: string
  ): Promise<OverlayBundle> {
    const response = await fetch(url);
    const data: IOverlayBundleData[] = await response.json();
    return this.createOverlayBundle(credentialDefinitionId, data[0]);
  }

  public static createOverlayBundle(
    id: string,
    data: IOverlayBundleData
  ): OverlayBundle {
    return new OverlayBundle(id, data);
  }
}

export default OverlayBundleFactory;
