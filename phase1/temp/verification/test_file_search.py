from pathlib import Path

# 프로젝트 루트 경로
project_root = Path("../project/sampleSrc")

print("=== 파일 검색 테스트 ===")

# 1. 직접 rglob로 Java 파일 검색
print("\n1. 직접 rglob로 Java 파일 검색:")
java_files = list(project_root.rglob("*.java"))
print(f"  발견된 Java 파일 수: {len(java_files)}")
for file_path in java_files[:5]:  # 처음 5개만 출력
    print(f"    {file_path}")

# 2. include_patterns 방식으로 검색
print("\n2. include_patterns 방식으로 검색:")
include_patterns = ["**/*.java"]
for include_pattern in include_patterns:
    # 기존 방식 (문제가 있을 수 있는 방식)
    old_pattern = include_pattern.replace("**/", "")
    old_files = list(project_root.rglob(old_pattern))
    print(f"  패턴 '{include_pattern}' -> '{old_pattern}': {len(old_files)}개")
    
    # 수정된 방식
    new_files = list(project_root.rglob(include_pattern))
    print(f"  패턴 '{include_pattern}' (수정): {len(new_files)}개")

# 3. 누락된 파일들 확인
print("\n3. 누락된 파일들 확인:")
missing_files = [
    "src/main/java/com/example/integrated/VulnerabilityTestService.java",
    "src/main/java/com/example/service/OrderService.java",
    "src/main/java/com/example/service/ProductService.java",
    "src/main/java/com/example/service/UserService.java"
]

for missing_file in missing_files:
    full_path = project_root / missing_file
    if full_path.exists():
        print(f"  ✅ {missing_file}: 존재")
    else:
        print(f"  ❌ {missing_file}: 없음")

