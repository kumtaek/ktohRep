package com.example.multilingual;

import org.springframework.stereotype.Service;

// 이 서비스는 다국어 처리를 테스트합니다.
@Service
public class MultilingualService {

    private static final String DEFAULT_GREETING = "Hello"; // Default English greeting
    private String userName; // 사용자 이름

    public MultilingualService() {
        this.userName = "Guest"; // 기본 사용자
    }

    /**
     * 사용자에게 환영 메시지를 반환합니다.
     * Returns a welcome message to the user.
     * @param lang 언어 코드 (ko, en 등)
     * @return 환영 메시지
     */
    public String getWelcomeMessage(String lang) {
        String message;
        switch (lang.toLowerCase()) {
            case "ko":
                message = userName + "님, 환영합니다!"; // 한국어 메시지
                break;
            case "en":
                message = DEFAULT_GREETING + ", " + userName + "!"; // English message
                break;
            default:
                message = "Unsupported language";
                break;
        }
        return message;
    }

    public void setUserName(String userName) {
        this.userName = userName; // 사용자 이름 설정
    }
}