package com.example.llm;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class UserService {

    private final UserMapper userMapper;

    @Autowired
    public UserService(UserMapper userMapper) {
        this.userMapper = userMapper;
    }

    public List<Map<String, Object>> getUsers(String status) {
        // Business logic using USER_STATUS
        if ("ACTIVE".equals(status)) {
            return userMapper.findUsersByStatus("A");
        } else if ("INACTIVE".equals(status)) {
            return userMapper.findUsersByStatus("I");
        }
        return userMapper.findAllUsers();
    }

    public void updateUserStatus(String userId, String newStatus) {
        userMapper.updateStatus(userId, newStatus);
    }
}