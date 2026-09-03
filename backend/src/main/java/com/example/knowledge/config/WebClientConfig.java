package com.example.knowledge.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    @Bean
    public WebClient aiWebClient(AppProperties properties) {
        return WebClient.builder()
                .baseUrl(properties.aiServiceBaseUrl())
                .build();
    }
}
