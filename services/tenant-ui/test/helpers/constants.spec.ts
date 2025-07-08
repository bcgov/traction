import { RESERVATION_STATUSES } from "../../src/helpers/constants.js";

describe("constants", () => {
  describe("RESERVATION_STATUSES", () => {
    it("should have all expected status values", () => {
      expect(RESERVATION_STATUSES.APPROVED).toBe("approved");
      expect(RESERVATION_STATUSES.CHECKED_IN).toBe("checked_in");
      expect(RESERVATION_STATUSES.DENIED).toBe("denied");
      expect(RESERVATION_STATUSES.REQUESTED).toBe("requested");
    });

    it("should have correct number of statuses", () => {
      expect(Object.keys(RESERVATION_STATUSES)).toHaveLength(4);
    });

    it("should have immutable structure", () => {
      const statusKeys = Object.keys(RESERVATION_STATUSES);
      expect(statusKeys).toEqual([
        "APPROVED",
        "CHECKED_IN",
        "DENIED",
        "REQUESTED",
      ]);
    });
  });
});
