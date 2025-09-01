package com.example.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * 보안 설정 클래스
 * 인증 및 권한 부여 규칙 정의
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private TokenProvider tokenProvider;
    
    /**
     * 보안 필터 체인 설정
     */
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf().disable()
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/orders/**").hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter(), UsernamePasswordAuthenticationFilter.class)
            .exceptionHandling()
                .authenticationEntryPoint(customAuthenticationEntryPoint())
                .accessDeniedHandler(customAccessDeniedHandler())
            .and()
            .build();
    }
    
    /**
     * 패스워드 인코더
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
    
    /**
     * JWT 인증 필터
     */
    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter(tokenProvider, userService);
    }
    
    /**
     * 인증 실패 핸들러
     */
    @Bean
    public AuthenticationEntryPoint customAuthenticationEntryPoint() {
        return new CustomAuthenticationEntryPoint();
    }
    
    /**
     * 접근 거부 핸들러
     */
    @Bean
    public AccessDeniedHandler customAccessDeniedHandler() {
        return new CustomAccessDeniedHandler();
    }
    
    /**
     * 인증 관리자 설정
     */
    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration authConfig) throws Exception {
        return authConfig.getAuthenticationManager();
    }
    
    /**
     * 사용자 상세 서비스
     */
    @Bean
    public UserDetailsService userDetailsService() {
        return new CustomUserDetailsService(userService);
    }
    
    /**
     * CORS 설정
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
    
    /**
     * 보안 이벤트 리스너
     */
    @EventListener
    public void handleAuthenticationSuccess(AuthenticationSuccessEvent event) {
        String username = event.getAuthentication().getName();
        logger.info("로그인 성공: {}", username);
        
        // 로그인 히스토리 저장
        auditService.logLoginSuccess(username, getClientIP());
    }
    
    /**
     * 인증 실패 이벤트 처리
     */
    @EventListener
    public void handleAuthenticationFailure(AbstractAuthenticationFailureEvent event) {
        String username = event.getAuthentication().getName();
        logger.warn("로그인 실패: {}", username);
        
        // 실패 히스토리 저장
        auditService.logLoginFailure(username, getClientIP());
        
        // 연속 실패 횟수 체크
        int failureCount = auditService.getFailureCount(username);
        if (failureCount >= 5) {
            // 계정 잠금
            userService.lockAccount(username);
            logger.warn("계정 잠금: {} (연속 실패 {}회)", username, failureCount);
        }
    }
    
    /**
     * 클라이언트 IP 주소 추출
     */
    private String getClientIP() {
        HttpServletRequest request = getCurrentRequest();
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        
        String xRealIP = request.getHeader("X-Real-IP");
        if (xRealIP != null && !xRealIP.isEmpty()) {
            return xRealIP;
        }
        
        return request.getRemoteAddr();
    }
    
    /**
     * 현재 HTTP 요청 반환
     */
    private HttpServletRequest getCurrentRequest() {
        return ((ServletRequestAttributes) RequestContextHolder.currentRequestAttributes()).getRequest();
    }
}