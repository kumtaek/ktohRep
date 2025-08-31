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

    /**
     * @MethodName : updateUserStatus
     * @Description : 사용자 ID와 새로운 상태로 사용자 상태를 업데이트합니다.
     * @Parameters : String userId - 업데이트할 사용자 ID, String newStatus - 새로운 상태
     * @Return : int - 업데이트된 레코드 수
     */
    public int updateUserStatus(String userId, String newStatus) {
        // 실제 구현에서는 UserMapper에 해당 메소드가 정의되어야 합니다.
        // 여기서는 예시를 위해 가상의 호출을 사용합니다.
        System.out.println("사용자 " + userId + "의 상태를 " + newStatus + "(으)로 업데이트합니다.");
        // userMapper.updateUserStatus(userId, newStatus); // 실제 매퍼 호출
        return 1; // 성공 가정
    }
}