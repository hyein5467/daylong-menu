import axios from "axios";

const pythonApi = axios.create({
  baseURL: process.env.AI_SERVER_URL, // http://ai-server:8000
  timeout: 5000,
  headers: {
    "x-api-key": process.env.PYTHON_API_KEY,
    "Content-Type": "application/json"
  }
});

export async function fetchKeywords(payload) {
  const res = await pythonApi.post("/ai/keywords", payload);
  return res.data;
}

export async function fetchMenus(payload) {
  const res = await pythonApi.post("/ai/menus", payload);
  return res.data;
}
