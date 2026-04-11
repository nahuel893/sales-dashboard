/* Session expiry handler
 * Intercepts 401 responses from Dash callbacks and forces a page reload,
 * which redirects to /login when the session has expired.
 */
(function () {
    var _fetch = window.fetch;
    window.fetch = function (url, options) {
        return _fetch(url, options).then(function (response) {
            if (response.status === 401) {
                window.location.href = '/login';
            }
            return response;
        });
    };
})();
