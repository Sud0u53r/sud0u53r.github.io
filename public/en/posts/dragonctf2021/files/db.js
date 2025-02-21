const { Pool } = require("pg");

function sqlEscape(value) {
	return "'" + String(value).replace(/[^\x20-\x7e]|[']/g, "") + "'";
}

function connect() {
	return new Pool({
		connectionString: "postgresql://webpwn:webpwn@localhost/webpwn",
	});
}

function prepare(query, params) {
	for (const key in params) {
		// console.log(query, params[key], sqlEscape(params[key]));
		query = query.replaceAll(":" + key, sqlEscape(params[key]));
		// console.log(params[key], sqlEscape(params[key]));
	}
	return query;
}

module.exports = {
	connect,
	prepare,
};
