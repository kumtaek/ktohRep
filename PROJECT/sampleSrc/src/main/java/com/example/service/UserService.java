package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;
import java.util.Optional;

@Service
public class UserService {

    @Autowired
    private com.example.mapper.UserMapper userMapper;

    /**
     * @MethodName : getUserById
     * @Description : ID로 사용자를 조회합니다. MyBatis 매퍼를 통해 안전한 파라미터 바인딩 사용
     * @Parameters : String userId - 조회할 사용자 ID
     * @Return : Optional<User> - 사용자 정보 (없으면 빈 Optional)
     */
    public Optional<Object> getUserById(String userId) {
        return Optional.ofNullable(userMapper.selectUserById(userId));
    }

    /**
     * @MethodName : getActiveUsers
     * @Description : 활성 사용자 목록을 조회합니다. DEL_YN = 'N' 조건 포함
     * @Parameters : 없음
     * @Return : List<Object> - 활성 사용자 목록
     */
    public List<Object> getActiveUsers() {
        return userMapper.selectActiveUsers();
    }

    /**
     * 사용자 데이터 생성
     * 간단한 주석의 예
     */
    public void createUser(Object user) {
        userMapper.insertUser(user);
    }

    // 리플렉션 사용 예 - 신뢰도 감점 요인
    public void processWithReflection(String className) {
        try {
            Class<?> clazz = Class.forName(className);
            Object instance = clazz.getDeclaredConstructor().newInstance();
            System.out.println("리플렉션으로 생성: " + instance.toString());
        } catch (Exception e) {
            System.err.println("리플렉션 처리 실패: " + e.getMessage());
        }
    }

    // 동적 SQL 생성 예 - 신뢰도 감점 요인  
    public List<Object> getDynamicUserData(String condition) {
        String sql = "SELECT * FROM users WHERE status = '" + condition + "'";
        return userMapper.executeDynamicQuery(sql);
    }
}