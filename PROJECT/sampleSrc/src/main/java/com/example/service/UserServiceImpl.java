package com.example.service;

import com.example.mapper.UserMapper;
import com.example.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@Service
@Transactional
public class UserServiceImpl implements UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    @Override
    public List<User> getUsersByCondition(Map<String, Object> params) {
        return userMapper.selectUsersByCondition(params);
    }
    
    @Override
    public List<User> getUsersByAdvancedCondition(Map<String, Object> params) {
        return userMapper.selectUsersByAdvancedCondition(params);
    }
    
    @Override
    public List<User> getUsersByType(String type) {
        return userMapper.selectUsersByType(type);
    }
    
    @Override
    public User getUserById(Long id) {
        return userMapper.selectUserById(id);
    }
    
    @Override
    public int updateUserDynamic(User user) {
        return userMapper.updateUserDynamic(user);
    }
    
    @Override
    public int deleteUsersByCondition(Map<String, Object> params) {
        return userMapper.deleteUsersByCondition(params);
    }
}