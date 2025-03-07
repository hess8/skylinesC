import AjaxRequest from './ajax-request';
/**
 * Same as `request` except it resolves an object with
 *
 *   {response, textStatus, jqXHR}
 *
 * Useful if you need access to the jqXHR object for headers, etc.
 *
 * @public
 */
export default function raw(url, options) {
    const ajax = AjaxRequest.create();
    return ajax.raw(url, options);
}
