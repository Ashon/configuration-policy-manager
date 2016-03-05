
var frisby = require('frisby');
var host = require('./host');


frisby.globalSetup({
    request: {
        baseUrl: host.RESTAPI_HOST,
        timeout: 300
    }
})


frisby
    .create('[GET] Status Code Should be 401 when user is not logged.')
    .get('/version/')
    .expectStatus(401)
    .toss();

frisby
    .create('[GET] Status Code Should be 200 when user is valid.')
    .get('/version/')
    .expectStatus(200)
    .auth(
        host.RESTAPI_USER,
        host.RESTAPI_PASS)
    .toss();
