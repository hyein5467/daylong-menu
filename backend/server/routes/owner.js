const express = require("express");
const router = express.Router();
const pool = require("../../db");
const upload = require("../utils/upload"); // ⭐ 추가

/**
 * 사장님 - 메뉴 전체 조회
 */
router.get("/menus", async (req, res) => {
  try {
    const [rows] = await pool.query(`
      SELECT id, name, type, enabled
      FROM menu
      ORDER BY id ASC
    `);

    res.json({ success: true, data: rows });
  } catch (err) {
    console.error("GET /menus error", err);
    res.status(500).json({ success: false });
  }
});

/**
 * 사장님 - 메뉴 상태 저장
 */
router.post("/menus/save", async (req, res) => {
  const { menus } = req.body;

  if (!Array.isArray(menus)) {
    return res.status(400).json({ success: false });
  }

  const conn = await pool.getConnection();
  try {
    await conn.beginTransaction();

    for (const m of menus) {
      await conn.query(
        "UPDATE menu SET enabled = ? WHERE id = ?",
        [m.enabled, m.id]
      );
    }

    await conn.commit();
    res.json({ success: true });
  } catch (e) {
    await conn.rollback();
    console.error("POST /menus/save error", e);
    res.status(500).json({ success: false });
  } finally {
    conn.release();
  }
});

/**
 * 사장님 - 신메뉴 추가
 * ✅ 이미지 → Cloudinary
 * ✅ name / type / enabled → DB
 */
router.post(
  "/menus",
  upload.single("image"), // ⭐ multer + cloudinary
  async (req, res) => {
    try {
      const { name, type } = req.body;
      console.log("req.file: ",req.file);
      console.log("req.body: ",req.body)

      // 🔒 방어 코드 (중요)
      if (!name || !type) {
        return res.status(400).json({
          success: false,
          message: "name 또는 type 누락",
        });
      }

      const parsedType = Number(type);
      if (![1, 2].includes(parsedType)) {
        return res.status(400).json({
          success: false,
          message: "type 값은 1(음료) 또는 2(디저트)",
        });
      }

      // ✅ DB 저장
      await pool.query(
        "INSERT INTO menu (name, type, enabled) VALUES (?, ?, 1)",
        [name, parsedType]
      );

      res.json({
        success: true,
        imageUrl: req.file?.path, // Cloudinary URL (확인용)
      });
    } catch (err) {
      console.error("POST /menus error", err);
      res.status(500).json({ success: false });
    }
  }
);

module.exports = router;
