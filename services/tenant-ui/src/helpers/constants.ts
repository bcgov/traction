export const RESERVATION_STATUSES = {
  APPROVED: "approved",
  CHECKED_IN: "checked_in",
  DENIED: "denied",
  REQUESTED: "requested",
} as const;

export type ReservationStatus =
  (typeof RESERVATION_STATUSES)[keyof typeof RESERVATION_STATUSES];
