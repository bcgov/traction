// import { createContext, Dispatch, useContext, useReducer } from "react";

export interface Action {
  type: string;
  payload: any;
}

export enum ActionType {
  SET_BRANDING = 'setBranding',
  LOGO = 'logo',
  BACKGROUND_IMAGE = 'backgroundImage',
  BACKGROUND_IMAGE_SLICE = 'backgroundImageSlice',
  PRIMARY_BACKGROUND_COLOR = 'primaryBackgroundColor',
  SECONDARY_BACKGROUND_COLOR = 'secondaryBackgroundColor',
  PRIMARY_ATTRIBUTE = 'primaryAttribute',
  SECONDARY_ATTRIBUTE = 'secondaryAttribute',
  ISSUED_DATE_ATTRIBUTE = 'issuedDateAttribute',
  EXPIRY_DATE_ATTRIBUTE = 'expiryDateAttribute',
}

export interface BrandingState {
  captureBase?: string;
  type?: string;
  digest?: string;
  logo: string;
  backgroundImage: string;
  backgroundImageSlice: string;
  primaryBackgroundColor: string;
  secondaryBackgroundColor: string;
  primaryAttribute: string;
  secondaryAttribute: string;
  issuedDateAttribute?: string;
  expiryDateAttribute?: string;
}

const initialState: BrandingState = {
  captureBase: '',
  type: '',
  digest: '',
  logo: '',
  backgroundImage: '',
  backgroundImageSlice: '',
  primaryBackgroundColor: '',
  secondaryBackgroundColor: '',
  primaryAttribute: '',
  secondaryAttribute: '',
  issuedDateAttribute: undefined,
  expiryDateAttribute: undefined,
};

// const BrandingContext = createContext<BrandingState | null>(null);
// const BrandingDispatchContext = createContext<Dispatch<Action> | null>(null);

// export function BrandingProvider({ children }: any) {
//   const [state, dispatch] = useReducer(brandingReducer, initialState);

//   return (
//     <BrandingContext.Provider value={state}>
//       <BrandingDispatchContext.Provider value={dispatch}>
//         {children}
//       </BrandingDispatchContext.Provider>
//     </BrandingContext.Provider>
//   );
// }

// export function useBranding() {
//   return useContext(BrandingContext);
// }

// export function useBrandingDispatch() {
//   return useContext(BrandingDispatchContext);
// }

export function brandingReducer(
  state = initialState,
  action: Action
): BrandingState {
  switch (action.type) {
    case ActionType.SET_BRANDING:
    case ActionType.LOGO:
    case ActionType.BACKGROUND_IMAGE:
    case ActionType.BACKGROUND_IMAGE_SLICE:
    case ActionType.PRIMARY_BACKGROUND_COLOR:
    case ActionType.SECONDARY_BACKGROUND_COLOR:
    case ActionType.PRIMARY_ATTRIBUTE:
    case ActionType.SECONDARY_ATTRIBUTE:
      return {
        ...state,
        ...action.payload,
      };
    default:
      return state;
  }
}
