function nullOr(type) {
    return function(val) {
        expect(val).toBeTypeOrNull(type);
    };
}

module.exports.APIResponse = {
    count: Number,
    next: nullOr(String),
    previous: nullOr(String),
    results: Array
};

module.exports.ConfigPolicy = {
    policy_id: Number,
    policy_name: String,
    policy_description: nullOr(String),
    schema: Array,
    rules: Array
};

module.exports.ConfigPolicyScheme = {
    policy_id: Number,
    scheme_id: Number,
    scheme_name: String,
    scheme_type: String,
    scheme_description: nullOr(String)
}