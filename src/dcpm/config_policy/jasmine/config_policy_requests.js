
var frisby = require('frisby');
var host = require('./host');

function wrap_auth(frisby) {
    return frisby.auth(
        host.RESTAPI_USER,
        host.RESTAPI_PASS);
};

module.exports.ReadPolicyListTest = function(casename) {

    return wrap_auth(frisby
        .create(casename)
        .get('config_policy/')
        .expectStatus(200));
}

module.exports.ReadPolicyTest = function(casename, policyID) {

    return wrap_auth(frisby
        .create(casename)
        .get('config_policy/' + policyID + '/')
        .expectStatus(200));
}

module.exports.DeletePolicyTest = function(casename, policyID) {

    return wrap_auth(frisby
        .create(casename)
        .delete('config_policy/' + policyID + '/')
        .expectStatus(204));
}

module.exports.CreatePolicyTest = function(casename, data) {

    return wrap_auth(frisby
        .create(casename)
        .post('config_policy/', data, { json: true })
        .expectStatus(201));
}

module.exports.UpdatePolicyTest = function(casename, policyID, data) {

    return wrap_auth(frisby
        .create(casename)
        .put('config_policy/' + policyID + '/', data, { json: true })
        .expectStatus(200));
}


module.exports.CreatePolicySchemeTest = function(casename, policyID, data) {
    return wrap_auth(frisby
        .create(casename)
        .post('config_policy/' + policyID + '/scheme/', data, { json: true })
        .expectStatus(201));
}