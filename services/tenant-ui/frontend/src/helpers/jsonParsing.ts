export function tryParseJson<T>(jsonString: string): T | undefined {
  try {
    const o = JSON.parse(jsonString);
    if (o && typeof o === 'object') {
      return o;
    }
    return undefined;
  } catch (e) {
    return undefined;
  }
}
