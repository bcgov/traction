import { buildStatusAutofill } from "../../src/helpers/index.js";

describe("buildStatusAutofill", () => {
  const body = {
    serverUrlStatusRoute: "http://tenant-ui.gov.bc.ca",
    contactEmail: "my.email@gov.fake",
    reservationId: "50542cfe-e9bd-4881-8a71-1b529f40bc2b",
  };

  it("should return a correctly formed url including the body params", () => {
    expect(buildStatusAutofill(body)).toBe(
      "http://tenant-ui.gov.bc.ca?email=my.email%40gov.fake&id=50542cfe-e9bd-4881-8a71-1b529f40bc2b"
    );
  });

  it("should percent-encode special characters in email and id", () => {
    expect(
      buildStatusAutofill({
        serverUrlStatusRoute: "https://example.com/check",
        contactEmail: "user+tag@example.com",
        reservationId: "id with spaces & symbols=1",
      })
    ).toBe(
      "https://example.com/check?email=user%2Btag%40example.com&id=id%20with%20spaces%20%26%20symbols%3D1"
    );
  });

  it("should return a blank string for no input param", () => {
    expect(buildStatusAutofill(undefined)).toBe("");
    expect(buildStatusAutofill(null)).toBe("");
    expect(buildStatusAutofill({})).toBe("");
    expect(buildStatusAutofill("")).toBe("");
  });

  it("should return a blank string for no serverUrlStatusRoute", () => {
    expect(
      buildStatusAutofill({
        contactEmail: "abc@test.com",
        reservationId: "123",
      })
    ).toBe("");
  });
});
