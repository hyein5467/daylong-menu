const express = require("express");
const router = express.Router();
const pool = require("../../db");
const upload = require("../utils/upload");

/**
 * 메뉴 전체 조회
 */
router.get("/menus", async (req, res) => {
  const [rows] = await pool.query(
    "SELECT id, name, type, enabled FROM menu ORDER BY id ASC"
  );
  res.json({ success: true, data: rows });
});

/**
 * 대상메뉴 저장
 */
router.post("/menus/save", async (req, res) => {
  const { menus } = req.body;
  const conn = await pool.getConnection();
  await conn.beginTransaction();

  try {
    for (const m of menus) {
      await conn.query(
        "UPDATE menu SET enabled=? WHERE id=?",
        [m.enabled, m.id]
      );
    }
    await conn.commit();
    res.json({ success: true });
  } catch (e) {
    await conn.rollback();
    res.status(500).json({ success: false });
  } finally {
    conn.release();
  }
});

/**
 * 메뉴 추가 (중복 방지)
 */
router.post("/menus", upload.single("image"), async (req, res) => {
  const { name, type } = req.body;

  if (!name || !type) {
    return res.status(400).json({
      success: false,
      message: "메뉴명과 타입은 필수입니다."
    });
  }

  try {
    await pool.query(
      "INSERT INTO menu (name, type, enabled) VALUES (?, ?, 1)",
      [name.trim(), Number(type)]
    );

    res.json({ success: true });
  } catch (e) {
    if (e.code === "ER_DUP_ENTRY") {
      return res.status(409).json({
        success: false,
        message: "이미 존재하는 메뉴입니다."
      });
    }

    console.error("POST /menus error", e);
    res.status(500).json({
      success: false,
      message: "서버 오류"
    });
  }
});

/**
 * 추천 / 인기 조회
 */
router.get("/menus/recommend", async (req, res) => {
  const [rows] = await pool.query("SELECT * FROM menu_recommend LIMIT 1");
  res.json({ success: true, data: rows[0] });
});

/**
 * 추천 / 인기 부분 업데이트
 */
router.post("/menus/recommend", async (req, res) => {
  const {
    popular_drink,
    popular_snack,
    recommend_drink,
    recommend_snack
  } = req.body;

  const fields = [];
  const values = [];

  if (popular_drink !== undefined) {
    fields.push("popular_drink = ?");
    values.push(popular_drink);
  }
  if (popular_snack !== undefined) {
    fields.push("popular_snack = ?");
    values.push(popular_snack);
  }
  if (recommend_drink !== undefined) {
    fields.push("recommend_drink = ?");
    values.push(recommend_drink);
  }
  if (recommend_snack !== undefined) {
    fields.push("recommend_snack = ?");
    values.push(recommend_snack);
  }

  if (!fields.length) {
    return res.status(400).json({ success: false });
  }

  const sql = `
    UPDATE menu_recommend
    SET ${fields.join(", ")}
    LIMIT 1
  `;

  try {
    await pool.query(sql, values);
    res.json({ success: true });
  } catch (e) {
    console.error("UPDATE menu_recommend error", e);
    res.status(500).json({ success: false });
  }
});

/**
 * 메뉴 삭제
 */
/**
 * 메뉴 삭제 (인기/추천 사용 중이면 차단)
 */
router.post("/menus/delete", async (req, res) => {
  const { ids } = req.body;

  if (!Array.isArray(ids) || ids.length === 0) {
    return res.status(400).json({
      success: false,
      message: "삭제할 메뉴가 없습니다."
    });
  }

  const conn = await pool.getConnection();
  await conn.beginTransaction();

  try {
    // 1️⃣ 인기/추천으로 사용 중인지 검사
    const [used] = await conn.query(
      `
      SELECT *
      FROM menu_recommend
      WHERE
        recommend_drink IN (?)
        OR recommend_snack IN (?)
        OR popular_drink IN (?)
        OR popular_snack IN (?)
      `,
      [ids, ids, ids, ids]
    );

    if (used.length > 0) {
      await conn.rollback();
      return res.status(409).json({
        success: false,
        message:
          "인기메뉴 또는 추천메뉴로 설정된 메뉴는 삭제할 수 없습니다."
      });
    }

    // 2️⃣ 실제 메뉴 삭제
    await conn.query(
      "DELETE FROM menu WHERE id IN (?)",
      [ids]
    );

    await conn.commit();
    res.json({ success: true });
  } catch (e) {
    await conn.rollback();
    console.error("DELETE /menus/delete error", e);
    res.status(500).json({ success: false });
  } finally {
    conn.release();
  }
});

/* 만족도 조사 별점 결과 조회 */
router.get("/statistics/star", async (req, res) => {
  try {
    const [counts] = await pool.query(`
      SELECT star, COUNT(*) AS count
      FROM statistics_star
      GROUP BY star
      ORDER BY star
    `);

    const [summary] = await pool.query(`
      SELECT COUNT(*) AS total, AVG(star) AS average
      FROM statistics_star
    `);

    const [rows] = await pool.query(`
      SELECT
        id,
        star,
        drink_name,
        snack_name,
        selected_keywords,
        created_at
      FROM statistics_star
      ORDER BY id DESC
    `);

    res.json({
      success: true,
      data: {
        counts,
        total: Number(summary[0].total || 0),
        average: Number(summary[0].average || 0),
        rows
      }
    });

  } catch (err) {
    console.error("GET /statistics/star error", err);
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
