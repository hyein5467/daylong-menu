/**
 * =====================================================
 * Node.js Backend (Control Tower)
 *
 * 역할
 * - userToken 쿠키 발급
 * - 키워드 / 메뉴 추천 사용 횟수 제한 (하루 3회)
 * - 자정(00:00) 기준 자동 초기화
 * - 제한 초과 시 Python 호출 ❌
 * - DB fallback 처리
 * =====================================================
 */

const express = require("express");
const cors = require("cors");
const cookieParser = require("cookie-parser");
const axios = require("axios");
const pool = require("../db"); // mysql2 pool
require("dotenv").config();

const ownerRoutes = require("./routes/owner");


const app = express();

/**
 * -----------------------------------------------------
 * 기본 미들웨어
 * -----------------------------------------------------
 */
app.use(express.json());
app.use(cookieParser());
app.use("/api/owner", ownerRoutes);

app.use(
  cors({
    origin: true,
    credentials: true,
  })
);

/**
 * -----------------------------------------------------
 * 0️⃣ bootstrap
 * - 최초 접속 시 userToken 쿠키 발급
 * -----------------------------------------------------
 */
app.get("/api/bootstrap", (req, res) => {
  let token = req.cookies.userToken;

  if (!token) {
    token = require("crypto").randomUUID();

    res.cookie("userToken", token, {
      httpOnly: true,
      sameSite: "lax",
      maxAge: 1000 * 60 * 60 * 24, // 1일
      path: "/",
    });
  }

  res.json({ success: true });
});

/**
 * 인기 / 사장님 추천 메뉴 조회
 */
app.get("/api/popular", async (req, res) => {
  try {
    const [[row]] = await pool.query(`
      SELECT
        popular_drink,
        popular_snack,
        recommend_drink,
        recommend_snack
      FROM menu_recommend
      LIMIT 1
    `);

    if (!row) {
      return res.status(404).json({ error: "No menu recommend data" });
    }

    const [
      [[popularDrink]],
      [[popularSnack]],
      [[recommendDrink]],
      [[recommendSnack]]
    ] = await Promise.all([
      pool.query("SELECT name FROM menu WHERE id = ?", [row.popular_drink]),
      pool.query("SELECT name FROM menu WHERE id = ?", [row.popular_snack]),
      pool.query("SELECT name FROM menu WHERE id = ?", [row.recommend_drink]),
      pool.query("SELECT name FROM menu WHERE id = ?", [row.recommend_snack]),
    ]);

    res.json({
      popular: {
        drink: { name: popularDrink?.name || null },
        snack: { name: popularSnack?.name || null },
      },
      recommend: {
        drink: { name: recommendDrink?.name || null },
        snack: { name: recommendSnack?.name || null },
      }
    });
  } catch (err) {
    console.error("GET /api/popular error", err);
    res.status(500).json({ error: "DB error" });
  }
});


/**
 * 별점 저장
 */
app.post("/api/star", async (req, res) => {
  const { star } = req.body;

  try {
    if (typeof star !== "number" || star < 0 || star > 5) {
      return res.status(400).json({
        message: "Star must be between 0 and 5"
      });
    }

    await pool.query(
      "INSERT INTO statistics_star (star) VALUES (?)",
      [star]
    );

    res.json({ message: "Star saved successfully" });
  } catch (err) {
    console.error("Error saving star:", err);
    res.status(500).json({ message: "Database error" });
  }
});

/**
 * 인기 메뉴 클릭 +1
 */
app.post("/api/click/popular", async (req, res) => {
  try {
    await pool.query(
      "UPDATE statistics_click SET popular_click = popular_click + 1"
    );

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "DB update failed" });
  }
});

/**
 * 사장님 추천 클릭 +1
 */
app.post("/api/click/recommend", async (req, res) => {
  try {
    await pool.query(
      "UPDATE statistics_click SET recommend_click = recommend_click + 1"
    );

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "DB update failed" });
  }
});


/**
 * -----------------------------------------------------
 * 1️⃣ 키워드 조회
 * - 하루 3회 (자정 기준)
 * -----------------------------------------------------
 */
