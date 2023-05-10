import { BrandingState } from '../contexts/Branding';
import { IBrandingOverlayData } from '../interfaces/overlay/BrandingOverlayData.interface';

class BrandingOverlayDataFactory {
  public static getBrandingOverlayData(
    branding: BrandingState
  ): IBrandingOverlayData {
    const {
      captureBase,
      type,
      digest,
      logo,
      backgroundImageSlice,
      backgroundImage,
      primaryBackgroundColor,
      secondaryBackgroundColor,
      primaryAttribute,
      secondaryAttribute,
      issuedDateAttribute,
      expiryDateAttribute,
    } = branding;
    return {
      capture_base: captureBase ?? '',
      type: type ?? '',
      digest: digest ?? '',
      logo: logo ?? '',
      background_image_slice: backgroundImageSlice ?? '',
      background_image: backgroundImage ?? '',
      primary_background_color: primaryBackgroundColor ?? '',
      secondary_background_color: secondaryBackgroundColor ?? '',
      primary_attribute: primaryAttribute ?? '',
      secondary_attribute: secondaryAttribute ?? '',
      issued_date_attribute: issuedDateAttribute ?? '',
      expiry_date_attribute: expiryDateAttribute ?? '',
    };
  }
}

export default BrandingOverlayDataFactory;
