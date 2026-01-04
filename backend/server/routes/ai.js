import express from "express";
import { fetchKeywords } from "../services/pythonClient.js";
import { aiDownError } from "../utils/errorMapper.js";

const router = express.Router();

router.get("/keywords", async (req, res) => {
  try {
    const pythonRes = await fetchKeywords({
      weather: "Clear",
      temp: 24.5
    });

    // Python 성공
    return res.json({
      status: "success",
      data: pythonRes.keywords
    });

  } catch (err) {
    console.error("AI KEYWORDS ERROR:", err.message);

    // 🔥 무조건 이 에러로 통일
    return res.status(503).json(aiDownError());
  }
});

export default router;
