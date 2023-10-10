import { format, fromUnixTime, parseJSON } from 'date-fns';
import { enCA, fr, ja } from 'date-fns/locale';
import { useI18n } from 'vue-i18n';

export type I18nLocale = 'en' | 'fr' | 'ja';

function i18n2DateLocale(i18nLocale: I18nLocale): Locale {
  switch (i18nLocale) {
    case 'en':
      return enCA;
    case 'fr':
      return fr;
    case 'ja':
      return ja;
  }
  // This way we can fall back to a default while using typescript to
  // enforce that all instances of i18nLocale have a corresponding case in the
  // switch statement
  /* eslint no-unreachable: "error" */
  throw new Error('No valid date-fn');
}

function _dateFnsFormat(value: string, formatter: string) {
  const { locale } = useI18n();
  const formatted = '';
  try {
    if (value) {
      try {
        return format(parseJSON(value), formatter, {
          locale: i18n2DateLocale(locale.value as I18nLocale),
        });
      } catch {
        // Incase the locale was never set (used outside of a vue component)
        console.log(
          `No valid translation found for ${locale.value} defaulting to enCA`
        );
        return format(parseJSON(value), formatter, { locale: enCA });
      }
    }
  } catch (error) {
    console.error(`_dateFnsFormat: Error parsing ${value} to ${error}`);
  }
  return formatted;
}

/**
 * @function formatDate
 * Converts an acapy-returned string date to an 'MMMM D YYYY' formatted string
 * @param {String} value A string representation of a date
 * @returns {String} A string representation of `value`
 */
export function formatDate(value: string) {
  return _dateFnsFormat(value, 'MMMM d yyyy');
}

/**
 * @function formatDateLong
 * Converts an acapy-returned string date to an 'MMMM D yyyy, h:mm:ss a' formatted string
 * @param {String} value A string representation of a date
 * @returns {String} A string representation of `value`
 */
export function formatDateLong(value: string | undefined) {
  return value ? _dateFnsFormat(value, 'MMMM d yyyy, h:mm:ss a') : '';
}

/**
 * @function formatUnixDate
 * Converts a unix time number to an 'MMMM D yyyy' formatted string
 * @param {String} value A unix timestamp number
 * @returns {String} A string representation of `value`
 */
export function formatUnixDate(value: number) {
  return format(fromUnixTime(value), 'MMMM d yyyy');
}

export function toKebabCase(str: string | null) {
  const strs =
    str &&
    str.match(
      /[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g
    );
  return strs ? strs.join('-').toLocaleLowerCase() : '';
}

export function paramFromUrlString(url: string, paramName: string) {
  const results = new RegExp('[?&]' + paramName + '=([^&#]*)').exec(url);
  if (results == null) {
    return null;
  }
  return decodeURI(results[1]) || 0;
}

export function isJsonString(str: string) {
  try {
    JSON.parse(str);
  } catch (e) {
    return false;
  }
  return true;
}

export function formatGuid(guid: string): string {
  return guid.replace(/(\w{8})(\w{4})(\w{4})(\w{4})(\w{12})/, '$1-$2-$3-$4-$5');
}

export function stringOrBooleanTruthy(value: string | boolean) {
  return value === 'true' || value === true;
}