app.get("/api/keywords", async (req, res) => {
  const token = req.cookies.userToken;
  if (!token) {
    return res.status(400).json({ message: "No user token" });
  }

  const BASIC_KEYWORDS = ["커피", "논커피"];
  const MAX_RETRY = 5;
  const now = new Date();

  const normalize = (k) => k.replace(/\s+/g, "");

  try {
    // 1️⃣ 사용 횟수 체크
    const [[usage]] = await pool.query(
      "SELECT count, reset_at FROM keyword_usage WHERE user_token = ?",
      [token]
    );

    let count = 1;

    if (!usage || now > usage.reset_at) {
      await pool.query(
        `
        INSERT INTO keyword_usage (user_token, count, reset_at)
        VALUES (?, 1, DATE_ADD(CURDATE(), INTERVAL 1 DAY))
        ON DUPLICATE KEY UPDATE
          count = 1,
          reset_at = DATE_ADD(CURDATE(), INTERVAL 1 DAY)
        `,
        [token]
      );
    } else {
      count = usage.count + 1;
      await pool.query(
        "UPDATE keyword_usage SET count = ? WHERE user_token = ?",
        [count, token]
      );
    }

    // 4회차 이상 → DB ONLY
    if (count >= 4) {
      const fixedSet = new Set(BASIC_KEYWORDS);

      let dbKeywords = [];
      let success = false;

      for (let i = 0; i < MAX_RETRY; i++) {
        const [rows] = await pool.query(
          `
          SELECT keyword
          FROM keywords
          WHERE CHAR_LENGTH(keyword) <= 5
          ORDER BY RAND()
          LIMIT 10
          `
        );

        const candidates = rows.map(r => r.keyword);
        const hasOverlap =
          candidates.some(k => fixedSet.has(k)) ||
          new Set(candidates).size !== candidates.length;

        if (!hasOverlap) {
          dbKeywords = candidates;
          success = true;
          break;
        }
      }
      if (!success) {
        return res.status(500).json({ message: "DB 키워드 중복 해결 실패" });
      }

      return res.json({
        status: "success",
        data: [...BASIC_KEYWORDS, ...dbKeywords],
        source: "db",
      });
    }
      // 1~3회차 → AI + DB
    const pythonRes = await axios.post(
    "http://127.0.0.1:8000/ai/keywords",
    {},
    {
      headers: { "x-api-key": process.env.PYTHON_API_KEY },
      timeout: 10000,
    }
  );


  // 🔥 AI 토큰 부족 판별 (HTTP 200이라도)
  if (
    pythonRes.data?.status === "error" &&
    (
      pythonRes.data?.code === "E429_QUOTA_EXCEEDED" ||
      pythonRes.data?.message?.includes("quota") ||
      pythonRes.data?.message?.includes("exceeded")
    )
  ) {
    return res.status(429).json({
      status: "error",
      code: "E429_QUOTA_EXCEEDED",
      message: "AI 무료 사용량이 소진되었습니다.",
    });
  }
    const rawAi = pythonRes.data.keywords || [];

    const aiKeywords = [];
    let invalidAiCount = 0;

    for (const k of rawAi.slice(0, 5)) {
      if (normalize(k).length <= 5) {
        aiKeywords.push(k);
      } else {
        invalidAiCount++;
      }
    }
    for (const keyword of aiKeywords) {
      const cleaned = normalize(keyword).trim();
      if (!cleaned) continue;

      try {
        await pool.query(
          `INSERT IGNORE INTO keywords (keyword) VALUES (?)`,
          [cleaned]
        );
      } catch (e) {
        console.warn("⚠️ keyword save failed:", cleaned);
      }
    }



    const needDbCount = 5 + invalidAiCount;
    const fixedKeywords = [...BASIC_KEYWORDS, ...aiKeywords];
    const fixedSet = new Set(fixedKeywords);

    let dbKeywords = [];
    let success = false;

    for (let i = 0; i < MAX_RETRY; i++) {
      const [rows] = await pool.query(
        `
        SELECT keyword
        FROM keywords
        WHERE CHAR_LENGTH(keyword) <= 5
        ORDER BY RAND()
        LIMIT ?
        `,
        [needDbCount]
      );

      const candidates = rows.map(r => r.keyword);
      const hasOverlap =
        candidates.some(k => fixedSet.has(k)) ||
        new Set(candidates).size !== candidates.length;

      if (!hasOverlap) {
        dbKeywords = candidates;
        success = true;
        break;
      }
    }

    if (!success) {
      return res.status(500).json({ message: "DB 키워드 중복 해결 실패" });
    }

    return res.json({
      status: "success",
      data: [...BASIC_KEYWORDS, ...aiKeywords, ...dbKeywords],
      source: "ai+db",
    });

  } catch (err) {
    const status = err.response?.status;

    if (status === 429) {
      return res.status(429).json({
        status: "error",
        code: "E429_QUOTA_EXCEEDED",
        message: "AI 무료 사용량이 소진되었습니다.",
      });
    }

    console.error("AI keyword error:", err.message);

    return res.status(500).json({
      status: "error",
      message: "AI keyword server error",
    });
  }
});

