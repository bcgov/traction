import { format, parseISO } from 'date-fns'

function _dateFnsFormat(value: string, formatter: string) {
  try {
    if (value) {
      return format(parseISO(value), formatter);
    }
  } catch (error) {
    console.error(`_dateFnsFormat: Error parsing ${value} to ${formatter}`);
  } finally {
    return '';
  }
};

/**
 * @function formatDate
 * Converts a date to an 'MMMM D YYYY' formatted string
 * @param {String} value A string representation of a date
 * @returns {String} A string representation of `value`
 */
export function formatDate(value: string) {
  return _dateFnsFormat(value, 'MMMM D YYYY');
};

/**
 * @function formatDateLong
 * Converts a date to an 'MMMM D YYYY, h:mm:ss a' formatted string
 * @param {String} value A string representation of a date
 * @returns {String} A string representation of `value`
 */
export function formatDateLong(value: string) {
  return _dateFnsFormat(value, 'MMMM D YYYY, h:mm:ss a');
};
