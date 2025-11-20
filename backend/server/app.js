const express = require("express");
const cors = require("cors");
const pool = require("../db");

const app = express();
app.use(express.json());
app.use(cors());

// 메뉴 전체 조회
app.get("/api/menu", async (req, res) => {
    const [rows] = await pool.query("SELECT * FROM menu ORDER BY id DESC");
    res.json(rows);
});

// 메뉴 추가
app.post("/api/menu", async (req, res) => {
    const { name } = req.body;

    if (!name || !name.trim()) {
        return res.status(400).json({ message: "메뉴명이 없습니다." });
    }

    const [result] = await pool.query(
        "INSERT INTO menu (name) VALUES (?)",
        [name]
    );

    res.json({
        id: result.insertId,
        name
    });
});

app.listen(3000, () => console.log("Backend running on 3000"));
