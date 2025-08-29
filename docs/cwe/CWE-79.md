# CWE-79: Cross-Site Scripting (XSS)

## 설명
신뢰되지 않은 입력이 브라우저에서 스크립트로 실행되어 사용자의 세션/데이터를 탈취하거나 UI를 변조하는 취약점입니다.

## 영향
- 세션 하이재킹, 피싱/디피싱, 콘텐츠 변조, 키로깅

## 방어
- 컨텍스트별 출력 인코딩(HTML/JS/URL/Attr)
- 템플릿 자동 이스케이프, CSP 적용, DOM 기반 위험 API 사용 제한
- 입력 검증 및 신뢰 경계 확인

## 취약/안전 코드 예시
### JSP (취약)
```jsp
<div><%= request.getParameter("q") %></div>
```

### JSP (안전: JSTL/EL 자동 이스케이프)
```jsp
<c:out value="${param.q}"/>
```

### Thymeleaf (안전)
```html
<span th:text="${q}"></span>
```

## 체크리스트
- [ ] 모든 출력은 컨텍스트 적합한 이스케이프 적용
- [ ] 템플릿 엔진의 auto-escape 활성화
- [ ] 인라인 이벤트/`innerHTML` 사용 금지, DOMPurify 등 사용 고려
