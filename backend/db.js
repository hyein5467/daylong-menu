const mysql = require('mysql2/promise');

const pool = mysql.createPool({
    host: "svc.sel3.cloudtype.app",
    port: 31443,
    user: "root",          // Cloudtype에서 제공된 DB 사용자
    password: "daylong",       // Cloudtype MariaDB 비밀번호
    database: "daylong",   // Cloudtype MariaDB DB 이름
    ssl: {
        rejectUnauthorized: false
    }
});

module.exports = pool;