/**
 * -----------------------------------------------------
 * 2️⃣ 메뉴 추천
 * - 하루 3회 (자정 기준)
 * -----------------------------------------------------
 */
app.post("/api/menus", async (req, res) => {
  const token = req.cookies?.userToken;
  if (!token) {
    return res.status(400).json({
      status: "error",
      message: "No user token",
    });
  }

  const now = new Date();

  try {
    /* -------------------------------------------------
     * 1️⃣ 사용 횟수 체크
     * ------------------------------------------------- */
    const [[usage]] = await pool.query(
      "SELECT count, reset_at FROM menu_usage WHERE user_token = ?",
      [token]
    );

    if (!usage || now > usage.reset_at) {
      await pool.query(
        `
        INSERT INTO menu_usage (user_token, count, reset_at)
        VALUES (?, 1, DATE_ADD(CURDATE(), INTERVAL 1 DAY))
        ON DUPLICATE KEY UPDATE
          count = 1,
          reset_at = DATE_ADD(CURDATE(), INTERVAL 1 DAY)
        `,
        [token]
      );
    } else if (usage.count >= 3) {
      return res.status(429).json({
        status: "error",
        message: "고객님의 금일 추천 횟수가 소진되었습니다.",
      });
    } else {
      await pool.query(
        "UPDATE menu_usage SET count = count + 1 WHERE user_token = ?",
        [token]
      );
    }

    /* -------------------------------------------------
     * 2️⃣ 메뉴 목록 DB 조회 (핵심)
     * ------------------------------------------------- */
    const [menus] = await pool.query(
      `
      SELECT name, type
      FROM menu
      WHERE enabled = 1
      `
    );

    const menu_list = {
      drinks: menus
        .filter((m) => m.type === 1)
        .map((m) => m.name),
      snacks: menus
        .filter((m) => m.type === 2)
        .map((m) => m.name),
    };

    /* -------------------------------------------------
     * 3️⃣ Python AI 서버 호출
     * ------------------------------------------------- */
    const pythonRes = await axios.post(
      "http://127.0.0.1:8000/ai/menus",
      {
        // Python schema에 맞게 변환
        keywords: req.body.selected_keywords,
        menu_list: menu_list,
      },
      {
        headers: {
          "x-api-key": process.env.PYTHON_API_KEY,
        },
        timeout: 30000,
      }
    );

    /* -------------------------------------------------
     * 4️⃣ Python 응답 정규화
     * ------------------------------------------------- */
    const pythonData = pythonRes.data;

    return res.json({
      status: "success",
      data: pythonData.data ?? pythonData,
    });

  } catch (err) {
    console.error("❌ 메뉴 추천 실패", err);

    return res.status(500).json({
      status: "error",
      message: "Server error",
    });
  }
});


/**
 * -----------------------------------------------------
 * 서버 실행
 * -----------------------------------------------------
 */
app.listen(3000, () => {
  console.log("🚀 Backend running on http://localhost:3000");
});
