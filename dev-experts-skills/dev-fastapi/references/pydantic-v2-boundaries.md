# Pydantic v2 경계 설계 — 모델 3종 세트와 v2 함정 (SKILL.md 비중복)

> 기준: Pydantic 2.13 (2026-06). v1 문법(class Config·parse_obj·validator)은 FastAPI 0.128에서 지원 제거 — 보이면 마이그레이션 대상.

## 모델 3종 세트 패턴 (경계마다 다른 모델)

```python
class UserBase(BaseModel):            # 공통 필드
    email: EmailStr
    name: str

class UserCreate(UserBase):           # 입력 전용 — 클라이언트가 주는 것만
    password: str

class UserOut(UserBase):              # 출력 전용 — 노출해도 되는 것만
    id: int
    model_config = ConfigDict(from_attributes=True)   # ORM 객체에서 변환 허용
```

- 입력·출력·내부(ORM)를 한 모델로 합치면: 클라이언트가 `id`를 보내거나(입력 오염) `password_hash`가 나간다(출력 유출). **모델 수가 늘어나는 게 정상이다.**
- `from_attributes=True`(v1의 orm_mode)는 출력 모델에만 — 입력 모델엔 불필요.
- 부분 수정(PATCH)은 `UserUpdate`에 전 필드 `| None = None` + `model_dump(exclude_unset=True)`로 "안 보낸 필드"와 "null로 보낸 필드"를 구분.

## v2 함정 (v1 경험자가 자신 있게 틀리는 곳)

1. **`Optional[X]`는 더 이상 기본값이 아니다** — v2에서 `x: int | None`은 "None 허용이지만 **필수**". 선택 필드는 `x: int | None = None`처럼 기본값을 반드시 명시. v1 코드 이식 시 422 폭발의 1순위 원인.
2. **엄격해진 강제 변환** — v1이 조용히 받던 것들(`"123"` → int 일부 케이스, 불명 필드)이 에러가 된다. 외부 API의 지저분한 응답을 받을 땐 필드별 `field_validator(mode="before")`로 명시 정제 — "v1처럼 느슨하게" 전역 완화는 검증을 다시 구멍 낸다.
3. **이름 변경 매핑**: `class Config` → `model_config = ConfigDict(...)` · `parse_obj` → `model_validate` · `parse_raw` → `model_validate_json` · `dict()` → `model_dump()` · `json()` → `model_dump_json()` · `@validator` → `@field_validator` · `@root_validator` → `@model_validator`.
4. **`model_dump()` vs `model_dump(mode="json")`** — 전자는 datetime을 datetime 객체로, 후자는 ISO 문자열로. 직접 json.dumps에 넣을 거면 후자. (FastAPI 응답 경로는 알아서 처리 — 직접 직렬화할 때만 문제.)
5. **검증 비용 위치** — v2는 Rust 코어라 모델 검증 자체는 싸다. 비싼 건 **거대 리스트의 중첩 모델** — 수만 행 응답이면 페이지네이션이 답이지 검증 끄기(`model_construct`)가 아니다. `model_construct`는 신뢰 가능한 내부 데이터 전용.

## 에러 응답 일관화

- 422(검증 실패)의 형식은 FastAPI 기본 제공 — 바꾸려면 `app.exception_handler(RequestValidationError)`로 1곳에서.
- 도메인 에러는 HTTPException을 직접 던지지 말고 도메인 예외 → 핸들러 매핑으로 한 층 분리하면 서비스 함수가 프레임워크 무관해진다(SKILL.md 워크플로우 3 "엔드포인트는 얇게"의 연장):

```python
class CodeNotFound(Exception): ...

@app.exception_handler(CodeNotFound)
async def on_code_not_found(req, exc):
    return JSONResponse(status_code=404, content={"error": "code_not_found"})
```

- 에러 스키마(코드·메시지 필드 구성) 자체의 규약은 dev-rest-api-design 소관.

## 설정 모델 (pydantic-settings)

```python
class Settings(BaseSettings):
    dsn: PostgresDsn
    api_key: SecretStr                 # repr·로그에서 자동 마스킹
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")
```

- 시크릿 필드는 `SecretStr` — 로그에 `**********`로 찍힌다. `.get_secret_value()`는 사용 지점 1곳에서만.
- 설정 검증이 기동 시점에 실패하는 게 **장점**이다 — 환경변수 누락을 첫 요청이 아니라 배포 순간에 알게 된다.
