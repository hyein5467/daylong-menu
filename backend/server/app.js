const express = require("express");
const cors = require("cors");
const pool = require("../db");

const app = express();
app.use(express.json());
app.use(cors());

// 인기메뉴
app.get("/api/popular", async (req, res) => {
  const [rows] = await pool.query("SELECT popular_drink, popular_snack FROM menu_recommend LIMIT 1");

  const drinkId = rows[0].popular_drink;
  const snackId = rows[0].popular_snack;

  const [[drink]] = await pool.query("SELECT name FROM menu WHERE id = ?", [drinkId]);
  const [[snack]] = await pool.query("SELECT name FROM menu WHERE id = ?", [snackId]);

  res.json({
    drink: { name: drink.name },
    snack: { name: snack.name }
  });

});

// 별점 저장
app.post("/api/star", async (req, res) => {
  const { star } = req.body;

  try {
    if (star < 0 || star > 5) {
      return res.status(400).json({ message: "Star must be between 0 and 5" });
    }

    await pool.query("INSERT INTO statistics_star (star) VALUES (?)", [star]);

    res.json({ message: "Star saved successfully" });
  } catch (err) {
    console.error("Error saving star:", err);
    res.status(500).json({ message: "Database error" });
  }
});



// 요즘 가장 인기있는 메뉴 탭 +1
app.post("/api/click/popular", async (req, res) => {
  try {
    await pool.query(`
      UPDATE statistics_click 
      SET popular_click = popular_click + 1
    `);

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "DB update failed" });
  }
});

// 사장님추천메뉴 탭 +1
app.post("/api/click/recommend", async (req, res) => {
  try {
    await pool.query(`
      UPDATE statistics_click 
      SET recommend_click = recommend_click + 1
    `);

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "DB update failed" });
  }
});

app.listen(3000, () => console.log("Backend running on 3000"));
