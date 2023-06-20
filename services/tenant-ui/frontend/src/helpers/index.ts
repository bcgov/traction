import { format, fromUnixTime, parseJSON } from 'date-fns';
import { enCA, fr, ja } from 'date-fns/locale';
import { useI18n } from 'vue-i18n';

export type i18nLocale = 'en' | 'fr' | 'jp';

function i18n2DateLocale(i18nLocal: i18nLocale) {
  switch (i18nLocal) {
    case 'en':
      return enCA;
    case 'fr':
      return fr;
    case 'jp':
      return ja;
    default:
      console.log(
        `No valid translation found for ${i18nLocal} defaulting to enCA`
      );
      return enCA;
  }
}

function _dateFnsFormat(value: string, formatter: string) {
  const { locale } = useI18n();
  const formatted = '';
  try {
    if (value) {
      return format(parseJSON(value), formatter, {
        locale: i18n2DateLocale(locale.value as i18nLocale),
      });
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
export function formatDateLong(value: string) {
  return _dateFnsFormat(value, 'MMMM d yyyy, h:mm:ss a');
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
