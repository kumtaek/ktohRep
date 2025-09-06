@echo off
chcp 65001 > nul 

echo [1/3] 연관성 요약 정보 조회...
python -m visualize relatedness --project-name sampleSrc --summary
echo.

echo [2/3] 연관성 시각화 생성 (최소 점수: 0.3)...
python -m visualize relatedness --project-name sampleSrc --export-html output/relatedness_0.3.html --min-score 0.3
echo.

echo [3/3] 연관성 시각화 생성 (최소 점수: 0.5)...
python -m visualize relatedness --project-name sampleSrc --export-html output/relatedness_0.5.html --min-score 0.5
echo.

echo ===============================================
echo 시각화 완료!
echo 결과 파일: output/sampleSrc/visualize/
echo - relatedness_0.3.html (낮은 임계값)
echo - relatedness_0.5.html (높은 임계값)
echo ===============================================