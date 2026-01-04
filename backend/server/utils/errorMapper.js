export function aiDownError() {
  return {
    status: "error",
    code: "E503_AI_DOWN",
    message: "AI 서버가 응답하지 않습니다."
  };
}
