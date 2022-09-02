import { format, parseJSON } from 'date-fns';

function _dateFnsFormat(value: string, formatter: string) {
  const formatted = '';
  try {
    if (value) {
      return format(parseJSON(value), formatter);
    }
  } catch (error) {
    console.error(`_dateFnsFormat: Error parsing ${value} to ${error}`);
  }
  return formatted;
}

/**
 * @function formatDate
 * Converts a date to an 'MMMM D YYYY' formatted string
 * @param {String} value A string representation of a date
 * @returns {String} A string representation of `value`
 */
export function formatDate(value: string) {
  return _dateFnsFormat(value, 'MMMM d yyyy');
}

/**
 * @function formatDateLong
 * Converts a date to an 'MMMM D yyyy, h:mm:ss a' formatted string
 * @param {String} value A string representation of a date
 * @returns {String} A string representation of `value`
 */
export function formatDateLong(value: string) {
  return _dateFnsFormat(value, 'MMMM d yyyy, h:mm:ss a');
}
