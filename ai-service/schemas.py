# ai-service/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# [응답] 공통 규격
class BaseSuccessResponse(BaseModel):
    status: str = Field("success", description="응답 상태")

# [요청] 키워드 추천 (비어있어도 됨)
class KeywordRequest(BaseModel):
    pass

# [응답] 날씨 기반 키워드
class KeywordResponse(BaseSuccessResponse):
    keywords: List[str] = Field(..., description="AI가 생성한 추천 키워드")

# [요청] 메뉴 추천 (Node -> Python)
class AIRecommendationRequest(BaseModel):
    keywords: List[str] = Field(..., description="유저가 선택한 키워드")
    menu_list: Dict[str, List[str]] = Field(..., description="전체 메뉴판")

# [응답] 메뉴 추천 결과
class AIRecommendResponse(BaseSuccessResponse):
    drink: str
    snack: str
    reason: str