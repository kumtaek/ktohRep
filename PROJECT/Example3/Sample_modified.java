public class Sample {
    public void queryData() {
        String table = "USERS";
        String sql = "SELECT * FROM " + table;  // 동적 SQL 생성
        try {
            Class<?> clazz = Class.forName("com.example.Unknown");  // 리플렉션 사용
        } catch (Exception e) {
            // 예외 처리
        }
    }
}
