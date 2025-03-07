import AjaxRequest from './ajax-request';
/**
 * Helper function that allows you to use the default `ember-ajax` to make
 * requests without using the service.
 *
 * @public
 */
export default function request(url, options) {
    const ajax = AjaxRequest.create();
    return ajax.request(url, options);
}
