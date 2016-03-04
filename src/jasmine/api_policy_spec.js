
var crypto = require('crypto');
var frisby = require('frisby');

var host = require('./host');
var models = require('./models');
var req = require('./config_policy_requests');

var testID = crypto.createHash('md5').update(Date().toString()).digest("hex").slice(0, 5);
var TEST_DATA_PREFIX = 'frisby_test-';


req.ReadPolicyListTest('get Policy List')

    .expectJSONTypes(models.APIResponse)
    .afterJSON(function(response) {

        response.results
            .filter(function(policy) {
                return policy.policy_name.search(TEST_DATA_PREFIX) > -1;
            })
            .forEach(function(policy) {
                req.DeletePolicyTest('cleanup', policy.policy_id).toss();
            });
    })

    .toss();

// test fixtures
var createForm = {
    policy_name: TEST_DATA_PREFIX + testID
};

var updateForm = {
    policy_name: TEST_DATA_PREFIX + testID + '-updated'
};

req.CreatePolicyTest('[POST] Add Config Policy Test', createForm)

    .expectJSONTypes(models.ConfigPolicy)
    .afterJSON(function(response) {

        var registeredPolicyID = response.policy_id;

        // update policy name
        req.UpdatePolicyTest('[PUT] Update Config Policy Name Test', registeredPolicyID, updateForm)

            .expectJSONTypes(models.ConfigPolicy)
            .afterJSON(function(response) {
                req.DeletePolicyTest('cleanup', registeredPolicyID).toss();
            })
            .toss();
    })
    .toss();


// test fixtures
var scenarioTestCreateForm = {
    policy_name: TEST_DATA_PREFIX + testID + '-scenario'
};

var createPolicySchemeFormA = {
    scheme_name: TEST_DATA_PREFIX + testID + '-scheme-a',
    scheme_type: 'string'
};

var createPolicySchemeFormB = {
    scheme_name: TEST_DATA_PREFIX + testID + '-scheme-b',
    scheme_type: 'string'
};

// create policy
req.CreatePolicyTest('Policy Add Schema Scenario test', scenarioTestCreateForm)

    .expectJSONTypes(models.ConfigPolicy)
    .afterJSON(function(response) {

        var registeredPolicyID = response.policy_id;

        // add policy schema-a
        req.CreatePolicySchemeTest('Add Policy Schema A - ' + testID, registeredPolicyID, createPolicySchemeFormA)

            .expectJSONTypes(models.ConfigPolicyScheme)
            .afterJSON(function(response) {

                var schemeA = response;

                // add policy schema-b
                req.CreatePolicySchemeTest('Add Policy Schema B - ' + testID, registeredPolicyID, createPolicySchemeFormB)

                    .expectJSONTypes(models.ConfigPolicyScheme)
                    .afterJSON(function(response) {

                        var schemeB = response;

                        req.ReadPolicyTest('get policy info - policy should have 2 schema', registeredPolicyID)
                            .expectJSONTypes(models.ConfigPolicy)

                            // registered policy should have schema which registered in test.
                            .expectJSON('schema', [ schemeA, schemeB ])

                            .afterJSON(function(response) {
                                // cleanup
                                req.DeletePolicyTest('cleanup', registeredPolicyID).toss();
                            })
                            .toss();
                    })
                    .toss();
            })
            .toss();
    })
    .toss();
